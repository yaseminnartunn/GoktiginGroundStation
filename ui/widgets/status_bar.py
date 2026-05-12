from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel
from ui.styles import COLORS, DATA_COLORS

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
            ("İRTİFA", "İRTİFA", DATA_COLORS["İRTİFA (m)"]),
            ("HIZ",    "HIZ",    DATA_COLORS["HIZ (m/s)"]),
            ("SİNYAL", "SİNYAL GÜCÜ", COLORS["accent_yellow"]),
            ("KAYIP",  "KAYIP",  COLORS["accent_orange"]),
        ]:
            lbl = QLabel(f"{label}  —")
            lbl.setStyleSheet(f"color: {color}; font: 12px 'Segoe UI'; letter-spacing: 1px;")
            layout.addWidget(lbl)
            self.items[key] = lbl

        layout.addStretch()

        mission_lbl = QLabel("MISSION: TEKNOFEST 2026 | ORTA İRTİFA SINIFI")
        mission_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font: 10px 'Segoe UI';")
        layout.addWidget(mission_lbl)

    def update_data(self, data):
        if not data:
            for key, lbl in self.items.items():
                lbl.setText(f"{key}  —")
            return
            
        self.items["İRTİFA"].setText(f"İRTİFA  {data['altitude']:.0f} m")
        self.items["HIZ"].setText(f"HIZ  {data['velocity']:.1f} m/s")
        self.items["SİNYAL"].setText(f"SİNYAL GÜCÜ  {data['sinyal_gücü']} dBm")
        self.items["KAYIP"].setText(f"KAYIP  {data['paket_kaybi']:.2f}%")
