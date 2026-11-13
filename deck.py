"""PowerPoint (.pptx) yig'ish. Telegramga bog'liq emas, alohida sinash mumkin."""
from concurrent.futures import ThreadPoolExecutor

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from images import fetch_image

FONT = "Calibri"
MAX_IMAGES = 4
IMG_W, IMG_H = 4.9, 3.9  # dyuym
NS = "http://schemas.openxmlformats.org/presentationml/2006/main"

# id: (nom uz, nom ru, nom en, to'q rang, aksent, och fon)
THEMES = {
    "1": ("Universitet", "Университет", "University", "123B63", "2E75B6", "F3F7FB"),
    "2": ("Qora-oltin", "Чёрно-золотой", "Black & Gold", "20212A", "D6B15D", "F4F0E6"),
    "3": ("Gradient", "Градиент", "Gradient", "4934A4", "E65B91", "F8F5FF"),
    "4": ("Statistika", "Статистика", "Data", "12343B", "0F9D8A", "EEF7F5"),
    "5": ("Minimalistik", "Минимализм", "Minimal", "343A40", "7C8A96", "F7F7F5"),
    "6": ("Texnologik", "Технологии", "Tech", "071D49", "00A6FB", "EDF6FF"),
    "7": ("Iqtisodiyot", "Экономика", "Economy", "174A35", "6CA66A", "F1F7F0"),
    "8": ("Tarix", "История", "History", "5B3825", "B47B48", "F8F0E4"),
    "9": ("Tibbiyot", "Медицина", "Medical", "174B68", "37A6A0", "EFF9FA"),
    "10": ("Tabiat", "Природа", "Nature", "285943", "8DBF67", "F1F7E9"),
    "11": ("Kreativ", "Креатив", "Creative", "3B2063", "F08A4B", "FFF5EF"),
    "12": ("Klassik", "Классика", "Classic", "27364B", "9A8058", "F5F2EA"),
}
LANG_IDX = {"uz": 0, "ru": 1, "en": 2}

LABELS = {
    "uz": {"cover": "TAQDIMOT", "agenda": "REJA", "conclusion": "XULOSA", "by": "Tayyorladi"},
    "ru": {"cover": "ПРЕЗЕНТАЦИЯ", "agenda": "ПЛАН", "conclusion": "ВЫВОДЫ", "by": "Подготовил(а)"},
    "en": {"cover": "PRESENTATION", "agenda": "AGENDA", "conclusion": "CONCLUSION", "by": "Prepared by"},
}


def theme_name(theme_id, lang):
    return THEMES[theme_id][LANG_IDX[lang]]


def _colors(theme_id):
    _, _, _, dark, accent, light = THEMES[theme_id]
    return dark, accent, light


def rgb(h):
    return RGBColor.from_string(h)


def _luma(h):
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b


def add_text(slide, text, x, y, w, h, size=22, color="263238", bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.04)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    f = run.font
    f.name, f.size, f.bold = FONT, Pt(size), bold
    f.color.rgb = rgb(color)
    return box


