import requests
import time
import random
from bs4 import BeautifulSoup

# --- KULLANICI AYARLARI ---
TELEGRAM_TOKEN = "7747118685:AAFrpeDFJ2LH9ae7TmVjuVEAusuaEi65ZDI"  # Buraya güncel tokenini yaz
TELEGRAM_CHAT_ID = "5669602367"

# TEST MODU (True ise 15 saniyede bir, False ise 10 dakikada bir çalışır)
TEST_MODU = True

if TEST_MODU:
    KONTROL_SIKLIGI = 15  # 15 Saniye bekle
    OK_MESAJ_ARALIGI = 15  # Her kontrolde mesaj at (Test için)
    print("⚠️ DİKKAT: TEST MODU AÇIK! (15 saniyede bir mesaj atılacak)")
else:
    KONTROL_SIKLIGI = 600  # 10 Dakika
    OK_MESAJ_ARALIGI = 3600  # 1 Saat
    print("✅ CANLI MOD AKTİF. (10 dakikada bir kontrol, 1 saatte bir rapor)")

# --- URL AYARLARI ---
SABIT_SAYFALAR = [
    "https://risale.online/",
    "https://risale.online/soru-cevap?sort=son-eklenen"
]
KAYNAK_URL = "https://risale.online/soru-cevap?sort=son-eklenen"

son_ok_mesaji_zamani = 0


def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    # Çizgi ve Saat
    cizgi = "\n" + "—" * 15
    saat = f"\n🕒 {time.strftime('%H:%M:%S')}"
    son_mesaj = mesaj + cizgi + saat

    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': son_mesaj,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }

    try:
        # Hata yakalamayı açtık, sonucu görelim
        response = requests.post(url, data=payload, timeout=10)

        if response.status_code == 200:
            print(">> 📤 Telegram mesajı başarıyla sunucuya iletildi.")
        else:
            print(f"!! 🛑 TELEGRAM HATASI: {response.status_code}")
            print(f"!! Detay: {response.text}")

    except Exception as e:
        print(f"!! 💥 TELEGRAM GÖNDERİLEMEDİ: {e}")


def dinamik_linkleri_bul():
    linkler = []
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
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


# --- DÖNGÜ BAŞLIYOR ---
print("-" * 50)

while True:
    su_an = time.time()
    hata_listesi = []
    basarili_sayisi = 0

    print(f"\n🔎 Kontrol: {time.strftime('%H:%M:%S')}")

    dinamik_linkler = dinamik_linkleri_bul()
    tum_liste = SABIT_SAYFALAR + dinamik_linkler
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

    for url in tum_liste:
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code != 200:
                hata_listesi.append(f"❌ <b>HATA ({resp.status_code})</b>\n🔗 {url}")
                print(f"   ❌ HATA: {url}")
            else:
                basarili_sayisi += 1
                print(f"   ✅ OK: {url}")
        except Exception as e:
            hata_listesi.append(f"🚫 <b>ERİŞİM YOK</b>\n🔗 {url}")
            print(f"   🚫 ÇÖKME: {url}")

    # --- KARAR VE GÖNDERİM ---
    if len(hata_listesi) > 0:
        ana_mesaj = (
                f"🚨 <b>ERİŞİM SORUNU!</b>\n\n"
                + "\n\n".join(hata_listesi)
        )
        telegram_gonder(ana_mesaj)

    else:
        # Süre kontrolü
        gecen_sure = su_an - son_ok_mesaji_zamani
        if gecen_sure > OK_MESAJ_ARALIGI:
            mesaj = (
                f"✅ <b>DURUM RAPORU</b>\n"
                f"Sistem stabil.\n"
                f"Kontrol edilen: {basarili_sayisi} sayfa."
            )
            telegram_gonder(mesaj)
            son_ok_mesaji_zamani = su_an
        else:
            kalan = int(OK_MESAJ_ARALIGI - gecen_sure)
            print(f">> ⏳ Mesaj için {kalan} saniye bekleniyor...")

    print(f">> 💤 {KONTROL_SIKLIGI} saniye uyku...")
    time.sleep(KONTROL_SIKLIGI)