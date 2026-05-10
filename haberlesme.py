import time
import math
import random
import serial
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal

# Loglama sınıfımızı dışarıdan içeri aktarıyoruz
from veri_kaydi import VeriKaydedici

class HaberlesmeMotoru(QThread):
    """
    Arka planda (ayrı bir thread üzerinde) çalışan, arayüzü dondurmadan (kasmadan)
    seri port verilerini okuyan veya simülasyon verisi üreten motor.
    """
    # Veri başarıyla ayrıştırıldığında arayüze (main.py'ye) fırlatılacak sinyal
    veri_ayristirildi_sinyali = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self._calisiyor = False
        self.simulasyon_modu = False
        self.seri_port = None
        self.port_ismi = ""
        self.baud_hizi = 9600
        
        # Loglama sınıfımızı başlatıyoruz
        self.kaydedici = VeriKaydedici()
        
        # Simülasyon için kullanılan zaman değişkeni
        self.t = 0.0

        # Dikey Hız hesabı için geçmiş veriler
        self._son_irtifa = 0.0
        self._son_zaman = 0.0
        self.hz = 5.0  # Kullanıcının SET ettiği (istenen) hız
        
        # Gerçek zamanlı frekans hesaplama
        self._paket_sayaci = 0
        self._frekans_zamanlayici = time.time()
        self.anlik_hz = 0.0

    def baglan(self, port, baud, simulasyon_mu):
        """
        Kullanıcı Ayarlar sayfasından "Bağlan" dediğinde çağrılır.
        """
        self.port_ismi = port
        self.baud_hizi = baud
        self.simulasyon_modu = simulasyon_mu
        
        # Eğer simülasyon değilse, gerçek donanıma (COM Port) bağlanmayı dene
        if not self.simulasyon_modu:
            try:
                self.seri_port = serial.Serial(self.port_ismi, int(self.baud_hizi), timeout=1)
                print(f"BAŞARILI: {self.port_ismi} portuna bağlanıldı.")
            except Exception as e:
                print(f"HATA: {self.port_ismi} portuna bağlanılamadı. Hata detayları: {e}")
                return False # Bağlantı başarısız
        
        # Thread'i (Arka plan döngüsünü) başlat
        self._calisiyor = True
        self.start()
        return True

    def baglantiyi_kes(self):
        """
        Kullanıcı "Bağlantıyı Kes" dediğinde çağrılır.
        """
        self._calisiyor = False
        self.wait() # Döngünün tamamen durmasını bekle
        
        if self.seri_port and self.seri_port.is_open:
            self.seri_port.close()
            print("Seri port bağlantısı kapatıldı.")

    def set_hiz(self, hz):
        """Dışarıdan (Settings) veri yenileme hızını dinamik değiştirmek için."""
        self.hz = max(1, hz)
        print(f"BİLGİ: Veri hızı {self.hz} Hz olarak güncellendi.")

    def run(self):
        """
        QThread başlatıldığında otomatik olarak çalışan ve sürekli dönen arka plan döngüsü.
        """
        while self._calisiyor:
            if self.simulasyon_modu:
                # SİMÜLASYON MODU: Yapay veri üret
                data_str = self._simulasyon_verisi_uret()
                self.seri_veri_oku(data_str)
                time.sleep(1.0 / self.hz) 
            else:
                # GERÇEK MOD: Seri porttan gelen verileri dinle
                if self.seri_port and self.seri_port.is_open:
                    try:
                        if self.seri_port.in_waiting > 0:
                            # Porttan satır satır okur ve temizler (strip)
                            data_str = self.seri_port.readline().decode('utf-8').strip()
                            if data_str:
                                self.seri_veri_oku(data_str)
                    except Exception as e:
                        print("Veri okuma sırasında bağlantı hatası:", e)
                        time.sleep(0.1)
                else:
                    time.sleep(0.1)

    def seri_veri_oku(self, data_str):
        """
        Okunan veya üretilen ham string veriyi alır, kaydeder ve ayrıştırmaya gönderir.
        Eski sistemdeki 'read_serial_data'nın yeni versiyonu.
        """
        # 1. Adım: Her gelen veriyi 'ucus_kaydi.csv' içerisine kalıcı olarak yazdır
        self.kaydedici.veri_kaydet(data_str)
        
        # 2. Adım: Veriyi virgüllerinden ayırıp sözlüğe (dict) dönüştür
        self.veri_ayristir_ve_guncelle(data_str)

    def veri_ayristir_ve_guncelle(self, data_str):
        """
        KEY:VALUE formatlı veriyi ayrıştırıp arayüzün anlayacağı sözlüğe döndürür.
        Beklenen format: PKT:1,ALT:11.2,VEL:0.0,LAT:39.905,LON:32.804,...
        """
        ZORUNLU_ANAHTARLAR = ['PKT','ALT','VEL','LAT','LON','AX','AY','AZ','GX','GY','GZ','FLAT','FLON','FPRESS','GALT']
        try:
            # Her 'ANAHTAR:DEGER' cıftını ayrıştır
            d = {}
            for parca in data_str.split(','):
                if ':' in parca:
                    anahtar, deger = parca.split(':', 1)
                    d[anahtar.strip()] = deger.strip()

            # Zorunlu anahtarların hepsinin gelip gelmediğini kontrol et
            eksikler = [k for k in ZORUNLU_ANAHTARLAR if k not in d]
            if eksikler:
                print(f"HATA: Eksik anahtar(lar): {eksikler} | Veri: {data_str}")
                return

            # Dikey hız hesabı
            current_alt = float(d['ALT'])
            current_time = time.time()
            dikey_hiz = 0.0
            if self._son_zaman > 0:
                dt = current_time - self._son_zaman
                if dt > 0:
                    dikey_hiz = (current_alt - self._son_irtifa) / dt
            self._son_irtifa = current_alt
            self._son_zaman = current_time

            data_dict = {
                "pkt":              int(d['PKT']),
                "altitude":         current_alt,
                "velocity":         float(d['VEL']),
                "latitude":         float(d['LAT']),
                "longitude":        float(d['LON']),
                "accel_x":          float(d['AX']),
                "accel_y":          float(d['AY']),
                "accel_z":          float(d['AZ']),
                "gyro_x":           float(d['GX']),
                "gyro_y":           float(d['GY']),
                "gyro_z":           float(d['GZ']),
                "fa_lat":           float(d['FLAT']),
                "fa_lon":           float(d['FLON']),
                "pressure":         float(d['FPRESS']),
                "gps_altitude":     float(d['GALT']),  # YENİ: GPS İrtifası
                "vertical_velocity":round(dikey_hiz, 2),
                "temperature":      25.0,
                "timestamp":        datetime.now().strftime("%H:%M:%S.%f")[:-3],
                "raw_data":         data_str,
                "actual_hz":        self.anlik_hz  # ANLIK FREKANS
            }
            
            # Frekans hesaplama (Her 1 saniyede bir güncelle)
            self._paket_sayaci += 1
            simdi = time.time()
            if simdi - self._frekans_zamanlayici >= 1.0:
                self.anlik_hz = self._paket_sayaci / (simdi - self._frekans_zamanlayici)
                self._paket_sayaci = 0
                self._frekans_zamanlayici = simdi

            self.veri_ayristirildi_sinyali.emit(data_dict)
        except Exception as e:
            print("AYRIPŞTIRMA HATASI:", e, "| Veri:", data_str)
            
    def _simulasyon_verisi_uret(self):
        """
        Sensör olmadan test yapabilmek için gerçekçi uuş verileri üretir.
        KEY:VALUE formatında üretir — sıra karışması imkansız.
        """
        self.t += 0.1
        t = self.t
        pkt = int(t * 10)
        alt = max(0, 2800 * math.sin(t * 0.05) + random.gauss(0, 10))
        vel = max(0, 180 * math.sin(t * 0.05) * math.cos(t * 0.02) + random.gauss(0, 2))
        lat = 39.9053 + t * 0.00001
        lon = 32.8049 + t * 0.00001
        acc_x = random.gauss(0.2, 2.5)
        acc_y = random.gauss(0.1, 2.3)
        acc_z = random.gauss(-9.81, 1.2)
        gyro_x = random.gauss(5.0, 2.0) * math.sin(t * 0.1)
        gyro_y = random.gauss(10.0, 5.0)
        gyro_z = random.gauss(0.0, 1.0)
        fa_lat   = lat + 0.001
        fa_lon   = lon + 0.001
        fa_press = 1013.25 * math.exp(-alt / 8500)
        # GPS irtifası (barometre irtifasından hafif farklı olabilir)
        gps_alt  = alt + random.gauss(0, 3.0)

        # KEY:VALUE formatı — Arduino tarafında da aynı format kullanılmalı!
        return (
            f"PKT:{pkt},ALT:{alt:.1f},VEL:{vel:.1f},"
            f"LAT:{lat:.6f},LON:{lon:.6f},"
            f"AX:{acc_x:.2f},AY:{acc_y:.2f},AZ:{acc_z:.2f},"
            f"GX:{gyro_x:.2f},GY:{gyro_y:.2f},GZ:{gyro_z:.2f},"
            f"FLAT:{fa_lat:.6f},FLON:{fa_lon:.6f},FPRESS:{fa_press:.1f},"
            f"GALT:{gps_alt:.1f}"
        )
