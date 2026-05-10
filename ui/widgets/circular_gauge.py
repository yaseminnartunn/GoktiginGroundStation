from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont
from ui.styles import COLORS

class CircularGauge(QWidget):
    def __init__(self, label, unit, min_val=0, max_val=100, color="#00D4FF"):
        super().__init__()
        self.label   = label
        self.unit    = unit
        self.min_val = min_val
        self.max_val = max_val
        self.color   = QColor(color)
        self.value   = 0.0
        self.setFixedSize(120, 120)

    def set_value(self, v):
        self.value = v
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        r = min(w, h) // 2 - 10

        # Arkaplan daire
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(COLORS["bg_card"])))
        p.drawEllipse(cx - r - 5, cy - r - 5, (r + 5) * 2, (r + 5) * 2)

        # Track
        p.setPen(QPen(QColor(COLORS["border_glow"]), 6, Qt.SolidLine, Qt.RoundCap))
        p.setBrush(Qt.NoBrush)
        p.drawArc(cx - r, cy - r, r * 2, r * 2, 225 * 16, -270 * 16)

        # Değer yayı
        pct = max(0, min(1, (self.value - self.min_val) / (self.max_val - self.min_val)))
        span = int(-270 * 16 * pct)
        pen = QPen(self.color, 6, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        p.drawArc(cx - r, cy - r, r * 2, r * 2, 225 * 16, span)

        # Değer
        p.setPen(QPen(QColor(COLORS["text_primary"])))
        p.setFont(QFont("Segoe UI", 18, QFont.Bold))
        p.drawText(QRect(0, cy - 26, w, 30), Qt.AlignCenter, f"{self.value:.1f}")

        # Label + birim
        p.setPen(QPen(QColor(COLORS["text_secondary"])))
        label_font = QFont("Segoe UI", 10, QFont.DemiBold)
        unit_font = QFont("Segoe UI", 9)
        p.setFont(label_font)
        fm_label = p.fontMetrics()
        label_text = fm_label.elidedText(self.label, Qt.ElideRight, w - 12)
        p.drawText(QRect(0, cy + 4, w, 18), Qt.AlignCenter, label_text)

        p.setFont(unit_font)
        fm_unit = p.fontMetrics()
        unit_text = fm_unit.elidedText(f"[{self.unit}]", Qt.ElideRight, w - 12)
        p.drawText(QRect(0, cy + 20, w, 18), Qt.AlignCenter, unit_text)
