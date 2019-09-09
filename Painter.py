from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QLabel, QSpinBox
from PyQt5.QtWidgets import QMainWindow, QComboBox, QHBoxLayout, QWidget, QColorDialog, \
    QDialog, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPen, \
    QLinearGradient, QRadialGradient
from Figures import Line, Hand, Rectangle, Circle, Combiner, Object
from copy import deepcopy
from math import sqrt


class Painter(QMainWindow):

    def __init__(self, width=640, height=480, color=QColor('white'), name='', objects=None):

        super().__init__()

        if objects is None:
            objects = []
        self.objects = objects

        self.file_name = name

        self.height = height
        self.width = width
        self.color = color

        self.temp = []
        self.history = [[]]
        self.history_flag = False
        self.state_number = 0

        self.click = False
        self.instrument = None
        self.cur_object = None

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

        self.edit_fl = False
        self.is_moving = False

        self.make_forms()

        self.gr_x1 = None
        self.gr_x2 = None
        self.gr_y1 = None
        self.gr_y2 = None

        self.line_color = QColor('blue')
        self.fill_color = None

    def make_forms(self):
        self.instruments = QComboBox(self)
        self.instruments.addItems(["Line", "Hand", "Rectangle", "Circle", "Select"])
        self.instruments.move(10, 50)
        self.instruments.resize(200, 70)
        self.instruments.currentIndexChanged.connect(self.instrumentChanged)

        self.color_button = QPushButton('COLOR', self)
        self.color_button.move(220, 50)
        self.color_button.resize(150, 70)
        self.color_button.clicked.connect(self.color_picker)

        self.thick_button = QSpinBox(self)
        self.thick_button.move(530, 50)
        self.thick_button.resize(100, 70)
        self.thick_button.setMinimum(2)
        self.thick_button.setMaximum(60)
        self.thick_button.valueChanged.connect(self.spinboxChanged)

        self.thick_lbl = QLabel('Thickness', self)
        self.thick_lbl.move(530, -10)
        self.thick_lbl.resize(120, 70)

        self.combine_button = QPushButton('COMBINE', self)
        self.combine_button.move(640, 50)
        self.combine_button.resize(150, 70)
        self.combine_button.clicked.connect(self.combine)
        self.combine_button.hide()

        self.delete_button = QPushButton('DELETE', self)
        self.delete_button.move(800, 50)
        self.delete_button.resize(100, 70)
        self.delete_button.clicked.connect(self.delete)
        self.delete_button.hide()

        self.change_color_button = QPushButton('COLOR', self)
        self.change_color_button.move(220, 50)
        self.change_color_button.resize(150, 70)
        self.change_color_button.clicked.connect(self.change_color)
        self.change_color_button.hide()

        self.background_button = QPushButton('BACKGROUND', self)
        self.background_button.move(2500, 50)
        self.background_button.resize(200, 70)
        self.background_button.clicked.connect(self.settings)

        self.fill_button = QPushButton('FILL', self)
        self.fill_button.move(910, 50)
        self.fill_button.resize(100, 70)
        self.fill_button.clicked.connect(self.fill)
        self.fill_button.hide()

        self.save_button = QPushButton('SAVE', self)
        self.save_button.move(1500, 50)
        self.save_button.resize(100, 70)
        self.save_button.clicked.connect(self.save)
        self.save_button.show()

        self.grad_instruments = QComboBox(self)
        self.grad_instruments.addItems(["Linear", "Radial"])
        self.grad_instruments.move(10, 50)
        self.grad_instruments.resize(1300, 70)
        self.grad_instruments.hide()

    def save(self):
        from SVGParser import SVGParser as svg

        s = svg(self.file_name).save2svg(self)

    def instrumentChanged(self):
        self.get_instrument()
        for o in self.objects:
            if o.selected:
                o.deselect()
        self.is_moving = False
        self.click = False
        self.cur_object = None
        self.update()

    def set_instrument(self, o):
        if isinstance(o, Circle):
            self.instrument = 'Circle'
        elif isinstance(o, Rectangle):
            self.instrument = 'Rectangle'
        elif isinstance(o, Line):
            self.instrument = 'Line'
        elif isinstance(o, Hand):
            self.instrument = 'Hand'
        elif isinstance(o, Object):
            self.instrument = 'Object'

    def edit(self):
        for i in self.objects:
            if i.selected:
                self.cur_object = i
                break
        if self.cur_object is not None:
            self.edit_fl = True
            self.click = True
            self.set_instrument(self.cur_object)

    def edit_ok(self):
        self.edit_fl = False
        self.cur_object.deselect()
        self.cur_object.stop_moving()
        self.instrument = 'Select'
        self.cur_object = None
        self.click = False
        self.is_moving = False

    def settings(self):
        form = Form(self)
        form.setFocus()

        vbox = QVBoxLayout()
        vbox.addWidget(form)
        self.setLayout(vbox)

        form.setGeometry(500, 500, 500, 800)
        form.show()

    def get_line_thick(self):
        th = int(self.thick_button.text())
        return th

    def color_picker(self):
        self.line_color = QColorDialog.getColor()

    def change_thick(self, th):

        for e in self.objects:
            if e.selected:
                e.set_thickness(th)
        self.history_flag = True
        self.update()

    def fill(self):

        form = FillForm(self)
        form.setFocus()

        vbox = QVBoxLayout()
        vbox.addWidget(form)
        self.setLayout(vbox)

        form.setGeometry(500, 500, 500, 800)
        form.show()
        form.exec()

        for e in self.objects:
            if e.selected:
                e.fill(self.fill_color)
        self.history_flag = True
        self.fill_color = None
        self.update()

    def spinboxChanged(self, value):
        self.change_thick(value)

    def change_color(self):
        self.color_picker()
        for e in self.objects:
            if e.selected:
                e.deselect()
                e.set_color(self.line_color)
        self.history_flag = True
        self.update()

    def get_instrument(self):
        self.instrument = self.instruments.currentText()
        if self.instrument == "Select":

            self.instruments.show()
            self.thick_button.show()
            self.change_color_button.show()
            self.combine_button.show()
            self.delete_button.show()
            self.fill_button.show()
            self.color_button.hide()

        elif self.instrument == 'Line' \
                or self.instrument == "Hand" \
                or self.instrument == "Rectangle" \
                or self.instrument == "Circle":
            self.combine_button.hide()

            self.change_color_button.hide()
            self.combine_button.hide()
            self.delete_button.hide()
            self.fill_button.hide()

            self.instruments.show()
            self.thick_button.show()
            self.color_button.show()
        self.update()

    def in_bounds(self, x, y):

        if self.is_moving and (
                self.cur_object is not None) and (
                not self.cur_object.in_bounds(self.width, self.height)):

            self.edit_ok()
            return False

        return 40 <= x + self.get_line_thick() / 2 <= self.width + 40 and (
                150 <= y + self.get_line_thick() / 2 <= 150 + self.height) and (
                40 <= x - self.get_line_thick() / 2 <= self.width + 40) and (
                150 <= y - self.get_line_thick() / 2 <= 150 + self.height)

    def mousePressEvent(self, event):

        x, y = event.pos().x(), event.pos().y()

        if not self.in_bounds(x, y):
            return

        if not self.edit_fl:
            self.get_instrument()
        self.get_line_thick()

        if self.instrument != "Select":

            if self.click and self.is_moving and self.cur_object is not None:
                self.edit_ok()
                self.click = False
                return

            self.history = self.history[:self.state_number + 1]
            self.history_flag = True

            if self.click:
                self.click = False

                if self.in_bounds(x, y):
                    if self.instrument == 'Circle' and self.cur_object is not None:
                        if self.circle_in_bounds(x, y):
                            if self.cur_object is not None:
                                if self.is_moving:
                                    self.cur_object.move(x, y)
                                else:
                                    self.cur_object.set_end_coord(x, y)
                    else:

                        if self.cur_object is not None:
                            if self.is_moving:

                                self.cur_object.move(x, y)
                            else:
                                self.cur_object.set_end_coord(x, y)

                    if not self.edit_fl:
                        self.objects.append(self.cur_object)
                    self.cur_object.set_color(self.line_color)
                    self.cur_object.set_thickness(self.get_line_thick())

                    if self.edit_fl:
                        self.edit_ok()
            else:
                if self.in_bounds(x, y):
                    self.click = True
                    if self.instrument == "Line":
                        self.cur_object = Line(x, y)
                    elif self.instrument == "Hand":
                        self.cur_object = Hand(x, y)
                    elif self.instrument == 'Rectangle':
                        self.cur_object = Rectangle(x, y)
                    elif self.instrument == 'Circle':
                        self.cur_object = Circle(x, y)

        else:

            self.history_flag = False
            for f in self.objects:
                if f.is_coord_on_figure(x, y):
                    if f.selected:
                        f.move_or_deselect(x, y)
                        if f.selected:
                            self.is_moving = True
                            self.edit()
                    else:
                        f.select()
                        self.is_moving = True
        self.update()

    def circle_in_bounds(self, x2, y2):

        if self.is_moving and not self.cur_object.in_bounds(self.width, self.height):
            return False
        xr = self.cur_object.x1
        yr = self.cur_object.y1
        x = x2 - xr
        y = y2 - yr
        rad = sqrt(x * x + y * y)
        return self.in_bounds(xr + rad, yr) and (
                self.in_bounds(xr - rad, yr)) and (
                self.in_bounds(xr, yr + rad)) and (
                self.in_bounds(xr, yr - rad))

    def mouseMoveEvent(self, e):
        y = e.pos().y()
        x = e.pos().x()

        if self.cur_object is not None and self.click:

            if self.in_bounds(x, y):
                if self.instrument == 'Circle' and self.cur_object is not None:
                    if self.circle_in_bounds(x, y):
                        if self.is_moving:
                            self.cur_object.move(x, y)
                        else:
                            self.cur_object.set_end_coord(x, y)
                else:
                    if self.is_moving:
                        self.cur_object.move(x, y)
                    else:
                        self.cur_object.set_end_coord(x, y)

            self.temp.append(self.cur_object)

        self.update()

    def get_max_x(self):
        return 40 + self.width

    def get_max_y(self):
        return 150 + self.height

    def draw_current_image(self):
        painter = QPainter(self)

        painter.fillRect(380, 50, 140, 70, self.line_color)
        painter.fillRect(40, 150, self.width, self.height, self.color)

        for e in self.objects:
            if e is not None:
                e.draw(painter, None, None, self.get_max_x(), self.get_max_y())
            else:
                self.objects.remove(e)
        for e in self.temp:
            if e is not None:
                e.draw(painter, self.line_color, self.get_line_thick(), None, None)
        self.temp = []

    def store_current_state(self):
        if self.history_flag and not self.click:
            self.history.append(deepcopy(self.objects))
            self.history_flag = False
            self.state_number += 1

    def paintEvent(self, e):

        self.draw_current_image()
        self.store_current_state()

    def keyPressEvent(self, event):

        key = event.key()
        if key == Qt.Key_Right:
            if self.state_number + 1 < len(self.history):
                self.state_number += 1
                self.objects = deepcopy(self.history[self.state_number])
                self.update()

        if key == Qt.Key_Left:
            if self.state_number - 1 >= 0:
                self.was_back = True
                self.state_number -= 1
                self.objects = deepcopy(self.history[self.state_number])
                self.update()

    def combine(self):
        li = []
        o = []
        obj = None
        for e in self.objects:
            if e.selected:
                e.deselect()
                if e is Object and obj is not None:
                    obj = e
                else:
                    li.append(e)
            else:
                o.append(e)
        self.history_flag = True
        o.append(Combiner.combine(li, obj))
        self.objects = o
        self.update()

    def delete(self):
        o = []
        for e in self.objects:
            if not e.selected:
                o.append(e)
        self.history_flag = True
        self.objects = o
        self.update()


