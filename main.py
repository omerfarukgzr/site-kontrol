import requests
import random
import os
import sys
from bs4 import BeautifulSoup

# --- AYARLAR (GitHub'dan Gelecek) ---
# Güvenlik için token'ı kodun içine yazmıyoruz, GitHub Ayarlarından çekeceğiz.
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SABIT_SAYFALAR = [
    "https://risale.online/",
    "https://risale.online/soru-cevap?sort=son-eklenen"
]
KAYNAK_URL = "https://risale.online/soru-cevap?sort=son-eklenen"

def telegram_gonder(mesaj):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Token veya Chat ID eksik!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID, 
        'text': mesaj, 
        'parse_mode': 'HTML', 
        'disable_web_page_preview': True
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram hatası: {e}")

def dinamik_linkleri_bul():
    linkler = []
    headers = {'User-Agent': 'Mozilla/5.0 (GitHub Actions Monitor)'}
    try:
        response = requests.get(KAYNAK_URL, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/soru-cevap/' in href and len(href) > 15 and href != "/soru-cevap":
                    tam_link = href if href.startswith("http") else "https://risale.online" + href
                    if tam_link not in linkler and tam_link not in SABIT_SAYFALAR:
                        linkler.append(tam_link)
            if len(linkler) >= 3:
                return random.sample(linkler, 3)
            return linkler
        return []
    except:
        return []

# --- ANA İŞLEM ---
print("Kontrol başlatılıyor...")

dinamik_linkler = dinamik_linkleri_bul()
tum_liste = SABIT_SAYFALAR + dinamik_linkler
hata_listesi = []

headers = {'User-Agent': 'Mozilla/5.0 (GitHub Actions Monitor)'}

for url in tum_liste:
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            hata_listesi.append(f"❌ <b>HATA ({resp.status_code})</b>\n🔗 {url}")
            print(f"HATA: {url}")
        else:
            print(f"OK: {url}")
    except Exception as e:
        hata_listesi.append(f"🚫 <b>ERİŞİM YOK</b>\n🔗 {url}")
        print(f"ÇÖKME: {url}")

# Sadece HATA varsa mesaj atıyoruz.
# GitHub sürekli çalıştığı için "Her şey yolunda" mesajı atarsak seni spamlar.
if len(hata_listesi) > 0:
    ana_mesaj = (
            f"🚨 <b>RİSALE ONLINE ERİŞİM SORUNU!</b>\n"
            f"Kontrol edilen {len(tum_liste)} sayfadan {len(hata_listesi)} tanesi açılmıyor!\n\n"
            + "\n\n".join(hata_listesi)
    )
    telegram_gonder(ana_mesaj)
    # GitHub'a işlemin başarısız olduğunu bildir (Kırmızı çarpı çıkar)
    sys.exit(1) 
else:
    print("✅ Tüm siteler çalışıyor. Sorun yok.")
