from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QScrollArea, \
    QFrame, QLabel, QHBoxLayout, QWidget, QMessageBox, QLineEdit
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QColor, QBrush, QPen, QFont
from PyQt5.QtCore import Qt, QSize, QRectF, QPoint,QObject, QEvent
from pynput import mouse
import sys
from PathTool import resource_path
import requests

class InfoWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.listener = None
        self.parent = parent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(340, 340)

        # Основной лейаут
        self.central_search_widget_layout = QVBoxLayout(self)
        self.central_search_widget_layout.setSpacing(5)
        self.central_search_widget_layout.setAlignment(Qt.AlignTop)
        self.central_search_widget_layout.setContentsMargins(40, 60, 40, 20)

        # Поле ввода поиска

        label_FIO = QLabel("Фамилия, имя, отчество")
        label_FIO.setStyleSheet('color: #696969; font-family: Microsoft Sans Serif; font-size: 14px; padding-left: 5px;')
        self.line_FIO = QLineEdit()
        self.line_FIO.setFixedHeight(50)
        self.line_FIO.setStyleSheet('''background:transparent;
                                   color: #909090;
                                   border: 1px solid #757575;
                                   border-radius: 12px;
                                   font-family: Microsoft Sans Serif;
                                   font-size: 20px;
                                   padding-left: 10px;''')


        label_address = QLabel("Telegram ID")
        label_address.setStyleSheet(
            'color: #696969; font-family: Microsoft Sans Serif; font-size: 14px; padding-left: 5px;')
        self.line_address = QLineEdit()
        self.line_address.setFixedHeight(50)
        self.line_address.setStyleSheet('''background:transparent;
                                    color: #909090;
                                    border: 1px solid #757575;
                                    border-radius: 12px;
                                    font-family: Microsoft Sans Serif;
                                    font-size: 20px;
                                    padding-left: 10px;''')


        self.add_inhabitant =  QPushButton('Сохранить')
        self.add_inhabitant.clicked.connect(self.update_info)
        self.add_inhabitant.setFixedHeight(50)
        self.add_inhabitant.setStyleSheet('''background: #3FFFAC; color: #757575;
         border-radius: 12px; font-family: Microsoft Sans Serif; font-size: 18px;''')

        self.spacer = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Minimum)


        self.central_search_widget_layout.addWidget(label_address)
        self.central_search_widget_layout.addWidget(self.line_address)
        self.central_search_widget_layout.addWidget(label_FIO)
        self.central_search_widget_layout.addWidget(self.line_FIO)
        self.central_search_widget_layout.addItem(self.spacer)
        self.central_search_widget_layout.addWidget(self.add_inhabitant)


    def start_listener(self):
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Отрисовка основного фона с закругленными углами
        rounded_rect = QRectF(0, 0, self.width(), self.height())
        radius = 45
        path = QPainterPath()
        path.addRoundedRect(rounded_rect, radius, radius)
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)


    def on_click(self, x, y, button, pressed):
        if not pressed:
            return
        global_pos = QPoint(x, y)
        if not self.rect().contains(self.mapFromGlobal(global_pos)) and self.isVisible():
            self.close()
            self.listener.stop()


    def set_info(self, name, tg_id):
        self.line_FIO.setText(name)
        self.line_address.setText(tg_id)

    def update_info(self):
        self.parent.name = self.line_FIO.text()
        self.parent.update_label()
        update_resident_name(self.parent.tg_id, self.line_FIO.text())
        self.close()
        self.listener.stop()


def update_resident_name(tg_id, new_name):
    tg_id = int(tg_id)
    url = f"http://localhost:8000/parking/residents/{tg_id}"
    params = {
        "new_name": new_name
    }
    try:
        response = requests.put(url, params=params)
        response.raise_for_status()

        if response.status_code == 200:
            print(f"Имя жителя с tg_id={tg_id} успешно изменено на '{new_name}'.")
            return True
        else:
            print(f"Не удалось обновить имя. Код ответа: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = InfoWindow()
    widget.start_listener()
    widget.show()


    sys.exit(app.exec_())