---
alwaysApply: true
---

# Proje Anayasası: Telegram Analiz Aracı

Bu belge, "Telegram Analiz Aracı" projesinin geliştirilmesi sırasında uyulması zorunlu olan teknik kuralları, mimari yapıyı ve standartları tanımlar. Projeye dahil olan her geliştirici bu anayasayı okumuş ve kabul etmiş sayılır.

## 1. Felsefe ve Genel Prensipler

1.  **Modülerlik:** Her bileşen (UI, Core, Utils) kendi içinde bir bütün olmalı ve diğer bileşenlerle olan bağımlılığı minimumda tutulmalıdır. UI, core olmadan çalışmaz ama core, UI olmadan test edilebilir olmalıdır.
2.  **Okunabilirlik > Kısalık:** Kod, onu ilk kez okuyan bir geliştirici tarafından bile kolayca anlaşılabilir olmalıdır. PEP 8 standartlarına harfiyen uyulacaktır.
3.  **Tek Sorumluluk Prensibi (Single Responsibility Principle):** Her sınıf ve her fonksiyon, iyi tanımlanmış tek bir işi yapmalıdır.
4.  **Test Edilebilirlik:** Yazılan her kod parçası, özellikle `core` katmanındaki mantık, birim testleri (unit tests) ile test edilebilir şekilde tasarlanmalıdır.
5.  **Performans Odaklı:** Büyük veri setleri için optimize edilmiş, hızlı filtreleme ve işlem kapasitesine sahip olmalıdır.

## 2. Teknoloji Yığını (Technology Stack)

Bu projede aşağıdaki teknoloji ve kütüphaneler dışında bir teknoloji kullanılması kesinlikle yasaktır. Versiyonlar, projenin tutarlılığı için kilitlenmiştir.

* **Programlama Dili:** Python 3.11.x
* **Telegram İstemcisi:** `telethon==1.34.0` (Asenkron yapısı ve kullanıcı hesabı otomasyonu için)
* **Kullanıcı Arayüzü (GUI):** `flet==0.21.0` (Modern web benzeri arayüz ve cross-platform desteği için)
* **Dosya İşlemleri (Excel):** `pandas==2.2.2` ve `openpyxl==3.1.2`
* **Veri Yönetimi:** `sqlite3` (Yerel contact database için)
* **Asenkron İşlemler:** `asyncio` ve `aiofiles==23.2.1`
* **Çevre Değişkenleri:** `python-dotenv==1.0.0` (.env dosyası okuma için)
* **Logging:** `logging` (Python built-in, detaylı loglama için)
* **Bağımlılık Yönetimi:** Proje kök dizininde bulunan `requirements.txt` dosyası kullanılacaktır. Sanal ortam (virtual environment) kullanımı zorunludur.
* **Kod Formatlama:** `black==24.4.2`
* **Kod Analizi (Linting):** `flake8==7.0.0`
* **Executable (Dağıtım):** `pyinstaller==6.6.0`

## 3. Proje Mimarisi

Proje, **Katmanlı Mimari (Layered Architecture)** prensibine göre tasarlanacaktır. Bu mimari, sorumlulukların net bir şekilde ayrılmasını sağlar.

* **Sunum Katmanı (`ui`):** Kullanıcının gördüğü ve etkileşimde bulunduğu tüm arayüz bileşenlerini içerir. Bu katman, iş mantığı (`core`) hakkında doğrudan bilgi sahibi değildir. Yalnızca `core` katmanındaki fonksiyonları çağırır ve ondan gelen veriyi kullanıcıya gösterir.
* **İş Mantığı Katmanı (`core`):** Uygulamanın beynidir. Tüm Telegram işlemleri (bağlanma, numara kontrolü), dosya okuma/yazma, contact management ve veri işleme mantığı bu katmanda yer alır. Bu katmanın, sunum katmanından (`ui`) haberi yoktur.
* **Veri Katmanı (`data`):** Contact bilgilerinin saklanması ve yönetimi için SQLite veritabanı işlemleri.
* **Giriş Noktası (`main.py`):** Uygulamayı başlatan, UI ve Core katmanlarını birbirine bağlayan ana script.

## 4. Klasör Yapısı

Proje, aşağıdaki klasör yapısına harfiyen uyacaktır. Bu yapı, modülerliği ve kodun bulunabilirliğini artırır.

