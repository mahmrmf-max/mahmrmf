import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import google.generativeai as genai
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery
import requests
from elevenlabs import ElevenLabs
import time
from pathlib import Path

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# States for conversation
STORY_INPUT, VIDEO_LENGTH, TITLE_CHECK, TITLE_INPUT, DESCRIPTION_CHECK, DESCRIPTION_INPUT = range(6)

class YouTubeVideoBot:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")
        self.youtube_creds_json = os.getenv("YOUTUBE_CREDS_JSON")
        
        # Initialize Gemini
        genai.configure(api_key=self.gemini_api_key)
        
        # Learning data storage
        self.learning_data = {
            "title_preferences": [],
            "description_preferences": [],
            "style_notes": []
        }
        self.load_learning_data()
    
    def load_learning_data(self):
        """Botun öğrendiklerini yükle"""
        if os.path.exists("learning_data.json"):
            with open("learning_data.json", "r", encoding="utf-8") as f:
                self.learning_data = json.load(f)
    
    def save_learning_data(self):
        """Botun öğrendiklerini kaydet"""
        with open("learning_data.json", "w", encoding="utf-8") as f:
            json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
    
    def get_youtube_service(self):
        """YouTube API servisini başlat"""
        SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                creds_dict = json.loads(self.youtube_creds_json)
                flow = InstalledAppFlow.from_client_config(creds_dict, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        
        return discovery.build("youtube", "v3", credentials=creds)
    
    async def generate_story(self, topic: str) -> str:
        """Gemini ile hikaye oluştur"""
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        Konu: {topic}
        
        Lütfen 20-30 saniye için uygun, dramatik ve ilgi çekici bir kısa hikaye yaz.
        Hikaye:
        - Açılış: Hızlı ve dikkat çekici
        - Gelişme: Gerilim veya beklenti
        - Sonuç: Şaşırtıcı veya etkileyici
        
        Hikaye (sadece metin, süsleme olmadan):
        """
        response = model.generate_content(prompt)
        return response.text
    
    async def generate_title_with_learning(self, story: str) -> str:
        """Öğrenme verilerine göre başlık oluştur"""
        model = genai.GenerativeModel('gemini-pro')
        
        learning_context = ""
        if self.learning_data["title_preferences"]:
            learning_context = f"Kullanıcı daha önceki başlıkları şöyle düzeltmişti: {self.learning_data['title_preferences'][-3:]}"
        
        prompt = f"""
        Hikaye: {story[:200]}...
        
        {learning_context}
        
        Lütfen YouTube için uygun, dikkat çekici bir başlık öner (max 60 karakter).
        Başlık şunları içermeli:
        - Dramatik ve ilgi çekici olmak
        - Merak uyandırmak
        - Kısa ve özlü olmak
        
        Başlık (sadece başlık metni):
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    
    async def generate_description_with_learning(self, story: str, title: str) -> str:
        """Öğrenme verilerine göre açıklama oluştur"""
        model = genai.GenerativeModel('gemini-pro')
        
        learning_context = ""
        if self.learning_data["description_preferences"]:
            learning_context = f"Kullanıcı daha önceki açıklamalar için şunları belirtmişti: {self.learning_data['description_preferences'][-2:]}"
        
        prompt = f"""
        Hikaye: {story}
        Başlık: {title}
        
        {learning_context}
        
        YouTube video açıklaması yaz. Şunları içer:
        - Hikayenin kısa özeti (1-2 cümle)
        - Neden izlenmeli (1 cümle)
        - İlgili hashtagler (#cinematik #hikaye #drama vs)
        - Hoşlanırsan abone ol çağrısı
        
        Açıklama (sadece açıklama metni, markdown kullan):
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    
    async def generate_video(self, story: str, duration: int) -> str:
        """Gemini Veo ile video oluştur (simülasyon - gerçekte API gerekli)"""
        # Not: Gerçek Veo API integrasyonu için ayrı endpoint gerekli
        # Bu bir placeholder - detaylı implementasyon için docs.claude.com kontrol et
        logger.info(f"Video oluşturuluyor: {duration} saniye")
        
        # Simülasyon: video file oluştur (gerçekte Gemini Veo API)
        video_path = f"video_{int(time.time())}.mp4"
        
        # Placeholder - gerçek video oluşturma için:
        # https://ai.google.dev/gemini-api/docs/video
        
        return video_path
    
    async def add_audio(self, video_path: str, story: str) -> str:
        """ElevenLabs ile ses ekle"""
        if not self.elevenlabs_key:
            logger.warning("ElevenLabs API key bulunamadı, ses olmadan devam et")
            return video_path
        
        client = ElevenLabs(api_key=self.elevenlabs_key)
        
        # Text-to-speech
        audio = client.generate(
            text=story,
            voice="Bella",  # Turkish friendly voice
            model="eleven_monolingual_v1"
        )
        
        audio_path = f"audio_{int(time.time())}.mp3"
        with open(audio_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        return audio_path
    
    async def upload_to_youtube(self, video_path: str, title: str, description: str) -> str:
        """YouTube'a video yükle"""
        youtube = self.get_youtube_service()
        
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "categoryId": "24",  # Entertainment
                    "title": title,
                    "description": description,
                    "tags": ["hikaye", "dramatik", "ai", "kısa film"],
                    "defaultLanguage": "tr",
                    "defaultAudioLanguage": "tr"
                },
                "status": {
                    "privacyStatus": "public",  # Herkese açık
                    "madeForKids": False
                }
            },
            media_body=video_path
        )
        
        response = request.execute()
        return response["id"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Başlat komutu"""
    welcome_text = """
    🎬 YouTube AI Video Bot'a hoş geldin!
    
    Nasıl çalışıyor:
    1. Bir hikaye konusu yaz
    2. Video süresini seç (8s / 15s / 30s)
    3. AI hikaye oluşturur
    4. Başlık ve açıklama önerir
    5. Beğenmezsen düzeltir ve öğrenir
    6. YouTube'a otomatik yükler
    
    Başlayalım! Bir hikaye konusu yaz:
    Örn: "Uzayda kayıp astronot", "Geceyi ormanda geçirmek", vs...
    """
    await update.message.reply_text(welcome_text)
    return STORY_INPUT

async def story_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hikaye konusunu al"""
    context.user_data["topic"] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("8 saniye", callback_data="8"),
         InlineKeyboardButton("15 saniye", callback_data="15"),
         InlineKeyboardButton("30 saniye", callback_data="30")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"📹 Konu: {context.user_data['topic']}\n\nVideo süresini seç:",
        reply_markup=reply_markup
    )
    return VIDEO_LENGTH