def add_bullets(slide, bullets, x, y, w, h, dark, accent):
    # kenglik va balandlikka qarab shrift o'lchamini tanlaymiz (matn qutidan chiqib ketmasin)
    size = 14
    for s in (24, 22, 20, 18, 16, 14):
        chars_per_line = max(10, int(w * 72 / (s * 0.52)))
        lines = sum(-(-len(b) // chars_per_line) for b in bullets)
        need = lines * s * 1.25 / 72 + len(bullets) * 0.16
        size = s
        if need <= h:
            break
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(size * 0.55)
        m = p.add_run()
        m.text = "■  "
        m.font.name, m.font.size = FONT, Pt(size * 0.6)
        m.font.color.rgb = rgb(accent)
        t = p.add_run()
        t.text = b
        t.font.name, t.font.size = FONT, Pt(size)
        t.font.color.rgb = rgb(dark)


def _rect(slide, x, y, w, h, color):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(color)
    s.line.fill.background()
    return s


def add_base(prs, dark, accent, light):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = rgb(light)
    _rect(slide, 0, 0, Inches(0.20), prs.slide_height, accent)
    _rect(slide, Inches(0.55), Inches(0.48), Inches(12.0), Inches(0.05), accent)
    return slide


def add_footer(slide, num, label, dark, accent):
    add_text(slide, label, 0.65, 7.08, 9.0, 0.28, 10, dark)
    add_text(slide, str(num), 12.0, 7.06, 0.5, 0.3, 11, accent, True, PP_ALIGN.RIGHT)


def add_fade(slide):
    """Haqiqiy 'fade' slayd o'tish effekti (OOXML)."""
    sld = slide._element
    for old in sld.findall(f"{{{NS}}}transition"):
        sld.remove(old)
    tr = etree.SubElement(sld, f"{{{NS}}}transition")
    tr.set("spd", "med")
    etree.SubElement(tr, f"{{{NS}}}fade")
    clr = sld.find(f"{{{NS}}}clrMapOvr")  # tartib: cSld, clrMapOvr, transition, timing
    if clr is not None:
        sld.remove(tr)
        clr.addnext(tr)


def _title_size(text, base=34):
    n = len(text)
    return base if n <= 40 else base - 4 if n <= 70 else base - 8 if n <= 110 else base - 12


def create_presentation(lang, topic, author, theme_id, content, output_path):
    """Faylni yozadi. (slaydlar soni, rasmlar soni) qaytaradi."""
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    dark, accent, light = _colors(theme_id)
    white = "FFFFFF"
    lb = LABELS[lang]
    label = f"{topic[:60]} • {author}"
    slides_data = content["slides"]

    # rasmlarni parallel yuklab olamiz (eng ko'pi bilan MAX_IMAGES ta)
    wanted = [(i, s["image_query"]) for i, s in enumerate(slides_data) if s.get("image_query")][:MAX_IMAGES]
    images = {}
    if wanted:
        with ThreadPoolExecutor(max_workers=3) as ex:
            futs = {i: ex.submit(fetch_image, q, IMG_W / IMG_H) for i, q in wanted}
            for i, fu in futs.items():
                try:
                    res = fu.result(timeout=60)
                except Exception:
                    res = None
                if res:
                    images[i] = res

    # --- Muqova
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(dark)
    _rect(s, 0, Inches(6.72), prs.slide_width, Inches(0.78), accent)
    sub_color = accent if _luma(accent) > 90 else "D9E2F2"
    add_text(s, lb["cover"], 0.85, 0.8, 11.5, 0.6, 18, sub_color, True)
    add_text(s, topic, 0.85, 1.6, 11.6, 2.6, _title_size(topic), white, True)
    add_text(s, f"{lb['by']}: {author}", 0.9, 4.6, 10.8, 0.55, 20, white)
    add_fade(s)

    # --- Reja
    s = add_base(prs, dark, accent, light)
    add_text(s, lb["agenda"], 0.75, 0.72, 11.7, 0.65, 30, dark, True)
    plan = content["plan"][:5]
    step = min(1.15, 4.9 / len(plan))
    for i, item in enumerate(plan):
        y = 1.75 + i * step
        sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(y), Inches(11.2), Inches(step * 0.7))
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(white)
        sh.line.color.rgb = rgb(accent)
        add_text(s, f"{i + 1:02d}", 1.15, y + step * 0.08, 0.7, 0.45, 20, accent, True)
        add_text(s, item, 2.0, y + step * 0.08, 9.8, 0.5, 20, dark, True)
    add_footer(s, 2, label, dark, accent)
    add_fade(s)

    # --- Asosiy slaydlar
    for i, sd in enumerate(slides_data):
        s = add_base(prs, dark, accent, light)
        add_text(s, sd["title"], 0.75, 0.68, 11.8, 0.8, _title_size(sd["title"], 28), dark, True)
        if i in images:
            img, credit = images[i]
            s.shapes.add_picture(img, Inches(7.6), Inches(1.75), width=Inches(IMG_W), height=Inches(IMG_H))
            add_text(s, credit, 7.6, 1.75 + IMG_H + 0.05, IMG_W, 0.5, 9, "5F6B73")
            add_bullets(s, sd["bullets"], 0.85, 1.75, 6.5, 4.9, dark, accent)
        else:
            add_bullets(s, sd["bullets"], 0.85, 1.75, 11.6, 4.9, dark, accent)
        add_footer(s, i + 3, label, dark, accent)
        if sd.get("notes"):
            s.notes_slide.notes_text_frame.text = sd["notes"]
        add_fade(s)

    # --- Xulosa
    s = add_base(prs, dark, accent, light)
    add_text(s, lb["conclusion"], 0.75, 0.72, 11.7, 0.7, 30, dark, True)
    add_bullets(s, content["conclusion"], 0.95, 1.8, 11.2, 3.8, dark, accent)
    add_text(s, f"{lb['by']}: {author}", 0.95, 5.9, 10.0, 0.5, 18, accent if _luma(accent) < 190 else dark, True)
    add_footer(s, len(prs.slides), label, dark, accent)
    add_fade(s)

    prs.save(output_path)
    return len(prs.slides), len(images)
