#!/usr/bin/env python3
"""Unify navigation of Mirror of China and generate Russian thematic guides.

Run after: build_site.py -> build_distribution.py -> build_guides.py -> build_checklist.py.
Standard library only. Never modifies data/*.json or external dataset files.
"""
from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit, unquote
from html.parser import HTMLParser
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
BASE = "https://banan333.github.io/mirror-of-china/"
META = ROOT / "distribution" / "guidebook" / "guides.json"
BEGIN = "<!-- MIRROR_UNIFIED_NAV_BEGIN -->"
END = "<!-- MIRROR_UNIFIED_NAV_END -->"
HUB_BEGIN = "<!-- MIRROR_PORTAL_HUB_BEGIN -->"
HUB_END = "<!-- MIRROR_PORTAL_HUB_END -->"
STYLE_BEGIN = "<!-- MIRROR_PORTAL_CSS_BEGIN -->"
STYLE_END = "<!-- MIRROR_PORTAL_CSS_END -->"
HEALTH_CHECK = ("site/index.html", "site/ru/index.html", "site/zh/index.html")

GUIDES = {
    "admissions": {
        "title": "Поступление в РУТ (МИИТ): порядок действий и экзамены",
        "desc": "Как разобраться в правилах поступления иностранного абитуриента, экзаменах, сроках и зачислении",
        "intro": "Начни с выбора программы и года приёма. Условия могут различаться для платного обучения, общего конкурса и государственной квоты. Проверяй документы именно для своего способа поступления.",
    },
    "documents": {
        "title": "Документы для поступления в РУТ: что и когда готовить",
        "desc": "Документы, переводы, подтверждение образования, подача заявления и прибытие",
        "intro": "Разделяй документы для подачи заявления, вступительных испытаний, въезда в Россию и заселения. Требования могут различаться в зависимости от гражданства и программы.",
    },
    "programs": {
        "title": "Программы РУТ (МИИТ): транспорт, IT и сотрудничество с КНР",
        "desc": "Выбор направления, уровни образования и международные совместные программы",
        "intro": "Проверяй направление и уровень обучения в актуальном каталоге университета, отдельно уточняй язык преподавания и особенности совместных программ.",
    },
    "tuition": {
        "title": "Стоимость обучения, бюджет и квоты: что проверить",
        "desc": "Как проверять стоимость выбранной программы, оплату обучения и возможные бюджетные основания",
        "intro": "Стоимость зависит от программы и года приёма. Не переноси цифры из старой кампании на новый год; отличай платное обучение от бюджетного конкурса и государственной квоты.",
    },
    "life": {
        "title": "Жизнь студента РУТ: общежитие, приезд и расписание",
        "desc": "Проживание, документы для заселения и первые действия после зачисления",
        "intro": "Наличие общежитий не гарантирует место каждому студенту. После официального зачисления уточни даты прибытия, миграционные документы, страховку и порядок заселения.",
    },
}

