#!/usr/bin/env python3
import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleBot:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_key:
            logger.error("❌ GEMINI_API_KEY EKSIK!")
        else:
            logger.info("✅ GEMINI_API_KEY BULUNDU")
            genai.configure(api_key=self.gemini_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')

    
    def generate_story(self, topic):
        try:
            prompt = f"Konu: {topic}\n\nKısa, dramatik hikaye yaz (Türkçe, 15-20 saniye):"
            response = self.model.generate_content(prompt)
            return response.text if response else "Hikaye oluşturulamadı"
        except Exception as e:
            logger.error(f"❌ Story error: {e}")
            return f"Hata: {str(e)}"
    
    def generate_title(self, story):
        try:
            prompt = f"Hikaye: {story[:200]}...\n\nYouTube başlığı yaz (max 60 karakter):"
            response = self.model.generate_content(prompt)
            return response.text.strip() if response else "Başlık oluşturulamadı"
        except Exception as e:
            logger.error(f"❌ Title error: {e}")
            return f"Hata: {str(e)}"

bot_instance = SimpleBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info(f"✅ /start komutu alındı")
        await update.message.reply_text(
            "🎬 **Video Bot**\n\n"
            "Bir hikaye konusu yaz:\n"
            "Örn: Uzayda kayıp astronot"
        )
    except Exception as e:
        logger.error(f"❌ Start error: {e}")
        try:
            await update.message.reply_text(f"Hata: {str(e)}")
        except:
            pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        topic = update.message.text
        logger.info(f"📝 Konu alındı: {topic}")
        
        # Hikaye oluştur
        logger.info("⏳ Hikaye oluşturuluyor...")
        story = bot_instance.generate_story(topic)
        
        if "Hata" in story:
            await update.message.reply_text(story)
            return
        
        logger.info("✅ Hikaye oluşturuldu")
        
        # Başlık oluştur
        logger.info("⏳ Başlık oluşturuluyor...")
        title = bot_instance.generate_title(story)
        
        logger.info(f"✅ Başlık: {title}")
        
        # Göster
        keyboard = [
            [InlineKeyboardButton("✅ OK", callback_data="ok"),
             InlineKeyboardButton("❌ Tekrar", callback_data="retry")]
        ]
        
        await update.message.reply_text(
            f"📝 **Başlık:**\n\n{title}\n\nBeğendin mi?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"❌ Message error: {e}")
        try:
            await update.message.reply_text(f"❌ Hata: {str(e)}")
        except:
            logger.error(f"❌ Reply hatası: {e}")

def main():
    logger.info("🚀 Bot başlıyor...")
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN EKSIK!")
        return
    
    logger.info("✅ TELEGRAM_BOT_TOKEN BULUNDU")
    
    app = Application.builder().token(token).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ Handlers eklendi")
    logger.info("✅ Polling başlıyor...")
    
    app.run_polling()

if __name__ == "__main__":
    main()
