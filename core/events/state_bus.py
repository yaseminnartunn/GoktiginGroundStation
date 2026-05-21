from PyQt5.QtCore import QObject, pyqtSignal

class StateBus(QObject):
    """
    SİNYAL SİSTEMİ (HABERLEŞME HATTI):
    Yazılımın içindeki birimlerin (Örn: Seri Port ve Harita Sayfası) 
    birbirinden bağımsız ama haberdar çalışmasını sağlar.
    """
    
    # Yeni bir telemetri verisi (sözlük yapısında) geldiğinde tüm sisteme duyurur.
    telemetry_updated = pyqtSignal(dict)
    
    # Kullanıcı giriş yaptığında durumunu (başarılı/başarısız) ve mesajını taşır.
    login_status = pyqtSignal(bool, str)
    
    # Arayüzden gelen 'Başlat', 'Durdur' gibi komutları TelemetryService'e iletir.
    simulation_command = pyqtSignal(str)
    
    # Bilgisayara kayıt (log) alma aralığı değiştiğinde bunu duyurur.
    log_interval_changed = pyqtSignal(float)