NAV_CSS = """
.mc-site-nav{position:sticky;top:0;z-index:1000;background:#fff;border-bottom:1px solid #dbe5f0;box-shadow:0 4px 20px #172e4a13;font-family:system-ui,-apple-system,'Segoe UI','Noto Sans SC',sans-serif;color:#172d49}
.mc-nav-inner{max-width:1160px;margin:auto;min-height:67px;padding:9px 18px;display:flex;align-items:center;flex-wrap:wrap;gap:8px 18px}
.mc-logo{font-weight:850;font-size:15px;color:#15355e;text-decoration:none;display:flex;align-items:center;gap:9px;white-space:nowrap}
.mc-logo-mark{display:grid;place-items:center;border-radius:9px;background:#143e6b;color:#fff;font-size:13px;width:29px;height:29px}
.mc-links{display:flex;align-items:center;gap:5px;flex-wrap:wrap;flex:1}
.mc-links a{color:#3a5576;text-decoration:none;font-size:13px;font-weight:700;padding:9px 11px;border-radius:9px;white-space:nowrap}
.mc-links a:hover{background:#eaf2fc;color:#163e74;text-decoration:none}
.mc-links a.mc-current{background:#e8f1ff;color:#124b93}
.mc-lang{margin-left:auto;white-space:nowrap;text-decoration:none;color:#15528a;border:1px solid #cdddec;border-radius:99px;padding:8px 12px;font-size:12px;font-weight:800}
.mc-site-nav a:focus-visible,.mc-portal-hub a:focus-visible{outline:3px solid #ebaa34;outline-offset:2px}
body>.topbar{display:none!important}
body>.mc-site-nav + .wrap > nav{display:none!important}
.mc-portal-hub{margin:0 auto 24px;max-width:1100px;font-family:system-ui,-apple-system,'Segoe UI','Noto Sans SC',sans-serif;color:#173050}
.mc-portal-hub h2{font-size:clamp(20px,3vw,28px);margin:0 0 6px;color:#173050}
.mc-portal-hub p{margin:0 0 16px;color:#64768e;font-size:14px;line-height:1.6}
.mc-portal-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.mc-portal-card{display:block;background:#fff;border:1px solid #d8e4f1;border-radius:14px;padding:18px 18px;color:#173d70;text-decoration:none;box-shadow:0 6px 25px #1b3f610a}
.mc-portal-card:hover{border-color:#8aafe3;background:#f8fbff;text-decoration:none}
.mc-portal-card strong{font-size:16px;display:block;margin-bottom:6px}
.mc-portal-card small{font-size:12px;display:block;line-height:1.6;color:#536c87}
.mc-home-hub{margin:21px 0 10px;text-align:left}
.mc-home-hub h2{color:#fff;font-size:17px;margin:0 0 12px}
.mc-home-hub .mc-portal-card{color:#173d70}
@media(max-width:720px){.mc-nav-inner{padding:11px 13px;gap:8px}.mc-links{order:3;flex-basis:100%;overflow-x:auto;flex-wrap:nowrap;padding-bottom:3px}.mc-links a{font-size:12px}.mc-lang{margin-left:auto}.mc-portal-cards{grid-template-columns:1fr}.mc-portal-card{padding:15px}}
.mc-nav-actions{margin-left:auto;display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.mc-nav-actions .mc-lang{margin-left:0}
.mc-official{white-space:nowrap;text-decoration:none;color:#fff;background:#194c82;border:1px solid #194c82;border-radius:99px;padding:9px 13px;font-size:12px;font-weight:800}
.mc-official:hover{background:#12385f;color:#fff}
.mc-home-hub{margin-top:28px;margin-bottom:25px;text-align:center}
.mc-home-hub h2{color:#fff;font-size:clamp(22px,3vw,29px)}
.mc-home-hub p{color:#cfdef2;margin-bottom:20px}
.mc-home-hub .mc-portal-cards{text-align:left}
.mc-home-hub .mc-portal-card{min-height:116px;transition:transform .15s,box-shadow .15s}
.mc-home-hub .mc-portal-card:hover{transform:translateY(-2px);box-shadow:0 12px 28px #0519323b}
.home-card{width:min(980px,100%) !important}
.home .mc-disclaimer{font-size:12px;color:#bed0e7;margin-top:17px}
@media(max-width:900px){.mc-nav-inner{gap:8px}.mc-nav-actions{margin-left:auto}.mc-links{order:3;flex-basis:100%;overflow-x:auto;flex-wrap:nowrap;padding:2px 0 4px}}
@media(max-width:540px){.mc-nav-actions{gap:5px}.mc-official,.mc-lang{font-size:11px;padding:8px 9px}.mc-home-hub .mc-portal-card{min-height:0}}

"""


