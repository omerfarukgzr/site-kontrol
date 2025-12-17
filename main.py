import requests
import random
import os
import sys
from bs4 import BeautifulSoup
# datetime kütüphanesini kaldırdık çünkü artık saate bakmıyoruz.

# --- AYARLAR ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SABIT_SAYFALAR = [
    "https://risale.online/",
    "https://risale.online/soru-cevap?sort=son-eklenen"
]
KAYNAK_URL = "https://risale.online/soru-cevap?sort=son-eklenen"

def telegram_gonder(mesaj):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Token veya Chat ID eksik! Mesaj gönderilemedi.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID, 
        'text': mesaj, 
        'parse_mode': 'HTML', 
        'disable_web_page_preview': True
    }
    try:
        requests.post(url, data=payload, timeout=10)
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
if __name__ == "__main__":
    print("🚀 Kontrol başlatılıyor...")

    dinamik_linkler = dinamik_linkleri_bul()
    tum_liste = SABIT_SAYFALAR + dinamik_linkler
    hata_listesi = []
    basarili_sayisi = 0

    headers = {'User-Agent': 'Mozilla/5.0 (GitHub Actions Monitor)'}

    for url in tum_liste:
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code != 200:
                hata_listesi.append(f"❌ <b>HATA ({resp.status_code})</b>\n🔗 {url}")
                print(f"HATA: {url}")
            else:
                basarili_sayisi += 1
                print(f"OK: {url}")
        except Exception as e:
            hata_listesi.append(f"🚫 <b>ERİŞİM YOK</b>\n🔗 {url}")
            print(f"ÇÖKME: {url}")

    # --- RAPORLAMA (Her Seferinde Mesaj Atacak) ---

    if len(hata_listesi) > 0:
        # HATA VARSA
        ana_mesaj = (
                f"🚨 <b>ERİŞİM SORUNU!</b>\n"
                f"{len(hata_listesi)} sayfa açılmadı!\n\n"
                + "\n\n".join(hata_listesi)
        )
        telegram_gonder(ana_mesaj)
        sys.exit(1) # Hata koduyla çık
    else:
        # HATA YOKSA (Artık her 10 dakikada bir bu mesaj gelir)
        ok_mesaji = (
            f"✅ <b>SİSTEM STABİL</b>\n"
            f"10 dakikalık kontrol tamamlandı.\n"
            f"Taranan Sayfa: {basarili_sayisi}\n"
            f"Durum: Sorun Yok."
        )
        telegram_gonder(ok_mesaji)
        print(">> ✅ OK raporu gönderildi.")
