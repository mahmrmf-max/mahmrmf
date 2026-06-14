#!/usr/bin/env python3
import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import google.generativeai as genai

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# States
STORY_INPUT, VIDEO_LENGTH, TITLE_CHECK, TITLE_INPUT, DESCRIPTION_CHECK, DESCRIPTION_INPUT, UPLOAD = range(7)

class SimpleVideoBot:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.gemini_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Learning data
        self.learning_file = "learning_data.json"
        self.load_learning()
    
    def load_learning(self):
        """Öğrenme verilerini yükle"""
        if os.path.exists(self.learning_file):
            try:
                with open(self.learning_file, "r", encoding="utf-8") as f:
                    self.learning = json.load(f)
            except:
                self.learning = {"titles": [], "descriptions": []}
        else:
            self.learning = {"titles": [], "descriptions": []}
    
    def save_learning(self):
        """Öğrenme verilerini kaydet"""
        with open(self.learning_file, "w", encoding="utf-8") as f:
            json.dump(self.learning, f, ensure_ascii=False, indent=2)
    
    def generate_story(self, topic):
        """Hikaye oluştur"""
        try:
            prompt = f"""
Konu: {topic}

Lütfen 15-20 saniye için dramatik, ilgi çekici bir kısa hikaye yaz.
Sadece hikaye metni, başka şey yazma.
Türkçe olsun.
"""
            response = self.model.generate_content(prompt)
            return response.text if response else "Hikaye oluşturulamadı"
        except Exception as e:
            logger.error(f"Story generation error: {e}")
            return f"Hata: {str(e)}"
    
    def generate_title(self, story):
        """Başlık öner"""
        try:
            learning_hint = ""
            if self.learning["titles"]:
                learning_hint = f"\nKullanıcı daha önceki başlıkları şöyle düzeltmişti: {self.learning['titles'][-2:]}"
            
            prompt = f"""
Hikaye: {story[:300]}...

{learning_hint}

YouTube için çekici bir başlık yaz (max 60 karakter).
Sadece başlık, başka şey yazma.
"""
            response = self.model.generate_content(prompt)
            return response.text.strip() if response else "Başlık oluşturulamadı"
        except Exception as e:
            logger.error(f"Title generation error: {e}")
            return "Başlık oluşturulamadı"
    
    def generate_description(self, story, title):
        """Açıklama öner"""
        try:
            learning_hint = ""
            if self.learning["descriptions"]:
                learning_hint = f"\nKullanıcı daha önceki açıklamalar için şunları belirtmişti: {self.learning['descriptions'][-1]}"
            
            prompt = f"""
Hikaye: {story}
Başlık: {title}

{learning_hint}

YouTube açıklaması yaz (3-4 satır):
- Hikayenin özeti
- Neden izlenmeli
- Hashtags (#hikaye #dramatik #ai vb)

Sadece açıklama, başka şey yazma.
"""
            response = self.model.generate_content(prompt)
            return response.text.strip() if response else "Açıklama oluşturulamadı"
        except Exception as e:
            logger.error(f"Description generation error: {e}")
            return "Açıklama oluşturulamadı"

# Global bot instance
bot = SimpleVideoBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Başlat"""
    text = """
🎬 **YouTube AI Video Bot v2**

Nasıl çalışıyor:
1️⃣ Bir hikaye konusu yaz
2️⃣ Video süresini seç
3️⃣ AI hikaye + başlık + açıklama oluşturur
4️⃣ Beğenmezsen düzeltirsin
5️⃣ Bot öğrenir ve gelişir

