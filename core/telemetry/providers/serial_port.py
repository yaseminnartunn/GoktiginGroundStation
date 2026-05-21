import serial
import serial.tools.list_ports

class SerialPortProvider:
    """Gerçek donanım sağlayıcısı: Portları tarar ve veriyi okur."""
    def __init__(self, port=None, baudrate=9600):
        self.baudrate = baudrate
        self.serial_port = None
        self._setup_serial()

    def _setup_serial(self):
        """Bilgisayardaki portları tarar ve ilk bulduğuna bağlanır."""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                self.serial_port = serial.Serial(port.device, self.baudrate, timeout=1)
                print(f"✅ Connected: {port.device}")
                return
            except Exception as e:
                print(f"❌ Port Error ({port.device}): {e}")
        print("⚠️ No suitable serial port found.")

    def read_data(self):
        """Ham veriyi okur."""
        if self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    return self.serial_port.readline().decode('utf-8').strip()
            except Exception as e:
                print(f"🔴 Read Error: {e}")
        return None

    def close(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("🔌 Serial port closed.")

