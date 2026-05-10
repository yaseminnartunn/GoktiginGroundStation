from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QProgressBar
from ui.styles import COLORS

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