# MIRROR_PORTAL_HOME_V2
HOME_JS = "(() => {\n  // MIRROR_HOME_CARDS_V6: exact same portal with RU / ZH home-language switch.\n  const locale = new URLSearchParams(window.location.search).get('lang') === 'zh' ? 'zh' : 'ru';\n  const zh = locale === 'zh';\n  document.documentElement.lang = zh ? 'zh-CN' : 'ru';\n  document.title = zh\n    ? '天朝之镜 — 俄罗斯交通大学申请助手 | RUT MIIT'\n    : 'Зеркало Поднебесной — помощник поступления в РУТ (МИИТ)';\n  const one = (selector) => document.querySelector(selector);\n  const heroTitle = one('.home-card h1');\n  if (heroTitle) heroTitle.textContent = zh ? '天朝之镜' : 'Зеркало Поднебесной';\n  const lead = one('.home-card > p:not(.eyebrow):not(.mc-disclaimer)');\n  if (lead) lead.innerHTML = zh\n    ? '俄罗斯交通大学（RUT/MIIT）申请信息导航。<br>填写申请助手，获取行动计划，并查阅有来源的常见问答。'\n    : 'Информационный портал о поступлении в РУТ (МИИТ).<br>Заполни анкету, получи план подготовки и уточни детали в FAQ.';\n  const hub = one('.mc-home-hub');\n  if (hub) {\n    const title = hub.querySelector('h2');\n    const intro = hub.querySelector('p');\n    if (title) title.textContent = zh ? '从这里开始' : 'С чего начать';\n    if (intro) intro.textContent = zh\n      ? '先填写申请助手，再跟进准备计划；有疑问时查阅常见问答。'\n      : 'Пройди анкету, получи персональный план действий и уточняй детали в FAQ.';\n    const faqText = [...hub.querySelectorAll('.mc-portal-card')].map(a => a.textContent).join(' ');\n    const faqMatch = faqText.match(/\\d+/);\n    const faqCount = faqMatch ? faqMatch[0] : '24';\n    const entries = zh ? [\n      ['智能申请助手', '按学习形式、入学途径和专业生成个性化申请路线', 'zh/guides/index.html'],\n      ['我的申请准备计划', '跟进材料、考试、入境及报到等具体任务', 'zh/checklist/index.html'],\n      [faqCount + '组常见问答', '查找具体问题并核对大学官方来源', 'zh/index.html'],\n    ] : [\n      ['Помощник поступления', 'Выбери условия поступления и программу — получи персональный маршрут', 'ru/guides/index.html'],\n      ['Мой план подготовки', 'Документы, экзамены, приезд: отслеживай конкретные действия', 'ru/checklist/index.html'],\n      ['База знаний: ' + faqCount + ' FAQ', 'Ответы на вопросы о РУТ со ссылками на официальные источники', 'ru/index.html'],\n    ];\n    hub.setAttribute('aria-label', title ? title.textContent : '');\n    const cards = hub.querySelector('.mc-portal-cards');\n    if (cards) {\n      cards.replaceChildren();\n      entries.forEach(([name, description, href]) => {\n        const a = document.createElement('a');\n        a.className = 'mc-portal-card';\n        a.href = href;\n        const strong = document.createElement('strong');\n        strong.textContent = name;\n        const small = document.createElement('small');\n        small.textContent = description;\n        a.append(strong, small);\n        cards.append(a);\n      });\n    }\n  }\n  const logo = one('.mc-logo');\n  if (logo) {\n    const last = logo.lastChild;\n    if (last && last.nodeType === Node.TEXT_NODE) last.textContent = zh ? '天朝之镜' : 'Зеркало Поднебесной';\n    logo.href = 'index.html?lang=' + locale;\n  }\n  const navLinks = [...document.querySelectorAll('.mc-links a')];\n  const labels = zh ? ['首页', '全部问答', '申请助手', '行动计划', '传播渠道']\n                    : ['Главная', 'Все FAQ', 'Помощник поступления', 'Мой план', 'Площадки'];\n  const targets = ['index.html?lang=' + locale, locale + '/index.html',\n                   locale + '/guides/index.html', locale + '/checklist/index.html', locale + '/resources/index.html'];\n  navLinks.forEach((a, i) => {\n    if (i >= labels.length) return;\n    a.textContent = labels[i];\n    a.href = targets[i];\n  });\n  const langSwitch = one('.mc-lang');\n  if (langSwitch) {\n    langSwitch.href = '?lang=' + (zh ? 'ru' : 'zh');\n    langSwitch.textContent = zh ? 'Русский' : '中文';\n    langSwitch.lang = zh ? 'ru' : 'zh-CN';\n    langSwitch.setAttribute('aria-label', zh ? '切换为俄语' : 'Переключить на китайский');\n  }\n  const official = one('.mc-official');\n  if (official) official.textContent = zh ? '俄交大官网 ↗' : 'Сайт РУТ ↗';\n  const disclaimer = one('.mc-disclaimer');\n  if (disclaimer) disclaimer.textContent = zh\n    ? '独立学生研究项目，非俄罗斯交通大学官方招生平台。'\n    : 'Независимый студенческий проект. Не является официальной приёмной страницей РУТ.';\n})();"
HOME_BEGIN = "<!-- MIRROR_HOME_LOCALE_BEGIN -->"
HOME_END = "<!-- MIRROR_HOME_LOCALE_END -->"

RU_GUIDES_CSS = """
:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#f5f8fc;color:#1b304c;font-family:system-ui,-apple-system,'Segoe UI',sans-serif;line-height:1.7}a{color:#1557a0;text-underline-offset:3px}
.rg-wrap{max-width:940px;margin:34px auto 70px;padding:0 18px}.rg-sheet{background:#fff;border:1px solid #dbe5ef;border-radius:18px;padding:clamp(21px,4vw,44px);box-shadow:0 7px 30px #18385d11}.rg-eyebrow{font-size:12px;font-weight:850;letter-spacing:.08em;color:#476d9b;text-transform:uppercase}.rg-sheet h1{line-height:1.23;font-size:clamp(27px,4vw,40px);margin:12px 0 14px}.rg-lead{font-size:16px;color:#526983;line-height:1.75}.rg-notice{margin:22px 0 30px;padding:15px 18px;border-left:4px solid #d19a3b;background:#fff9ed;color:#6e5528;font-size:14px;border-radius:10px}
.rg-faq{border-top:1px solid #e5ebf3;padding:22px 0}.rg-faq h2{font-size:20px;line-height:1.4;margin:0 0 9px}.rg-faq p{white-space:pre-line;font-size:14px;line-height:1.85;color:#34506b}.rg-meta{display:flex;flex-wrap:wrap;gap:10px;font-size:12px;color:#71829a}.rg-meta a{overflow-wrap:anywhere}.rg-other{margin-top:30px;border-radius:12px;background:#edf5ff;padding:18px}.rg-other a{margin-right:15px}.rg-footer{color:#6c7f96;font-size:12px;margin-top:16px}
"""


def esc(x: str) -> str:
    return html.escape(str(x), quote=True)


def href_from(origin: Path, destination: Path) -> str:
    return os.path.relpath(destination, origin.parent).replace(os.sep, '/')


def remove_marked(text: str, start: str, end: str) -> str:
    if (start in text) != (end in text):
        raise RuntimeError(f"Непарные маркеры {start}")
    if start not in text:
        return text
    return text[:text.index(start)] + text[text.index(end)+len(end):]


