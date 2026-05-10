from dataclasses import dataclass

@dataclass
class TelemetryState:
    """MERKEZİ VERİ KAYNAĞI: Anlık uçuş verileri"""
    velocity: float = 0.0
    altitude: float = 0.0
    temperature: float = 0.0
    pressure: float = 0.0
    accel_x: float = 0.0
    accel_y: float = 0.0
    accel_z: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    sinyal_gücü: float = 0.0
    paket_no: int = 0
    paket_kaybi: float = 0.0
    timestamp: str = ""
