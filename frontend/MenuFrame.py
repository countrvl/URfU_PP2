from PyQt5.QtCore import Qt, QRectF, QSize
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect

from PathTool import resource_path
from RegistrationForm import RegistrationWindow
from SearchWidget import SearchWidget
from TitleBar import CustomTitleBar
from UserList import UserListWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(1200, 750)

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setAlignment(Qt.AlignTop)

        self.title_bar = CustomTitleBar(self)
        self.search_widget = SearchWidget()
        self.user_list = UserListWidget()
        self.widget_add = RegistrationWindow()

        self.add_user = QPushButton()
        self.add_user.setFixedSize(QSize(64,64))

        self.add_user.setStyleSheet('border-radius: 12px; background: white;')
        self.add_user.setContentsMargins(0,0,0,0)
        self.add_user.setIcon(QIcon(resource_path('assets/add_user.png')))
        self.add_user.setIconSize(QSize(32,32))
        self.add_user.clicked.connect(self.create_user)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 0)
        self.add_user.setGraphicsEffect(shadow)



        self.main_layout.addWidget(self.title_bar)
        self.main_layout.addWidget(self.search_widget, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(self.user_list)
        self.main_layout.addWidget(self.add_user, alignment=Qt.AlignRight)


        self.setCentralWidget(self.main_widget)



    def create_user(self):
        self.widget_add.show()
        self.widget_add.start_listener()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(painter.Antialiasing)
        rounded_rect = self.rect()
        rounded_rect_f = QRectF(rounded_rect)
        radius = 15
        path = QPainterPath()
        path.addRoundedRect(rounded_rect_f, radius, radius)
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()


    def mouseMoveEvent(self, event):
        if self._is_dragging:
            self.move(event.globalPos() - self._drag_start_position)
            event.accept()


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            event.accept()



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())