def topic_for(item: dict, slug: str) -> bool:
    ident = str(item.get('id', '')).lower()
    cat = str(item.get('category', '')).lower()
    question = str(item.get('question', '')).lower()
    if slug == 'documents':
        return any(s in ident for s in ('documents', 'foreign_education', 'passport', 'translation', 'visa')) or any(s in question for s in ('документ', 'диплом', 'перевод', 'аттестат'))
    if slug == 'programs':
        return cat in ('education', 'international') or any(s in ident for s in ('program', 'joint'))
    if slug == 'tuition':
        return any(s in ident for s in ('tuition', 'budget', 'scholarship', 'payment')) or any(s in question for s in ('стоимость', 'оплат', 'бюджет', 'квот', 'стипенд'))
    if slug == 'life':
        return cat == 'student_life' or any(s in ident for s in ('dormitor', 'schedule', 'student_portal'))
    return cat == 'admission' and not any(s in ident for s in ('foreign_education', 'documents', 'tuition', 'budget', 'scholarship'))


def russian_guides(meta: list[dict]):
    source = ROOT / 'data' / 'ru' / 'faq.json'
    db = json.loads(source.read_text(encoding='utf-8-sig'))
    items = [x for x in db['items'] if x.get('status') == 'verified']
    if len(items) < 5:
        raise RuntimeError('Нужно не менее 5 проверенных FAQ для русских материалов')
    folder = SITE / 'ru' / 'guides'
    folder.mkdir(parents=True, exist_ok=True)
    listing = []
    for record in meta:
        slug = record['slug']
        if slug not in GUIDES:
            raise RuntimeError(f'Неизвестный раздел {slug}')
        info = GUIDES[slug]
        matches = [x for x in items if topic_for(x, slug)]
        if not matches:
            raise RuntimeError(f'Не нашлось RU-FAQ по теме {slug} — проверь структуру базы')
        canonical = BASE + 'ru/guides/' + slug + '/'
        href_zh = BASE + 'zh/guides/' + slug + '/'
        sections = []
        for item in matches:
            src = item.get('source') or {}
            link = src.get('url','') if isinstance(src,dict) else str(src)
            title = src.get('title','') if isinstance(src,dict) else 'Источник'
            source_html = f'<a href="{esc(link)}" target="_blank" rel="noopener noreferrer">{esc(title or "Официальный источник РУТ")} ↗</a>' if urlsplit(link).scheme in ('http','https') else 'Проверь источник в основной базе'
            faq_id = 'faq-' + re.sub(r'[^a-zA-Z0-9._-]', '-', item['id'])
            sections.append(f'<section class="rg-faq" id="{esc(faq_id)}"><h2>{esc(item["question"])}</h2><p>{esc(item["answer"])}</p><div class="rg-meta">{source_html}<span>Проверено: {esc(item.get("last_verified","не указано"))}</span><a href="../../index.html#{esc(faq_id)}">Вопрос в общей базе FAQ</a></div></section>')
        file = folder / slug / 'index.html'
        file.parent.mkdir(parents=True, exist_ok=True)
        page = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="index,follow"><title>{esc(info['title'])} | Зеркало Поднебесной</title><meta name="description" content="{esc(info['desc'])}"><link rel="canonical" href="{esc(canonical)}"><link rel="alternate" hreflang="ru" href="{esc(canonical)}"><link rel="alternate" hreflang="zh-CN" href="{esc(href_zh)}"><style>{RU_GUIDES_CSS}</style></head><body><main class="rg-wrap"><article class="rg-sheet"><div class="rg-eyebrow">РУТ (МИИТ) · РУССКОЯЗЫЧНЫЙ СПРАВОЧНИК</div><h1>{esc(info['title'])}</h1><p class="rg-lead">{esc(info['intro'])}</p><aside class="rg-notice">Это независимый студенческий справочник, а не официальная инструкция университета. Условия приёма, цены и сроки меняются; уточняй их по ссылкам на источники и в актуальных правилах РУТ.</aside>{''.join(sections)}<div class="rg-other"><strong>Что дальше?</strong><p><a href="../../checklist/index.html">Пройти чек-лист поступления</a><a href="../../index.html">Все 24 FAQ</a><a href="../../../zh/guides/{esc(slug)}/index.html">中文版</a></p></div></article><footer class="rg-footer">Зеркало Поднебесной · Независимый образовательный проект · Неофициальная информация</footer></main></body></html>'''
        file.write_text(page, encoding='utf-8')
        listing.append(f'<a class="mc-portal-card" href="{esc(slug)}/index.html"><strong>{esc(info["title"])}</strong><small>{esc(info["desc"])}</small></a>')
    path = folder / 'index.html'
    zh_link = BASE + 'zh/guides/'
    idx = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="index,follow"><title>Тематические материалы о РУТ (МИИТ) | Зеркало Поднебесной</title><meta name="description" content="Пять тем: поступление, документы, программы, стоимость и студенческая жизнь"><link rel="canonical" href="{BASE}ru/guides/"><link rel="alternate" hreflang="zh-CN" href="{zh_link}"><link rel="alternate" hreflang="ru" href="{BASE}ru/guides/"><style>{RU_GUIDES_CSS}</style></head><body><main class="rg-wrap"><div class="rg-sheet"><div class="rg-eyebrow">ЗЕРКАЛО ПОДНЕБЕСНОЙ · ПУТЕВОДИТЕЛЬ</div><h1>Пять тематических материалов о РУТ (МИИТ)</h1><p class="rg-lead">Короткие русские материалы, собранные на основе проверенных вопросов базы. Для каждого тезиса приводим официальный источник.</p><aside class="rg-notice">Материалы не являются официальными объявлениями РУТ. Проверяй требования и сроки своей приёмной кампании.</aside><div class="mc-portal-cards">{''.join(listing)}</div><p style="margin-top:24px"><a href="../checklist/index.html">Чек-лист из 7 шагов</a> · <a href="../index.html">Все FAQ</a> · <a href="../../zh/guides/index.html">中文专题指南</a></p></div></main></body></html>'''
    path.write_text(idx, encoding='utf-8')
    return 6


