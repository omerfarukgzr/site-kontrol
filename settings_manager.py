"""Ayarlar yönetimi (bildirim durumu vb.)"""
import os
import json
from config import SETTINGS_FILE


def ayarlari_yukle():
    """Ayarları JSON dosyasından yükler"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except:
            return {'notifications_enabled': True}  # Varsayılan: açık
    return {'notifications_enabled': True}  # Varsayılan: açık


def ayarlari_kaydet(ayarlar):
    """Ayarları JSON dosyasına kaydeder"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(ayarlar, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Ayar kaydetme hatası: {e}")
        return False


def bildirim_durumu_al():
    """Bildirim durumunu döner (True/False)"""
    ayarlar = ayarlari_yukle()
    return ayarlar.get('notifications_enabled', True)


def bildirim_durumu_degistir(durum):
    """Bildirim durumunu değiştirir"""
    ayarlar = ayarlari_yukle()
    ayarlar['notifications_enabled'] = durum
    if ayarlari_kaydet(ayarlar):
        durum_metni = "açıldı" if durum else "kapatıldı"
        return True, f"✅ Bildirimler {durum_metni}!"
    else:
        return False, "❌ Ayar kaydetme hatası!"

