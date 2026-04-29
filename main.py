import sys
import math
import random
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QFrame, QSizePolicy, QPushButton, QProgressBar,
    QGraphicsDropShadowEffect, QScrollArea, QStackedWidget, QGroupBox
)
from PyQt5.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QRect, QSize, pyqtProperty, QObject
)
from PyQt5.QtGui import (
    QColor, QPalette, QFont, QPainter, QPen, QBrush, QLinearGradient,
    QRadialGradient, QConicalGradient, QPixmap, QPolygon, QFontDatabase,
    QPainterPath, QTransform
)
import time
from girişsayfası import LoginPage


# ─────────────────────────────────────────────
#  RENK PALETİ
# ─────────────────────────────────────────────
COLORS = {
    "bg_primary":    "#050A14",
    "bg_secondary":  "#0A1628",
    "bg_card":       "#0D1F3C",
    "bg_card_hover": "#112547",
    "accent_cyan":   "#00D4FF",
    "accent_green":  "#00FF9C",
    "accent_orange": "#FF6B35",
    "accent_red":    "#FF2D55",
    "accent_yellow": "#FFD700",
    "accent_purple": "#BD00FF",
    "text_primary":  "#E8F4FD",
    "text_secondary":"#7BA3C8",
    "text_dim":      "#3A5A7A",
    "border_glow":   "#1A3A5C",
    "grid_line":     "#0F2040",
}


# ─────────────────────────────────────────────
#  VERI SİMÜLATÖRÜ (gerçek seri port yerine)
# ─────────────────────────────────────────────
class TelemetrySimulator(QThread):
    data_received = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._running = True
        self.altitude = 0.0
        self.velocity = 0.0
        self.phase = "IDLE"
        self.t = 0.0

    def run(self):
        while self._running:
            self.t += 0.1
            data = self._simulate()
            self.data_received.emit(data)
            time.sleep(0.1)

    def _simulate(self):
        t = self.t
        alt = max(0, 2800 * math.sin(t * 0.05) + random.gauss(0, 10))
        vel = max(0, 180 * math.sin(t * 0.05) * math.cos(t * 0.02) + random.gauss(0, 2))
        return {
            "velocity":    round(vel, 1),
            "altitude":    round(alt, 1),
            "accel_x":     round(random.gauss(0.2, 2.5), 2),
            "accel_y":     round(random.gauss(0.1, 2.3), 2),
            "accel_z":     round(random.gauss(-9.81, 1.2), 2),
            "temperature": round(-1.5 + alt * -0.006 + random.gauss(0, 0.3), 1),
            "pressure":    round(1013.25 * math.exp(-alt / 8500) + random.gauss(0, 0.5), 1),
            "battery":     round(max(0, 97 - t * 0.02 + random.gauss(0, 0.1)), 1),
            "latitude":    round(39.9053 + t * 0.00001 + random.gauss(0, 0.00002), 6),
            "longitude":   round(32.8049 + t * 0.00001 + random.gauss(0, 0.00002), 6),
            "rssi":        round(random.uniform(-105, -85), 1),
            "pkt":         int(t * 10),
            "loss":        round(random.uniform(0, 2), 1),
            "timestamp":   datetime.now().strftime("%H:%M:%S.%f")[:-3],
        }

    def stop(self):
        self._running = False


