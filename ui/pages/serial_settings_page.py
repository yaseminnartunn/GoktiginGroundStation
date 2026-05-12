import sys, os, shutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, QTime
from ui.styles import COLORS

# Modüler parçalar
from ui.widgets.serial.status_card import StatusCard
from ui.widgets.serial.config_card import ConfigCard
from ui.widgets.serial.command_card import CommandCard
from ui.widgets.serial.advanced_card import AdvancedCard

C = COLORS

class SerialSettingsPage(QWidget):
    def __init__(self, state_bus, go_back_callback):
        super().__init__()
        self.state_bus = state_bus
        self.go_back_callback = go_back_callback
        self._advanced_visible = False
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"background:{C['bg_primary']};")
        outer = QVBoxLayout(self); outer.setContentsMargins(40, 40, 40, 40); outer.setSpacing(30)

        # Header
        hdr = QHBoxLayout()
        self.btn_back = QPushButton("←")
        self.btn_back.setCursor(Qt.PointingHandCursor); self.btn_back.setFixedSize(45, 45)
        self.btn_back.setStyleSheet(f"QPushButton{{background:{C['bg_secondary']}; color:{C['accent_cyan']}; font:20px; border:none; border-radius:10px;}} QPushButton:hover{{background:{C['bg_card']};}}")
        self.btn_back.clicked.connect(self.go_back_callback)
        hdr.addWidget(self.btn_back)
        tb = QVBoxLayout(); tb.setSpacing(2)
        t1 = QLabel("YER KONTROL İSTASYONU"); t1.setStyleSheet(f"color:{C['text_primary']}; font:700 22px 'Segoe UI'; letter-spacing:1px;")
        t2 = QLabel("GÖREV BAĞLANTISI / HABERLEŞME MODÜLÜ"); t2.setStyleSheet(f"color:{C['text_dim']}; font:12px 'Segoe UI'; letter-spacing:1px;")
        tb.addWidget(t1); tb.addWidget(t2); hdr.addLayout(tb); hdr.addStretch()
        self.status_label = QLabel("● ÇEVRİMDIŞI"); self.status_label.setStyleSheet(f"color:{C['accent_red']}; font:700 14px 'Segoe UI';")
        hdr.addWidget(self.status_label); outer.addLayout(hdr)

        # Scroll İçerik
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("QScrollArea{border:none; background:transparent;}")
        container = QWidget(); m = QVBoxLayout(container); m.setSpacing(20); m.setContentsMargins(0, 0, 10, 0)

        self.status_card = StatusCard(lambda: self.advanced_card.chk_audio.isChecked()); m.addWidget(self.status_card)
        self.config_card = ConfigCard(self.state_bus); m.addWidget(self.config_card)

        # Bağlan / Kes
        br = QHBoxLayout(); br.setSpacing(20)
        self.btn_connect = QPushButton("► BAĞLAN"); self.btn_connect.setCursor(Qt.PointingHandCursor); self.btn_connect.setStyleSheet(self._btn_style(C['accent_green']))
        self.btn_connect.clicked.connect(self._on_connect)
        self.btn_disconnect = QPushButton("■ BAĞLANTIYI KES"); self.btn_disconnect.setCursor(Qt.PointingHandCursor); self.btn_disconnect.setStyleSheet(self._btn_style(C['text_secondary'], True))
        self.btn_disconnect.clicked.connect(self._on_disconnect)
        br.addWidget(self.btn_connect, 1); br.addWidget(self.btn_disconnect, 1); m.addLayout(br)

        self.command_card = CommandCard(self.state_bus); m.addWidget(self.command_card)

        self.btn_adv_toggle = QPushButton("▶ GELİŞMİŞ MÜHENDİSLİK AYARLARI"); self.btn_adv_toggle.setCursor(Qt.PointingHandCursor); self.btn_adv_toggle.setStyleSheet(f"QPushButton{{background:transparent; color:{C['accent_orange']}; font:700 12px 'Segoe UI'; border:1px dashed {C['accent_orange']}; border-radius:8px; padding:12px;}} QPushButton:hover{{background:{C['accent_orange']}15;}}")
        self.btn_adv_toggle.clicked.connect(self._toggle_adv); m.addWidget(self.btn_adv_toggle)

        self.advanced_card = AdvancedCard(self.state_bus); self.advanced_card.setVisible(False); m.addWidget(self.advanced_card)
        m.addStretch()

        # Footer
        foot = QHBoxLayout(); foot.setContentsMargins(10, 20, 10, 0)
        ver = QLabel("v2.5.0-MODULAR"); ver.setStyleSheet(f"color:{C['text_dim']}; font:10px 'Consolas';"); foot.addWidget(ver); foot.addStretch()
        for txt, clr in [("■ KAYDI DURDUR", C['accent_red']), ("■ KAYITLARI İNDİR", C['accent_cyan'])]:
            b = QPushButton(txt); b.setCursor(Qt.PointingHandCursor); b.setStyleSheet(f"QPushButton{{background:transparent; color:{clr}; font:700 10px 'Segoe UI'; border:1px solid {clr}; border-radius:4px; padding:5px 14px;}}")
            if "İNDİR" in txt: b.clicked.connect(self._manual_download)
            foot.addWidget(b)
        self.time_lbl = QLabel("00:00:00 UTC"); self.time_lbl.setStyleSheet(f"color:{C['text_secondary']}; font:11px 'Segoe UI';"); foot.addWidget(self.time_lbl)
        self._tmr = QTimer(self); self._tmr.timeout.connect(self._tick); self._tmr.start(1000); self._tick()
        m.addLayout(foot); scroll.setWidget(container); outer.addWidget(scroll)

    def _btn_style(self, clr, danger=False):
        h = C['accent_red'] if danger else clr
        return f"QPushButton{{background:transparent; color:{C['text_secondary'] if danger else clr}; font:700 15px 'Segoe UI'; padding:16px; border:2px solid {C['border_glow'] if danger else clr}; border-radius:8px;}} QPushButton:hover{{color:{h}; border-color:{h}; background:{h}10;}}"

    def _toggle_adv(self):
        self._advanced_visible = not self._advanced_visible; self.advanced_card.setVisible(self._advanced_visible)
        self.btn_adv_toggle.setText(f"{'▼' if self._advanced_visible else '▶'} GELİŞMİŞ MÜHENDİSLİK AYARLARI")

    def _tick(self): self.time_lbl.setText(QTime.currentTime().toString("HH:mm:ss") + " UTC")

    def _on_connect(self): self.status_label.setText("● ÇEVRİMİÇİ"); self.status_label.setStyleSheet(f"color:{C['accent_green']}; font:700 14px 'Segoe UI';")
    def _on_disconnect(self): self.status_label.setText("● ÇEVRİMDIŞI"); self.status_label.setStyleSheet(f"color:{C['accent_red']}; font:700 14px 'Segoe UI';")

    def _manual_download(self):
        d = "data/flights"; fs = [f for f in os.listdir(d) if f.endswith(".csv")] if os.path.exists(d) else []
        if not fs: QMessageBox.warning(self, "Hata", "Kayıt bulunamadı."); return
        fs.sort(key=lambda x: os.path.getmtime(os.path.join(d, x)), reverse=True); lat = os.path.join(d, fs[0])
        p, _ = QFileDialog.getSaveFileName(self, "Kaydı İndir", os.path.expanduser(f"~/Desktop/{fs[0]}"), "CSV (*.csv)")
        if p:
            try: shutil.copy2(lat, p); QMessageBox.information(self, "Başarılı", f"Kayıt indirildi:\n{p}")
            except Exception as e: QMessageBox.critical(self, "Hata", str(e))

    # Proxy
    def receive_heartbeat(self): self.status_card.receive_heartbeat()
    def update_rssi(self, dbm): self.status_card.update_rssi(dbm)
    def append_raw(self, b): self.advanced_card.append_raw(b)
    def update_health(self, v, t, l): self.advanced_card.update_health(v, t, l)
