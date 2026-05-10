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
        self.provider = provider
        self.state_bus = state_bus
        self._running = True
        self._paused = True  # Varsayılan olarak duraklatıldı

    def handle_simulation_command(self, cmd: str):
        if cmd == "start":
            self._paused = False
        elif cmd == "stop":
            self._paused = True
        elif cmd == "clear":
            self._paused = True
            self.state_bus.telemetry_updated.emit({})

    def run(self):
        while self._running:
            if self._paused:
                time.sleep(0.1)
                continue
                
            # Sağlayıcıdan veriyi al
            data = self.provider.read_data()
            
            # TODO: processing/parser ve processing/validator buraya eklenebilir.
            
            # Veriyi StateBus üzerinden yayınla
            self.state_bus.telemetry_updated.emit(data)
            time.sleep(0.1)

    def stop(self):
        self._running = False
