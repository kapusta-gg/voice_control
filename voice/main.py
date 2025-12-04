import os
import sys
import numpy as np
import pyaudio
import torch
import librosa
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import zmq
from queue import Queue, Empty
from threading import Thread
import time
import logging
import argparse
import json
import vosk
import uuid

from nlp_processor import NLPProcessor
from window_com import CommandsList

# =============================================
# 0. Настройка и парсинг аргументов
# =============================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('VoiceControlSystem')
parser = argparse.ArgumentParser(description='Система голосового управления')
parser.add_argument('--zmq-client', action='store_true', help='Запустить только клиент ZeroMQ для тестов')
parser.add_argument('--model-path', type=str, default="models/vosk-model-small-ru", help='Путь к модели VOSK')

args = parser.parse_args()

# =============================================
# 1. Конфигурация и инициализация
# =============================================
SAMPLE_RATE = 16000
CHUNK_SIZE = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
VAD_THRESHOLD = 0.5
MIN_SPEECH_DURATION = 0.3
POST_SPEECH_SILENCE = 0.5
ZMQ_PORT = 5555

raw_audio_queue = Queue(maxsize=50)
speech_chunks_queue = Queue(maxsize=50)
result_queue = Queue(maxsize=10)

# =============================================
# 2. Загрузка моделей
# =============================================
logger.info("Загрузка моделей...")
vad_model, _ = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False, onnx=False)
try:
    logger.info(f"Загрузка модели VOSK из {args.model_path}...")
    if not os.path.exists(args.model_path):
        logger.error(f"Путь к модели VOSK не найден: {args.model_path}")
        sys.exit(1)
    vosk_model = vosk.Model(args.model_path)
    logger.info("Модель VOSK успешно загружена.")
except Exception as e:
    logger.error(f"Не удалось загрузить модель VOSK: {e}")
    sys.exit(1)


# =============================================
# 3. Потоки обработки
# =============================================
class AudioProcessor(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True
        self.speech_buffer = np.array([], dtype=np.float32)
        self.last_speech_time = 0
        self.speech_active = False
        self.last_vad_prob = 0.0
        self.current_speech_id = None

        self.nlp = NLPProcessor()
        logger.info("NLP процессор готов.")

    def recognize_speech(self, audio_data):
        try:
            audio_data_int16 = (audio_data * 32767).astype(np.int16)
            recognizer = vosk.KaldiRecognizer(vosk_model, SAMPLE_RATE)
            recognizer.AcceptWaveform(audio_data_int16.tobytes())
            result = json.loads(recognizer.FinalResult())
            return result.get("text", "")
        except Exception as e:
            logger.error(f"Ошибка распознавания VOSK: {e}")
            return ""

    def run(self):
        logger.info("Поток обработки аудио запущен.")
        while self.running:
            try:
                audio_chunk = raw_audio_queue.get(timeout=1)
                audio_tensor = torch.from_numpy(audio_chunk).float()
                speech_prob = vad_model(audio_tensor, SAMPLE_RATE).item()
                self.last_vad_prob = speech_prob
                is_speech = speech_prob > VAD_THRESHOLD

                if is_speech:
                    self.last_speech_time = time.time()
                    if not self.speech_active:
                        self.speech_active = True
                        self.current_speech_id = str(uuid.uuid4())
                        self.speech_buffer = np.array([], dtype=np.float32)

                    if not speech_chunks_queue.full():
                        speech_chunks_queue.put({'id': self.current_speech_id, 'chunk': audio_chunk})

                    self.speech_buffer = np.concatenate([self.speech_buffer, audio_chunk])

                elif self.speech_active:
                    silence_duration = time.time() - self.last_speech_time
                    if (silence_duration > POST_SPEECH_SILENCE and
                            len(self.speech_buffer) / SAMPLE_RATE > MIN_SPEECH_DURATION):

                        logger.info(f"Конец сегмента ID: {self.current_speech_id[:8]}. Обработка...")

                        recognized_text = self.recognize_speech(self.speech_buffer)
                        logger.info(f"Распознанный текст: '{recognized_text}'")

                        command_obj = self.nlp.process_text(recognized_text)
                        if command_obj is None:
                            logger.info("Команда не распознана, действие не требуется.")
                            self.speech_active = False
                            self.current_speech_id = None
                            continue

                        logger.info(f"Сгенерирована команда: {command_obj.get_description()}")
                        original_command_dict = command_obj.to_dict()

                        payload_dict = original_command_dict.copy()
                        command_type_for_zmq = payload_dict.pop('type', None)

                        if command_type_for_zmq:
                            params_dict = {}
                            if 'params' in payload_dict and len(payload_dict) == 1:
                                params_dict = payload_dict['params']
                            else:
                                params_dict = payload_dict

                            zmq_payload = {
                                "command": command_type_for_zmq,
                                "params": params_dict
                            }

                            logger.info(f"Отправка ZMQ команды: {zmq_payload}")
                            zmq_socket.send_json(zmq_payload)
                        else:
                            logger.warning("Не удалось определить тип команды для отправки по ZMQ.")

                        result_data = {
                            'id': self.current_speech_id,
                            'text': recognized_text,
                            'command_obj': command_obj
                        }

                        if not result_queue.full(): result_queue.put(result_data)

                        self.speech_active = False
                        self.current_speech_id = None

            except Empty:
                continue
            except Exception as e:
                logger.error(f"Ошибка в потоке обработки: {e}", exc_info=True)


def audio_capture_thread():
    logger.info("Поток захвата аудио запущен.")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK_SIZE)
    while True:
        try:
            raw_data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            audio_chunk = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
            if not raw_audio_queue.full(): raw_audio_queue.put(audio_chunk)
        except Exception as e:
            logger.error(f"Ошибка в потоке захвата аудио: {e}")
            break
    stream.stop_stream();
    stream.close();
    audio.terminate()


