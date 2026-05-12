import os
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, pyqtSlot, QTimer, Qt
from ui.styles import COLORS

C = COLORS

class MapPage(QWidget):
    """
    Harita Sayfası: Sadece koordinatlar değiştiğinde güncellenen akıllı harita sistemi.
    """
    def __init__(self, state_bus):
        super().__init__()
        self.state_bus = state_bus
        
        # Koordinatlar
        self.rocket_pos = [38.3745, 33.2456]
        self.payload_pos = [38.3750, 33.2460]
        self.pc_pos = None
        
        # Son çizilen koordinatlar (Gereksiz yenilemeyi önlemek için)
        self._last_draw_rocket = [0, 0]
        self._last_draw_payload = [0, 0]
        
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20); layout.setSpacing(15)

        # Üst Panel
        info_row = QHBoxLayout()
        self.rocket_card = self._create_info_card("ROKET", C['accent_orange'])
        self.lbl_rocket = QLabel("Bekleniyor..."); self.lbl_rocket.setStyleSheet(f"color:{C['text_primary']}; font:13px 'Segoe UI';")
        self.rocket_card.layout().addWidget(self.lbl_rocket); info_row.addWidget(self.rocket_card)

        self.payload_card = self._create_info_card("GÖREV YÜKÜ", C['accent_cyan'])
        self.lbl_payload = QLabel("Bekleniyor..."); self.lbl_payload.setStyleSheet(f"color:{C['text_primary']}; font:13px 'Segoe UI';")
        self.payload_card.layout().addWidget(self.lbl_payload); info_row.addWidget(self.payload_card)

        self.test_card = self._create_info_card("SİSTEM KONUMU", C['accent_green'])
        self.btn_toggle_pc = QPushButton("🛰 HASSAS KONUMU AÇ")
        self.btn_toggle_pc.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_pc.setStyleSheet(self._btn_style(False))
        self.btn_toggle_pc.clicked.connect(self._handle_pc_location)
        self.test_card.layout().addWidget(self.btn_toggle_pc); info_row.addWidget(self.test_card)

        layout.addLayout(info_row)

        # Harita
        self.web_view = QWebEngineView()
        self.web_view.page().featurePermissionRequested.connect(self._on_permission_requested)
        self.web_view.setStyleSheet(f"background:{C['bg_secondary']}; border-radius:15px; border:1px solid {C['border_glow']};")
        self._update_map() # İlk çizim
        layout.addWidget(self.web_view, 1)

    def _btn_style(self, active):
        if active:
            return f"QPushButton{{background:{C['accent_green']}30; color:{C['accent_green']}; border:2px solid {C['accent_green']}; border-radius:6px; padding:8px; font:700 11px 'Segoe UI';}}"
        return f"QPushButton{{background:{C['bg_primary']}; color:{C['text_dim']}; border:1px solid {C['border_glow']}; border-radius:6px; padding:8px; font:700 11px 'Segoe UI';}} QPushButton:hover{{color:{C['accent_green']}; border-color:{C['accent_green']};}}"

    def _create_info_card(self, title, color):
        frame = QFrame()
        frame.setStyleSheet(f"background:{C['bg_secondary']}; border-radius:10px; border-left:4px solid {color};")
        ly = QVBoxLayout(frame); ly.setContentsMargins(15, 10, 15, 10)
        lbl_t = QLabel(title); lbl_t.setStyleSheet(f"color:{color}; font:700 11px 'Segoe UI'; letter-spacing:1px;")
        ly.addWidget(lbl_t)
        return frame

    def _on_permission_requested(self, url, feature):
        if feature == QWebEnginePage.Geolocation:
            self.web_view.page().setFeaturePermission(url, feature, QWebEnginePage.PermissionGrantedByUser)

    def _handle_pc_location(self):
        if self.pc_pos:
            self.pc_pos = None
            self.btn_toggle_pc.setText("🛰 HASSAS KONUMU AÇ")
            self.btn_toggle_pc.setStyleSheet(self._btn_style(False))
            self._update_map()
        else:
            self.btn_toggle_pc.setText("⏳ ARANIYOR...")
            try:
                response = requests.get("http://ip-api.com/json/", timeout=5).json()
                if response["status"] == "success":
                    self.pc_pos = [response["lat"], response["lon"]]
                    self.btn_toggle_pc.setText("✅ KONUM AKTİF (KAPAT)")
                    self.btn_toggle_pc.setStyleSheet(self._btn_style(True))
                    self._update_map()
                else:
                    self.btn_toggle_pc.setText("❌ MEŞGUL")
            except:
                self.btn_toggle_pc.setText("❌ HATA")

    def _connect_signals(self):
        self.state_bus.telemetry_updated.connect(self._on_telemetry)

    def _on_telemetry(self, data):
        updated = False
        
        # Roket GPS
        if "gps_lat" in data and "gps_long" in data:
            lat, lon = float(data["gps_lat"]), float(data["gps_long"])
            if lat != 0 and (abs(lat - self.rocket_pos[0]) > 0.0001 or abs(lon - self.rocket_pos[1]) > 0.0001):
                self.rocket_pos = [lat, lon]
                self.lbl_rocket.setText(f"Lat: {lat:.5f}\nLon: {lon:.5f}")
                updated = True
        
        # Görev Yükü GPS
        if "payload_lat" in data and "payload_long" in data:
            lat, lon = float(data["payload_lat"]), float(data["payload_long"])
            if lat != 0 and (abs(lat - self.payload_pos[0]) > 0.0001 or abs(lon - self.payload_pos[1]) > 0.0001):
                self.payload_pos = [lat, lon]
                self.lbl_payload.setText(f"Lat: {lat:.5f}\nLon: {lon:.5f}")
                updated = True

        # Sadece koordinatlar değiştiyse haritayı yenile
        if updated:
            self._update_map()

    def _update_map(self):
        import folium
        try:
            # Gereksiz render'ı önle (Sadece koordinatlar ciddi değişince)
            if self.rocket_pos == self._last_draw_rocket and self.payload_pos == self._last_draw_payload:
                return
            
            m = folium.Map(location=self.rocket_pos, zoom_start=14, tiles="OpenStreetMap")
            folium.Marker(self.rocket_pos, popup="ROKET", icon=folium.Icon(color="orange", icon="rocket", prefix="fa")).add_to(m)
            folium.Marker(self.payload_pos, popup="GÖREV YÜKÜ", icon=folium.Icon(color="blue", icon="archive", prefix="fa")).add_to(m)
            
            if self.pc_pos:
                folium.Marker(self.pc_pos, popup="YER İSTASYONU", icon=folium.Icon(color="cadetblue", icon="home", prefix="fa")).add_to(m)

            self.web_view.setHtml(m._repr_html_())
            self._last_draw_rocket = self.rocket_pos[:]
            self._last_draw_payload = self.payload_pos[:]
        except Exception as e:
            print(f"Map render error: {e}")
