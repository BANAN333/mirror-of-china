#!/usr/bin/env python3
"""Generate bilingual admission checklists and link them from Mirror of China.

Run AFTER build_site.py / build_distribution.py / build_guides.py.
No FAQ or Python generator files are modified. Standard library only.
"""
from __future__ import annotations
from datetime import date
from html import escape
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
BASE = 'https://banan333.github.io/mirror-of-china/'
START = '<!-- MIRROR_CHECKLIST_NAV_START -->'
END = '<!-- MIRROR_CHECKLIST_NAV_END -->'

# Each stage is illustrative. Requirements always depend on the particular
# admissions channel, qualification, nationality, and current year's rules.
STEPS = [
    {
        'zh': ('选择专业与学习方式', '在官方专业目录中核对专业、培养层次、授课语言和学费。不要只凭中文招生广告选择项目。'),
        'ru': ('Выбрать программу и форму обучения', 'Открой официальный каталог: проверь программу, уровень, язык преподавания и стоимость. Не полагайся только на рекламные описания.'),
        'guide': 'programs', 'official': 'https://rut-miit.ru/admissions/degrees',
    },
    {
        'zh': ('确认申请渠道和当年日期', '核对当前招生年份，以及自费、预算或政府配额对应的规则与截止日期。2026/27学年的日期不能直接用于下一年。'),
        'ru': ('Проверить условия и сроки текущего года', 'Выясни, идёшь ли по платному приёму, общему конкурсу или квоте, и проверь сроки именно своей кампании. Даты 2026/27 нельзя переносить на следующий год.'),
        'guide': 'admissions', 'official': 'https://rut-miit.ru/admissions/',
    },
    {
        'zh': ('整理护照与学历材料', '准备护照、学历证明及成绩附件；按照具体要求准备俄语翻译、公证或认证。申请、入境及住宿文件不能混为一谈。'),
        'ru': ('Собрать документы', 'Подготовь паспорт, документ об образовании и приложение с оценками. Проверь, какие переводы, заверения или подтверждения нужны именно тебе. Не путай документы для подачи, въезда и заселения.'),
        'guide': 'documents', 'official': 'https://rut-miit.ru/page/120705',
    },
    {
        'zh': ('按学校指引提交申请', '选择官方页面提供的适用提交方式，填写申请并检查附件；保存提交记录，留意学校的回复和申请状态。'),
        'ru': ('Подать заявление', 'Выбери доступный способ подачи из официальной инструкции, заполни заявление, проверь вложения и следи за статусом и письмами университета.'),
        'guide': 'admissions', 'official': 'https://rut-miit.ru/page/171057',
    },
    {
        'zh': ('确认并完成入学考试或选拔', '查看所选专业对应的考试安排；符合条件的外国申请者可参加学校组织的俄语入学测试。不同申请渠道可能适用不同选拔程序。'),
        'ru': ('Пройти вступительные испытания или отбор', 'Проверь экзамены по выбранной программе. Иностранные поступающие при соблюдении условий могут сдавать внутренние испытания на русском; для других каналов действуют свои процедуры.'),
        'guide': 'admissions', 'official': 'https://rut-miit.ru/admissions/office/94725',
    },
    {
        'zh': ('核对录取结果与后续手续', '在官方系统确认是否已录取；如属于合同制学习，按学校要求签订合同并缴费。未收到正式录取结果前不要假定已被录取。'),
        'ru': ('Проверить зачисление', 'Проверь официальный результат зачисления. При платном обучении уточни договор и оплату. До официального подтверждения не считай себя зачисленным.'),
        'guide': 'tuition', 'official': 'https://rut-miit.ru/admissions/',
    },
    {
        'zh': ('准备抵俄、住宿与报到', '确认签证与入境要求、医疗保险、移民登记、报到日期和宿舍申请。学校设有宿舍，但不能默认每位外国学生都有床位。'),
        'ru': ('Подготовить въезд, жильё и прибытие', 'Уточни визовые и миграционные процедуры, страховку, дату прибытия и документы для общежития. Наличие общежитий не гарантирует место каждому.'),
        'guide': 'life', 'official': 'https://navigator.rut-miit.ru/cmam',
    },
]

