from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from ui.styles import COLORS

class TopBar(QFrame):
    def __init__(self, toggle_callback=None):
        super().__init__()
        self.setFixedHeight(52)
        self.setStyleSheet(f"""
            background: {COLORS['bg_secondary']};
            border-bottom: 1px solid {COLORS['border_glow']};
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)

        # Menü Aç/Kapat Butonu
        if toggle_callback:
            self.toggle_btn = QPushButton("☰")
            self.toggle_btn.setFixedSize(36, 36)
            self.toggle_btn.setCursor(Qt.PointingHandCursor)
            self.toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {COLORS['text_primary']};
                    font: 24px;
                    border: none;
                }}
                QPushButton:hover {{
                    color: {COLORS['accent_cyan']};
                }}
            """)
            self.toggle_btn.clicked.connect(toggle_callback)
            layout.addWidget(self.toggle_btn)

        # Logo
        logo = QLabel("⬡  GÖKTİGİN GROUND STATION")
        logo.setStyleSheet(f"color: {COLORS['accent_cyan']}; font: 700 13px 'Segoe UI'; letter-spacing: 3px;")
        layout.addWidget(logo)

        layout.addStretch()

        # Status göstergeleri
        self.status_items = {}
        for key, label in [("PKT", "PKT"), ("DELAY", "DELAY"), ("RSSI", "RSSI"), ("KAYIP", "KAYIP")]:
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
        if not data:
            self.status_items["PKT"].setText("—")
            self.status_items["DELAY"].setText("—")
            self.status_items["RSSI"].setText("—")
            self.status_items["KAYIP"].setText("—")
            self.time_lbl.setText("")
            return
            
        self.status_items["PKT"].setText(str(data["pkt"]))
        self.status_items["DELAY"].setText("64ms")
        self.status_items["RSSI"].setText(f"{data['rssi']} dBm")
        self.status_items["KAYIP"].setText(f"{data['kayip']}%")
        self.time_lbl.setText(data["timestamp"])
