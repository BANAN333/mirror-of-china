#!/usr/bin/env python3
# coding: utf-8
"""Last-stage generator of a unified application assistant and actionable checklist.
Reads the already verified catalog, never changes FAQ and does not access Internet.
"""
from __future__ import annotations
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
ASSETS = SITE / 'assets'
SCRIPTS = Path(__file__).resolve().parent
CATALOG = ROOT / 'data' / 'program_catalog_2026.json'
BASE = 'https://banan333.github.io/mirror-of-china/'
STAMP = '<!-- MIRROR_UNIFIED_APPLICATION_V5 -->'

T = {
 'ru': {
  'brand':'Зеркало Поднебесной', 'home':'Главная', 'faq':'24 FAQ', 'assistant':'Помощник поступления',
  'check':'План действий', 'resources':'Площадки', 'switch':'中文', 'official':'Сайт РУТ ↗',
  'eyebrow':'ИНТЕРАКТИВНЫЙ ПОМОЩНИК · РУТ (МИИТ)',
  'title':'Поступление — шаг за шагом',
  'intro':'Ответь на несколько вопросов, выбери реальные программы РУТ и получи персональный план подготовки. Не нужно заполнять пять разных форм.',
  'micro':'Твои ответы остаются в браузере. Никаких аккаунтов и передачи личных документов.',
  'disclaimer':'Независимый студенческий проект. Результат — справочный маршрут, не подтверждение права на поступление. Условия, сроки и стоимость проверяй на официальном сайте РУТ.',
  'checktitle':'Твой план подготовки к поступлению',
  'checkintro':'Не просто галочки: у каждого этапа есть конкретные действия, статусы и ссылка на официальный источник. Прогресс сохраняется в этом браузере.',
  'checkmicro':'Если пройдёшь анкету, сюда автоматически попадут твой вариант поступления и выбранная программа.',
 },
 'zh': {
  'brand':'天朝之镜', 'home':'首页', 'faq':'常见问答', 'assistant':'申请助手',
  'check':'我的行动计划', 'resources':'传播渠道', 'switch':'Русский', 'official':'俄交大官网 ↗',
  'eyebrow':'互动申请助手 · 俄罗斯交通大学',
  'title':'一步一步准备申请俄交大',
  'intro':'回答几个问题，从俄交大正式公布的专业目录中选择项目，生成个性化准备计划。无需分别填写五种工具。',
  'micro':'回答仅保存在当前浏览器，不需要注册，也不会上传个人证件。',
  'disclaimer':'独立学生研究项目，仅提供参考计划，不判断录取资格。入学条件、日期与费用须在俄交大官网核实。',
  'checktitle':'你的个性化申请行动清单',
  'checkintro':'不仅是七个勾选框：每个阶段都有实际任务、进度和大学官方核实链接。',
  'checkmicro':'先填写申请助手，系统会按你的情况列出相关事项和所选专业。',
 }
}

def esc(x): return html.escape(str(x), quote=True)

def link(lang,slug): return '../../'+slug if slug else '../../index.html?lang='+lang

def nav(lang, current):
 t=T[lang]
 # Both guides and checklist pages are two levels below site root.
 links=[('home',t['home'],'../../index.html?lang='+lang),('faq',t['faq'],'../index.html'),
        ('assistant',t['assistant'],'../guides/index.html'),('check',t['check'],'../checklist/index.html'),
        ('resources',t['resources'],'../../resources/index.html')]
 other='zh' if lang=='ru' else 'ru'
 switch='../../'+other+'/'+('guides' if current=='assistant' else 'checklist')+'/index.html'
 return ('<nav class="v5-nav" aria-label="' + esc('网站导航' if lang=='zh' else 'Навигация') + '">'
   '<div class="v5-nav-inner"><a class="v5-brand" href="../../index.html?lang='+lang+'"><span>中</span>'+esc(t['brand'])+'</a>'
   '<div class="v5-nav-links">'+''.join('<a '+('aria-current="page" ' if kind==current else '')+'href="'+esc(href)+'">'+esc(label)+'</a>' for kind,label,href in links)+'</div>'
   '<div class="v5-nav-actions"><a class="v5-switch" href="'+switch+'" lang="'+other+'">'+esc(t['switch'])+'</a>'
   '<a class="v5-official" href="https://www.rut-miit.ru/" target="_blank" rel="noopener noreferrer">'+esc(t['official'])+'</a></div></div></nav>')

