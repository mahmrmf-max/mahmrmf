# 🚀 RAILWAY’E DEPLOY TALIMATLAR

## ADIM 1: Dosyaları Hazırla

1. Bilgisayarında bir klasör aç: “youtube-bot”
1. İçine bu 3 dosyayı kopyala:
- main.py
- requirements.txt
- Procfile

## ADIM 2: GitHub’a Yükle

1. GitHub.com’a git, hesap aç (yoksa)
1. Yeni repository oluştur: “youtube-bot”
1. Dosyaları GitHub’a yükle (veya Git CLI kullan)

## ADIM 3: Railway’e Bağla

1. railway.app’e git
1. “New Project” → “Deploy from GitHub”
1. “youtube-bot” repository’sini seç
1. Deploy et (otomatik başlayacak)

## ADIM 4: Environment Variables Ekle

Railway dashboard’da şu değişkenleri ekle:

```
TELEGRAM_BOT_TOKEN = [Senin Telegram Bot Token'ı]
GEMINI_API_KEY = [Senin Gemini API Key'i]
ELEVENLABS_API_KEY = [Senin ElevenLabs Key'i (opsiyonel)]
YOUTUBE_CREDS_JSON = [Senin YouTube API JSON'u - ÖNEMLİ!]
```

⚠️ YOUTUBE_CREDS_JSON’u nasıl eklemeliysin:

- Indirdiğin JSON dosyasını açıkça text editor’da aç
- İçeriğini TAMAMEN kopyala (Ctrl+A, Ctrl+C)
- Railway’de YOUTUBE_CREDS_JSON değerine yapıştır

## ADIM 5: Başlat

- Railway otomatik restart edecek
- Telegram bot’una /start yaz
- Bot çalışmaya başlayacak!

-----

## 🔧 Sorun Giderme

**Bot yanıt vermiyor mu?**

- Railway logs’a bak (dashboard’da Logs tabı)
- Hatayı gör, düzelt, tekrar deploy et

**YouTube API hatası?**

- JSON doğru mu eki kontrol et
- YouTube API gerçekten enabled mi kontrol et

**Gemini hatası?**

- API key doğru mu
- API’nin quota’sı kalmış mı kontrol et

-----

## 💡 Alternatif: Replit’e Deploy

1. replit.com’a git
1. “Import from GitHub” → youtube-bot
1. Secrets (sol panelde) → Environment variables ekle
1. “Run” tıkla
1. Replit terminal’de otomatik çalışır

-----

## 🎯 Öğrenme Dosyası

Bot “learning_data.json” dosyasında öğrendiklerini kaydeder:

- Başlık tercihlerini
- Açıklama tercihlerini
- Stil notlarını

Bunu silersen bot’un “hafızası” silinir (reset)