TEXT = {
    'zh': {
        'lang': 'zh-CN', 'title': '中国学生申请俄罗斯交通大学：7步清单',
        'description': '俄罗斯交通大学中国申请者的七步入学清单：选专业、核对政策、准备材料、提交申请、考试、录取、报到。每步均有详细指南和校方来源。',
        'eyebrow': 'RUT (MIIT) · MIRROR OF CHINA', 'h1': '赴俄交大申请清单',
        'intro': '从选专业到抵达莫斯科，用七个步骤梳理申请过程。勾选已经完成的事项，随时继续查阅详细指南。',
        'secondary': '可独立使用的参考清单，不是学校的官方申请系统。请根据具体项目和最新招生规则调整。',
        'progress': '已完成', 'outof': '/ 7 步', 'reset': '重置进度', 'guide': '查看详细说明',
        'faq': '阅读中文 FAQ', 'official': '校方原始来源 ↗', 'back': '返回中文 FAQ', 'switch': 'Русская версия',
        'notice': '⚠️ 招生政策、费用和截止日期可能变化。2026/27学年的规定不能自动视为2027/28学年的现行规则。勾选仅储存在此浏览器，不等于正式提交申请或获得录取。',
        'more': '下一步怎么做？', 'done': '你已勾选所有步骤。请再次确认校方要求和录取状态。',
    },
    'ru': {
        'lang': 'ru', 'title': 'Поступление в РУТ (МИИТ): чек-лист из 7 шагов',
        'description': 'Практический чек-лист иностранного абитуриента РУТ: выбор программы, документы, заявление, экзамены, зачисление и прибытие. Со ссылками на официальный университет.',
        'eyebrow': 'РУТ (МИИТ) · ЗЕРКАЛО ПОДНЕБЕСНОЙ', 'h1': 'Чек-лист поступления в РУТ',
        'intro': 'Семь понятных шагов от выбора программы до приезда в университет. Отмечай выполненное и открывай подробности по каждому этапу.',
        'secondary': 'Справочный инструмент для абитуриента, а не официальный личный кабинет университета. Условия зависят от программы и способа поступления.',
        'progress': 'Выполнено', 'outof': 'из 7 шагов', 'reset': 'Сбросить прогресс', 'guide': 'Подробный материал',
        'faq': 'Читать FAQ', 'official': 'Официальный источник ↗', 'back': 'Вернуться к FAQ', 'switch': '中文版',
        'notice': '⚠️ Сроки, правила и стоимость обучения меняются. Нельзя использовать условия 2026/27 как подтверждённые правила следующей кампании. Галочки сохраняются только в браузере и не означают официальную подачу заявления или зачисление.',
        'more': 'Что нужно сделать?', 'done': 'Все шаги отмечены. Проверь, что университет официально подтвердил твой статус.',
    },
}