# =============================================
# 4. Визуализация
# =============================================
class VoiceControlVisualizer(QtWidgets.QMainWindow):
    def  __init__(self, processor):
        super().__init__()
        self.processor = processor
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.setWindowTitle("Система голосового управления")
        self.setGeometry(100, 100, 1200, 800)
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        left_column = QtWidgets.QVBoxLayout()
        main_layout.addLayout(left_column, 3)
        wave_widget = pg.GraphicsLayoutWidget()
        left_column.addWidget(wave_widget)
        self.waveform_plot = wave_widget.addPlot(title="Обнаруженные речевые фрагменты")
        self.waveform_plot.setLabel('left', "Амплитуда")
        self.waveform_plot.setLabel('bottom', "Время (в накопленной речи)", units="с")
        self.waveform_curve = self.waveform_plot.plot(pen=pg.mkPen('#1f77b4', width=1))

        spectrogram_widget = pg.GraphicsLayoutWidget()
        left_column.addWidget(spectrogram_widget)
        self.spectrogram_plot = spectrogram_widget.addPlot(title="Спектрограмма (накопленная)")
        self.spectrogram_plot.setLabel('left', "Частота", units="кГц")
        self.spectrogram_img = pg.ImageItem(border='k')
        self.spectrogram_plot.addItem(self.spectrogram_img)
        self.spectrogram_img.setLookupTable(pg.colormap.get('viridis').getLookupTable())
        self.spectrogram_plot.getAxis('left').setTicks(
            [[(v / 1000, f"{v / 1000:.0f}") for v in [2000, 4000, 6000, 8000]]])

        right_column = QtWidgets.QVBoxLayout()
        main_layout.addLayout(right_column, 2)
        title_label = QtWidgets.QLabel("Результаты распознавания")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        right_column.addWidget(title_label)
        self.text_output = QtWidgets.QTextEdit()
        self.text_output.setReadOnly(True)
        right_column.addWidget(self.text_output)
        self.status_bar = self.statusBar()
        self.vad_status_label = QtWidgets.QLabel("Речь: НЕТ")
        self.vad_status_label.setStyleSheet(
            "padding: 2px 8px; border-radius: 4px; background-color: #e74c3c; color: white;")
        self.status_bar.addPermanentWidget(self.vad_status_label)
        self.status_label = QtWidgets.QLabel("Статус: Ожидание...");
        self.status_bar.addWidget(self.status_label)
        self.command_colors = {"move": "#27ae60", "turn": "#3498db", "stop": "#e74c3c"}

        self.speech_chunks_log = []
        self.total_samples = 0
        self.max_log_len_sec = 20
        self.display_window_sec = 8

        self.timer = QtCore.QTimer();
        self.timer.timeout.connect(self.update_gui);
        self.timer.start(30)

        
        act = self.menuBar().addAction("Команды")
        act.triggered.connect(self.open_comand_window)

    def open_comand_window(self):
        logger.info("Открывается окно списка команд")
        self.widget = CommandsList(logger)
        self.widget.show()

    def update_gui(self):
        has_new_chunks = False
        while not speech_chunks_queue.empty():
            data = speech_chunks_queue.get_nowait()
            chunk = data['chunk']
            start_sample = self.total_samples
            end_sample = start_sample + len(chunk)
            self.speech_chunks_log.append(
                {'id': data['id'], 'chunk': chunk, 'start_sample': start_sample, 'end_sample': end_sample})
            self.total_samples = end_sample
            has_new_chunks = True

        max_samples_in_log = int(self.max_log_len_sec * SAMPLE_RATE)
        if self.total_samples > max_samples_in_log:
            samples_to_cut = self.total_samples - max_samples_in_log
            cut_index = 0
            for i, log_entry in enumerate(self.speech_chunks_log):
                if log_entry['end_sample'] >= samples_to_cut:
                    cut_index = i
                    break
            self.speech_chunks_log = self.speech_chunks_log[cut_index:]

        if has_new_chunks: self.update_plots()

        try:
            result = result_queue.get_nowait()
            self.update_text_output(result)
            self.add_annotation(result)
        except Empty:
            pass

        self.update_vad_status(self.processor.last_vad_prob)

    def get_concatenated_buffer(self):
        if not self.speech_chunks_log: return np.array([])
        return np.concatenate([entry['chunk'] for entry in self.speech_chunks_log])

    def update_plots(self):
        buffer = self.get_concatenated_buffer()
        if len(buffer) == 0: return

        start_time_sec = self.speech_chunks_log[0]['start_sample'] / SAMPLE_RATE
        end_time_sec = self.total_samples / SAMPLE_RATE
        time_axis = np.linspace(start_time_sec, end_time_sec, num=len(buffer))

        self.waveform_curve.setData(time_axis, buffer)

        display_start_time = max(start_time_sec, end_time_sec - self.display_window_sec)
        self.waveform_plot.setXRange(display_start_time, end_time_sec)

        visible_start_sample = int(display_start_time * SAMPLE_RATE)
        current_start_sample = self.speech_chunks_log[0]['start_sample']
        start_idx = visible_start_sample - current_start_sample

        if start_idx < len(buffer):
            visible_buffer = buffer[max(0, start_idx):]
            if len(visible_buffer) > 1024:
                S = np.abs(librosa.stft(visible_buffer, n_fft=1024, hop_length=256))
                db_S = librosa.amplitude_to_db(S, ref=np.max)
                self.spectrogram_img.setImage(db_S.T, autoLevels=False, levels=(-60, 0))
                scale_x = (len(visible_buffer) / SAMPLE_RATE) / db_S.shape[1]
                scale_y = (SAMPLE_RATE / 2000) / db_S.shape[0]
                transform = QtGui.QTransform()
                transform.translate(display_start_time, 0)
                transform.scale(scale_x, scale_y)
                self.spectrogram_img.setTransform(transform)

    def add_annotation(self, result):
        speech_id = result['id']
        relevant_chunks = [entry for entry in self.speech_chunks_log if entry['id'] == speech_id]
        if not relevant_chunks:
            logger.warning(f"Не найдены чанки для аннотации ID: {speech_id[:8]}")
            return

        start_time = relevant_chunks[0]['start_sample'] / SAMPLE_RATE
        end_time = relevant_chunks[-1]['end_sample'] / SAMPLE_RATE

        command_obj = result['command_obj']
        description = command_obj.get_description()
        command_type = command_obj.to_dict()['type']
        color = self.command_colors.get(command_type, "#95a5a6")

        region = pg.LinearRegionItem(values=[start_time, end_time], brush=pg.mkBrush(f'{color}40'), movable=False,
                                     pen=pg.mkPen(color))
        self.waveform_plot.addItem(region)

        text_html = f"<div style='text-align: center;'><b style='color: {color}; font-size: 10pt;'>{description}</b></div>"
        text_item = pg.TextItem(html=text_html, color='k', anchor=(0.5, 0), fill=pg.mkBrush('#ffffffA0'))

        buffer = self.get_concatenated_buffer()
        start_sample_abs = relevant_chunks[0]['start_sample']
        end_sample_abs = relevant_chunks[-1]['end_sample']
        log_start_sample = self.speech_chunks_log[0]['start_sample']
        region_slice = buffer[start_sample_abs - log_start_sample: end_sample_abs - log_start_sample]
        max_amplitude = np.max(region_slice) if len(region_slice) > 0 else 0.5

        text_item.setPos((start_time + end_time) / 2, max_amplitude * 1.05)
        self.waveform_plot.addItem(text_item)

    def update_vad_status(self, prob):
        if prob > VAD_THRESHOLD:
            self.vad_status_label.setText("Речь: АКТИВНА")
            self.vad_status_label.setStyleSheet(
                "padding: 2px 8px; border-radius: 4px; background-color: #27ae60; color: white;")
        else:
            self.vad_status_label.setText("Речь: НЕТ")
            self.vad_status_label.setStyleSheet(
                "padding: 2px 8px; border-radius: 4px; background-color: #e74c3c; color: white;")

    def update_text_output(self, result):
        command_obj = result['command_obj']
        text = result['text']
        description = command_obj.get_description()
        command_type = command_obj.to_dict()['type']
        color = self.command_colors.get(command_type, "#95a5a6")

        output_html = f"""<div style='border-left: 5px solid {color}; padding-left: 10px; margin-bottom: 15px;'><b style='color: {color}; font-size: 18pt;'>{description.upper()}</b><div style='font-size: 12pt; color: #555;'>Исходный текст: "{text}"</div></div>"""
        self.text_output.setHtml(output_html + self.text_output.toHtml())
        self.status_label.setText(f"Статус: Команда '{description}'")

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()


# =============================================
# 5. и 6. Клиент и запуск
# =============================================
def zmq_client():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://localhost:{ZMQ_PORT}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    logger.info(f"Клиент ZeroMQ запущен на порту {ZMQ_PORT}...")
    try:
        while True:
            data = socket.recv_json()
            logger.info(f"ZMQ_CLIENT | Получена команда: {data}")
    except KeyboardInterrupt:
        logger.info("Клиент ZeroMQ остановлен.")
    finally:
        socket.close()
        context.term()


if __name__ == "__main__":
    if args.zmq_client:
        zmq_client();
        sys.exit(0)

    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUB)
    zmq_socket.bind(f"tcp://*:{ZMQ_PORT}")
    logger.info(f"Сервер ZeroMQ запущен на порту {ZMQ_PORT}")
    processor = AudioProcessor()
    processor.start()
    capture_thread = Thread(target=audio_capture_thread, daemon=True)
    capture_thread.start()
    app = QtWidgets.QApplication(sys.argv)
    visualizer = VoiceControlVisualizer(processor)
    visualizer.show()
    sys.exit(app.exec())