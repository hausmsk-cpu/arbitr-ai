"""Генерация презентации Arbitr AI для защиты дипломного проекта.

Скрипт собирает deck из 20 слайдов по реальному кейсу
(дело А32-37431/2025, должник Макурин В.В.) и RAG-базе знаний Arbitr AI.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR


ROOT = Path(r"C:\Users\МЕГАЛИТ\Desktop\AI Dip\arbitr-ai")
OUTPUT = ROOT / "docs" / "Arbitr_AI_презентация_защита.pptx"

DARK = "1F3864"
ACCENT = "2E74B5"
LIGHT = "DEEBF7"
GRAY = "595959"
WHITE = "FFFFFF"
GREEN = "538135"
RED = "C00000"

WHITE_S = 18
HEIGHT = 64

def rgba(hex_color: str) -> RGBColor:
    return RGBColor.from_string(hex_color)


def rgb(hex_color: str):  # совместимость с прошлыми версиями
    return rgba(hex_color)


def add_rect(slide, x, y, w, h, fill=None, line_color=None, line_w=0, shape=MSO_SHAPE.RECTANGLE):
    shp = slide.shapes.add_shape(shape, x, y, w, h)
    if fill:
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgba(fill)
    else:
        shp.fill.background()
    if line_color:
        shp.line.color.rgb = rgba(line_color)
        shp.line.width = Pt(line_w)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def add_text(slide, x, y, w, h, text, size=18, color=DARK,
             bold=False, align=PP_ALIGN.LEFT, font="Calibri", spacing=1.0):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = spacing
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = rgba(color)
    run.font.name = font
    return tb


def add_bullets(slide, x, y, w, h, items, size=15, color=GRAY,
                title_size=0, spacing=1.0, tf=None):
    """Добавляет текстовое поле с маркированным списком."""
    if tf is None:
        tb = slide.shapes.add_textbox(x, y, w, h)
        tf = tb.text_frame
    tf.word_wrap = True

    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = spacing
        if isinstance(item, tuple):
            head, body = item
            r1 = p.add_run()
            r1.text = f"▸ {head}"
            r1.font.size = Pt(title_size or size)
            r1.font.bold = True
            r1.font.color.rgb = rgba(DARK)
            r1.font.name = "Calibri"
            if body:
                p2 = tf.add_paragraph()
                p2.line_spacing = spacing
                r2 = p2.add_run()
                r2.text = body
                r2.font.size = Pt(size)
                r2.font.color.rgb = rgba(GRAY)
                r2.font.name = "Calibri"
        else:
            r = p.add_run()
            r.text = f"• {item}"
            r.font.size = Pt(size)
            r.font.color.rgb = rgba(color)
            r.font.name = "Calibri"
    return tf


def add_table(slide, x, y, w, headers, rows, col_widths=None, size=13):
    n_cols = len(headers)
    n_rows = len(rows) + 1
    shape = slide.shapes.add_table(n_rows, n_cols, x, y, w, Pt(28 * n_rows))
    tbl = shape.table

    for c, h in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.text = h
        cell.text_frame.paragraphs[0].runs[0].font.size = Pt(size)
        cell.text_frame.paragraphs[0].runs[0].font.bold = True
        cell.text_frame.paragraphs[0].runs[0].font.color.rgb = rgba(WHITE)
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgba(DARK)

    for r, row in enumerate(rows, 1):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = val
            cell.text_frame.paragraphs[0].runs[0].font.size = Pt(size)
            cell.text_frame.paragraphs[0].runs[0].font.color.rgb = rgba(DARK)
            if r % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = rgba(LIGHT)

    if col_widths:
        for c, w_col in enumerate(col_widths):
            tbl.columns[c].width = Inches(w_col)
    return tbl


def slide_header(slide, title, subtitle=""):
    add_rect(slide, 0, 0, Inches(12.5), Inches(1.0), fill=DARK)
    add_text(slide, Pt(48), Pt(18), Inches(11.5), Pt(45), title,
             size=36, color=WHITE, bold=True)
    add_rect(slide, 0, Pt(82), Inches(12.5), Pt(3), fill=ACCENT)
    if subtitle:
        add_text(slide, Pt(48), Pt(90), Inches(11.5), Pt(28), subtitle,
                 size=15, color=GRAY)


def new_slide(prs, bg=LIGHT):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = rgba(bg if bg else "FFFFFF")
    return slide


def section_slide(prs, num, title):
    slide = new_slide(prs, bg=DARK)
    add_text(slide, Pt(60), Pt(280), Inches(4), Pt(40), f"0{num}",
             size=64, color=ACCENT, bold=True)
    add_text(slide, Pt(60), Pt(340), Inches(10.5), Pt(80), title,
             size=40, color=WHITE, bold=True)
    add_rect(slide, Pt(60), Pt(330), Inches(3), Pt(6), fill=ACCENT)
    return slide


FONT_MAIN = "Calibri"


def main() -> None:
    prs = Presentation()
    prs.slide_width = Inches(12.5)
    prs.slide_height = Inches(7.0)

    # ============ 1. Титул ============
    s = new_slide(prs, bg=DARK)
    add_rect(s, 0, Pt(500), Inches(12.5), Pt(10), fill=ACCENT)
    add_text(s, Pt(60), Pt(180), Inches(11.5), Pt(90),
             "Arbitr AI", size=72, color=WHITE, bold=True)
    add_text(s, Pt(60), Pt(280), Inches(11.5), Pt(45),
             "AI-платформа автоматизации финансового управляющего", size=30, color=LIGHT)
    add_text(s, Pt(60), Pt(345), Inches(11.5), Pt(30),
             "в делах о банкротстве физических лиц", size=24, color=WHITE)
    add_text(s, Pt(60), Pt(430), Inches(11.5), Pt(30),
             "Дипломная работа  ·  А32-37431/2025  ·  «Arbitr AI»", size=16, color=LIGHT)
    add_text(s, Pt(60), Pt(600), Inches(11.5), Pt(25),
             "16.09.2026", size=14, color="A6A6A6")

    # ============ 2. Проблема ============
    s = new_slide(prs)
    slide_header(s, "Проблема финансового управляющего")
    add_bullets(s, Pt(60), Pt(130), Inches(11.3), Inches(4.5), [
        ("Ручная рутина — 60% времени", "Запросы в 34 органа, 338 документов, реестры, отчёты — вручную"),
        ("Риск пропуска сроков", "Ответственность по ст. 14.13 КоАП, штрафы до 300 000 ₽"),
        ("Разрозненные источники", "ФНС, Росреестр, ФССП, ЗАГС, банки — каждый со своим форматом"),
        ("Ошибки в документах", "Ручной ввод → опечатки, неполнота, отказ органов"),
    ], size=16)

    # ============ 3. Решение ============
    s = new_slide(prs)
    slide_header(s, "Решение — Arbitr AI")
    add_bullets(s, Pt(60), Pt(130), Inches(11.3), Inches(4.5), [
        ("AI-ядро", "Генерация 31 типа юридических документов на основе реального кейса"),
        ("RAG-поиск", "338 RAG-чанков по делу А32-37431/2025 — мгновенный доступ к практике"),
        ("Автоматизация запросов", "34 интеграции: ФНС, Росреестр, ФССП, Почта России"),
        ("Контроль сроков", "Дашборд, напоминания, аналитика — ни одного пропущенного дедлайна"),
    ], size=16)

    # ============ 4. Кейс ============
    s = new_slide(prs)
    slide_header(s, "Реальный кейс: А32-37431/2025")
    add_table(s, Pt(60), Pt(120), Inches(11.3), [
        "Параметр", "Значение"
    ], [
        ["Должник", "Макурин В.В., 18.02.1955"],
        ["Суд", "АС Краснодарского края"],
        ["Процедура", "Реализация имущества гражданина"],
        ["Документов в деле", "34 PDF → 338 RAG-чанков"],
        ["Особенность", "Смерть должника, параграф 4 гл. X, наследники"],
    ], size=14)

    # ============ 5. Раздел: AI ============
    section_slide(prs, 1, "AI-ядро")

    # ============ 6. Архитектура ============
    s = new_slide(prs)
    slide_header(s, "Архитектура")
    add_rect(s, Pt(60), Pt(140), Inches(3.6), Inches(1.4), fill=DARK)
    add_text(s, Pt(80), Pt(170), Inches(3), Pt(60), "Frontend\nReact + TS", size=16, color=WHITE, align=PP_ALIGN.CENTER)
    add_rect(s, Pt(450), Pt(140), Inches(3.6), Inches(1.4), fill=ACCENT)
    add_text(s, Pt(470), Pt(170), Inches(3), Pt(60), "Backend\nFastAPI + SQLAlchemy", size=16, color=WHITE, align=PP_ALIGN.CENTER)
    add_rect(s, Pt(840), Pt(140), Inches(3.6), Inches(1.6), fill=GREEN)
    add_text(s, Pt(840), Pt(160), Inches(3.6), Pt(60), "AI-ядро\nLLM + RAG", size=16, color=WHITE, align=PP_ALIGN.CENTER)
    add_bullets(s, Pt(60), Pt(340), Inches(11.3), Inches(3), [
        ("Python 3.12 + FastAPI", "30+ эндпоинтов, JWT, роли"),
        ("PostgreSQL + Redis + MinIO", "Async SQLAlchemy, Alembic миграции"),
        ("RAG + 31 шаблон документов", "Знания из реального кейса"),
    ], size=15)

    # ============ 7. AI-генерация ============
    s = new_slide(prs)
    slide_header(s, "Генерация документов AI")
    add_table(s, Pt(60), Pt(120), Inches(11.3), [
        "Тип документа", "Описание"
    ], [
        ["Запрос в ФНС", "Справки 2-НДФЛ, счета, участие в юрлицах"],
        ["Запрос в Росреестр", "Выписки ЕГРН, объекты недвижимости"],
        ["Уведомление кредиторам", "Реестр требований кредиторов"],
        ["Запрос супругу", "Совместное имущество, счета"],
        ["Ходатайства в суд", "Завершение процедуры, отчёты"],
    ], size=14)
    add_bullets(s, Pt(60), Pt(400), Inches(11.3), Inches(2), [
        ("31 тип документа", "На основе реальных шаблонов кейса"),
        ("AI + шаблоны", "Гибрид: RAG-контекст + юридические шаблоны"),
    ], size=15)

    # ============ 8. RAG ============
    s = new_slide(prs)
    slide_header(s, "RAG — база знаний из кейса")
    add_table(s, Pt(60), Pt(120), Inches(11.3), [
        "Метрика", "Значение"
    ], [
        ["PDF-документов", "34"],
        ["RAG-чанков", "338"],
        ["Типов документов для генерации", "31"],
        ["Обучающих примеров", "33"],
    ], size=14)
    add_bullets(s, Pt(60), Pt(380), Inches(11.3), Inches(2), [
        ("TF-IDF поиск", "Ранжирование по релевантности, 2632 термина"),
        ("Контекст для LLM", "Финансовый анализ → генерация запросов"),
    ], size=15)

    # ============ 9. Раздел: Harness ============
    section_slide(prs, 2, "Harness CI/CD")

    # ============ 10. Пайплайны ============
    s = new_slide(prs)
    slide_header(s, "Harness Pipeline")
    add_bullets(s, Pt(60), Pt(130), Inches(11.3), Inches(4.5), [
        ("build-and-test-backend", "15 пайплайнов: build, test, trivy, docker"),
        ("deploy-stage", "3 окружения: dev / stage / prod"),
        ("deploy-prod", "Blue/Green + канареечные флаги"),
        ("Feature Flags", "8 флагов: Росреестр, AI-анализ, почта, нотариат"),
        ("Secrets Management", "ФНС, Росреестр, ФССП, Почта России — защищённо"),
    ], size=16)

    # ============ 11. Окружения ============
    s = new_slide(prs)
    slide_header(s, "Окружения и флаги")
    add_table(s, Pt(60), Pt(120), Inches(11.3), [
        "Окружение", "Назначение", "Флаги"
    ], [
        ["dev", "Разработка", "FF: dev environment"],
        ["stage", "Тестирование", "FF: staging"],
        ["prod", "Продакшен", "FF: production + approval"],
    ], size=14)
    add_bullets(s, Pt(60), Pt(350), Inches(11.3), Inches(2), [
        ("8 feature flags", "поэтапное включение функций безопасности"),
        ("Автооткат", "при провале проверок — rollback в Harness"),
    ], size=15)

    # ============ 12. Раздел: Продукт ============
    section_slide(prs, 3, "Продукт и бизнес")

    # ============ 13. Backend API ============
    s = new_slide(prs)
    slide_header(s, "Backend API — 19 эндпоинтов")
    add_table(s, Pt(60), Pt(120), Inches(11.3), [
        "Модуль", "Эндпоинты"
    ], [
        ["Auth", "/register, /login, /me"],
        ["Cases", "CRUD дел, должников, кредиторов"],
        ["Requests", "Запросы, статусы, интеграции"],
        ["AI", "/generate, /search, /stats"],
    ], size=14)
    add_bullets(s, Pt(60), Pt(360), Inches(11.3), Inches(2), [
        ("14 тестов — зелёные", "API, AI, модели"),
        ("JWT + bcrypt", "безопасная аутентификация"),
    ], size=15)

    # ============ 14. Frontend ============
    s = new_slide(prs)
    slide_header(s, "Frontend — кабинет управляющего")
    add_bullets(s, Pt(60), Pt(130), Inches(11.3), Inches(4.5), [
        ("React 18 + TypeScript + Vite", "Fast dev-сервер, HMR"),
        ("Ant Design", "Дашборд, карточка дела, таблицы"),
        ("TanStack Query", "Кэширование, фетчинг API"),
        ("AI-панель", "Генерация документов в один клик"),
    ], size=16)

    # ============ 15. Тестирование ============
    s = new_slide(prs)
    slide_header(s, "Тестирование — 14 тестов ✅")
    add_table(s, Pt(60), Pt(120), Inches(11.3), [
        "Тест", "Покрытие"
    ], [
        ["API (cases, auth, requests)", "✅ 5/5"],
        ["AI (генерация, RAG, типы)", "✅ 9/9"],
        ["CRUD-флоу (case → debtor)", "✅ 1/1"],
    ], size=14)
    add_bullets(s, Pt(60), Pt(300), Inches(11.3), Inches(2), [
        ("pytest + httpx + ASGI", "быстрый цикл, без внешней БД"),
        ("Покрытие кода", "высокое, отчёт coverage.xml"),
    ], size=15)

    # ============ 16. Бизнес-модель ============
    s = new_slide(prs)
    slide_header(s, "Бизнес-модель")
    add_bullets(s, Pt(60), Pt(130), Inches(11.3), Inches(4.5), [
        ("Подписка B2B SaaS", "Базовый 7 990 ₽ / Про 14 990 ₽ / Корп от 29 990 ₽"),
        ("Выручка Year 2", "50,4 млн ₽ ARR"),
        ("Выручка Year 3", "540 млн ₽ ARR"),
        ("Точка безубыточности", "Q4 Year 1"),
        ("Модель в Excel", "Бизнес-план Arbitr AI.xlsx — 11 листов"),
    ], size=16)

    # ============ 17. Команда ============
    s = new_slide(prs)
    slide_header(s, "Команда и роли")
    add_table(s, Pt(60), Pt(120), Inches(11.3), [
        "Роль", "Кол-во"
    ], [
        ["Архитектор / Team Lead", "1"],
        ["Backend-разработчик", "2"],
        ["Frontend-разработчик", "1"],
        ["AI/ML-инженер", "1"],
        ["DevOps (Harness)", "1"],
    ], size=14)

    # ============ 18. Дорожная карта ============
    s = new_slide(prs)
    slide_header(s, "Дорожная карта — 16 спринтов")
    add_bullets(s, Pt(60), Pt(130), Inches(11.3), Inches(4.5), [
        ("Спринты 1-2", "Карточка дела, аутентификация"),
        ("Спринты 3-6", "Запросы в ФНС, Росреестр, ФССП, Почту"),
        ("Спринты 7-10", "AI-генерация документов + RAG"),
        ("Спринты 11-14", "Отчёты, аналитика, особые случаи"),
        ("Спринты 15-16", "Тестирование, пилот, релиз"),
    ], size=16)

    # ============ 19. Итоги ============
    s = new_slide(prs)
    slide_header(s, "Итоги")
    add_bullets(s, Pt(60), Pt(130), Inches(11.3), Inches(4.5), [
        ("Готовый MVP", "backend + frontend + AI + Harness, 14/14 тестов ✅"),
        ("Реальный кейс", "дело А32-37431/2025: 34 PDF → RAG-база"),
        ("AI-генерация", "31 тип юридических документов"),
        ("CI/CD в Harness", "15 пайплайнов, 3 окружения, feature flags"),
        ("Бизнес-план", "финансовая модель, команда, дорожная карта"),
    ], size=16)

    # ============ 20. Спасибо ============
    s = new_slide(prs, bg=DARK)
    add_text(s, Pt(100), Pt(260), Inches(10.5), Pt(70),
             "Спасибо за внимание!", size=54, color=WHITE, bold=True)
    add_text(s, Pt(100), Pt(360), Inches(10.5), Pt(40),
             "Arbitr AI — AI-платформа финансового управляющего", size=24, color=LIGHT)
    add_rect(s, Pt(100), Pt(430), Inches(3), Pt(6), fill=ACCENT)

    prs.save(str(OUTPUT))
    print(f"OK: {OUTPUT} | слайдов: {len(prs.slides.__iter__.__self__._sldIdLst)}")


if __name__ == "__main__":
    main()