import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QFrame, QCheckBox, QScrollArea,
    QTextEdit, QDoubleSpinBox, QProgressBar, QSlider, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, QTime
from ui.styles import COLORS

C = COLORS


class SerialSettingsPage(QWidget):
    def __init__(self, state_bus, go_back_callback=None):
        super().__init__()
        self.state_bus = state_bus
        self.go_back_callback = go_back_callback
        self._advanced_visible = False
        self._hex_mode = True
        self._setup_ui()

    # ── Style helpers ──
    def _lbl(self, t):
        l = QLabel(t)
        l.setStyleSheet(f"color:{C['text_dim']};font:700 12px 'Segoe UI';letter-spacing:2px;")
        return l

    def _combo(self, items, cur, accent=None):
        accent = accent or C['accent_cyan']
        c = QComboBox()
        c.addItems(items)
        c.setCurrentText(cur)
        c.setStyleSheet(f"""
            QComboBox{{background:{C['bg_primary']};color:{accent};font:700 15px 'Segoe UI';
                padding:10px 14px;border:none;border-radius:6px;min-height:24px;}}
            QComboBox:hover{{background:{C['bg_card']};}}
            QComboBox::drop-down{{width:28px;border:none;}}
            QComboBox QAbstractItemView{{background:{C['bg_card']};color:{C['text_primary']};
                selection-background-color:{accent}30;border:none;padding:4px;}}
        """)
        return c

    def _spin(self, lo, hi, val, suffix="", accent=None):
        accent = accent or C['accent_cyan']
        s = QSpinBox()
        s.setRange(lo, hi)
        s.setValue(val)
        s.setSuffix(suffix)
        s.setStyleSheet(f"""
            QSpinBox{{background:{C['bg_primary']};color:{accent};font:700 15px 'Segoe UI';
                padding:10px 14px;border:none;border-radius:6px;min-height:24px;}}
            QSpinBox:hover{{background:{C['bg_card']};}}
            QSpinBox::up-button,QSpinBox::down-button{{width:20px;border:none;background:transparent;}}
        """)
        return s

    def _dspin(self, lo, hi, val, dec=4):
        s = QDoubleSpinBox()
        s.setRange(lo, hi)
        s.setValue(val)
        s.setDecimals(dec)
        s.setStyleSheet(f"""
            QDoubleSpinBox{{background:{C['bg_primary']};color:{C['accent_cyan']};font:700 15px 'Segoe UI';
                padding:10px 14px;border:none;border-radius:6px;min-height:24px;}}
            QDoubleSpinBox:hover{{background:{C['bg_card']};}}
            QDoubleSpinBox::up-button,QDoubleSpinBox::down-button{{width:20px;border:none;background:transparent;}}
        """)
        return s

    def _frame(self, color):
        f = QFrame()
        f.setStyleSheet(f"QFrame{{background:{C['bg_secondary']};border:none;border-radius:10px;}}")
        return f

    def _section_title(self, text, color):
        l = QLabel(f"●  {text}")
        l.setStyleSheet(f"color:{color};font:700 13px 'Segoe UI';letter-spacing:2px;")
        return l

    def _field(self, label_text, widget):
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._lbl(label_text))
        col.addWidget(widget)
        return col

    # ── Main UI ──
    def _setup_ui(self):
        self.setStyleSheet(f"background:{C['bg_primary']};")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;}")
        container = QWidget()
        m = QVBoxLayout(container)
        m.setContentsMargins(32, 24, 32, 16)
        m.setSpacing(20)

        # ── HEADER ──
        hdr = QHBoxLayout()
        hdr.setSpacing(14)
        btn_back = QPushButton("< GERİ")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setStyleSheet(f"""
            QPushButton{{background:transparent;color:{C['accent_cyan']};font:700 12px 'Segoe UI';
                padding:6px 14px;border:1px solid {C['accent_cyan']};border-radius:14px;}}
            QPushButton:hover{{background:{C['accent_cyan']}20;}}
        """)
        if self.go_back_callback:
            btn_back.clicked.connect(self.go_back_callback)
        hdr.addWidget(btn_back)

        tb = QVBoxLayout()
        tb.setSpacing(2)
        t1 = QLabel("YER KONTROL İSTASYONU")
        t1.setStyleSheet(f"color:{C['text_primary']};font:700 22px 'Segoe UI';letter-spacing:1px;")
        t2 = QLabel("GÖREV BAĞLANTISI  /  HABERLEŞME VE SİMÜLASYON MODÜLÜ")
        t2.setStyleSheet(f"color:{C['text_dim']};font:12px 'Segoe UI';letter-spacing:1px;")
        tb.addWidget(t1)
        tb.addWidget(t2)
        hdr.addLayout(tb)
        hdr.addStretch()

        self.status_label = QLabel("●  ÇEVRİMDIŞI")
        self.status_label.setStyleSheet(f"color:{C['accent_red']};font:700 14px 'Segoe UI';letter-spacing:1px;")
        hdr.addWidget(self.status_label)
        m.addLayout(hdr)

        # ═══ DONANIM DURUM PANELI: Heartbeat + RSSI ═══
        hw_frame = self._frame(C['accent_cyan'])
        hw_layout = QHBoxLayout(hw_frame)
        hw_layout.setContentsMargins(24, 14, 24, 14)
        hw_layout.setSpacing(24)

        # Heartbeat göstergesi
        hb_col = QVBoxLayout(); hb_col.setSpacing(4)
        hb_col.addWidget(self._lbl("HEARTBEAT"))
        self.lbl_heartbeat = QLabel("●  BEKLENİYOR")
        self.lbl_heartbeat.setStyleSheet(f"color:{C['text_dim']};font:700 15px 'Segoe UI';")
        hb_col.addWidget(self.lbl_heartbeat)
        hw_layout.addLayout(hb_col, 1)

        # RSSI bar
        rssi_col = QVBoxLayout(); rssi_col.setSpacing(4)
        rssi_col.addWidget(self._lbl("SİNYAL GÜCÜ (RSSI)"))
        rssi_row = QHBoxLayout(); rssi_row.setSpacing(8)
        self.rssi_bar = QProgressBar()
        self.rssi_bar.setRange(0, 100); self.rssi_bar.setValue(0)
        self.rssi_bar.setFixedHeight(14); self.rssi_bar.setTextVisible(False)
        self.rssi_bar.setStyleSheet(f"""
            QProgressBar{{background:{C['bg_primary']};border:none;border-radius:7px;}}
            QProgressBar::chunk{{background:{C['accent_green']};border-radius:7px;}}
        """)
        self.lbl_rssi = QLabel("— dBm")
        self.lbl_rssi.setStyleSheet(f"color:{C['text_secondary']};font:700 13px 'Segoe UI';")
        rssi_row.addWidget(self.rssi_bar, 1); rssi_row.addWidget(self.lbl_rssi)
        rssi_col.addLayout(rssi_row)
        hw_layout.addLayout(rssi_col, 2)

        # Son heartbeat zamanı
        self._last_heartbeat = 0
        self._hb_timer = QTimer(self)
        self._hb_timer.timeout.connect(self._check_heartbeat)
        self._hb_timer.start(1000)

        m.addWidget(hw_frame)

        # ═══ BÖLÜM 1: SERİ BAĞLANTI ═══
        f1 = self._frame(C['accent_cyan'])
        ly1 = QVBoxLayout(f1)
        ly1.setContentsMargins(24, 18, 24, 22)
        ly1.setSpacing(16)
        ly1.addWidget(self._section_title("SERİ BAĞLANTI AYARLARI", C['accent_cyan']))

        # Satır 1: COM + Baud + Parity
        r1a = QHBoxLayout()
        r1a.setSpacing(20)

        # COM Port + Tara butonu
        col_com = QVBoxLayout()
        col_com.setSpacing(6)
        col_com.addWidget(self._lbl("COM PORT SEÇİMİ"))
        com_row = QHBoxLayout()
        com_row.setSpacing(8)
        self.combo_port = self._combo(self._get_ports(), "COM4")
        self.btn_scan = QPushButton("🔄")
        self.btn_scan.setToolTip("Portları Tara")
        self.btn_scan.setCursor(Qt.PointingHandCursor)
        self.btn_scan.setFixedSize(42, 42)
        self.btn_scan.setStyleSheet(f"""
            QPushButton{{background:{C['bg_primary']};color:{C['accent_cyan']};font:18px;
                border:none;border-radius:6px;}}
            QPushButton:hover{{background:{C['bg_card']};}}
        """)
        self.btn_scan.clicked.connect(self._scan_ports)
        com_row.addWidget(self.combo_port, 1)
        com_row.addWidget(self.btn_scan)
        col_com.addLayout(com_row)
        r1a.addLayout(col_com, 1)

        self.combo_baud = self._combo(
            ["1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200"], "9600")
        r1a.addLayout(self._field("BAUD HIZI", self.combo_baud), 1)

        self.combo_parity = self._combo(["8N1", "8E1", "8O1", "7N1", "7E1"], "8N1")
        r1a.addLayout(self._field("VERİ BİTİ / PARİTE", self.combo_parity), 1)

        ly1.addLayout(r1a)

        # Satır 2: Flow Control + Timeout
        r1b = QHBoxLayout()
        r1b.setSpacing(20)

        self.combo_flow = self._combo(["Yok", "RTS/CTS", "XON/XOFF"], "Yok")
        r1b.addLayout(self._field("AKIŞ KONTROLÜ", self.combo_flow), 1)

        self.spin_timeout = self._spin(1, 30, 3, "  sn")
        r1b.addLayout(self._field("ZAMAN AŞIMI", self.spin_timeout), 1)

        r1b.addStretch(1)  # Boşluk — sağ tarafı ferah bırak

        ly1.addLayout(r1b)
        m.addWidget(f1)

        # ═══ BÖLÜM 2: SİMÜLASYON MODU ═══
        f2 = self._frame(C['accent_purple'])
        ly2 = QHBoxLayout(f2)
        ly2.setContentsMargins(24, 16, 24, 16)
        ly2.setSpacing(16)

        sim_icon = QLabel("◯")
        sim_icon.setStyleSheet(f"color:{C['text_secondary']};font:22px 'Segoe UI';")
        ly2.addWidget(sim_icon)

        stb = QVBoxLayout()
        stb.setSpacing(2)
        st1 = QLabel("Simülasyon Modu")
        st1.setStyleSheet(f"color:{C['text_primary']};font:700 16px 'Segoe UI';")
        st2 = QLabel("Yapay sensör verisi üretimi etkin")
        st2.setStyleSheet(f"color:{C['text_dim']};font:13px 'Segoe UI';")
        stb.addWidget(st1)
        stb.addWidget(st2)
        ly2.addLayout(stb)
        ly2.addStretch()

        self.sim_toggle = QCheckBox()
        self.sim_toggle.setStyleSheet(f"""
            QCheckBox{{spacing:0;}}
            QCheckBox::indicator{{width:44px;height:24px;border-radius:12px;
                background:{C['bg_secondary']};border:2px solid {C['border_glow']};}}
            QCheckBox::indicator:checked{{background:{C['accent_green']};border:2px solid {C['accent_green']};}}
        """)
        self.sim_toggle.stateChanged.connect(
            lambda s: self.state_bus.simulation_command.emit("start" if s else "stop"))
        ly2.addWidget(self.sim_toggle)
        m.addWidget(f2)

        # ═══ BÖLÜM 3: TELEMETRİ FİLTRE ═══
        f3 = self._frame("#FF00FF")
        ly3 = QVBoxLayout(f3)
        ly3.setContentsMargins(24, 18, 24, 22)
        ly3.setSpacing(16)
        ly3.addWidget(self._section_title("TELEMETRİ VE FİLTRE AYARLARI", "#FF00FF"))

        r3 = QHBoxLayout()
        r3.setSpacing(20)
        self.spin_hz = self._spin(1, 100, 5, "  Hz")
        r3.addLayout(self._field("VERİ YENİLEME HIZI", self.spin_hz), 1)
        self.spin_alpha = self._spin(1, 100, 96, "  %")
        r3.addLayout(self._field("FİLTRE HASSASİYETİ (ALPHA)", self.spin_alpha), 1)
        self.combo_prec = self._combo(["Düşük", "Normal", "Yüksek"], "Normal", C['text_secondary'])
        r3.addLayout(self._field("VERİ HASSASİYETİ", self.combo_prec), 1)
        ly3.addLayout(r3)
        m.addWidget(f3)

        # ═══ BAĞLAN / KES ═══
        br = QHBoxLayout()
        br.setSpacing(20)

        self.btn_connect = QPushButton("►  BAĞLAN")
        self.btn_connect.setCursor(Qt.PointingHandCursor)
        self.btn_connect.setStyleSheet(f"""
            QPushButton{{background:transparent;color:{C['accent_green']};font:700 15px 'Segoe UI';
                letter-spacing:2px;padding:16px;border:2px solid {C['accent_green']};border-radius:8px;}}
            QPushButton:hover{{background:{C['accent_green']}18;}}
        """)
        self.btn_connect.clicked.connect(self._on_connect)
        br.addWidget(self.btn_connect, 1)

        self.btn_disconnect = QPushButton("■  BAĞLANTIYI KES")
        self.btn_disconnect.setCursor(Qt.PointingHandCursor)
        self.btn_disconnect.setStyleSheet(f"""
            QPushButton{{background:transparent;color:{C['text_secondary']};font:700 15px 'Segoe UI';
                letter-spacing:2px;padding:16px;border:2px solid {C['border_glow']};border-radius:8px;}}
            QPushButton:hover{{color:{C['accent_red']};border-color:{C['accent_red']};background:{C['accent_red']}10;}}
        """)
        self.btn_disconnect.clicked.connect(self._on_disconnect)
        br.addWidget(self.btn_disconnect, 1)
        m.addLayout(br)

        # ═══ KRİTİK KOMUT PANELİ (Uplink) + ZAMAN SENKRONİZASYONU ═══
        f_cmd = self._frame(C['accent_orange'])
        ly_cmd = QVBoxLayout(f_cmd)
        ly_cmd.setContentsMargins(24, 18, 24, 22)
        ly_cmd.setSpacing(14)
        ly_cmd.addWidget(self._section_title("KRİTİK KOMUT PANELİ (UPLINK)", C['accent_orange']))

        cmd_row1 = QHBoxLayout(); cmd_row1.setSpacing(16)

        # Sensör Kalibrasyon komutu
        self.btn_calibrate = QPushButton("🔧  SENSÖR KALİBRASYON")
        self.btn_calibrate.setCursor(Qt.PointingHandCursor)
        self.btn_calibrate.setStyleSheet(f"""
            QPushButton{{background:transparent;color:{C['accent_yellow']};font:700 13px 'Segoe UI';
                padding:12px;border:2px solid {C['accent_yellow']};border-radius:8px;}}
            QPushButton:hover{{background:{C['accent_yellow']}18;}}
        """)
        self.btn_calibrate.clicked.connect(lambda: self._send_command("CALIBRATE"))
        cmd_row1.addWidget(self.btn_calibrate, 1)

        # Ayrılma Testi
        self.btn_sep_test = QPushButton("🚀  AYRILMA TESTİ")
        self.btn_sep_test.setCursor(Qt.PointingHandCursor)
        self.btn_sep_test.setStyleSheet(f"""
            QPushButton{{background:transparent;color:{C['accent_orange']};font:700 13px 'Segoe UI';
                padding:12px;border:2px solid {C['accent_orange']};border-radius:8px;}}
            QPushButton:hover{{background:{C['accent_orange']}18;}}
        """)
        self.btn_sep_test.clicked.connect(lambda: self._send_command("SEP_TEST"))
        cmd_row1.addWidget(self.btn_sep_test, 1)

        # Zaman Eşitle
        self.btn_timesync = QPushButton("⏱  ZAMANI EŞİTLE")
        self.btn_timesync.setCursor(Qt.PointingHandCursor)
        self.btn_timesync.setStyleSheet(f"""
            QPushButton{{background:transparent;color:{C['accent_cyan']};font:700 13px 'Segoe UI';
                padding:12px;border:2px solid {C['accent_cyan']};border-radius:8px;}}
            QPushButton:hover{{background:{C['accent_cyan']}18;}}
        """)
        self.btn_timesync.clicked.connect(self._time_sync)
        cmd_row1.addWidget(self.btn_timesync, 1)

        ly_cmd.addLayout(cmd_row1)

        # Onay slider'ı (yanlışlıkla basmayı önler)
        slider_row = QHBoxLayout(); slider_row.setSpacing(12)
        slider_lbl = QLabel("Komutu göndermek için kaydırın →")
        slider_lbl.setStyleSheet(f"color:{C['text_dim']};font:12px 'Segoe UI';")
        slider_row.addWidget(slider_lbl)
        self.cmd_slider = QSlider(Qt.Horizontal)
        self.cmd_slider.setRange(0, 100); self.cmd_slider.setValue(0)
        self.cmd_slider.setStyleSheet(f"""
            QSlider::groove:horizontal{{background:{C['bg_primary']};height:8px;border-radius:4px;}}
            QSlider::handle:horizontal{{background:{C['accent_orange']};width:24px;margin:-8px 0;border-radius:12px;}}
            QSlider::sub-page:horizontal{{background:{C['accent_orange']}40;border-radius:4px;}}
        """)
        self.cmd_slider.sliderReleased.connect(self._reset_slider)
        slider_row.addWidget(self.cmd_slider, 1)
        self.slider_status = QLabel("KİLİTLİ")
        self.slider_status.setStyleSheet(f"color:{C['accent_red']};font:700 12px 'Segoe UI';")
        slider_row.addWidget(self.slider_status)
        ly_cmd.addLayout(slider_row)

        m.addWidget(f_cmd)

        # ═══ SESLİ UYARI + FAIL-SAFE KAYIT ═══
        f_alert = self._frame(C['accent_red'])
        ly_alert = QHBoxLayout(f_alert)
        ly_alert.setContentsMargins(24, 14, 24, 14)
        ly_alert.setSpacing(24)

        # Sesli uyarı toggle
        alert_col = QVBoxLayout(); alert_col.setSpacing(4)
        alert_col.addWidget(self._lbl("SESLİ UYARI SİSTEMİ"))
        self.chk_audio = QCheckBox("Kritik eşiklerde sesli bildirim")
        self.chk_audio.setChecked(True)
        self.chk_audio.setStyleSheet(f"""
            QCheckBox{{color:{C['text_primary']};font:14px 'Segoe UI';spacing:8px;}}
            QCheckBox::indicator{{width:18px;height:18px;border-radius:4px;
                background:{C['bg_primary']};border:none;}}
            QCheckBox::indicator:checked{{background:{C['accent_red']};}}
        """)
        alert_col.addWidget(self.chk_audio)
        ly_alert.addLayout(alert_col, 1)

        # Fail-Safe kayıt toggle
        fs_col = QVBoxLayout(); fs_col.setSpacing(4)
        fs_col.addWidget(self._lbl("ANLIK KAYIT (FAIL-SAFE)"))
        self.chk_failsafe = QCheckBox("Her paketi anında diske yaz")
        self.chk_failsafe.setChecked(True)
        self.chk_failsafe.setStyleSheet(f"""
            QCheckBox{{color:{C['text_primary']};font:14px 'Segoe UI';spacing:8px;}}
            QCheckBox::indicator{{width:18px;height:18px;border-radius:4px;
                background:{C['bg_primary']};border:none;}}
            QCheckBox::indicator:checked{{background:{C['accent_green']};}}
        """)
        fs_col.addWidget(self.chk_failsafe)
        ly_alert.addLayout(fs_col, 1)

        m.addWidget(f_alert)

        # ═══ GELİŞMİŞ BUTON ═══
        self.btn_advanced = QPushButton("▶  GELİŞMİŞ MÜHENDİSLİK AYARLARI")
        self.btn_advanced.setCursor(Qt.PointingHandCursor)
        self.btn_advanced.setStyleSheet(f"""
            QPushButton{{background:transparent;color:{C['accent_orange']};font:700 12px 'Segoe UI';
                letter-spacing:1px;padding:12px;border:1px dashed {C['accent_orange']};border-radius:8px;}}
            QPushButton:hover{{background:{C['accent_orange']}15;}}
        """)
        self.btn_advanced.clicked.connect(self._toggle_advanced)
        m.addWidget(self.btn_advanced)

        # ═══ GELİŞMİŞ PANEL (gizli) ═══
        self.advanced_widget = QWidget()
        self.advanced_widget.setVisible(False)
        adv = QVBoxLayout(self.advanced_widget)
        adv.setContentsMargins(0, 0, 0, 0)
        adv.setSpacing(16)

        # -- Güvenlik --
        fg = self._frame(C['accent_yellow'])
        lyg = QVBoxLayout(fg)
        lyg.setContentsMargins(24, 18, 24, 22)
        lyg.setSpacing(16)
        lyg.addWidget(self._section_title("PAKET DOĞRULAMA VE GÜVENLİK", C['accent_yellow']))
        rg = QHBoxLayout()
        rg.setSpacing(20)
        self.combo_crc = self._combo(
            ["CRC-8", "CRC-16", "CRC-32", "Checksum", "Yok"], "CRC-16", C['accent_yellow'])
        rg.addLayout(self._field("CRC/CHECKSUM TÜRÜ", self.combo_crc), 1)
        self.lbl_health = QLabel("—")
        self.lbl_health.setStyleSheet(f"""
            color:{C['accent_green']};font:700 18px 'Segoe UI';padding:10px;
            background:{C['bg_primary']};border:none;border-radius:6px;
        """)
        rg.addLayout(self._field("SAĞLIK DURUMU", self.lbl_health), 1)
        self.lbl_loss = QLabel("0 / 0  (0%)")
        self.lbl_loss.setStyleSheet(f"""
            color:{C['accent_orange']};font:700 15px 'Segoe UI';padding:10px;
            background:{C['bg_primary']};border:none;border-radius:6px;
        """)
        rg.addLayout(self._field("PAKET KAYBI (kayıp/toplam)", self.lbl_loss), 1)
        lyg.addLayout(rg)
        adv.addWidget(fg)

        # -- Kalman + Birim --
        fk = self._frame(C['accent_cyan'])
        lyk = QVBoxLayout(fk)
        lyk.setContentsMargins(24, 18, 24, 22)
        lyk.setSpacing(16)
        lyk.addWidget(self._section_title("KALMAN FİLTRESİ VE BİRİM DÖNÜŞÜMÜ", C['accent_cyan']))
        rk = QHBoxLayout()
        rk.setSpacing(20)
        self.spin_q = self._dspin(0.0001, 10.0, 0.01, 4)
        rk.addLayout(self._field("Q (SÜREÇ VARYANS)", self.spin_q), 1)
        self.spin_r = self._dspin(0.0001, 10.0, 0.1, 4)
        rk.addLayout(self._field("R (GÜRÜLTÜ VARYANS)", self.spin_r), 1)
        self.dspin_scale = self._dspin(0.001, 1000.0, 1.0, 3)
        rk.addLayout(self._field("SCALE (ÇARPAN)", self.dspin_scale), 1)
        self.dspin_offset = self._dspin(-1000.0, 1000.0, 0.0, 2)
        rk.addLayout(self._field("OFFSET", self.dspin_offset), 1)
        lyk.addLayout(rk)
        adv.addWidget(fk)

        # -- Kayıt Yönetimi --
        fr = self._frame(C['accent_green'])
        lyr = QVBoxLayout(fr)
        lyr.setContentsMargins(24, 18, 24, 22)
        lyr.setSpacing(16)
        lyr.addWidget(self._section_title("KAYIT VE ARŞİV YÖNETİMİ", C['accent_green']))
        rr = QHBoxLayout()
        # Kayıt Aralığı Seçimi
        self.combo_log_interval = self._combo(["Anlık", "3 sn", "5 sn", "10 sn"], "Anlık", C['accent_green'])
        self.combo_log_interval.currentIndexChanged.connect(self._on_interval_changed)
        rr.addLayout(self._field("KAYIT ARALIĞI", self.combo_log_interval), 1)
        self.chk_autoname = QCheckBox("Otomatik tarih/saat damgalı kayıt")
        self.chk_autoname.setChecked(True)
        self.chk_autoname.setStyleSheet(f"""
            QCheckBox{{color:{C['text_primary']};font:13px 'Segoe UI';spacing:8px;padding:10px;}}
            QCheckBox::indicator{{width:18px;height:18px;border-radius:4px;
                border:1px solid {C['border_glow']};background:{C['bg_primary']};}}
            QCheckBox::indicator:checked{{background:{C['accent_green']};border-color:{C['accent_green']};}}
        """)
        rr.addWidget(self.chk_autoname, 2)
        lyr.addLayout(rr)
        adv.addWidget(fr)

        # -- Ham Veri Monitörü --
        fm = self._frame(C['text_secondary'])
        lym = QVBoxLayout(fm)
        lym.setContentsMargins(24, 18, 24, 18)
        lym.setSpacing(10)
        hdr_m = QHBoxLayout()
        hdr_m.addWidget(self._section_title("HAM VERİ MONİTÖRÜ", C['text_secondary']))
        hdr_m.addStretch()
        self.btn_hex = QPushButton("HEX")
        self.btn_ascii = QPushButton("ASCII")
        for b, active in [(self.btn_hex, True), (self.btn_ascii, False)]:
            b.setCursor(Qt.PointingHandCursor)
            b.setCheckable(True)
            b.setChecked(active)
            ac = C['accent_cyan']
            b.setStyleSheet(f"""
                QPushButton{{background:{'%s30'%ac if active else 'transparent'};
                    color:{ac if active else C['text_dim']};font:700 10px 'Segoe UI';
                    padding:5px 14px;border:1px solid {ac if active else C['border_glow']};border-radius:4px;}}
                QPushButton:hover{{border-color:{ac};}}
            """)
            hdr_m.addWidget(b)
        self.btn_hex.clicked.connect(lambda: self._set_monitor_mode(True))
        self.btn_ascii.clicked.connect(lambda: self._set_monitor_mode(False))
        lym.addLayout(hdr_m)

        self.raw_monitor = QTextEdit()
        self.raw_monitor.setReadOnly(True)
        self.raw_monitor.setFixedHeight(140)
        self.raw_monitor.setStyleSheet(f"""
            QTextEdit{{background:{C['bg_primary']};color:{C['accent_green']};font:12px 'Consolas';
                border:1px solid {C['border_glow']};border-radius:6px;padding:10px;}}
        """)
        self.raw_monitor.setPlaceholderText("Bağlantı kurulduğunda ham veri burada görünecektir...")
        lym.addWidget(self.raw_monitor)
        adv.addWidget(fm)

        m.addWidget(self.advanced_widget)

        # ═══ FOOTER ═══
        m.addStretch()
        foot = QHBoxLayout()
        foot.setSpacing(12)
        ver = QLabel("YER İSTASYONU v3.7  -  GÖREV BAĞLANTI PROTOKOLÜ")
        ver.setStyleSheet(f"color:{C['text_dim']};font:10px 'Segoe UI';letter-spacing:1px;")
        foot.addWidget(ver)
        foot.addStretch()

        for txt, clr in [("■ KAYDI DURDUR", C['accent_red']), ("■ KAYITLARI İNDİR", C['accent_cyan'])]:
            b = QPushButton(txt)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton{{background:transparent;color:{clr};font:700 10px 'Segoe UI';
                    padding:5px 14px;border:1px solid {clr};border-radius:4px;}}
                QPushButton:hover{{background:{clr}20;}}
            """)
            if "İNDİR" in txt:
                b.clicked.connect(self._manual_download)
            foot.addWidget(b)

        self.time_label = QLabel("00:00:00 UTC")
        self.time_label.setStyleSheet(f"color:{C['text_secondary']};font:11px 'Segoe UI';letter-spacing:1px;")
        foot.addWidget(self.time_label)
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._tick)
        self._clock.start(1000)
        self._tick()
        m.addLayout(foot)

        scroll.setWidget(container)
        outer.addWidget(scroll)

    # ── Callbacks ──
    def _get_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return ports if ports else ["COM1", "COM2", "COM3", "COM4"]

    def _scan_ports(self):
        ports = serial.tools.list_ports.comports()
        self.combo_port.clear()
        for p in ports:
            self.combo_port.addItem(f"{p.device} - {p.description}")
        if not ports:
            self.combo_port.addItems(["Port bulunamadı"])

    def _toggle_advanced(self):
        self._advanced_visible = not self._advanced_visible
        self.advanced_widget.setVisible(self._advanced_visible)
        arrow = "▼" if self._advanced_visible else "▶"
        self.btn_advanced.setText(f"{arrow}  GELİŞMİŞ MÜHENDİSLİK AYARLARI")

    def _set_monitor_mode(self, hex_mode):
        self._hex_mode = hex_mode
        self.btn_hex.setChecked(hex_mode)
        self.btn_ascii.setChecked(not hex_mode)
        ac, dm, td = C['accent_cyan'], C['border_glow'], C['text_dim']
        for b, on in [(self.btn_hex, hex_mode), (self.btn_ascii, not hex_mode)]:
            b.setStyleSheet(f"""
                QPushButton{{background:{ac+'30' if on else 'transparent'};
                    color:{ac if on else td};font:700 10px 'Segoe UI';
                    padding:5px 14px;border:1px solid {ac if on else dm};border-radius:4px;}}
                QPushButton:hover{{border-color:{ac};}}
            """)

    def _tick(self):
        self.time_label.setText(QTime.currentTime().toString("HH:mm:ss") + " UTC")

    def _on_connect(self):
        self.status_label.setText("●  ÇEVRİMİÇİ")
        self.status_label.setStyleSheet(
            f"color:{C['accent_green']};font:700 14px 'Segoe UI';letter-spacing:1px;")

    def _on_disconnect(self):
        self.status_label.setText("●  ÇEVRİMDIŞI")
        self.status_label.setStyleSheet(
            f"color:{C['accent_red']};font:700 14px 'Segoe UI';letter-spacing:1px;")

    # ── Kayıt ve Zamanlama ──
    def _on_interval_changed(self):
        text = self.combo_log_interval.currentText()
        if text == "Anlık":
            interval = 0
        else:
            # "3 sn" -> 3.0
            interval = float(text.split(" ")[0])
        self.state_bus.log_interval_changed.emit(interval)

    def _manual_download(self):
        """Mevcut log dosyasını kullanıcının seçtiği bir yere kopyalar."""
        # Not: Logger'ın yoluna MainWindow üzerinden veya global bir yapıdan erişmek daha iyi olabilir.
        # Şimdilik data/flights klasöründeki en güncel dosyayı önerelim.
        import shutil
        import os

        log_dir = "data/flights"
        files = [f for f in os.listdir(log_dir) if f.endswith(".csv")]
        if not files:
            QMessageBox.warning(self, "Hata", "İndirilecek kayıt bulunamadı.")
            return

        # En yeni dosyayı bul
        files.sort(key=lambda x: os.path.getmtime(os.path.join(log_dir, x)), reverse=True)
        latest_file = os.path.join(log_dir, files[0])

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Kaydı Farklı Kaydet", 
            os.path.expanduser(f"~/Desktop/{files[0]}"), 
            "CSV Files (*.csv)"
        )

        if save_path:
            try:
                shutil.copy2(latest_file, save_path)
                QMessageBox.information(self, "Başarılı", f"Kayıt şuraya indirildi:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya kopyalanamadı: {str(e)}")

    # ── Heartbeat ──
    def _check_heartbeat(self):
        import time
        elapsed = time.time() - self._last_heartbeat
        if self._last_heartbeat == 0:
            self.lbl_heartbeat.setText("●  BEKLENİYOR")
            self.lbl_heartbeat.setStyleSheet(f"color:{C['text_dim']};font:700 15px 'Segoe UI';")
        elif elapsed > 3:
            self.lbl_heartbeat.setText("●  BAĞLANTI KESİLDİ")
            self.lbl_heartbeat.setStyleSheet(f"color:{C['accent_red']};font:700 15px 'Segoe UI';")
            if self.chk_audio.isChecked():
                from PyQt5.QtWidgets import QApplication
                QApplication.beep()
        else:
            self.lbl_heartbeat.setText("●  HAYATTA")
            self.lbl_heartbeat.setStyleSheet(f"color:{C['accent_green']};font:700 15px 'Segoe UI';")

    def receive_heartbeat(self):
        """Dışarıdan heartbeat sinyali geldiğinde çağrılır."""
        import time
        self._last_heartbeat = time.time()

    def update_rssi(self, dbm):
        """RSSI değerini günceller. dbm: -120 ile 0 arası."""
        pct = max(0, min(100, int((dbm + 120) / 120 * 100)))
        self.rssi_bar.setValue(pct)
        self.lbl_rssi.setText(f"{dbm} dBm")
        if pct > 60:
            color = C['accent_green']
        elif pct > 30:
            color = C['accent_yellow']
        else:
            color = C['accent_red']
        self.rssi_bar.setStyleSheet(f"""
            QProgressBar{{background:{C['bg_primary']};border:none;border-radius:7px;}}
            QProgressBar::chunk{{background:{color};border-radius:7px;}}
        """)

    # ── Komut Paneli ──
    def _send_command(self, cmd):
        if self.cmd_slider.value() < 90:
            self.slider_status.setText("KİLİTLİ")
            self.slider_status.setStyleSheet(f"color:{C['accent_red']};font:700 12px 'Segoe UI';")
            return
        reply = QMessageBox.question(
            self, "Komut Onayı",
            f"{cmd} komutu gönderilecek. Emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.slider_status.setText("GÖNDERİLDİ ✓")
            self.slider_status.setStyleSheet(f"color:{C['accent_green']};font:700 12px 'Segoe UI';")
            # TODO: Gerçek seri port üzerinden komutu gönder
        self.cmd_slider.setValue(0)

    def _reset_slider(self):
        val = self.cmd_slider.value()
        if val >= 90:
            self.slider_status.setText("HAZIR")
            self.slider_status.setStyleSheet(f"color:{C['accent_green']};font:700 12px 'Segoe UI';")
        else:
            self.cmd_slider.setValue(0)
            self.slider_status.setText("KİLİTLİ")
            self.slider_status.setStyleSheet(f"color:{C['accent_red']};font:700 12px 'Segoe UI';")

    def _time_sync(self):
        """PC saatini rokete gönderir."""
        import datetime
        now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        self.slider_status.setText(f"SYNC: {now}")
        self.slider_status.setStyleSheet(f"color:{C['accent_cyan']};font:700 12px 'Segoe UI';")
        # TODO: Gerçek seri port üzerinden zaman senkronizasyonu gönder

    # ── Ham Veri ──
    def append_raw(self, data_bytes):
        if self._hex_mode:
            text = " ".join(f"{b:02X}" for b in data_bytes)
        else:
            text = data_bytes.decode("ascii", errors="replace")
        self.raw_monitor.append(text)

    def update_health(self, valid, total, lost):
        pct = (lost / total * 100) if total > 0 else 0
        self.lbl_loss.setText(f"{lost} / {total}  ({pct:.1f}%)")
        if pct > 10:
            self.lbl_health.setText("⚠ KÖTÜ")
            self.lbl_health.setStyleSheet(
                f"color:{C['accent_red']};font:700 18px 'Segoe UI';padding:10px;"
                f"background:{C['bg_primary']};border:none;border-radius:6px;")
        elif pct > 3:
            self.lbl_health.setText("● ORTA")
            self.lbl_health.setStyleSheet(
                f"color:{C['accent_orange']};font:700 18px 'Segoe UI';padding:10px;"
                f"background:{C['bg_primary']};border:none;border-radius:6px;")
        else:
            self.lbl_health.setText("● İYİ")
            self.lbl_health.setStyleSheet(
                f"color:{C['accent_green']};font:700 18px 'Segoe UI';padding:10px;"
                f"background:{C['bg_primary']};border:none;border-radius:6px;")
