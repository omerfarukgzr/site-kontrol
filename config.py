"""Konfigürasyon ve environment variables"""
import os

# Telegram ayarları
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
KULLANICI_ADI = os.environ.get("TELEGRAM_USERNAME")
# Yetkili kullanıcı chat_id (sadece bu kullanıcı ekle/sil/bildirim komutlarını kullanabilir)
AUTHORIZED_CHAT_ID = os.environ.get("AUTHORIZED_CHAT_ID")
USERNAMES_FILE = "usernames.json"
SETTINGS_FILE = "settings.json"

# Login bilgileri
LOGIN_EMAIL = os.environ.get("LOGIN_EMAIL")
LOGIN_PASSWORD = os.environ.get("LOGIN_PASSWORD")
LOGIN_URL = "https://idare.risale.online/api/auth/login"

# Kontrol edilecek URL'ler
IDARE_URLS = [
    "https://idare.risale.online/",
    "https://idare.risale.online/qa/12261"
]

SABIT_SAYFALAR = [
    "https://risale.online/",
    "https://risale.online/soru-cevap?sort=son-eklenen"
]

KAYNAK_URL = SABIT_SAYFALAR[1]

