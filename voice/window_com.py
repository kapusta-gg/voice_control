from pyqtgraph.Qt import QtWidgets, QtCore, QtGui


class CommandsList(QtWidgets.QMainWindow):
    def __init__(self, logger=None):
        self._logger = logger
        super().__init__()

        self.resize(300, 560)
        #self._logger.info("Открыто окно команд")

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
        }

        # --- Движение НАЗАД ---

        self.MOVE_BACKWARD_KEYWORDS = {
            'назад', 'отъехать', 'сдать', 'отступить', 'пятиться',
            'отъезжай', 'откатись', 'сдай назад', 'двигай назад', 'задний ход',
        }

        # --- Общие команды ПОВОРОТА ---
        self.TURN_KEYWORDS = {
            'повернуть', 'развернуться', 'крутиться', 'поворот',
            'поверни', 'повернись', 'разверни', 'развернись', 'крутись', 'покрутись', 'вертись',
            'вращайся', 'поворачивай', 'разворачивайся', 'вращение',
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
            'стоп', 'стоять', 'остановиться', 'остановка', 'замереть', 'прекратить', 'тормози', 'стой',
            'замри', 'тормоз', 'отставить',
        }

        # --- Увеличение СКОРОСТИ ---
        self.SPEED_FASTER_KEYWORDS = {
            'быстро', 'быстрее', 'побыстрее', 'скорее', 'резче', 'ускориться', 'живо', 'поживее',
            'быстрей', 'скорей', 'ускорься', 'давай быстрее', 'шустрее',
        }

        # --- Уменьшение СКОРОСТИ ---
        self.SPEED_SLOWER_KEYWORDS = {
            'медленно', 'медленнее', 'помедленнее', 'плавно', 'тише', 'потише', 'неспеша', 'не спеша',
            'замедлись', 'притормози', 'сбавь скорость',
            'тихий ход', 'минимальная', 'спокойнее', 'аккуратнее', 'осторожнее'
        }

        # --- Единицы измерения: МЕТРЫ ---
        self.DISTANCE_UNITS_M = {
            'метр', 'м', 'метра', 'метров'
        }

        # --- Единицы измерения: САНТИМЕТРЫ ---
        self.DISTANCE_UNITS_CM = {
            'сантиметр', 'см', 'сантиметра', 'сантиметров'
        }

        # --- Единицы измерения: ГРАДУСЫ ---
        self.ANGLE_UNITS = {
            'градус', 'град', 'градуса', 'градусов'
        }

        # --- Примеры команд ---
        self.COMMANDS_TEMPLATE = {
            "Повернись на <i><b>{n}</b></i> градусов",
            "Проедь <i><b>{n}</b></i> метров/сантиметров вперед/назад",
            "Повернись налево/направо",
            "Езжай вперед/назад",
            "Ускорься/замедлись"
        }
        self.tab_widget = QtWidgets.QTabWidget()

        self.move_widget = InfoTabWindow(
            ["Вперед", "Назад", "Остановка"],
            self.MOVE_FORWARD_KEYWORDS, self.MOVE_BACKWARD_KEYWORDS, self.STOP_KEYWORDS
            )
        self.turn_widget = InfoTabWindow(
            ["Общее", "Влево", "Вправо"], 
            self.TURN_KEYWORDS, self.TURN_LEFT_KEYWORDS, self.TURN_RIGHT_KEYWORDS
            )
        self.speed_widget = InfoTabWindow(
            ["Ускорение", "Замедление"], 
            self.SPEED_FASTER_KEYWORDS, self.SPEED_SLOWER_KEYWORDS
            )
        self.measurment_widget = InfoTabWindow(
            ["М", "См", "Градус"], 
            self.DISTANCE_UNITS_M, self.DISTANCE_UNITS_CM, self.ANGLE_UNITS
            )
        self.commands_widget = InfoTabWindow(
            ["Примеры команд"],
            self.COMMANDS_TEMPLATE
        )

        self.tab_widget.addTab(self.move_widget, "Движение")
        self.tab_widget.addTab(self.turn_widget, "Поворот")
        self.tab_widget.addTab(self.speed_widget, "Скорость")
        self.tab_widget.addTab(self.measurment_widget, "ЕИ")
        self.tab_widget.addTab(self.commands_widget, "Примеры")

        self.setCentralWidget(self.tab_widget)


class InfoTabWindow(QtWidgets.QWidget):
    def __init__(self, names, *args):
        super().__init__()
        
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем горизонтальный контейнер для колонок
        columns_widget = QtWidgets.QWidget()
        columns_layout = QtWidgets.QHBoxLayout()
        columns_layout.setSpacing(0)
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_widget.setLayout(columns_layout)
        
        for i in range(len(names)):
            # Создаем вертикальную колонку
            column_widget = QtWidgets.QWidget()
            column_layout = QtWidgets.QVBoxLayout()
            column_layout.setSpacing(0)
            column_layout.setContentsMargins(0, 0, 0, 0)
            column_widget.setLayout(column_layout)
            
            # Добавляем заголовок
            title_label = TitleLabel(f"<b>{names[i]}</b>")
            column_layout.addWidget(title_label)
            
            # Добавляем элементы
            t = list(args[i])
            for item in t:
                info_label = InfoLabel(item)
                column_layout.addWidget(info_label)
            
            # Добавляем растягивающий спейсер в конец колонки
            column_layout.addStretch(1)
            
            # Добавляем колонку в горизонтальный layout
            columns_layout.addWidget(column_widget)
        
        # Добавляем растягивающий спейсер в конец горизонтального layout
        columns_layout.addStretch(1)
        
        layout.addWidget(columns_widget)
        self.setLayout(layout)


class TitleLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedHeight(40)
        self.setMinimumWidth(200)
        self.setStyleSheet('''
                               background-color: lightblue;
                               border: 1px solid #555;
                               margin: 0px;
                               padding: 0px;
                           ''')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)


class InfoLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedHeight(30)  # Фиксированная высота
        self.setMinimumWidth(90)
        self.setMaximumWidth(300)
        self.setStyleSheet('''
                               border: 1px solid #555;
                               margin: 0px;
                               padding: 0px;
                           ''')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication([])
    ex = CommandsList()
    ex.show()
    sys.exit(app.exec())