async def video_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Video süresini al"""
    query = update.callback_query
    await query.answer()
    
    context.user_data["duration"] = int(query.data)
    context.user_data["bot"] = YouTubeVideoBot()
    
    await query.edit_message_text(f"✨ Video oluşturuluyor ({context.user_data['duration']}s)...\n\nBu biraz zaman alabilir...")
    
    # Hikaye oluştur
    story = await context.user_data["bot"].generate_story(context.user_data["topic"])
    context.user_data["story"] = story
    
    # Başlık oluştur
    title = await context.user_data["bot"].generate_title_with_learning(story)
    context.user_data["proposed_title"] = title
    
    keyboard = [
        [InlineKeyboardButton("✅ Beğendim", callback_data="title_ok"),
         InlineKeyboardButton("✏️ Düzelt", callback_data="title_edit"),
         InlineKeyboardButton("❌ Baştan Yap", callback_data="title_reject")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        f"📝 **Önerilen Başlık:**\n\n{title}\n\nBeğendin mi?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return TITLE_CHECK

async def title_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Başlık onayı"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "title_ok":
        context.user_data["final_title"] = context.user_data["proposed_title"]
        
        # Açıklama oluştur
        description = await context.user_data["bot"].generate_description_with_learning(
            context.user_data["story"],
            context.user_data["final_title"]
        )
        context.user_data["proposed_description"] = description
        
        keyboard = [
            [InlineKeyboardButton("✅ Beğendim", callback_data="desc_ok"),
             InlineKeyboardButton("✏️ Düzelt", callback_data="desc_edit"),
             InlineKeyboardButton("❌ Baştan Yap", callback_data="desc_reject")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"📋 **Önerilen Açıklama:**\n\n{description}\n\nBeğendin mi?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return DESCRIPTION_CHECK
    
    elif query.data == "title_edit":
        await query.edit_message_text("✏️ Yeni başlığı yaz:")
        return TITLE_INPUT
    
    else:  # reject
        await query.edit_message_text("🔄 Başlık yeniden oluşturuluyor...")
        title = await context.user_data["bot"].generate_title_with_learning(context.user_data["story"])
        context.user_data["proposed_title"] = title
        
        keyboard = [
            [InlineKeyboardButton("✅ Beğendim", callback_data="title_ok"),
             InlineKeyboardButton("✏️ Düzelt", callback_data="title_edit"),
             InlineKeyboardButton("❌ Baştan Yap", callback_data="title_reject")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            f"📝 **Yeni Başlık:**\n\n{title}\n\nBeğendin mi?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return TITLE_CHECK

async def title_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Başlığı düzelt"""
    context.user_data["final_title"] = update.message.text
    context.user_data["bot"].learning_data["title_preferences"].append(
        f"Orijinal: {context.user_data['proposed_title']} → Düzeltme: {context.user_data['final_title']}"
    )
    context.user_data["bot"].save_learning_data()
    
    # Açıklama oluştur
    description = await context.user_data["bot"].generate_description_with_learning(
        context.user_data["story"],
        context.user_data["final_title"]
    )
    context.user_data["proposed_description"] = description
    
    keyboard = [
        [InlineKeyboardButton("✅ Beğendim", callback_data="desc_ok"),
         InlineKeyboardButton("✏️ Düzelt", callback_data="desc_edit"),
         InlineKeyboardButton("❌ Baştan Yap", callback_data="desc_reject")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"📋 **Önerilen Açıklama:**\n\n{description}\n\nBeğendin mi?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return DESCRIPTION_CHECK

async def description_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Açıklama onayı"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "desc_ok":
        context.user_data["final_description"] = context.user_data["proposed_description"]
        
        await query.edit_message_text("🎬 Video YouTube'a yükleniyor...\n\n⏳ Lütfen bekle...")
        
        try:
            # Video oluştur
            video_path = await context.user_data["bot"].generate_video(
                context.user_data["story"],
                context.user_data["duration"]
            )
            
            # Ses ekle
            audio_path = await context.user_data["bot"].add_audio(
                video_path,
                context.user_data["story"]
            )
            
            # YouTube'a yükle
            video_id = await context.user_data["bot"].upload_to_youtube(
                video_path,
                context.user_data["final_title"],
                context.user_data["final_description"]
            )
            
            await query.message.reply_text(
                f"✅ **Video Başarıyla Yüklendi!**\n\n"
                f"📝 Başlık: {context.user_data['final_title']}\n\n"
                f"🔗 YouTube: https://youtube.com/watch?v={video_id}\n\n"
                f"📚 Bot öğrenme modunda: Başlık ve açıklama tercihlerini hatırlıyorum!"
            )
        except Exception as e:
            await query.message.reply_text(f"❌ Hata: {str(e)}")
        
        return ConversationHandler.END
    
    elif query.data == "desc_edit":
        await query.edit_message_text("✏️ Yeni açıklamayı yaz:")
        return DESCRIPTION_INPUT
    
    else:  # reject
        await query.edit_message_text("🔄 Açıklama yeniden oluşturuluyor...")
        description = await context.user_data["bot"].generate_description_with_learning(
            context.user_data["story"],
            context.user_data["final_title"]
        )
        context.user_data["proposed_description"] = description
        
        keyboard = [
            [InlineKeyboardButton("✅ Beğendim", callback_data="desc_ok"),
             InlineKeyboardButton("✏️ Düzelt", callback_data="desc_edit"),
             InlineKeyboardButton("❌ Baştan Yap", callback_data="desc_reject")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            f"📋 **Yeni Açıklama:**\n\n{description}\n\nBeğendin mi?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return DESCRIPTION_CHECK

async def description_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Açıklamayı düzelt"""
    context.user_data["final_description"] = update.message.text
    context.user_data["bot"].learning_data["description_preferences"].append(
        f"Düzeltme: {context.user_data['final_description']}"
    )
    context.user_data["bot"].save_learning_data()
    
    await update.message.reply_text("🎬 Video YouTube'a yükleniyor...\n\n⏳ Lütfen bekle...")
    
    try:
        # Video oluştur ve yükle
        video_path = await context.user_data["bot"].generate_video(
            context.user_data["story"],
            context.user_data["duration"]
        )
        
        audio_path = await context.user_data["bot"].add_audio(
            video_path,
            context.user_data["story"]
        )
        
        video_id = await context.user_data["bot"].upload_to_youtube(
            video_path,
            context.user_data["final_title"],
            context.user_data["final_description"]
        )
        
        await update.message.reply_text(
            f"✅ **Video Başarıyla Yüklendi!**\n\n"
            f"📝 Başlık: {context.user_data['final_title']}\n\n"
            f"🔗 YouTube: https://youtube.com/watch?v={video_id}\n\n"
            f"📚 Bot öğrenme modunda: Düzeltmelerinizi hatırlıyorum!"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)}")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """İptal"""
    await update.message.reply_text("❌ İşlem iptal edildi. /start ile yeniden başlayabilirsin.")
    return ConversationHandler.END

def main():
    """Bot'u başlat"""
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STORY_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, story_input)],
            VIDEO_LENGTH: [CommandHandler("start", start)],
            TITLE_CHECK: [CommandHandler("start", start)],
            TITLE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, title_input)],
            DESCRIPTION_CHECK: [CommandHandler("start", start)],
            DESCRIPTION_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, description_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
