from importlib import reload

from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets


class MainMenu(QtWidgets.QMainWindow):
    def __init__(self, actions):
        QtWidgets.QMainWindow.__init__(self, parent=None, flags=Qt.Window)
        self.setWindowTitle("Procedural Generation")

        box = QtWidgets.QWidget(flags=Qt.Widget)
        vlayout = QtWidgets.QVBoxLayout(box)
        for action in actions:
            btn = QtWidgets.QPushButton()
            btn.setText(action.label)
            btn.clicked.connect(action.trigger)
            vlayout.addWidget(btn, alignment=Qt.AlignCenter)
        self.setCentralWidget(box)

        self.resize(200, len(actions) * 40)