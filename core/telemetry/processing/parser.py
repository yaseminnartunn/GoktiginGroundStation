from datetime import datetime

class TelemetryParser:
    """Ham veriyi anlamlı objelere dönüştürür (CSV parser)"""
    def __init__(self):
        self.packet_no = 0

    def parse(self, raw_data):
        if not raw_data:
            return None
        
        # Byte ise string'e çevir
        if isinstance(raw_data, bytes):
            try:
                raw_data = raw_data.decode("utf-8", errors="ignore")
            except Exception:
                return None
                
        raw_str = raw_data.strip()
        if not raw_str:
            return None
            
        # Başlangıç ($) ve bitiş (#) işaretlerini kaldır (varsa)
        if raw_str.startswith('$'):
            raw_str = raw_str[1:]
        if raw_str.endswith('#'):
            raw_str = raw_str[:-1]
            
        parts = [p.strip() for p in raw_str.split(',')]
        
        # HIZ,IRTIFA,SICAKLIK,BASINC,IVME_X,IVME_Y,IVME_Z,DIKEY_HIZ,OMEGA_X,OMEGA_Y,OMEGA_Z,PITCH,ROLL,YAW,ENLEM,BOYLAM,CHECKSUM
        # En az enlem/boylama kadar (16 eleman) veya checksum dahil (17 eleman) olmalı
        if len(parts) not in (16, 17):
            return None
            
        try:
            self.packet_no += 1
            data = {
                "velocity":          round(float(parts[0]), 1),
                "altitude":          round(float(parts[1]), 1),
                "temperature":       round(float(parts[2]), 1),
                "pressure":          round(float(parts[3]), 1),
                "accel_x":           round(float(parts[4]), 2),
                "accel_y":           round(float(parts[5]), 2),
                "accel_z":           round(float(parts[6]), 2),
                "vertical_velocity": round(float(parts[7]), 1),
                "gyro_x":            round(float(parts[8]), 2),
                "gyro_y":            round(float(parts[9]), 2),
                "gyro_z":            round(float(parts[10]), 2),
                "pitch":             round(float(parts[11]), 1),
                "roll":              round(float(parts[12]), 1),
                "yaw":               round(float(parts[13]), 1),
                "latitude":          round(float(parts[14]), 6),
                "longitude":         round(float(parts[15]), 6),
                "sinyal_gücü":       -75.0,  # Varsayılan sinyal gücü (RSSI)
                "paket_no":          self.packet_no,
                "paket_kaybi":       0.0,
                "timestamp":         datetime.now().strftime("%H:%M:%S.%f")[:-3]
            }
            
            if len(parts) == 17:
                data["checksum"] = parts[16]
                
            return data
        except (ValueError, IndexError):
            return None
