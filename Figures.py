from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient
from PyQt5.QtCore import QPoint
from math import sqrt
import math


class Object:
    def __init__(self, figures=None):
        if figures is None:
            figures = list()
        self.figures = figures
        self.selected = False

        self.center_x = None
        self.center_y = None

        self.center = False

    def stop_moving(self):
        self.center = False

    def move_or_deselect(self, x, y):

        if self.center_x - 10 <= x <= self.center_x + 10 \
                and self.center_y - 10 <= y <= self.center_y + 10\
                or self.center:
            self.center = True
            self.move(x, y)
        else:
            self.deselect()

    def move(self, x, y):
        if self.center_x - 10 <= x <= self.center_x + 10 \
                and self.center_y - 10 <= y <= self.center_y + 10\
                or self.center:
            self.transport(x, y)

    def transport(self, x, y):
        dx = x - self.center_x
        dy = y - self.center_y
        self.transport_center(dx, dy)

    def transport_center(self, dx, dy):
        self.center_y += dy
        self.center_x += dx
        for l in self.figures:
            l.transport_center(dx, dy)

    def in_bounds(self, x, y):
        for f in self.figures:
            if not f.in_bounds(x, y):
                return False
        return True

    def set_central_coord(self):
        x_min = None
        y_min = None
        y_max = None
        x_max = None

        for f in self.figures:
            if x_min is None or x_min > f.x1:
                x_min = f.x1
            elif x_max is None or x_max < f.x1:
                x_max = f.x1

            if x_min is None or x_min > f.x2:
                x_min = f.x2
            elif x_max is None or x_max < f.x2:
                x_max = f.x2

            if y_min is None or y_min > f.y1:
                y_min = f.y1
            elif y_max is None or y_max < f.y1:
                y_max = f.y1

            if y_min is None or y_min > f.y2:
                y_min = f.y2
            elif y_max is None or y_max < f.y2:
                y_max = f.y2

        self.center_x = (x_max + x_min) / 2
        self.center_y = (y_max + y_min) / 2

    def add_figure(self, figure):
        if figure is Object:
            for e in figure.figures:
                self.figures.append(e)
        else:
            self.figures.append(figure)

    def is_coord_on_figure(self, x, y):
        self.set_central_coord()
        if self.center_x - 10 <= x <= self.center_x + 10 \
                and self.center_y - 10 <= y <= self.center_y + 10 or self.center:
            return True
        for e in self.figures:
            if e.is_coord_on_figure(x, y):
                return True

    def set_color(self, col):
        for e in self.figures:
            e.set_color(col)

    def fill(self, col):
        for e in self.figures:
            e.fill(col)

    def set_thickness(self, th):
        for e in self.figures:
            e.set_thickness(th)

    def draw_selected(self, painter):
        self.set_central_coord()
        pen = QPen(QColor('black'), 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawEllipse(QPoint(self.center_x, self.center_y), 10, 10)

    def draw(self, painter, col, th, x, y):

        if self.selected:
            self.draw_selected(painter)

        for e in self.figures:
            sel = e.selected
            e.selected = False
            e.draw(painter, col, th, x, y)
            e.selected = sel

    def select(self):
        self.selected = True
        for e in self.figures:
            e.select()

    def deselect(self):
        self.selected = False
        for e in self.figures:
            e.deselect()


class Line:

    def __init__(self, x1, y1, x2=None, y2=None, color=None, th=None):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

        self.center_x = None
        self.center_y = None

        self.color = color
        self.thick = th
        self.selected = False
        self.unlighter = color

        self.center = False
        self.first = False
        self.second = False

    def stop_moving(self):
        self.center = False
        self.first = False
        self.second = False

    def in_bounds(self, w, h):

        if self.x2 is None or self.y2 is None:
            return True
        if self.thick is None:
            th = 10
        else:
            th = self.thick
        return (40 <= self.x1 + th / 2 <= w + 40 and
                150 <= self.y1 + th / 2 <= 150 + h and
                40 <= self.x2 + th / 2 <= w + 40 and
                150 <= self.y2 + th / 2 <= 150 + h and
                40 <= self.x1 - th / 2 <= w + 40 and
                150 <= self.y1 - th / 2 <= h + 150 and
                40 <= self.x2 - th / 2 <= w + 40 and
                150 <= self.y2 - th / 2 <= h + 150)

    def transport(self, x, y):
        dx = x - self.center_x
        dy = y - self.center_y
        self.transport_center(dx, dy)

    def transport_center(self, dx, dy):
        self.x1 += dx
        self.x2 += dx

        self.y1 += dy
        self.y2 += dy

    def set_thickness(self, th):
        self.thick = th

    def set_color(self, col):
        self.color = col

    def set_end_coord(self, x2, y2):
        self.x2 = x2
        self.y2 = y2

    def set_start_coord(self, x1, y1):
        self.x1 = x1
        self.y1 = y1

    def move_or_deselect(self, x, y):
        if self.center_x - 10 <= x <= self.center_x + 10 \
                and self.center_y - 10 <= y <= self.center_y + 10 or self.center\
                or self.x1 - 10 <= x <= self.x1 + 10 \
                and self.y1 - 10 <= y <= self.y1 + 10 or self.first\
                or self.x2 - 10 <= x <= self.x2 + 10 \
                and self.y2 - 10 <= y <= self.y2 + 10 or self.second:
            self.move(x, y)
        else:
            self.deselect()

    def move(self, x, y):
        if self.center_x - 10 <= x <= self.center_x + 10 \
                and self.center_y - 10 <= y <= self.center_y + 10\
                or self.center:
            self.center = True
            self.transport(x, y)
        elif self.x1 - 10 <= x <= self.x1 + 10 \
                and self.y1 - 10 <= y <= self.y1 + 10\
                or self.first:
            self.first = True
            self.set_start_coord(x, y)
        elif self.x2 - 10 <= x <= self.x2 + 10 \
                and self.y2 - 10 <= y <= self.y2 + 10\
                or self.second:
            self.second = True
            self.set_end_coord(x, y)

    def set_central_coord(self):
        self.center_x = (self.x1 + self.x2) / 2
        self.center_y = (self.y1 + self.y2) / 2

    def draw(self, painter, col, th, x, y):

        dr_x1 = self.x1
        dr_x2 = self.x2
        dr_y1 = self.y1
        dr_y2 = self.y2

        if self.color is not None:
            col = self.color
        else:
            self.color = col
        if self.thick is not None:
            th = self.thick
        else:
            self.thick = th

        changed = False

        if x is not None:
            if self.x1 > x and self.x2 > x:
                return
            if self.x1 > x:
                dr_x1 = x
                dr_y1 = self.f(x, y)
                changed = True
            if self.x2 > x:
                dr_x2 = x
                dr_y2 = self.f(x, y)
                changed = True

        if y is not None:
            if self.y1 > y and self.y2 > y:
                return
            if self.y1 > y and not changed:
                dr_y1 = y
                dr_x1 = self.g(y, x)
            if self.y2 > y and not changed:
                dr_y2 = y
                dr_x2 = self.g(y, x)
        pen = QPen(col, th, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(dr_x1, dr_y1, dr_x2, dr_y2)

        if self.selected:
            self.draw_selected(painter)

    def draw_selected(self, painter):
        self.set_central_coord()
        pen = QPen(QColor('black'), 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawEllipse(QPoint(self.center_x, self.center_y), 10, 10)
        painter.drawEllipse(QPoint(self.x1, self.y1), 10, 10)
        painter.drawEllipse(QPoint(self.x2, self.y2), 10, 10)

    def get_y_shift(self):
        x = abs(self.x1 - self.x2)
        y = abs(self.y1 - self.y2)
        if y == 0 or x == 0:
            return 0
        else:
            tg_fi = x / y
        return tg_fi * x

    def f(self, x0, y0):
        if self.x1 == self.x2:
            return self.y1
        dx = (self.x2 - self.x1)
        dy = (self.y1 - self.y2)
        return ((self.x2 * self.y1 - self.x1 * self.y2) - dy * x0) / dx

    def g(self, y0, x0):
        if self.y1 == self.y2:
            return self.x1
        dx = (self.x2 - self.x1)
        dy = (self.y1 - self.y2)
        return ((self.x2 * self.y1 - self.x1 * self.y2) - dx * y0) / dy

    def is_coord_on_figure(self, x, y):

        self.set_central_coord()
        if self.selected and (self.center_x - 10 <= x <= self.center_x + 10
                              and self.center_y - 10 <= y <= self.center_y + 10 or self.center
                              or self.x1 - 10 <= x <= self.x1 + 10
                              and self.y1 - 10 <= y <= self.y1 + 10 or self.first
                              or self.x2 - 10 <= x <= self.x2 + 10
                              and self.y2 - 10 <= y <= self.y2 + 10 or self.second):
            return True

        absx = abs(self.x1 - self.x2)
        absy = abs(self.y1 - self.y2)
        th = self.thick / 2
        if absy < 0.00001:

            if self.x1 > self.x2:
                x1 = self.x2
                x2 = self.x1
            else:
                x1 = self.x1
                x2 = self.x2

            y1 = self.y1 - th
            y2 = self.y2 + th

            return x1 <= x <= x2 and y1 <= y <= y2

        if absx < 0.00001:

            if self.y1 > self.y2:
                y1 = self.y2
                y2 = self.y1
            else:
                y1 = self.y1
                y2 = self.y2

            x1 = self.x1 - th
            x2 = self.x2 + th

            return x1 <= x <= x2 and y1 <= y <= y2

        if self.x1 > self.x2:
            minx = self.x2
            maxx = self.x1
        else:
            minx = self.x1
            maxx = self.x2
        if self.y1 > self.y2:
            miny = self.y2
            maxy = self.y1
        else:
            miny = self.y1
            maxy = self.y2

        dy = self.get_y_shift()
        y1 = self.y1 + dy
        y2 = self.y2 + dy

        k = (y2 - y1) / (self.x2 - self.x1)

        return (maxx >= x >= minx and
                maxy >= y >= miny and
                k * x + (self.y1 - k * self.x1) + th > y > k * x + (self.y1 - k * self.x1) - th)

    def select(self):
        self.selected = True
        self.unlighter = self.color
        self.color = QColor('red')

    def deselect(self):
        self.selected = False
        self.color = self.unlighter

    def fill(self, c):
        pass


class Hand:

    def __init__(self, x1, y1, color=None, th=None):
        self.x1 = x1
        self.y1 = y1
        self.lines = []
        self.color = color
        self.thick = th
        self.selected = False

        self.center_x = None
        self.center_y = None

        self.x2 = x1
        self.y2 = y1

        self.center = False

    def in_bounds(self, x, y):
        for i in self.lines:
            if not i.in_bounds(x, y):
                return False
        return True

    def stop_moving(self):
        self.center = False

    def move_or_deselect(self, x, y):
        if self.center_x - 10 <= x <= self.center_x + 10 \
                and self.center_y - 10 <= y <= self.center_y + 10\
                or self.center:
            self.center = True
            self.move(x, y)
        else:
            self.deselect()

    def move(self, x, y):
        if self.center_x - 10 <= x <= self.center_x + 10 \
                and self.center_y - 10 <= y <= self.center_y + 10\
                or self.center:
            self.transport(x, y)

    def transport(self, x, y):
        dx = x - self.center_x
        dy = y - self.center_y
        self.transport_center(dx, dy)

    def transport_center(self, dx, dy):
        for l in self.lines:
            l.transport_center(dx, dy)

        self.x1 += dx
        self.y1 += dy
        self.x2 += dx
        self.y2 += dy

    def set_central_coord(self):
        x_min = None
        y_min = None
        y_max = None
        x_max = None

        for f in self.lines:
            if x_min is None or x_min > f.x1:
                x_min = f.x1
            elif x_max is None or x_max < f.x1:
                x_max = f.x1

            if x_min is None or x_min > f.x2:
                x_min = f.x2
            elif x_max is None or x_max < f.x2:
                x_max = f.x2

            if y_min is None or y_min > f.y1:
                y_min = f.y1
            elif y_max is None or y_max < f.y1:
                y_max = f.y1

            if y_min is None or y_min > f.y2:
                y_min = f.y2
            elif y_max is None or y_max < f.y2:
                y_max = f.y2

        self.center_x = (x_max + x_min) / 2
        self.center_y = (y_max + y_min) / 2

    def set_end_coord(self, x2, y2):
        self.lines.append(Line(self.x1, self.y1, x2, y2))
        self.x1 = x2
        self.y1 = y2

    def set_color(self, col):
        self.color = col
        for l in self.lines:
            l.color = col

    def set_thickness(self, th):
        self.thick = th
        for l in self.lines:
            l.set_thickness(self.thick)

    def draw(self, painter, col, th, x, y):
        if self.color is not None:
            col = self.color
        if self.thick is not None:
            th = self.thick
        for l in self.lines:
            sel = l.selected
            l.selected = False
            l.draw(painter, col, th, x, y)
            l.selected = sel

        if self.selected:
            self.set_central_coord()
            pen = QPen(QColor('black'), 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawEllipse(QPoint(self.center_x, self.center_y), 10, 10)

    def is_coord_on_figure(self, x, y):
        self.set_central_coord()
        if self.selected \
                and (self.center_x - 10 <= x <= self.center_x + 10
                     and self.center_y - 10 <= y <= self.center_y + 10
                     or self.center):
            return True
        for l in self.lines:
            if l.is_coord_on_figure(x, y):
                return True

    def select(self):
        self.selected = True
        for l in self.lines:
            l.select()

    def deselect(self):
        self.selected = False
        for l in self.lines:
            l.deselect()

    def fill(self, c):
        pass


class Rectangle:

    def __init__(self, x1, y1, color=None, th=None):
        self.x1 = x1
        self.y1 = y1

        self.x2 = x1
        self.y2 = y1

        self.color = color
        self.thick = th
        self.selected = False

        self.fill_color = None

        self.center = False
        self.first = False
        self.second = False

    def in_bounds(self, x, y):
        for i in self.lines:
            if not i.in_bounds(x, y):
                return False
        return True

    def stop_moving(self):
        self.center = False
        self.first = False
        self.second = False

    def set_end_coord(self, x2, y2):

        self.x2 = x2
        self.y2 = y2

        self.lines = []
        self.lines.append(Line(self.x1, self.y1, self.x1, y2))
        self.lines.append(Line(self.x1, self.y1, x2, self.y1))
        self.lines.append(Line(x2, y2, self.x1, y2))
        self.lines.append(Line(x2, y2, x2, self.y1))

    def transport(self, x, y):
        dx = x - self.center_x
        dy = y - self.center_y
        self.transport_center(dx, dy)

    def transport_center(self, dx, dy):
        for i in self.lines:
            i.transport_center(dx, dy)

        self.x1 += dx
        self.y1 += dy

        self.x2 += dx
        self.y2 += dy

        if self.fill_color.col2 is not None:
            self.fill_color.x1 += dx
            self.fill_color.x2 += dx

            self.fill_color.y1 += dy
            self.fill_color.y2 += dy

    def set_start_coord(self, x1, y1):

        self.x1 = x1
        self.y1 = y1
        self.lines = []
        self.lines.append(Line(self.x1, self.y1, self.x1, self.y2))
        self.lines.append(Line(self.x1, self.y1, self.x2, self.y1))
        self.lines.append(Line(self.x2, self.y2, self.x1, self.y2))
        self.lines.append(Line(self.x2, self.y2, self.x2, self.y1))

    def set_central_coord(self):
        self.center_x = (self.x1 + self.x2) / 2
        self.center_y = (self.y1 + self.y2) / 2

    def move_or_deselect(self, x, y):
        if self.center_x - 10 <= x <= self.center_x + 10 \
                and self.center_y - 10 <= y <= self.center_y + 10 or self.center\
                or self.x1 - 10 <= x <= self.x1 + 10 \
                and self.y1 - 10 <= y <= self.y1 + 10 or self.first\
                or self.x2 - 10 <= x <= self.x2 + 10 \
                and self.y2 - 10 <= y <= self.y2 + 10 or self.second:
            self.move(x, y)
        else:
            self.deselect()

    def move(self, x, y):
        if self.center_x - 10 <= x <= self.center_x + 10 \
                and self.center_y - 10 <= y <= self.center_y + 10\
                or self.center:
            self.center = True
            self.transport(x, y)
        elif self.x1 - 10 <= x <= self.x1 + 10 \
                and self.y1 - 10 <= y <= self.y1 + 10\
                or self.first:
            self.first = True
            self.set_start_coord(x, y)
        elif self.x2 - 10 <= x <= self.x2 + 10 \
                and self.y2 - 10 <= y <= self.y2 + 10\
                or self.second:
            self.second = True
            self.set_end_coord(x, y)

    def set_color(self, col):
        self.color = col
        for l in self.lines:
            l.color = col

    def set_thickness(self, th):
        self.thick = th
        for l in self.lines:
            l.set_thickness(self.thick)

    def draw(self, painter, col, th, x, y):

        if self.color is not None:
            col = self.color
        if self.thick is not None:
            th = self.thick

        for l in self.lines:
            sel = l.selected
            l.selected = False
            l.draw(painter, col, th, x, y)
            l.selected = sel

        if self.fill_color is not None:

            minx = min(self.x1, self.x2)
            miny = min(self.y1, self.y2)
            col = self.fill_color.get_color()

            painter.fillRect(minx + self.thick / 2,
                             miny + self.thick / 2,
                             abs(self.x1 - self.x2) - self.thick,
                             abs(self.y1 - self.y2) - self.thick,
                             col)

        if self.selected:
            self.set_central_coord()
            pen = QPen(QColor('black'), 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawEllipse(QPoint(self.center_x, self.center_y), 10, 10)
            painter.drawEllipse(QPoint(self.x1, self.y1), 10, 10)
            painter.drawEllipse(QPoint(self.x2, self.y2), 10, 10)

    def is_coord_on_figure(self, x, y):

        if self.fill_color is not None:
            if self.x1 < self.x2:
                minx = self.x1
                miny = self.y1

                maxx = self.x2
                maxy = self.y2
            else:
                minx = self.x2
                miny = self.y2

                maxx = self.x1
                maxy = self.y1
            return minx <= x <= maxx and miny <= y <= maxy

        self.set_central_coord()
        if self.selected and (self.center_x - 10 <= x <= self.center_x + 10 and
                              self.center_y - 10 <= y <= self.center_y + 10 or
                              self.center):
            return True

        for l in self.lines:
            if l.is_coord_on_figure(x, y):
                return True

    def select(self):
        self.selected = True
        for l in self.lines:
            l.select()

    def deselect(self):
        self.selected = False
        for l in self.lines:
            l.deselect()

    def fill(self, col):
        self.fill_color = col
        if self.fill_color.col2 is not None:
            self.fill_color.x1 += self.x1
            self.fill_color.x2 += self.x1

            self.fill_color.y1 += self.y1
            self.fill_color.y2 += self.y1


class Circle:

    def __init__(self, x1, y1, color=None, th=None):
        self.x1 = x1
        self.y1 = y1
        self.color = color
        self.thick = th
        self.x2 = x1
        self.y2 = y1
        self.selected = False
        self.fill_color = None
        self.unlighter = self.color
        self.center_x = x1
        self.center_y = y1

        self.center = False
        self.second = False

        self.rad = None

    def in_bounds(self, x, y):
        return 40 <= self.x1 + self.rad <= x + 40 and \
               150 <= self.y1 + self.rad <= 150 + y and \
               40 <= self.x1 - self.rad <= x + 40 \
               and 150 <= self.y1 - self.rad <= 150 + y

    def stop_moving(self):
        self.center = False
        self.second = False

    def set_end_coord(self, x2, y2):
        self.x2 = x2
        self.y2 = y2
        x = self.x1 - self.x2
        y = self.y1 - self.y2
        self.rad = sqrt(x * x + y * y)

    def set_color(self, col):
        self.color = col

    def set_thickness(self, th):
        self.thick = th

    def move_or_deselect(self, x, y):
        if self.center_x - 10 <= x <= self.center_x + 10 \
                and self.center_y - 10 <= y <= self.center_y + 10 or self.center\
                or self.center_x - 10 <= x - self.rad <= self.center_x + 10 \
                and self.center_y - 10 <= y <= self.center_y + 10 or self.second:
            self.move(x, y)
        else:
            self.deselect()

    def set_start_coord(self, x, y):
        self.x1 = x
        self.y1 = y

        self.center_y = self.y1
        self.center_x = self.x1

    def transport_center(self, dx, dy):
        self.x1 += dx
        self.y1 += dy

        if self.fill_color.col2 is not None:
            self.fill_color.x1 += dx
            self.fill_color.x2 += dx

            self.fill_color.y1 += dy
            self.fill_color.y2 += dy

        self.center_y = self.y1
        self.center_x = self.x1

    def move(self, x, y):
        if self.x1 - 10 <= x <= self.x1 + 10 \
                and self.y1 - 10 <= y <= self.y1 + 10 or self.center:
            self.center = True
            self.transport_center(x - self.x1, y - self.y1)
        elif self.x1 - 10 <= x - self.rad <= self.x1 + 10 \
                and self.y1 - 10 <= y <= self.y1 + 10 or self.second:
            self.second = True
            self.set_end_coord(x, y)

    def draw(self, painter, col, th, x, y):

        if col is None:
            col = self.color
        if th is None:
            th = self.thick
        pen = QPen(col, th, Qt.SolidLine)
        painter.setPen(pen)

        changed = False
        if y is not None:
            if self.y1 - self.rad > y:
                return

            if self.rad + self.y1 > y:
                a = math.acos((y - self.y1) / self.rad) * 180 / math.pi

                s = -(90 - a)
                start = s * 16

                e = (90 - a) * 2 + 180
                span = e * 16

                changed = True

        if x is not None:
            if self.x1 - self.rad > x:
                return

            if self.rad + self.x1 > x:
                a = math.acos((x - self.x1) / self.rad) * 180 / math.pi

                if not changed:
                    s = a
                    start = s * 16
                    e = (90 - a) * 2 + 180
                    span = e * 16
                else:
                    s = a
                    start1 = s * 16
                    e = (90 - a) * 2 + 180
                    span1 = e * 16

                    res_s = max(start, start1)
                    end = min(start + span, start1 + span1)
                    span = end - res_s
                    start = res_s
                changed = True

        if self.fill_color is not None:
            col = self.fill_color.get_color()
            brush = QBrush(col)
            painter.setBrush(brush)

        else:
            brush = QBrush(QColor(255, 255, 255, alpha=0))
            painter.setBrush(brush)

        if changed:
            painter.drawArc(self.x1 - self.rad, self.y1 - self.rad,
                            self.rad * 2, self.rad * 2,
                            start, span)
        else:
            painter.drawEllipse(QPoint(self.x1, self.y1), self.rad, self.rad)

        if self.selected:
            pen = QPen(QColor('black'), 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawEllipse(QPoint(self.center_x, self.center_y), 10, 10)
            painter.drawEllipse(QPoint(self.center_x + self.rad, self.center_y), 10, 10)

    def is_coord_on_figure(self, x, y):

        if self.selected and (self.center_x - 10 <= x <= self.center_x + 10
                              and self.center_y - 10 <= y <= self.center_y + 10 or self.center
                              or self.center_x - 10 <= x - self.rad <= self.center_x + 10
                              and self.center_y - 10 <= y <= self.center_y + 10 or self.second):
            return True

        if self.fill_color is not None:
            return (y - self.y1) ** 2 + (x - self.x1) ** 2 <= self.rad ** 2

        th = self.thick / 2
        return (self.rad + th) ** 2 >= (y - self.y1) ** 2 + (x - self.x1) ** 2 >= (self.rad - th) ** 2

    def fill(self, col):
        self.fill_color = col

        if self.fill_color.col2 is not None:
            self.fill_color.x1 += self.x1 - self.rad
            self.fill_color.x2 += self.x1 - self.rad

            self.fill_color.y1 += self.y1 - self.rad
            self.fill_color.y2 += self.y1 - self.rad

    def select(self):
        self.selected = True
        self.unlighter = self.color
        self.color = QColor('red')

    def deselect(self):
        self.selected = False
        self.color = self.unlighter


class Combiner:

    @staticmethod
    def combine(figures, obj=None):
        if obj is None:
            obj = Object()
        for e in figures:
            obj.add_figure(e)
        return obj
