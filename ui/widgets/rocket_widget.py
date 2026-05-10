from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from ui.styles import COLORS

class RocketWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.pitch = 0.0
        self.roll  = 0.0
        self.setMinimumSize(200, 280)

    def set_orientation(self, pitch, roll):
        self.pitch = pitch
        self.roll  = roll
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(COLORS["bg_primary"]))
