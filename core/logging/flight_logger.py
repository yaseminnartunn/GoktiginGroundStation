import csv
import os
import datetime
import time

class FlightLogger:
    """
    FAIL-SAFE LOGGING: Telemetri verilerini anlık olarak CSV formatında diske yazar.
    Her paket geldiğinde dosya flus edilir (anlık yazılır), böylece çökme durumunda veri kaybı önlenir.
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
        self.log_interval = seconds

    def start_logging(self):
        if self.file_handle: self.stop_logging()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"flight_{timestamp}.csv"
        self.current_file_path = os.path.join(self.log_dir, filename)
        self.file_handle = open(self.current_file_path, "w", newline="", encoding="utf-8")
        self.writer = None
        self._last_log_time = 0

    def log_telemetry(self, data: dict):
        if not data or not self.file_handle: return
        curr = time.time()
        if self.log_interval > 0 and (curr - self._last_log_time < self.log_interval): return
        
        if self.writer is None:
            self.writer = csv.DictWriter(self.file_handle, fieldnames=data.keys())
            self.writer.writeheader()
        
        self.writer.writerow(data)
        self.file_handle.flush() # FAIL-SAFE: Anlık diske işle
        self._last_log_time = curr

    def stop_logging(self):
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            self.writer = None