# ─────────────────────────────────────────────
#  GRAFIK WIDGET'I
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
#  ROCKET ORIENTATİON WIDGET
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
#  DAIRESEL GÖSTERGE
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
#  SENSOR KARTI
# ─────────────────────────────────────────────
class SensorCard(QFrame):
    def __init__(self, title, unit, color="#00D4FF", show_graph=True):
        super().__init__()
        self.title = title
        self.color = color
        self._value = 0.0
        self.setObjectName("sensorCard")
        self.setStyleSheet(f"""
            QFrame#sensorCard {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border_glow']};
                border-radius: 12px;
                border-top: 2px solid {color};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 10)
        layout.setSpacing(4)

        # Başlık
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font: 700 18px 'Segoe UI'; letter-spacing: 2px;")
        layout.addWidget(title_lbl)

        # Değer
        self.val_lbl = QLabel("—")
        self.val_lbl.setAlignment(Qt.AlignCenter)
        self.val_lbl.setStyleSheet(f"color: {color}; font: 700 36px 'Segoe UI';")
        layout.addWidget(self.val_lbl)

        # Birim
        unit_lbl = QLabel(unit)
        unit_lbl.setAlignment(Qt.AlignCenter)
        unit_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font: 700 14px 'Segoe UI';")
        layout.addWidget(unit_lbl)

        # Mini grafik
        if show_graph:
            self.graph = MiniGraph(color=color)
            layout.addWidget(self.graph)
        else:
            self.graph = None

    def update_value(self, v):
        self._value = v
        self.val_lbl.setText(str(v))
        if self.graph:
            self.graph.add_value(float(v))


# ─────────────────────────────────────────────
#  ÜST BAR
# ─────────────────────────────────────────────
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

        # Logo
        logo = QLabel("⬡  GÖKTİGİN GROUND STATION")
        logo.setStyleSheet(f"color: {COLORS['accent_cyan']}; font: 700 13px 'Segoe UI'; letter-spacing: 3px;")
        layout.addWidget(logo)

        layout.addStretch()

        # Status göstergeleri
        self.status_items = {}
        for key, label in [("PKT", "PKT"), ("DELAY", "DELAY"), ("RSSI", "RSSI"), ("LOSS", "LOSS%")]:
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

        # ARM butonu
        self.arm_btn = QPushButton("ARMED")
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

        # Zaman
        self.time_lbl = QLabel("")
        self.time_lbl.setStyleSheet(f"color: {COLORS['accent_cyan']}; font: 11px 'Segoe UI';")
        layout.addWidget(self.time_lbl)

    def update_data(self, data):
        self.status_items["PKT"].setText(str(data["pkt"]))
        self.status_items["DELAY"].setText("64ms")
        self.status_items["RSSI"].setText(f"{data['rssi']} dBm")
        self.status_items["LOSS"].setText(f"{data['loss']}%")
        self.time_lbl.setText(data["timestamp"])


# ─────────────────────────────────────────────
#  STATUS BAR (alt bilgi bandı)
# ─────────────────────────────────────────────
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
            ("ALT",  "ALT",  COLORS["accent_cyan"]),
            ("VEL",  "VEL",  COLORS["accent_green"]),
            ("RSSI", "RSSI", COLORS["accent_yellow"]),
            ("LOSS", "LOSS", COLORS["accent_orange"]),
        ]:
            lbl = QLabel(f"{label}  —")
            lbl.setStyleSheet(f"color: {color}; font: 12px 'Segoe UI'; letter-spacing: 1px;")
            layout.addWidget(lbl)
            self.items[key] = lbl

        layout.addStretch()

        mission_lbl = QLabel("MISSION: TEKNOFEST 2025 | ORTA İRTİFA SINIFI")
        mission_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font: 10px 'Segoe UI';")
        layout.addWidget(mission_lbl)

    def update_data(self, data):
        self.items["ALT"].setText(f"ALT  {data['altitude']:.0f} m")
        self.items["VEL"].setText(f"VEL  {data['velocity']:.1f} m/s")
        self.items["RSSI"].setText(f"RSSI  {data['rssi']} dBm")
        self.items["LOSS"].setText(f"LOSS  {data['loss']}%")


# ─────────────────────────────────────────────
#  GPS PANEL
# ─────────────────────────────────────────────
class GPSPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"""
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border_glow']};
            border-radius: 12px;
            border-top: 2px solid {COLORS['accent_purple']};
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        title = QLabel("GPS")
        title.setStyleSheet(f"color: {COLORS['text_secondary']}; font: 11px 'Segoe UI'; letter-spacing: 2px;")
        layout.addWidget(title)

        self.lat_lbl = QLabel("—")
        self.lat_lbl.setStyleSheet(f"color: {COLORS['accent_purple']}; font: 700 16px 'Segoe UI';")
        layout.addWidget(self.lat_lbl)

        self.lon_lbl = QLabel("—")
        self.lon_lbl.setStyleSheet(f"color: {COLORS['accent_purple']}; font: 700 16px 'Segoe UI';")
        layout.addWidget(self.lon_lbl)

        unit = QLabel("lat / lon")
        unit.setStyleSheet(f"color: {COLORS['text_dim']}; font: 11px 'Segoe UI';")
        layout.addWidget(unit)

    def update_data(self, lat, lon):
        self.lat_lbl.setText(f"φ {lat:.6f}")
        self.lon_lbl.setText(f"λ {lon:.6f}")


# ─────────────────────────────────────────────
#  BATARYA PANEL
# ─────────────────────────────────────────────
class BatteryPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"""
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border_glow']};
            border-radius: 12px;
            border-top: 2px solid {COLORS['accent_yellow']};
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        title = QLabel("BATARYA")
        title.setStyleSheet(f"color: {COLORS['text_secondary']}; font: 11px 'Segoe UI'; letter-spacing: 2px;")
        layout.addWidget(title)

        self.val_lbl = QLabel("—")
        self.val_lbl.setStyleSheet(f"color: {COLORS['accent_yellow']}; font: 700 30px 'Segoe UI';")
        layout.addWidget(self.val_lbl)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background: {COLORS['bg_secondary']};
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: {COLORS['accent_yellow']};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.bar)

        unit = QLabel("%")
        unit.setStyleSheet(f"color: {COLORS['text_dim']}; font: 11px 'Segoe UI';")
        layout.addWidget(unit)

    def update_value(self, v):
        self.val_lbl.setText(f"{v:.1f}")
        self.bar.setValue(int(v))
        color = COLORS["accent_green"] if v > 30 else COLORS["accent_orange"] if v > 15 else COLORS["accent_red"]
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background: {COLORS['bg_secondary']};
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 4px;
            }}
        """)


