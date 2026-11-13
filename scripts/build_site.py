#!/usr/bin/env python3
"""Static bilingual RUT (MIIT) FAQ site generator. No third-party dependencies.

The generated HTML contains every verified FAQ as visible semantic content so
search engines and assistants can access answers without executing JavaScript.
"""
from __future__ import annotations

import json
import re
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "site"
BASE_URL = "https://banan333.github.io/mirror-of-china/"

LANGUAGES = {
    "ru": {
        "html_lang": "ru",
        "title": "Зеркало Поднебесной — поступление в РУТ (МИИТ) для иностранных студентов",
        "description": "Двуязычная база ответов о поступлении в РУТ (МИИТ): документы, экзамены, стоимость, обучение и общежития. Ссылки на первоисточники университета.",
        "brand": "Зеркало Поднебесной",
        "eyebrow": "РОССИЙСКИЙ УНИВЕРСИТЕТ ТРАНСПОРТА · МОСКВА",
        "heading": "Поступление в РУТ (МИИТ) — без лишних вопросов",
        "lead": "Ответы об учёбе в России для иностранных абитуриентов. На русском и китайском, с прямыми ссылками на документы университета.",
        "locale": "RU / ZH",
        "switch": "中文版",
        "official": "Сайт университета",
        "stat_answers": "ответа на каждом языке",
        "stat_sources": "ссылки на источники",
        "stat_fresh": "обновление базы",
        "browse_title": "Найди нужный ответ",
        "browse_hint": "Выбери раздел или введи запрос. Все ответы доступны для чтения и без поиска.",
        "search_label": "Поиск по вопросам и ответам",
        "search_placeholder": "Например: ЕГЭ, документы, общежитие…",
        "clear": "Сбросить фильтры",
        "results": "Показано",
        "of": "из",
        "empty": "По вашему запросу ничего не найдено. Попробуйте другие слова или откройте все вопросы.",
        "source": "Первоисточник",
        "checked": "Проверено",
        "permalink": "Ссылка на вопрос",
        "disclaimer_title": "Об источниках",
        "disclaimer": "Независимый информационный проект, подготовленный на основе материалов РУТ (МИИТ). Это не официальный сайт университета. Сроки, стоимость и требования уточняйте на сайте РУТ перед подачей заявления.",
        "footer": "Информационный проект · Зеркало Поднебесной",
        "tabs": {"faq": "Все вопросы", "admission": "Поступление", "documents": "Документы", "programs": "Программы", "about": "О вузе"},
        "categories": {"admission": "Поступление", "documents": "Документы", "programs": "Программы", "about": "О вузе"},
    },
    "zh": {
        "html_lang": "zh-CN",
        "title": "天朝之镜｜俄罗斯交通大学（РУТ МИИТ）留学申请指南",
        "description": "俄罗斯交通大学 RUT（MIIT）中文入学问答：申请材料、入学考试、学费、专业选择和宿舍。附俄罗斯交通大学官网来源链接。",
        "brand": "天朝之镜",
        "eyebrow": "俄罗斯交通大学 RUT（MIIT）· 莫斯科",
        "heading": "申请俄罗斯交通大学，从这里开始",
        "lead": "为中国及其他国际申请者整理的实用问答。俄中双语对照，附大学官方网站原始资料链接。",
        "locale": "中文 / RU",
        "switch": "Русская версия",
        "official": "大学官方网站",
        "stat_answers": "条双语问答",
        "stat_sources": "官方资料链接",
        "stat_fresh": "资料更新日期",
        "browse_title": "查找你关心的问题",
        "browse_hint": "可以按主题筛选或输入关键词。所有答案均可直接阅读。",
        "search_label": "搜索问题和答案",
        "search_placeholder": "例如：入学考试、申请材料、宿舍…",
        "clear": "清除筛选",
        "results": "显示",
        "of": "/",
        "empty": "没有找到符合条件的问题，请换个关键词或显示全部。",
        "source": "官方资料来源",
        "checked": "核实日期",
        "permalink": "此问题的链接",
        "disclaimer_title": "资料说明",
        "disclaimer": "本站是基于俄罗斯交通大学（РУТ（МИИТ））官方资料整理的独立信息项目，并非大学官方网站。申请时间、学费及入学要求可能发生变化，请以大学最新官方通知为准。",
        "footer": "独立信息项目 · 天朝之镜",
        "tabs": {"faq": "全部问题", "admission": "入学申请", "documents": "申请材料", "programs": "专业与课程", "about": "学校介绍"},
        "categories": {"admission": "入学申请", "documents": "申请材料", "programs": "专业与课程", "about": "学校介绍"},
    },
}


