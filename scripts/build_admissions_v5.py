#!/usr/bin/env python3
# coding: utf-8
"""Last-stage generator of a unified application assistant and actionable checklist.
Reads the already verified catalog, never changes FAQ and does not access Internet.
"""
from __future__ import annotations
import html
import json
import shutil
from pathlib import Path

from site_config import SITE_URL as BASE

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
ASSETS = SITE / 'assets'
SCRIPTS = Path(__file__).resolve().parent
CATALOG = ROOT / 'data' / 'program_catalog_2026.json'
STAMP = '<!-- MIRROR_UNIFIED_APPLICATION_V5 -->'

T = {
 'ru': {
  'brand':'Зеркало Поднебесной',
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
  'brand':'天朝之镜',
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

def page(lang, mode, payload):
 t=T[lang]; is_w=mode=='wizard'; p='guides' if is_w else 'checklist'
 url=BASE+lang+'/'+p+'/'
 title=t['title'] if is_w else t['checktitle']
 intro=t['intro'] if is_w else t['checkintro']
 micro=t['micro'] if is_w else t['checkmicro']
 faq_label = '查看俄交大申请指南与常见问答' if lang == 'zh' else 'Открыть гайды и вопросы о поступлении'
 fallback = '互动功能需要 JavaScript。您仍可阅读所有申请指南和问答。' if lang == 'zh' else 'Для интерактивной анкеты нужен JavaScript. Гайды и ответы доступны без него.'
 catalog=('<script type="application/json" id="v5-catalog">'+json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+'</script>') if is_w else ''
 return f'''<!doctype html><html lang="{'zh-CN' if lang=='zh' else 'ru'}"><head>
 <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
 <title>{esc(title)} | {esc(t['brand'])}</title>
 <meta name="description" content="{esc(intro)}"><meta name="robots" content="index,follow">
 <link rel="canonical" href="{url}">
 <link rel="alternate" hreflang="ru" href="{BASE}ru/{p}/"><link rel="alternate" hreflang="zh-CN" href="{BASE}zh/{p}/">
 <link rel="stylesheet" href="../../assets/admissions_v5.css">
 </head><body>{STAMP}
 <main class="v5-main" id="v5-root" data-mode="{mode}" data-lang="{lang}">
  <section class="v5-hero">
  <div class="v5-kicker">{esc(t['eyebrow'])}</div><h1>{esc(title)}</h1>
  <p>{esc(intro)}</p><div class="v5-micro">🔒 {esc(micro)}</div>
  </section>
  <div id="v5-application" aria-live="polite"><p class="v5-loading">{'正在加载申请助手…' if lang=='zh' else 'Загрузка помощника…'}</p></div>
  <noscript><style>.v5-loading{{display:none}}</style><p>{esc(fallback)} <a href="../index.html">{esc(faq_label)}</a></p></noscript>
  <aside class="v5-disclaimer">{esc(t['disclaimer'])}<div class="v5-reference"><a href="https://rut-miit.ru/page/120705" target="_blank" rel="noopener noreferrer">{'外国公民招生' if lang=='zh' else 'Поступление иностранных граждан'} ↗</a><a href="https://rut-miit.ru/sveden/education/programs" target="_blank" rel="noopener noreferrer">{'专业目录' if lang=='zh' else 'Каталог программ'} ↗</a></div></aside>
 </main>
 {catalog}<script src="../../assets/admissions_v5.js" defer></script></body></html>'''

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
 # V5 runs after the portal generator: reapply the shared menu to fresh pages.
 from build_portal import patch_html as harmonize_nav
 for lang in ('ru', 'zh'):
  for section in ('guides', 'checklist'):
   harmonize_nav(SITE/lang/section/'index.html')
 print(f'OK: единый помощник RU/ZH; официальный каталог: {len(data["programs"])} вариантов (учебные планы, не набор)')
 print('OK: чек-лист RU/ZH заменён на персональный план с подзадачами')
 print('OK: исходные FAQ, каталог программ и опубликованные данные не изменены')

if __name__=='__main__':main()