CSS = '''
:root{color-scheme:light;--ink:#142940;--blue:#173f72;--muted:#647990;--line:#dbe5ef;--paper:#fff;--bg:#f4f7fc;--gold:#f2b34d}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:system-ui,-apple-system,"Segoe UI","Noto Sans SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}a{color:#1756a0;text-underline-offset:3px}a:hover{color:#0f3768}button,input{font:inherit}button:focus-visible,input:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid #df9c28;outline-offset:3px}
.topbar{border-bottom:1px solid var(--line);background:#fff}.wrap{max-width:970px;margin:0 auto;padding:0 20px}.topinner{display:flex;align-items:center;justify-content:space-between;gap:14px;min-height:68px;flex-wrap:wrap}.brand{font-weight:800;color:var(--ink);text-decoration:none}.switch{border:1px solid var(--line);padding:9px 15px;border-radius:30px;text-decoration:none;font-size:13px;font-weight:700}.hero{background:radial-gradient(circle at 78% 5%,#2a578a,transparent 37%),linear-gradient(110deg,#0c2444,#174675);color:white;padding:54px 0 58px}.eyebrow{font-size:11px;letter-spacing:.16em;font-weight:800;color:#b2d3ff}.hero h1{font-size:clamp(32px,5vw,49px);margin:12px 0 12px;line-height:1.15}.hero p{max-width:730px;line-height:1.8;color:#d7e5f8;margin:0}.subline{font-size:13px;margin-top:14px!important;color:#b5cbea!important}.content{padding-top:30px;padding-bottom:55px}.progress-card{background:white;border-radius:18px;padding:24px 28px;border:1px solid var(--line);box-shadow:0 10px 32px #1f46700a;margin-bottom:20px}.progress-top{display:flex;gap:14px;align-items:center;justify-content:space-between;flex-wrap:wrap}.progress-count{font-size:17px;font-weight:750}.small{font-size:13px;color:var(--muted)}.progress-bar{height:11px;background:#e7edf5;overflow:hidden;border-radius:99px;margin:17px 0 14px}.progress-fill{height:100%;width:0;background:linear-gradient(90deg,#2b9e78,#51bc9c);border-radius:99px;transition:width .2s}.reset{border:1px solid #c6d7e9;background:#f6faff;color:#1a4f82;padding:10px 14px;border-radius:9px;cursor:pointer}.reset:hover{background:#edf5ff}.steps{display:grid;gap:14px}.step{display:grid;grid-template-columns:auto 1fr;gap:15px;background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:21px 22px;box-shadow:0 6px 23px #17315108}.step:has(input:checked){background:#f8fffb;border-color:#b5ddce}.check{appearance:none;width:29px;height:29px;border:2px solid #9fb2c8;background:#fff;border-radius:9px;margin:2px 0;cursor:pointer;display:grid;place-items:center}.check:checked{background:#208c69;border-color:#208c69}.check:checked:after{content:"✓";font-size:20px;line-height:1;color:white}.step h2{margin:0 0 6px;line-height:1.4;font-size:20px}.step label{cursor:pointer}.step p{font-size:14px;color:#495e76;margin:0 0 12px;line-height:1.75}.more{border:0;color:#235889;background:transparent;font-weight:700;padding:0;cursor:pointer;list-style:none}.more:hover{text-decoration:underline}details summary{font-weight:750;color:#275987;cursor:pointer;margin:9px 0 8px;font-size:13px}details p{padding:7px 0 3px}.links{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 0}.links a{display:inline-block;border:1px solid #d3e1f0;padding:9px 12px;border-radius:10px;text-decoration:none;font-size:13px;font-weight:750;background:#f8fbff}.links a.primary{background:#e7f2ff;color:#164c87}.notice{margin-top:22px;border-left:4px solid #d39a3b;background:#fff9ee;color:#725722;border-radius:12px;padding:18px 21px;font-size:13px;line-height:1.75}.footer{padding:24px 0;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}.finish{display:none;margin-top:13px;font-size:14px;color:#176d50;font-weight:700}.finish.visible{display:block}@media(max-width:600px){.hero{padding:42px 0}.wrap{padding:0 15px}.progress-card{padding:19px}.step{padding:17px;gap:12px}.step h2{font-size:17px}.links a{font-size:12px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.progress-fill{transition:none}}
'''

JS = r'''(function(){
  const boxes=Array.from(document.querySelectorAll('.check'));
  const count=document.getElementById('count');
  const bar=document.getElementById('bar');
  const finish=document.getElementById('finish');
  const key='mirror-of-china-application-steps-v1';
  let saved=[];
  try {const data=JSON.parse(localStorage.getItem(key)||'[]');if(Array.isArray(data)) saved=data;}catch(e){}
  boxes.forEach(box=>{box.checked=saved.includes(box.dataset.step);box.addEventListener('change',refresh)});
  function refresh(){const selected=boxes.filter(box=>box.checked).map(box=>box.dataset.step);count.textContent=String(selected.length);bar.style.width=(100*selected.length/boxes.length)+'%';bar.setAttribute('aria-valuenow',String(selected.length));finish.classList.toggle('visible',selected.length===boxes.length);try{localStorage.setItem(key,JSON.stringify(selected));}catch(e){}}
  document.getElementById('reset').addEventListener('click',()=>{boxes.forEach(box=>box.checked=false);refresh();});
  refresh();
})();'''


