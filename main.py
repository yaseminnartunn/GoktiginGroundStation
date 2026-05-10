import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QFileDialog
from PyQt5.QtGui import QFont

# Kendi modüllerimiz
from config import COLORS
from girişsayfası import LoginPage
from seriayarlar import SettingsPage
from dashboard import DashboardPage
from haberlesme import HaberlesmeMotoru

class GroundStation(QMainWindow):
    """
    Tüm sayfaların geçişlerini ve arkadaki haberleşme altyapısını
    birbiriyle konuşturan (yöneten) çok hafif bir Ana Pencere.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GökTigin Yer İstasyonu — TEKNOFEST 2026")
        self.setMinimumSize(1280, 780)
        self.logo_path = str(Path(__file__).resolve().parent / "fotoğraflar" / "logo.png")

        # Genel arka plan
        self.setStyleSheet(f"QMainWindow, QWidget {{ background: {COLORS['bg_primary']}; }}")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sayfa Yöneticisi (QStackedWidget)
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # 1. Sayfaları Oluştur
        self.login_page = LoginPage(self.show_dashboard, self.logo_path, COLORS)
        self.dashboard_page = DashboardPage()
        self.settings_page = SettingsPage(COLORS)
        
        # 2. Sayfaları Yığına Ekle
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.settings_page)
        
        # İlk açılışta Giriş Ekranını göster
        self.stack.setCurrentWidget(self.login_page)

        # 3. Haberleşme ve Veri Motorunu Başlat
        self.haberlesme = HaberlesmeMotoru()
        
        # Haberleşme motorundan gelen veriyi, Dashboard sayfasına aktar
        self.haberlesme.veri_ayristirildi_sinyali.connect(self.dashboard_page.update_data)

        # 4. Sayfalar Arası Buton Bağlantıları
        self.dashboard_page.top_bar.settings_btn.clicked.connect(self.show_settings)
        self.settings_page.btn_back.clicked.connect(self.show_dashboard_only)
        self.settings_page.btn_connect.clicked.connect(self._on_serial_connect)
        self.settings_page.btn_disconnect.clicked.connect(self._on_serial_disconnect)
        self.settings_page.btn_download.clicked.connect(self._on_download_data)
        self.settings_page.btn_toggle_record.clicked.connect(self._on_toggle_record)

        # ── YENİ: Dinamik Ayar Bağlantıları ─────────────────────────────
        self.settings_page.spin_rate.valueChanged.connect(self.haberlesme.set_hiz)
        self.settings_page.spin_filter.valueChanged.connect(self.dashboard_page.set_filter_alpha)

    def show_dashboard_only(self):
        self.stack.setCurrentWidget(self.dashboard_page)
        
    def show_settings(self):
        self.stack.setCurrentWidget(self.settings_page)

    def _on_serial_connect(self):
        port = self.settings_page.cb_port.currentText()
        baud = self.settings_page.cb_baud.currentText()
        sim_mu = self.settings_page.chk_simulation.isChecked()
        
        # Bağlantı başarılı olursa otomatik olarak Ana Ekrana ışınlan
        if self.haberlesme.baglan(port, baud, sim_mu):
            self.show_dashboard_only()

    def _on_serial_disconnect(self):
        self.haberlesme.baglantiyi_kes()

    def _on_download_data(self):
        klasor = QFileDialog.getExistingDirectory(self, "Kayıtların İndirileceği Klasörü Seçin")
        if klasor:
            self.haberlesme.kaydedici.veri_indir(klasor)

    def _on_toggle_record(self):
        kaydedici = self.haberlesme.kaydedici
        kaydedici.kayit_aktif = not kaydedici.kayit_aktif
        
        if kaydedici.kayit_aktif:
            self.settings_page.btn_toggle_record.setText("■ KAYDI DURDUR")
            self.settings_page.btn_toggle_record.setStyleSheet("""
                QPushButton { color: #FF4D4D; font: 600 11px 'Segoe UI'; background: transparent; border: 1px solid #FF4D4D; border-radius: 4px; padding: 4px 8px; }
                QPushButton:hover { background: rgba(255, 77, 77, 40); color: #FFF; }
            """)
        else:
            self.settings_page.btn_toggle_record.setText("▶ KAYDI BAŞLAT")
            self.settings_page.btn_toggle_record.setStyleSheet("""
                QPushButton { color: #00FF9C; font: 600 11px 'Segoe UI'; background: transparent; border: 1px solid #00FF9C; border-radius: 4px; padding: 4px 8px; }
                QPushButton:hover { background: rgba(0, 255, 156, 40); color: #000; }
            """)

    def show_dashboard(self, success, username=None):
        if success:
            self.stack.setCurrentWidget(self.dashboard_page)

    def closeEvent(self, event):
        if hasattr(self, 'haberlesme') and self.haberlesme is not None:
            self.haberlesme.baglantiyi_kes()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    win = GroundStation()
    win.show()
    sys.exit(app.exec_())