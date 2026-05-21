import csv
import os
import datetime
import time

class FlightLogger:
    """
    UÇUŞ KAYITÇISI (LOGGER): 
    Roketten gelen tüm telemetri verilerini anlık olarak CSV formatında bilgisayara yazar.
    Her paket geldiğinde dosya 'flush' edilir, yani anında kaydedilir. 
    Bu sayede bilgisayar kapansa bile veri kaybı yaşanmaz.
    """
    def __init__(self, log_dir="data/flights"):
        self.log_dir = log_dir           # Kayıtların saklanacağı ana klasör
        self.current_file_path = None    # Oluşturulan CSV dosyasının bilgisayardaki yolu
        self.file_handle = None          # Python'un dosyayı yönettiği nesne
        self.writer = None               # CSV yazma işlemlerini yapan araç
        self.log_interval = 0            # Kayıt sıklığı (0 = Her paket, 1 = Saniyede bir)
        self._last_log_time = 0          # En son ne zaman kayıt yapıldığını tutan sayaç
        
        # Eğer 'data/flights' klasörü yoksa, program başında otomatik oluştur
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def set_interval(self, seconds: float):
        """Kayıt sıklığını ayarlamaya yarar (Örn: 0.5 saniye)."""
        self.log_interval = seconds

    def start_logging(self):
        """Yeni bir uçuş dosyası açar ve kayda başlar."""
        if self.file_handle: self.stop_logging() # Eğer açık dosya varsa önce onu kapat
        
        # Dosya adını o anki tarih ve saatle oluştur (Örn: flight_2024-05-13_15-30-00.csv)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"flight_{timestamp}.csv"
        self.current_file_path = os.path.join(self.log_dir, filename)
        
        # Dosyayı 'Yazma' modunda aç ve hazırla
        self.file_handle = open(self.current_file_path, "w", newline="", encoding="utf-8")
        self.writer = None
        self._last_log_time = 0

    def log_telemetry(self, data: dict):
        """Gelen her telemetri paketini dosyaya bir satır olarak ekler."""
        if not data or not self.file_handle: return
        
        curr = time.time()
        # Belirlenen kayıt aralığına uyulup uyulmadığını kontrol et
        if self.log_interval > 0 and (curr - self._last_log_time < self.log_interval): 
            return
        
        # Eğer CSV dosyasının başlıkları (Sıcaklık, Hız vb.) yazılmadıysa, ilk satıra yaz
        if self.writer is None:
            self.writer = csv.DictWriter(self.file_handle, fieldnames=data.keys())
            self.writer.writeheader() # Başlık satırını ekle

        # Veri paketini (sözlüğü) CSV satırı olarak yaz
        self.writer.writerow(data)
        
        # KRİTİK: Veriyi hemen diske işle (flush). Çökme durumunda veriyi korur.
        self.file_handle.flush() 
        self._last_log_time = curr

    def stop_logging(self):
        """Kayıt işlemini bitirir ve dosyayı güvenli bir şekilde kapatır."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            self.writer = None
