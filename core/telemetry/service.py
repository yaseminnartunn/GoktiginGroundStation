import time
from PyQt5.QtCore import QThread
from core.events.state_bus import StateBus
from core.telemetry.processing.parser import TelemetryParser
from core.telemetry.processing.kalman import SimpleKalmanFilter

class TelemetryService(QThread):
    """
    ORKESTRA ŞEFİ (TELEMETRİ SERVİSİ): 
    Bu sınıf bir 'işçi' (QThread) olarak arka planda çalışır. 
    Ana görevi: Donanımdan veriyi çekmek, işlemek ve sisteme yaymaktır.
    """
    def __init__(self, provider, state_bus: StateBus):
        super().__init__()
        self.provider = provider      # Verinin nereden geleceğini tutar (Seri Port / Simülatör)
        self.state_bus = state_bus     # Duyuruları yapacağı santral merkezi
        self.parser = TelemetryParser() # Ham veriyi (string) parçalara ayıracak olan tercüman
        
        # Filtrelenecek veriler için ayrı ayrı Kalman filtreleri oluşturuyoruz
        self.kalman_filters = {
            "altitude": SimpleKalmanFilter(mea_e=1.0, est_e=1.0, q=0.01),
            "velocity": SimpleKalmanFilter(mea_e=1.0, est_e=1.0, q=0.01),
            "accel_x": SimpleKalmanFilter(mea_e=0.5, est_e=0.5, q=0.05),
            "accel_y": SimpleKalmanFilter(mea_e=0.5, est_e=0.5, q=0.05),
            "accel_z": SimpleKalmanFilter(mea_e=0.5, est_e=0.5, q=0.05),
            "pressure": SimpleKalmanFilter(mea_e=1.0, est_e=1.0, q=0.01),
            "gyro_x": SimpleKalmanFilter(mea_e=0.5, est_e=0.5, q=0.05),
            "gyro_y": SimpleKalmanFilter(mea_e=0.5, est_e=0.5, q=0.05),
            "gyro_z": SimpleKalmanFilter(mea_e=0.5, est_e=0.5, q=0.05),
            "latitude": SimpleKalmanFilter(mea_e=0.0001, est_e=0.0001, q=0.00001),
            "longitude": SimpleKalmanFilter(mea_e=0.0001, est_e=0.0001, q=0.00001),
            "gps_lat": SimpleKalmanFilter(mea_e=0.0001, est_e=0.0001, q=0.00001),
            "gps_long": SimpleKalmanFilter(mea_e=0.0001, est_e=0.0001, q=0.00001),
            "payload_lat": SimpleKalmanFilter(mea_e=0.0001, est_e=0.0001, q=0.00001),
            "payload_long": SimpleKalmanFilter(mea_e=0.0001, est_e=0.0001, q=0.00001),
            "vertical_velocity": SimpleKalmanFilter(mea_e=1.0, est_e=1.0, q=0.01),
            "temperature": SimpleKalmanFilter(mea_e=0.5, est_e=0.5, q=0.01)
        }
        
        self._running = True          # Servis çalışmaya devam etsin mi?
        self._paused = True           # Başlangıçta veri akışı duraklatılmış (beklemede) başlar

    def handle_simulation_command(self, cmd: str):
        """Arayüzdeki butonlara basıldığında veri akışını yönetir."""
        if cmd == "start":
            self._paused = False      # Akışı başlat
        elif cmd == "stop":
            self._paused = True       # Akışı duraklat
        elif cmd == "clear":
            self._paused = True       # Akışı duraklat ve ekrana boş veri gönder
            self.state_bus.telemetry_updated.emit({})

    def run(self):
        """Thread başladığında bu döngü program kapanana kadar durmadan çalışır."""
        while self._running:
            if self._paused:
                time.sleep(0.1)       # Duraklatıldıysa bekle ve başa dön
                continue
                
            # 1. ADIM: Donanımdan (veya simülatörden) ham veriyi al
            raw_data = self.provider.read_data()
            
            # 2. ADIM: Veri varsa işle
            if raw_data:
                # Eğer veri zaten hazır bir sözlükse (Simülatörden geliyorsa)
                if isinstance(raw_data, dict):
                    data = raw_data
                else:
                    # Eğer veri seri porttan gelen bir metinse, Parser ile parçala
                    data = self.parser.parse(raw_data)
                
                # 3. ADIM: İşlenmiş veri geçerliyse, bunu StateBus üzerinden yayınla
                if data:
                    # Gelen veriyi (data) filtre sözlüğündeki anahtarlarla eşleştir ve filtrele
                    for key, kalman in self.kalman_filters.items():
                        if key in data and isinstance(data[key], (int, float)):
                            data[key] = kalman.update(data[key])
                            
                    self.state_bus.telemetry_updated.emit(data)
            
            # Bilgisayarın işlemcisini %100 kullanmaması için kısa bir mola (100ms)
            time.sleep(0.1)

    def stop(self):
        """Program kapatılırken servisi güvenli bir şekilde durdurur."""
        self._running = False

