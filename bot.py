"""Telegram taqdimot boti (uz / ru / en): mavzu -> Gemini -> PowerPoint (.pptx)."""
import asyncio
import logging
import os
import re
import tempfile
import time
from threading import Thread

import requests
from flask import Flask
from telegram import BotCommand, InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup, Update
from telegram.constants import ChatAction
from telegram.error import BadRequest, TelegramError
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters,
)

import ai
import config
import db
import deck
from i18n import t

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logging.getLogger("werkzeug").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("bot")

MAX_TOPIC = 150
MAX_AUTHOR = 40
COUNTS = (5, 7, 10, 12, 15, 20)
FLOW_KEYS = ("step", "topic", "count", "theme", "author")
LIMIT = asyncio.Semaphore(config.MAX_PARALLEL)

# ------------------------------------------------------------------ Veb qism
# Render "web service" ochiq port talab qiladi. Bu 24/7 ishlashni kafolatlamaydi.
web = Flask(__name__)


@web.get("/")
def health():
    return "PowerPoint bot is running", 200


def run_web():
    web.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))


def keepalive():
    """Bepul Render xizmati 15 daqiqa trafiksiz uxlab qoladi; o'z manzilimizga vaqti-vaqti bilan so'rov yuboramiz."""
    url = os.environ.get("RENDER_EXTERNAL_URL")
    if not url or not config.KEEPALIVE:
        return
    while True:
        time.sleep(600)
        try:
            requests.get(url, timeout=15)
        except Exception as e:
            log.warning("keepalive xato: %s", e)


# ------------------------------------------------------------- Yordamchilar
def clean_filename(s):
    return re.sub(r'[\\/:*?"<>|\n\r]', "", s).strip()[:70] or "Presentation"


def clear_flow(ud):
    for k in FLOW_KEYS:
        ud.pop(k, None)


def lang_of(update, context):
    """Foydalanuvchi tili (yo'q bo'lsa None)."""
    lang = context.user_data.get("lang")
    if lang not in config.LANGS:
        lang = db.get_lang(update.effective_user.id)
        if lang:
            context.user_data["lang"] = lang
    return lang


async def show(update, context, text, markup=None):
    """Tugma bosilgan bo'lsa xabarni tahrirlaydi, aks holda yangi xabar yuboradi."""
    q = update.callback_query
    if q and q.message:
        try:
            await q.edit_message_text(text, reply_markup=markup)
            return
        except BadRequest as e:
            if "not modified" in str(e).lower():
                return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=markup)


# ---------------------------------------------------------------- Klaviaturalar
def lang_kb():
    return Markup([[
        Btn("🇺🇿 O'zbekcha", callback_data="lang:uz"),
        Btn("🇷🇺 Русский", callback_data="lang:ru"),
        Btn("🇬🇧 English", callback_data="lang:en"),
    ]])


def menu_kb(lang):
    return Markup([
        [Btn(t("btn_new", lang), callback_data="menu:new")],
        [Btn(t("btn_limit", lang), callback_data="menu:limit"), Btn(t("btn_lang", lang), callback_data="menu:lang")],
        [Btn(t("btn_help", lang), callback_data="menu:help")],
    ])


def home_kb(lang):
    return Markup([[Btn(t("btn_home", lang), callback_data="home")]])


def cancel_kb(lang):
    return Markup([[Btn(t("btn_cancel", lang), callback_data="cancel")]])


def counts_kb(lang):
    row1 = [Btn(str(n), callback_data=f"n:{n}") for n in COUNTS[:3]]
    row2 = [Btn(str(n), callback_data=f"n:{n}") for n in COUNTS[3:]]
    return Markup([row1, row2, [Btn(t("btn_cancel", lang), callback_data="cancel")]])


def themes_kb(lang):
    items = list(deck.THEMES)
    rows = []
    for i in range(0, len(items), 2):
        rows.append([Btn(f"{k}. {deck.theme_name(k, lang)}", callback_data=f"t:{k}") for k in items[i:i + 2]])
    rows.append([Btn(t("btn_cancel", lang), callback_data="cancel")])
    return Markup(rows)


# ------------------------------------------------------ Kanalga a'zolikni tekshirish
async def is_subscribed(bot, uid):
    if uid in config.ADMIN_IDS or not config.REQUIRED_CHANNELS:
        return True
    for ch in config.REQUIRED_CHANNELS:
        try:
            m = await bot.get_chat_member(chat_id=ch, user_id=uid)
        except TelegramError as e:
            # Odatda bot kanalda admin emas yoki kanal nomi xato. Foydalanuvchilar qulflanib qolmasligi uchun o'tkazib yuboramiz.
            log.error("Kanalni tekshirib bo'lmadi (%s): %s. Bot kanalda ADMIN ekanini tekshiring.", ch, e)
            continue
        if m.status in ("left", "kicked"):
            return False
        if m.status == "restricted" and not getattr(m, "is_member", True):
            return False
    return True


