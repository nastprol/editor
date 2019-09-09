from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import QLineEdit, QPushButton, QLabel, QSpinBox, QComboBox
from PyQt5.QtWidgets import QColorDialog
import sys
from Painter import Painter
from PyQt5.QtGui import QColor


class Form(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(100, 100)

        self.lbl_height = QLabel("Enter height", self)
        self.lbl_height.move(20, 20)
        self.lbl_height.resize(200, 50)
        self.height_box = QSpinBox(self)
        self.height_box.move(20, 70)
        self.height_box.resize(200, 70)
        self.height_box.setMinimum(200)
        self.height_box.setMaximum(1300)

        self.lbl_width = QLabel("Enter width", self)
        self.lbl_width.move(20, 140)
        self.lbl_width.resize(200, 70)
        self.width_box = QSpinBox(self)
        self.width_box.move(20, 190)
        self.width_box.resize(200, 70)
        self.width_box.setMinimum(200)
        self.width_box.setMaximum(3000)

        self.button = QPushButton('COLOR', self)
        self.button.move(20, 400)
        self.button.resize(200, 70)
        self.button.clicked.connect(self.color_picker)

        self.button = QPushButton('START', self)
        self.button.move(20, 500)
        self.button.resize(200, 70)
        self.button.clicked.connect(self.on_click)

        self.lbl_name = QLabel("Enter file's name", self)
        self.lbl_name.move(20, 250)
        self.lbl_name.resize(200, 70)
        self.name_box = QLineEdit(self)
        self.name_box.move(20, 300)
        self.name_box.resize(200, 70)

        self.color = QColor('white')

    def color_picker(self):
        self.color = QColorDialog.getColor()

    def on_click(self):

        self.width = int(self.width_box.text())
        self.height = int(self.height_box.text())
        self.name = self.name_box.text()
        self.close()
        self.game = Game(self.width, self.height, self.color, self.name)
        self.setCentralWidget(self.game)
        self.game.setGeometry(0, 0, 2000, 1500)
        self.game.show()


class Game(QMainWindow):

    def __init__(self, w, h, col, name):
        super().__init__()
        self.painter = Painter(w, h, col, name)
        self.painter.setGeometry(0, 0, 3200, 1600)
        self.painter.show()


class Start(QMainWindow):

    def __init__(self):
        super().__init__()
        self.form = Form()

        self.form.setGeometry(500, 500, 500, 800)
        self.form.show()


if __name__ == '__main__':
    app = QApplication([])
    start = Start()
    sys.exit(app.exec_())
