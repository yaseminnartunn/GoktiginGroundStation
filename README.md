# GoktiginGroundStation
## Teknofest 2026 – Orta İrtifa Roket Yarışması – Göktigin Roket Takımı

---

### 📖 Proje Özeti
`GoktiginGroundStation
`, Göktigin Roket Takımı’nın **Teknofest 2026 Orta İrtifa Roket Yarışması**’nda kullanılmak üzere geliştirdiği, **tamamen Python/Qt5** tabanlı, görsel‑zengin bir **yer kontrol istasyonu**dur. Uçuş sırasında telemetri verilerini gerçek‑zamanlı olarak alır, grafiksel bir arayüzde gösterir ve veri kaydını yönetir.
**Not:** Uygulamayı başlatmak için giriş ekranında **kullanıcı adı:** `a` ve **şifre:** `a` (büyük/küçük harfe duyarlıdır) kullanılmalıdır.
---
### ✨ Öne Çıkan Özellikler

| Özellik | Açıklama |
|---------|----------|
| **Görsel Tasarım** | Şık **glass‑morphism**, dinamik yıldız alanı, scan‑line efekti ve özel renk paleti. |
| **Qt5‑QtWebEngine** tabanlı **responsive UI** – Windows‑10/11 uyumlu. |
| **Gerçek‑zamanlı Telemetri** | `TelemetryService` (QThread) ile **simülatör** ya da **seri port** üzerinden veri alımı. |
| **Kalman Filtreleme** | Altitude, hız ve dikey hız verileri için `KalmanFilter1D` uygulanır, gürültünün etkisi azaltılır. |
| **Kayıt / Log** | `FlightLogger` ile konfigüre edilebilir periyotlarda CSV/JSON loglama. |
| **Bağlantı Yönetimi** | `StateBus` sinyalleri üzerinden **seri port** bağlanması, ayrılması ve simülasyon geçişi. |
| **Kullanıcı Girişi** | `LoginPage` içinde basit kullanıcı‑şifre doğrulama (`a:a` varsayılan). |
| **Modüler Mimari** | `core` (events, telemetry, state) ve `ui` (pages, manager) katmanları ayrı tutulmuş, **Dependency Injection** prensibiyle. |
| **Cross‑Platform** | Python‑3.10+ uyumlu, `requirements.txt` içinde bağımlılıklar listelenmiştir. |

### 🚀 Başlangıç Rehberi

1. **Depoyu klonlayın** ve proje klasörüne girin
   ```bash
   git clone https://github.com/yaseminnartunn/Yer-stasyonuVer2.git
   cd Yer-stasyonuVer2
   ```

2. **Sanal ortam oluşturun** (isteğe bağlı)
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1   # PowerShell
   ```

3. **Bağımlılıkları kurun**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Uygulamayı çalıştırın**
   ```powershell
   python main.py
   ```
   *Uygulama açılır, **kullanıcı adı:** `a` – **şifre:** `a`  ile giriş yapılabilir (değiştirilebilir, `ui/pages/login_page.py` içinde `USERS` sözlüğü güncellenir).*

### 🔧 Özelleştirme

| İhtiyaç | Dosya / Bölüm | Nasıl Değiştirilir |
|--------|---------------|-------------------|
| **Kullanıcı‑şifre** | `ui/pages/login_page.py` → `class LoginPage.USERS` | `"kullanici": "parola"` gibi yeni çift ekleyin. |
| **Kalman parametreleri** | `core/telemetry/service.py` (satır 20‑24) | `process_noise`, `measurement_noise`, `estimated_error` değerlerini ayarlayın. |
| **Log formatı / dosya yolu** | `core/logging/flight_logger.py` | `self.log_file = Path("logs") / f"{datetime.now():%Y%m%d_%H%M%S}.csv"` gibi değiştirin. |
| **Renk & Tema** | `ui/pages/login_page.py` (style sheet) ve `ui/styles.py` | `COLORS` sözlüğündeki HEX renkleri değiştirin. |
| **Seri Port** | `core/telemetry/providers/serial_port.py` | `port` ve `baudrate` parametrelerini gerektiği gibi ayarlayın. |

### 🛠️ Geliştirme İçin Önerilen Araçlar

| Araç | Kullanım Alanı |
|------|-----------------|
| **PyCharm / VS Code** | Kod tamamlama, refactor, debugger |
| **Git** | Versiyon kontrol, branch yönetimi |
| **Black / isort** | Kod formatlama, import sıralama |
| **pytest** | Birim testleri (eklenebilir) |
| **Flake8 / mypy** | Statik analiz, tip kontrolü |

### 📚 Dokümantasyon & Kaynaklar
- **Qt5 Documentation** – https://doc.qt.io/qt-5/
- **PyQt5 Quick Start** – https://www.riverbankcomputing.com/static/Docs/PyQt5/
- **Kalman Filter Tutorial** – https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python
- **Teknofest 2026 Kılavuzu** – (resmi teknofest sitesinde yarışma kuralları)

### 🤝 Katkı & İletişim
1. **Fork** edin, değişikliklerinizi `feature/your‑name` branşıyla gönderin.
2. **Pull Request** açın, kod incelemesi ve test sonuçlarını ekleyin.
3. Sorular / öneriler için **issues** kısmını kullanın.