async def send_gate(update, context, lang, prefix=""):
    rows = [[Btn(f"📢 {ch}", url=f"https://t.me/{ch[1:]}")] for ch in config.REQUIRED_CHANNELS]
    rows.append([Btn(t("btn_check", lang), callback_data="chk")])
    await show(update, context, prefix + t("sub_required", lang), Markup(rows))


async def gate(update, context, lang):
    """True bo'lsa foydalanuvchi davom etishi mumkin."""
    if await is_subscribed(context.bot, update.effective_user.id):
        return True
    await send_gate(update, context, lang)
    return False


# ----------------------------------------------------------------- Ekranlar
async def show_menu(update, context, lang):
    clear_flow(context.user_data)
    await show(update, context, t("menu", lang), menu_kb(lang))


async def open_home(update, context):
    lang = lang_of(update, context)
    if lang is None:
        await show(update, context, t("choose_lang", "uz"), lang_kb())
        return
    if not await gate(update, context, lang):
        return
    await show_menu(update, context, lang)


async def start_new(update, context, lang):
    uid = update.effective_user.id
    left = db.left_today(uid)
    if left is not None and left <= 0:
        await show(update, context, t("limit_over", lang, total=config.DAILY_LIMIT), home_kb(lang))
        return
    clear_flow(context.user_data)
    context.user_data["step"] = "topic"
    await show(update, context, t("ask_topic", lang), cancel_kb(lang))


async def show_limit(update, context, lang):
    left = db.left_today(update.effective_user.id)
    if left is None:
        text = t("limit_unlimited", lang)
    else:
        text = t("limit_left", lang, left=left, total=config.DAILY_LIMIT)
    await show(update, context, text, home_kb(lang))


async def expired(update, context, lang):
    clear_flow(context.user_data)
    await show(update, context, t("expired", lang), home_kb(lang))


# ------------------------------------------------------------ Taqdimot yaratish
async def generate(update, context, lang):
    ud = context.user_data
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    if not all(k in ud for k in ("topic", "count", "theme", "author")):
        await expired(update, context, lang)
        return
    left = db.left_today(uid)
    if left is not None and left <= 0:
        await show(update, context, t("limit_over", lang, total=config.DAILY_LIMIT), home_kb(lang))
        clear_flow(ud)
        return

    topic, count, theme, author = ud["topic"], ud["count"], ud["theme"], ud["author"]
    ud["busy"] = True
    ud["step"] = None
    try:
        await show(update, context, t("generating", lang))
        await context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
        async with LIMIT:
            content = await asyncio.to_thread(ai.build_content, topic, lang, max(1, count - 3))
            with tempfile.TemporaryDirectory() as td:
                filename = clean_filename(topic) + ".pptx"
                path = os.path.join(td, filename)
                total, n_img = await asyncio.to_thread(
                    deck.create_presentation, lang, topic, author, theme, content, path)
                caption = t("caption", lang, n=total, topic=topic) + (t("caption_images", lang) if n_img else "")
                with open(path, "rb") as f:
                    await context.bot.send_document(
                        chat_id=chat_id, document=f, filename=filename, caption=caption[:1020],
                        write_timeout=120, read_timeout=120, connect_timeout=30,
                    )
        db.add_usage(uid)  # limit faqat muvaffaqiyatli yuborilgandan keyin sarflanadi
        await context.bot.send_message(chat_id=chat_id, text=t("menu", lang), reply_markup=menu_kb(lang))
    except ai.AIUnavailable:
        await context.bot.send_message(chat_id=chat_id, text=t("ai_fail", lang), reply_markup=menu_kb(lang))
    except Exception:
        log.exception("Taqdimot yaratishda xato")
        await context.bot.send_message(chat_id=chat_id, text=t("error", lang), reply_markup=menu_kb(lang))
    finally:
        clear_flow(ud)
        ud["busy"] = False