def resource_page():
    # Two native-language, static platform pages; old /resources/ remains a redirect.
    # MIRROR_RESOURCES_RUZH_V7
    destinations = [
        ('GitHub', 'https://github.com/BANAN333/mirror-of-china',
         'Исходный код, сборка и поддержка данных', '源代码、网站构建和数据维护'),
        ('Hugging Face', 'https://huggingface.co/datasets/smasher143/rut-miit-bilingual-faq',
         'Публичный набор вопросов и ответов RU/ZH', '公开的俄中双语问答数据集'),
        ('ModelScope / 魔搭社区', 'https://modelscope.cn/datasets/smasher143/rut-miit-bilingual-faq',
         'Публикация двуязычного набора данных для разработчиков', '面向开发者的俄中双语数据集'),
        ('CSDN', 'https://blog.csdn.net/smasher143/article/details/170740701',
         'Техническая статья о создании базы знаний', '关于知识库构建的技术文章'),
    ]
    ru_url = BASE + 'ru/resources/'
    zh_url = BASE + 'zh/resources/'
    for lang in ('ru', 'zh'):
        zh = lang == 'zh'
        heading = '项目发布平台' if zh else 'Площадки проекта'
        lead = ('这里汇总了「天朝之镜」项目的公开发布渠道。网站提供申请导航，技术平台发布代码、资料和双语问答数据。'
                if zh else 'Здесь собраны площадки, на которых мы публикуем код, материалы и двуязычную базу вопросов о РУТ (МИИТ).')
        note = ('本项目由学生独立维护，不代表俄罗斯交通大学官方立场。公开发布不意味着搜索引擎或 AI 助手已自动收录、学习或引用这些材料。'
                if zh else 'Это независимый студенческий проект, не официальный ресурс РУТ. Публикация материалов не означает, что поисковики и ИИ уже обнаружили или использовали их.')
        description = ('天朝之镜：关于俄罗斯交通大学的俄中双语问答公开发布渠道'
                       if zh else 'Площадки публикации проекта «Зеркало Поднебесной»: RU/ZH материалы о РУТ')
        cards = ''.join(
            '<a class="mc-portal-card" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer">'
            '<strong>' + esc(name) + ' ↗</strong><small>' + esc(cn if zh else ru) + '</small></a>'
            for name, url, ru, cn in destinations
        )
        canonical = zh_url if zh else ru_url
        body = f'''<!doctype html><html lang="{'zh-CN' if zh else 'ru'}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="index,follow"><title>{esc(heading)} | {'天朝之镜' if zh else 'Зеркало Поднебесной'}</title>
<meta name="description" content="{esc(description)}"><link rel="canonical" href="{esc(canonical)}">
<link rel="alternate" hreflang="ru" href="{esc(ru_url)}">
<link rel="alternate" hreflang="zh-CN" href="{esc(zh_url)}">
<style>{RU_GUIDES_CSS}</style></head><body>
<main class="rg-wrap"><section class="rg-sheet"><div class="rg-eyebrow">{'天朝之镜 · 公开发布渠道' if zh else 'ЗЕРКАЛО ПОДНЕБЕСНОЙ · ПУБЛИКАЦИИ'}</div>
<h1>{esc(heading)}</h1><p class="rg-lead">{esc(lead)}</p>
<div class="mc-portal-cards">{cards}</div><aside class="rg-notice">{esc(note)}</aside></section></main></body></html>'''
        path = SITE / lang / 'resources' / 'index.html'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding='utf-8')
    # Compatibility route for any old links to /resources/. It keeps ?lang=zh.
    old = SITE / 'resources' / 'index.html'
    old.parent.mkdir(parents=True, exist_ok=True)
    old.write_text('''<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="robots" content="noindex,follow"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="2; url=../ru/resources/index.html">
<title>Площадки / 发布平台</title></head><body>
<p><a href="../ru/resources/index.html">Площадки проекта</a> · <a href="../zh/resources/index.html">项目发布平台</a></p>
<script>(function(){
// First preference: explicit URL query string (?lang=zh or ?lang=ru).
var query = new URLSearchParams(location.search).get('lang');
var lang = query === 'zh' || query === 'ru' ? query : null;
// Second: the page from which the visitor opened the legacy link.
if (!lang && document.referrer) {
  try {
    var from = new URL(document.referrer);
    if (from.origin === location.origin) {
      var fromQuery = from.searchParams.get('lang');
      if (fromQuery === 'zh' || fromQuery === 'ru') lang = fromQuery;
      else if (/\/zh(?:\/|$)/.test(from.pathname)) lang = 'zh';
      else if (/\/ru(?:\/|$)/.test(from.pathname)) lang = 'ru';
    }
  } catch (e) { /* No referrer available */ }
}
// Third: remembered choice from the same browser tab.
if (!lang) {
  try {
    var saved = sessionStorage.getItem('mirror-site-language');
    if (saved === 'zh' || saved === 'ru') lang = saved;
  } catch (e) { /* Storage may be blocked */ }
}
if (!lang) lang = 'ru';
location.replace('../' + lang + '/resources/index.html' + location.hash);
})();</script>
</body></html>''', encoding='utf-8')