class Form(QWidget):

    def __init__(self, p):
        super().__init__()

        self.p = p

        self.resize(100, 100)

        self.lbl_height = QLabel("Enter height", self)
        self.lbl_height.move(20, 20)
        self.lbl_height.resize(200, 50)
        self.height_box = QSpinBox(self)
        self.height_box.move(20, 70)
        self.height_box.resize(200, 70)
        self.height_box.setMinimum(200)
        self.height_box.setMaximum(1300)
        self.height_box.setValue(p.height)

        self.lbl_width = QLabel("Enter width", self)
        self.lbl_width.move(20, 140)
        self.lbl_width.resize(200, 70)
        self.width_box = QSpinBox(self)
        self.width_box.move(20, 190)
        self.width_box.resize(200, 70)
        self.width_box.setMinimum(200)
        self.width_box.setMaximum(3000)
        self.width_box.setValue(p.width)

        self.button = QPushButton('COLOR', self)
        self.button.move(20, 300)
        self.button.resize(200, 70)
        self.button.clicked.connect(self.color_picker)

        self.button = QPushButton('OK', self)
        self.button.move(20, 400)
        self.button.resize(200, 70)
        self.button.clicked.connect(self.on_click)

        self.color = p.color

    def color_picker(self):
        self.color = QColorDialog.getColor()
        self.update()

    def on_click(self):
        self.p.width = int(self.width_box.text())
        self.p.height = int(self.height_box.text())
        self.p.color = self.color
        self.close()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.fillRect(240, 300, 200, 70, self.color)


