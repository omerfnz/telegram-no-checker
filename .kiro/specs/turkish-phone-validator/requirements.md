# Requirements Document

## Introduction

Bu uygulama, +90 ile başlayan Türk cep telefonu numaralarını rastgele oluşturup Telegram'da kayıtlı olup olmadığını kontrol eden bir Python masaüstü uygulamasıdır. Kontrol edilen numaralar SQLite3 veritabanında saklanır ve tekrar kontrol edilmez. Kullanıcı geçerli veya geçersiz numaraları export edebilir.

## Requirements

### Requirement 1

**User Story:** Bir kullanıcı olarak, rastgele Türk telefon numaraları oluşturmak istiyorum, böylece Telegram'da kayıtlı olanları bulabilirim.

#### Acceptance Criteria

1. WHEN uygulama başlatıldığında THEN sistem +90 ile başlayan geçerli Türk telefon numarası formatında rastgele numaralar oluşturabilir SHOULD
2. WHEN numara oluşturulduğunda THEN sistem +90 5XX XXX XX XX formatında (X rakam) geçerli numaralar üretir SHALL
3. WHEN numara oluşturulduğunda THEN sistem Türk operatör kodlarını (50X, 51X, 52X, 53X, 54X, 55X, 559) kullanır SHALL

### Requirement 2

**User Story:** Bir kullanıcı olarak, oluşturulan numaraların Telegram'da kayıtlı olup olmadığını kontrol etmek istiyorum, böylece geçerli hesapları bulabilirim.

#### Acceptance Criteria

1. WHEN bir numara kontrol edildiğinde THEN sistem MTProto (Telethon/Pyrogram) kullanarak numaranın kayıtlı olup olmadığını kontrol eder SHALL
2. WHEN Telegram kontrolü yapıldığında THEN sistem numaranın durumunu (kayıtlı/kayıtlı değil) belirler SHALL
3. WHEN kontrol tamamlandığında THEN sistem sonucu veritabanına kaydeder SHALL
4. IF bir numara daha önce kontrol edilmişse THEN sistem o numarayı tekrar kontrol etmez SHALL
5. WHEN API istekleri gönderildiğinde THEN sistem her istek arasında 2-5 saniye rastgele bekleme yapar SHALL
6. WHEN rate limiting uygulandığında THEN sistem insan benzeri davranış sergiler SHALL

### Requirement 3

**User Story:** Bir kullanıcı olarak, kontrol edilen numaraları kalıcı olarak saklamak istiyorum, böylece aynı numarayı tekrar kontrol etmem.

#### Acceptance Criteria

1. WHEN uygulama başlatıldığında THEN sistem SQLite3 veritabanı oluşturur veya mevcut olanı açar SHALL
2. WHEN bir numara kontrol edildiğinde THEN sistem numarayı, durumunu ve kontrol tarihini veritabanına kaydeder SHALL
3. WHEN numara kontrol edilmeden önce THEN sistem o numaranın daha önce kontrol edilip edilmediğini veritabanından sorgular SHALL
4. WHEN veritabanı sorgulandığında THEN sistem duplicate kontrolleri önler SHALL

### Requirement 4

**User Story:** Bir kullanıcı olarak, kontrol sonuçlarını export edebilmek istiyorum, böylece verileri başka yerlerde kullanabilirim.

#### Acceptance Criteria

1. WHEN kullanıcı export işlemi başlattığında THEN sistem geçerli numaraları ayrı bir dosyaya export eder SHALL
2. WHEN kullanıcı export işlemi başlattığında THEN sistem geçersiz numaraları ayrı bir dosyaya export eder SHALL
3. WHEN export yapıldığında THEN sistem CSV, JSON ve Excel formatlarında dosya oluşturur SHALL
4. WHEN export dosyası oluşturulduğunda THEN dosya numara, durum ve kontrol tarihi bilgilerini içerir SHALL

### Requirement 5

**User Story:** Bir kullanıcı olarak, kullanıcı dostu bir masaüstü arayüzü istiyorum, böylece uygulamayı kolayca kullanabilirim.

#### Acceptance Criteria

1. WHEN uygulama açıldığında THEN sistem CustomTkinter ile Windows uyumlu modern bir GUI arayüzü gösterir SHALL
2. WHEN arayüz gösterildiğinde THEN kullanıcı kontrol işlemini başlatabilir, durdurabilir SHALL
3. WHEN kontrol devam ederken THEN sistem anlık durumu (kontrol edilen numara sayısı, bulunan geçerli/geçersiz sayısı) gösterir SHALL
4. WHEN kullanıcı export butonuna tıkladığında THEN sistem dosya kaydetme dialogu açar SHALL
5. WHEN işlem devam ederken THEN sistem progress bar veya benzer görsel feedback sağlar SHALL
6. WHEN arayüz yüklendiğinde THEN sistem dark mode desteği sunar SHALL
7. WHEN kullanıcı ayarlara girdiğinde THEN sistem Telegram API key girişi için alan sağlar SHALL

### Requirement 6

**User Story:** Bir kullanıcı olarak, uygulamanın güvenli ve kararlı çalışmasını istiyorum, böylece veri kaybı yaşamam.

#### Acceptance Criteria

