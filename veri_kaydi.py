import datetime
import os

class VeriKaydedici:
    """
    Yer istasyonuna gelen sensör verilerini 'ucus_kaydi.csv' adlı dosyaya 
    tarih ve saat damgasıyla (timestamp) kalıcı olarak kaydetmek için kullanılır.
    """
    def __init__(self, dosya_adi="ucus_kaydi.csv"):
        self.dosya_adi = dosya_adi
        self.kayit_aktif = True  # Yeni özellik: Kullanıcı dilerse kaydı duraklatabilir
        
        # Eğer dosya hiç oluşturulmamışsa, ilk satıra (header) başlıkları ekler
        if not os.path.exists(self.dosya_adi):
            try:
                with open(self.dosya_adi, "w", encoding="utf-8") as f:
                    f.write("KayitZamani,PaketNumarasi,Irtifa,Hiz,Enlem,Boylam,IvmeX,IvmeY,IvmeZ,GyroX,GyroY,GyroZ,FaEnlem,FaBoylam,FaBasinc,GpsIrtifasi\n")
            except Exception as e:
                print("Log dosyası oluşturulamadı:", e)

    def veri_kaydet(self, data_str):
        """
        Gelen virgülle ayrılmış sensör verisini zaman damgasıyla (timestamp) birlikte
        ucus_kaydi.csv dosyasına alt satır olarak ekler.
        """
        # Kayıt butonu ile durdurulmuşsa hiçbir şey yapmadan dön
        if not self.kayit_aktif:
            return

        try:
            # O anki saati ve tarihi al (Örn: 2026-05-10 14:30:15)
            zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # "a" (append - sonuna ekle) modunda açar, verileri silmez alt satıra ekler
            with open(self.dosya_adi, "a", encoding="utf-8") as dosya:
                dosya.write(f"{zaman},{data_str}\n")
                
        except Exception as e:
            print("Veri loglama hatası:", e)

    def veri_indir(self, hedef_klasor):
        """
        Kaydedilen 'ucus_kaydi.csv' dosyasını güvenli bir şekilde
        kullanıcının seçtiği klasöre kopyalar (indirir).
        """
        import shutil
        
        # Eğer henüz kayıt dosyası yoksa işlem yapma
        if not os.path.exists(self.dosya_adi):
            print("Hata: İndirilecek (kopyalanacak) herhangi bir kayıt bulunamadı.")
            return False
            
        try:
            # Hedef dosyanın adının sonuna çakışmaması için saati ekliyoruz
            zaman_eki = datetime.datetime.now().strftime("%H%M%S")
            hedef_dosya = os.path.join(hedef_klasor, f"ucus_kaydi_disa_aktarim_{zaman_eki}.csv")
            
            # shutil.copy2 ile dosyayı hedef klasöre güvenle kopyala
            shutil.copy2(self.dosya_adi, hedef_dosya)
            print(f"BAŞARILI: Veriler başarıyla şu konuma indirildi: {hedef_dosya}")
            return True
        except Exception as e:
            print("Veri indirme (dışa aktarma) hatası:", e)
            return False