#  ANA PENCERE
# ─────────────────────────────────────────────
class GroundStation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GökTigin Ground Station — TEKNOFEST 2025")
        self.setMinimumSize(1280, 780)
        self.logo_path = (
            r"C:\Users\Acer\.cursor\projects\c-Users-Acer-OneDrive-Desktop-deneme\assets\c__Users_Acer_AppData_Roaming_Cursor_User_workspaceStorage_5586babad2924fabad38f53e1f4af2a6_images_image-75a32522-e95c-4ea2-a86a-4c64f6e6cb5b.png"
        )

        # Genel arka plan
        self.setStyleSheet(f"QMainWindow, QWidget {{ background: {COLORS['bg_primary']}; }}")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self.login_page = LoginPage(self.show_dashboard, self.logo_path, COLORS)
        self.dashboard_page = self._build_dashboard_page()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.dashboard_page)
        self.stack.setCurrentWidget(self.login_page)

        self.sim = None
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.rocket_widget.update)

    def _build_dashboard_page(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # Top bar
        self.top_bar = TopBar()
        page_layout.addWidget(self.top_bar)

        # İçerik alanı
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)
        page_layout.addWidget(content, 1)

        # ── SOL PANEL: Roket + GPS + Batarya ──
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        self.rocket_widget = RocketWidget()
        self.rocket_widget.setFixedWidth(220)
        left_panel.addWidget(self.rocket_widget)

        self.gps_panel = GPSPanel()
        left_panel.addWidget(self.gps_panel)

        self.battery_panel = BatteryPanel()
        left_panel.addWidget(self.battery_panel)

        left_panel.addStretch()
        content_layout.addLayout(left_panel)

        # ── ORTA PANEL: Sensor kartları ──
        center_panel = QVBoxLayout()
        center_panel.setSpacing(10)

        # Üst satır: Hız | İrtifa | Sıcaklık | Basınç
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self.card_velocity    = SensorCard("HIZ",      "m/s",  COLORS["accent_cyan"])
        self.card_altitude    = SensorCard("İRTİFA",   "m",    COLORS["accent_green"])
        self.card_temperature = SensorCard("SICAKLIK", "°C",   COLORS["accent_orange"])
        self.card_pressure    = SensorCard("BASINÇ",   "hPa",  COLORS["accent_yellow"])
        for card in [self.card_velocity, self.card_altitude, self.card_temperature, self.card_pressure]:
            row1.addWidget(card)
        center_panel.addLayout(row1)

        # Alt satır: İvme X | İvme Y | İvme Z
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self.card_accel_x = SensorCard("İVME X", "m/s²", COLORS["accent_purple"])
        self.card_accel_y = SensorCard("İVME Y", "m/s²", "#FF4FA3")
        self.card_accel_z = SensorCard("İVME Z", "m/s²", COLORS["accent_red"])
        for card in [self.card_accel_x, self.card_accel_y, self.card_accel_z]:
            row2.addWidget(card)
        center_panel.addLayout(row2)

        content_layout.addLayout(center_panel, 1)

        # ── SAĞ PANEL: Dairesel göstergeler ──
        right_panel = QVBoxLayout()
        right_panel.setSpacing(12)
        right_panel.setAlignment(Qt.AlignTop)

        right_title = QLabel("GÖSTERGELER")
        right_title.setStyleSheet(f"color: {COLORS['text_dim']}; font: 10px 'Segoe UI'; letter-spacing: 2px;")
        right_panel.addWidget(right_title, 0, Qt.AlignCenter)

        self.gauge_vel = CircularGauge("HIZ",    "m/s", 0, 300,  COLORS["accent_cyan"])
        self.gauge_alt = CircularGauge("İRTİFA", "m",   0, 3500, COLORS["accent_green"])
        self.gauge_bat = CircularGauge("BATARYA","%",   0, 100,  COLORS["accent_yellow"])

        for g in [self.gauge_vel, self.gauge_alt, self.gauge_bat]:
            right_panel.addWidget(g, 0, Qt.AlignCenter)

        right_panel.addStretch()
        content_layout.addLayout(right_panel)

        # Status bar
        self.status_bar_widget = StatusBar()
        page_layout.addWidget(self.status_bar_widget)
        return page

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard_page)
        if self.sim is None:
            self.sim = TelemetrySimulator()
            self.sim.data_received.connect(self.on_data)
            self.sim.start()
        if not self.anim_timer.isActive():
            self.anim_timer.start(50)

    def on_data(self, data):
        self.top_bar.update_data(data)
        self.status_bar_widget.update_data(data)

        self.card_velocity.update_value(data["velocity"])
        self.card_altitude.update_value(data["altitude"])
        self.card_temperature.update_value(data["temperature"])
        self.card_pressure.update_value(data["pressure"])
        self.card_accel_x.update_value(data["accel_x"])
        self.card_accel_y.update_value(data["accel_y"])
        self.card_accel_z.update_value(data["accel_z"])

        self.gps_panel.update_data(data["latitude"], data["longitude"])
        self.battery_panel.update_value(data["battery"])

        self.gauge_vel.set_value(data["velocity"])
        self.gauge_alt.set_value(data["altitude"])
        self.gauge_bat.set_value(data["battery"])

        # Roket yönelimi ivmelerden simüle et
        pitch = math.degrees(math.atan2(data["accel_x"], abs(data["accel_z"])))
        roll  = math.degrees(math.atan2(data["accel_y"], abs(data["accel_z"])))
        self.rocket_widget.set_orientation(pitch, roll * 0.3)

    def closeEvent(self, event):
        if self.sim is not None:
            self.sim.stop()
            self.sim.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    win = GroundStation()
    win.show()
    sys.exit(app.exec_())