def make_page(language: str) -> str:
    t=TEXT[language]
    o='zh' if language=='ru' else 'ru'
    url=BASE+language+'/checklist/'
    guide_folder=SITE/'zh'/'guides'
    cards=[]
    for i, step in enumerate(STEPS,1):
        name,desc=step[language]
        original=step['official']
        guide_url=('../guides/'+step['guide']+'/index.html' if language=='zh' else '../../zh/guides/'+step['guide']+'/index.html')
        # Only show guide link when guide exists. FAQ works in both modes.
        if (guide_folder/step['guide']/'index.html').is_file():
            guide_html=f'<a class="primary" href="{escape(guide_url,quote=True)}">{escape(t["guide"])}</a>'
        else:
            guide_html=f'<a class="primary" href="../index.html">{escape(t["faq"])}</a>'
        cards.append(f'''<section class="step" id="step-{i}">
<input class="check" type="checkbox" id="check-{i}" data-step="{i}" aria-label="{escape(name,quote=True)}">
<div><label for="check-{i}"><h2>{i:02d}. {escape(name)}</h2></label>
<p>{escape(desc)}</p><details><summary>{escape(t['more'])}</summary>
<p>{escape(desc)}</p><div class="links">{guide_html}<a href="{escape(original,quote=True)}" target="_blank" rel="noopener noreferrer">{escape(t['official'])}</a></div>
</details></div></section>''')
    both={'ru':BASE+'ru/checklist/','zh':BASE+'zh/checklist/'}
    description=escape(t['description'],quote=True)
    head_title=escape(t['title'])
    # No personal application information is sent to any external endpoint.
    return f'''<!doctype html>
<html lang="{t['lang']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="index,follow"><meta name="description" content="{description}"><meta name="theme-color" content="#0c2444">
<title>{head_title} | Mirror of China</title><link rel="canonical" href="{url}">
<link rel="alternate" hreflang="ru" href="{both['ru']}"><link rel="alternate" hreflang="zh-CN" href="{both['zh']}"><link rel="alternate" hreflang="x-default" href="{both['zh']}">
<style>{CSS}</style></head><body>
<header class="topbar"><div class="wrap topinner"><a class="brand" href="../index.html">中 · Mirror of China</a><a class="switch" href="../../{o}/checklist/index.html">{escape(t['switch'])}</a></div></header>
<section class="hero"><div class="wrap"><div class="eyebrow">{escape(t['eyebrow'])}</div><h1>{escape(t['h1'])}</h1><p>{escape(t['intro'])}</p><p class="subline">{escape(t['secondary'])}</p></div></section>
<main class="wrap content"><section class="progress-card" aria-label="Progress"><div class="progress-top"><span class="progress-count">{escape(t['progress'])}: <span id="count">0</span> {escape(t['outof'])}</span><button class="reset" id="reset" type="button">{escape(t['reset'])}</button></div>
<div class="progress-bar" role="progressbar" id="bar" aria-label="Progress" aria-valuemin="0" aria-valuemax="7" aria-valuenow="0"><div class="progress-fill" id="progress-fill"></div></div>
<div class="small">{escape(t['secondary'])}</div><p id="finish" class="finish" aria-live="polite">{escape(t['done'])}</p></section>
<div class="steps">{''.join(cards)}</div><aside class="notice">{escape(t['notice'])}</aside>
</main><footer class="footer"><div class="wrap">Mirror of China · {date.today().isoformat()} · <a href="../index.html">{escape(t['back'])}</a> · <a href="https://rut-miit.ru/page/120705" target="_blank" rel="noopener noreferrer">RUT (MIIT)</a></div></footer>
<script>{JS.replace("bar.style.width", "document.getElementById('progress-fill').style.width")}</script>
</body></html>'''


