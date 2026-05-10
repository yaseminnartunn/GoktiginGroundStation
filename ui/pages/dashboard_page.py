from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel
from PyQt5.QtCore import Qt
from ui.widgets.rocket_widget import RocketWidget
from ui.widgets.circular_gauge import CircularGauge
from ui.widgets.sensor_card import SensorCard
from ui.widgets.panels import GPSPanel
from ui.styles import COLORS, DATA_COLORS

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        content_layout = QHBoxLayout(self)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)

        # ── SOL PANEL: Roket + GPS + Batarya ──
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

        # Satır 1: Hız | İrtifa | Sıcaklık | Basınç
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self.card_velocity    = SensorCard("HIZ",      "m/s",  DATA_COLORS["HIZ (m/s)"])
        self.card_altitude    = SensorCard("İRTİFA",   "m",    DATA_COLORS["İRTİFA (m)"])
        self.card_temperature = SensorCard("SICAKLIK", "°C",   DATA_COLORS["SICAKLIK (°C)"])
        self.card_pressure    = SensorCard("BASINÇ",   "hPa",  DATA_COLORS["BASINÇ (hPa)"])
        for card in [self.card_velocity, self.card_altitude, self.card_temperature, self.card_pressure]:
            row1.addWidget(card)
        center_panel.addLayout(row1)

        # Satır 2: İvme X | İvme Y | İvme Z | Dikey Hız
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self.card_accel_x = SensorCard("İVME X", "m/s²", DATA_COLORS["İVME X (m/s²)"])
        self.card_accel_y = SensorCard("İVME Y", "m/s²", DATA_COLORS["İVME Y (m/s²)"])
        self.card_accel_z = SensorCard("İVME Z", "m/s²", DATA_COLORS["İVME Z (m/s²)"])
        self.card_vertical_velocity = SensorCard("DİKEY HIZ", "m/s", DATA_COLORS["DİKEY HIZ (m/s)"])
        for card in [self.card_accel_x, self.card_accel_y, self.card_accel_z, self.card_vertical_velocity]:
            row2.addWidget(card)
        center_panel.addLayout(row2)

        # Satır 3: ω X | ω Y | ω Z
        row3 = QHBoxLayout()
        row3.setSpacing(10)
        self.card_gyro_x = SensorCard("ω X", "°/s", DATA_COLORS["ω X (°/s)"])
        self.card_gyro_y = SensorCard("ω Y", "°/s", DATA_COLORS["ω Y (°/s)"])
        self.card_gyro_z = SensorCard("ω Z", "°/s", DATA_COLORS["ω Z (°/s)"])
        for card in [self.card_gyro_x, self.card_gyro_y, self.card_gyro_z]:
            row3.addWidget(card)
        center_panel.addLayout(row3)
        
        # Kartların sayfaya yayılması için stretch'i kaldırdık


        content_layout.addLayout(center_panel, 1)

        # ── SAĞ PANEL: Dairesel göstergeler ──
        right_panel = QVBoxLayout()
        right_panel.setSpacing(12)
        right_panel.setAlignment(Qt.AlignTop)

        right_title = QLabel("GÖSTERGELER")
        right_title.setStyleSheet(f"color: {COLORS['text_dim']}; font: 10px 'Segoe UI'; letter-spacing: 2px;")
        right_panel.addWidget(right_title, 0, Qt.AlignCenter)

        self.gauge_vel = CircularGauge("HIZ",    "m/s", 0, 300,  DATA_COLORS["HIZ (m/s)"])
        self.gauge_alt = CircularGauge("İRTİFA", "m",   0, 3500, DATA_COLORS["İRTİFA (m)"])

        for g in [self.gauge_vel, self.gauge_alt]:
            right_panel.addWidget(g, 0, Qt.AlignCenter)

        right_panel.addStretch()
        content_layout.addLayout(right_panel)

    def update_data(self, data):
        if not data:
            self.card_velocity.update_value("—")
            self.card_altitude.update_value("—")
            self.card_temperature.update_value("—")
            self.card_pressure.update_value("—")
            self.card_accel_x.update_value("—")
            self.card_accel_y.update_value("—")
            self.card_accel_z.update_value("—")
            self.card_vertical_velocity.update_value("—")
            self.card_gyro_x.update_value("—")
            self.card_gyro_y.update_value("—")
            self.card_gyro_z.update_value("—")
            self.gps_panel.lat_lbl.setText("—")
            self.gps_panel.lon_lbl.setText("—")
            self.gauge_vel.set_value(0)
            self.gauge_alt.set_value(0)
            self.rocket_widget.set_orientation(0, 0)
            return
            
        import math
        self.card_velocity.update_value(data["velocity"])
        self.card_altitude.update_value(data["altitude"])
        self.card_temperature.update_value(data["temperature"])
        self.card_pressure.update_value(data["pressure"])
        self.card_accel_x.update_value(data["accel_x"])
        self.card_accel_y.update_value(data["accel_y"])
        self.card_accel_z.update_value(data["accel_z"])
        self.card_vertical_velocity.update_value(data["vertical_velocity"])
        self.card_gyro_x.update_value(data["gyro_x"])
        self.card_gyro_y.update_value(data["gyro_y"])
        self.card_gyro_z.update_value(data["gyro_z"])

        self.gps_panel.update_data(data["latitude"], data["longitude"])

        self.gauge_vel.set_value(data["velocity"])
        self.gauge_alt.set_value(data["altitude"])

        pitch = math.degrees(math.atan2(data["accel_x"], abs(data["accel_z"])))
        roll  = math.degrees(math.atan2(data["accel_y"], abs(data["accel_z"])))
        self.rocket_widget.set_orientation(pitch, roll * 0.3)
