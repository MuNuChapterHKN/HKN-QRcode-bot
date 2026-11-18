import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import io
import logging
import math
import os
from urllib.parse import urlparse

import qrcode
from qrcode.exceptions import DataOverflowError
from PIL import Image, ImageDraw

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configurazione
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
QR_COLOR = "#3c506e"
BG_COLOR = "#061e33"
QR_SIZE = 1000      # lato del QR in pixel, margine escluso
QR_BORDER = 2       # margine attorno al QR, in moduli (come QRCode Monkey)
LOGO_RATIO = 0.28   # lato del logo rispetto al lato del QR

INVALID_LINK_MSG = (
    "Il link non è valido😭😭😭\n"
    "Inserisci un indirizzo completo che inizi con http:// o https://, ad esempio:\n\n"
    "-> https://hknpolito.org"
)
TOO_LONG_MSG = "Il link è troppo lungo per stare in un QR code 😕 Mandamene uno più corto."
ERROR_MSG = "Qualcosa è andato storto durante la creazione del QR code 😕 Riprova con /start."


def load_logo(filename):
    # carica il logo dalla cartella assets e lo ritaglia sul contenuto (toglie i bordi trasparenti)
    with Image.open(os.path.join(ASSETS_DIR, filename)) as img:
        logo = img.convert("RGBA")
    return logo.crop(logo.getbbox())


QR_STYLES = {
    "white": {"fg": QR_COLOR, "bg": "#ffffff", "logo": load_logo("logo_blue.png")},
    "blue": {"fg": "#ffffff", "bg": BG_COLOR, "logo": load_logo("logo_white.png")},
}

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


def make_qr(data, style):
    # genera il QR code con il logo al centro e lo restituisce come PNG in memoria
    qr_code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=QR_BORDER)
    qr_code.add_data(data)
    try:
        qr_code.make(fit=True)  # sceglie la versione più piccola che contiene il link
    except ValueError as exc:
        # qrcode 8.2 segnala i dati troppo lunghi con ValueError("Invalid version (was 41, ...)")
        raise DataOverflowError(str(exc)) from exc

    modules = qr_code.modules_count
    box = max(1, QR_SIZE // modules)  # lato di un modulo in pixel
    qr_code.box_size = box
    img = qr_code.make_image(fill_color=style["fg"], back_color=style["bg"]).convert("RGBA")

    clean = math.ceil(modules * LOGO_RATIO)
    if (modules - clean) % 2:
        clean += 1  # stessa parità del QR, così l'area è perfettamente centrata
    start = (QR_BORDER + (modules - clean) // 2) * box
    end = start + clean * box
    ImageDraw.Draw(img).rectangle([start, start, end - 1, end - 1], fill=style["bg"])

    # logo ridimensionato e incollato al centro dell'area pulita
    logo = style["logo"].copy()
    side = round(modules * box * LOGO_RATIO)
    logo.thumbnail((side, side), Image.Resampling.LANCZOS)
    img.paste(logo, (start + (end - start - logo.width) // 2, start + (end - start - logo.height) // 2), logo)

    output = io.BytesIO()
    img.convert("RGB").save(output, format="PNG")
    output.seek(0)
    output.name = "qr.png"
    return output


def is_valid_link(text):
    # True se il testo è un link http/https con un dominio, es. https://hknpolito.org
    if not text or any(c.isspace() for c in text):
        return False
    try:
        parsed = urlparse(text)
        host = parsed.hostname
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and bool(host) and "." in host


bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, parse_mode=None)

logging.info("Bot avviato con successo!")


def qr(message, color):

    bot.send_message(message.chat.id, "Inserisci un link valido")

    def create_qr(message):
        text = (message.text or "").strip()  # foto, sticker, ecc. non hanno testo

        # Un comando (es. /start) annulla l'attesa del link e riporta al menu
        if text.startswith("/"):
            send_welcome(message)
            return

        if not is_valid_link(text):
            bot.send_message(message.chat.id, INVALID_LINK_MSG)
            bot.register_next_step_handler(message, create_qr)  # aspetta un nuovo tentativo
            return

        try:
            image = make_qr(text, QR_STYLES[color])
            bot.send_message(message.chat.id, "QR code generato con successo!")
            bot.send_photo(message.chat.id, image)
        except DataOverflowError:
            bot.send_message(message.chat.id, TOO_LONG_MSG)
            bot.register_next_step_handler(message, create_qr)
            return
        except Exception:
            logging.exception("Errore durante la creazione o l'invio del QR code")
            bot.send_message(message.chat.id, ERROR_MSG)
            return

        keyboard = {"Crea un altro QR code": "new_qr"}
        bot.send_message(message.chat.id, "Se vuoi crearne un altro, premi il pulsante qui sotto!", reply_markup=gen_markup(keyboard, 1))

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
        qr(call.message, call.data)
    elif call.data == "blue":
        keyboard = {
            "Sfondo Bianco": "pass",
            "Sfondo Blu ✅": "pass"
        }
        reply_markup = gen_markup(keyboard, 2)
        bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=reply_markup)
        qr(call.message, call.data)
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

    bot.send_message(message.chat.id, "Benvenuto! Sono il bot per creare QR code personalizzati targati HKN🤳")

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

    bot.send_message(message.chat.id, "Scusami, non ho capito il comando.")
    send_welcome(message)


bot.infinity_polling()




        


