# Every FAQ belongs to a single section; "faq" shows all sections together.
def section_for(item: dict) -> str:
    category = str(item.get("category", ""))
    item_id = str(item.get("id", ""))
    if category in {"education", "international"}:
        return "programs"
    if category in {"about_university", "student_life"}:
        return "about"
    if any(word in item_id for word in ("documents", "foreign_education", "passport", "translation", "visa")):
        return "documents"
    if category == "admission":
        return "admission"
    return "about"


def load_faq(language: str) -> dict:
    file = DATA_DIR / language / "faq.json"
    data = json.loads(file.read_text(encoding="utf-8-sig"))
    if not isinstance(data.get("items"), list) or not isinstance(data.get("meta"), dict):
        raise ValueError(f"Некорректная структура базы: {file}")
    ids = [record["id"] for record in data["items"]]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Дублирующиеся FAQ ID: {file}")
    return data


def is_safe_url(url: str) -> bool:
    try:
        p = urlsplit(url)
        return p.scheme in {"http", "https"} and bool(p.netloc)
    except ValueError:
        return False


def iso_date(raw: str) -> str:
    try:
        return date.fromisoformat(raw).isoformat()
    except (ValueError, TypeError):
        return ""


def json_script(payload: dict) -> str:
    # Prevent the JSON-LD text from being interpreted as an HTML closing tag.
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def card_html(item: dict, language: str, number: int) -> str:
    t = LANGUAGES[language]
    section = section_for(item)
    item_id = str(item["id"])
    # IDs in this project are alphanumeric plus . - _; restrict other characters.
    fragment = "faq-" + re.sub(r"[^a-zA-Z0-9._-]", "-", item_id)
    question = escape(str(item["question"]))
    answer = escape(str(item["answer"]))
    source = item.get("source", {}) or {}
    source_url = str(source.get("url", ""))
    source_title = str(source.get("title", "")) or t["source"]
    source_link = (
        f'<a href="{escape(source_url, quote=True)}" target="_blank" rel="noopener noreferrer">'
        f'{escape(source_title)} <span aria-hidden="true">↗</span></a>'
        if is_safe_url(source_url) else escape(t["source"] + ": URL не указан")
    )
    verified = iso_date(str(item.get("last_verified", "")))
    checked = (f'<span class="verified">{escape(t["checked"])}: '
               f'<time datetime="{verified}">{verified}</time></span>') if verified else ""
    query = str(item["question"]) + " " + str(item["answer"]) + " " + item_id
    return f'''<article class="faq-card" id="{fragment}" data-section="{section}" data-search="{escape(query.lower(), quote=True)}">
      <div class="faq-topline"><span class="topic topic-{section}">{escape(t["categories"][section])}</span><span class="item-number">{number:02d}</span></div>
      <h2>{question}</h2>
      <p class="answer">{answer}</p>
      <div class="card-bottom"><div class="source-line"><span>{escape(t["source"])}:</span> {source_link}</div>{checked}</div>
      <a class="permalink" href="#{fragment}" aria-label="{escape(t["permalink"], quote=True)}"># {escape(t["permalink"])}</a>
    </article>'''