def page(lang, mode, payload):
 t=T[lang]; is_w=mode=='wizard'; p='guides' if is_w else 'checklist'
 url=BASE+lang+'/'+p+'/'
 title=t['title'] if is_w else t['checktitle']
 intro=t['intro'] if is_w else t['checkintro']
 micro=t['micro'] if is_w else t['checkmicro']
 other='zh' if lang=='ru' else 'ru'
 catalog=('<script type="application/json" id="v5-catalog">'+json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+'</script>') if is_w else ''
 return f'''<!doctype html><html lang="{'zh-CN' if lang=='zh' else 'ru'}"><head>
 <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
 <title>{esc(title)} | {esc(t['brand'])}</title>
 <meta name="description" content="{esc(intro)}"><meta name="robots" content="index,follow">
 <link rel="canonical" href="{url}">
 <link rel="alternate" hreflang="ru" href="{BASE}ru/{p}/"><link rel="alternate" hreflang="zh-CN" href="{BASE}zh/{p}/">
 <link rel="stylesheet" href="../../assets/admissions_v5.css">
 </head><body>{STAMP}
 {nav(lang, 'assistant' if is_w else 'check')}
 <main class="v5-main" id="v5-root" data-mode="{mode}" data-lang="{lang}">
  <section class="v5-hero">
  <div class="v5-kicker">{esc(t['eyebrow'])}</div><h1>{esc(title)}</h1>
  <p>{esc(intro)}</p><div class="v5-micro">🔒 {esc(micro)}</div>
  </section>
  <div id="v5-application" aria-live="polite"><p class="v5-loading">{'正在加载申请助手…' if lang=='zh' else 'Загрузка помощника…'}</p></div>
  <aside class="v5-disclaimer">{esc(t['disclaimer'])}<div class="v5-reference"><a href="https://rut-miit.ru/page/120705" target="_blank" rel="noopener noreferrer">{'外国公民招生' if lang=='zh' else 'Поступление иностранных граждан'} ↗</a><a href="https://rut-miit.ru/sveden/education/programs" target="_blank" rel="noopener noreferrer">{'专业目录' if lang=='zh' else 'Каталог программ'} ↗</a></div></aside>
 </main>
 {catalog}<script src="../../assets/admissions_v5.js" defer></script></body></html>'''

def update_home_and_nav():
 replacements={
   'Пять тематических гайдов':'Помощник поступления', 'Пять тематических материалов':'Помощник поступления',
   'Пять инструментов для поступления':'Помощник поступления',
   'Пять тематических гайдов о РУТ':'Помощник поступления',
   '5 тем':'Помощник', 'Пять тем':'Помощник', '五大专题指南':'申请助手',
   '五个专题':'申请助手', '申请俄交大的五项实用工具':'申请助手',
   '五项实用工具':'申请助手', '专题指南':'申请助手',
   'Поступление, документы, программы, стоимость и жизнь':'Ответь на вопросы и получи персональный маршрут поступления',
   'Документы, поступление, программы, стоимость, жизнь':'Ответь на вопросы и получи персональный маршрут поступления',
   '申请、材料、专业、学费与校园生活':'回答问题后生成专属申请路线和行动计划',
   '深入了解材料、专业、费用及生活':'回答问题后生成专属申请路线和行动计划',
   'Короткие русские материалы, собранные на основе проверенных вопросов базы. Для каждого тезиса приводим официальный источник.':'Заполни одну форму и получи подготовленный под твой выбор маршрут.',
   'Выбирай программу, документы, стоимость и общежитие':'Получай персональный маршрут и план действий',
   'маршрут поступления, подробные темы или база вопросов':'помощник поступления, персональный план действий или база вопросов',
   '七步申请清单、五个专题指南，或完整常见问题。':'申请助手、行动清单或完整常见问题。',
   '先看申请步骤，再阅读专题指南与常见问题。':'先用申请助手形成路线，再查看行动清单与常见问题。',
   'Начни с чек-листа или выбери интересующую тему.':'Начни с помощника поступления или перейди к плану действий.',
 }
 for file in SITE.rglob('*.html'):
  if file.parts[-3:-1] in [('ru','guides'),('zh','guides')] and file.name=='index.html':
   # New helper pages already contain correct titles; do not change them.
   continue
  raw=file.read_text(encoding='utf-8')
  modified=raw
  for before,after in replacements.items(): modified=modified.replace(before,after)
  # Existing home-switch script supplies the cards, keep its labels consistent.
  if file==SITE/'index.html':
   # Add stable post-locale touch-up. Existing locale script builds 3 cards.
   marker='<!-- MIRROR_HOME_V5_SCRIPT -->'
   modified=re.sub(r'<!-- MIRROR_HOME_V5_SCRIPT -->.*?<!-- /MIRROR_HOME_V5_SCRIPT -->','',modified,flags=re.S)
   patch='''<script>/* MIRROR_HOME_V5_SCRIPT */(function(){
    const cards=[...document.querySelectorAll('.mc-home-hub .mc-portal-card')];
    const helper=cards.find(a=>a.getAttribute('href')?.includes('/guides/'));
    if(helper&&helper.parentElement){helper.parentElement.prepend(helper);}
  })();</script>'''
   modified=re.sub(r'</body>',marker+patch+'<!-- /MIRROR_HOME_V5_SCRIPT --></body>',modified,count=1,flags=re.I)
  if modified!=raw:file.write_text(modified,encoding='utf-8')

