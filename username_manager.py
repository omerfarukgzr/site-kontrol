"""Username yönetimi fonksiyonları"""
import os
import json
from config import USERNAMES_FILE


def usernames_yukle():
    """Username listesini JSON dosyasından yükler"""
    if os.path.exists(USERNAMES_FILE):
        try:
            with open(USERNAMES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('usernames', [])
        except:
            return []
    return []


def usernames_kaydet(usernames_list):
    """Username listesini JSON dosyasına kaydeder"""
    try:
        with open(USERNAMES_FILE, 'w', encoding='utf-8') as f:
            json.dump({'usernames': usernames_list}, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Username kaydetme hatası: {e}")
        return False


def username_ekle(username):
    """Username listesine yeni username ekler"""
    if not username:
        return False, "❌ Username boş olamaz!"
    
    # @ işaretini kaldır
    username = username.lstrip('@')
    
    usernames = usernames_yukle()
    if username in usernames:
        return False, f"❌ @{username} zaten listede!"
    
    usernames.append(username)
    if usernames_kaydet(usernames):
        return True, f"✅ @{username} başarıyla eklendi!"
    else:
        return False, "❌ Kaydetme hatası!"


def username_cikar(username):
    """Username listesinden username çıkarır"""
    if not username:
        return False, "❌ Username boş olamaz!"
    
    # @ işaretini kaldır
    username = username.lstrip('@')
    
    usernames = usernames_yukle()
    if username not in usernames:
        return False, f"❌ @{username} listede bulunamadı!"
    
    usernames.remove(username)
    if usernames_kaydet(usernames):
        return True, f"✅ @{username} başarıyla çıkarıldı!"
    else:
        return False, "❌ Kaydetme hatası!"

