"""JSONBin.io üzerinden veri saklama"""
import os
import json
import requests


# JSONBin.io ayarları
JSONBIN_API_KEY = os.environ.get("JSONBIN_API_KEY")
JSONBIN_BIN_ID = os.environ.get("JSONBIN_BIN_ID")
JSONBIN_BASE_URL = "https://api.jsonbin.io/v3/b"


def _jsonbin_oku():
    """JSONBin.io'dan veriyi okur"""
    if not JSONBIN_API_KEY or not JSONBIN_BIN_ID:
        return None
    
    url = f"{JSONBIN_BASE_URL}/{JSONBIN_BIN_ID}/latest"
    headers = {
        "X-Master-Key": JSONBIN_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("record", {})
        else:
            print(f"⚠️ JSONBin okuma hatası: {response.status_code}")
    except Exception as e:
        print(f"❌ JSONBin okuma hatası: {e}")
    
    return None


def _jsonbin_yaz(data):
    """JSONBin.io'ya veri yazar"""
    if not JSONBIN_API_KEY or not JSONBIN_BIN_ID:
        print("❌ JSONBIN_API_KEY veya JSONBIN_BIN_ID eksik!")
        return False
    
    url = f"{JSONBIN_BASE_URL}/{JSONBIN_BIN_ID}"
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": JSONBIN_API_KEY
    }
    
    try:
        response = requests.put(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            print("✅ JSONBin güncellendi")
            return True
        else:
            print(f"❌ JSONBin yazma hatası: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ JSONBin yazma hatası: {e}")
    
    return False


# ============ USERNAMES ============

def usernames_yukle():
    """Username listesini JSONBin.io'dan yükler"""
    data = _jsonbin_oku()
    if data:
        return data.get("usernames", [])
    return []


def usernames_kaydet(usernames_list):
    """Username listesini JSONBin.io'ya kaydeder"""
    data = _jsonbin_oku() or {}
    data["usernames"] = usernames_list
    return _jsonbin_yaz(data)


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


# ============ SETTINGS ============

def ayarlari_yukle():
    """Ayarları JSONBin.io'dan yükler"""
    data = _jsonbin_oku()
    if data:
        return {
            "notifications_enabled": data.get("notifications_enabled", True)
        }
    return {"notifications_enabled": True}


def ayarlari_kaydet(ayarlar):
    """Ayarları JSONBin.io'ya kaydeder"""
    data = _jsonbin_oku() or {}
    data["notifications_enabled"] = ayarlar.get("notifications_enabled", True)
    return _jsonbin_yaz(data)


def bildirim_durumu_al():
    """Bildirim durumunu döner (True/False)"""
    ayarlar = ayarlari_yukle()
    return ayarlar.get("notifications_enabled", True)


def bildirim_durumu_degistir(durum):
    """Bildirim durumunu değiştirir"""
    ayarlar = ayarlari_yukle()
    ayarlar["notifications_enabled"] = durum
    if ayarlari_kaydet(ayarlar):
        durum_metni = "açıldı" if durum else "kapatıldı"
        return True, f"✅ Bildirimler {durum_metni}!"
    else:
        return False, "❌ Ayar kaydetme hatası!"