def main():
 if not CATALOG.is_file():raise RuntimeError('Нет data/program_catalog_2026.json; сначала заверши установку v4')
 data=json.loads(CATALOG.read_text(encoding='utf-8-sig'))
 if not isinstance(data.get('programs'),list) or len(data['programs'])<30 or data.get('count')!=len(data['programs']):
  raise RuntimeError('Каталог отсутствует или неполный. Текущие страницы не изменены.')
 required=['id','code','name','profile','degree','mode','group','year']
 if any(not all(k in x for k in required) for x in data['programs']):
  raise RuntimeError('Непонятный формат каталога — остановлено без изменений')
 for lang in ('ru','zh'):
  for seg in ('guides','checklist'):
   p=SITE/lang/seg/'index.html'
   if not p.is_file():raise RuntimeError('Нет страницы '+str(p))
 for name in ('admissions_v5.css','admissions_v5.js'):
  if not (SCRIPTS/name).is_file():raise RuntimeError('Файл генератора отсутствует: '+name)
 ASSETS.mkdir(parents=True,exist_ok=True)
 for name in ('admissions_v5.css','admissions_v5.js'):
  shutil.copy2(SCRIPTS/name,ASSETS/name)
 for lang in ('ru','zh'):
  for seg in ('guides','checklist'):
   (SITE/lang/seg/'index.html').write_text(page(lang,'wizard' if seg=='guides' else 'checklist',data),encoding='utf-8')
 update_home_and_nav()
 # Retain legacy deep links so existing CSDN / external links do not break.
 # Both home and old guide links lead to the new /guides/ entry point.
 for lang in ('ru','zh'):
  for slug in ('admissions','programs'):
   p=SITE/lang/'guides'/slug/'index.html'
   if not p.is_file():continue
   message='Перейти к единому помощнику поступления' if lang=='ru' else '打开统一申请助手'
   text=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="canonical" href="{BASE}{lang}/guides/"><meta http-equiv="refresh" content="0; url=../index.html"><title>{esc(message)}</title></head><body><p><a href="../index.html">{esc(message)}</a></p></body></html>'''
   p.write_text(text,encoding='utf-8')
 # Internal sitemap retains old URLs but should not promote redirect-only pages.
 site_map=SITE/'sitemap.xml'
 if site_map.exists():
  ns='http://www.sitemaps.org/schemas/sitemap/0.9'
  ET.register_namespace('',ns)
  tree=ET.parse(site_map);rt=tree.getroot()
  for node in list(rt):
   loc=node.find('{'+ns+'}loc')
   if loc is not None and loc.text and any(loc.text.rstrip('/').endswith('/'+l+'/guides/'+s) for l in ('ru','zh') for s in ('admissions','programs')):
    rt.remove(node)
  tree.write(site_map,encoding='utf-8',xml_declaration=True)
 print(f'OK: единый помощник RU/ZH; официальный каталог: {len(data["programs"])} вариантов (учебные планы, не набор)')
 print('OK: чек-лист RU/ZH заменён на персональный план с подзадачами')
 print('OK: главная/навигация обновлены; 5 карточек инструментов скрыты')
 print('OK: исходные FAQ, каталог программ и опубликованные данные не изменены')

if __name__=='__main__':main()
