from PyQt5.QtCore import Qt, QPropertyAnimation, QSize
from PyQt5.QtGui import QIcon, QColor, QPainter, QPainterPath
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QApplication


class SearchWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)



        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 0)
        self.layout.setSpacing(0)



        self.line_edit = QLineEdit()
        self.line_edit.setWindowIcon(QIcon('assets/exit.png'))
        self.line_edit.setFixedSize(800, 60)
        self.line_edit.setAlignment(Qt.AlignCenter)
        self.line_edit.setPlaceholderText("Поиск...")
        self.line_edit.setStyleSheet('''
            QLineEdit {
                background: rgba(255, 255, 255);
                border-radius: 30px;
                border: 1px solid rgba(150, 150, 150, 124);
                padding-left: 12px;
                font-family: Roboto;
                font-style: Regular;
                color: #7D7D7D;
                font-size: 24px;
            }
        ''')


        self.layout.addWidget(self.line_edit)



