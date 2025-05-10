from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QScrollArea, \
    QFrame, QLabel, QHBoxLayout, QWidget, QMessageBox, QLineEdit
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QColor, QBrush, QPen, QFont
from PyQt5.QtCore import Qt, QSize, QRectF, QPoint,QObject, QEvent
from PathTool import resource_path
from User import User
import sys
from WidgetController import WidgetController
import requests



class UserListWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.controller = WidgetController()
        self.controller.register_widget('UserList', self)
        self.central_search_widget_layout = QVBoxLayout(self)
        self.central_search_widget_layout.setSpacing(10)
        self.central_search_widget_layout.setAlignment(Qt.AlignTop)
        self.central_search_widget_layout.setContentsMargins(0, 20, 0, 0)




        self.scroll_area_wrapper = QFrame()
        self.scroll_area_wrapper.setStyleSheet("""
                   QFrame {
                       background: white; /* Фон для обёртки */
                       border: none;
                   }
               """)
        self.scroll_area_wrapper_layout = QVBoxLayout(self.scroll_area_wrapper)
        self.scroll_area_wrapper_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Настраиваем стиль ScrollArea
        self.scroll_area.setStyleSheet(""" QScrollArea {
                                            border: none; border-radius: 4px; background: white;
                                            }
                                            QScrollBar:vertical { width: 2px; background: white;
                                            }
                                            QScrollBar:horizontal { height: 10px; background: white;
                                            }
                                            QScrollBar::handle { background: #C3C3C3; border-radius: 1px;
                                            }
                                            QScrollBar::handle:hover { background: #a0a0a0;
                                            }
                                            QScrollBar::add-page { background: none; margin: 0;
                                            }
                                            QScrollBar::sub-page { background: none; margin: 0;
                                            }
                                            QScrollBar::add-line, QScrollBar::sub-line { background: none; border: none; }""")
        self.frame = QFrame()
        self.frame.setStyleSheet("""
                    QFrame {
                        background: transparent;
                        border-radius: 4px;
                    }
                """)
        self.frame_layout = QVBoxLayout(self.frame)
        self.frame_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.frame)


        self.scroll_area_wrapper_layout.addWidget(self.scroll_area)

        spacer = QSpacerItem(12, 12, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.central_search_widget_layout.addWidget(self.scroll_area_wrapper)
        self.central_search_widget_layout.addItem(spacer)



        self.all_buttons = []
        self.populate_buttons()


    def delete_button(self, object):
        self.all_buttons.remove(object)
        self.frame_layout.removeWidget(object)


    def create_user(self, name, tg_id):
        user = User(name, tg_id)
        self.frame_layout.addWidget(user)
        self.all_buttons.append(user)



    def populate_buttons(self):
        residents = fetch_residents()

        if not residents:
            print("Нет данных о жителях.")
            return

        for resident in residents:
            name = resident.get('name', 'Без имени')
            tg_id = resident.get('tg_id', 'Н/Д')

            user_button = User(name, tg_id)
            self.frame_layout.addWidget(user_button)
            self.all_buttons.append(user_button)


def fetch_residents():
        url = "http://localhost:8000/parking/residents"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("residents", [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            return []