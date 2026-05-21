class SimpleKalmanFilter:
    """
    Basit 1 Boyutlu Kalman Filtresi
    Özellikle gürültülü sensör verilerini (örneğin BMP180/280 veya GPS irtifa)
    düzeltmek (yumuşatmak) için kullanılır.
    """
    def __init__(self, mea_e=1.0, est_e=1.0, q=0.01):
        self.mea_e = mea_e      # Ölçüm hatası (Measurement Error)
        self.est_e = est_e      # Tahmin hatası (Estimation Error)
        self.q = q              # Süreç gürültüsü (Process Noise)
        self.last_estimate = 0.0
        self.is_initialized = False

    def update(self, measurement):
        if not self.is_initialized:
            self.last_estimate = measurement
            self.is_initialized = True
            return measurement
            
        # Kalman kazancını hesapla
        kalman_gain = self.est_e / (self.est_e + self.mea_e)
        
        # Mevcut tahmini hesapla
        current_estimate = self.last_estimate + kalman_gain * (measurement - self.last_estimate)
        
        # Tahmin hatasını güncelle
        self.est_e = (1.0 - kalman_gain) * self.est_e + abs(self.last_estimate - current_estimate) * self.q
        
        # Sonraki adım için tahmini kaydet
        self.last_estimate = current_estimate
        
        return current_estimate
