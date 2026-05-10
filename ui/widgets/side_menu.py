from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from ui.styles import COLORS

class SideMenu(QFrame):
    def __init__(self, menu_callback):
        super().__init__()
        self.menu_callback = menu_callback
        self.setFixedWidth(0) # Başlangıçta kapalı
        self.setStyleSheet(f"""
            background: {COLORS['bg_secondary']};
            border-right: 1px solid {COLORS['border_glow']};
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(4)
        
        title = QLabel("MENÜ")
        title.setStyleSheet(f"color: {COLORS['text_dim']}; font: 700 10px 'Segoe UI'; letter-spacing: 2px;")
        layout.addWidget(title, 0, Qt.AlignCenter)
        
        layout.addSpacing(8)
        
        self.buttons = {}
        menu_items = [
            ("dashboard", "📊 Dashboard"),
            ("veriler", "📋 Telemetri Verileri"),
            ("test", "⚙️ Test ve Simülasyon"),
        ]
        
        for key, label in menu_items:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self._btn_style(False))
            btn.clicked.connect(lambda checked, k=key: self.menu_callback(k))
            self.buttons[key] = btn
            layout.addWidget(btn)
        
        layout.addStretch()
        self.set_active("dashboard")
    
    def _btn_style(self, active):
        if active:
            return f"""
                QPushButton {{
                    background: {COLORS['accent_cyan']}20;
                    color: {COLORS['accent_cyan']};
                    font: 600 13px 'Segoe UI';
                    text-align: left;
                    padding: 12px 16px;
                    border-left: 3px solid {COLORS['accent_cyan']};
                    border-radius: 0px;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background: transparent;
                    color: {COLORS['text_secondary']};
                    font: 600 13px 'Segoe UI';
                    text-align: left;
                    padding: 12px 16px;
                    border: none;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background: {COLORS['bg_card']};
                    color: {COLORS['text_primary']};
                }}
            """

    def set_active(self, key):
        for k, btn in self.buttons.items():
            btn.setStyleSheet(self._btn_style(k == key))
