#!/usr/bin/env python3
"""Build an open bilingual FAQ dataset and Chinese publication drafts.

Run from the mirror-of-china repo after: python scripts/build_site.py
Only creates/updates explicitly designated distribution files and marked README section.
No network calls, no third-party dependencies, no Git push.
"""
from __future__ import annotations
import csv
import io
import json
import re
from datetime import date
from html import escape as html_escape
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
OUT = SITE / 'open-data'
DIST = ROOT / 'distribution'
BASE = 'https://banan333.github.io/mirror-of-china/'
BEGIN = '<!-- MIRROR-OF-CHINA: OPEN-DATA-BEGIN -->'
END = '<!-- MIRROR-OF-CHINA: OPEN-DATA-END -->'
TODAY = date.today().isoformat()

TOPICS = {
    'admission': {'zh': '入学申请与考试', 'ru': 'Поступление и экзамены'},
    'documents': {'zh': '申请材料与学历认证', 'ru': 'Документы и подтверждение образования'},
    'programs': {'zh': '专业、课程与合作项目', 'ru': 'Программы и сотрудничество'},
    'life': {'zh': '住宿、费用与校园生活', 'ru': 'Проживание, оплата и жизнь в вузе'},
    'university': {'zh': '大学概况与历史', 'ru': 'Об университете'},
}

def topic_for(x: dict) -> str:
    category = str(x.get('category', ''))
    ident = str(x.get('id', ''))
    if 'about_university' in ident or category == 'about_university':
        return 'university'
    if category in ('education','international') or any(k in ident for k in ('program', 'courses')):
        return 'programs'
    if category == 'student_life' or any(k in ident for k in ('tuition', 'payment', 'dormitor', 'scholarship')):
        return 'life'
    if any(k in ident for k in ('documents', 'foreign_education', 'passport', 'translation', 'visa')):
        return 'documents'
    return 'admission'

def load(lang: str) -> dict:
    p = ROOT / 'data' / lang / 'faq.json'
    if not p.exists():
        raise RuntimeError(f'Не найден исходный файл {p}')
    obj = json.loads(p.read_text(encoding='utf-8-sig'))
    if not isinstance(obj.get('items'), list):
        raise RuntimeError(f'Неверный формат {p}: нет items[]')
    return obj

def source_info(x: dict) -> dict:
    s = x.get('source') or {}
    if isinstance(s, dict):
        url = str(s.get('url', '')).strip()
        title = str(s.get('title', '')).strip()
    elif isinstance(s, str):
        url, title = s.strip(), ''
    else:
        url, title = '', ''
    parts = urlsplit(url)
    if parts.scheme not in ('https', 'http') or not parts.netloc:
        raise RuntimeError(f"FAQ {x.get('id')}: отсутствует допустимый URL источника")
    return {'url': url, 'title': title}

def compact(x: dict) -> dict:
    return {
        'id': x['id'], 'category': x.get('category', ''),
        'topic': topic_for(x), 'question': x['question'], 'answer': x['answer'],
        'source': source_info(x), 'last_verified': x.get('last_verified', ''),
        'status': 'verified',
    }

def write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding='utf-8')

def pretty_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'

def csv_data(items: list[dict]) -> str:
    f = io.StringIO(newline='')
    w = csv.writer(f)
    w.writerow(('id','category','topic','question','answer','source_url','source_title','last_verified'))
    for x in items:
        w.writerow((x['id'],x['category'],x['topic'],x['question'],x['answer'],x['source']['url'],x['source']['title'],x['last_verified']))
    return f.getvalue()

def article(lang: str, topic: str, items: list[dict]) -> str:
    cfg = TOPICS[topic]
    cn = lang == 'zh'
    project = '天朝之镜｜俄罗斯交通大学信息指南' if cn else 'Зеркало Поднебесной — справочник о РУТ (МИИТ)'
    header = f'# {cfg[lang]}｜俄罗斯交通大学 RUT (MIIT)' if cn else f'# {cfg[lang]} — РУТ (МИИТ)'
    intro = (f'> 独立资料整理项目「{project}」。以下内容根据大学官方来源编写，非学校官方公告。申请规定、学费及截止日期以大学最新通知为准。\n'
             if cn else f'> Независимый справочник «{project}». Данные основаны на источниках университета, но не являются официальным объявлением. Условия приёма следует перепроверить перед подачей.\n')
    parts = [header, '', intro, '', f'**{"资料整理日期" if cn else "Дата сборки"}：{TODAY}**', '']
    for x in items:
        src = x['source']
        parts += [f"## {x['question']}", '', x['answer'], '',
            f"**{'大学官方来源' if cn else 'Официальный источник'}:** {src['title'] or 'RUT (MIIT)'} — {src['url']}",
            f"**{'核对日期' if cn else 'Проверено'}:** {x['last_verified'] or 'не указана'}", '']
    parts += [
        '---', '',
        '完整问答与俄中双语版本：' + BASE + 'zh/' if cn else 'Все ответы RU/ZH: ' + BASE,
        '开放数据（JSON / CSV）：' + BASE + 'open-data/' if cn else 'Открытые данные: ' + BASE + 'open-data/',
        '大学官网：https://rut-miit.ru/',
        ''
    ]
    return '\n'.join(parts)

