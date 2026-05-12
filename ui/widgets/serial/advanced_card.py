from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox, QFrame, QCheckBox, QPushButton, QTextEdit, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
import os, shutil
from ui.styles import COLORS

C = COLORS

class AdvancedCard(QWidget):
    """Güvenlik, Kayıt ve Mühendislik Terminali (Grup 2, 4 & 5)"""
    def __init__(self, state_bus):
        super().__init__()
        self.state_bus = state_bus
        self._hex_mode = True
        self._setup_ui()

    def _lbl(self, t):
        l = QLabel(t); l.setStyleSheet(f"color:{C['text_dim']}; font:700 11px 'Segoe UI'; letter-spacing:2px;")
        return l

    def _combo(self, items, cur, accent=None):
        accent = accent or C['accent_cyan']
        c = QComboBox(); c.addItems(items); c.setCurrentText(cur)
        c.setStyleSheet(f"QComboBox{{background:{C['bg_primary']}; color:{accent}; font:700 14px 'Segoe UI'; padding:10px; border:none; border-radius:6px;}} QComboBox:hover{{background:{C['bg_card']};}}")
        return c

    def _section_title(self, text, color):
        l = QLabel(f"●  {text}"); l.setStyleSheet(f"color:{color}; font:700 12px 'Segoe UI'; letter-spacing:2px;")
        return l

    def _setup_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(15)

        # 2. GÜVENLİK GRUBU (Telemetri Doğrulama)
        fg = QFrame(); fg.setStyleSheet(f"background:{C['bg_secondary']}; border-radius:10px;")
        lyg = QVBoxLayout(fg); lyg.setContentsMargins(20, 15, 20, 20); lyg.setSpacing(12)
        lyg.addWidget(self._section_title("2. TELEMETRİ VERİ PAKETİ DOĞRULAMA (GÜVENLİK)", C['accent_yellow']))
        rg = QHBoxLayout(); rg.setSpacing(15)
        
        c_crc = QVBoxLayout(); c_crc.addWidget(self._lbl("CHECKSUM/CRC TÜRÜ")); self.combo_crc = self._combo(["CRC-16", "CRC-32", "Checksum", "Yok"], "CRC-16", C['accent_yellow']); c_crc.addWidget(self.combo_crc); rg.addLayout(c_crc, 1)
        
        c_h = QVBoxLayout(); c_h.addWidget(self._lbl("HEALTH CHECK (SAĞLIK)")); self.lbl_health = QLabel("● BEKLENİYOR"); self.lbl_health.setStyleSheet(f"color:{C['accent_green']}; font:700 16px 'Segoe UI'; padding:10px; background:{C['bg_primary']}; border-radius:6px;"); c_h.addWidget(self.lbl_health); rg.addLayout(c_h, 1)
        
        c_l = QVBoxLayout(); c_l.addWidget(self._lbl("PACKET LOSS COUNTER")); self.lbl_loss = QLabel("0 / 0 (0%)"); self.lbl_loss.setStyleSheet(f"color:{C['accent_orange']}; font:700 14px 'Segoe UI'; padding:10px; background:{C['bg_primary']}; border-radius:6px;"); c_l.addWidget(self.lbl_loss); rg.addLayout(c_l, 1)
        lyg.addLayout(rg); layout.addWidget(fg)

        # 4. VERİ GRUBU (Kayıt ve Arşiv)
        fr = QFrame(); fr.setStyleSheet(f"background:{C['bg_secondary']}; border-radius:10px;")
        lyr = QVBoxLayout(fr); lyr.setContentsMargins(20, 15, 20, 20); lyr.setSpacing(12)
        lyr.addWidget(self._section_title("4. KAYIT VE ARŞİV YÖNETİMİ (VERİ)", C['accent_green']))
        rr = QHBoxLayout(); rr.setSpacing(15)
        
        c_i = QVBoxLayout(); c_i.addWidget(self._lbl("LOG SAMPLING RATE (ARALIK)")); self.combo_log_interval = self._combo(["Anlık", "3 sn", "5 sn", "10 sn"], "Anlık", C['accent_green']); self.combo_log_interval.currentIndexChanged.connect(self._on_interval_changed); c_i.addWidget(self.combo_log_interval); rr.addLayout(c_i, 1)
        
        self.chk_autoname = QCheckBox("OTOMATİK DOSYA İSİMLENDİRME (TARİH/SAAT)"); self.chk_autoname.setChecked(True); self.chk_autoname.setStyleSheet(f"QCheckBox{{color:{C['text_primary']}; font:12px 'Segoe UI'; padding:10px;}} QCheckBox::indicator{{width:16px; height:16px; border:1px solid {C['border_glow']}; background:{C['bg_primary']};}} QCheckBox::indicator:checked{{background:{C['accent_green']};}}"); rr.addWidget(self.chk_autoname, 2)
        lyr.addLayout(rr); layout.addWidget(fr)

        # 5. MÜHENDİSLİK TERMİNALİ (Hata Ayıklama)
        fm = QFrame(); fm.setStyleSheet(f"background:{C['bg_secondary']}; border-radius:10px;")
        lym = QVBoxLayout(fm); lym.setContentsMargins(20, 15, 20, 15); lym.setSpacing(10)
        h_m = QHBoxLayout(); h_m.addWidget(self._section_title("5. MÜHENDİSLİK TERMİNALİ (RAW MONITOR)", C['text_secondary'])); h_m.addStretch()
        self.btn_hex = QPushButton("HEX"); self.btn_ascii = QPushButton("ASCII")
        for b, on in [(self.btn_hex, True), (self.btn_ascii, False)]:
            b.setCheckable(True); b.setChecked(on); b.setStyleSheet(self._mon_btn_style(on))
        self.btn_hex.clicked.connect(lambda: self._set_mon(True)); self.btn_ascii.clicked.connect(lambda: self._set_mon(False))
        h_m.addWidget(self.btn_hex); h_m.addWidget(self.btn_ascii); lym.addLayout(h_m)
        
        self.raw_monitor = QTextEdit(); self.raw_monitor.setReadOnly(True); self.raw_monitor.setFixedHeight(150); self.raw_monitor.setStyleSheet(f"background:{C['bg_primary']}; color:{C['accent_cyan']}; font:11px 'Consolas'; border:none; padding:10px;"); lym.addWidget(self.raw_monitor); layout.addWidget(fm)

    def _mon_btn_style(self, on):
        ac = C['accent_cyan']
        return f"QPushButton{{background:{ac+'30' if on else 'transparent'}; color:{ac if on else C['text_dim']}; font:700 10px 'Segoe UI'; padding:5px 12px; border:1px solid {ac if on else C['border_glow']}; border-radius:4px;}}"

    def _set_mon(self, h):
        self._hex_mode = h; self.btn_hex.setChecked(h); self.btn_ascii.setChecked(not h); self.btn_hex.setStyleSheet(self._mon_btn_style(h)); self.btn_ascii.setStyleSheet(self._mon_btn_style(not h))

    def _on_interval_changed(self):
        t = self.combo_log_interval.currentText(); v = 0 if t == "Anlık" else float(t.split(" ")[0]); self.state_bus.log_interval_changed.emit(v)

    def append_raw(self, b):
        t = " ".join(f"{x:02X}" for x in b) if self._hex_mode else b.decode("ascii", errors="replace")
        self.raw_monitor.append(t)
        if self.raw_monitor.document().lineCount() > 100: self.raw_monitor.clear()

    def update_health(self, v, t, l):
        p = (l / t * 100) if t > 0 else 0; self.lbl_loss.setText(f"{l} / {t} ({p:.1f}%)")
        color = C['accent_green'] if p < 3 else (C['accent_orange'] if p < 10 else C['accent_red'])
        self.lbl_health.setText("● İYİ" if p < 3 else ("● ORTA" if p < 10 else "⚠ KÖTÜ")); self.lbl_health.setStyleSheet(f"color:{color}; font:700 16px 'Segoe UI'; padding:10px; background:{C['bg_primary']}; border-radius:6px;")
