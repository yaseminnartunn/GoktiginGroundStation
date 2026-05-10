import math
import random
from datetime import datetime

class TelemetrySimulatorProvider:
    """Geliştirme aşaması için sahte veri üretir (Arayüz tabanlı tasarıma uygun)."""
    
    def __init__(self):
        self.t = 0.0
        
    def read_data(self) -> dict:
        self.t += 0.1
        t = self.t
        alt = max(0, 2800 * math.sin(t * 0.05) + random.gauss(0, 10))
        vel = max(0, 180 * math.sin(t * 0.05) * math.cos(t * 0.02) + random.gauss(0, 2))
        return {
            "velocity":    round(vel, 1),
            "altitude":    round(alt, 1),
            "accel_x":     round(random.gauss(0.2, 2.5), 2),
            "accel_y":     round(random.gauss(0.1, 2.3), 2),
            "accel_z":     round(random.gauss(-9.81, 1.2), 2),
            "temperature": round(-1.5 + alt * -0.006 + random.gauss(0, 0.3), 1),
            "pressure":    round(1013.25 * math.exp(-alt / 8500) + random.gauss(0, 0.5), 1),
            "battery":     round(max(0, 97 - t * 0.02 + random.gauss(0, 0.1)), 1),
            "latitude":    round(39.9053 + t * 0.00001 + random.gauss(0, 0.00002), 6),
            "longitude":   round(32.8049 + t * 0.00001 + random.gauss(0, 0.00002), 6),
            "rssi":        round(random.uniform(-105, -85), 1),
            "pkt":         int(t * 10),
            "kayip":       round(random.uniform(0, 2), 1),
            "timestamp":   datetime.now().strftime("%H:%M:%S.%f")[:-3],
        }