CSS = r"""
:root { color-scheme: light; --ink:#12243e; --muted:#5d7189; --navy:#0c2344; --blue:#235ed5; --pale:#f5f8ff; --border:#dce5f0; --white:#fff; --gold:#fbc979; }
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body { margin:0; color:var(--ink); background:#f7f9fc; font-family:system-ui,-apple-system,"Segoe UI","Microsoft YaHei","Noto Sans CJK SC",Arial,sans-serif; }
a { color:#1654bb; text-underline-offset:3px; }
a:hover { text-decoration-thickness:2px; }
button,input { font:inherit; }
.sr-label { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
button:focus-visible,a:focus-visible,input:focus-visible { outline:3px solid #f6a73c; outline-offset:3px; }
.wrap { width:min(1100px, calc(100% - 40px)); margin-inline:auto; }
.topbar { background:var(--white); border-bottom:1px solid var(--border); }
.nav-inner { display:flex; justify-content:space-between; align-items:center; gap:22px; padding:16px 0; }
.brand { display:flex; align-items:center; gap:11px; text-decoration:none; color:var(--ink); font-size:18px; font-weight:800; }
.brand small { display:block; color:var(--muted); font-weight:500; font-size:11px; letter-spacing:.06em; text-transform:uppercase; margin-top:2px; }
.logo { width:40px; height:40px; border-radius:12px; background:var(--navy); display:grid; place-items:center; color:#fff; font-weight:900; box-shadow:inset -6px -6px 0 #315f9e; }
.nav-actions { display:flex; align-items:center; flex-wrap:wrap; gap:10px; }
.nav-actions a { font-size:13px; font-weight:700; padding:10px 13px; border:1px solid var(--border); border-radius:999px; text-decoration:none; color:#1d406e; }
.nav-actions .switch { background:#eff5ff; border-color:#d5e4fd; }
.hero { background:radial-gradient(circle at 80% 5%,#244e87 0%,transparent 35%),linear-gradient(125deg,#0d2341,#133e72); overflow:hidden; color:#fff; }
.hero-grid { display:grid; grid-template-columns:minmax(0,1.6fr) minmax(200px,.6fr); align-items:center; gap:38px; padding:67px 0 76px; }
.eyebrow { text-transform:uppercase; font-weight:800; font-size:11px; letter-spacing:.14em; color:#a9c9f6; }
.hero h1 { font-size:clamp(30px,4.7vw,53px); line-height:1.12; letter-spacing:-.035em; max-width:690px; margin:17px 0 20px; }
.hero p { max-width:670px; line-height:1.72; font-size:16px; color:#d7e6f9; margin:0; }
.hero-panel { min-height:225px; border:1px solid #ffffff40; border-radius:24px; background:linear-gradient(145deg,#ffffff19,#ffffff0b); display:grid; align-content:center; justify-items:center; text-align:center; box-shadow:0 14px 50px #07162a25; }
.hero-panel strong { font-size:75px; font-weight:850; letter-spacing:-.075em; line-height:1.2; }
.hero-panel span { font-size:13px; color:#dfecff; margin-top:4px; }
.hero-panel em { margin-top:22px; padding:7px 12px; font-style:normal; font-size:11px; letter-spacing:.09em; color:var(--navy); background:var(--gold); border-radius:99px; font-weight:800; }
.body-content { padding:34px 0 66px; }
.section-head { display:flex; justify-content:space-between; align-items:end; gap:20px; margin-bottom:21px; }
.section-head h2 { font-size:clamp(24px,3vw,31px); margin:0 0 8px; letter-spacing:-.025em; }
.section-head p { margin:0; color:var(--muted); line-height:1.6; }
.toolbar { background:#fff; border:1px solid var(--border); border-radius:18px; box-shadow:0 8px 24px #17315108; padding:18px; margin-bottom:21px; }
.tabs { display:flex; gap:8px; overflow-x:auto; scrollbar-width:thin; padding-bottom:4px; margin-bottom:16px; }
.tab { cursor:pointer; border:1px solid var(--border); border-radius:999px; background:#f9fbff; color:#334b6d; padding:10px 16px; white-space:nowrap; font-weight:700; font-size:13px; }
.tab:hover { border-color:#8eafec; }
.tab[aria-pressed="true"] { color:#fff; background:var(--navy); border-color:var(--navy); }
.search-row { display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
.search-field { flex:1 1 300px; position:relative; }
.search-field svg { position:absolute; left:14px; top:50%; transform:translateY(-50%); color:#6984a6; pointer-events:none; }
.search-field input { display:block; width:100%; background:#fff; border:1px solid #c8d5e7; border-radius:11px; padding:14px 14px 14px 44px; min-height:47px; color:var(--ink); }
.clear { cursor:pointer; border:0; background:transparent; color:#1e56ac; font-weight:700; padding:11px; }
.result-count { font-size:13px; color:var(--muted); font-weight:600; margin:12px 4px 0; }
.faq-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:17px; }
.faq-card { position:relative; display:flex; flex-direction:column; background:#fff; border:1px solid var(--border); padding:25px 26px 22px; border-radius:16px; box-shadow:0 7px 23px #17315107; scroll-margin-top:15px; }
.faq-card:target { outline:3px solid #f5c56a; }
.faq-card[hidden] { display:none !important; }
.faq-topline { display:flex; justify-content:space-between; align-items:center; gap:12px; }
.topic { border-radius:99px; padding:6px 11px; font-size:11px; font-weight:800; color:#244d8a; background:#e9f2ff; }
.topic-documents { color:#88601a; background:#fff2d6; }
.topic-programs { color:#3d6a4b; background:#e8f8eb; }
.topic-about { color:#704f9d; background:#f0eaff; }
.item-number { font-variant-numeric:tabular-nums; color:#93a3b7; font-weight:800; font-size:12px; }
.faq-card h2 { font-size:19px; letter-spacing:-.02em; line-height:1.43; margin:15px 0 11px; }
.answer { white-space:pre-line; line-height:1.72; font-size:14px; color:#324762; margin:0 0 22px; flex:1; overflow-wrap:anywhere; }
.card-bottom { border-top:1px solid #e7edf4; padding-top:14px; display:flex; flex-direction:column; gap:9px; font-size:12px; color:#566c86; }
.source-line { overflow-wrap:anywhere; }
.source-line a { font-weight:750; }
.verified { color:#59728f; }
.permalink { margin-top:11px; align-self:flex-start; color:#6a7f99; font-size:11px; text-decoration:none; }
.permalink:hover { color:#174e99; }
.empty { background:#fff; border:1px dashed #c0cfe4; border-radius:16px; color:#5d7189; text-align:center; padding:35px 20px; }
.notice { margin-top:35px; background:#edf3fb; border:1px solid #d8e4f3; border-left:4px solid #3564a2; border-radius:12px; padding:21px 23px; }
.notice h2 { margin:0 0 7px; font-size:16px; }
.notice p { margin:0; color:#4e627d; font-size:13px; line-height:1.75; }
.footer { border-top:1px solid var(--border); background:#fff; padding:24px 0; color:#687b91; font-size:13px; }
.footer-inner { display:flex; gap:15px; justify-content:space-between; flex-wrap:wrap; }
.footer a { color:#456a9e; }
@media (max-width:800px) { .hero-grid{grid-template-columns:1fr;padding:50px 0 56px} .hero-panel{display:none} .faq-grid{grid-template-columns:1fr} }
@media (max-width:560px) { .wrap{width:min(100% - 28px,1100px)} .nav-inner{align-items:flex-start} .brand{font-size:14px} .nav-actions{justify-content:flex-end} .nav-actions a{font-size:11px;padding:8px} .hero h1{font-size:31px} .hero p{font-size:14px} .toolbar{padding:13px} .faq-card{padding:20px} .nav-actions .official{display:none} }
@media (prefers-reduced-motion:reduce) { html{scroll-behavior:auto} }
"""

