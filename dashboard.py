import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty, QPointF
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QBrush, QLinearGradient, QPainterPath, QPolygonF

from config import COLORS

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

class RocketWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.pitch = 0.0
        self.roll  = 0.0
        self.yaw   = 0.0
        self.setMinimumSize(200, 280)

    def set_orientation(self, pitch, roll, yaw):
        self.pitch = pitch
        self.roll  = roll
        self.yaw   = yaw
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        painter.fillRect(self.rect(), QColor(COLORS["bg_primary"]))

        # Roket koordinatları (ham ölçek)
        bw    = 22    # Gövde yarı genişliği
        top   = -115  # Gövde üst (burun tabanı)
        bot   = 80    # Gövde alt (fin kökü)
        nose_h = 55   # Burun yüksekliği
        fin_h  = 38
        noz_h  = 22
        flame_max = 50  # Max alev uzunluğu

        # Roketin uçtan uca toplam yüksekliği
        rocket_top    = top - nose_h          # Burun ucu
        rocket_bottom = bot + noz_h + flame_max  # Alev sonu
        rocket_height = rocket_bottom - rocket_top

        # Widget'a sığdırmak için ölçek hesapla
        padding = 30
        available_h = h - padding * 2
        scale = min(1.0, available_h / rocket_height)

        # Dikey merkezi roketin geometrik merkezine göre ayarla
        rocket_center_y = (rocket_top + rocket_bottom) / 2
        cx = w / 2
        cy = h / 2 - rocket_center_y * scale  # Tam ortala

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-self.pitch)
        painter.scale(scale * max(0.15, abs(math.cos(math.radians(self.roll)))), scale)

        gh = bot - top

        # ── GÖVDE ──
        body_grad = QLinearGradient(-bw, 0, bw, 0)
        body_grad.setColorAt(0.0,  QColor(12, 14, 22))
        body_grad.setColorAt(0.25, QColor(30, 35, 58))
        body_grad.setColorAt(0.5,  QColor(42, 50, 80))
        body_grad.setColorAt(0.75, QColor(20, 25, 42))
        body_grad.setColorAt(1.0,  QColor(8, 10, 18))
        painter.setBrush(QBrush(body_grad))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(int(-bw), int(top), int(bw*2), int(gh), 8, 8)

        shine_grad = QLinearGradient(-bw, 0, -bw + 8, 0)
        shine_grad.setColorAt(0.0, QColor(0, 212, 255, 60))
        shine_grad.setColorAt(1.0, QColor(0, 212, 255, 0))
        painter.setBrush(QBrush(shine_grad))
        painter.drawRoundedRect(int(-bw), int(top), 8, int(gh), 4, 4)

        # ── BURUN KONİ ──
        nose_path = QPainterPath()
        nose_path.moveTo(0, top - nose_h)
        nose_path.lineTo(-bw, top + 6)
        nose_path.lineTo(bw, top + 6)
        nose_path.closeSubpath()
        nose_grad = QLinearGradient(-bw, 0, bw, 0)
        nose_grad.setColorAt(0.0,  QColor(0, 80, 120))
        nose_grad.setColorAt(0.3,  QColor(0, 190, 240))
        nose_grad.setColorAt(0.55, QColor(180, 240, 255))
        nose_grad.setColorAt(0.75, QColor(0, 160, 200))
        nose_grad.setColorAt(1.0,  QColor(0, 40, 70))
        painter.setBrush(QBrush(nose_grad))
        painter.setPen(Qt.NoPen)
        painter.drawPath(nose_path)
        painter.setPen(QPen(QColor(200, 240, 255, 180), 1.2))
        painter.drawLine(int(-bw * 0.3), int(top + 4), 0, int(top - nose_h + 4))

        # ── NEON ŞERİT ──
        band_y = top + gh * 0.28
        band_grad = QLinearGradient(-bw, 0, bw, 0)
        band_grad.setColorAt(0.0, QColor(0, 212, 255, 0))
        band_grad.setColorAt(0.3, QColor(0, 212, 255, 150))
        band_grad.setColorAt(0.7, QColor(0, 212, 255, 150))
        band_grad.setColorAt(1.0, QColor(0, 212, 255, 0))
        painter.setBrush(QBrush(band_grad))
        painter.setPen(Qt.NoPen)
        painter.drawRect(int(-bw), int(band_y), int(bw * 2), 5)

        # ── GÖKTİGİN YAZISI ──
        painter.save()
        painter.translate(0, int(top + gh * 0.55))
        painter.rotate(-90)
        text_w = int(gh * 0.45)
        painter.setPen(QColor(0, 212, 255, 210))
        font = QFont("Segoe UI", 9, QFont.Bold)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2.5)
        painter.setFont(font)
        painter.drawText(QRect(-text_w // 2, -9, text_w, 18), Qt.AlignCenter, "GÖKTİGİN")
        painter.restore()

        # ── FİNLER ──
        fin_y_top = bot - 30
        fin_y_bot = bot + fin_h
        fin_grad = QLinearGradient(0, fin_y_top, 0, fin_y_bot)
        fin_grad.setColorAt(0.0, QColor(0, 140, 180))
        fin_grad.setColorAt(1.0, QColor(0, 60, 90))
        fin_w = 28

        left_fin = QPainterPath()
        left_fin.moveTo(-bw, fin_y_top)
        left_fin.lineTo(-bw - fin_w, fin_y_bot)
        left_fin.lineTo(-bw, bot)
        left_fin.closeSubpath()
        painter.setBrush(QBrush(fin_grad))
        painter.setPen(QPen(QColor(0, 212, 255, 60), 1))
        painter.drawPath(left_fin)

        right_fin = QPainterPath()
        right_fin.moveTo(bw, fin_y_top)
        right_fin.lineTo(bw + fin_w, fin_y_bot)
        right_fin.lineTo(bw, bot)
        right_fin.closeSubpath()
        painter.drawPath(right_fin)

        # ── NOZUL ──
        noz_w_top = bw - 4
        noz_w_bot = bw - 10
        noz_y = bot
        nozzle = QPainterPath()
        nozzle.moveTo(-noz_w_top, noz_y)
        nozzle.lineTo(-noz_w_bot, noz_y + noz_h)
        nozzle.lineTo(noz_w_bot,  noz_y + noz_h)
        nozzle.lineTo(noz_w_top,  noz_y)
        nozzle.closeSubpath()
        noz_grad = QLinearGradient(-noz_w_top, 0, noz_w_top, 0)
        noz_grad.setColorAt(0.0,  QColor(80, 50, 20))
        noz_grad.setColorAt(0.4,  QColor(220, 100, 30))
        noz_grad.setColorAt(0.6,  QColor(255, 180, 80))
        noz_grad.setColorAt(1.0,  QColor(80, 50, 20))
        painter.setBrush(QBrush(noz_grad))
        painter.setPen(Qt.NoPen)
        painter.drawPath(nozzle)

        # ── ALEV ──
        flame_len = 28 + abs(math.sin(self.yaw * 0.05)) * 18
        flame = QPainterPath()
        flame.moveTo(-noz_w_bot + 4, noz_y + noz_h)
        flame.quadTo(0, noz_y + noz_h + flame_len * 1.4,
                     noz_w_bot - 4, noz_y + noz_h)
        flame_grad = QLinearGradient(0, noz_y + noz_h, 0, noz_y + noz_h + flame_len * 1.4)
        flame_grad.setColorAt(0.0,  QColor(255, 220, 100, 230))
        flame_grad.setColorAt(0.4,  QColor(255, 120, 30, 180))
        flame_grad.setColorAt(1.0,  QColor(255, 50, 0, 0))
        painter.setBrush(QBrush(flame_grad))
        painter.setPen(Qt.NoPen)
        painter.drawPath(flame)

        painter.restore()

        # Bilgi yazıları — dönüşümden bağımsız, sabit köşe
        painter.setPen(QColor(COLORS["text_dim"]))
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.drawText(8, 16, f"ωx: {self.pitch:+.1f}°")
        painter.drawText(8, 30, f"ωy: {self.roll:+.1f}°")
        painter.drawText(8, 44, f"ωz: {self.yaw:+.1f}°")



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

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(COLORS["bg_card"])))
        p.drawEllipse(cx - r - 5, cy - r - 5, (r + 5) * 2, (r + 5) * 2)

        p.setPen(QPen(QColor(COLORS["border_glow"]), 6, Qt.SolidLine, Qt.RoundCap))
        p.setBrush(Qt.NoBrush)
        p.drawArc(cx - r, cy - r, r * 2, r * 2, 225 * 16, -270 * 16)

        pct = max(0, min(1, (self.value - self.min_val) / (self.max_val - self.min_val)))
        span = int(-270 * 16 * pct)
        pen = QPen(self.color, 6, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        p.drawArc(cx - r, cy - r, r * 2, r * 2, 225 * 16, span)

        p.setPen(QPen(QColor(COLORS["text_primary"])))
        p.setFont(QFont("Segoe UI", 18, QFont.Bold))
        p.drawText(QRect(0, cy - 26, w, 30), Qt.AlignCenter, f"{self.value:.1f}")

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

class TechBackgroundWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._scan_phase = 0.0
        self._scan_timer = QTimer(self)
        self._scan_timer.timeout.connect(self._tick_scan)
        self._scan_timer.start(33)

    def _tick_scan(self):
        self._scan_phase += 0.012
        if self._scan_phase > 1.0:
            self._scan_phase = 0.0
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        p.fillRect(self.rect(), QColor(COLORS["bg_primary"]))

        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return

        p.setPen(QPen(QColor(0, 170, 255, 24), 1))
        step = 28
        for x in range(0, w, step):
            p.drawLine(x, 0, x, h)
        for y in range(0, h, step):
            p.drawLine(0, y, w, y)

        p.setPen(QPen(QColor(0, 212, 255, 14), 1))
        for x in range(-h, w, 48):
            p.drawLine(x, h, x + h, 0)

        y = int(self._scan_phase * (h + 90)) - 45
        scan = QLinearGradient(0, y - 18, 0, y + 18)
        scan.setColorAt(0.0, QColor(0, 212, 255, 0))
        scan.setColorAt(0.5, QColor(0, 212, 255, 40))
        scan.setColorAt(1.0, QColor(0, 212, 255, 0))
        p.fillRect(0, y - 18, w, 36, scan)

class SensorCard(QFrame):
    def __init__(self, title, unit, color="#00D4FF", show_graph=True):
        super().__init__()
        self.title = title
        self.color = color
        self._value = 0.0
        self._pulse = 0.0
        self.setObjectName("sensorCard")
        self._pulse_anim = QPropertyAnimation(self, b"pulse", self)
        self._pulse_anim.setDuration(220)
        self._pulse_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._apply_style()

        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(24)
        glow.setOffset(0, 0)
        glow_color = QColor(self.color)
        glow_color.setAlpha(55)
        glow.setColor(glow_color)
        self.setGraphicsEffect(glow)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 12)
        layout.setSpacing(6)

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font: 600 14px 'Segoe UI'; letter-spacing: 2px;")
        layout.addWidget(title_lbl)

        self.val_lbl = QLabel("—")
        self.val_lbl.setAlignment(Qt.AlignCenter)
        self.val_lbl.setStyleSheet(f"color: {color}; font: 700 34px 'Segoe UI';")
        layout.addWidget(self.val_lbl)

        unit_lbl = QLabel(unit)
        unit_lbl.setAlignment(Qt.AlignCenter)
        unit_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font: 500 12px 'Segoe UI';")
        layout.addWidget(unit_lbl)

        if show_graph:
            self.graph = MiniGraph(color=color)
            layout.addWidget(self.graph)
        else:
            self.graph = None

    def _apply_style(self):
        rgb = QColor(self.color)
        r, g, b, _ = rgb.getRgb()
        pulse_alpha = int(35 + 90 * self._pulse)
        top_alpha = int(160 + 70 * self._pulse)
        self.setStyleSheet(f"""
            QFrame#sensorCard {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(13, 31, 60, 230),
                    stop: 1 rgba(10, 22, 40, 215)
                );
                border: 1px solid rgba({r}, {g}, {b}, {pulse_alpha});
                border-radius: 12px;
                border-top: 2px solid rgba({r}, {g}, {b}, {top_alpha});
            }}
        """)

    def _get_pulse(self):
        return self._pulse

    def _set_pulse(self, v):
        self._pulse = v
        self._apply_style()

    pulse = pyqtProperty(float, _get_pulse, _set_pulse)

    def _trigger_pulse(self):
        self._pulse_anim.stop()
        self._pulse_anim.setStartValue(1.0)
        self._pulse_anim.setEndValue(0.0)
        self._pulse_anim.start()

    def update_value(self, v):
        prev = self._value
        self._value = v
        self.val_lbl.setText(str(v))
        if self.graph:
            self.graph.add_value(float(v))
        if abs(float(v) - float(prev)) > 0.4:
            self._trigger_pulse()

class TopBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(52)
        self.setStyleSheet(f"""
            background: {COLORS['bg_secondary']};
            border-bottom: 1px solid {COLORS['border_glow']};
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)

        logo = QLabel("⬢  GÖKTİGİN YER İSTASYONU")
        logo.setStyleSheet(f"color: {COLORS['accent_cyan']}; font: 700 13px 'Segoe UI'; letter-spacing: 3px;")
        layout.addWidget(logo)

        layout.addStretch()

        self.status_items = {}
        for key, label in [("PKT", "PKT"), ("FREQ", "FREKANS"), ("DELAY", "GECİKME")]:
            frame = QFrame()
            frame.setStyleSheet(f"""
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border_glow']};
                border-radius: 6px;
            """)
            fl = QHBoxLayout(frame)
            fl.setContentsMargins(10, 4, 10, 4)
            fl.setSpacing(6)
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font: 10px 'Segoe UI'; letter-spacing: 1px;")
            val = QLabel("—")
            val.setStyleSheet(f"color: {COLORS['text_primary']}; font: 700 12px 'Segoe UI';")
            fl.addWidget(lbl)
            fl.addWidget(val)
            self.status_items[key] = val
            layout.addWidget(frame)

        layout.addSpacing(12)

        self.arm_btn = QPushButton("AKTİF")
        self.arm_btn.setFixedSize(90, 32)
        self.arm_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent_green']};
                color: #000;
                font: 700 11px 'Segoe UI';
                letter-spacing: 2px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background: #00ffb3;
            }}
        """)
        layout.addWidget(self.arm_btn)
        
        self.settings_btn = QPushButton("⚙ AYARLAR")
        self.settings_btn.setFixedSize(100, 32)
        self.settings_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_primary']};
                font: 700 11px 'Segoe UI';
                letter-spacing: 2px;
                border-radius: 6px;
                border: 1px solid {COLORS['accent_cyan']};
            }}
            QPushButton:hover {{
                background: {COLORS['accent_cyan']};
                color: #000;
            }}
        """)
        layout.addWidget(self.settings_btn)

        self.time_lbl = QLabel("")
        self.time_lbl.setStyleSheet(f"color: {COLORS['accent_cyan']}; font: 11px 'Segoe UI';")
        layout.addWidget(self.time_lbl)

    def update_data(self, data):
        self.status_items["PKT"].setText(str(data["pkt"]))
        self.status_items["DELAY"].setText("64ms")
        self.time_lbl.setText(data["timestamp"])

class StatusBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(36)
        self.setStyleSheet(f"""
            background: {COLORS['bg_secondary']};
            border-top: 1px solid {COLORS['border_glow']};
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(30)

        self.items = {}
        for key, label, color in [
            ("ALT",  "İRTİFA",  COLORS["accent_cyan"]),
            ("VEL",  "HIZ",     COLORS["accent_green"]),
        ]:
            lbl = QLabel(f"{label}  —")
            lbl.setStyleSheet(f"color: {color}; font: 12px 'Segoe UI'; letter-spacing: 1px;")
            layout.addWidget(lbl)
            self.items[key] = lbl

        layout.addStretch()

        mission_lbl = QLabel("GÖREV: TEKNOFEST 2026 | ORTA İRTİFA")
        mission_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font: 10px 'Segoe UI';")
        layout.addWidget(mission_lbl)

    def update_data(self, data):
        self.items["ALT"].setText(f"İRTİFA  {data['altitude']:.0f} m")
        self.items["VEL"].setText(f"HIZ  {data['velocity']:.1f} m/s")

