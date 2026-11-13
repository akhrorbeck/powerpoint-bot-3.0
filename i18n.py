"""Bot matnlari: o'zbek (uz), rus (ru), ingliz (en)."""

TEXTS = {
    "choose_lang": {
        "uz": "🌐 Tilni tanlang / Выберите язык / Choose language:",
        "ru": "🌐 Tilni tanlang / Выберите язык / Choose language:",
        "en": "🌐 Tilni tanlang / Выберите язык / Choose language:",
    },
    "menu": {
        "uz": "🏠 Bosh menyu\n\nMavzu bo'yicha tayyor PowerPoint taqdimot yarataman. Boshlash uchun tugmani bosing.",
        "ru": "🏠 Главное меню\n\nЯ создам готовую презентацию PowerPoint по вашей теме. Нажмите кнопку, чтобы начать.",
        "en": "🏠 Main menu\n\nI create a ready PowerPoint presentation on your topic. Press the button to start.",
    },
    "btn_new": {"uz": "📊 Yangi taqdimot", "ru": "📊 Новая презентация", "en": "📊 New presentation"},
    "btn_lang": {"uz": "🌐 Til", "ru": "🌐 Язык", "en": "🌐 Language"},
    "btn_limit": {"uz": "📈 Limitim", "ru": "📈 Мой лимит", "en": "📈 My limit"},
    "btn_help": {"uz": "ℹ️ Yordam", "ru": "ℹ️ Помощь", "en": "ℹ️ Help"},
    "btn_home": {"uz": "🏠 Menyu", "ru": "🏠 Меню", "en": "🏠 Menu"},
    "btn_cancel": {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "en": "❌ Cancel"},
    "btn_check": {"uz": "✅ Tekshirish", "ru": "✅ Проверить", "en": "✅ Check"},
    "sub_required": {
        "uz": "📢 Botdan foydalanish uchun quyidagi kanal(lar)ga obuna bo'ling, so'ng «Tekshirish» tugmasini bosing.",
        "ru": "📢 Чтобы пользоваться ботом, подпишитесь на канал(ы) ниже, затем нажмите «Проверить».",
        "en": "📢 To use the bot, subscribe to the channel(s) below, then press “Check”.",
    },
    "sub_fail": {
        "uz": "❌ Siz hali barcha kanallarga obuna bo'lmagansiz.",
        "ru": "❌ Вы ещё не подписались на все каналы.",
        "en": "❌ You haven't subscribed to all channels yet.",
    },
    "ask_topic": {
        "uz": "✍️ Taqdimot mavzusini yozing.\n\nMasalan: Alisher Navoiy hayoti va ijodi",
        "ru": "✍️ Напишите тему презентации.\n\nНапример: Жизнь и творчество Алишера Навои",
        "en": "✍️ Write the topic of your presentation.\n\nFor example: The life and works of Alisher Navoi",
    },
    "topic_short": {
        "uz": "⚠️ Mavzu juda qisqa. Kamida 3 ta belgi yozing.",
        "ru": "⚠️ Тема слишком короткая. Напишите минимум 3 символа.",
        "en": "⚠️ The topic is too short. Write at least 3 characters.",
    },
    "topic_long": {
        "uz": "⚠️ Mavzu juda uzun. {n} belgidan qisqaroq yozing.",
        "ru": "⚠️ Тема слишком длинная. Напишите короче {n} символов.",
        "en": "⚠️ The topic is too long. Keep it under {n} characters.",
    },
    "ask_count": {
        "uz": "📑 Mavzu: {topic}\n\nNechta slayd kerak?",
        "ru": "📑 Тема: {topic}\n\nСколько слайдов нужно?",
        "en": "📑 Topic: {topic}\n\nHow many slides do you need?",
    },
    "ask_theme": {
        "uz": "🎨 Dizayn shablonini tanlang:",
        "ru": "🎨 Выберите шаблон оформления:",
        "en": "🎨 Choose a design template:",
    },
    "ask_author": {
        "uz": "👤 Muallif ismini yozing (muqovada ko'rinadi) yoki pastdagi tugmani bosing.",
        "ru": "👤 Напишите имя автора (будет на титульном слайде) или нажмите кнопку ниже.",
        "en": "👤 Write the author's name (shown on the title slide) or press the button below.",
    },
    "author_long": {
        "uz": "⚠️ Ism juda uzun. {n} belgidan qisqaroq yozing.",
        "ru": "⚠️ Имя слишком длинное. Напишите короче {n} символов.",
        "en": "⚠️ The name is too long. Keep it under {n} characters.",
    },
    "generating": {
        "uz": "⏳ Taqdimot tayyorlanmoqda, 30–60 soniya kuting...",
        "ru": "⏳ Готовлю презентацию, подождите 30–60 секунд...",
        "en": "⏳ Creating your presentation, please wait 30–60 seconds...",
    },
    "caption": {
        "uz": "✅ Taqdimot tayyor: {n} slayd\n📌 {topic}\n\nℹ️ Matn sun'iy intellekt yordamida yozilgan. Sana va faktlarni manbadan tekshirib oling.",
        "ru": "✅ Презентация готова: {n} слайдов\n📌 {topic}\n\nℹ️ Текст написан с помощью ИИ. Проверьте даты и факты по источникам.",
        "en": "✅ Presentation ready: {n} slides\n📌 {topic}\n\nℹ️ The text was written by AI. Please verify dates and facts against sources.",
    },
    "caption_images": {
        "uz": "\n🖼 Rasmlar Wikimedia Commons'dan (muallif va litsenziya slayd ostida).",
        "ru": "\n🖼 Изображения с Wikimedia Commons (автор и лицензия указаны под рисунком).",
        "en": "\n🖼 Images from Wikimedia Commons (author and license under the picture).",
    },
    "ai_fail": {
        "uz": "⚠️ Sun'iy intellekt hozir javob bermadi. Limitingiz sarflanmadi. Birozdan keyin qayta urinib ko'ring.",
        "ru": "⚠️ ИИ сейчас не ответил. Ваш лимит не потрачен. Попробуйте ещё раз чуть позже.",
        "en": "⚠️ The AI did not respond. Your limit was not used. Please try again a bit later.",
    },
    "error": {
        "uz": "❌ Xatolik yuz berdi. Limitingiz sarflanmadi. Birozdan keyin qayta urinib ko'ring.",
        "ru": "❌ Произошла ошибка. Ваш лимит не потрачен. Попробуйте ещё раз чуть позже.",
        "en": "❌ Something went wrong. Your limit was not used. Please try again a bit later.",
    },
    "busy": {
        "uz": "⏳ Oldingi taqdimot hali tayyorlanmoqda, kuting.",
        "ru": "⏳ Предыдущая презентация ещё создаётся, подождите.",
        "en": "⏳ Your previous presentation is still being created, please wait.",
    },
    "expired": {
        "uz": "Ma'lumotlar topilmadi. Boshidan boshlash uchun /start bosing.",
        "ru": "Данные не найдены. Нажмите /start, чтобы начать заново.",
        "en": "Data not found. Press /start to begin again.",
    },
    "limit_left": {
        "uz": "📈 Bugungi qolgan limit: {left}/{total}\nLimit har kuni 00:00 da (Toshkent vaqti) yangilanadi.",
        "ru": "📈 Остаток лимита на сегодня: {left}/{total}\nЛимит обновляется каждый день в 00:00 (по Ташкенту).",
        "en": "📈 Remaining limit today: {left}/{total}\nThe limit resets every day at 00:00 (Tashkent time).",
    },
    "limit_unlimited": {
        "uz": "📈 Sizda limit cheklovi yo'q.",
        "ru": "📈 У вас нет ограничений по лимиту.",
        "en": "📈 You have no limit restrictions.",
    },
    "limit_over": {
        "uz": "⛔ Bugungi bepul limit tugadi ({total}/{total}). Ertaga 00:00 dan keyin qayta urinib ko'ring.",
        "ru": "⛔ Бесплатный лимит на сегодня исчерпан ({total}/{total}). Попробуйте завтра после 00:00.",
        "en": "⛔ Today's free limit is used up ({total}/{total}). Try again tomorrow after 00:00.",
    },
    "help": {
        "uz": "ℹ️ Yordam\n\n1. «Yangi taqdimot» tugmasini bosing\n2. Mavzuni yozing\n3. Slayd soni va dizaynni tanlang\n4. Muallif ismini kiriting\n5. Tayyor .pptx faylni oling\n\nBekor qilish: /cancel\nMenyu: /menu",
        "ru": "ℹ️ Помощь\n\n1. Нажмите «Новая презентация»\n2. Напишите тему\n3. Выберите количество слайдов и дизайн\n4. Введите имя автора\n5. Получите готовый файл .pptx\n\nОтмена: /cancel\nМеню: /menu",
        "en": "ℹ️ Help\n\n1. Press “New presentation”\n2. Write the topic\n3. Choose the number of slides and the design\n4. Enter the author's name\n5. Get the ready .pptx file\n\nCancel: /cancel\nMenu: /menu",
    },
    "use_menu": {
        "uz": "Boshlash uchun menyudan «Yangi taqdimot» ni tanlang.",
        "ru": "Чтобы начать, выберите в меню «Новая презентация».",
        "en": "To start, choose “New presentation” in the menu.",
    },
}


def t(key, lang, **kw):
    text = TEXTS[key].get(lang) or TEXTS[key]["uz"]
    return text.format(**kw) if kw else text