JS = r"""
(() => {
  const tabs = Array.from(document.querySelectorAll('.tab'));
  const cards = Array.from(document.querySelectorAll('.faq-card'));
  const input = document.getElementById('search');
  const counter = document.getElementById('results');
  const empty = document.getElementById('empty');
  const reset = document.getElementById('clear-filters');
  const total = cards.length;
  let section = 'faq';
  function apply() {
    const terms = input.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let shown = 0;
    cards.forEach(card => {
      const matchesSection = section === 'faq' || card.dataset.section === section;
      const matchesQuery = terms.every(term => card.dataset.search.includes(term));
      const visible = matchesSection && matchesQuery;
      card.hidden = !visible;
      if (visible) shown++;
    });
    counter.textContent = shown + ' ' + counter.dataset.of + ' ' + total;
    empty.hidden = shown !== 0;
  }
  tabs.forEach(tab => tab.addEventListener('click', () => {
    section = tab.dataset.section;
    tabs.forEach(button => button.setAttribute('aria-pressed', String(button === tab)));
    apply();
  }));
  input.addEventListener('input', apply);
  reset.addEventListener('click', () => {
    input.value = '';
    tabs[0].click();
    input.focus();
  });
  // A deep-linked FAQ is always discoverable, even if the current filter hides it.
  window.addEventListener('hashchange', () => {
    const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target && target.classList.contains('faq-card')) { input.value = ''; tabs[0].click(); }
  });
  apply();
})();
"""