def page_language(page: Path) -> str:
    rel = page.relative_to(SITE)
    if rel.parts and rel.parts[0] in ('ru','zh'):
        return rel.parts[0]
    return 'ru'


def current_section(page: Path) -> str:
    parts = page.relative_to(SITE).parts
    if not parts or parts == ('index.html',): return 'home'
    if 'guides' in parts: return 'guides'
    if 'checklist' in parts: return 'checklist'
    if 'open-data' in parts: return 'open-data'
    if 'resources' in parts: return 'resources'
    return 'faq'


def nav(page: Path) -> str:
    language = page_language(page)
    section = current_section(page)
    zh = language == 'zh'
    home = page.relative_to(SITE).parts == ('index.html',)
    choices = [
        ('home', '首页' if zh else 'Главная', SITE / 'index.html'),
        ('faq', '全部问答' if zh else 'Все FAQ', SITE / language / 'index.html'),
        ('guides', '申请助手' if zh else 'Помощник поступления', SITE / language / 'guides' / 'index.html'),
        ('checklist', '行动计划' if zh else 'Мой план', SITE / language / 'checklist' / 'index.html'),
        ('resources', '传播渠道' if zh else 'Площадки', SITE / language / 'resources' / 'index.html'),
    ]
    parts = page.relative_to(SITE).parts
    other_lang = 'ru' if zh else 'zh'
    if home:
        counterpart_href = '?lang=zh'  # Homepage stays the homepage, only locale changes.
    elif 'guides' in parts:
        slug = parts[-2] if len(parts) > 3 else None
        counterpart = SITE / other_lang / 'guides' / (slug or '') / 'index.html'
        counterpart_href = href_from(page, counterpart if counterpart.is_file() else SITE / other_lang / 'index.html')
    elif 'resources' in parts:
        counterpart = SITE / other_lang / 'resources' / 'index.html'
        counterpart_href = href_from(page, counterpart)
    elif 'checklist' in parts:
        counterpart = SITE / other_lang / 'checklist' / 'index.html'
        counterpart_href = href_from(page, counterpart if counterpart.is_file() else SITE / other_lang / 'index.html')
    else:
        counterpart_href = href_from(page, SITE / other_lang / 'index.html')
    items = []
    for kind, label, dest in choices:
        if not dest.is_file():
            continue
        attrs = ' class="mc-current" aria-current="page"' if kind == section else ''
        href = href_from(page, dest)
        if kind == 'home' and zh:
            href += '?lang=zh'
        items.append(f'<a href="{esc(href)}"{attrs}>{esc(label)}</a>')
    title = '天朝之镜' if zh else 'Зеркало Поднебесной'
    switch = 'Русский' if zh else '中文'
    official_label = '俄交大官网 ↗' if zh else 'Сайт РУТ ↗'
    return (f'{BEGIN}<nav class="mc-site-nav" aria-label="{"网站导航" if zh else "Навигация по сайту"}">'
            f'<div class="mc-nav-inner"><a class="mc-logo" href="{esc(href_from(page, SITE / "index.html") + ("?lang=zh" if zh else ""))}">'
            f'<span class="mc-logo-mark">中</span>{esc(title)}</a>'
            f'<div class="mc-links">{"".join(items)}</div>'
            f'<div class="mc-nav-actions">'
            f'<a class="mc-lang" href="{esc(counterpart_href)}" lang="{other_lang}">{switch}</a>'
            f'<a class="mc-official" href="https://www.rut-miit.ru/" target="_blank" rel="noopener noreferrer">'
            f'{esc(official_label)}</a></div></div></nav>'
            f'<script data-mirror-language="1">(function(){{'
            f'var q=new URLSearchParams(location.search).get("lang");'
            f'var l=(q==="ru"||q==="zh")?q:"{language}";'
            f'try{{sessionStorage.setItem("mirror-site-language",l)}}catch(e){{}}'
            f'}})();</script>{END}')


def verified_count(lang: str) -> int:
    data = json.loads((ROOT/'data'/lang/'faq.json').read_text(encoding='utf-8-sig'))
    return sum(row.get('status') == 'verified' for row in data['items'])


