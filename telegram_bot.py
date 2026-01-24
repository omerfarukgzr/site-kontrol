"""Telegram bot işlemleri"""
import requests
import time
import sys
from datetime import datetime, timedelta
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, KULLANICI_ADI
from username_manager import usernames_yukle, username_ekle, username_cikar


def telegram_mesaj_gonder(chat_id, mesaj, parse_mode='HTML'):
    """Telegram'a mesaj gönderir"""
    if not TELEGRAM_TOKEN:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': mesaj,
        'parse_mode': parse_mode,
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Hata: {e}")
        return False


def telegram_gonder(mesaj, hata_var_mi=False):
    """Site kontrol sonuçlarını Telegram'a gönderir"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ HATA: Token eksik!")
        sys.exit(1)

    tr_saati = datetime.utcnow() + timedelta(hours=3)
    saat_str = tr_saati.strftime('%H:%M:%S')
    cizgi = "——————————————————"

    # Username listesini yükle ve etiketle
    usernames = usernames_yukle()
    if hata_var_mi and usernames:
        # Tüm username'leri @ ile etiketle
        etiketler = " ".join([f"@{u}" for u in usernames])
        baslik = f"⚠️ {etiketler} DİKKAT!\n"
    elif hata_var_mi and KULLANICI_ADI:
        # Eski yöntem (geriye dönük uyumluluk)
        baslik = f"⚠️ {KULLANICI_ADI} DİKKAT!\n"
    else:
        baslik = ""

    son_hal = f"{baslik}{mesaj}\n\n🕒 {saat_str}\n{cizgi}"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': son_hal,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Hata: {e}")


def bot_komutlari_kaydet():
    """Bot komutlarını Telegram'a kaydeder (otomatik öneri için)"""
    if not TELEGRAM_TOKEN:
        return False
    
    commands = [
        {
            "command": "adduser",
            "description": "Username ekle: /adduser @kullanici"
        },
        {
            "command": "deletuser",
            "description": "Username çıkar: /deletuser @kullanici"
        },
        {
            "command": "userlist",
            "description": "Kayıtlı username'leri listele"
        },
        {
            "command": "help",
            "description": "Yardım mesajını göster"
        }
    ]
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyCommands"
        payload = {"commands": commands}
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('ok', False)
        return False
    except Exception as e:
        print(f"⚠️ Komut kaydetme hatası: {e}")
        return False


def bot_baglanti_testi():
    """Bot'un Telegram API'ye bağlanabildiğini test eder"""
    if not TELEGRAM_TOKEN:
        return False, "TELEGRAM_TOKEN eksik!"
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                bot_username = bot_info.get('username', 'Bilinmiyor')
                return True, f"✅ Bot bağlantısı başarılı! Bot: @{bot_username}"
            else:
                return False, f"❌ API hatası: {data.get('description', 'Bilinmeyen hata')}"
        else:
            return False, f"❌ HTTP hatası: {response.status_code}"
    except Exception as e:
        return False, f"❌ Bağlantı hatası: {e}"


