class SerialPortProvider:
    """Saha kullanımı için gerçek donanım sağlayıcısı (İskelet)"""
    def __init__(self, port="COM3", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        
    def read_data(self):
        # Gerçek donanımdan seri port okuma işlemleri
        pass
