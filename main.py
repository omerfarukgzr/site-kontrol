"""Ana giriş noktası"""
import argparse
from telegram_bot import bot_dinle, bot_mesajlari_isle, telegram_gonder
from site_checker import site_kontrol_et


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Site Kontrol Botu')
    parser.add_argument('--bot', action='store_true', help='Bot dinleme modunu başlat (sürekli çalışır)')
    args = parser.parse_args()
    
    if args.bot:
        # Sürekli dinleme modu (lokal geliştirme için)
        bot_dinle()
    else:
        # GitHub Actions modu: Önce bekleyen mesajları işle, sonra site kontrolü yap
        
        # 1. Bekleyen Telegram mesajlarını işle
        bot_mesajlari_isle()
        
        # 2. Site kontrolü yap
        hata_listesi, basarili_sayisi = site_kontrol_et()

        if len(hata_listesi) > 0:
            ana_mesaj = (
                f"🚨 <b>ERİŞİM SORUNU!</b>\n"
                f"{len(hata_listesi)} sayfa açılmadı!\n\n"
                + "\n\n".join(hata_listesi)
            )
            telegram_gonder(ana_mesaj, hata_var_mi=True)
            print(">> ⚠️ Hata raporu (Etiketli) gönderildi.")
        else:
            ok_mesaji = (
                f"✅ <b>SİSTEM STABİL</b>\n"
                f"Kontrol tamamlandı. ({basarili_sayisi} sayfa aktif)"
            )
            telegram_gonder(ok_mesaji, hata_var_mi=False)
            print(">> ✅ OK raporu (Etiketsiz) gönderildi.")
