# BASIT BOT - DEPLOYMENT TALİMATI

## ⚠️ ÖNEMLİ

Eski dosyaları silebilirsin:

- ❌ main.py (ESKİ - HATA VAR)
- ❌ requirements.txt (ESKİ)
- ✅ Procfile (AYNI KALABILIR)

## 🔄 YENİ DOSYALARI YÜKLE

### 1️⃣ GitHub’da Eski main.py’yi SİL

1. Repo → main.py → Delete
1. Commit

### 2️⃣ Yeni main.py’yi YÜKLE

1. Repo → Add file → Upload files
1. `main_new.py` dosyasını seç
1. **Dosya adını değiştir:** `main_new.py` → `main.py`
1. Commit

### 3️⃣ requirements.txt’i GÜNCELLE

1. Repo → requirements.txt → Edit
1. TÜM İÇERİĞİ SİL
1. YENİ İÇERİĞİ YAPISTIR:

```
python-telegram-bot==20.7
google-generativeai==0.4.0
python-dotenv==1.0.0
```

1. Commit

### 4️⃣ Procfile AYNI KALABILIR

- VEYA `worker: python main.py` yap

## ⏳ SONRA

Railway otomatik deploy edecek.
Logs’ta **“🚀 Bot başlıyor…”** yazacak

Sonra Telegram bot’una `/start` yaz!

-----

## 📝 BOT NE YAPACAK

✅ Hikaye oluştur (Gemini)
✅ Başlık öner
✅ Açıklama öner
✅ Kullanıcıdan feedback al
✅ Öğren ve gelişir
✅ learning_data.json’a kaydet

❌ YouTube upload (şimdilik yok - sonra ekleriz)

-----

## 🎯 TEST

1. `/start` yaz
1. “Uzayda kayıp astronot” yaz
1. 15 saniye seç
1. Başlık onay
1. Açıklama onay
1. ✅ Başarılı!

-----

İlk seferde çalışacak. Emin ol! 🚀