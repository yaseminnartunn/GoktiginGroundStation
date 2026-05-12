import csv
import os
import datetime
import time

class FlightLogger:
    """
    KAYIT YÖNETİMİ: Telemetri verilerini belirlenen aralıklarla CSV formatında diske yazar.
    - Zaman Ayarlı Kayıt: Kullanıcı 3s, 5s, 10s gibi aralıklar belirleyebilir.
    - Fail-Safe: Her yazmada disk flus edilir.
    """
    def __init__(self, log_dir="data/flights"):
        self.log_dir = log_dir
        self.current_file_path = None
        self.file_handle = None
        self.writer = None
        self.log_interval = 0  # 0 = Anlık (her paket)
        self._last_log_time = 0
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def set_interval(self, seconds: float):
        """Kayıt aralığını günceller (0 = anlık)."""
        self.log_interval = seconds
        print(f"[LOGGER] Kayıt aralığı güncellendi: {seconds} sn")

    def start_logging(self):
        """Yeni bir uçuş log dosyası oluşturur."""
        if self.file_handle:
            self.stop_logging()

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"flight_{timestamp}.csv"
        self.current_file_path = os.path.join(self.log_dir, filename)
        
        self.file_handle = open(self.current_file_path, "w", newline="", encoding="utf-8")
        self.writer = None
        self._last_log_time = 0
        print(f"[LOGGER] Yeni kayıt başladı: {self.current_file_path}")

    def log_telemetry(self, data: dict):
        """Gelen veriyi belirlenen zaman aralığına göre CSV'ye ekler."""
        if not data or not self.file_handle:
            return

        current_time = time.time()
        
        # Zaman kontrolü (Anlık değilse ve süre dolmamışsa geç)
        if self.log_interval > 0:
            if current_time - self._last_log_time < self.log_interval:
                return

        # Header yazımı
        if self.writer is None:
            self.writer = csv.DictWriter(self.file_handle, fieldnames=data.keys())
            self.writer.writeheader()

        # Kaydet
        self.writer.writerow(data)
        self.file_handle.flush()
        self._last_log_time = current_time

    def stop_logging(self):
        """Kayıt işlemini sonlandırır."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            self.writer = None
            print("[LOGGER] Kayıt durduruldu.")

    def get_current_path(self):
        return self.current_file_path