def html_dataset_index(count: int, dt: str) -> str:
    rows = [
        ('faq-ru.json','Русский JSON'), ('faq-zh.json','简体中文 JSON'),
        ('faq-pairs.json','RU–ZH paired JSON'), ('faq-bilingual.jsonl','JSONL for search / RAG'),
        ('faq-ru.csv','RU CSV'), ('faq-zh.csv','ZH CSV'), ('README.md','Формат и ограничения / 数据说明'),
    ]
    lis = '\n'.join(f'<li><a href="{html_escape(file,quote=True)}">{html_escape(label)}</a></li>' for file,label in rows)
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>开放数据 / Открытые данные — Зеркало Поднебесной</title>
<meta name="description" content="俄罗斯交通大学 RUT MIIT 双语招生问答开放数据。JSON、CSV、JSONL；附大学官方资料来源。">
<link rel="canonical" href="{BASE}open-data/"><style>
body{{font:16px/1.65 system-ui,'Microsoft YaHei',sans-serif;max-width:820px;margin:50px auto;padding:0 20px;color:#142741}}
h1{{line-height:1.2}}li{{margin:9px 0}}a{{color:#1557af}}.note{{background:#f2f5fa;padding:16px;border-radius:12px}}small{{color:#5a6b7d}}</style></head>
<body><p><a href="{BASE}">← Зеркало Поднебесной / 天朝之镜</a></p>
<h1>开放数据 / Открытые данные</h1>
<p>俄罗斯交通大学（РУТ МИИТ）双语问答 / Двуязычная база ответов о РУТ (МИИТ).</p>
<p><strong>{count} RU/ZH 问答对 / пар FAQ.</strong> <small>Сборка / 生成: {dt}</small></p>
<ul>{lis}</ul><div class="note">独立项目，非大学官方网站。内容依据所附来源整理，使用前请核对最新规定。<br>
Независимый проект, не официальный ресурс университета. Сроки и стоимость требуют проверки по свежим официальным документам.</div>
<p><a href="{BASE}ru/">Русская версия</a> · <a href="{BASE}zh/">中文版</a> · <a href="https://github.com/BANAN333/mirror-of-china">GitHub</a></p></body></html>'''

def update_readme(count: int) -> bool:
    p = ROOT / 'README.md'
    original = p.read_text(encoding='utf-8-sig') if p.exists() else '# Mirror of China\n'
    part = f'''{BEGIN}

## 天朝之镜 / Зеркало Поднебесной — open bilingual university knowledge base

简体中文 / Русский: проверяемая база из **{count} пар вопросов и ответов** о Российском университете транспорта (РУТ/МИИТ) для иностранных абитуриентов. 每条资料包含官网来源和核实日期。

- [中文版 — 中文问答]({BASE}zh/)
- [Русская версия — вопросы и ответы]({BASE}ru/)
- [Открытые машиночитаемые данные / 开放数据]({BASE}open-data/)
- [中文 JSON]({BASE}open-data/faq-zh.json) · [Русский JSON]({BASE}open-data/faq-ru.json)
- [RU/ZH парные записи]({BASE}open-data/faq-pairs.json) · [JSONL]({BASE}open-data/faq-bilingual.jsonl)

**Источник / 来源:** официальные страницы университета указаны в каждой записи. База — независимый информационный проект, **не официальный сайт РУТ**. Проверяйте действующие правила приёма, стоимость и сроки по свежим документам университета.

**Data use:** downloadable static files, no authenticated API and no direct AI integration. Attribution and source-date review are recommended.

{END}'''
    if (BEGIN in original) != (END in original):
        raise RuntimeError('В README непарные маркеры блока. Обновление отменено.')
    if BEGIN in original:
        start = original.index(BEGIN)
        stop = original.index(END, start) + len(END)
        result = original[:start] + part + original[stop:]
    else:
        result = original.rstrip() + '\n\n' + part + '\n'
    if result != original:
        write(p, result)
        return True
    return False

def add_sitemap_url() -> bool:
    p = SITE / 'sitemap.xml'
    if not p.exists():
        return False
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', ns)
    ET.register_namespace('xhtml', 'http://www.w3.org/1999/xhtml')
    tree = ET.parse(p)
    root = tree.getroot()
    expected = BASE+'open-data/'
    exists = any((loc.text or '').strip() == expected for loc in root.findall(f'.//{{{ns}}}loc'))
    if exists:
        return False
    url = ET.SubElement(root, f'{{{ns}}}url')
    loc = ET.SubElement(url, f'{{{ns}}}loc')
    loc.text = expected
    tree.write(p, encoding='utf-8', xml_declaration=True)
    return True

def main() -> None:
    if not (ROOT / 'scripts/build_site.py').exists() or not (SITE / 'zh/index.html').exists():
        raise RuntimeError('Сначала запустите в проекте: python scripts/build_site.py')
    ru = load('ru')
    zh = load('zh')
    ru_verified = {x['id']: compact(x) for x in ru['items'] if x.get('status') == 'verified'}
    zh_verified = {x['id']: compact(x) for x in zh['items'] if x.get('status') == 'verified'}
    if set(ru_verified) != set(zh_verified):
        raise RuntimeError('Несовпадение verified ID RU/ZH. Публикация отменена.')
    if len(ru_verified) < 1:
        raise RuntimeError('Нет проверенных RU/ZH FAQ.')
    ids = list(ru_verified)
    ru_items = [ru_verified[i] for i in ids]
    zh_items = [zh_verified[i] for i in ids]
    pairs = [{'id': i,'topic':ru_verified[i]['topic'], 'ru':ru_verified[i], 'zh':zh_verified[i]} for i in ids]
    for p in pairs:
        if p['ru']['topic'] != p['zh']['topic']:
            raise RuntimeError('Несовпадение темы RU/ZH: '+p['id'])
    OUT.mkdir(parents=True, exist_ok=True)
    write(OUT / 'faq-ru.json', pretty_json({'meta':{'language':'ru','generated':TODAY, 'count':len(ids), 'university':'RUT (MIIT)', 'independent_project':True},'items':ru_items}))
    write(OUT / 'faq-zh.json', pretty_json({'meta':{'language':'zh-CN','generated':TODAY, 'count':len(ids), 'university':'RUT (MIIT)', 'independent_project':True},'items':zh_items}))
    write(OUT / 'faq-pairs.json', pretty_json({'meta':{'generated':TODAY,'count':len(ids)},'items':pairs}))
    rows = [{**x, 'language':lang, 'source_url': x['source']['url']} for lang,items in (('ru',ru_items),('zh',zh_items)) for x in items]
    write(OUT / 'faq-bilingual.jsonl', ''.join(json.dumps(x, ensure_ascii=False)+'\n' for x in rows))
    write(OUT / 'faq-ru.csv', csv_data(ru_items))
    write(OUT / 'faq-zh.csv', csv_data(zh_items))
    readme = f'''# Open bilingual FAQ dataset / 开放问答数据

- Generated: {TODAY}
- Paired RU/ZH FAQ: {len(ids)}
- `faq-ru.json`, `faq-zh.json`: {{meta, items}}. Record fields: `id`, `category`, `topic`, `question`, `answer`, `source` (url and title), `last_verified`, `status`.
- `faq-pairs.json`: each ID paired with RU and ZH objects.
- `faq-bilingual.jsonl`: one record per language/FAQ pair; {2*len(ids)} JSON lines.
- CSV: UTF-8; import in Excel with UTF-8 to preserve Chinese text.

**Use and limits:** Independent project, not affiliated with RUT (MIIT). `verified` is an internal source-check status, not university approval. Admissions conditions, costs and deadlines depend on the relevant admissions year and must be rechecked. All records link to official sources. The files are static downloads, not an API or a promise of AI ingestion.

Home: {BASE}
Repository: https://github.com/BANAN333/mirror-of-china
'''
    write(OUT / 'README.md', readme)
    write(OUT / 'index.html', html_dataset_index(len(ids), TODAY))
    distribution_readme = f'''# Материалы для распространения «Зеркала Поднебесной»

Создано: {TODAY}. Сформировано автоматически из локальных FAQ, не из памяти ассистента.

- `articles/zh/` — тематические статьи на упрощённом китайском. Это **черновики** для ручной публикации на подходящих площадках; не публикуй одинаковые тексты массово.
- `CHANNEL_PLAN.md` — последовательность каналов и контрольные метрики.
- `site/open-data/` — открытые файлы с RU/ZH, CSV и JSONL. Они публикуются через GitHub Pages вместе с сайтом.

**Важное:** не назывaй материалы официальными заявлениями университета. При публикации сохраняй ссылки на документы РУТ и даты проверки. Перед публикацией проверь особенно сроки/цены/правила приёма 2026/27.
'''
    write(DIST / 'README.md', distribution_readme)
    for topic,cfg in TOPICS.items():
        group = [x for x in zh_items if x['topic'] == topic]
        if group:
            write(DIST/'articles'/'zh'/f'{topic}.md', article('zh',topic,group))
    plan = '''# Карта распространения — «Зеркало Поднебесной»

Не публиковать одинаковые рекламные тексты во множестве сообществ. Приоритет — оригинальные полезные материалы с официальными источниками.

## 1. Собственные открытые форматы (делаем сейчас)
- GitHub README с китайскими ключевыми словами и ссылками на прямой JSON.
- `/open-data/` — статические JSON, CSV, JSONL, индексная страница.
- Проверить публичную доступность и загрузку файлов после git push.

## 2. Площадки с готовым читательским интересом (публикация вручную)
- **Zhihu (知乎)**: полезные ответы о поступлении и вариантах обучения, если доступен аккаунт. Китайский номер может потребоваться при регистрации и верификации; не пытаться обходить ограничения.
- **Xiaohongshu (小红书)**: отдельные понятные карточки на китайском, а не копия базы; оценить возможность регистрации и ссылки.
- **Bilibili (哔哩哔哩)**: оригинальные короткие видео-гайды, если появятся материалы/участники; не первоочередной канал.
- **CSDN**: техническая заметка о открытой RU/ZH базе для разработчиков, не общая реклама университета. Требуется проверить возможность публикации и условия.
- **Тематические образовательные порталы о российском образовании**: предложить редакции самостоятельный справочный материал, избегая платных объявлений, выдаваемых за редакционный контент.

## 3. Дополнительные независимые точки доступа
- При необходимости зеркало на независимом хостинге / другом Git-провайдере с той же открытой базой, не копировать бездумно разрозненные версии.
- Для партнёров — разрешённый экспорт JSON/CSV и конкретные ссылки на первоисточники. Никакой «прямой интеграции в DeepSeek» без подтверждения от платформы.

## 4. Измерение
Для каждой публикации фиксировать: дата, площадка, доступный URL, язык, тема, статус, число переходов при наличии.
После 1–2 недель сравнить независимые ответы DeepSeek, Qwen, Doubao, ERNIE с исходным тестом 12 ноября 2026 года; не подсказывать им ссылку. Тест Kimi, если регистрация не пройдена, помечать «не проведён».

Заказчик/официальный сайт РУТ — **отложенный**, а не обязательный для начала распространения канал.
'''
    write(DIST / 'CHANNEL_PLAN.md',plan)
    changed = update_readme(len(ids))
    sitemap = add_sitemap_url()
    # Sanity checks after writing: JSON roundtrip and CSV row count
    for lang in ('ru','zh'):
        obj = json.loads((OUT/f'faq-{lang}.json').read_text(encoding='utf-8'))
        assert len(obj['items']) == len(ids)
    assert sum(1 for _ in (OUT/'faq-bilingual.jsonl').open(encoding='utf-8')) == 2*len(ids)
    print(f'Готово: {len(ids)} пар RU/ZH ({2*len(ids)} строк JSONL)')
    print('Открытые данные:', OUT)
    print('Черновики публикаций:', DIST/'articles'/'zh')
    print('README GitHub:', 'обновлён' if changed else 'уже актуален')
    print('Sitemap:', 'добавлен /open-data/' if sitemap else 'без изменений')
    print('FAQ, сайт RU/ZH и скрипт сборки НЕ менялись.')
    print('Следующий шаг: git add README.md scripts/build_distribution.py site/open-data/ site/sitemap.xml distribution/')

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        raise SystemExit('ОШИБКА: ' + str(exc))