# ------------------------------------------------------------------ Handlerlar
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_flow(context.user_data)
    await open_home(update, context)


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data or ""
    ud = context.user_data
    uid = update.effective_user.id

    if data.startswith("lang:"):
        await q.answer()
        lang = data[5:]
        if lang in config.LANGS:
            db.set_lang(uid, lang)
            ud["lang"] = lang
            await open_home(update, context)
        return

    lang = lang_of(update, context)
    if lang is None:
        await q.answer()
        await show(update, context, t("choose_lang", "uz"), lang_kb())
        return
    if ud.get("busy"):
        await q.answer(t("busy", lang), show_alert=True)
        return
    await q.answer()

    if data == "chk":
        if await is_subscribed(context.bot, uid):
            await show_menu(update, context, lang)
        else:
            await send_gate(update, context, lang, prefix=t("sub_fail", lang) + "\n\n")
        return
    if not await gate(update, context, lang):
        return

    if data in ("home", "cancel"):
        await show_menu(update, context, lang)
    elif data == "menu:new":
        await start_new(update, context, lang)
    elif data == "menu:lang":
        await show(update, context, t("choose_lang", lang), lang_kb())
    elif data == "menu:limit":
        await show_limit(update, context, lang)
    elif data == "menu:help":
        await show(update, context, t("help", lang), home_kb(lang))
    elif data.startswith("n:"):
        n = int(data[2:]) if data[2:].isdigit() else 0
        if "topic" not in ud or n not in COUNTS:
            await expired(update, context, lang)
            return
        ud["count"] = n
        await show(update, context, t("ask_theme", lang), themes_kb(lang))
    elif data.startswith("t:"):
        theme = data[2:]
        if "count" not in ud or theme not in deck.THEMES:
            await expired(update, context, lang)
            return
        ud["theme"] = theme
        ud["step"] = "author"
        name = (update.effective_user.full_name or "").strip()[:MAX_AUTHOR] or "—"
        kb = Markup([
            [Btn(f"👤 {name}", callback_data="a:tg")],
            [Btn(t("btn_cancel", lang), callback_data="cancel")],
        ])
        await show(update, context, t("ask_author", lang), kb)
    elif data == "a:tg":
        if "theme" not in ud:
            await expired(update, context, lang)
            return
        ud["author"] = (update.effective_user.full_name or "").strip()[:MAX_AUTHOR] or "—"
        await generate(update, context, lang)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return
    lang = lang_of(update, context)
    if lang is None:
        await show(update, context, t("choose_lang", "uz"), lang_kb())
        return
    ud = context.user_data
    if ud.get("busy"):
        await msg.reply_text(t("busy", lang))
        return
    if not await gate(update, context, lang):
        return

    text = re.sub(r"\s+", " ", msg.text).strip()
    step = ud.get("step")
    if step == "topic":
        if len(text) < 3:
            await msg.reply_text(t("topic_short", lang))
        elif len(text) > MAX_TOPIC:
            await msg.reply_text(t("topic_long", lang, n=MAX_TOPIC))
        else:
            ud["topic"] = text
            ud["step"] = None
            await show(update, context, t("ask_count", lang, topic=text), counts_kb(lang))
    elif step == "author":
        if len(text) > MAX_AUTHOR:
            await msg.reply_text(t("author_long", lang, n=MAX_AUTHOR))
        else:
            ud["author"] = text
            await generate(update, context, lang)
    else:
        await msg.reply_text(t("use_menu", lang), reply_markup=menu_kb(lang))


async def on_error(update, context: ContextTypes.DEFAULT_TYPE):
    log.error("Kutilmagan xato", exc_info=context.error)


async def post_init(app):
    try:
        await app.bot.set_my_commands([
            BotCommand("start", "Start / Boshlash / Начать"),
            BotCommand("menu", "Menu / Menyu / Меню"),
            BotCommand("cancel", "Cancel / Bekor qilish / Отмена"),
        ])
    except Exception as e:
        log.warning("Buyruqlarni o'rnatib bo'lmadi: %s", e)


def main():
    # Python 3.14 da asyncio.get_event_loop() "no current event loop" xatosini beradi,
    # python-telegram-bot esa run_polling() ichida aynan shuni chaqiradi.
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    if not config.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing.")
    db._db()  # ombor yaratiladi (yozish huquqi bo'lmasa, shu yerda xato ko'rinadi)
    Thread(target=run_web, daemon=True).start()
    Thread(target=keepalive, daemon=True).start()

    app = Application.builder().token(config.BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler(["menu", "cancel"], cmd_start))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_error_handler(on_error)
    log.info("Bot ishga tushdi. Gemini kaliti: %s | kanallar: %s | kunlik limit: %s",
             "bor" if config.GEMINI_API_KEY else "YO'Q", config.REQUIRED_CHANNELS or "o'chiq", config.DAILY_LIMIT)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
