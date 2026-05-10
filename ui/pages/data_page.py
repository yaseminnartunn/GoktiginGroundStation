from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QBrush
from ui.styles import COLORS, DATA_COLORS

class DataTablePage(QWidget):
    """Tüm telemetri verilerini gösteren tablo sayfası"""
    
    data_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self._selected_row = -1
        self._setup_ui()
        
    def _setup_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['bg_primary']};
            }}
            QLabel#pageTitle {{
                color: {COLORS['text_primary']};
                font: 700 20px 'Segoe UI';
                letter-spacing: 2px;
            }}
            QLabel#pageSubtitle {{
                color: {COLORS['text_secondary']};
                font: 600 12px 'Segoe UI';
                letter-spacing: 3px;
            }}
            QTableWidget {{
                background: rgba(13, 31, 60, 200);
                border: 1px solid rgba(0, 212, 255, 100);
                border-radius: 12px;
                gridline-color: rgba(0, 212, 255, 30);
                color: #000000;
                font: 600 13px 'Segoe UI';
                alternate-background-color: rgba(5, 16, 40, 150);
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background: rgba(0, 212, 255, 50);
            }}
            QHeaderView::section {{
                background: rgba(5, 16, 40, 220);
                color: #000000;
                font: 700 12px 'Segoe UI';
                padding: 10px;
                border: none;
                border-bottom: 2px solid #00D4FF;
            }}
            QScrollBar:vertical {{
                background: {COLORS['bg_secondary']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['accent_cyan']};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Başlık
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        title = QLabel("TELEMETRİ VERİLERİ")
        title.setObjectName("pageTitle")
        title_layout.addWidget(title, 0, Qt.AlignCenter)
        
        subtitle = QLabel("ANLIK SENSÖR OKUMALARI")
        subtitle.setObjectName("pageSubtitle")
        title_layout.addWidget(subtitle, 0, Qt.AlignCenter)
        
        main_layout.addLayout(title_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["PARAMETRE", "DEĞER"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Sütun genişlikleri
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Satır seçimi sinyali
        self.table.itemClicked.connect(self._on_row_clicked)
        
        main_layout.addWidget(self.table, 1)
        
        # Başlangıç verileri
        self._init_table()
        
    def _init_table(self):
        """Tabloyu başlangıç değerleriyle doldur"""
        parameters = list(DATA_COLORS.keys())
        self.table.setRowCount(len(parameters))
        
        for i, param in enumerate(parameters):
            # Parametre adı
            param_item = QTableWidgetItem(param)
            param_item.setForeground(QColor(COLORS["text_secondary"]))
            param_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            self.table.setItem(i, 0, param_item)
            
            # Değer
            value_item = QTableWidgetItem("--")
            value_item.setForeground(QColor(DATA_COLORS.get(param, COLORS["text_primary"])))
            value_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            self.table.setItem(i, 1, value_item)
            
        self.table.setRowHeight(0, 40)
        
    def _on_row_clicked(self, item):
        """Satıra tıklandığında metin rengini vurgula"""
        row = item.row()
        
        # Önceki seçimi kaldır
        if self._selected_row >= 0 and self._selected_row < self.table.rowCount():
            self.table.item(self._selected_row, 0).setForeground(QColor(COLORS["text_secondary"]))
        
        # Yeni seçimi uygula
        if row != self._selected_row:
            self._selected_row = row
            param = self.table.item(row, 0).text()
            color = DATA_COLORS.get(param, COLORS["accent_cyan"])
            
            # Seçili satırın parametre adını renklendir
            self.table.item(row, 0).setForeground(QColor(color))
            
    def update_data(self, data):
        """Verileri tabloya güncelle"""
        if not data:
            for i in range(self.table.rowCount()):
                self.table.item(i, 1).setText("--")
            return
            
        # Veri eşlemesi
        param_map = {
            "HIZ (m/s)":      data.get("velocity"),
            "İRTİFA (m)":     data.get("altitude"),
            "SICAKLIK (°C)":  data.get("temperature"),
            "BASINÇ (hPa)":   data.get("pressure"),
            "İVME X (m/s²)":  data.get("accel_x"),
            "İVME Y (m/s²)":  data.get("accel_y"),
            "İVME Z (m/s²)":  data.get("accel_z"),
            "BATARYA (%)":    data.get("battery"),
            "ENLEM":          data.get("latitude"),
            "BOYLAM":         data.get("longitude"),
            "RSSI (dBm)":     data.get("rssi"),
            "PAKET":          data.get("pkt"),
            "KAYIP (%)":      data.get("kayip"),
            "ZAMAN":          data.get("timestamp"),
        }
        
        for i in range(self.table.rowCount()):
            param = self.table.item(i, 0).text()
            value = param_map.get(param)
            
            if value is not None:
                # Sayısal değerleri formatla
                if isinstance(value, float):
                    if param in ["İRTİFA (m)", "HIZ (m/s)", "BASINÇ (hPa)"]:
                        display_value = f"{value:.1f}"
                    elif param in ["SICAKLIK (°C)"]:
                        display_value = f"{value:.1f}"
                    elif param in ["İVME X (m/s²)", "İVME Y (m/s²)", "İVME Z (m/s²)"]:
                        display_value = f"{value:.2f}"
                    elif param in ["ENLEM", "BOYLAM"]:
                        display_value = f"{value:.6f}"
                    elif param in ["RSSI (dBm)"]:
                        display_value = f"{value:.1f}"
                    elif param in ["KAYIP (%)"]:
                        display_value = f"{value:.1f}"
                    else:
                        display_value = str(value)
                else:
                    display_value = str(value)
                    
                self.table.item(i, 1).setText(display_value)
                self.table.item(i, 1).setForeground(QColor(DATA_COLORS.get(param, COLORS["text_primary"])))
