from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from ui.styles import COLORS

class TestPage(QWidget):
    """
    Test ve Simülasyon Ekranı
    Kullanıcının simülasyonu başlatıp durdurmasını sağlar.
    """
    def __init__(self, state_bus):
        super().__init__()
        self.state_bus = state_bus
        self._setup_ui()
        
    def _setup_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['bg_primary']};
            }}
            QLabel#pageTitle {{
                color: {COLORS['text_primary']};
                font: 700 24px 'Segoe UI';
                letter-spacing: 2px;
            }}
            QLabel#pageDesc {{
                color: {COLORS['text_secondary']};
                font: 400 14px 'Segoe UI';
            }}
            QPushButton#btnStart {{
                background: {COLORS['accent_cyan']};
                color: #000;
                font: 700 16px 'Segoe UI';
                padding: 15px 30px;
                border-radius: 8px;
                border: none;
            }}
            QPushButton#btnStart:hover {{
                background: #00e5ff;
            }}
            QPushButton#btnStop {{
                background: transparent;
                color: {COLORS['accent_red']};
                font: 700 16px 'Segoe UI';
                padding: 15px 30px;
                border-radius: 8px;
                border: 2px solid {COLORS['accent_red']};
            }}
            QPushButton#btnStop:hover {{
                background: rgba(255, 45, 85, 0.1);
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("SİMÜLASYON KONTROL MERKEZİ")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Desc
        desc = QLabel("Arkaplanda çalışan telemetri simülatörünü buradan başlatabilir veya durdurabilirsiniz.\nTest verileri Dashboard ve Telemetri Verileri ekranlarına yansıyacaktır.")
        desc.setObjectName("pageDesc")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Buttons Layout
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(20)
        
        # Start Button
        self.btn_start = QPushButton("▶ TESTİ BAŞLAT")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.clicked.connect(lambda: self.state_bus.simulation_command.emit("start"))
        btn_layout.addWidget(self.btn_start)
        
        # Stop Button
        self.btn_stop = QPushButton("■ TESTİ DURDUR")
        self.btn_stop.setObjectName("btnStop")
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.clicked.connect(lambda: self.state_bus.simulation_command.emit("stop"))
        btn_layout.addWidget(self.btn_stop)

        # Clear Button
        self.btn_clear = QPushButton("🗑 VERİLERİ TEMİZLE")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                font: 700 14px 'Segoe UI';
                padding: 15px 25px;
                border-radius: 8px;
                border: 2px dashed {COLORS['text_dim']};
            }}
            QPushButton:hover {{
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['text_secondary']};
                background: rgba(255, 255, 255, 0.05);
            }}
        """)
        self.btn_clear.clicked.connect(lambda: self.state_bus.simulation_command.emit("clear"))
        btn_layout.addWidget(self.btn_clear)
        
        layout.addLayout(btn_layout)
