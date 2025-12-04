
import spacy
import math
from typing import Optional, List


from interfaces.command_interface import CommandInterface
from move_command import MoveCommand
from turn_command import TurnCommand
from stop_command import StopCommand


class NLPProcessor:

    DEFAULT_LINEAR_SPEED = 0.5
    DEFAULT_ANGULAR_SPEED = 0.5
    SPEED_FASTER_MULTIPLIER = 1.5
    SPEED_SLOWER_MULTIPLIER = 0.1

    def __init__(self):
        try:
            self.nlp = spacy.load("ru_core_news_md")
        except OSError:
            print("Не удалось загрузить модель spaCy 'ru_core_news_md'.")
            print("Пожалуйста, установите ее командой: python -m spacy download ru_core_news_md")
            self.nlp = None

        self._NUMBER_WORDS = {
            'ноль': 0, 'нуль': 0, 'один': 1, 'одна': 1, 'одно': 1,
            'два': 2, 'две': 2, 'три': 3, 'четыре': 4, 'пять': 5,
            'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9, 'десять': 10,
            'одиннадцать': 11, 'двенадцать': 12, 'тринадцать': 13,
            'четырнадцать': 14, 'пятнадцать': 15, 'шестнадцать': 16,
            'семнадцать': 17, 'восемнадцать': 18, 'девятнадцать': 19,
            'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50,
            'шестьдесят': 60, 'семьдесят': 70, 'восемьдесят': 80, 'девяносто': 90,
            'сто': 100, 'двести': 200, 'триста': 300, 'четыреста': 400,
            'пятьсот': 500, 'шестьсот': 600, 'семьсот': 700, 'восемьсот': 800,
            'девятьсот': 900,
            'полтора': 1.5, 'полторы': 1.5,
        }
        self._SCALE_WORDS = {'тысяча': 1000, 'миллион': 1000000}
        self.ALL_NUM_WORDS = set(self._NUMBER_WORDS.keys()) | set(self._SCALE_WORDS.keys())

        # --- Ключевые слова ---
        # --- Движение ВПЕРЕД ---
        self.MOVE_FORWARD_KEYWORDS = {
            # Основные
            'вперед', 'вперёд', 'прямо', 'ехать', 'проехать', 'двигаться', 'переместиться', 'идти',
            # Повелительные/Разговорные
            'катись', 'поезжай', 'езжай', 'двигай', 'шагай', 'ступай', 'топай', 'вперёд-вперёд', 'давай вперёд',
            # Ошибки распознавания / неполные слова
            'перед', 'перёд', 'прям', 'вперт'
        }

        # --- Движение НАЗАД ---

        self.MOVE_BACKWARD_KEYWORDS = {
            # Основные
            'назад', 'отъехать', 'сдать', 'отступить', 'пятиться',
            # Повелительные/Разговорные
            'отъезжай', 'откатись', 'сдай назад', 'двигай назад', 'задний ход',
            # Ошибки распознавания
            'назат', 'назад', 'здать', 'здавать'
        }

        # --- Общие команды ПОВОРОТА ---
        self.TURN_KEYWORDS = {
            # Основные
            'повернуть', 'развернуться', 'крутиться', 'поворот',
            # Повелительные/Раздоворные
            'поверни', 'повернись', 'разверни', 'развернись', 'крутись', 'покрутись', 'вертись',
            'вращайся', 'поворачивай', 'разворачивайся', 'вращение',
            # Ошибки распознавания
            'поверь', 'вернуть', 'поворот'
        }

        # --- Направление ВЛЕВО ---
        self.TURN_LEFT_KEYWORDS = {
            'налево', 'влево', 'левее', 'левую', 'левый', 'лево', 'на лево'
        }

        # --- Направление ВПРАВО ---
        self.TURN_RIGHT_KEYWORDS = {
            'направо', 'вправо', 'правее', 'правую', 'правый', 'право', 'на право'
        }

        # --- Команды ОСТАНОВКИ ---
        self.STOP_KEYWORDS = {
            # Основные
            'стоп', 'стоять', 'остановиться', 'остановка', 'замереть', 'прекратить', 'тормози', 'стой',
            # Синонимы и разговорные
            'замри', 'застынь', 'хватит', 'достаточно', 'тормоз', 'отставить', 'стопэ', 'стопе', 'ни с места',
            # Ошибки распознавания
            'столб', 'строй'
        }

        # --- Увеличение СКОРОСТИ ---
        self.SPEED_FASTER_KEYWORDS = {
            # Основные
            'быстро', 'быстрее', 'побыстрее', 'скорее', 'резче', 'ускориться', 'живо', 'поживее',
            # Разговорные и повелительные
            'быстрей', 'скорей', 'газуй', 'жми', 'гони', 'ускорься', 'давай быстрее', 'шустрее', 'резво',
            # Существительные и описания
            'ускорение', 'быстрый', 'резкий', 'максимальная', 'полный вперёд', 'быстро-быстро'
        }

        # --- Уменьшение СКОРОСТИ ---
        self.SPEED_SLOWER_KEYWORDS = {
            # Основные
            'медленно', 'медленнее', 'помедленнее', 'плавно', 'тише', 'потише', 'неспеша', 'не спеша',
            # Повелительные
            'замедлись', 'притормози', 'сбавь скорость', 'не спеши',
            # Описания и синонимы
            'замедление', 'медленный', 'плавный', 'тихий ход', 'минимальная', 'спокойнее', 'аккуратнее', 'осторожнее'
        }

        # --- Единицы измерения: МЕТРЫ ---
        self.DISTANCE_UNITS_M = {
            'метр', 'м', 'метра', 'метров', 'метро', 'метов'
        }

        # --- Единицы измерения: САНТИМЕТРЫ ---
        self.DISTANCE_UNITS_CM = {
            'сантиметр', 'см', 'сантиметра', 'сантиметров', 'сантиметре'
        }

        # --- Единицы измерения: ГРАДУСЫ ---
        self.ANGLE_UNITS = {
            'градус', 'град', 'градуса', 'градусов', 'радус'
        }
    def _parse_number_from_lemmas(self, lemmas: List[str]) -> Optional[float]:
        if len(lemmas) == 1 and lemmas[0] in ('полтора', 'полторы'): return 1.5
        total, current_chunk_val = 0.0, 0.0
        for lemma in lemmas:
            if lemma in self._NUMBER_WORDS:
                current_chunk_val += self._NUMBER_WORDS[lemma]
            elif lemma in self._SCALE_WORDS:
                scale = self._SCALE_WORDS[lemma]
                total += (current_chunk_val if current_chunk_val != 0 else 1.0) * scale
                current_chunk_val = 0.0
        total += current_chunk_val
        return total if total > 0 or any(l in ('ноль', 'нуль') for l in lemmas) else None

    def process_text(self, text: str) -> Optional[CommandInterface]:
        if not self.nlp: return None
        doc = self.nlp(text.lower())
        print(text)
        value, unit = None, None
        move_direction, turn_direction = 0, 0
        speed_modifier = 1.0

        i = 0
        while i < len(doc):
            token = doc[i]
            num_val, num_tokens_len = None, 0

            # Попытка 1: Распознать цифру
            if token.pos_ == "NUM" and token.text.replace('.', '', 1).replace(',', '', 1).isdigit():
                try:
                    num_val, num_tokens_len = float(token.text.replace(',', '.')), 1
                except ValueError:
                    pass
            # Попытка 2: Распознать число из слов
            else:
                num_phrase_lemmas, j = [], i
                while j < len(doc) and doc[j].lemma_ in self.ALL_NUM_WORDS:
                    num_phrase_lemmas.append(doc[j].lemma_)
                    j += 1
                if num_phrase_lemmas:
                    num_val = self._parse_number_from_lemmas(num_phrase_lemmas)
                    num_tokens_len = len(num_phrase_lemmas)

            # Если число найдено, ищем единицу измерения и сохраняем
            if num_val is not None:
                value = num_val  # Сохраняем значение по умолчанию
                unit_token_index = i + num_tokens_len
                if unit_token_index < len(doc):
                    next_token_lemma = doc[unit_token_index].lemma_
                    if next_token_lemma in self.DISTANCE_UNITS_M:
                        unit = 'distance'
                    elif next_token_lemma in self.DISTANCE_UNITS_CM:
                        value /= 100.0
                        unit = 'distance'
                    elif next_token_lemma in self.ANGLE_UNITS:
                        unit = 'angle'
                i += num_tokens_len  # Пропускаем обработанные токены
            else:
                i += 1  # Если число не найдено, переходим к следующему токену

        # Находим все ключевые слова
        lemmas = {token.lemma_ for token in doc}
        is_stop = bool(lemmas.intersection(self.STOP_KEYWORDS))
        is_move_forward = bool(lemmas.intersection(self.MOVE_FORWARD_KEYWORDS))
        is_move_backward = bool(lemmas.intersection(self.MOVE_BACKWARD_KEYWORDS))
        is_turn_left = bool(lemmas.intersection(self.TURN_LEFT_KEYWORDS))
        is_turn_right = bool(lemmas.intersection(self.TURN_RIGHT_KEYWORDS))
        is_generic_turn = bool(lemmas.intersection(self.TURN_KEYWORDS))

        if bool(lemmas.intersection(self.SPEED_FASTER_KEYWORDS)):
            speed_modifier = self.SPEED_FASTER_MULTIPLIER
        elif bool(lemmas.intersection(self.SPEED_SLOWER_KEYWORDS)):
            speed_modifier = self.SPEED_SLOWER_MULTIPLIER

        # --- ЭТАП 2: ПРИНЯТИЕ РЕШЕНИЯ НА ОСНОВЕ СОБРАННЫХ ДАННЫХ ---
        if is_stop: return StopCommand()

        # Определяем направления
        if is_move_forward: move_direction = 1
        if is_move_backward: move_direction = -1
        if is_turn_left: turn_direction = 1
        if is_turn_right: turn_direction = -1

        command_type = None
        has_move_keyword = is_move_forward or is_move_backward
        has_turn_keyword = is_generic_turn or is_turn_left or is_turn_right

        if has_turn_keyword:
            command_type = 'turn'
        elif has_move_keyword:
            command_type = 'move'
        elif unit == 'angle':
            command_type = 'turn'
        elif unit == 'distance':
            command_type = 'move'

        # --- ЭТАП 3: СОЗДАНИЕ ОБЪЕКТА КОМАНДЫ ---
        if command_type == 'turn':
            if turn_direction == 0 and value is not None:
                turn_direction = 1
            elif turn_direction == 0:
                turn_direction = 1

            angular_speed = self.DEFAULT_ANGULAR_SPEED * turn_direction * speed_modifier
            angle_rad = math.radians(value) * turn_direction if unit == 'angle' and value is not None else None
            return TurnCommand(angular_speed=angular_speed, angle=angle_rad )

        if command_type == 'move':
            if move_direction == 0: move_direction = 1
            linear_speed = self.DEFAULT_LINEAR_SPEED * move_direction * speed_modifier
            distance_m = value * move_direction if unit == 'distance' and value is not None else None
            return MoveCommand(linear_speed=linear_speed, distance=distance_m)

        return None