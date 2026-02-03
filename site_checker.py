"""Site kontrol işlemleri"""
import requests
import random
import time
from bs4 import BeautifulSoup
from config import LOGIN_EMAIL, LOGIN_PASSWORD, LOGIN_URL, KAYNAK_URL, SABIT_SAYFALAR, IDARE_URLS


def login_ol():
    """Login yapıp session döndürür"""
    if not LOGIN_EMAIL or not LOGIN_PASSWORD:
        print("⚠️ Login bilgileri eksik, login olmadan devam ediliyor...")
        return None
    
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json'
    }
    
    payload = {
        "email": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    }
    
    session = requests.Session()
    try:
        response = session.post(LOGIN_URL, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            print("✅ Login başarılı")
            return session
        else:
            print(f"❌ Login başarısız: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Login hatası: {e}")
        return None


# Geçici ağ/timeout hatalarında yeniden deneme
MAX_RETRIES = 3
RETRY_DELAY_SEC = 2
REQUEST_TIMEOUT = 25

# Gerçek tarayıcı gibi görünmek için (site bot isteklerini engelleyebilir)
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


def dinamik_linkleri_bul():
    """Dinamik linkleri bulur"""
    linkler = []
    headers = BROWSER_HEADERS.copy()
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


def site_kontrol_et():
    """Tüm siteleri kontrol eder ve sonuçları döner"""
    print("🚀 Kontrol başlatılıyor...")

    # Login gerektiren URL'ler için session oluştur
    session = login_ol()
    login_basarili = session is not None
    
    # Login bilgileri kontrolü
    login_bilgileri_eksik = not LOGIN_EMAIL or not LOGIN_PASSWORD
    
    dinamik_linkler = dinamik_linkleri_bul()
    
    # Login başarısızsa veya eksikse, idare paneli URL'lerini kontrol etme
    if login_basarili:
        tum_liste = SABIT_SAYFALAR + dinamik_linkler + IDARE_URLS
    else:
        tum_liste = SABIT_SAYFALAR + dinamik_linkler
        # IDARE_URLS'leri atla
    
    hata_listesi = []
    basarili_sayisi = 0
    idare_paneli_uyarisi = None
    
    # Login durumuna göre uyarı mesajı oluştur
    if not login_basarili:
        if login_bilgileri_eksik:
            idare_paneli_uyarisi = (
                "⚠️ <b>İDARE PANELİ KONTROL EDİLEMEDİ</b>\n\n"
                "🔐 <b>Sebep:</b> Login bilgileri (LOGIN_EMAIL veya LOGIN_PASSWORD) "
                "environment variable'larında tanımlı değil.\n\n"
                "📋 <b>Kontrol edilemeyen sayfalar:</b>\n"
                + "\n".join([f"• {url}" for url in IDARE_URLS])
            )
        else:
            idare_paneli_uyarisi = (
                "⚠️ <b>İDARE PANELİ KONTROL EDİLEMEDİ</b>\n\n"
                "🔐 <b>Sebep:</b> Login işlemi başarısız oldu. "
                "Email veya şifre hatalı olabilir.\n\n"
                "📋 <b>Kontrol edilemeyen sayfalar:</b>\n"
                + "\n".join([f"• {url}" for url in IDARE_URLS])
            )
    
    headers = BROWSER_HEADERS.copy()

    for url in tum_liste:
        for deneme in range(MAX_RETRIES):
            try:
                # Login gerektiren URL'ler için session kullan
                if session and 'idare.risale.online' in url:
                    resp = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
                else:
                    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
                if resp.status_code != 200:
                    if deneme < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY_SEC)
                        continue
                    hata_listesi.append(f"❌ <b>HATA ({resp.status_code})</b>\n🔗 {url}")
                    print(f"HATA: {url}")
                    break
                basarili_sayisi += 1
                print(f"OK: {url}")
                break
            except Exception as e:
                if deneme < MAX_RETRIES - 1:
                    print(f"  ↳ Yeniden denenecek ({deneme + 1}/{MAX_RETRIES}): {url} - {e}")
                    time.sleep(RETRY_DELAY_SEC)
                else:
                    hata_listesi.append(f"🚫 <b>ERİŞİM YOK</b>\n🔗 {url}")
                    print(f"ÇÖKME: {url} - {e}")
                    break

    return hata_listesi, basarili_sayisi, idare_paneli_uyarisi

