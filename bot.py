import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import requests
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configurazione
QR_API_URL = "https://api.qrcode-monkey.com/qr/custom"
LOGO_URL_W = "https://hknpolito.org/directus/assets/149f57c9-e3c6-4680-ae08-7fa7b83bef4a.png"  
LOGO_URL_B = "https://hknpolito.org/directus/assets/50024bd5-76ba-43f8-b058-e6d2aeb3b2cb.png"
QR_COLOR = "#3c506e"
BG_COLOR = "#061e33" 


# Logging (utile per il debug)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def gen_markup(dict, n):
    markup = InlineKeyboardMarkup()
    markup.row_width = n
    for key in dict:
        markup.add(InlineKeyboardButton(key, callback_data=dict[key]))
    return markup


bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, parse_mode=None)

logging.info("Bot avviato con successo!")


def qr_white(message):

    bot.send_message(message.chat.id, "Inviami un link e creerò un QR code per te!")

    @bot.message_handler(func=lambda m: True)
    def create_qr(message):
        text = message.text.strip()

        payload = {
            "data": text,
            "config": {
                "logo": LOGO_URL_B,
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

        r = requests.post(QR_API_URL, json=payload)

        bot.send_message(message.chat.id, "L'area IT ha cucinato👨🏻‍🍳")
        bot.send_photo(message.chat.id, r.content, caption="Ecco il tuo QR code!")
        keyboard = {"Crea un altro QR code": "new_qr"}
        bot.send_message(message.chat.id, "Se vuoi crearne un altro, premi il pulsante qui sotto!", reply_markup=gen_markup(keyboard, 1))

    bot.register_next_step_handler(message, create_qr)

def qr_blue(message):

    bot.send_message(message.chat.id, "Inviami un link e creerò un QR code per te!")

    @bot.message_handler(func=lambda m: True)
    def create_qr(message):
        text = message.text.strip()

        payload = {
            "data": text,
            "config": {
                "logo": LOGO_URL_W,
                "logoMode": "clean",
                "bodyColor": "#ffffff",
                "eye1Color": "#ffffff",
                "eye2Color": "#ffffff",
                "eye3Color": "#ffffff",
                "eyeBall1Color": "#ffffff",
                "eyeBall2Color": "#ffffff",
                "eyeBall3Color": "#ffffff",
                "bgColor": BG_COLOR,
            },
            "size": 1000,
            "download": False,
            "file": "png"
        }

        r = requests.post(QR_API_URL, json=payload)

        bot.send_message(message.chat.id, "L'area IT ha cucinato👨🏻‍🍳")
        bot.send_photo(message.chat.id, r.content, caption="Ecco il tuo QR code!")
        bot.send_message(message.chat.id, "Se vuoi crearne un altro, premi il pulsante qui sotto!", reply_markup=gen_markup({"Crea un altro QR code": "new_qr"}, 1))

    bot.register_next_step_handler(message, create_qr)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "white":
        keyboard = {
            "Sfondo Bianco ✅": "pass",
            "Sfondo Blu": "pass"
        }
        reply_markup = gen_markup(keyboard, 2)
        bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=reply_markup)
        qr_white(call.message)
    elif call.data == "blue":
        keyboard = {
            "Sfondo Bianco": "pass",
            "Sfondo Blu ✅": "pass"
        }
        reply_markup = gen_markup(keyboard, 2)
        bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=reply_markup)
        qr_blue(call.message)
    elif call.data == "new_qr":
        keyboard = {"Creazione in corso...": "pass"}
        reply_markup = gen_markup(keyboard, 1)
        bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=reply_markup)
        send_welcome(call.message)
    elif call.data == "pass":
        pass
    else: 
        bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id)


@bot.message_handler(commands=['start']) 
def send_welcome(message):

    bot.send_message(message.chat.id, "Benvenuto! Sono il tuo bot per creare QR code personalizzati targati HKN🤳")

    # Creazione dei bottoni
    keyboard = {
        "Sfondo Bianco": "white",
        "Sfondo Blu": "blue"
    }
    reply_markup = gen_markup(keyboard, 2)

    # Invio del messaggio con i bottoni
    bot.send_message(message.chat.id, "Scegli il colore dello sfondo:", reply_markup=reply_markup)

@bot.message_handler(func=lambda message: True)
def unknown(message):

    bot.send_message(message.chat.id, "Sorry, I didn't understand that command.")
    send_welcome(message)


bot.infinity_polling()




        


























