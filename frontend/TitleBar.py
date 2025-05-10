from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PathTool import resource_path

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.resource_path = resource_path
        self.is_maximized = False
        self.setFixedHeight(30)

        # Минимизировать окно
        btn_minimize = QPushButton()
        btn_minimize.setFixedSize(24,24)
        btn_minimize.setStyleSheet('background:transparent;')
        icon_path = self.resource_path('assets/minimize.png')
        btn_minimize.setIcon(QIcon(icon_path))
        btn_minimize.setIconSize(QSize(24,24))
        btn_minimize.clicked.connect(self.parent.showMinimized)

        # Закрыть окно
        btn_close = QPushButton()
        btn_close.setFixedSize(22,24)
        btn_close.setStyleSheet('background:transparent;')
        icon_path = self.resource_path('assets/exit.png')
        btn_close.setIcon(QIcon(icon_path))
        btn_close.setIconSize(QSize(22,24))
        btn_close.clicked.connect(self.parent.close)

        # Макет кнопок
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignRight)
        layout.setContentsMargins(0, 6, 6, 0)
        layout.addWidget(btn_minimize)
        layout.addWidget(btn_close)

        self.setLayout(layout)


