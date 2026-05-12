from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar, QApplication
from PyQt5.QtCore import Qt, QTimer
import time
from ui.styles import COLORS

C = COLORS

class StatusCard(QFrame):
    """1. Donanım Durum İzleme (Heartbeat & RSSI)"""
    def __init__(self, get_audio_enabled_callback):
        super().__init__()
        self.get_audio_enabled = get_audio_enabled_callback
        self._last_heartbeat = 0
        self._setup_ui()
        
        # Heartbeat Kontrol Sayacı (1 saniyede bir kontrol)
        self._hb_timer = QTimer(self)
        self._hb_timer.timeout.connect(self._check_heartbeat)
        self._hb_timer.start(1000)

    def _setup_ui(self):
        self.setStyleSheet(f"QFrame{{background:{C['bg_secondary']}; border:none; border-radius:10px;}}")
        layout = QHBoxLayout(self); layout.setContentsMargins(24, 14, 24, 14); layout.setSpacing(24)

        # Heartbeat (Bağlantı Sağlığı)
        hb_col = QVBoxLayout(); hb_col.setSpacing(4)
        lbl_hb_title = QLabel("BAĞLANTI SAĞLIĞI (HEARTBEAT)")
        lbl_hb_title.setStyleSheet(f"color:{C['text_dim']}; font:700 11px 'Segoe UI'; letter-spacing:2px;")
        hb_col.addWidget(lbl_hb_title)
        
        self.lbl_heartbeat = QLabel("●  BEKLENİYOR")
        self.lbl_heartbeat.setStyleSheet(f"color:{C['text_dim']}; font:700 15px 'Segoe UI';")
        hb_col.addWidget(self.lbl_heartbeat)
        layout.addLayout(hb_col, 1)

        # RSSI (Sinyal Gücü)
        rssi_col = QVBoxLayout(); rssi_col.setSpacing(4)
        lbl_rssi_title = QLabel("SİNYAL GÜCÜ (RSSI)")
        lbl_rssi_title.setStyleSheet(f"color:{C['text_dim']}; font:700 11px 'Segoe UI'; letter-spacing:2px;")
        rssi_col.addWidget(lbl_rssi_title)
        
        rssi_row = QHBoxLayout(); rssi_row.setSpacing(8)
        self.rssi_bar = QProgressBar()
        self.rssi_bar.setRange(0, 100); self.rssi_bar.setValue(0); self.rssi_bar.setFixedHeight(12); self.rssi_bar.setTextVisible(False)
        self.rssi_bar.setStyleSheet(f"QProgressBar{{background:{C['bg_primary']}; border:none; border-radius:6px;}} QProgressBar::chunk{{background:{C['accent_green']}; border-radius:6px;}}")
        
        self.lbl_rssi = QLabel("— dBm")
        self.lbl_rssi.setStyleSheet(f"color:{C['text_secondary']}; font:700 13px 'Segoe UI';")
        rssi_row.addWidget(self.rssi_bar, 1); rssi_row.addWidget(self.lbl_rssi)
        rssi_col.addLayout(rssi_row)
        layout.addLayout(rssi_col, 2)

    def receive_heartbeat(self):
        """Roketten veri geldiğinde bu metod çağrılır."""
        self._last_heartbeat = time.time()

    def _check_heartbeat(self):
        """Heartbeat sinyalini saniyede bir kontrol eder."""
        elapsed = time.time() - self._last_heartbeat
        if self._last_heartbeat == 0:
            self.lbl_heartbeat.setText("●  BEKLENİYOR")
            self.lbl_heartbeat.setStyleSheet(f"color:{C['text_dim']}; font:700 15px 'Segoe UI';")
        elif elapsed > 2: # 2 saniye veri gelmezse bağlantı kesilmiş sayılır
            self.lbl_heartbeat.setText("●  BAĞLANTI KESİLDİ")
            self.lbl_heartbeat.setStyleSheet(f"color:{C['accent_red']}; font:700 15px 'Segoe UI';")
            # Sesli uyarı aktifse bip sesi ver
            if self.get_audio_enabled(): QApplication.beep()
        else:
            self.lbl_heartbeat.setText("●  HAYATTA")
            self.lbl_heartbeat.setStyleSheet(f"color:{C['accent_green']}; font:700 15px 'Segoe UI';")

    def update_rssi(self, dbm):
        """RSSI değerini (dBm) bar üzerinde gösterir."""
        # -120 dBm (0%) ile 0 dBm (100%) arası eşleme
        pct = max(0, min(100, int((dbm + 120) / 120 * 100)))
        self.rssi_bar.setValue(pct); self.lbl_rssi.setText(f"{dbm} dBm")
        color = C['accent_green'] if pct > 60 else (C['accent_yellow'] if pct > 30 else C['accent_red'])
        self.rssi_bar.setStyleSheet(f"QProgressBar{{background:{C['bg_primary']}; border:none; border-radius:6px;}} QProgressBar::chunk{{background:{color}; border-radius:6px;}}")