def hub(page: Path) -> str:
    """The same three-stage journey on homepage and FAQ pages."""
    zh = page_language(page) == 'zh'
    home = page.parent == SITE
    if zh:
        title = '从这里开始'
        lead = '先填写申请助手，再跟进准备计划；有疑问时查阅常见问答。'
        entries = [
            ('智能申请助手', '按学习形式、入学途径和专业生成个性化申请路线', 'guides'),
            ('我的申请准备计划', '跟进材料、考试、入境及报到等具体任务', 'checklist'),
            (f'{verified_count("zh")}组常见问答', '查找具体问题并核对大学官方来源', 'faq'),
        ]
    else:
        title = 'С чего начать'
        lead = 'Пройди анкету, получи персональный план действий и уточняй детали в FAQ.'
        entries = [
            ('Помощник поступления', 'Выбери условия поступления и программу — получи персональный маршрут', 'guides'),
            ('Мой план подготовки', 'Документы, экзамены, приезд: отслеживай конкретные действия', 'checklist'),
            (f'База знаний: {verified_count("ru")} FAQ', 'Ответы на вопросы о РУТ со ссылками на официальные источники', 'faq'),
        ]
    folder = SITE / ('zh' if zh else 'ru')
    destinations = {
        'guides': folder/'guides'/'index.html',
        'checklist': folder/'checklist'/'index.html',
        'faq': folder/'index.html',
    }
    cards = ''.join(
        f'<a class="mc-portal-card" href="{esc(href_from(page, destinations[key]))}">'
        f'<strong>{esc(label)}</strong><small>{esc(desc)}</small></a>'
        for label, desc, key in entries if destinations[key].is_file())
    cls = 'mc-portal-hub mc-home-hub' if home else 'mc-portal-hub'
    return (f'{HUB_BEGIN}<section class="{cls}" aria-label="{esc(title)}">'
            f'<h2>{esc(title)}</h2><p>{esc(lead)}</p>'
            f'<div class="mc-portal-cards">{cards}</div></section>{HUB_END}')


def patch_html(page: Path):
    text = page.read_text(encoding='utf-8-sig')
    # Remove older disconnected promotional panels and any previous portal inserts.
    for begin,end in [
        ('<!-- MIRROR_GUIDES_NAV_START -->','<!-- MIRROR_GUIDES_NAV_END -->'),
        ('<!-- MIRROR_CHECKLIST_NAV_START -->','<!-- MIRROR_CHECKLIST_NAV_END -->'),
        (BEGIN,END),(STYLE_BEGIN,STYLE_END),(HUB_BEGIN,HUB_END),(HOME_BEGIN,HOME_END),
    ]:
        text = remove_marked(text,begin,end)
    if '</head>' not in text.lower() or not re.search(r'<body\b[^>]*>',text,re.I):
        raise RuntimeError(f'Некорректная страница без head/body: {page}')
    css = STYLE_BEGIN + '<style>' + NAV_CSS + '</style>' + STYLE_END
    text = re.sub(r'</head>',css+'</head>',text,count=1, flags=re.I)
    text = re.sub(r'<body\b[^>]*>',lambda m: m.group(0)+nav(page),text,count=1,flags=re.I)
    # Preserve direct index.html links when opened locally (file://), not just on GitHub Pages.
    rel = page.relative_to(SITE).parts
    if rel == ('index.html',):
        text = text.replace('href="./ru/"', 'href="./ru/index.html"')
        text = text.replace('href="./zh/"', 'href="./zh/index.html"')
    # Reciprocal hreflang for Chinese guides (Russian guides are generated above).
    if len(rel) >= 3 and rel[:2] == ('zh','guides'):
        slug = rel[-2] if len(rel) == 4 else None
        alt_ru = BASE+'ru/guides/'+(slug+'/' if slug else '')
        alt_zh = BASE+'zh/guides/'+(slug+'/' if slug else '')
        if 'hreflang="ru"' not in text:
            alts = ('<link rel="alternate" hreflang="ru" href="'+esc(alt_ru)+'">'
                    '<link rel="alternate" hreflang="zh-CN" href="'+esc(alt_zh)+'">')
            text = re.sub(r'</head>',alts+'</head>',text,count=1,flags=re.I)
    # Add prominent route to the guidebook and checklist on home + both FAQ pages.
    if rel == ('index.html',):
        choices = re.search(r'<nav\s+class=["\']choices["\'][^>]*>.*?</nav>', text, re.I|re.S)
        if choices:
            text = text[:choices.start()] + hub(page) + text[choices.end():]
        else:
            intro_end = re.search(r'</h1>\s*<p[^>]*>.*?</p>', text, re.I|re.S)
            if not intro_end:
                raise RuntimeError('Не найден блок главной страницы; обновление остановлено')
            text = text[:intro_end.end()] + hub(page) + text[intro_end.end():]
        # Preserve the official university link in the header, not duplicate it in the footer.
        text, n_notice = re.subn(
            r'<p\s+style=["\']font-size:12px["\']>\s*Независимый информационный проект.*?</p>',
            '<p class="mc-disclaimer">Независимый студенческий проект. Не является официальной приёмной страницей РУТ.</p>',
            text, count=1, flags=re.I|re.S)
        if n_notice != 1:
            raise RuntimeError('Не удалось обновить нижний текст главной страницы')
        text = re.sub(r'</body>', lambda _m: HOME_BEGIN + '<script>' + HOME_JS + '</script>' + HOME_END + '</body>',
                      text, count=1, flags=re.I)
    elif rel in [('ru','index.html'),('zh','index.html')]:
        start = re.search(r'<main\b[^>]*>',text,re.I)
        if start: text = text[:start.end()] + hub(page) + text[start.end():]
    page.write_text(text,encoding='utf-8')