```
telegram_checker/
│
├── core/
│   ├── __init__.py
│   ├── telegram_client.py      # Telethon ile ilgili tüm mantık (bağlantı, kontrol vb.)
│   ├── file_handler.py         # Dosya okuma/yazma işlemleri (Excel, Txt)
│   ├── contact_manager.py      # Contact CRUD işlemleri ve veritabanı yönetimi
│   ├── number_generator.py     # Otomatik numara oluşturma sistemi
│   └── anti_robot_driver.py    # Anti-robot driver mode ve rate limiting
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # Ana uygulama penceresi ve tüm arayüz bileşenleri
│   ├── contact_panel.py        # Contact yönetimi için özel panel
│   ├── number_generator_panel.py # Otomatik numara oluşturma paneli
│   ├── number_checker_panel.py # Dosyadan numara kontrolü paneli
│   └── widgets/                # Özel arayüz bileşenleri
│       ├── __init__.py
│       ├── fast_filter.py      # Super fast filter widget'ı
│       ├── progress_bar.py     # Özel progress bar
│       └── number_range_input.py # Numara aralığı giriş widget'ı
│
├── data/
│   ├── __init__.py
│   ├── database.py             # SQLite veritabanı yönetimi
│   └── models.py               # Veri modelleri (Contact, NumberRecord vb.)
│
├── assets/
│   └── icon.ico                # Uygulama ikonu
│
├── tests/
│   ├── __init__.py
│   ├── test_file_handler.py    # file_handler fonksiyonları için birim testleri
│   ├── test_telegram_client.py # telegram_client için testler
│   ├── test_contact_manager.py # contact_manager için testler
│   ├── test_number_generator.py # number_generator için testler
│   ├── test_database.py        # database işlemleri için testler
│   └── test_anti_robot.py      # anti_robot_driver için testler
│
├── .gitignore                  # Git'in takip etmeyeceği dosyalar (örn: pycache, .env)
├── anayasa.md                  # BU DOSYA
├── main.py                     # Uygulamanın başlangıç noktası
├── map.md                      # Proje yol haritası
└── requirements.txt            # Proje bağımlılıkları
```

## 5. Kodlama Standartları

1.  **Formatlama:** Her `commit` işleminden önce tüm proje `black .` komutu ile formatlanmalıdır.
2.  **Linting:** `commit` öncesi `flake8 .` komutu çalıştırılmalı ve kritik hatalar (error) düzeltilmelidir.
3.  **İsimlendirme:**
    * Değişkenler ve fonksiyonlar: `snake_case` (örn: `kontrol_edilecek_numaralar`)
    * Sınıflar (Classes): `PascalCase` (örn: `TelegramClient`)
    * Sabitler (Constants): `UPPER_SNAKE_CASE` (örn: `API_ID`)
4.  **Docstrings:** Her modül, sınıf ve fonksiyonun bir `docstring`'i olmalıdır. `Google Style Docstrings` formatı kullanılacaktır.
5.  **Type Hinting:** Tüm fonksiyon parametreleri ve geri dönüş değerleri için `type hinting` (tür ipuçları) kullanımı zorunludur. Bu, kodun anlaşılırlığını ve güvenilirliğini artırır.
6.  **Yapılandırma (Configuration):** `API_ID` ve `API_HASH` gibi hassas veriler asla koda gömülmeyecektir. Bu veriler, `.gitignore` dosyasına eklenmiş bir `.env` dosyası üzerinden okunacaktır.
7.  **Güvenlik:** Session dosyaları şifrelenmiş olarak saklanacak ve API anahtarları için ek güvenlik katmanları uygulanacaktır.

## 6. Git ve Versiyon Kontrolü

1.  **Branch Stratejisi:**
    * `main`: Sadece stabil ve yayınlanmış versiyonları içerir. Doğrudan `commit` atılmaz.
    * `develop`: Geliştirme yapılan ana branch'tir.
    * `feature/<ozellik-adi>`: Her yeni özellik veya modül için `develop` branch'inden yeni bir `feature` branch'i açılır (örn: `feature/contact-management`). İş bitince `develop` branch'ine `merge` edilir.
2.  **Commit Mesajları:** "Conventional Commits" standardı zorunludur.
    * `feat:`: Yeni bir özellik eklendiğinde.
    * `fix:`: Bir hata düzeltildiğinde.
    * `docs:`: Sadece dokümantasyon (örn: bu dosya) güncellendiğinde.
    * `style:`: Sadece kod formatlaması (black, linting) yapıldığında.
    * `refactor:`: Kodun işlevini değiştirmeyen yapısal düzenlemeler yapıldığında.
    * `test:`: Test eklendiğinde veya mevcut testler düzenlendiğinde.
    * Örnek: `feat: Add contact management system with name-number pairing`