class GPSPanel(QFrame):
    def __init__(self):
        super().__init__()
        tech_blue = COLORS["accent_tech_blue"]
        self.setStyleSheet(f"""
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border_glow']};
            border-radius: 12px;
            border-top: 2px solid {tech_blue};
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        title = QLabel("⌖ GPS")
        title.setStyleSheet(f"color: {COLORS['text_secondary']}; font: 600 11px 'Segoe UI'; letter-spacing: 2px;")
        layout.addWidget(title)

        self.lat_lbl = QLabel("—")
        self.lat_lbl.setStyleSheet(f"color: {tech_blue}; font: 700 16px 'Segoe UI';")
        layout.addWidget(self.lat_lbl)

        self.lon_lbl = QLabel("—")
        self.lon_lbl.setStyleSheet(f"color: {tech_blue}; font: 700 16px 'Segoe UI';")
        layout.addWidget(self.lon_lbl)

        self.galt_lbl = QLabel("—")
        self.galt_lbl.setStyleSheet(f"color: {COLORS['accent_green']}; font: 700 16px 'Segoe UI';")
        layout.addWidget(self.galt_lbl)

        unit = QLabel("enlem / boylam / gps irtifası")
        unit.setStyleSheet(f"color: {COLORS['text_dim']}; font: 11px 'Segoe UI';")
        layout.addWidget(unit)

    def update_data(self, lat, lon, gps_alt=None):
        self.lat_lbl.setText(f"φ {lat:.6f}")
        self.lon_lbl.setText(f"λ {lon:.6f}")
        if gps_alt is not None:
            self.galt_lbl.setText(f"↑ {gps_alt:.1f} m")


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # Filtre değişkenleri
        self.filter_pitch = 0.0
        self.filter_roll  = 0.0
        self.filter_yaw   = 0.0
        self.alpha        = 0.96 # Varsayılan filtre katsayısı
        
        self._build_ui()
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.rocket_widget.update)
        self.anim_timer.start(50)

    def _build_ui(self):
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # Top bar
        self.top_bar = TopBar()
        page_layout.addWidget(self.top_bar)

        # İçerik alanı
        content = TechBackgroundWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(14)
        page_layout.addWidget(content, 1)

        # ── SOL PANEL: Roket + GPS ──
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        self.rocket_widget = RocketWidget()
        self.rocket_widget.setFixedWidth(220)
        left_panel.addWidget(self.rocket_widget)

        self.gps_panel = GPSPanel()
        left_panel.addWidget(self.gps_panel)

        left_panel.addStretch()
        content_layout.addLayout(left_panel)

        # ── ORTA PANEL: Sensor kartları ──
        center_panel = QVBoxLayout()
        center_panel.setSpacing(10)

        # Üst satır: Hız | İrtifa | Sıcaklık | Basınç
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self.card_velocity    = SensorCard("◌ HIZ",      "m/s", "#00D7FF")
        self.card_altitude    = SensorCard("◌ İRTİFA",   "m",   "#00FFB2")
        self.card_temperature = SensorCard("◌ SICAKLIK", "°C",  "#FF8A2B")
        self.card_pressure    = SensorCard("◌ BASINÇ",   "hPa", "#FFD84A")
        for card in [self.card_velocity, self.card_altitude, self.card_temperature, self.card_pressure]:
            row1.addWidget(card)
        center_panel.addLayout(row1)

        # 2. satır: İvme X | İvme Y | İvme Z | Dikey Hız
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self.card_accel_x = SensorCard("◌ İVME X", "m/s²", "#B56BFF")
        self.card_accel_y = SensorCard("◌ İVME Y", "m/s²", "#FF5FC7")
        self.card_accel_z = SensorCard("◌ İVME Z", "m/s²", "#FF4D7E")
        self.card_vertical_vel = SensorCard("◌ DİKEY HIZ", "m/s", "#00B4D8")
        for card in [self.card_accel_x, self.card_accel_y, self.card_accel_z, self.card_vertical_vel]:
            row2.addWidget(card)
        center_panel.addLayout(row2)

        # 3. satır: Gyro ωx | ωy | ωz
        row3 = QHBoxLayout()
        row3.setSpacing(10)
        self.card_gyro_x = SensorCard("◌ ωx", "°/s", "#00FFD0")
        self.card_gyro_y = SensorCard("◌ ωy", "°/s", "#00CFFF")
        self.card_gyro_z = SensorCard("◌ ωz", "°/s", "#0090FF")
        for card in [self.card_gyro_x, self.card_gyro_y, self.card_gyro_z]:
            row3.addWidget(card)
        center_panel.addLayout(row3)

        content_layout.addLayout(center_panel, 1)

        # ── SAĞ PANEL: Dairesel göstergeler ──
        right_panel = QVBoxLayout()
        right_panel.setSpacing(12)
        right_panel.setAlignment(Qt.AlignTop)

        right_title = QLabel("◉ GÖSTERGELER")
        right_title.setStyleSheet(f"color: {COLORS['text_dim']}; font: 10px 'Segoe UI'; letter-spacing: 2px;")
        right_panel.addWidget(right_title, 0, Qt.AlignCenter)

        self.gauge_vel = CircularGauge("HIZ",    "m/s", 0, 300,  COLORS["accent_cyan"])
        self.gauge_alt = CircularGauge("İRTİFA", "ft",   0, 3500, COLORS["accent_green"])
        self.gauge_temp = CircularGauge("SICAKLIK", "°C", -40, 80, COLORS["accent_orange"])

        for g in [self.gauge_vel, self.gauge_alt, self.gauge_temp]:
            right_panel.addWidget(g, 0, Qt.AlignCenter)

        right_panel.addStretch()
        content_layout.addLayout(right_panel)

        # Status bar
        self.status_bar_widget = StatusBar()
        page_layout.addWidget(self.status_bar_widget)

    def update_data(self, data):
        self.top_bar.update_data(data)
        self.status_bar_widget.update_data(data)

        self.status_bar_widget.status_items["PKT"].setText(str(data["pkt"]))
        self.status_bar_widget.status_items["FREQ"].setText(f"{data.get('actual_hz', 0):.1f} Hz")

        self.card_velocity.update_value(data["velocity"])
        self.card_altitude.update_value(data["altitude"])
        self.card_temperature.update_value(data["temperature"])
        self.card_pressure.update_value(data["pressure"])
        self.card_accel_x.update_value(data["accel_x"])
        self.card_accel_y.update_value(data["accel_y"])
        self.card_accel_z.update_value(data["accel_z"])
        self.card_vertical_vel.update_value(data["vertical_velocity"])

        self.card_gyro_x.update_value(data["gyro_x"])
        self.card_gyro_y.update_value(data["gyro_y"])
        self.card_gyro_z.update_value(data["gyro_z"])

        self.gps_panel.update_data(data["latitude"], data["longitude"], data.get("gps_altitude"))

        self.gauge_vel.set_value(data["velocity"])
        self.gauge_alt.set_value(data["altitude"])
        self.gauge_temp.set_value(data["temperature"])

        # İvmeden gelen tahmini açılar
        accel_pitch = math.degrees(math.atan2(data["accel_x"], abs(data["accel_z"])))
        accel_roll  = math.degrees(math.atan2(data["accel_y"], abs(data["accel_z"])))
        
        # Zaman deltası (Simülasyon yaklaşık 10Hz/0.1 sn ile çalışıyor)
        dt = 0.1
        
        # Complementary Filter (Tamamlayıcı Filtre)
        # Gyro verisiyle ivme verisini birleştirip pürüzsüz açı elde ediyoruz
        self.filter_pitch = self.alpha * (self.filter_pitch + data["gyro_x"] * dt) + (1.0 - self.alpha) * accel_pitch
        self.filter_roll  = self.alpha * (self.filter_roll  + data["gyro_y"] * dt) + (1.0 - self.alpha) * accel_roll
        self.filter_yaw   = self.filter_yaw + data["gyro_z"] * dt
        
        self.rocket_widget.set_orientation(self.filter_pitch, self.filter_roll, self.filter_yaw)

    def set_filter_alpha(self, alpha_percent):
        """Settings sayfasından gelen % değerini 0.0-1.0 arasına çevirir."""
        self.alpha = alpha_percent / 100.0