def update_sitemap():
    p = SITE/'sitemap.xml'
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    xhtml = 'http://www.w3.org/1999/xhtml'
    ET.register_namespace('',ns)
    ET.register_namespace('xhtml',xhtml)
    tree=ET.parse(p);root=tree.getroot()
    urls = {u.text for u in root.findall(f'.//{{{ns}}}loc')}
    for slug in [None, *GUIDES.keys()]:
        suffix = 'ru/guides/' if slug is None else f'ru/guides/{slug}/'
        url=BASE+suffix
        if url not in urls:
            child=ET.SubElement(root,f'{{{ns}}}url'); ET.SubElement(child,f'{{{ns}}}loc').text=url; urls.add(url)
    # Replace the legacy bilingual URL with two canonical localized pages.
    for child in list(root.findall(f'{{{ns}}}url')):
        loc = child.find(f'{{{ns}}}loc')
        if loc is not None and loc.text == BASE+'resources/':
            root.remove(child)
            urls.discard(BASE+'resources/')
    for lang in ('ru', 'zh'):
        url = BASE + lang + '/resources/'
        if url not in urls:
            child=ET.SubElement(root,f'{{{ns}}}url')
            ET.SubElement(child,f'{{{ns}}}loc').text=url
            urls.add(url)
    tree.write(p,encoding='utf-8',xml_declaration=True)
    return len(urls)


class LinkParser(HTMLParser):
    def __init__(self): super().__init__();self.refs=[]
    def handle_starttag(self,tag,attrs):
        if tag == 'a':
            href = dict(attrs).get('href')
            if href: self.refs.append(href)


def validate_site(pages: list[Path]):
    bad=[]
    for page in pages:
        p=LinkParser();p.feed(page.read_text(encoding='utf-8'))
        for href in p.refs:
            parsed=urlsplit(href)
            if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith('/'):continue
            target=(page.parent / unquote(parsed.path)).resolve()
            if target.is_dir(): target=target/'index.html'
            if not target.is_file():bad.append((str(page.relative_to(ROOT)),href))
    if bad:
        raise RuntimeError('Найдены неработающие внутренние ссылки:\n'+'\n'.join(f'{p}: {h}' for p,h in bad[:20]))
    return len(pages)


def main():
    for relative in HEALTH_CHECK:
        if not (ROOT/relative).is_file(): raise RuntimeError(f'Не найдена страница {relative}')
    if not META.is_file():
        raise RuntimeError(f'Не найдены источники китайских гайдов: {META}')
    meta=json.loads(META.read_text(encoding='utf-8'))
    slugs=[x['slug'] for x in meta]
    if sorted(slugs)!=sorted(GUIDES):
        raise RuntimeError('Ожидалось 5 тематических гайдов, проверь guides.json')
    for slug in slugs:
        if not (SITE/'zh'/'guides'/slug/'index.html').is_file():
            raise RuntimeError(f'Нет китайского гайда {slug}. Запусти scripts/build_guides.py')
    for lang in ('ru','zh'):
        if not (SITE/lang/'checklist'/'index.html').is_file():
            raise RuntimeError(f'Нет чек-листа {lang}. Запусти scripts/build_checklist.py')
    count=russian_guides(meta)
    resource_page()
    # Only hand-authored html generated by this project, no third-party files.
    pages=[SITE/'index.html',SITE/'ru'/'index.html',SITE/'zh'/'index.html',SITE/'open-data'/'index.html',SITE/'resources'/'index.html',SITE/'ru'/'resources'/'index.html',SITE/'zh'/'resources'/'index.html']
    pages += sorted((SITE/'ru'/'guides').rglob('index.html'))
    pages += sorted((SITE/'zh'/'guides').rglob('index.html'))
    pages += [SITE/lang/'checklist'/'index.html' for lang in ('ru','zh')]
    pages = [x for x in dict.fromkeys(pages) if x.is_file()]
    for page in pages: patch_html(page)
    sitemap_count=update_sitemap()
    n=validate_site(pages)
    for lang in ('ru','zh'):
        t=(SITE/lang/'index.html').read_text(encoding='utf-8')
        expected = verified_count(lang)
        found = t.count('class="faq-card"')
        if found != expected:
            raise RuntimeError(f'FAQ {lang}: найдено {found} карточек вместо {expected}')
        c=(SITE/lang/'checklist'/'index.html').read_text(encoding='utf-8')
        if c.count('class="step"') != 7:
            raise RuntimeError(f'Чек-лист {lang}: не обнаружены все 7 шагов')
    print(f'OK: созданы {count} русских тематических страниц (5 гайдов + каталог)')
    print('OK: общий навбар и маршруты добавлены на главную, RU/ZH FAQ, гайды, чек-листы и открытые данные')
    print(f'OK: проверено {n} HTML-страниц, все локальные ссылки работают; Sitemap: {sitemap_count} URL')
    print('FAQ JSON, данные Hugging Face и ModelScope не изменялись')

if __name__ == '__main__':
    main()