## 7. Hata Yönetimi (Error Handling)

* Uygulama hiçbir koşulda son kullanıcıya ham bir `exception` göstermemelidir.
* Tüm beklenen hatalar (`FileNotFoundError`, Telethon'dan gelen `PhoneNumberInvalidError`, `FloodWaitError` vb.) `try...except` blokları içinde yakalanmalı ve kullanıcıya anlaşılır bir dilde (örn: bir pop-up ile) bildirilmelidir.
* Beklenmeyen hatalar için genel bir `exception handler` mekanizması kurulmalı ve bu hatalar bir log dosyasına yazılmalıdır.

## 8. Contact Management Sistemi

### 8.1 Veri Yapısı
```python
class Contact:
    id: int
    name: str
    phone_number: str
    is_valid: bool
    last_checked: datetime
    notes: str
    created_at: datetime
    updated_at: datetime
```

### 8.2 CRUD Operasyonları
* **Create:** Yeni contact ekleme (isim + numara)
* **Read:** Contact listesi okuma, arama ve filtreleme
* **Update:** Contact bilgilerini güncelleme
* **Delete:** Contact silme

### 8.3 Arama ve Filtreleme
* İsme göre arama
* Numaraya göre arama
* Geçerlilik durumuna göre filtreleme
* Son kontrol tarihine göre filtreleme

## 8.5 Otomatik Numaralar Sistemi

### 8.5.1 Numaralar Veritabanı Yapısı
```python
class NumberRecord:
    id: int
    country_code: str          # +90, +1, +44 vb.
    operator_prefix: str       # 555, 542, 501 vb.
    phone_number: str          # 1234567 (alan kodu olmadan)
    full_number: str           # +905551234567
    is_valid: bool             # Telegram'da kayıtlı mı?
    is_checked: bool           # Daha önce kontrol edildi mi?
    check_date: datetime       # Son kontrol tarihi
    check_count: int           # Kaç kez kontrol edildi
    notes: str                 # Ek notlar
    created_at: datetime       # Oluşturulma tarihi
    updated_at: datetime       # Güncellenme tarihi
```

### 8.5.2 Otomatik Numaralar Oluşturma
* **Ülke Kodu Sabit:** Kullanıcı ülke kodunu seçer (+90, +1, +44 vb.)
* **Operatör Seçimi:** Ülkeye özel operatör numara aralıklarını seçme
* **Numara Aralığı:** Seçilen operatörün numara aralığını belirleme
* **Pattern Oluşturma:** Belirli pattern'lere göre numara üretme
* **Bulk Generation:** Binlerce numarayı tek seferde oluşturma

### 8.5.2.1 Ülke Bazlı Operatör Numaraları
```python
# Türkiye (+90) Operatör Numaraları
TURKEY_OPERATORS = {
    "Turkcell": ["501", "502", "503", "504", "505", "506", "507", "508", "509", "530", "531", "532", "533", "534", "535", "536", "537", "538", "539", "561"],
    "Vodafone": ["542", "543", "544", "545", "546", "547", "548", "549", "552", "553", "554", "555", "556", "557", "558", "559"],
    "Türk Telekom": ["501", "502", "503", "504", "505", "506", "507", "508", "509", "530", "531", "532", "533", "534", "535", "536", "537", "538", "539"],
    "Diğer": ["540", "541", "550", "551", "560", "562", "563", "564", "565", "566", "567", "568", "569"]
}

# ABD (+1) Operatör Numaraları (Örnek)
USA_OPERATORS = {
    "Verizon": ["201", "202", "203", "204", "205"],
    "AT&T": ["206", "207", "208", "209", "210"],
    "T-Mobile": ["211", "212", "213", "214", "215"]
}

# İngiltere (+44) Operatör Numaraları (Örnek)
UK_OPERATORS = {
    "Vodafone": ["7700", "7701", "7702", "7703"],
    "O2": ["7704", "7705", "7706", "7707"],
    "EE": ["7708", "7709", "7710", "7711"]
}
```

### 8.5.2.2 Akıllı Numara Aralığı Belirleme
* **Operatör Seçimi:** Kullanıcı hangi operatörün numaralarını kontrol etmek istediğini seçer
* **Otomatik Aralık:** Seçilen operatörün numara aralığı otomatik belirlenir
* **Özel Aralık:** Kullanıcı isterse özel numara aralığı da girebilir
* **Çoklu Operatör:** Birden fazla operatör seçilebilir

### 8.5.3 Numaralar Yönetimi
* **Yeni Numaralar:** Daha önce kontrol edilmemiş numaraları bulma
* **Cache Sistemi:** Kontrol edilmiş numaraları tekrar kontrol etmeme
* **Batch Processing:** Numaraları gruplar halinde işleme
* **Progress Tracking:** Hangi numaraların kontrol edildiğini takip etme

### 8.5.4 Numaralar Filtreleme
* **Geçerli Numaralar:** Telegram'da kayıtlı olanlar
* **Geçersiz Numaralar:** Telegram'da kayıtlı olmayanlar
* **Kontrol Edilmemiş:** Henüz kontrol edilmemiş numaralar
* **Tarih Filtreleme:** Belirli tarihte kontrol edilenler

## 9. Anti-Robot Driver Mode

### 9.1 Rate Limiting
* Telegram API limitlerini aşmamak için akıllı delay mekanizması
* `FloodWaitError` durumunda otomatik bekleme
* Paralel işlem sayısını kontrol etme

### 9.2 Session Yönetimi
* Oturum bilgilerini güvenli saklama
* Otomatik yeniden bağlanma
* Proxy desteği (opsiyonel)

### 9.3 Güvenlik Önlemleri
* IP değişikliği tespiti
* Şüpheli aktivite algılama
* Otomatik durdurma mekanizması
* Session dosyalarının şifrelenmiş saklanması
* API anahtarlarının güvenli yönetimi
* Rate limiting konfigürasyonu

## 10. Super Fast Filter

### 10.1 Performans Optimizasyonu
* Asenkron işlem yönetimi (`asyncio`)
* Batch processing (toplu işlem)
* Memory-efficient veri yapıları
* Lazy loading (gerektiğinde yükleme)

### 10.2 Caching Stratejileri
* Sonuçları önbellekte tutma
* Veritabanı sorgu optimizasyonu
* UI güncellemelerini minimize etme

### 10.3 Filtreleme Algoritmaları
* Real-time filtreleme
* Regex desteği
* Fuzzy search (bulanık arama)
* Multi-criteria filtering (çoklu kriter filtreleme)

## 11. Dosya İşlemleri

### 11.1 Import İşlemleri
* Excel dosyalarından toplu numara yükleme
* TXT dosyalarından numara listesi okuma
* CSV formatı desteği
* Farklı sütun formatlarını otomatik algılama

### 11.2 Export İşlemleri
* Sonuçları Excel formatında kaydetme
* TXT formatında rapor oluşturma
* Özelleştirilebilir rapor şablonları
* Batch export (toplu dışa aktarma)

## 12. Kullanıcı Arayüzü Gereksinimleri

### 12.1 Ana Pencere
* Modern Material Design tabanlı arayüz
* Responsive layout (otomatik boyutlandırma)
* Dark/Light mode desteği (tema geçişleri)
* Çoklu dil desteği (Türkçe/İngilizce)
* Web benzeri kullanıcı deneyimi
* Hot reload desteği (geliştirme sırasında)

### 12.2 Contact Management Panel
* Modern DataTable ile contact listesi görüntüleme
* Responsive form ile yeni contact ekleme
* Drag & drop ile toplu contact import/export
* Real-time arama ve filtreleme araçları
* Modern kartlar ve animasyonlar

### 12.2.5 Otomatik Numaralar Panel
* Modern dropdown ile ülke kodu seçimi (+90, +1, +44 vb.)
* Checkbox kartları ile operatör seçimi (Turkcell, Vodafone, Türk Telekom vb.)
* Slider ile numara aralığı belirleme (otomatik veya manuel)
* Çoklu operatör seçimi (modern toggle'lar)
* Animasyonlu progress bar ile otomatik numara oluşturma ve kontrol
* DataTable ile sonuçları filtreleme ve export

### 12.3 Number Checker Panel
* Modern FilePicker ile dosya seçimi
* Floating Action Button ile kontrol başlatma/durdurma
* Animasyonlu progress gösterimi (real-time)
* Modern DataTable ile sonuç tablosu
* Drag & drop dosya yükleme

### 12.4 Settings Panel
* Modern form ile API ayarları
* Slider'lar ile anti-robot driver ayarlarını ekle
* Switch'ler ile performans ayarları
* Modern tema seçici (Dark/Light/Auto)
* Animasyonlu ayar geçişleri 