from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QBrush, QPen

class MiniGraph(QWidget):
    def __init__(self, color="#00D4FF", max_points=80):
        super().__init__()
        self.color = QColor(color)
        self.fill_color = QColor(color)
        self.fill_color.setAlpha(25)
        self.max_points = max_points
        self.data = []
        self.setMinimumHeight(60)
        self.setMaximumHeight(70)

    def add_value(self, v):
        self.data.append(v)
        if len(self.data) > self.max_points:
            self.data.pop(0)
        self.update()

    def paintEvent(self, event):
        if len(self.data) < 2:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        mn, mx = min(self.data), max(self.data)
        rng = mx - mn if mx != mn else 1
        def sx(i): return int(i * w / (self.max_points - 1))
        def sy(v): return int(h - 4 - (v - mn) / rng * (h - 8))

        path = QPainterPath()
        path.moveTo(sx(0), h)
        path.lineTo(sx(0), sy(self.data[0]))
        for i, v in enumerate(self.data[1:], 1):
            path.lineTo(sx(i), sy(v))
        path.lineTo(sx(len(self.data) - 1), h)
        path.closeSubpath()
        p.fillPath(path, QBrush(self.fill_color))

        line = QPainterPath()
        line.moveTo(sx(0), sy(self.data[0]))
        for i, v in enumerate(self.data[1:], 1):
            line.lineTo(sx(i), sy(v))
        pen = QPen(self.color, 1.5)
        p.setPen(pen)
        p.drawPath(line)