def komut_isle(update):
    """Gelen komutu işler ve cevap döner"""
    if 'message' not in update:
        return None
    
    message = update['message']
    chat_id = message['chat']['id']
    text = message.get('text', '')
    
    # Debug: Gelen mesajı göster
    print(f"📨 Gelen mesaj: {text} (Chat ID: {chat_id})")
    
    # Sadece komutları işle
    if not text.startswith('/'):
        return None
    
    # Komut ve parametreleri ayır
    parts = text.split()
    komut = parts[0].lower()
    
    print(f"🔧 İşlenen komut: {komut}")
    
    if komut == '/start':
        baslangic_mesaji = (
            "👋 <b>Hoş Geldiniz!</b>\n\n"
            "Bu bot site kontrol sistemidir. Hata durumunda kayıtlı kullanıcıları bilgilendirir.\n\n"
            "📋 <b>KOMUTLAR:</b>\n"
            "/adduser @kullanici - Username ekle\n"
            "/deletuser @kullanici - Username çıkar\n"
            "/userlist - Kayıtlı username'leri listele\n"
            "/help - Yardım mesajı\n\n"
            "💡 <i>Not: @ işareti opsiyoneldir</i>"
        )
        telegram_mesaj_gonder(chat_id, baslangic_mesaji)
        return True
    
    elif komut == '/help':
        help_mesaji = (
            "📋 <b>KOMUTLAR</b>\n\n"
            "/adduser @kullanici - Username ekle\n"
            "/deletuser @kullanici - Username çıkar\n"
            "/userlist - Kayıtlı username'leri listele\n"
            "/help - Bu yardım mesajını göster\n\n"
            "💡 <i>Not: @ işareti opsiyoneldir</i>"
        )
        telegram_mesaj_gonder(chat_id, help_mesaji)
        return True
    
    elif komut == '/adduser':
        if len(parts) < 2:
            # Komut seçildi ama username verilmemiş, kullanıcıya örnek göster
            ornek_mesaj = (
                "➕ <b>Username Ekleme</b>\n\n"
                "Kullanım: <code>/adduser @kullanici</code>\n\n"
                "Örnekler:\n"
                "• <code>/adduser @omer</code>\n"
                "• <code>/adduser omer</code>\n\n"
                "💡 <i>@ işareti opsiyoneldir</i>"
            )
            telegram_mesaj_gonder(chat_id, ornek_mesaj)
            return True
        
        username = parts[1]
        basarili, mesaj = username_ekle(username)
        telegram_mesaj_gonder(chat_id, mesaj)
        return True
    
    elif komut == '/deletuser':
        if len(parts) < 2:
            # Komut seçildi ama username verilmemiş, kullanıcıya örnek göster
            ornek_mesaj = (
                "➖ <b>Username Çıkarma</b>\n\n"
                "Kullanım: <code>/deletuser @kullanici</code>\n\n"
                "Örnekler:\n"
                "• <code>/deletuser @omer</code>\n"
                "• <code>/deletuser omer</code>\n\n"
                "💡 <i>@ işareti opsiyoneldir</i>"
            )
            telegram_mesaj_gonder(chat_id, ornek_mesaj)
            return True
        
        username = parts[1]
        basarili, mesaj = username_cikar(username)
        telegram_mesaj_gonder(chat_id, mesaj)
        return True
    
    elif komut == '/userlist':
        usernames = usernames_yukle()
        if usernames:
            liste = "\n".join([f"• @{u}" for u in usernames])
            mesaj = f"📝 <b>Kayıtlı Username'ler:</b>\n\n{liste}\n\nToplam: {len(usernames)}"
        else:
            mesaj = "📝 Henüz kayıtlı username yok.\n\n/adduser @kullanici ile ekleyebilirsiniz."
        telegram_mesaj_gonder(chat_id, mesaj)
        return True
    
    # Bilinmeyen komut
    elif text.startswith('/'):
        telegram_mesaj_gonder(chat_id, "❌ Bilinmeyen komut!\n\n/help ile tüm komutları görebilirsiniz.")
        return True
    
    return None


def bot_dinle():
    """Telegram bot'unu dinler ve komutları işler"""
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN eksik!")
        print("💡 Environment variable olarak ayarlayın: export TELEGRAM_TOKEN='your_token'")
        sys.exit(1)
    
    print("🤖 Bot dinleme modu başlatılıyor...")
    
    # Bot bağlantı testi
    basarili, mesaj = bot_baglanti_testi()
    print(mesaj)
    if not basarili:
        print("❌ Bot bağlantısı başarısız! Lütfen TELEGRAM_TOKEN'i kontrol edin.")
        sys.exit(1)
    
    # Bot komutlarını kaydet (otomatik öneri için)
    if bot_komutlari_kaydet():
        print("✅ Bot komutları kaydedildi (otomatik öneri aktif)")
    else:
        print("⚠️ Bot komutları kaydedilemedi (otomatik öneri çalışmayabilir)")
    
    print("💡 Bot'u durdurmak için Ctrl+C kullanın")
    print("📱 Telegram'da bot'unuza komut gönderebilirsiniz...")
    print("💡 İpucu: '/' yazıp komutları görebilirsiniz")
    print("-" * 50)
    
    last_update_id = 0
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
            params = {
                'offset': last_update_id + 1,
                'timeout': 30
            }
            
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and data.get('result'):
                    updates = data['result']
                    if updates:
                        print(f"📬 {len(updates)} yeni mesaj alındı")
                    for update in updates:
                        last_update_id = update['update_id']
                        komut_isle(update)
                elif response.status_code != 200:
                    print(f"⚠️ API yanıt hatası: {response.status_code}")
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n👋 Bot durduruluyor...")
            break
        except Exception as e:
            print(f"❌ Hata: {e}")
            time.sleep(5)

