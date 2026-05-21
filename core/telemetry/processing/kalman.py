class KalmanFilter1D:
    """
    Bir Boyutlu Kalman Filtresi (1D Kalman Filter)
    Gürültülü sensör ölçümlerini düzeltmek için kullanılır.
    """
    def __init__(self, process_noise: float = 0.1, measurement_noise: float = 10.0, estimated_error: float = 1.0, initial_value: float = 0.0):
        self.q = process_noise  # Süreç gürültüsü kovaryansı (Q)
        self.r = measurement_noise  # Ölçüm gürültüsü kovaryansı (R)
        self.p = estimated_error  # Tahmin hata kovaryansı (P)
        self.x = initial_value  # Durum tahmini (x)
        self.initialized = False

    def update(self, measurement: float) -> float:
        if not self.initialized:
            self.x = measurement
            self.initialized = True
            return self.x

        # Tahmin Adımı (Predict)
        p_prior = self.p + self.q

        # Güncelleme Adımı (Correct)
        kalman_gain = p_prior / (p_prior + self.r)
        self.x = self.x + kalman_gain * (measurement - self.x)
        self.p = (1.0 - kalman_gain) * p_prior

        return self.x

    def reset(self, initial_value: float = 0.0):
        self.x = initial_value
        self.p = 1.0
        self.initialized = False
