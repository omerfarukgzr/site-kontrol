"""Site kontrol işlemleri"""
import requests
import random
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


def dinamik_linkleri_bul():
    """Dinamik linkleri bulur"""
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


def site_kontrol_et():
    """Tüm siteleri kontrol eder ve sonuçları döner"""
    print("🚀 Kontrol başlatılıyor...")

    # Login gerektiren URL'ler için session oluştur
    session = login_ol()
    
    dinamik_linkler = dinamik_linkleri_bul()
    tum_liste = SABIT_SAYFALAR + dinamik_linkler + IDARE_URLS
    
    hata_listesi = []
    basarili_sayisi = 0
    headers = {'User-Agent': 'Mozilla/5.0 (GitHub Actions Monitor)'}

    for url in tum_liste:
        try:
            # Login gerektiren URL'ler için session kullan
            if session and 'idare.risale.online' in url:
                resp = session.get(url, headers=headers, timeout=20)
            else:
                resp = requests.get(url, headers=headers, timeout=20)
            
            if resp.status_code != 200:
                hata_listesi.append(f"❌ <b>HATA ({resp.status_code})</b>\n🔗 {url}")
                print(f"HATA: {url}")
            else:
                basarili_sayisi += 1
                print(f"OK: {url}")
        except Exception as e:
            hata_listesi.append(f"🚫 <b>ERİŞİM YOK</b>\n🔗 {url}")
            print(f"ÇÖKME: {url} - {e}")

    return hata_listesi, basarili_sayisi