1. WHEN Telegram API hatası oluştuğunda THEN sistem hatayı yakalar ve uygulamayı çökertmez SHALL
2. WHEN ağ bağlantısı kesildiğinde THEN sistem kullanıcıyı bilgilendirir ve işlemi duraklatır SHALL
3. WHEN veritabanı hatası oluştuğunda THEN sistem hatayı loglar ve kullanıcıyı bilgilendirir SHALL
4. WHEN uygulama kapatıldığında THEN sistem mevcut işlemleri güvenli şekilde sonlandırır SHALL
###
 Requirement 7

**User Story:** Bir geliştirici olarak, temiz ve sürdürülebilir kod yapısı istiyorum, böylece uygulama kolayca geliştirilebilir ve bakımı yapılabilir.

#### Acceptance Criteria

1. WHEN kod yazıldığında THEN sistem MVVM (Model-View-ViewModel) mimarisini takip eder SHALL
2. WHEN sınıflar oluşturulduğunda THEN her sınıf tek sorumluluk prensibine uyar SHALL
3. WHEN UI katmanı geliştirildiğinde THEN business logic'ten tamamen ayrılır SHALL
4. WHEN kod organize edildiğinde THEN sistem katmanlı mimari kullanır SHALL#
## Requirement 8

**User Story:** Bir kullanıcı olarak, numaraları isim ve numara ile birlikte kaydetmek istiyorum, böylece kişilerimizi organize edebilirim.

#### Acceptance Criteria

1. WHEN bir numara geçerli bulunduğunda THEN sistem kullanıcıdan isim girişi isteyebilir SHALL
2. WHEN numara kaydedildiğinde THEN sistem isim ve numara bilgisini birlikte saklar SHALL
3. WHEN kayıtlı numaralar görüntülendiğinde THEN sistem isim ve numara bilgisini birlikte gösterir SHALL
4. WHEN arama yapıldığında THEN sistem hem isim hem numara ile arama yapabilir SHALL

### Requirement 9

**User Story:** Bir kullanıcı olarak, toplu numara listelerini kontrol etmek istiyorum, böylece büyük veri setlerini hızlıca işleyebilirim.

#### Acceptance Criteria

1. WHEN kullanıcı dosya yüklediğinde THEN sistem CSV, TXT veya Excel formatındaki numara listelerini okur SHALL
2. WHEN liste yüklendiğinde THEN sistem tüm numaraları sırayla kontrol eder SHALL
3. WHEN toplu kontrol yapıldığında THEN sistem progress durumunu gösterir SHALL
4. WHEN liste işlendiğinde THEN sistem geçerli/geçersiz numaraları ayrı ayrı gösterir SHALL

### Requirement 10

**User Story:** Bir kullanıcı olarak, sonuçları farklı formatlarda export etmek istiyorum, böylece CRM sistemlerime entegre edebilirim.

#### Acceptance Criteria

1. WHEN export yapıldığında THEN sistem Excel (.xlsx) formatında dosya oluşturur SHALL
2. WHEN export yapıldığında THEN sistem TXT formatında dosya oluşturur SHALL
3. WHEN export yapıldığında THEN sistem JSON formatında dosya oluşturur SHALL
4. WHEN export dosyası oluşturulduğunda THEN dosya isim, numara, durum ve tarih bilgilerini içerir SHALL

### Requirement 11

**User Story:** Bir kullanıcı olarak, anti-robot koruması istiyorum, böylece hesabım güvende kalır ve işlemler kesintisiz devam eder.

#### Acceptance Criteria

1. WHEN API istekleri gönderildiğinde THEN sistem insan benzeri davranış patterns kullanır SHALL
2. WHEN çok fazla istek gönderildiğinde THEN sistem otomatik olarak bekleme süresini artırır SHALL
3. WHEN Telegram tarafından rate limit uyarısı geldiğinde THEN sistem işlemi duraklatır ve bekler SHALL
4. WHEN anti-robot modu aktifken THEN sistem rastgele user-agent ve session bilgileri kullanır SHALL

### Requirement 12

**User Story:** Bir kullanıcı olarak, süper hızlı filtreleme istiyorum, böylece büyük hacimli numaraları verimli şekilde işleyebilirim.

#### Acceptance Criteria

1. WHEN çoklu numara kontrolü yapıldığında THEN sistem paralel işleme kullanır SHALL
2. WHEN filtreleme yapıldığında THEN sistem optimize edilmiş algoritma kullanır SHALL
3. WHEN büyük listeler işlendiğinde THEN sistem memory-efficient yaklaşım kullanır SHALL
4. WHEN hız optimizasyonu yapıldığında THEN sistem veritabanı sorgularını optimize eder SHALL### Re
quirement 13

**User Story:** Bir kullanıcı olarak, paralel işleme ayarlarını kontrol etmek istiyorum, böylece ban riskini minimize edebilirim.

#### Acceptance Criteria

1. WHEN uygulama başlatıldığında THEN sistem güvenli default paralel işleme değeri (2-3 thread) kullanır SHALL
2. WHEN kullanıcı ayarlara girdiğinde THEN sistem paralel thread sayısını değiştirme seçeneği sunar SHALL
3. WHEN paralel ayarlar değiştirildiğinde THEN sistem risk seviyesi hakkında bilgi verir SHALL
4. WHEN yüksek thread sayısı seçildiğinde THEN sistem kullanıcıyı ban riski konusunda uyarır SHALL
5. WHEN ayarlar kaydedildiğinde THEN sistem yeni değerleri SQLite3 veritabanında saklar SHALL