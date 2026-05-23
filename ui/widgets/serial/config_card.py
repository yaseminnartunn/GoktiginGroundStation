from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox, QFrame, QCheckBox, QPushButton, QDoubleSpinBox
from PyQt5.QtCore import Qt
import serial.tools.list_ports
from ui.styles import COLORS

C = COLORS

class ConfigCard(QWidget):
    """Fiziksel Katman ve Sinyal İşleme Ayarları (Grup 1 & 3)"""
    def __init__(self, state_bus):
        super().__init__()
        self.state_bus = state_bus
        self._setup_ui()

    def _lbl(self, t):
        l = QLabel(t); l.setStyleSheet(f"color:{C['text_dim']}; font:700 11px 'Segoe UI'; letter-spacing:2px;")
        return l

    def _combo(self, items, cur, accent=None):
        accent = accent or C['accent_cyan']
        c = QComboBox(); c.addItems(items); c.setCurrentText(cur)
        c.setStyleSheet(f"QComboBox{{background:{C['bg_primary']}; color:{accent}; font:700 14px 'Segoe UI'; padding:10px; border:none; border-radius:6px;}} QComboBox:hover{{background:{C['bg_card']};}} QComboBox::drop-down{{width:24px; border:none;}}")
        return c

    def _spin(self, lo, hi, val, suffix="", accent=None):
        accent = accent or C['accent_cyan']
        s = QSpinBox(); s.setRange(lo, hi); s.setValue(val); s.setSuffix(suffix)
        s.setStyleSheet(f"QSpinBox{{background:{C['bg_primary']}; color:{accent}; font:700 14px 'Segoe UI'; padding:10px; border:none; border-radius:6px;}} QSpinBox:hover{{background:{C['bg_card']};}}")
        return s

    def _dspin(self, lo, hi, val, dec=4, accent=None):
        accent = accent or C['accent_cyan']
        s = QDoubleSpinBox(); s.setRange(lo, hi); s.setValue(val); s.setDecimals(dec)
        s.setStyleSheet(f"QDoubleSpinBox{{background:{C['bg_primary']}; color:{accent}; font:700 14px 'Segoe UI'; padding:10px; border:none; border-radius:6px;}} QDoubleSpinBox:hover{{background:{C['bg_card']};}}")
        return s

    def _section_title(self, text, color):
        l = QLabel(f"●  {text}"); l.setStyleSheet(f"color:{color}; font:700 12px 'Segoe UI'; letter-spacing:2px;")
        return l

    def _field(self, label, widget):
        col = QVBoxLayout(); col.setSpacing(6); col.addWidget(self._lbl(label)); col.addWidget(widget)
        return col

    def _setup_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(15)

        # 1. BAĞLANTI GRUBU (Fiziksel Katman)
        f1 = QFrame(); f1.setStyleSheet(f"background:{C['bg_secondary']}; border-radius:10px;")
        ly1 = QVBoxLayout(f1); ly1.setContentsMargins(20, 15, 20, 20); ly1.setSpacing(12)
        ly1.addWidget(self._section_title("1. BAĞLANTI GRUBU (FİZİKSEL KATMAN)", C['accent_cyan']))
        
        r1a = QHBoxLayout(); r1a.setSpacing(15)
        # Port seçimi (Friendly Name desteği için genişletilebilir)
        self.combo_port = self._combo([], "COM4")
        self._refresh_ports()
        btn_refresh = QPushButton("🔄"); btn_refresh.setFixedSize(38, 38); btn_refresh.setStyleSheet(f"QPushButton{{background:{C['bg_primary']}; color:{C['accent_cyan']}; border-radius:6px; font:16px;}} QPushButton:hover{{background:{C['bg_card']};}}")
        btn_refresh.clicked.connect(self._refresh_ports)
        port_container = QWidget()
        p_row = QHBoxLayout(port_container)
        p_row.setContentsMargins(0, 0, 0, 0)
        p_row.addWidget(self.combo_port, 1)
        p_row.addWidget(btn_refresh)
        
        r1a.addLayout(self._field("PORT SEÇİMİ (AUTO-SCAN)", port_container), 1)

        self.combo_baudrate = self._combo(["9600", "57600", "115200"], "9600")
        r1a.addLayout(self._field("BAUD HIZI", self.combo_baudrate), 1)
        r1a.addLayout(self._field("STOP BITS & PARITY", self._combo(["8N1", "8E1", "8O1", "7N1"], "8N1")), 1)
        ly1.addLayout(r1a)
        
        r1b = QHBoxLayout(); r1b.setSpacing(15)
        r1b.addLayout(self._field("FLOW CONTROL (Hardware/Software)", self._combo(["None", "RTS/CTS", "XON/XOFF"], "None")), 1)
        r1b.addLayout(self._field("TIMEOUT (ZAMAN AŞIMI)", self._spin(1, 30, 3, " sn")), 1); r1b.addStretch(1)
        ly1.addLayout(r1b); layout.addWidget(f1)

        # 2. FİLTRELEME GRUBU (Sinyal İşleme)
        f3 = QFrame(); f3.setStyleSheet(f"background:{C['bg_secondary']}; border-radius:10px;")
        ly3 = QVBoxLayout(f3); ly3.setContentsMargins(20, 15, 20, 20); ly3.setSpacing(12)
        ly3.addWidget(self._section_title("3. DİNAMİK SİNYAL İŞLEME (FİLTRELEME)", "#FF00FF"))
        
        # Kalman Q ve R Varyansları
        rk = QHBoxLayout(); rk.setSpacing(15)
        rk.addLayout(self._field("KALMAN Q (PROCESS NOISE)", self._dspin(0.0001, 1.0, 0.01, 4, "#FF00FF")), 1)
        rk.addLayout(self._field("KALMAN R (MEASUREMENT NOISE)", self._dspin(0.0001, 10.0, 0.1, 4, "#FF00FF")), 1)
        ly3.addLayout(rk)
        
        # Birim Dönüştürücü
        ru = QHBoxLayout(); ru.setSpacing(15)
        ru.addLayout(self._field("UNIT SCALE (ÇARPAN)", self._dspin(0.001, 1000.0, 1.0, 3, C['text_secondary'])), 1)
        ru.addLayout(self._field("UNIT OFFSET (KAYMA)", self._dspin(-1000.0, 1000.0, 0.0, 3, C['text_secondary'])), 1)
        ly3.addLayout(ru); layout.addWidget(f3)

        # 3. SİMÜLASYON MODU (Basitleştirilmiş)
        f2 = QFrame(); f2.setStyleSheet(f"background:{C['bg_secondary']}; border-radius:10px;")
        ly2 = QHBoxLayout(f2); ly2.setContentsMargins(20, 12, 20, 12)
        sim_lbl = QLabel("◯  SİMÜLASYON MODUNU ETKİNLEŞTİR"); sim_lbl.setStyleSheet(f"color:{C['text_primary']}; font:700 13px 'Segoe UI';")
        ly2.addWidget(sim_lbl); ly2.addStretch()
        self.sim_toggle = QCheckBox(); self.sim_toggle.setStyleSheet(f"QCheckBox::indicator{{width:40px; height:20px; border-radius:10px; background:{C['bg_primary']}; border:2px solid {C['border_glow']};}} QCheckBox::indicator:checked{{background:{C['accent_green']};}}")
        self.sim_toggle.stateChanged.connect(lambda s: self.state_bus.simulation_command.emit("start" if s else "stop"))
        ly2.addWidget(self.sim_toggle); layout.addWidget(f2)

    def _refresh_ports(self):
        self.combo_port.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.combo_port.addItem(f"{p.device} ({p.description})")
        if not ports: self.combo_port.addItem("Cihaz Bulunamadı")
