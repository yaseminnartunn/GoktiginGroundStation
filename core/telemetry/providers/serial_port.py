import serial
import time
from core.telemetry.processing.parser import TelemetryParser

class SerialPortProvider:
    """Saha kullanımı için gerçek donanım sağlayıcısı"""
    def __init__(self, port="COM3", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.parser = TelemetryParser()

    def connect(self):
        """Seri port bağlantısını açar"""
        self.disconnect() # Eğer açık bağlantı varsa kapat
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=0.2)
            # Giriş tamponunu temizle
            self.serial_conn.reset_input_buffer()
            print(f"Seri port bağlandı: {self.port} @ {self.baudrate}")
            return True
        except Exception as e:
            print(f"Seri port bağlantı hatası ({self.port}): {e}")
            self.serial_conn = None
            return False

    def disconnect(self):
        """Seri port bağlantısını kapatır"""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
                print(f"Seri port bağlantısı kesildi: {self.port}")
            except Exception:
                pass
        self.serial_conn = None

    def read_data(self) -> dict:
        """Seri porttan veri okur ve ayrıştırır"""
        if not self.serial_conn or not self.serial_conn.is_open:
            # Bağlı değilse, bağlanmayı dene
            if not self.connect():
                time.sleep(1.0) # Sürekli hızlı deneme yapıp sistemi yormasın
                return None

        try:
            # Satır oku
            line = self.serial_conn.readline()
            if not line:
                return None
            
            # Veriyi parse et
            parsed_data = self.parser.parse(line)
            return parsed_data
        except Exception as e:
            print(f"Seri port veri okuma hatası: {e}")
            # Port koptuysa kapat ki sonraki döngüde tekrar bağlanmayı denesin
            self.disconnect()
            time.sleep(0.5)
            return None

