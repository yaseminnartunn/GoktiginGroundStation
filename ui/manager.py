from ui.windows.main_window import MainWindow

class UIManager:
    """
    UI Controller: Sinyalleri dinler, sayfaları yönetir.
    İş mantığı ve UI arasındaki bağlantıyı sağlar.
    """
    def __init__(self, state_bus, logo_path, colors):
        self.state_bus = state_bus
        self.window = MainWindow(state_bus, logo_path, colors)
        
        # StateBus üzerinden gelen verileri UI'a bağla
        self.state_bus.telemetry_updated.connect(self.on_telemetry_updated)
        
        # Eğer MainWindow'da login başarılı olursa, controller'ı haberdar etmek istiyorsak:
        # Ancak LoginPage şu anda direkt MainWindow içindeki self.show_dashboard callback'ini çağırıyor.
        # Clean architecture gereği login işlemi UIManager üzerinden geçebilir. 
        # Fakat UI kodu %100 aynı kalsın diye mevcut callback sistemini (show_dashboard) MainWindow içinde tuttuk.
        # Ek bağlantılar buraya eklenebilir.

    def on_telemetry_updated(self, data):
        # UI bileşenlerine veriyi dağıt
        self.window.top_bar.update_data(data)
        self.window.status_bar.update_data(data)
        self.window.dashboard_page.update_data(data)
        self.window.data_page.update_data(data)

    def show(self):
        self.window.show()