PAGE = r'''<!doctype html>
<html lang="%%LANG%%">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="index,follow,max-snippet:-1">
  <meta name="description" content="%%DESCRIPTION%%">
  <meta name="theme-color" content="#0c2344">
  <title>%%TITLE%%</title>
  <link rel="canonical" href="%%CANONICAL%%">
  <link rel="alternate" hreflang="ru" href="%%RU_URL%%">
  <link rel="alternate" hreflang="zh-CN" href="%%ZH_URL%%">
  <link rel="alternate" hreflang="x-default" href="%%ROOT_URL%%">
  <script type="application/ld+json">%%JSONLD%%</script>
  <style>%%CSS%%</style>
</head>
<body>
  <header class="topbar">
    <div class="wrap nav-inner">
      <a class="brand" href="../index.html" aria-label="%%BRAND%%"><span class="logo" aria-hidden="true">中</span><span>%%BRAND%%<small>Mirror of China</small></span></a>
      <nav class="nav-actions" aria-label="Language and sources">
        <a class="official" target="_blank" rel="noopener noreferrer" href="https://rut-miit.ru/">%%OFFICIAL%% ↗</a>
        <a class="switch" href="../%%OTHER%%/index.html">%%SWITCH%%</a>
      </nav>
    </div>
  </header>
  <section class="hero"><div class="wrap hero-grid">
    <div><div class="eyebrow">%%EYEBROW%%</div><h1>%%HEADING%%</h1><p>%%LEAD%%</p></div>
    <div class="hero-panel"><strong>%%TOTAL%%</strong><span>%%STAT_ANSWERS%%</span><em>%%LOCALE%%</em></div>
  </div></section>
  <main class="wrap body-content" id="content">
    <div class="section-head"><div><h2>%%BROWSE_TITLE%%</h2><p>%%BROWSE_HINT%%</p></div></div>
    <div class="toolbar">
      <nav class="tabs" aria-label="FAQ categories">%%TABS%%</nav>
      <label for="search" class="sr-label">%%SEARCH_LABEL%%</label>
      <div class="search-row"><div class="search-field">
        <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/></svg>
        <input id="search" type="search" autocomplete="off" aria-label="%%SEARCH_LABEL%%" placeholder="%%SEARCH_PLACEHOLDER%%">
      </div><button id="clear-filters" type="button" class="clear">%%CLEAR%%</button></div>
      <p class="result-count">%%RESULTS%%: <span id="results" data-of="%%OF%%">%%TOTAL%% %%OF%% %%TOTAL%%</span></p>
    </div>
    <div class="faq-grid" id="faq-list">%%CARDS%%</div>
    <p id="empty" class="empty" hidden>%%EMPTY%%</p>
    <noscript><p>JavaScript is optional. All verified questions and answers are displayed below.</p></noscript>
    <aside class="notice"><h2>%%DISCLAIMER_TITLE%%</h2><p>%%DISCLAIMER%%</p></aside>
  </main>
  <footer class="footer"><div class="wrap footer-inner"><span>%%FOOTER%%</span><span><time datetime="%%UPDATED%%">%%UPDATED%%</time> · <a href="../index.html">Mirror of China</a></span></div></footer>
  <script>%%JS%%</script>
</body>
</html>
'''


