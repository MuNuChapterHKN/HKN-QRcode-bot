import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configurazione
QR_API_URL = "https://api.qrcode-monkey.com/qr/custom"
LOGO_URL = "https://hknpolito.org/directus/assets/e7e4038d-0f2c-4bbe-a483-a83541c74494.png"  # Cambia con l'URL della tua immagine
QR_COLOR = "#3c506e"  # Verde foresta, puoi cambiare

# Logging (utile per il debug)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Inviami un link e creerò un QR code per te!")

async def create_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not (text.startswith("http://") or text.startswith("https://")):
        await update.message.reply_text("Per favore, inviami un link valido (http o https).")
        return

    payload = {
        "data": text,
        "config": {
            "logo": LOGO_URL,
            "logoMode": "clean",
            "bodyColor": QR_COLOR,
            "eye1Color": QR_COLOR,
            "eye2Color": QR_COLOR,
            "eye3Color": QR_COLOR,
            "eyeBall1Color": QR_COLOR,
            "eyeBall2Color": QR_COLOR,
            "eyeBall3Color": QR_COLOR,
        },
        "size": 1000,
        "download": False,
        "file": "png"
    }

    try:
        r = requests.post(QR_API_URL, json=payload)

        await update.message.reply_text("L'area IT ha cucinato")
        await update.message.reply_photo(photo=r.content, caption="Ecco il tuo QR code!")
    except Exception as e:
        logging.error(f"Errore nella generazione del QR: {e}")
        await update.message.reply_text("Si è verificato un errore nella generazione del QR code.")

# Setup del bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, create_qr))

    print("Bot avviato.")
    app.run_polling()
