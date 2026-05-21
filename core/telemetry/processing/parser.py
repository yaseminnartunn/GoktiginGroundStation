class TelemetryParser:
    """
    TERCÜMAN (PARSER): 
    Roketten gelen karmaşık ve ham metinleri (CSV formatı), 
    yazılımın anlayabileceği düzenli bir sözlüğe (dictionary) çevirir.
    """
    def parse(self, raw_data):
        try:
            # 1. ADIM: Veri byte formatındaysa (0-1), onu okunabilir yazıya (string) çevir
            if isinstance(raw_data, bytes):
                raw_data = raw_data.decode('utf-8').strip()
            
            # 2. ADIM: Metnin başındaki ve sonundaki gereksiz boşlukları/satır başlarını temizle
            raw_data = str(raw_data).strip()
            
            # 3. ADIM: Metni her virgülden ayırarak bir liste haline getir
            # Örn: "1,350,20" -> ["1", "350", "20"]
            parts = raw_data.split(',')
            
            # 4. ADIM: Eğer veri paketi tam ise (14 parça), her bir sayıya isim ver
            if len(parts) >= 14:
                
                # --- CHECKSUM DOĞRULAMASI ---
                # Eğer roketten 15. bir veri (Checksum) geliyorsa, paketin yolda bozulup bozulmadığını kontrol et
                if len(parts) >= 15:
                    try:
                        received_checksum = int(parts[14])
                        # Son virgülden önceki tüm metni al (Örn: "1,350,...,2.5")
                        data_without_checksum = raw_data.rsplit(',', 1)[0]
                        # Karakterlerin ASCII değerlerini toplayıp 256'ya modunu alıyoruz (Standart Checksum)
                        calculated_checksum = sum(ord(c) for c in data_without_checksum) % 256
                        
                        if received_checksum != calculated_checksum:
                            return None # Paket yolda bozulmuş! Çöpe at.
                    except ValueError:
                        return None # Checksum sayı değil, paket bozuk.
                
                return {
                    "packet_no":    parts[0],          # Paket Numarası
                    "altitude":     float(parts[1]),   # İrtifa (Yükseklik)
                    "velocity":     float(parts[2]),   # Hız
                    "gps_lat":      float(parts[3]),   # Roketin Enlemi
                    "gps_long":     float(parts[4]),   # Roketin Boylamı
                    "accel_x":      float(parts[5]),   # X ekseni ivmesi
                    "accel_y":      float(parts[6]),   # Y ekseni ivmesi
                    "accel_z":      float(parts[7]),   # Z ekseni ivmesi
                    "payload_lat":  float(parts[8]),   # Faydalı Yük Enlemi
                    "payload_long": float(parts[9]),   # Faydalı Yük Boylamı
                    "pressure":     float(parts[10]),  # Basınç verisi
                    "gyro_x":       float(parts[11]),  # X ekseni dönüş hızı
                    "gyro_y":       float(parts[12]),  # Y ekseni dönüş hızı
                    "gyro_z":       float(parts[13]),  # Z ekseni dönüş hızı
                    
                    # Dashboard ve Harita sayfalarının ortak kullandığı ana koordinatlar:
                    "latitude":     float(parts[3]),
                    "longitude":    float(parts[4]),
                    
                    # Diğer alanlar için varsayılan değerler (Hata almamak için)
                    "temperature": 0.0,
                    "sinyal_gücü": 0.0,
                    "paket_kaybi": 0.0,
                    "vertical_velocity": 0.0,
                    "timestamp": ""
                }
            # Eğer 14 parçadan az veri geldiyse, paket bozuktur, None döndür.
            return None
        except Exception:
            # Sayıya çevirme (float) sırasında hata olursa (Örn: harf geldiyse) None döndür.
            return None



