import time
from PyQt5.QtCore import QThread
from core.events.state_bus import StateBus

class TelemetryService(QThread):
    """
    ORKESTRA ŞEFİ: Telemetri verilerini sağlayıcıdan (provider) alır, 
    gerekirse doğrular (validator) ve StateBus üzerinden UI'a yayınlar.
    """
    def __init__(self, provider, state_bus: StateBus):
        super().__init__()
        self.simulator_provider = provider
        self.serial_provider = None
        self.provider = self.simulator_provider
        self.state_bus = state_bus
        self._running = True
        self._paused = True  # Varsayılan olarak duraklatıldı
        
        # Kalman Filtreleri
        from core.telemetry.processing.kalman import KalmanFilter1D
        self.kalman_altitude = KalmanFilter1D(process_noise=0.1, measurement_noise=100.0, estimated_error=1.0)
        self.kalman_velocity = KalmanFilter1D(process_noise=0.05, measurement_noise=4.0, estimated_error=1.0)
        self.kalman_vertical_velocity = KalmanFilter1D(process_noise=0.05, measurement_noise=1.0, estimated_error=1.0)
        
        # Sinyal Bağlantıları
        self.state_bus.connect_serial.connect(self.handle_connect_serial)
        self.state_bus.disconnect_serial.connect(self.handle_disconnect_serial)

    def handle_connect_serial(self, port, baudrate):
        from core.telemetry.providers.serial_port import SerialPortProvider
        if self.serial_provider:
            self.serial_provider.disconnect()
        self.serial_provider = SerialPortProvider(port, baudrate)
        self.provider = self.serial_provider
        self._paused = False
        print(f"TelemetryService: Gerçek donanıma geçildi ({port} @ {baudrate})")

    def handle_disconnect_serial(self):
        if self.serial_provider:
            self.serial_provider.disconnect()
        self.provider = self.simulator_provider
        self._paused = True
        print("TelemetryService: Seri port bağlantısı kesildi, duraklatıldı.")

    def handle_simulation_command(self, cmd: str):
        if cmd == "start":
            self.provider = self.simulator_provider
            self._paused = False
        elif cmd == "stop":
            self._paused = True
        elif cmd == "clear":
            self._paused = True
            self.kalman_altitude.reset()
            self.kalman_velocity.reset()
            self.kalman_vertical_velocity.reset()
            self.state_bus.telemetry_updated.emit({})

    def run(self):
        while self._running:
            if self._paused:
                time.sleep(0.1)
                continue
                
            # Sağlayıcıdan veriyi al
            data = self.provider.read_data()
            
            if data:
                if "altitude" in data:
                    data["altitude_raw"] = data["altitude"]
                    data["altitude_kalman"] = round(self.kalman_altitude.update(data["altitude"]), 1)
                    data["altitude"] = data["altitude_kalman"]
                if "velocity" in data:
                    data["velocity_raw"] = data["velocity"]
                    data["velocity_kalman"] = round(self.kalman_velocity.update(data["velocity"]), 1)
                    data["velocity"] = data["velocity_kalman"]
                if "vertical_velocity" in data:
                    data["vertical_velocity_raw"] = data["vertical_velocity"]
                    data["vertical_velocity_kalman"] = round(self.kalman_vertical_velocity.update(data["vertical_velocity"]), 1)
                    data["vertical_velocity"] = data["vertical_velocity_kalman"]
            
                # Veriyi StateBus üzerinden yayınla
                self.state_bus.telemetry_updated.emit(data)
            time.sleep(0.1)

    def stop(self):
        self._running = False
        if self.serial_provider:
            self.serial_provider.disconnect()

