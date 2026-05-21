from PyQt5.QtCore import QObject, pyqtSignal

class StateBus(QObject):
    """
    SİNYAL SİSTEMİ: Veri değişimini UI'a duyuran mekanizma.
    UI bu sinyalleri dinler, iş mantığı ise bu sinyalleri tetikler.
    Böylece aralarında doğrudan bir bağ kalmaz.
    """
    # dict türünde telemetri verisi
    telemetry_updated = pyqtSignal(dict)
    
    # Kullanıcı giriş başarılı/başarısız durumu
    login_status = pyqtSignal(bool, str)
    
    # Simülasyon komutları (örn: "start", "stop")
    simulation_command = pyqtSignal(str)
    
    # Kayıt aralığı (saniye cinsinden)
    log_interval_changed = pyqtSignal(float)

    # Seri port bağlantı sinyalleri
    connect_serial = pyqtSignal(str, int)  # port, baudrate
    disconnect_serial = pyqtSignal()

