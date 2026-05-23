import re
from datetime import datetime

class TelemetryParser:
    """Ham veriyi anlamlı objelere dönüştürür (CSV ve Human-Readable destekli)"""
    def __init__(self):
        self.packet_no = 0
        # Çok satırlı (human-readable) okuma için önbellek
        self.buffer = {
            "velocity": 0.0, "altitude": 0.0, "temperature": 0.0, "pressure": 0.0,
            "accel_x": 0.0, "accel_y": 0.0, "accel_z": 0.0,
            "vertical_velocity": 0.0, "gyro_x": 0.0, "gyro_y": 0.0, "gyro_z": 0.0,
            "pitch": 0.0, "roll": 0.0, "yaw": 0.0,
            "latitude": 0.0, "longitude": 0.0, "sinyal_gücü": -75.0,
            "paket_no": 0, "paket_kaybi": 0.0
        }

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
            
        # 1. KONTROL: Klasik virgüllü (CSV) format
        if ',' in raw_str:
            clean_str = raw_str.strip('$#')
            parts = [p.strip() for p in clean_str.split(',')]
            if len(parts) in (16, 17):
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
                        "sinyal_gücü":       -75.0,
                        "paket_no":          self.packet_no,
                        "paket_kaybi":       0.0,
                        "timestamp":         datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    }
                    if len(parts) == 17:
                        data["checksum"] = parts[16]
                    return data
                except (ValueError, IndexError):
                    pass
        
        # 2. KONTROL: İnsan Okuyabilir (Çok Satırlı) Format
        try:
            if "Paket #" in raw_str:
                m = re.search(r"Paket #(\d+)", raw_str)
                if m: self.buffer["paket_no"] = int(m.group(1))
            elif "Sicaklik" in raw_str:
                m = re.search(r"Sicaklik\s*:\s*([\d\.\-]+)", raw_str)
                if m: self.buffer["temperature"] = float(m.group(1))
            elif "Irtifa" in raw_str:
                m = re.search(r"Irtifa\s*:\s*([\d\.\-]+)", raw_str)
                if m: self.buffer["altitude"] = float(m.group(1))
            elif "Dikey Hiz" in raw_str:
                m = re.search(r"Dikey Hiz\s*:\s*([\d\.\-]+)", raw_str)
                if m: self.buffer["vertical_velocity"] = float(m.group(1))
            elif "Ivme X/Y/Z" in raw_str:
                m = re.search(r"Ivme X/Y/Z\s*:\s*([\d\.\-]+)\s*/\s*([\d\.\-]+)\s*/\s*([\d\.\-]+)", raw_str)
                if m:
                    self.buffer["accel_x"] = float(m.group(1))
                    self.buffer["accel_y"] = float(m.group(2))
                    self.buffer["accel_z"] = float(m.group(3))
            elif "Pitch/Roll" in raw_str:
                m = re.search(r"Pitch/Roll\s*:\s*([\d\.\-]+)\s*/\s*([\d\.\-]+)", raw_str)
                if m:
                    self.buffer["pitch"] = float(m.group(1))
                    self.buffer["roll"] = float(m.group(2))
            elif "Yaw" in raw_str:
                m = re.search(r"Yaw\s*:\s*([\d\.\-]+)", raw_str)
                if m: self.buffer["yaw"] = float(m.group(1))
            elif "PAKET ALINDI" in raw_str:
                # Paket sonuna ulaşıldı, tüm birikmiş veriyi bir paket olarak gönder
                emitted_data = self.buffer.copy()
                emitted_data["timestamp"] = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                return emitted_data
        except Exception:
            pass

        return None
