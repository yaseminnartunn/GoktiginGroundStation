import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush,
    QLinearGradient, QRadialGradient,
    QPolygonF, QFont
)
from PyQt5.QtCore import Qt, QPointF, QRectF, QTimer
from ui.styles import COLORS


class RocketWidget(QFrame):
    """
    Roketin pitch/roll değerlerine göre dönen 2D simülasyon görüntüsü.
    Dashboard sol üst panelde GPS verisinin üstünde gösterilir.
    """
    def __init__(self):
        super().__init__()
        self.pitch = 0.0
        self.roll = 0.0
        self.flame_phase = 0.0  # Alev animasyonu fazı
        self.setMinimumSize(200, 280)
        self.setStyleSheet(f"""
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border_glow']};
            border-radius: 12px;
            border-top: 2px solid {COLORS['accent_cyan']};
        """)

        # Alev animasyon zamanlayıcısı
        self._flame_timer = QTimer(self)
        self._flame_timer.timeout.connect(self._animate_flame)
        self._flame_timer.start(60)

    def _animate_flame(self):
        self.flame_phase += 0.25
        if self.flame_phase > 2 * math.pi:
            self.flame_phase -= 2 * math.pi
        self.update()

    def set_orientation(self, pitch, roll):
        self.pitch = pitch
        self.roll = roll
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        w = self.width()
        h = self.height()

        # ── Arka plan ──
        p.fillRect(self.rect(), QColor(COLORS["bg_card"]))

        # ── Başlık yazısı ──
        p.setPen(QColor(COLORS["text_secondary"]))
        p.setFont(QFont("Segoe UI", 9))
        p.drawText(QRectF(0, 6, w, 18), Qt.AlignCenter, "ROKET SİMÜLASYONU")

        # ── Referans çizgileri (horizon + dikey) ──
        center_x = w / 2
        center_y = h / 2 + 10  # Başlık için biraz aşağı kaydır

        pen_grid = QPen(QColor(COLORS["grid_line"]), 1, Qt.DashLine)
        p.setPen(pen_grid)
        # Yatay (horizon)
        p.drawLine(int(center_x - 70), int(center_y), int(center_x + 70), int(center_y))
        # Dikey
        p.drawLine(int(center_x), int(center_y - 90), int(center_x), int(center_y + 90))

        # ── Dönüşüm (roll açısı) ──
        p.save()
        p.translate(center_x, center_y)
        p.rotate(self.roll)

        # Ölçek faktörleri
        body_w = 22
        body_h = 100
        nose_h = 32
        fin_w = 18
        fin_h = 28

        # ── Alev / Egzoz ──
        flame_len = 20 + 8 * math.sin(self.flame_phase)
        flame_w = 10 + 4 * math.sin(self.flame_phase * 1.7)

        flame_grad = QLinearGradient(0, body_h / 2, 0, body_h / 2 + flame_len)
        flame_grad.setColorAt(0.0, QColor("#FF6B35"))
        flame_grad.setColorAt(0.4, QColor("#FFD700"))
        flame_grad.setColorAt(1.0, QColor(255, 215, 0, 0))

        flame_poly = QPolygonF([
            QPointF(-flame_w, body_h / 2),
            QPointF(0, body_h / 2 + flame_len),
            QPointF(flame_w, body_h / 2),
        ])
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(flame_grad))
        p.drawPolygon(flame_poly)

        # İç alev (daha parlak)
        inner_len = flame_len * 0.6
        inner_w = flame_w * 0.5
        inner_grad = QLinearGradient(0, body_h / 2, 0, body_h / 2 + inner_len)
        inner_grad.setColorAt(0.0, QColor("#FFFFFF"))
        inner_grad.setColorAt(0.5, QColor("#FF6B35"))
        inner_grad.setColorAt(1.0, QColor(255, 107, 53, 0))
        inner_poly = QPolygonF([
            QPointF(-inner_w, body_h / 2),
            QPointF(0, body_h / 2 + inner_len),
            QPointF(inner_w, body_h / 2),
        ])
        p.setBrush(QBrush(inner_grad))
        p.drawPolygon(inner_poly)

        # ── Kanatçıklar (finler) ──
        fin_color = QColor(COLORS["accent_red"])
        p.setBrush(fin_color)
        p.setPen(Qt.NoPen)

        # Sol fin
        left_fin = QPolygonF([
            QPointF(-body_w / 2, body_h / 2 - 5),
            QPointF(-body_w / 2 - fin_w, body_h / 2),
            QPointF(-body_w / 2, body_h / 2 - fin_h),
        ])
        p.drawPolygon(left_fin)

        # Sağ fin
        right_fin = QPolygonF([
            QPointF(body_w / 2, body_h / 2 - 5),
            QPointF(body_w / 2 + fin_w, body_h / 2),
            QPointF(body_w / 2, body_h / 2 - fin_h),
        ])
        p.drawPolygon(right_fin)

        # ── Gövde (gradient) ──
        body_grad = QLinearGradient(-body_w / 2, 0, body_w / 2, 0)
        body_grad.setColorAt(0.0, QColor("#1A3A5C"))
        body_grad.setColorAt(0.3, QColor("#2A5A8C"))
        body_grad.setColorAt(0.5, QColor("#3A7ABB"))
        body_grad.setColorAt(0.7, QColor("#2A5A8C"))
        body_grad.setColorAt(1.0, QColor("#1A3A5C"))

        p.setBrush(QBrush(body_grad))
        p.setPen(QPen(QColor(COLORS["accent_cyan"]), 1))
        body_rect = QRectF(-body_w / 2, -body_h / 2, body_w, body_h)
        p.drawRoundedRect(body_rect, 4, 4)

        # Gövde üstündeki pencere (viewport)
        viewport_y = -body_h / 2 + 20
        vp_radius = 6
        vp_grad = QRadialGradient(0, viewport_y, vp_radius)
        vp_grad.setColorAt(0.0, QColor("#00D4FF"))
        vp_grad.setColorAt(0.6, QColor("#006688"))
        vp_grad.setColorAt(1.0, QColor("#003344"))
        p.setBrush(QBrush(vp_grad))
        p.setPen(QPen(QColor(COLORS["accent_cyan"]), 1))
        p.drawEllipse(QPointF(0, viewport_y), vp_radius, vp_radius)

        # Gövde üstünde şerit
        stripe_pen = QPen(QColor(COLORS["accent_red"]), 2)
        p.setPen(stripe_pen)
        stripe_y = -body_h / 2 + 38
        p.drawLine(QPointF(-body_w / 2 + 2, stripe_y), QPointF(body_w / 2 - 2, stripe_y))

        # ── Burun konisi ──
        nose_grad = QLinearGradient(0, -body_h / 2 - nose_h, 0, -body_h / 2)
        nose_grad.setColorAt(0.0, QColor(COLORS["accent_cyan"]))
        nose_grad.setColorAt(1.0, QColor("#2A5A8C"))

        nose_poly = QPolygonF([
            QPointF(0, -body_h / 2 - nose_h),
            QPointF(-body_w / 2, -body_h / 2),
            QPointF(body_w / 2, -body_h / 2),
        ])
        p.setPen(QPen(QColor(COLORS["accent_cyan"]), 1))
        p.setBrush(QBrush(nose_grad))
        p.drawPolygon(nose_poly)

        p.restore()

        # ── Pitch / Roll bilgileri ──
        p.setPen(QColor(COLORS["text_dim"]))
        p.setFont(QFont("Segoe UI", 8))
        info_y = h - 36
        p.drawText(QRectF(8, info_y, w - 16, 16), Qt.AlignLeft,
                    f"Pitch: {self.pitch:+.1f}°")
        p.drawText(QRectF(8, info_y + 14, w - 16, 16), Qt.AlignLeft,
                    f"Roll:  {self.roll:+.1f}°")

        p.end()
