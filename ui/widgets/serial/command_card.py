from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QFrame, QMessageBox
from PyQt5.QtCore import Qt
import datetime
from ui.styles import COLORS

C = COLORS

class CommandCard(QFrame):
    def __init__(self, state_bus):
        super().__init__()
        self.state_bus = state_bus
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"QFrame{{background:{C['bg_secondary']}; border:none; border-radius:10px;}}")
        layout = QVBoxLayout(self); layout.setContentsMargins(24, 18, 24, 22); layout.setSpacing(14)
        lbl_title = QLabel("●  KRİTİK KOMUT PANELİ (UPLINK)")
        lbl_title.setStyleSheet(f"color:{C['accent_orange']}; font:700 13px 'Segoe UI'; letter-spacing:2px;")
        layout.addWidget(lbl_title)
        cmd_row = QHBoxLayout(); cmd_row.setSpacing(16)
        btn_style = "QPushButton{{background:transparent; color:{clr}; font:700 13px 'Segoe UI'; padding:12px; border:2px solid {clr}; border-radius:8px;}} QPushButton:hover{{background:{clr}18;}}"
        self.btn_calibrate = QPushButton("🔧  SENSÖR KALİBRASYON"); self.btn_calibrate.setStyleSheet(btn_style.format(clr=C['accent_yellow']))
        self.btn_calibrate.clicked.connect(lambda: self._send_command("CALIBRATE"))
        cmd_row.addWidget(self.btn_calibrate, 1)
        self.btn_sep_test = QPushButton("🚀  AYRILMA TESTİ"); self.btn_sep_test.setStyleSheet(btn_style.format(clr=C['accent_orange']))
        self.btn_sep_test.clicked.connect(lambda: self._send_command("SEP_TEST"))
        cmd_row.addWidget(self.btn_sep_test, 1)
        self.btn_timesync = QPushButton("⏱  ZAMANI EŞİTLE"); self.btn_timesync.setStyleSheet(btn_style.format(clr=C['accent_cyan']))
        self.btn_timesync.clicked.connect(self._time_sync)
        cmd_row.addWidget(self.btn_timesync, 1); layout.addLayout(cmd_row)
        slider_row = QHBoxLayout(); slider_row.setSpacing(12)
        slider_lbl = QLabel("Komutu göndermek için kaydırın →"); slider_lbl.setStyleSheet(f"color:{C['text_dim']}; font:12px 'Segoe UI';"); slider_row.addWidget(slider_lbl)
        self.cmd_slider = QSlider(Qt.Horizontal); self.cmd_slider.setRange(0, 100); self.cmd_slider.setValue(0)
        self.cmd_slider.setStyleSheet(f"QSlider::groove:horizontal{{background:{C['bg_primary']}; height:8px; border-radius:4px;}} QSlider::handle:horizontal{{background:{C['accent_orange']}; width:24px; margin:-8px 0; border-radius:12px;}} QSlider::sub-page:horizontal{{background:{C['accent_orange']}40; border-radius:4px;}}")
        self.cmd_slider.sliderReleased.connect(self._reset_slider); slider_row.addWidget(self.cmd_slider, 1)
        self.slider_status = QLabel("KİLİTLİ"); self.slider_status.setStyleSheet(f"color:{C['accent_red']}; font:700 12px 'Segoe UI';"); slider_row.addWidget(self.slider_status); layout.addLayout(slider_row)

    def _send_command(self, cmd):
        if self.cmd_slider.value() < 90:
            self.slider_status.setText("KİLİTLİ"); self.slider_status.setStyleSheet(f"color:{C['accent_red']}; font:700 12px 'Segoe UI';")
            return
        reply = QMessageBox.question(self, "Komut Onayı", f"{cmd} komutu gönderilecek. Emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.slider_status.setText("GÖNDERİLDİ ✓"); self.slider_status.setStyleSheet(f"color:{C['accent_green']}; font:700 12px 'Segoe UI';")
        self.cmd_slider.setValue(0)

    def _reset_slider(self):
        if self.cmd_slider.value() >= 90:
            self.slider_status.setText("HAZIR"); self.slider_status.setStyleSheet(f"color:{C['accent_green']}; font:700 12px 'Segoe UI';")
        else: self.cmd_slider.setValue(0); self.slider_status.setText("KİLİTLİ"); self.slider_status.setStyleSheet(f"color:{C['accent_red']}; font:700 12px 'Segoe UI';")

    def _time_sync(self):
        now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        self.slider_status.setText(f"SYNC: {now}"); self.slider_status.setStyleSheet(f"color:{C['accent_cyan']}; font:700 12px 'Segoe UI';")