class FillForm(QDialog):

    def __init__(self, p):
        super().__init__()

        self.resize(400, 400)

        self.p = p

        self.first = None
        self.second = None
        self.click = False

        self.instruments = QComboBox(self)
        self.instruments.addItems(["Color", "Linear"])
        self.instruments.move(20, 300)
        self.instruments.resize(200, 70)
        self.instruments.currentIndexChanged.connect(self.instrumentChanged)

        self.button = QPushButton('OK', self)
        self.button.move(20, 400)
        self.button.resize(200, 70)
        self.button.clicked.connect(self.on_click)

        self.button0 = QPushButton('COLOR', self)
        self.button0.move(250, 50)
        self.button0.resize(200, 70)
        self.button0.clicked.connect(self.color1)

        self.button1 = QPushButton('COLOR 1', self)
        self.button1.move(250, 50)
        self.button1.resize(200, 70)
        self.button1.clicked.connect(self.color1)
        self.button1.hide()

        self.button2 = QPushButton('COLOR 2', self)
        self.button2.move(250, 130)
        self.button2.resize(200, 70)
        self.button2.clicked.connect(self.color2)
        self.button2.hide()

        self.instrument = 'Color'

        self.color = QColor('white')

        self.col1 = QColor('white')
        self.col2 = QColor('white')

    def instrumentChanged(self):
        self.instrument = self.instruments.currentText()
        if self.instrument == 'Color':
            self.button1.hide()
            self.button2.hide()
            self.button0.show()
        elif self.instrument == 'Linear':
            self.button1.show()
            self.button2.show()
            self.button0.hide()

    def color1(self):
        self.color_picker(True)

    def color2(self):
        self.color_picker(False)

    def color_picker(self, fl):
        if fl:
            self.col1 = QColorDialog.getColor()
        else:
            self.col2 = QColorDialog.getColor()
        self.update()

    def on_click(self):
        self.p.fill_color = self.color
        self.close()

    def paintEvent(self, e):
        painter = QPainter(self)

        if self.instrument == 'Color':
            if self.col1 is None:
                col = QColor('white')
            else:
                col = self.col1

            painter.fillRect(20, 50, 200, 200, col)

            self.color = FillFigure(self.col1)

        else:
            if self.col1 is None:
                col1 = QColor('white')
            else:
                col1 = self.col1
            if self.col2 is None:
                col2 = QColor('white')
            else:
                col2 = self.col2

            if self.first is None:
                self.first = [20, 50]
            if self.second is None:
                self.second = [21, 100]

            grad = QLinearGradient(self.first[0], self.first[1], self.second[0], self.second[1])
            grad.setColorAt(0, col1)
            grad.setColorAt(1, col2)
            painter.fillRect(20, 50, 200, 200, grad)

            self.color = FillFigure(self.col1, self.col2, self.first[0], self.first[1], self.second[0], self.second[1])

    def mousePressEvent(self, event):
        x, y = event.pos().x(), event.pos().y()

        if 20 <= x <= 220 and 50 <= y <= 250:

            if not self.click:
                self.click = True
                self.first = [x, y]

            else:
                self.click = False
                self.second = [x, y]
            self.update()


class FillFigure:

    def __init__(self, c1, c2=None, x1=None, y1=None, x2=None, y2=None):

        self.col1 = c1
        self.col2 = c2

        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def get_color(self):
        if self.col2 is None:
            return self.col1
        else:
            grad = QLinearGradient(self.x1, self.y1, self.x2, self.y2)
            grad.setColorAt(0, self.col1)
            grad.setColorAt(1, self.col2)
            return grad
