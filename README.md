# 🎬 YouTube AI Video Bot

Telegram’da basit komutlarla yapay zeka ile hikaye yazıp, video oluşturup YouTube’a otomatik yükleyen bot.

## ✨ Özellikler

- 📝 **Gemini AI** ile dramatik hikayeler oluştur
- 🎥 **Gemini Veo** ile video üret
- 🎵 **ElevenLabs** ile Türkçe ses ekle
- 📺 **YouTube’a otomatik upload**
- 🧠 **Öğrenme modu** - Bot başlık ve açıklamalarından öğrenir
- ⏱️ **Esnek süre** - 8s, 15s, 30s arasında seç
- 💬 **Sohbet modunda** - Komut değil, doğal metin

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Telegram Bot Token (@BotFather’dan)
- Gemini API Key (ai.google.dev)
- YouTube API Credentials (console.cloud.google.com)
- ElevenLabs API Key (elevenlabs.io) - OPSIYONEL
- Railway hesabı (railway.app)

### Kurulum

1. **Dosyaları indir**
   
   ```
   main.py
   requirements.txt
   Procfile
   ```
1. **GitHub’a yükle**
- Yeni repo oluştur: youtube-bot
- Bu dosyaları push et
1. **Railway’e deploy et**
- railway.app → New Project → Deploy from GitHub
- youtube-bot repo’sunu seç
1. **Environment Variables ekle**
- Railway dashboard → Variables
- Şunları ekle:
  - TELEGRAM_BOT_TOKEN
  - GEMINI_API_KEY
  - YOUTUBE_CREDS_JSON
  - ELEVENLABS_API_KEY (opsiyonel)
1. **Başla**
- Telegram bot’una /start yaz
- Sohbet başlasın!

## 📖 Nasıl Çalışıyor

```
1. Sen: "Uzayda kayıp astronot"
   ↓
2. Bot: "Video süresini seç (8s/15s/30s)"
   ↓
3. Bot: Hikaye oluşturur + video + ses
   ↓
4. Bot: "Başlık önerim: ... Beğendin mi?"
   ↓
5. Sen: ✅ Beğendim (veya ✏️ Düzelt)
   ↓
6. Bot: Açıklama önerir
   ↓
7. Sen: ✅ Onay
   ↓
8. Bot: 🎉 YouTube'a yükler!
```

## 🧠 Öğrenme Modu

Bot her sefer:

- Başlık tercihlerini hatırlar
- Açıklama tarzını öğrenir
- Sonraki videolarda daha iyiye getirir

Örnek:

```
Bot: "Başlık önerim: Uzayın Gizemli Kapısı"
Sen: "Geç, daha dramatik olsun"
Bot: "Peki, öğrendim! Sonraki başlıklar daha dramatik olacak"
```

## 📁 Dosya Yapısı

```
youtube-bot/
├── main.py           # Bot kodu
├── requirements.txt  # Dependencies
├── Procfile         # Railway deployment
├── DEPLOYMENT.md    # Detaylı talimatlar
├── .env.example     # Örnek config
└── learning_data.json # Bot'un öğrendikleri (otomatik)
```

## 🔧 Ortam Değişkenleri

```env
TELEGRAM_BOT_TOKEN    = Telegram bot tokenı
GEMINI_API_KEY        = Google Gemini API key
YOUTUBE_CREDS_JSON    = YouTube API credentials (JSON)
ELEVENLABS_API_KEY    = ElevenLabs API key (opsiyonel)
```

## ⚙️ Ayarlanabilir Seçenekler

Bot kodunda şu şeyleri özelleştirebilirsin:

- **Video kategorisi** - line 223 “categoryId”: “24” (Entertainment)
- **Seslendirme seçimi** - line 163 “voice”: “Bella”
- **Hashtags** - line 135 kısındaki tags listesi
- **Dil** - Türkçe olarak ayarlandı, değiştirebilirsin

## 🐛 Sorun Giderme

**Bot yanıt vermiyor?**

- Railway logs’ı kontrol et
- Environment variables doğru mu?
- Bot token aktif mi?

**YouTube upload hatası?**

- API credentials doğru mu?
- YouTube API enabled mi?
- Quota kalmış mı?

**Video oluşturmuyor?**

- Gemini API key valid mi?
- Rate limit hit mi? (bekle birkaç saat)

## 📞 Destek

Sorunlar için:

1. Railway logs’ı kontrol et
1. .env dosyasını kontrol et
1. API keys’i kontrol et
1. Gemini/YouTube docs’ları kontrol et

## 📜 Lisans

Kişisel kullanım için ücretsiz.

## 🎯 Gelecek Özellikler

- [ ] Sesli komutlar (voice messages)
- [ ] Görüntü yükleme (custom backgrounds)
- [ ] Müzik entegrasyonu
- [ ] Çoklu dil desteği
- [ ] Video scheduling

-----

**Oluşturduğu videonun keyifini çık! 🎬**