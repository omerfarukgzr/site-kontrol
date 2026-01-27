# Site Kontrol Botu

Otomatik site izleme ve Telegram bildirim sistemi. Belirlenen web sitelerini düzenli olarak kontrol eder ve erişim sorunlarında Telegram üzerinden bildirim gönderir.

## 🎯 Özellikler

- ✅ **Otomatik Site Kontrolü**: Belirlenen URL'leri düzenli olarak kontrol eder
- 📱 **Telegram Bildirimleri**: Hata durumlarında Telegram üzerinden anında bildirim
- 🤖 **Telegram Bot Arayüzü**: Komutlar ile kullanıcı yönetimi ve ayarlar
- 🔐 **Giriş Gerektiren Sayfalar**: Admin paneli gibi giriş gerektiren sayfaları kontrol edebilir
- 🔗 **Dinamik Link Keşfi**: Kaynak sayfadan otomatik olarak dinamik linkler bulur
- ☁️ **Bulut Depolama**: JSONBin.io üzerinden veri saklama
- ⚙️ **Bildirim Yönetimi**: Bildirimleri açıp kapatma özelliği
- 👥 **Kullanıcı Etiketleme**: Hata durumlarında kayıtlı kullanıcıları etiketler

## 📋 Gereksinimler

- Python 3.9+
- Telegram Bot Token
- JSONBin.io API Key (opsiyonel, veri depolama için)

## 🚀 Kurulum

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/hayrat/site-kontrol.git
cd site-kontrol
```

### 2. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 3. Environment Variables Ayarlayın

Aşağıdaki environment variable'ları ayarlayın:

```bash
export TELEGRAM_TOKEN="your_telegram_bot_token"
export TELEGRAM_CHAT_ID="your_telegram_chat_id"
export AUTHORIZED_CHAT_ID="your_authorized_chat_id"
export LOGIN_EMAIL="your_login_email"  # Opsiyonel
export LOGIN_PASSWORD="your_login_password"  # Opsiyonel
export JSONBIN_API_KEY="your_jsonbin_api_key"  # Opsiyonel
export JSONBIN_BIN_ID="your_jsonbin_bin_id"  # Opsiyonel
```

### 4. GitHub Actions Secrets Ayarlayın

GitHub Actions için aşağıdaki secrets'ları ekleyin:

- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`
- `AUTHORIZED_CHAT_ID`
- `LOGIN_EMAIL` (opsiyonel)
- `LOGIN_PASSWORD` (opsiyonel)
- `JSONBIN_API_KEY` (opsiyonel)
- `JSONBIN_BIN_ID` (opsiyonel)

## 💻 Kullanım

### Lokal Geliştirme (Bot Dinleme Modu)

Telegram bot'unu lokal olarak dinlemek için:

```bash
python main.py --bot
```

Bu modda bot sürekli çalışır ve Telegram mesajlarını dinler.

### GitHub Actions Modu

Normal modda (GitHub Actions için):

```bash
python main.py
```

Bu modda:
1. Bekleyen Telegram mesajları işlenir
2. Site kontrolü yapılır
3. Sonuçlar Telegram'a gönderilir

## 🤖 Telegram Bot Komutları

Bot'unuzu Telegram'da kullanmak için aşağıdaki komutları kullanabilirsiniz:

### Kullanıcı Yönetimi

- `/ekle @kullanici` - Username ekle (yetkili kullanıcılar için)
- `/sil @kullanici` - Username çıkar (yetkili kullanıcılar için)
- `/liste` - Kayıtlı username'leri listele

### Bildirim Yönetimi

- `/bildirimac` - Bildirimleri aç (yetkili kullanıcılar için)
- `/bildirimkapat` - Bildirimleri kapat (yetkili kullanıcılar için)

### Yardım

- `/start` veya `/basla` - Başlangıç mesajı
- `/yardim` - Yardım mesajı

**Not:** `@` işareti opsiyoneldir. `/ekle omer` ve `/ekle @omer` aynı şekilde çalışır.

## 📁 Proje Yapısı

```
site-kontrol/
├── main.py                 # Ana giriş noktası
├── config.py               # Konfigürasyon ve environment variables
├── site_checker.py         # Site kontrol işlemleri
├── telegram_bot.py         # Telegram bot işlemleri
├── github_storage.py        # JSONBin.io veri saklama
├── username_manager.py     # Username yönetimi (yerel)
├── settings_manager.py      # Ayarlar yönetimi (yerel)
├── requirements.txt         # Python bağımlılıkları
└── .github/
    └── workflows/
        └── main.yml         # GitHub Actions workflow
```

## ⚙️ Konfigürasyon

### Kontrol Edilecek URL'ler

`config.py` dosyasında kontrol edilecek URL'ler tanımlanmıştır:

- **SABIT_SAYFALAR**: Her zaman kontrol edilen sayfalar
- **IDARE_URLS**: Admin paneli sayfaları (login gerektirir)
- **KAYNAK_URL**: Dinamik linklerin bulunacağı kaynak sayfa

### Bildirim Ayarları

- Bildirimler varsayılan olarak açıktır
- `/bildirimkapat` komutu ile kapatılabilir
- Bildirimler kapalıyken hata olsa bile mesaj gönderilmez

## 🔄 GitHub Actions Entegrasyonu

Proje GitHub Actions ile otomatik çalışacak şekilde yapılandırılmıştır. Workflow şu şekilde çalışır:

1. `repository_dispatch` event'i ile tetiklenir
2. Site kontrolü yapılır
3. Sonuçlar Telegram'a gönderilir

**Not:** Workflow'u düzenli çalıştırmak için harici bir cron servisi veya GitHub Actions schedule kullanmanız gerekebilir.

## 📝 Özellikler Detayı

### Site Kontrolü

- Her URL için HTTP istekleri gönderilir
- Status code kontrolü yapılır
- Timeout süresi: 20 saniye
- Hata durumunda detaylı hata mesajı oluşturulur

### Login Desteği

- Admin paneli sayfaları için login desteği
- Session yönetimi ile giriş yapılır
- Login başarısızsa uyarı mesajı gönderilir

### Dinamik Link Keşfi

- Kaynak sayfadan otomatik link bulma
- Rastgele 3 link seçilir ve kontrol edilir
- Her çalıştırmada farklı linkler kontrol edilir

### Kullanıcı Etiketleme

- Hata durumunda kayıtlı kullanıcılar etiketlenir
- Başarılı durumda etiketleme yapılmaz
- Username listesi JSONBin.io'da saklanır

## 🛠️ Geliştirme

### Lokal Test

```bash
# Bot dinleme modu
python main.py --bot

# Normal mod (site kontrolü)
python main.py
```