def generate_page(language: str, data: dict) -> str:
    t = LANGUAGES[language]
    items = data["items"]
    canonical = BASE_URL + language + "/"
    structured = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": canonical + "#faq",
        "url": canonical,
        "inLanguage": t["html_lang"],
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
            }
            for item in items
        ],
    }
    tabs = "\n".join(
        f'<button type="button" class="tab" data-section="{key}" aria-pressed="{str(key == "faq").lower()}">{escape(label)}</button>'
        for key, label in t["tabs"].items()
    )
    replacements = {
        "LANG": t["html_lang"], "TITLE": t["title"], "DESCRIPTION": t["description"],
        "BRAND": t["brand"], "OFFICIAL": t["official"], "OTHER": ("zh" if language == "ru" else "ru"),
        "SWITCH": t["switch"], "EYEBROW": t["eyebrow"], "HEADING": t["heading"],
        "LEAD": t["lead"], "TOTAL": str(len(items)), "STAT_ANSWERS": t["stat_answers"],
        "LOCALE": t["locale"], "BROWSE_TITLE": t["browse_title"], "BROWSE_HINT": t["browse_hint"],
        "SEARCH_LABEL": t["search_label"], "SEARCH_PLACEHOLDER": t["search_placeholder"],
        "CLEAR": t["clear"], "RESULTS": t["results"], "OF": t["of"],
        "EMPTY": t["empty"], "DISCLAIMER_TITLE": t["disclaimer_title"], "DISCLAIMER": t["disclaimer"],
        "FOOTER": t["footer"], "UPDATED": iso_date(data["meta"].get("last_updated", "")) or "2026-11-13",
        "CANONICAL": canonical, "ROOT_URL": BASE_URL,
        "RU_URL": BASE_URL + "ru/", "ZH_URL": BASE_URL + "zh/",
    }
    rendered = PAGE
    for key, raw in replacements.items():
        rendered = rendered.replace("%%" + key + "%%", escape(raw, quote=True))
    for key, raw in {"CSS": CSS, "JS": JS, "JSONLD": json_script(structured), "TABS": tabs,
                     "CARDS": "\n".join(card_html(item, language, n) for n, item in enumerate(items, 1))}.items():
        rendered = rendered.replace("%%" + key + "%%", raw)
    if re.search(r"%%[A-Z_]+%%", rendered):
        raise RuntimeError(f"Не подставлены некоторые элементы шаблона {language}")
    return rendered


def generate_homepage() -> str:
    # Separate landing page: lets visitors choose a language instead of relying on redirects.
    return '''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Зеркало Поднебесной — Mirror of China | RUT (MIIT)</title>
<meta name="description" content="Двуязычная база знаний о Российском университете транспорта (РУТ МИИТ) для иностранных абитуриентов. 中文版与俄文版。">
<meta name="robots" content="index,follow"><link rel="canonical" href="''' + BASE_URL + '''">
<link rel="alternate" hreflang="ru" href="''' + BASE_URL + '''ru/">
<link rel="alternate" hreflang="zh-CN" href="''' + BASE_URL + '''zh/">
<link rel="alternate" hreflang="x-default" href="''' + BASE_URL + '''">
<meta name="theme-color" content="#0c2344">
<style>''' + CSS + '''
.home{min-height:75vh;display:grid;place-items:center;background:radial-gradient(circle at 70% 10%,#275287,#0d2341 60%);color:#fff;padding:45px 15px}
.home-card{width:min(720px,100%);text-align:center}.home-card h1{font-size:clamp(38px,6vw,66px);letter-spacing:-.04em;margin:10px 0}.home-card p{line-height:1.65;color:#d7e6f9}
.choices{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:32px 0}.choices a{display:block;text-align:left;background:#fff;color:#18375e;text-decoration:none;border-radius:16px;padding:24px;font-weight:800;font-size:20px}.choices a span{display:block;color:#647894;font-size:13px;font-weight:500;margin-top:9px}
@media(max-width:560px){.choices{grid-template-columns:1fr}}
</style></head><body><main class="home"><div class="home-card"><p class="eyebrow">RUT (MIIT) · MIRROR OF CHINA</p>
<h1>Зеркало Поднебесной</h1><p>Россия ⇄ 中国 · Информация о Российском университете транспорта для иностранных студентов.<br>俄罗斯交通大学国际学生信息指南</p>
<nav class="choices" aria-label="Choose language"><a href="./ru/index.html" lang="ru">Русская версия<span>Поступление, документы, программы и жизнь в университете</span></a><a href="./zh/index.html" lang="zh-CN">中文版<span>俄罗斯交通大学：申请、专业、学费与校园生活</span></a></nav>
<p style="font-size:12px">Независимый информационный проект · 独立信息项目 · <a href="https://rut-miit.ru/" style="color:#fff">Официальный сайт РУТ (МИИТ) / 大学官网 ↗</a></p>
</div></main></body></html>'''