Başlayalım! Bir konu yaz:
"""
    await update.message.reply_text(text)
    return STORY_INPUT

async def get_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hikaye konusu al"""
    context.user_data["topic"] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("8s", callback_data="8"),
         InlineKeyboardButton("15s", callback_data="15"),
         InlineKeyboardButton("30s", callback_data="30")]
    ]
    
    await update.message.reply_text(
        f"📹 Konu: {context.user_data['topic']}\n\nSüre seç:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return VIDEO_LENGTH

async def get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Süre al ve hikaye oluştur"""
    query = update.callback_query
    await query.answer()
    
    context.user_data["duration"] = int(query.data)
    
    await query.edit_message_text("⏳ Hikaye oluşturuluyor...")
    
    # Generate story
    story = bot.generate_story(context.user_data["topic"])
    context.user_data["story"] = story
    
    # Generate title
    title = bot.generate_title(story)
    context.user_data["proposed_title"] = title
    
    keyboard = [
        [InlineKeyboardButton("✅ OK", callback_data="title_ok"),
         InlineKeyboardButton("✏️ Düzelt", callback_data="title_edit")]
    ]
    
    await query.message.reply_text(
        f"📝 Başlık Önerim:\n\n**{title}**\n\nBeğendin mi?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return TITLE_CHECK

async def title_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Başlık kontrol"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "title_ok":
        context.user_data["final_title"] = context.user_data["proposed_title"]
    else:
        await query.edit_message_text("Yeni başlığı yaz:")
        return TITLE_INPUT
    
    # Generate description
    desc = bot.generate_description(
        context.user_data["story"],
        context.user_data["final_title"]
    )
    context.user_data["proposed_description"] = desc
    
    keyboard = [
        [InlineKeyboardButton("✅ OK", callback_data="desc_ok"),
         InlineKeyboardButton("✏️ Düzelt", callback_data="desc_edit")]
    ]
    
    await query.message.reply_text(
        f"📋 Açıklama Önerim:\n\n{desc}\n\nBeğendin mi?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return DESCRIPTION_CHECK

async def title_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Başlığı düzelt"""
    context.user_data["final_title"] = update.message.text
    
    # Learn
    bot.learning["titles"].append({
        "original": context.user_data["proposed_title"],
        "corrected": context.user_data["final_title"]
    })
    bot.save_learning()
    
    await update.message.reply_text("✅ Öğrendim!")
    
    # Generate description
    desc = bot.generate_description(
        context.user_data["story"],
        context.user_data["final_title"]
    )
    context.user_data["proposed_description"] = desc
    
    keyboard = [
        [InlineKeyboardButton("✅ OK", callback_data="desc_ok"),
         InlineKeyboardButton("✏️ Düzelt", callback_data="desc_edit")]
    ]
    
    await update.message.reply_text(
        f"📋 Açıklama Önerim:\n\n{desc}\n\nBeğendin mi?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return DESCRIPTION_CHECK

async def description_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Açıklama kontrol"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "desc_ok":
        context.user_data["final_description"] = context.user_data["proposed_description"]
    else:
        await query.edit_message_text("Yeni açıklamayı yaz:")
        return DESCRIPTION_INPUT
    
    # Summary
    await query.message.reply_text(
        f"""
✅ **Hazır!**

📝 Başlık: {context.user_data['final_title']}
📋 Açıklama: {context.user_data['final_description'][:50]}...
⏱️ Süre: {context.user_data['duration']}s

🎬 YouTube'a yüklemek için API entegrasyonu lazım.
Şu an Telegram'da hikaye + başlık + açıklama başarıyla oluşturuldu!

📚 Bot öğrenme modunda çalışıyor!
        """,
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END

async def description_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Açıklamayı düzelt"""
    context.user_data["final_description"] = update.message.text
    
    # Learn
    bot.learning["descriptions"].append(context.user_data["final_description"])
    bot.save_learning()
    
    await update.message.reply_text(
        f"""
✅ **Hazır!**

📝 Başlık: {context.user_data['final_title']}
📋 Açıklama: {context.user_data['final_description'][:50]}...
⏱️ Süre: {context.user_data['duration']}s

🎬 YouTube'a yüklemek için API entegrasyonu lazım.
Şu an Telegram'da hikaye + başlık + açıklama başarıyla oluşturuldu!

📚 Bot öğrenme modunda çalışıyor!
        """,
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """İptal"""
    await update.message.reply_text("❌ İptal. /start ile başla.")
    return ConversationHandler.END

def main():
    """Bot'u çalıştır"""
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STORY_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_story)],
            VIDEO_LENGTH: [CommandHandler("start", start)],
            TITLE_CHECK: [CommandHandler("start", start)],
            TITLE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, title_input)],
            DESCRIPTION_CHECK: [CommandHandler("start", start)],
            DESCRIPTION_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, description_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    
    logger.info("🚀 Bot başlıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
