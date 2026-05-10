import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame, QGridLayout, QSpinBox, QCheckBox,
    QGraphicsDropShadowEffect, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QColor, QFont


class SettingsPage(QWidget):
    def __init__(self, colors):
        super().__init__()
        self.colors = colors
        self._connected = False
        self.init_ui()

        # UTC saat zamanlayıcısı
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()

    # ------------------------------------------------------------------ #
    #  Arayüz Kurulumu
    # ------------------------------------------------------------------ #
    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(40, 40, 40, 40)
        root_layout.setSpacing(0)

        # Ana kart
        self.card = QFrame()
        self.card.setObjectName("gsCard")

        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(50)
        glow.setOffset(0, 0)
        c = QColor("#00B4D8")
        c.setAlpha(55)
        glow.setColor(c)
        self.card.setGraphicsEffect(glow)

        self.card.setStyleSheet(f"""
            QFrame#gsCard {{
                background: rgba(3, 8, 15, 245);
                border: 1px solid #0F3A5C;
                border-radius: 12px;
            }}
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(32, 28, 32, 24)
        card_layout.setSpacing(18)

        # ── BAŞLIK SATIRI ──────────────────────────────────────────────
        card_layout.addWidget(self._build_header())

        # ── AYIRICI ────────────────────────────────────────────────────
        card_layout.addWidget(self._hline("#0F3A5C"))

        # ── SERİ BAĞLANTI PANELİ ──────────────────────────────────────
        card_layout.addWidget(self._build_serial_panel())

        # ── SİMÜLASYON SATIRI ─────────────────────────────────────────
        card_layout.addWidget(self._build_simulation_row())

        # ── TELEMETRİ AYARLARI ────────────────────────────────────────
        card_layout.addWidget(self._build_telemetry_panel())

        # ── BUTONLAR ──────────────────────────────────────────────────
        card_layout.addWidget(self._build_buttons())

        # ── AYIRICI ────────────────────────────────────────────────────
        card_layout.addWidget(self._hline("#0A2A3A"))

        # ── ALT BİLGİ SATIRI ──────────────────────────────────────────
        card_layout.addWidget(self._build_footer())

        root_layout.addWidget(self.card)
        root_layout.addStretch()

    # ------------------------------------------------------------------ #
    #  Bileşen Oluşturucular
    # ------------------------------------------------------------------ #
    def _build_header(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Geri Dön Butonu
        self.btn_back = QPushButton("❮ GERİ")
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.setStyleSheet("""
            QPushButton {
                color: #A0C4D8;
                font: 700 12px 'Segoe UI';
                background: transparent;
                border: 1px solid #3A6A8A;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: rgba(58, 106, 138, 50);
                color: #00B4D8;
            }
        """)

        # Logo çemberi
        logo = QLabel("✦")
        logo.setFixedSize(44, 44)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            color: #00B4D8;
            font-size: 20px;
            border: 2px solid #00B4D8;
            border-radius: 22px;
            background: rgba(0, 180, 216, 10);
        """)

        # Başlık bloku
        title_block = QVBoxLayout()
        title_block.setSpacing(2)

        title = QLabel("YER KONTROL İSTASYONU")
        title.setStyleSheet("""
            color: #A0C4D8;
            font: 700 13px 'Segoe UI';
            letter-spacing: 4px;
            background: transparent;
        """)

        subtitle = QLabel("GÖREV BAĞLANTISI  /  HABERLEŞME VE SİMÜLASYON MODÜLÜ")
        subtitle.setStyleSheet("""
            color: #3A6A8A;
            font: 500 9px 'Courier New';
            letter-spacing: 2px;
            background: transparent;
        """)

        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        # Durum göstergesi
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(6)

        self.lbl_dot = QLabel("●")
        self.lbl_dot.setStyleSheet("color: #FF4D4D; font-size: 10px; background: transparent;")

        self.lbl_status = QLabel("ÇEVRİMDIŞI")
        self.lbl_status.setStyleSheet("""
            color: #3A6A8A;
            font: 600 10px 'Courier New';
            letter-spacing: 2px;
            background: transparent;
        """)

        status_layout.addWidget(self.lbl_dot)
        status_layout.addWidget(self.lbl_status)

        layout.addWidget(self.btn_back)
        layout.addWidget(logo)
        layout.addLayout(title_block)
        layout.addStretch()
        layout.addWidget(status_frame)
        return frame

    def _build_serial_panel(self):
        """Seri bağlantı ayarlarını içeren panel."""
        frame = QFrame()
        frame.setObjectName("serialPanel")
        frame.setStyleSheet("""
            QFrame#serialPanel {
                background: rgba(5, 20, 40, 200);
                border: 1px solid #0F3A5C;
                border-top: 2px solid #00B4D8;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 18)
        layout.setSpacing(14)

        panel_title = QLabel("◈  SERİ BAĞLANTI AYARLARI")
        panel_title.setStyleSheet("""
            color: #3A6A8A;
            font: 600 9px 'Courier New';
            letter-spacing: 3px;
            background: transparent;
        """)
        layout.addWidget(panel_title)

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)

        # COM Port
        grid.addWidget(self._field_label("COM PORT SEÇİMİ"), 0, 0)
        self.cb_port = self._make_combo(["COM1", "COM2", "COM3", "COM4", "COM5"])
        try:
            import serial.tools.list_ports
            ports = [p.device for p in serial.tools.list_ports.comports()]
            if ports:
                self.cb_port.clear()
                self.cb_port.addItems(ports)
        except ImportError:
            pass
        grid.addWidget(self.cb_port, 1, 0)

        # Baud Hızı
        grid.addWidget(self._field_label("BAUD HIZI"), 0, 1)
        self.cb_baud = self._make_combo(["9600"])
        self.cb_baud.setEnabled(False)
        grid.addWidget(self.cb_baud, 1, 1)

        # Zaman Aşımı
        grid.addWidget(self._field_label("ZAMAN AŞIMI"), 0, 2)
        self.spin_timeout = QSpinBox()
        self.spin_timeout.setRange(1, 15)
        self.spin_timeout.setValue(3)
        self.spin_timeout.setSuffix("  sn")
        self.spin_timeout.setStyleSheet(self._input_style())
        grid.addWidget(self.spin_timeout, 1, 2)

        layout.addLayout(grid)
        return frame

    def _build_telemetry_panel(self):
        """Telemetri ve filtreleme ayarları."""
        frame = QFrame()
        frame.setObjectName("telemetryPanel")
        frame.setStyleSheet("""
            QFrame#telemetryPanel {
                background: rgba(5, 20, 40, 200);
                border: 1px solid #0F3A5C;
                border-top: 2px solid #BD00FF;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 18)
        layout.setSpacing(14)

        panel_title = QLabel("◈  TELEMETRİ VE FİLTRE AYARLARI")
        panel_title.setStyleSheet("""
            color: #3A6A8A;
            font: 600 9px 'Courier New';
            letter-spacing: 3px;
            background: transparent;
        """)
        layout.addWidget(panel_title)

        grid = QGridLayout()
        grid.setSpacing(16)

        # Veri Hızı (Hz)
        grid.addWidget(self._field_label("VERİ YENİLEME HIZI"), 0, 0)
        self.spin_rate = QSpinBox()
        self.spin_rate.setRange(1, 50)
        self.spin_rate.setValue(5)
        self.spin_rate.setSuffix("  Hz")
        self.spin_rate.setStyleSheet(self._input_style())
        grid.addWidget(self.spin_rate, 1, 0)

        # Filtre Katsayısı (%)
        grid.addWidget(self._field_label("FİLTRE HASSASİYETİ (ALPHA)"), 0, 1)
        self.spin_filter = QSpinBox()
        self.spin_filter.setRange(0, 100)
        self.spin_filter.setValue(96)
        self.spin_filter.setSuffix("  %")
        self.spin_filter.setStyleSheet(self._input_style())
        grid.addWidget(self.spin_filter, 1, 1)

        # Log Hassasiyeti
        grid.addWidget(self._field_label("VERİ HASSASİYETİ"), 0, 2)
        self.cb_precision = self._make_combo(["Düşük", "Normal", "Yüksek"])
        self.cb_precision.setCurrentText("Normal")
        grid.addWidget(self.cb_precision, 1, 2)

        layout.addLayout(grid)
        return frame

    def _build_simulation_row(self):
        """Simülasyon modu satırı."""
        frame = QFrame()
        frame.setObjectName("simPanel")
        frame.setStyleSheet("""
            QFrame#simPanel {
                background: rgba(5, 20, 40, 200);
                border: 1px solid #0F3A5C;
                border-left: 3px solid #FFD700;
                border-radius: 8px;
            }
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(14)

        icon = QLabel("⬡")
        icon.setStyleSheet("color: #FFD700; font-size: 22px; background: transparent;")

        text_block = QVBoxLayout()
        text_block.setSpacing(2)

        sim_title = QLabel("Simülasyon Modu")
        sim_title.setStyleSheet("""
            color: #FFD700;
            font: 700 12px 'Courier New';
            letter-spacing: 2px;
            background: transparent;
        """)

        self.lbl_sim_desc = QLabel("Yapay sensör verisi üretimi etkin")
        self.lbl_sim_desc.setStyleSheet("""
            color: #5A5A3A;
            font: 500 10px 'Courier New';
            letter-spacing: 1px;
            background: transparent;
        """)

        text_block.addWidget(sim_title)
        text_block.addWidget(self.lbl_sim_desc)

        self.chk_simulation = QCheckBox()
        self.chk_simulation.setChecked(True)
        self.chk_simulation.setStyleSheet("""
            QCheckBox::indicator {
                width: 44px;
                height: 24px;
                border-radius: 12px;
                border: 1px solid #FFD700;
                background: rgba(255, 215, 0, 20);
            }
            QCheckBox::indicator:checked {
                background: rgba(255, 215, 0, 60);
                border: 1px solid #FFD700;
            }
            QCheckBox::indicator:disabled {
                opacity: 0.4;
            }
        """)
        self.chk_simulation.stateChanged.connect(self._on_sim_toggled)

        layout.addWidget(icon)
        layout.addLayout(text_block)
        layout.addStretch()
        layout.addWidget(self.chk_simulation)
        return frame

    def _build_buttons(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        self.btn_connect = QPushButton("▶  BAĞLAN")
        self.btn_connect.setFixedHeight(46)
        self.btn_connect.setStyleSheet(self._btn_style("#00FF99"))

        self.btn_disconnect = QPushButton("■  BAĞLANTIYI KES")
        self.btn_disconnect.setFixedHeight(46)
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.setStyleSheet(self._btn_style("#FF4D4D"))

        self.btn_connect.clicked.connect(self._on_connect)
        self.btn_disconnect.clicked.connect(self._on_disconnect)

        layout.addWidget(self.btn_connect)
        layout.addWidget(self.btn_disconnect)
        return frame

    def _build_footer(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)

        left = QLabel("YER İSTASYONU v3.7  ·  GÖREV BAĞLANTI PROTOKOLÜ")
        left.setStyleSheet("""
            color: #1A3A5A;
            font: 500 9px 'Courier New';
            letter-spacing: 2px;
            background: transparent;
        """)

        self.btn_toggle_record = QPushButton("■ KAYDI DURDUR")
        self.btn_toggle_record.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_record.setStyleSheet("""
            QPushButton {
                color: #FF4D4D;
                font: 600 11px 'Segoe UI';
                background: transparent;
                border: 1px solid #FF4D4D;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: rgba(255, 77, 77, 40);
                color: #FFF;
            }
        """)

        self.btn_download = QPushButton(" ⬇ KAYITLARI İNDİR ")
        self.btn_download.setCursor(Qt.PointingHandCursor)
        self.btn_download.setStyleSheet("""
            QPushButton {
                color: #00B4D8;
                font: 600 11px 'Segoe UI';
                background: transparent;
                border: 1px solid #00B4D8;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: rgba(0, 180, 216, 40);
                color: #FFF;
            }
        """)

        self.lbl_clock = QLabel("--:--:-- UTC")
        self.lbl_clock.setStyleSheet("""
            color: #3A6A8A;
            font: 500 10px 'Courier New';
            letter-spacing: 2px;
            background: transparent;
        """)

        layout.addWidget(left)
        layout.addStretch()
        layout.addWidget(self.btn_toggle_record)
        layout.addSpacing(10)
        layout.addWidget(self.btn_download)
        layout.addSpacing(20)
        layout.addWidget(self.lbl_clock)
        return frame

    # ------------------------------------------------------------------ #
    #  Yardımcı Stil / Widget Üreticiler
    # ------------------------------------------------------------------ #
    def _field_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("""
            color: #4A8AAA;
            font: 600 9px 'Courier New';
            letter-spacing: 2px;
            background: transparent;
        """)
        return lbl

    def _make_combo(self, items):
        cb = QComboBox()
        cb.addItems(items)
        cb.setStyleSheet(self._input_style())
        return cb

    def _input_style(self):
        return """
            QComboBox, QSpinBox {
                background: rgba(0, 10, 25, 220);
                color: #00B4D8;
                border: 1px solid #0F3A5C;
                border-radius: 4px;
                padding: 7px 10px;
                font: 700 13px 'Courier New';
            }
            QComboBox:focus, QSpinBox:focus {
                border: 1px solid #00B4D8;
            }
            QComboBox:disabled, QSpinBox:disabled {
                color: #1A4A6A;
                border: 1px solid #061828;
            }
            QComboBox QAbstractItemView {
                background: #050A14;
                color: #00B4D8;
                selection-background-color: #00B4D8;
                selection-color: #000000;
                border: 1px solid #00B4D8;
                outline: none;
            }
            QComboBox::drop-down { border: none; width: 24px; }
            QComboBox::down-arrow { image: none; }
        """

    def _btn_style(self, color):
        return f"""
            QPushButton {{
                background: transparent;
                color: {color};
                font: 700 13px 'Segoe UI';
                letter-spacing: 3px;
                border: 1px solid {color};
                border-radius: 6px;
            }}
            QPushButton:hover:!disabled {{
                background: rgba(255,255,255, 6);
            }}
            QPushButton:disabled {{
                color: #1A3A2A;
                border: 1px solid #0A2A1A;
            }}
        """

    def _hline(self, color):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {color}; border: none;")
        return line

    # ------------------------------------------------------------------ #
    #  Olay İşleyiciler
    # ------------------------------------------------------------------ #
    def _on_connect(self):
        self.btn_connect.setEnabled(False)
        self.btn_disconnect.setEnabled(True)
        self.cb_port.setEnabled(False)
        self.spin_timeout.setEnabled(False)
        self.chk_simulation.setEnabled(False)
        self.lbl_dot.setStyleSheet("color: #00FF99; font-size: 10px; background: transparent;")
        self.lbl_status.setStyleSheet("color: #00FF99; font: 600 10px 'Courier New'; letter-spacing: 2px; background: transparent;")
        self.lbl_status.setText("ÇEVRİMİÇİ")

    def _on_disconnect(self):
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.cb_port.setEnabled(True)
        self.spin_timeout.setEnabled(True)
        self.chk_simulation.setEnabled(True)
        self.lbl_dot.setStyleSheet("color: #FF4D4D; font-size: 10px; background: transparent;")
        self.lbl_status.setStyleSheet("color: #3A6A8A; font: 600 10px 'Courier New'; letter-spacing: 2px; background: transparent;")
        self.lbl_status.setText("ÇEVRİMDIŞI")

    def _on_sim_toggled(self, state):
        if state == Qt.Checked:
            self.lbl_sim_desc.setText("Yapay sensör verisi üretimi etkin")
        else:
            self.lbl_sim_desc.setText("Gerçek donanım bağlantısı bekleniyor...")

    def _update_clock(self):
        from datetime import datetime
        self.lbl_clock.setText(datetime.utcnow().strftime("%H:%M:%S") + " UTC")


# ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    COLORS = {
        "bg_primary":       "#03080F",
        "bg_secondary":     "#050A14",
        "bg_card":          "#0D1F3C",
        "accent_cyan":      "#00B4D8",
        "accent_green":     "#00FF99",
        "accent_red":       "#FF4D4D",
        "accent_yellow":    "#FFD700",
        "accent_purple":    "#BD00FF",
        "accent_tech_blue": "#00AEEF",
        "text_primary":     "#E8F4FD",
        "text_secondary":   "#7BA3C8",
        "text_dim":         "#3A5A7A",
        "border_glow":      "#1A3A5C",
    }

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SettingsPage(COLORS)
    window.setStyleSheet(f"background: {COLORS['bg_primary']};")
    window.resize(820, 500)
    window.setWindowTitle("Yer Kontrol İstasyonu")
    window.show()
    sys.exit(app.exec_())