def generate_sitemap(updated: dict[str, str]) -> str:
    urls = [(BASE_URL, max(updated.values())), (BASE_URL + "ru/", updated["ru"]), (BASE_URL + "zh/", updated["zh"])]
    alt = (('ru', BASE_URL + 'ru/'), ('zh-CN', BASE_URL + 'zh/'), ('x-default', BASE_URL))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for loc, lastmod in urls:
        lines.append('  <url>')
        lines.append(f'    <loc>{xml_escape(loc)}</loc>')
        lines.append(f'    <lastmod>{lastmod}</lastmod>')
        for lang, href in alt:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{xml_escape(href)}" />')
        lines.append('  </url>')
    lines.append('</urlset>')
    return '\n'.join(lines) + '\n'


def main():
    databases = {language: load_faq(language) for language in LANGUAGES}
    ru_all = {item['id'] for item in databases['ru']['items']}
    zh_all = {item['id'] for item in databases['zh']['items']}
    if ru_all != zh_all:
        raise ValueError('ID RU и ZH базы не совпадают!')

    published = {}
    for lang, database in databases.items():
        verified = [item for item in database['items'] if item.get('status') == 'verified']
        if not verified:
            raise ValueError(f'{lang.upper()}: нет проверенных записей')
        published[lang] = {**database, 'items': verified}
    if {x['id'] for x in published['ru']['items']} != {x['id'] for x in published['zh']['items']}:
        raise ValueError('ID публикуемых RU/ZH записей не совпадают')

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for lang, data in published.items():
        out = OUTPUT_DIR / lang
        out.mkdir(parents=True, exist_ok=True)
        (out / 'index.html').write_text(generate_page(lang, data), encoding='utf-8')
        n = len(data['items'])
        print(f'{lang.upper()}: опубликовано {n}, пропущено {len(databases[lang]["items"]) - n}')

    (OUTPUT_DIR / 'index.html').write_text(generate_homepage(), encoding='utf-8')
    updated = {lang: iso_date(str(data['meta'].get('last_updated', ''))) or '2026-11-13' for lang, data in published.items()}
    (OUTPUT_DIR / 'sitemap.xml').write_text(generate_sitemap(updated), encoding='utf-8')
    print('Готово: новый дизайн + 5 разделов + поиск + hreflang + canonical + sitemap.xml')
    print(f'Сайт успешно создан: {OUTPUT_DIR}')
    print('Примечание: для GitHub Pages по пути /mirror-of-china/ robots.txt не действует как файл в корне домена.')


if __name__ == '__main__':
    main()
    # MIRROR_UNIFIED_BUILD_PIPELINE_V1
    # Keep all additional pages, navigation, and sitemap URLs when regenerating the site.
    import subprocess as _mirror_subprocess
    import sys as _mirror_sys
    for _mirror_addon in ('build_distribution.py', 'build_guides.py', 'build_checklist.py', 'build_portal.py', 'build_tools.py', 'build_smart_tools.py', 'build_admissions_v5.py'):
        _mirror_path = ROOT / 'scripts' / _mirror_addon
        if not _mirror_path.is_file():
            raise SystemExit(f'Нужный генератор отсутствует: {_mirror_path}')
        print(f'>>> Полная сборка: {_mirror_addon}', flush=True)
        _mirror_subprocess.run([_mirror_sys.executable, str(_mirror_path)], cwd=ROOT, check=True)
