"""Barcha sozlamalar muhit o'zgaruvchilaridan (Environment Variables) o'qiladi."""
import logging
import os
from datetime import timedelta, timezone

log = logging.getLogger(__name__)


def _int(name, default):
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
# Asosiy model 404 bersa (o'chirilgan/eskirgan) ketma-ket shular sinaladi.
GEMINI_FALLBACK_MODELS = ("gemini-3.8-flash", "gemini-3.6-flash", "gemini-2.5-flash")

# Bepul foydalanuvchi uchun kunlik taqdimotlar soni
DAILY_LIMIT = _int("DAILY_LIMIT", 3)
# Bir vaqtda nechta taqdimot yaratilsin (bepul hostingda 1-2 yetarli)
MAX_PARALLEL = max(1, _int("MAX_PARALLEL", 2))
# Cheksiz foydalanadigan adminlar: Telegram ID lar vergul bilan
ADMIN_IDS = {int(x) for x in os.environ.get("ADMIN_IDS", "").replace(" ", "").split(",") if x.isdigit()}

# Majburiy kanallar: "@kanal1,@kanal2". Bo'sh bo'lsa, tekshiruv o'chiq.
REQUIRED_CHANNELS = []
for _ch in os.environ.get("REQUIRED_CHANNELS", "").replace(" ", "").split(","):
    if not _ch:
        continue
    if _ch.startswith("@") and len(_ch) > 2:
        REQUIRED_CHANNELS.append(_ch)
    else:
        log.warning("REQUIRED_CHANNELS: '%s' e'tiborga olinmadi (faqat @username ko'rinishi qo'llanadi)", _ch)

DB_PATH = os.environ.get("DB_PATH", "bot.db")
KEEPALIVE = os.environ.get("KEEPALIVE", "1") != "0"

# O'zbekiston vaqti (UTC+5, yozgi vaqt yo'q). Kunlik limit shu vaqt bo'yicha yangilanadi.
TZ = timezone(timedelta(hours=5))

LANGS = ("uz", "ru", "en")
