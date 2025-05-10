from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5.QtCore import Qt, QSize
from InfoForm import InfoWindow
from PathTool import resource_path
from WidgetController import WidgetController
import requests

class User(QPushButton):
    def __init__(self, name, tg_id):
        super().__init__()
        self.controller = WidgetController()
        self.refresh_info_widget = InfoWindow(self)
        self.name = name
        self.tg_id = tg_id

        self.setStyleSheet("""
            QPushButton {
                background-color: #F3F3F3 ;
                color: #696969;
                border-radius: 18px;
                padding: 10px;
                font-family: Gilroy;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #F3F3F3;
            }
            QLabel {
            background: none;
            }
        """)

        self.setFixedHeight(60)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 0, 10, 0)



        self.label = QLabel(self.name)
        self.label.setStyleSheet('font-size: 20px; color: #696969; font-family: Gilroy; font-weight: Bold;')

        self.side_buttons = QWidget()
        self.side_layout = QHBoxLayout(self.side_buttons)

        self.info = QPushButton()
        self.info.setIcon(QIcon(resource_path('assets/info.png')))
        self.info.clicked.connect(self.get_info)

        self.delete = QPushButton()
        self.delete.setIcon(QIcon(resource_path('assets/delete.png')))
        self.delete.clicked.connect(self.delete_widget)

        self.side_layout.addWidget(self.info)
        self.side_layout.addWidget(self.delete)


        main_layout.addWidget(self.label)
        main_layout.addWidget(self.side_buttons, alignment=Qt.AlignRight)

    def get_info(self):
        self.refresh_info_widget.show()
        self.refresh_info_widget.set_info(self.name, self.tg_id)
        self.refresh_info_widget.start_listener()

    def delete_widget(self):
        self.controller.call_widget_method('UserList', 'delete_button', self)
        delete_resident(self.tg_id)

    def update_label(self):
        self.label.setText(self.name)


def delete_resident(tg_id):
    tg_id = int(tg_id)
    url = f"http://localhost:8000/parking/residents/{tg_id}"
    try:
        response = requests.delete(url)
        response.raise_for_status()
        if response.status_code == 204:
            print(f"Житель с tg_id={tg_id} успешно удален.")
            return True
        else:
            print(f"Не удалось удалить жителя. Статус: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при удалении жителя: {e}")














