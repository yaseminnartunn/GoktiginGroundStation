# GökTigin Yer Kontrol İstasyonu (v3.7)

GökTigin Havacılık Takımı için geliştirilmiş, yüksek performanslı ve modern arayüzlü yer kontrol istasyonu yazılımı.

## 🚀 Genel Özellikler

*   **3D Roket Simülasyonu**: İvmeölçer ve Jiroskop verilerini kullanarak roketin yönelimini (Pitch, Roll, Yaw) anlık simüle eder.
*   **Key:Value Haberleşme Protokolü**: Veri kaybını ve sıra karışmasını önleyen etiketli haberleşme altyapısı.
*   **Gelişmiş Telemetri Analizi**: Hız, İrtifa, GPS, Basınç ve Açısal Hız verilerinin anlık takibi.
*   **Dinamik Ayarlar**: Yazılımı kapatmadan veri yenileme hızı ve filtre katsayılarını değiştirme imkanı.
*   **Otomatik Kayıt**: Tüm uçuş verilerini `.csv` formatında yüksek hassasiyetle yedekleme.

## 🛠 Teknik Mimari

Yazılım modüler bir yapıda, Python ve PyQt5 kütüphanesi kullanılarak geliştirilmiştir:
- `main.py`: Uygulamanın merkezi yönetim ve sayfa geçiş katmanı.
- `dashboard.py`: Sensör kartları, göstergeler ve roket simülasyonunun bulunduğu ana ekran.
- `haberlesme.py`: Seri port ve simülasyon motorunun çalıştığı arka plan thread'i.
- `veri_kaydi.py`: CSV loglama ve veri indirme sistemi.
- `config.py`: Neon tasarım sistemi ve renk paleti.

## 📡 Telemetri ve Filtre Mantığı (Detaylı Analiz)

Yazılımın kalbinde yer alan "Telemetri ve Filtre Ayarları" bölümü, roketten gelen ham verinin nasıl işleneceğini belirler.

### 1. Veri Yenileme Hızı (Data Rate)
Sistemde kullanılan RF modüllerinin bant genişliğine göre ayarlanır. 
*   **Simülasyon Modu**: Yazılımın ne kadar hızlı paket üreteceğini belirler.
*   **Gerçek Mod**: Donanımdan gelen verinin işlenme sıklığını senkronize eder.
*   **Önemli**: Dashboard altındaki **FREKANS** göstergesi, bağlantının kalitesini ve saniyede kaç paket ulaştığını ölçer.

### 2. Tamamlayıcı Filtre (Complementary Filter)
Roketin 3D yönelimi hesaplanırken **İvmeölçer** ve **Jiroskop** verileri birleştirilir. Bu işlem şu formülle yapılır:
`Açı = Alpha * (Açı + Gyro_Hızı * dt) + (1 - Alpha) * İvmeölçer_Açısı`

*   **Jiroskop (Hızlı Veri)**: Kısa vadede çok hassas ve pürüzsüzdür ancak zamanla "kayma" (drift) yapar.
*   **İvmeölçer (Kararlı Veri)**: Sarsıntılarda gürültülüdür ancak uzun vadede "yerçekimi" yönünü doğru gösterir.
*   **Alpha Katsayısı**:
    *   **%90-99 (Yüksek)**: Sarsıntılı uçuşlar için uygundur. Roket modeli pürüzsüz hareket eder.
    *   **%10-50 (Düşük)**: Çok sakin uçuşlar veya statik testler için uygundur.

### 3. Key:Value Protokolü
Veriler virgülle ayrılmış etiketli paketler halinde gelir. Örn: `PKT:10,ALT:120.5,VEL:12.2...`
Bu yöntem sayesinde:
1.  Sensör sırası karışsa bile yazılım veriyi doğru etiketle eşleştirir.
2.  Yeni bir sensör eklendiğinde eski kodlar bozulmaz.
3.  Eksik gelen paketler anında tespit edilir.

## 📦 Kurulum ve Çalıştırma

1.  Python 3.10+ kurulu olduğundan emin olun.
2.  Gerekli kütüphaneleri yükleyin: `pip install PyQt5 pyserial`
3.  Uygulamayı başlatın: `python main.py`

---
*GökTigin Havacılık Takımı - İstikbal Göklerdedir!* 🚀
