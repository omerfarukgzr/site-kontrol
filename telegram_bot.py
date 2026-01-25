"""Telegram bot işlemleri"""
import requests
import time
import sys
from datetime import datetime, timedelta
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, KULLANICI_ADI, AUTHORIZED_CHAT_ID
from username_manager import usernames_yukle, username_ekle, username_cikar
from settings_manager import bildirim_durumu_al, bildirim_durumu_degistir


def telegram_mesaj_gonder(chat_id, mesaj, parse_mode='HTML', reply_to_message_id=None):
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
    
    # Mesaja yanıt olarak gönder (alıntı)
    if reply_to_message_id:
        payload['reply_to_message_id'] = reply_to_message_id
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Hata: {e}")
        return False


def telegram_gonder(mesaj, hata_var_mi=False):
    """Site kontrol sonuçlarını Telegram'a gönderir"""
    # Bildirim durumunu kontrol et
    if not bildirim_durumu_al():
        print("🔕 Bildirimler kapalı, mesaj gönderilmedi.")
        return
    
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
            "command": "ekle",
            "description": "👤 Username ekle: /ekle @kullanici"
        },
        {
            "command": "sil",
            "description": "👤 Username çıkar: /sil @kullanici"
        },
        {
            "command": "liste",
            "description": "👤 Kayıtlı username'leri listele"
        },
        {
            "command": "bildirimac",
            "description": "🔔 Bildirimleri aç"
        },
        {
            "command": "bildirimkapat",
            "description": "🔔 Bildirimleri kapat"
        },
        {
            "command": "yardim",
            "description": "❓ Yardım mesajını göster"
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


def yetki_kontrol(chat_id):
    """Kullanıcının yetkili olup olmadığını kontrol eder"""
    if not AUTHORIZED_CHAT_ID:
        # Eğer AUTHORIZED_CHAT_ID tanımlı değilse, herkese izin ver (geriye dönük uyumluluk)
        return True
    return str(chat_id) == str(AUTHORIZED_CHAT_ID)


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
    message_id = message.get('message_id')  # Alıntı için mesaj ID'si
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
    
    # Komut normalizasyonu (Türkçe komutlar)
    komut_normalize = {
        '/start': 'start',
        '/basla': 'start',
        '/başla': 'start',
        '/yardim': 'help',
        '/yardım': 'help',
        '/ekle': 'adduser',
        '/sil': 'deletuser',
        '/liste': 'userlist',
        '/bildirimac': 'notify_on',
        '/bildirimkapat': 'notify_off',
    }
    
    # Komutu normalize et
    normalized_komut = komut_normalize.get(komut, komut[1:])  # / işaretini kaldır
    
    if normalized_komut == 'start':
        baslangic_mesaji = (
            "👋 <b>Hoş Geldiniz!</b>\n\n"
            "Bu bot site kontrol sistemidir. Hata durumunda kayıtlı kullanıcıları bilgilendirir.\n\n"
            "📋 <b>KOMUTLAR:</b>\n\n"
            "👤 <b>Username Yönetimi:</b>\n"
            "/ekle @kullanici - Username ekle\n"
            "/sil @kullanici - Username çıkar\n"
            "/liste - Kayıtlı username'leri listele\n\n"
            "🔔 <b>Bildirimler:</b>\n"
            "/bildirimac - Bildirimleri aç\n"
            "/bildirimkapat - Bildirimleri kapat\n\n"
            "❓ <b>Yardım:</b>\n"
            "/yardim - Yardım mesajı\n\n"
            "💡 <i>Not: @ işareti opsiyoneldir</i>"
        )
        telegram_mesaj_gonder(chat_id, baslangic_mesaji, reply_to_message_id=message_id)
        return True
    
    elif normalized_komut == 'help':
        help_mesaji = (
            "📋 <b>KOMUTLAR</b>\n\n"
            "👤 <b>Username Yönetimi:</b>\n"
            "• /ekle @kullanici - Username ekle\n"
            "• /sil @kullanici - Username çıkar\n"
            "• /liste - Kayıtlı username'leri listele\n\n"
            "🔔 <b>Bildirimler:</b>\n"
            "• /bildirimac - Bildirimleri aç\n"
            "• /bildirimkapat - Bildirimleri kapat\n\n"
            "❓ <b>Yardım:</b>\n"
            "• /yardim - Yardım mesajı\n\n"
            "💡 <i>Not: @ işareti opsiyoneldir</i>"
        )
        telegram_mesaj_gonder(chat_id, help_mesaji, reply_to_message_id=message_id)
        return True
    
    elif normalized_komut == 'adduser':
        # Yetki kontrolü
        if not yetki_kontrol(chat_id):
            telegram_mesaj_gonder(chat_id, "❌ Bu komutu kullanmak için yetkiniz bulunmamaktadır.", reply_to_message_id=message_id)
            return True
        
        if len(parts) < 2:
            # Komut seçildi ama username verilmemiş, kullanıcıya örnek göster
            ornek_mesaj = (
                "➕ <b>Username Ekleme</b>\n\n"
                "Kullanım: <code>/ekle @kullanici</code>\n\n"
                "Örnekler:\n"
                "• <code>/ekle @omer</code>\n"
                "• <code>/ekle omer</code>\n\n"
                "💡 <i>@ işareti opsiyoneldir</i>"
            )
            telegram_mesaj_gonder(chat_id, ornek_mesaj, reply_to_message_id=message_id)
            return True
        
        username = parts[1]
        basarili, mesaj = username_ekle(username)
        telegram_mesaj_gonder(chat_id, mesaj, reply_to_message_id=message_id)
        return True
    
    elif normalized_komut == 'deletuser':
        # Yetki kontrolü
        if not yetki_kontrol(chat_id):
            telegram_mesaj_gonder(chat_id, "❌ Bu komutu kullanmak için yetkiniz bulunmamaktadır.", reply_to_message_id=message_id)
            return True
        
        if len(parts) < 2:
            # Komut seçildi ama username verilmemiş, kullanıcıya örnek göster
            ornek_mesaj = (
                "➖ <b>Username Çıkarma</b>\n\n"
                "Kullanım: <code>/sil @kullanici</code>\n\n"
                "Örnekler:\n"
                "• <code>/sil @omer</code>\n"
                "• <code>/sil omer</code>\n\n"
                "💡 <i>@ işareti opsiyoneldir</i>"
            )
            telegram_mesaj_gonder(chat_id, ornek_mesaj, reply_to_message_id=message_id)
            return True
        
        username = parts[1]
        basarili, mesaj = username_cikar(username)
        telegram_mesaj_gonder(chat_id, mesaj, reply_to_message_id=message_id)
        return True
    
    elif normalized_komut == 'userlist':
        usernames = usernames_yukle()
        if usernames:
            liste = "\n".join([f"• @{u}" for u in usernames])
            mesaj = f"📝 <b>Kayıtlı Username'ler:</b>\n\n{liste}\n\nToplam: {len(usernames)}"
        else:
            mesaj = "📝 Henüz kayıtlı username yok.\n\n/ekle @kullanici ile ekleyebilirsiniz."
        telegram_mesaj_gonder(chat_id, mesaj, reply_to_message_id=message_id)
        return True
    
    elif normalized_komut == 'notify_on':
        # Yetki kontrolü
        if not yetki_kontrol(chat_id):
            telegram_mesaj_gonder(chat_id, "❌ Bu komutu kullanmak için yetkiniz bulunmamaktadır.", reply_to_message_id=message_id)
            return True
        
        # Direkt bildirim aç komutu
        basarili, mesaj = bildirim_durumu_degistir(True)
        telegram_mesaj_gonder(chat_id, mesaj, reply_to_message_id=message_id)
        return True
    
    elif normalized_komut == 'notify_off':
        # Yetki kontrolü
        if not yetki_kontrol(chat_id):
            telegram_mesaj_gonder(chat_id, "❌ Bu komutu kullanmak için yetkiniz bulunmamaktadır.", reply_to_message_id=message_id)
            return True
        
        # Direkt bildirim kapat komutu
        basarili, mesaj = bildirim_durumu_degistir(False)
        telegram_mesaj_gonder(chat_id, mesaj, reply_to_message_id=message_id)
        return True
    
    # Bilinmeyen komut
    elif text.startswith('/'):
        telegram_mesaj_gonder(chat_id, "❌ Bilinmeyen komut!\n\n/help ile tüm komutları görebilirsiniz.", reply_to_message_id=message_id)
        return True
    
    return None


def bot_mesajlari_isle():
    """Bekleyen Telegram mesajlarını tek seferlik işler (GitHub Actions için)"""
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN eksik!")
        return 0
    
    print("📬 Bekleyen mesajlar kontrol ediliyor...")
    
    # Bot komutlarını kaydet (otomatik öneri için)
    bot_komutlari_kaydet()
    
    islenen_mesaj = 0
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params = {
            'timeout': 5  # Kısa timeout, bekleyen mesajları al
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('result'):
                updates = data['result']
                if updates:
                    print(f"📬 {len(updates)} bekleyen mesaj bulundu")
                    for update in updates:
                        komut_isle(update)
                        islenen_mesaj += 1
                    
                    # Son mesajı işaretleyip sil (offset ile)
                    last_update_id = updates[-1]['update_id']
                    # Mesajları temizle (acknowledge)
                    requests.get(url, params={'offset': last_update_id + 1, 'timeout': 1}, timeout=5)
                    print(f"✅ {islenen_mesaj} mesaj işlendi")
                else:
                    print("📭 Bekleyen mesaj yok")
        else:
            print(f"⚠️ API yanıt hatası: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Mesaj işleme hatası: {e}")
    
    return islenen_mesaj


def bot_dinle():
    """Telegram bot'unu dinler ve komutları işler (sürekli çalışan mod)"""
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