def inject_nav(path: Path, href: str, zh: bool):
    old=path.read_text(encoding='utf-8-sig')
    if START in old and END not in old or END in old and START not in old:
        raise ValueError('Незакрытый маркер чек-листа в '+str(path))
    if START in old:
        old=old[:old.index(START)]+old[old.index(END)+len(END):]
    label='✅ 7步申请清单 · 立即开始' if zh else '✅ Чек-лист поступления · 7 шагов'
    desc='按步骤准备申请材料，完成后可继续查看官方资料。' if zh else 'Пройди шаги поступления и открой подробные официальные инструкции.'
    nav=f'''{START}<aside style="max-width:1050px;margin:24px auto;padding:19px 22px;border-radius:14px;border:1px solid #bed7ed;background:#f0f7ff;color:#173d68;font-family:system-ui,sans-serif;line-height:1.6"><a style="font-weight:800;color:#164f85;font-size:17px" href="{escape(href,quote=True)}">{label}</a><div style="font-size:13px;margin-top:4px">{desc}</div></aside>{END}'''
    match=re.search(r'<main\b[^>]*>',old,re.I)
    if not match:raise ValueError('Не найден <main> в '+str(path))
    new=old[:match.end()]+nav+old[match.end():]
    path.write_text(new,encoding='utf-8')


def sitemap_add():
    path=SITE/'sitemap.xml'
    if not path.is_file():raise FileNotFoundError('Сначала собери сайт: site/sitemap.xml отсутствует')
    ns='http://www.sitemaps.org/schemas/sitemap/0.9'
    xhtml='http://www.w3.org/1999/xhtml'
    ET.register_namespace('',ns);ET.register_namespace('xhtml',xhtml)
    tree=ET.parse(path)
    root=tree.getroot()
    existing={x.text for x in root.findall(f'.//{{{ns}}}loc')}
    for lang in ('ru','zh'):
        url=BASE+lang+'/checklist/'
        if url in existing:continue
        child=ET.SubElement(root,'{'+ns+'}url')
        loc=ET.SubElement(child,'{'+ns+'}loc');loc.text=url
        existing.add(url)
    tree.write(path,encoding='utf-8',xml_declaration=True)
    return existing


def main():
    expected=[SITE/'index.html',SITE/'ru'/'index.html',SITE/'zh'/'index.html',SITE/'sitemap.xml']
    for f in expected:
        if not f.is_file():raise FileNotFoundError(f'Не найден {f}; сначала собери сайт')
    for lang in ('ru','zh'):
        folder=SITE/lang/'checklist'
        folder.mkdir(parents=True,exist_ok=True)
        (folder/'index.html').write_text(make_page(lang),encoding='utf-8')
    inject_nav(SITE/'index.html','./zh/checklist/index.html',True)
    inject_nav(SITE/'ru'/'index.html','./checklist/index.html',False)
    inject_nav(SITE/'zh'/'index.html','./checklist/index.html',True)
    existing=sitemap_add()
    for lang in ('ru','zh'):
        p=SITE/lang/'checklist'/'index.html'
        contents=p.read_text(encoding='utf-8')
        assert contents.count('class="step"')==7
        assert contents.count('class="check"')==7
        assert 'localStorage' in contents
        assert BASE+lang+'/checklist/' in existing
    print('OK: 2 страницы чек-листа созданы (RU/ZH), по 7 шагов')
    print('OK: ссылки добавлены на главную и обе языковые страницы')
    print('OK: 2 новых URL добавлены в sitemap.xml; FAQ JSON не изменены')
    print('Открыть: site/zh/checklist/index.html')
    print('ПРИ ПЕРЕСБОРКЕ: после build_site.py, build_distribution.py и build_guides.py последним запускай build_checklist.py')

if __name__=='__main__':
    main()
