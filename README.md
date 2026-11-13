# PowerPoint Telegram bot (uz / ru / en)

Foydalanuvchi mavzu yozadi, Google Gemini slaydlar matnini tuzadi, bot tayyor `.pptx` faylni yuboradi.

## Imkoniyatlar
- 3 til: o'zbekcha, ruscha, inglizcha (bot matnlari va taqdimot matni shu tilda)
- Oqim: til -> mavzu -> slayd soni (5/7/10/12/15/20) -> dizayn (12 ta) -> muallif ismi -> fayl
- Majburiy kanalga a'zolik (ixtiyoriy)
- Kunlik limit (standart: 3 ta), adminlar uchun cheksiz
- Rasmlar Wikimedia Commons'dan (faqat mos kelsa; muallif va litsenziya slayd ostida)
- AI ishlamasa bot bo'sh taqdimot yubormaydi va limitni sarflamaydi

## Fayllar
| Fayl | Vazifasi |
|---|---|
| `bot.py` | Telegram oqimi, tugmalar, limit, kanal tekshiruvi |
| `ai.py` | Gemini bilan matn yaratish (qayta urinish, zaxira modellar) |
| `deck.py` | `.pptx` yig'ish (12 dizayn, 3 til) |
| `images.py` | Wikimedia'dan mos rasm topish |
| `db.py` | SQLite: til va kunlik limit |
| `i18n.py` | Barcha matnlar (uz/ru/en) |
| `config.py` | Sozlamalar (Environment Variables) |

## Sozlamalar (Render > Environment)
| O'zgaruvchi | Majburiy | Izoh |
|---|---|---|
| `BOT_TOKEN` | ha | @BotFather tokeni |
| `GEMINI_API_KEY` | ha | aistudio.google.com/apikey |
| `GEMINI_MODEL` | yo'q | standart `gemini-3.8-flash`; topilmasa zaxira modellar sinaladi |
| `REQUIRED_CHANNELS` | yo'q | masalan `@kanal1,@kanal2` (faqat @username) |
| `ADMIN_IDS` | yo'q | cheksiz foydalanadigan Telegram ID lar, vergul bilan |
| `DAILY_LIMIT` | yo'q | kuniga nechta taqdimot (standart 3) |
| `MAX_PARALLEL` | yo'q | bir vaqtda nechta taqdimot (standart 2) |
| `KEEPALIVE` | yo'q | `0` bo'lsa, bot o'zini "uyg'otmaydi" |

## Joylash (GitHub + Render)
1. Barcha fayllarni (nuqta bilan boshlanuvchi `.gitignore` va `.env.example` ham) GitHub repository'ga yuklang.
2. Render > New > Blueprint (yoki Web Service: build `pip install -r requirements.txt`, start `python bot.py`).
3. Environment Variables'ga `BOT_TOKEN` va `GEMINI_API_KEY` ni kiriting.
4. Logs'da `Bot ishga tushdi. Gemini kaliti: bor ...` yozuvini kuting, so'ng botga `/start` yuboring.

## Majburiy kanal qanday yoqiladi
1. Botni kanalingizga **administrator** qilib qo'shing (aks holda a'zolikni tekshira olmaydi).
2. `REQUIRED_CHANNELS=@kanal_nomi` qiling.
3. Bot kanalni tekshira olmasa, foydalanuvchilarni qulflab qo'ymaydi: Logs'da xato yozadi va o'tkazib yuboradi.

## Muhim cheklovlar
- Render bepul tarifida disk vaqtinchalik: bot qayta ishga tushsa yoki yangi deploy bo'lsa, kunlik limit hisoblagichi va saqlangan tillar tozalanadi (til qaytadan so'raladi). Doimiy saqlash uchun pullik disk yoki tashqi baza kerak.
- Bepul xizmat uxlab qolishi mumkin; birinchi javob kechikishi normal.
- AI matni xato qilishi mumkin. Caption'da foydalanuvchiga faktlarni tekshirish eslatiladi.

## Xatolarni tekshirish (Render > Logs)
- `BOT_TOKEN environment variable is missing` -> `BOT_TOKEN` qo'shing.
- `GEMINI_API_KEY o'rnatilmagan` -> kalitni qo'shing.
- `Gemini HTTP 429` -> Gemini kvotasi tugagan; birozdan keyin urinib ko'ring.
- `Gemini modeli topilmadi` -> bot keyingi modelni sinaydi; hammasi topilmasa `GEMINI_MODEL` ni yangilang.
- `Kanalni tekshirib bo'lmadi` -> bot kanalda admin emas yoki kanal nomi xato.
- `Conflict: terminated by other getUpdates request` -> bot boshqa joyda ham ishlayapti; eskisini to'xtating.
