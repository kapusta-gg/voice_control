from pyqtgraph.Qt import QtWidgets, QtCore, QtGui


class CommandsList(QtWidgets.QMainWindow):
    def __init__(self, logger=None):
        self._logger = logger
        super().__init__()

        # Устанавливаем минимальный размер, но позволяем окну растягиваться
        self.setMinimumSize(400, 560)
        
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
        self.MOVE_FORWARD_KEYWORDS = {
            'вперед', 'вперёд', 'прямо', 'ехать', 'проехать', 'двигаться', 'переместиться', 'идти',
        }

        self.MOVE_BACKWARD_KEYWORDS = {
            'назад', 'отъехать', 'сдать', 'отступить', 'пятиться',
            'отъезжай', 'откатись', 'сдай назад', 'двигай назад', 'задний ход',
        }

        self.TURN_KEYWORDS = {
            'повернуть', 'развернуться', 'крутиться', 'поворот',
            'поверни', 'повернись', 'разверни', 'развернись', 'крутись', 'покрутись', 'вертись',
            'вращайся', 'поворачивай', 'разворачивайся', 'вращение',
        }

        self.TURN_LEFT_KEYWORDS = {
            'налево', 'влево', 'левее', 'левую', 'левый', 'лево', 'на лево'
        }

        self.TURN_RIGHT_KEYWORDS = {
            'направо', 'вправо', 'правее', 'правую', 'правый', 'право', 'на право'
        }

        self.STOP_KEYWORDS = {
            'стоп', 'стоять', 'остановиться', 'остановка', 'замереть', 'прекратить', 'тормози', 'стой',
            'замри', 'тормоз', 'отставить',
        }

        self.SPEED_FASTER_KEYWORDS = {
            'быстро', 'быстрее', 'побыстрее', 'скорее', 'резче', 'ускориться', 'живо', 'поживее',
            'быстрей', 'скорей', 'ускорься', 'давай быстрее', 'шустрее',
        }

        self.SPEED_SLOWER_KEYWORDS = {
            'медленно', 'медленнее', 'помедленнее', 'плавно', 'тише', 'потише', 'неспеша', 'не спеша',
            'замедлись', 'притормози', 'сбавь скорость',
            'тихий ход', 'минимальная', 'спокойнее', 'аккуратнее', 'осторожнее'
        }

        self.DISTANCE_UNITS_M = {
            'метр', 'м', 'метра', 'метров'
        }

        self.DISTANCE_UNITS_CM = {
            'сантиметр', 'см', 'сантиметра', 'сантиметров'
        }

        self.ANGLE_UNITS = {
            'градус', 'град', 'градуса', 'градусов'
        }

        self.COMMANDS_TEMPLATE = {
            "Повернись на <i><b>{n}</b></i> градусов",
            "Проедь <i><b>{n}</b></i> метров/сантиметров вперед/назад",
            "Повернись налево/направо",
            "Езжай вперед/назад",
            "Ускорься/замедлись"
        }
        
        self.tab_widget = QtWidgets.QTabWidget()
        # Делаем табы растягиваемыми
        self.tab_widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

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
        
        layout = QtWidgets.QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5) 
        
        max_rows = max(len(arg) for arg in args)
        
        for i in range(len(names)):
            t = list(args[i])
            
            title_label = TitleLabel(f"<b>{names[i]}</b>")
            layout.addWidget(title_label, 0, i)
            
            for j in range(len(t)):
                info_label = InfoLabel(t[j])
                layout.addWidget(info_label, j + 1, i)
            
            for j in range(len(t) + 1, max_rows + 1):
                spacer = QtWidgets.QWidget()
                spacer.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
                layout.addWidget(spacer, j, i)
        
        for i in range(len(names)):
            layout.setColumnStretch(i, 1)
        
        for j in range(1, max_rows + 2):
            layout.setRowStretch(j, 1)
            
        self.setLayout(layout)


class TitleLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumHeight(40)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.setStyleSheet('''
            background-color: lightblue;
            border: 1px solid #555;
            margin: 0px;
            padding: 5px;
            font-size: 12px;
        ''')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)


class InfoLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumHeight(30)
        
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.setStyleSheet('''
            border: 1px solid #555;
            border-radius: 5px;
            margin: 2px;
            padding: 5px;
            font-size: 11px;
        ''')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        #
        self.setWordWrap(True)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication([])
    ex = CommandsList()
    ex.show()
    sys.exit(app.exec())