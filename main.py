import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

# Core Katmanı
from core.events.state_bus import StateBus
from tests.mocks.simulator import TelemetrySimulatorProvider
from core.telemetry.service import TelemetryService

# Sunum Katmanı
from ui.manager import UIManager
from ui.styles import COLORS

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))

    # ==========================================
    # BAĞIMLILIK ENJEKSİYONU (DI) VE BAŞLATMA
    # ==========================================

    # 1. State Bus (Sinyal Sistemi) Başlatılır
    state_bus = StateBus()

    # 2. Telemetri Sağlayıcı ve Servisi Başlatılır
    simulator_provider = TelemetrySimulatorProvider()
    telemetry_service = TelemetryService(simulator_provider, state_bus)
    state_bus.simulation_command.connect(telemetry_service.handle_simulation_command)

    # 3. UI Yöneticisi Başlatılır ve Bus'a Bağlanır
    # Not: Mevcut logoda değişiklik yapılmaması için aynı logo_path korundu.
    logo_path = r"C:\Users\Acer\.cursor\projects\c-Users-Acer-OneDrive-Desktop-deneme\assets\c__Users_Acer_AppData_Roaming_Cursor_User_workspaceStorage_5586babad2924fabad38f53e1f4af2a6_images_image-75a32522-e95c-4ea2-a86a-4c64f6e6cb5b.png"
    ui_manager = UIManager(state_bus, logo_path, COLORS)

    # 4. Servisler Çalıştırılır
    telemetry_service.start()
    ui_manager.show()

    # 5. Uygulama Döngüsü
    exit_code = app.exec_()

    # Kapanış Temizliği
    telemetry_service.stop()
    telemetry_service.wait()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()