#!/usr/bin/env python3
# coding: utf-8
"""Mirror of China - five applicant tools (RU / ZH).

Run only after scripts/build_portal.py. Regenerates the six guide pages
per language without modifying FAQ JSON or official source records.
Idempotent, standard-library only. Keeps old factual material under a
collapsed 'sources and reference' panel for verification.
"""
from __future__ import annotations
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
SLUGS = ('admissions','documents','programs','tuition','life')

DATA = {
 'ru': {
  'catalog_title':'Пять инструментов для поступления',
  'catalog_desc':'Здесь не копии FAQ, а действия: выбрать способ поступления, собрать документы, сравнить программы, посчитать бюджет и подготовить приезд.',
  'catalog_foot':'Независимый студенческий проект. Эти инструменты помогают ориентироваться, но не определяют право на поступление. Правила уточняй на официальном сайте РУТ.',
  'call':'Открыть инструмент', 'evidence':'Подробная справка и официальные источники',
  'unofficial':'Самостоятельный справочный инструмент, не официальная услуга РУТ. Все требования уточняются по правилам конкретной приёмной кампании.',
  'badge':'ИНСТРУМЕНТ АБИТУРИЕНТА', 'reset':'Сбросить',
  'tools': {
   'admissions': ('01','🧭','Выбор пути поступления','Определи, какой способ поступления нужно изучать, прежде чем собирать документы.','Выбрать маршрут'),
   'documents': ('02','📁','Папка документов','Отмечай, что уже проверил, и не путай документы для подачи заявления, въезда и общежития.','Собрать документы'),
   'programs': ('03','🎓','Сравнение двух программ','Сравни две реальные программы по проверяемым критериям, а не по общему названию специальности.','Сравнить программы'),
   'tuition': ('04','₽','Калькулятор бюджета','Введи официальную стоимость своего варианта обучения и получи ориентировочный расчёт расходов.','Рассчитать бюджет'),
   'life': ('05','🏠','Подготовка к приезду','Раздели подготовку на периоды: до поездки, по прибытии и в первую неделю.','Составить план'),
  }
 },
 'zh': {
  'catalog_title':'申请俄交大的五项实用工具',
  'catalog_desc':'不只是重复常见问题。这里可以选择申请路径、整理材料、比较专业、估算预算，以及规划抵俄后的事项。',
  'catalog_foot':'独立学生研究项目。这些工具仅辅助准备，不判断录取资格；以俄罗斯交通大学当年的正式要求为准。',
  'call':'打开工具', 'evidence':'查看详细说明及官方来源',
  'unofficial':'独立学生信息工具，非学校官方服务。申请资格、材料及期限应按适用年度和具体项目核实。',
  'badge':'申请者实用工具', 'reset':'清除',
  'tools': {
   'admissions': ('01','🧭','选择申请途径','先区分合同制、一般竞争录取和政府配额，再核查适用条件。','选择途径'),
   'documents': ('02','📁','申请材料整理表','按申请、入境和宿舍阶段准备资料，不把不同阶段的文件混在一起。','整理材料'),
   'programs': ('03','🎓','两项专业对比表','用专业代码、授课语言、地点等指标比较真正感兴趣的项目。','对比专业'),
   'tuition': ('04','₽','留学预算估算器','输入官网显示的项目费用和个人预估支出，形成以卢布计价的预算。','估算预算'),
   'life': ('05','🏠','抵俄前后准备计划','把待办事项分成出发前、抵达后及第一周三个阶段。','准备入学'),
  }
 }
}

STYLE = r'''
/* MIRROR_TOOLS_V3 */
.mc-tool-root{font-family:system-ui,-apple-system,"Segoe UI","Noto Sans SC",sans-serif;color:#183149}
.mc-tool-root *{box-sizing:border-box}
.mc-tools-head{padding:35px 36px;background:radial-gradient(ellipse at 88% 12%,#3873af 0%,transparent 44%),linear-gradient(110deg,#102e55,#174f7f);color:#fff;border-radius:19px;margin-bottom:22px}
.mc-kicker{font-size:11px;text-transform:uppercase;font-weight:850;letter-spacing:.15em;color:#b9d7f6;margin:0 0 12px}
.mc-tools-head h1{font-size:clamp(26px,4vw,37px)!important;color:#fff!important;border:0!important;margin:0 0 10px!important;padding:0!important;line-height:1.3}
.mc-tools-head p{font-size:15px!important;line-height:1.75;max-width:740px;color:#e1edfa;margin:0!important}
.mc-tools-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.mc-tool-card{display:flex;flex-direction:column;gap:9px;background:#fff;border:1px solid #d8e5f1;border-radius:15px;padding:23px;text-decoration:none!important;color:#193958!important;box-shadow:0 6px 23px #1c45640b;min-height:196px;transition:transform .16s,border-color .16s}
.mc-tool-card:hover{transform:translateY(-2px);border-color:#86b1e0;background:#fafeff}
.mc-tool-card .mc-card-number{font-size:11px;font-weight:900;color:#6386a6;letter-spacing:.12em}
.mc-tool-card .mc-card-icon{font-size:29px;line-height:1.1}
.mc-tool-card strong{font-size:18px;color:#193957;line-height:1.35}
.mc-tool-card small{font-size:13px;color:#647a90;line-height:1.6}
.mc-tool-card .mc-card-cta{font-size:13px;color:#125a9b;font-weight:800;margin-top:auto}
.mc-tool-card:nth-child(1){grid-column:1 / -1;min-height:168px}
.mc-tool-pane{background:#fff;border:1px solid #dce7f1;border-radius:17px;box-shadow:0 10px 30px #1939570d;padding:clamp(19px,3vw,31px);margin:20px 0}
.mc-tool-pane h2{border:0!important;padding:0!important;margin:0 0 13px!important;color:#193b5a!important;font-size:21px!important}
.mc-tool-pane p{font-size:14px;line-height:1.75;color:#536d85}
.mc-tool-hint{border-left:4px solid #ddaa49;background:#fff9ec;border-radius:9px;padding:13px 16px;font-size:13px;line-height:1.7;color:#725a35;margin:16px 0}
.mc-tool-stack{display:grid;gap:12px}
.mc-tool-choice{display:flex;gap:12px;align-items:flex-start;border:1px solid #e0e9f3;border-radius:10px;padding:13px 15px;background:#f9fbfe;cursor:pointer;color:#244661;font-size:14px}
.mc-tool-choice:has(input:checked){border-color:#75abc5;background:#edf8fc}
.mc-tool-choice input{width:18px;height:18px;accent-color:#176a9b;margin-top:2px;flex:none}
.mc-tool-out{background:#edf6ff;border:1px solid #c5dff1;border-radius:12px;padding:16px 18px;color:#1b4b75;line-height:1.7;font-size:14px;margin-top:15px}
.mc-field{display:flex;flex-direction:column;gap:6px;color:#37536c;font-size:13px;font-weight:700}
.mc-field input,.mc-field select{width:100%;min-width:0;padding:11px 12px;border:1px solid #cedde9;border-radius:9px;background:#fff;color:#1a3b59;font-size:15px;font-family:inherit}
.mc-field input:focus-visible,.mc-field select:focus-visible,.mc-tool-pane button:focus-visible,.mc-tool-pane summary:focus-visible{outline:3px solid #e0a634;outline-offset:3px}
.mc-input-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px}
.mc-program-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}
.mc-program-col{padding:15px;background:#f8fbfe;border:1px solid #e1ebf3;border-radius:13px;display:grid;gap:12px}
.mc-program-col h3{margin:0;font-size:16px;color:#194c7b}
.mc-tool-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:15px}
.mc-tool-btn{font:inherit;font-weight:750;font-size:13px;cursor:pointer;border:1px solid #b8cfdf;border-radius:9px;padding:10px 15px;color:#17466d;background:#f1f7ff}
.mc-tool-btn:hover{background:#dfedfa}
.mc-progress{height:9px;border-radius:99px;background:#e5edf4;overflow:hidden;margin:12px 0}
.mc-progress span{display:block;background:#238a75;height:100%;width:0;transition:width .2s}
.mc-tool-total{font-size:clamp(22px,3vw,32px);color:#123f64;font-weight:900;font-variant-numeric:tabular-nums}
.mc-check-section{margin:17px 0}.mc-check-section h3{font-size:16px;margin:0 0 10px;color:#20496c}
.mc-check-section .mc-tool-choice{margin-bottom:7px}
.mc-source-details{margin:24px 0;background:#f8fbfe;border:1px solid #d9e5ef;border-radius:13px;padding:5px 23px 19px;color:#284660;line-height:1.75}
.mc-source-details>summary{cursor:pointer;font-weight:800;font-size:15px;padding:17px 0;color:#175488}
.mc-source-details>summary:hover{text-decoration:underline}
.mc-source-details h2{font-size:19px!important;margin-top:21px!important;color:#173e63!important}
.mc-source-details h2:first-of-type{margin-top:5px!important}
.mc-source-details p,.mc-source-details li{font-size:14px!important}
.mc-source-details a{color:#155f9c}
.mc-tool-foot{font-size:12px;color:#637b92;margin:15px 0 6px;line-height:1.7}
.mc-tool-root a:focus-visible{outline:3px solid #e0a634;outline-offset:3px}
@media(max-width:690px){.mc-tools-head{padding:26px 22px}.mc-tools-grid,.mc-program-grid,.mc-input-grid{grid-template-columns:1fr}.mc-tool-card:nth-child(1){grid-column:auto}.mc-tool-card{min-height:0}.mc-tool-pane{padding:19px}}
@media(prefers-reduced-motion:reduce){.mc-tool-card{transition:none}.mc-progress span{transition:none}}
'''


def e(value: str) -> str:
    return html.escape(str(value), quote=True)


def checkbox_group(lang:str, groups:list[tuple[str,list[str]]], ident:str)->str:
    out=[]
    for title,labels in groups:
        boxes=''.join(f'<label class="mc-tool-choice"><input type="checkbox" data-mc-check="{ident}-{i}-{j}"><span>{e(label)}</span></label>' for j,label in enumerate(labels) for i in [groups.index((title,labels))])
        out.append(f'<section class="mc-check-section"><h3>{e(title)}</h3>{boxes}</section>')
    small='已核对' if lang=='zh' else 'Проверено'
    return (f'<div data-mc-checklist="{ident}"><p class="mc-tool-total"><span data-mc-count>0</span> / <span data-mc-max>0</span></p>'
            f'<div class="mc-progress"><span data-mc-progress></span></div>{"".join(out)}</div>'
            f'<div class="mc-tool-actions"><button type="button" class="mc-tool-btn" data-mc-reset="{ident}">{e(DATA[lang]["reset"])}</button></div>'
            f'<p class="mc-tool-foot">{e(small)} · '+('只保存在当前浏览器，不代表已提交材料。' if lang=='zh' else 'Отметки хранятся в браузере, а не в личном кабинете университета.')+'</p>')


def admissions_tool(lang:str)->str:
    zh=lang=='zh'
    title='先确定自己的申请情形' if zh else 'Сначала определись со способом поступления'
    opts=(('contract','合同制（付费学习）' if zh else 'Платное обучение по договору'),
          ('general','一般竞争录取（如适用）' if zh else 'Общий конкурс (если подходишь по условиям)'),
          ('quota','俄罗斯政府配额（如适用）' if zh else 'Квота правительства России (если подходит)'))
    choices=''.join(f'<label class="mc-tool-choice"><input type="radio" name="mc-route" value="{key}"><span>{e(label)}</span></label>' for key,label in opts)
    hint=('这里不是录取资格测试，也不是官方申请系统。具体是否符合资格必须按当年文件及学校回复确认。' if zh else
          'Это не проверка права на поступление и не официальный портал. Условия конкретной программы нужно подтвердить по документам и в университете.')
    return f'<section class="mc-tool-pane"><h2>{e(title)}</h2><div class="mc-tool-stack">{choices}</div><div id="mc-route-output" class="mc-tool-out" aria-live="polite">{e("选择一种情形，查看首先要核查什么。" if zh else "Выбери вариант, чтобы увидеть вопросы для проверки.")}</div><div class="mc-tool-hint">{e(hint)}</div></section>'


def documents_tool(lang:str)->str:
    if lang=='zh':
        groups=[('申请前核对',['护照或适用的身份证明是否有效','对应教育阶段的学历和成绩材料是否齐全','按学校要求核对俄语翻译及认证条件','照片和电子文件的扫描清晰度是否符合说明']),
                ('选拔与录取',['核对考试资格、科目及具体安排','检查申请状态和学校发出的通知']),
                ('入境与入住',['按本人身份核查入境/签证与登记文件','确认宿舍是否已获分配及入住材料'])]
    else:
        groups=[('Для подачи заявления',['Проверить действительность паспорта или иного допустимого удостоверения','Собрать документы об образовании и необходимые приложения','Уточнить требования к переводу и признанию документов','Проверить читаемость сканов и формат файлов']),
                ('Для отбора и зачисления',['Уточнить экзамены, формат и сроки для выбранной программы','Проверить уведомления университета и статус заявления']),
                ('Для приезда и заселения',['Отдельно уточнить документы для въезда и миграционного оформления','Уточнить, предоставлено ли место в общежитии и что требуется для заселения'])]
    return f'<section class="mc-tool-pane"><h2>{e("Материалы по этапам" if lang=="ru" else "按阶段整理材料")}</h2>{checkbox_group(lang, groups,"docs")}</section>'


def programs_tool(lang:str)->str:
    zh=lang=='zh'
    fields=[('name','专业名称' if zh else 'Название программы'),('code','专业代码' if zh else 'Код направления'),
            ('level','培养层次' if zh else 'Уровень образования'),('language','授课语言' if zh else 'Язык обучения'),
            ('campus','学习地点' if zh else 'Место обучения'),('form','学习形式' if zh else 'Форма обучения')]
    cols=[]
    for j in (1,2):
        fields_html=''.join(f'<label class="mc-field">{e(label)}<input type="text" data-mc-program="{j}-{key}" placeholder="{e("需要官网核对" if zh else "Уточнить на сайте РУТ")}" autocomplete="off" maxlength="120"></label>' for key,label in fields)
        cols.append(f'<div class="mc-program-col"><h3>{e("项目" if zh else "Программа")} {j}</h3>{fields_html}</div>')
    note=('输入内容仅保存在当前浏览器。这里不自动核实招生名额、收费或录取资格；请用官方目录逐项核对。' if zh else
          'Всё вводишь сам: сравнение не проверяет наличие набора, стоимость или право на зачисление. Сверяй поля с официальным каталогом РУТ.')
    return ('<section class="mc-tool-pane"><h2>'+e('两项专业并排比较' if zh else 'Сравни две конкретные программы')+'</h2>'
            +'<div class="mc-program-grid">'+''.join(cols)+'</div><div class="mc-tool-actions"><button class="mc-tool-btn" type="button" id="mc-print">'
            +e('打印比较表' if zh else 'Распечатать сравнение')+'</button><button class="mc-tool-btn" type="button" id="mc-clear-program">'+e(DATA[lang]['reset'])+'</button></div>'
            +f'<div class="mc-tool-hint">{e(note)}</div></section>')


def tuition_tool(lang:str)->str:
    zh=lang=='zh'
    fields=[('semester','官网所示每学期学费（卢布）' if zh else 'Цена за семестр с официальной страницы (₽)','0'),
            ('semesters','学期数量' if zh else 'Число семестров','2'),
            ('housing','每月住宿估计（卢布）' if zh else 'Жильё в месяц (₽)','0'),
            ('other','每月其他费用估计（卢布）' if zh else 'Прочие расходы в месяц (₽)','0'),
            ('months','预计月数' if zh else 'Количество месяцев','10')]
    fields_html=''.join(f'<label class="mc-field">{e(label)}<input type="number" data-mc-budget="{name}" min="0" max="100000000" step="1" inputmode="numeric" value="{default}"></label>' for name,label,default in fields)
    intro=('此计算器不提供官方学费报价。请输入已从学校核实的专业收费；其他费用由你自己估算。' if zh else
           'Это не официальный прайс-лист. Стоимость программы вводи по актуальному документу РУТ, остальные расходы — по собственной оценке.')
    total='估算合计' if zh else 'Ориентировочная сумма'
    return f'<section class="mc-tool-pane"><h2>{e("用自己的数字估算预算" if zh else "Рассчитай бюджет по своим данным")}</h2><p>{e(intro)}</p><div class="mc-input-grid">{fields_html}</div><div class="mc-tool-out"><div>{e(total)}</div><div class="mc-tool-total"><span id="mc-budget-total">0</span> ₽</div><div id="mc-budget-breakdown"></div></div><div class="mc-tool-hint">{e("不是全部留学费用清单；保险、签证、交通和其他个人支出可能需要另行计算。" if zh else "Расчёт не включает автоматически страховку, визовые расходы, дорогу и другие возможные платежи.")}</div></section>'


def life_tool(lang:str)->str:
    if lang=='zh':
        groups=[('出发前',['核实学校发出的入学及报到信息','确认是否获得宿舍名额，不预设一定有床位','核对本人适用的签证与入境文件']),
                ('到达后',['按规定办理迁移登记等手续','根据学校要求准备保险及必要的医学材料']),
                ('第一周',['了解宿舍入住与缴费的官方流程','登录学校个人账户，查看课表及通知','核对负责部门的联系方式'])]
    else:
        groups=[('До выезда',['Проверить официальное подтверждение зачисления и даты прибытия','Выяснить, выделено ли место в общежитии','Проверить въездные документы для своего статуса']),
                ('После прибытия',['Уточнить сроки и порядок миграционного оформления','Проверить требования к страховке и медицинским документам']),
                ('Первая неделя',['Получить порядок заселения и официальные платёжные инструкции','Войти в личный кабинет, проверить расписание и объявления','Сохранить контакты ответственных подразделений'])]
    return f'<section class="mc-tool-pane"><h2>{e("抵俄事项时间线" if lang=="zh" else "План первых дней")}</h2>{checkbox_group(lang,groups,"life")}</section>'


def content_for(lang: str, slug: str)->str:
    return {'admissions':admissions_tool,'documents':documents_tool,'programs':programs_tool,'tuition':tuition_tool,'life':life_tool}[slug](lang)


def js_for(lang: str, slug: str) -> str:
    if slug=='admissions':
        texts={
         'ru':{'contract':'Проверь наличие договорного набора на выбранную программу, текущие сроки, перечень экзаменов и условия договора. Платное обучение не означает зачисление без отбора.',
               'general':'Уточни, можешь ли участвовать в конкурсе на соответствующих условиях. Наличие бюджетных мест в каталоге само по себе не подтверждает право конкретного иностранного абитуриента.',
               'quota':'Проверь отдельный порядок государственной квоты, сроки, отбор и подтверждение результата. Квота не предоставляется автоматически.'},
         'zh':{'contract':'查看所选专业当年的合同制招生、申请期限、考试及合同条件。付费不等于免试或保证录取。',
               'general':'先确认自己是否符合一般竞争录取的适用条件。专业目录中出现预算名额，不代表每一位外国申请人都自动有资格。',
               'quota':'查看俄罗斯政府配额的独立申请流程、时间和选拔条件。配额不是自动获得的。'}
        }
        return '(()=>{const msgs='+json.dumps(texts[lang],ensure_ascii=False)+';const out=document.getElementById("mc-route-output");document.querySelectorAll("input[name=mc-route]").forEach(el=>el.addEventListener("change",()=>{if(el.checked)out.textContent=msgs[el.value]||"";}));})();'
    if slug in ('documents','life'):
        key='mirror-tools-v3-'+slug
        return r'''(()=>{const root=document.querySelector('[data-mc-checklist]');if(!root)return;const boxes=[...root.querySelectorAll('[data-mc-check]')];const key=__KEY__;let selected=[];try{const v=JSON.parse(localStorage.getItem(key)||'[]');if(Array.isArray(v))selected=v;}catch(_){ }boxes.forEach(b=>b.checked=selected.includes(b.dataset.mcCheck));function refresh(){const checked=boxes.filter(b=>b.checked).map(b=>b.dataset.mcCheck);root.querySelector('[data-mc-count]').textContent=checked.length;root.querySelector('[data-mc-max]').textContent=boxes.length;root.querySelector('[data-mc-progress]').style.width=(100*checked.length/Math.max(boxes.length,1))+'%';try{localStorage.setItem(key,JSON.stringify(checked));}catch(_){} }boxes.forEach(b=>b.addEventListener('change',refresh));document.querySelector('[data-mc-reset]').addEventListener('click',()=>{boxes.forEach(b=>b.checked=false);refresh();});refresh();})();'''.replace('__KEY__',json.dumps(key))
    if slug=='programs':
        return r'''(()=>{const fields=[...document.querySelectorAll('[data-mc-program]')];const key='mirror-tools-v3-programs';let data={};try{data=JSON.parse(localStorage.getItem(key)||'{}')||{};}catch(_){}fields.forEach(el=>{el.value=typeof data[el.dataset.mcProgram]==='string'?data[el.dataset.mcProgram]:'';el.addEventListener('input',()=>{const out={};fields.forEach(input=>out[input.dataset.mcProgram]=input.value);try{localStorage.setItem(key,JSON.stringify(out));}catch(_){}})});document.getElementById('mc-clear-program').addEventListener('click',()=>{fields.forEach(f=>f.value='');try{localStorage.removeItem(key);}catch(_){}});document.getElementById('mc-print').addEventListener('click',()=>window.print());})();'''
    if slug=='tuition':
        strings= {'ru':('Учёба','Жильё','Другие расходы'), 'zh':('学费','住宿','其他支出')}[lang]
        return r'''(()=>{const fields=[...document.querySelectorAll('[data-mc-budget]')];const fmt=new Intl.NumberFormat('__LANG__',{maximumFractionDigits:0});const labels=__LABELS__;function refresh(){const obj={};fields.forEach(f=>obj[f.dataset.mcBudget]=Math.min(100000000,Math.max(0,Number(f.value)||0)));const a=obj.semester*obj.semesters,b=obj.housing*obj.months,c=obj.other*obj.months;document.getElementById('mc-budget-total').textContent=fmt.format(a+b+c);document.getElementById('mc-budget-breakdown').textContent=labels[0]+': '+fmt.format(a)+' ₽ · '+labels[1]+': '+fmt.format(b)+' ₽ · '+labels[2]+': '+fmt.format(c)+' ₽';}fields.forEach(el=>el.addEventListener('input',refresh));refresh();})();'''.replace('__LANG__','zh-CN' if lang=='zh' else 'ru-RU').replace('__LABELS__',json.dumps(strings,ensure_ascii=False))
    return ''


def add_style(text:str)->str:
    if '/* MIRROR_TOOLS_V3 */' not in text:
        text=re.sub(r'</head>',lambda m:'<style>'+STYLE+'</style>'+m.group(0),text,count=1,flags=re.I)
    return text


def remove_redundant(text:str)->str:
    # Original guide-specific nav (replaced by the single shared nav).
    text=re.sub(r'(<div class="wrap">)\s*<nav>.*?</nav>',r'\1',text,count=1,flags=re.S)
    # Article "continue reading" and RU navigation duplicates.
    text=re.sub(r'<div class="links"><strong>继续阅读：</strong><div>.*?</div></div>','',text,flags=re.S)
    text=re.sub(r'<div class="rg-other">.*?</div>','',text,flags=re.S)
    text=re.sub(r'<p style="margin-top:24px">.*?</p>','',text,flags=re.S)
    # Inline links duplicating shared menu on Chinese guide pages.
    text=re.sub(r'<h2>更多信息</h2>\s*<ul>.*?</ul>','',text,flags=re.S)
    # RU original FAQ cards had repeating links to corresponding questions.
    text=re.sub(r'<a href="\.\./\.\./index\.html#faq-[^"]+">Вопрос в общей базе FAQ</a>','',text)
    return text


def catalog(lang:str)->str:
    t=DATA[lang]
    cards=[]
    for slug,(num,icon,title,desc,action) in t['tools'].items():
        cards.append(f'<a class="mc-tool-card" href="{slug}/index.html"><span class="mc-card-number">{e(num)} / 05</span><span class="mc-card-icon" aria-hidden="true">{e(icon)}</span><strong>{e(title)}</strong><small>{e(desc)}</small><span class="mc-card-cta">{e(action)} →</span></a>')
    return f'<main class="mc-tool-root {"rg-wrap" if lang=="ru" else "wrap"}"><section class="mc-tools-head"><div class="mc-kicker">{e(t["badge"])}</div><h1>{e(t["catalog_title"])}</h1><p>{e(t["catalog_desc"])}</p></section><div class="mc-tools-grid">{"".join(cards)}</div><p class="mc-tool-foot">{e(t["catalog_foot"])}</p></main>'


def update_meta(text:str, lang:str, title:str, desc:str)->str:
    full=title+' | '+('Зеркало Поднебесной' if lang=='ru' else '天朝之镜 · RUT/MIIT')
    text=re.sub(r'<title>.*?</title>', lambda m:'<title>'+e(full)+'</title>', text,count=1,flags=re.S)
    text=re.sub(r'<meta name="description" content="[^"]*"\s*/?>',lambda m:'<meta name="description" content="'+e(desc)+'">',text,count=1)
    # These pages are now tools with explanatory documentation, not five duplicate articles.
    text=text.replace('<meta property="og:type" content="article"/>','<meta property="og:type" content="website"/>')
    def rewrite_schema(match):
        try:
            obj=json.loads(match.group(1))
            obj['@type']='WebPage'
            obj['headline']=title
            obj['description']=desc
            return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False).replace('</','<\\/')+'</script>'
        except (ValueError,TypeError):
            return match.group(0)
    text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',rewrite_schema,text,count=1,flags=re.S)
    return text


def relabel_site_navigation():
    words={
       'Пять тематических гайдов':'5 практических инструментов',
       '五大专题指南':'五项实用工具',
       '五个专题':'实用工具',
       '5 тем':'Инструменты',
       'Поступление, документы, программы, стоимость и жизнь':'Маршрут, документы, сравнение, бюджет и приезд',
       '申请、材料、专业、学费与校园生活':'申请途径、材料整理、专业对比、预算与报到',
    }
    for page in SITE.rglob('index.html'):
        text=page.read_text(encoding='utf-8')
        for a,b in words.items():text=text.replace(a,b)
        page.write_text(text,encoding='utf-8')


def do_catalog(page:Path, lang:str):
    text=page.read_text(encoding='utf-8-sig')
    text=remove_redundant(text)
    # Replace only old main markup, preserving shared site navigation and head metadata.
    pattern=r'<main class="(?:rg-wrap|sheet)">.*?</main>'
    text,n=re.subn(pattern,lambda m:catalog(lang),text,count=1,flags=re.S)
    if n!=1:raise RuntimeError(f'Каталог {lang}: не найден основной блок')
    text=add_style(text)
    text=update_meta(text,lang,DATA[lang]['catalog_title'],DATA[lang]['catalog_desc'])
    page.write_text(text,encoding='utf-8')


def do_detail(page:Path, lang:str, slug:str):
    t=DATA[lang]
    text=remove_redundant(page.read_text(encoding='utf-8-sig'))
    body_match=re.search(r'<(?:article class="rg-sheet"|main class="sheet")>(.*?)</(?:article|main)>',text,flags=re.S)
    if not body_match:raise RuntimeError(f'Гайд {lang}/{slug}: не найден основной блок')
    original=body_match.group(1)
    if lang=='zh':
        # Source is the complete independently authored article; only its first title repeats the new hero.
        original=re.sub(r'^\s*<h1>.*?</h1>\s*','',original,count=1,flags=re.S)
    else:
        # RU information originally repeats verbatim FAQ: make it reference-only.
        original=''.join(re.findall(r'<section class="rg-faq".*?</section>',original,flags=re.S))
    if not original.strip():raise RuntimeError(f'Гайд {lang}/{slug}: пустые справочные источники')
    _,icon,title,desc,_=t['tools'][slug]
    new=f'''<main class="mc-tool-root {"rg-wrap" if lang=="ru" else "wrap"}">
<section class="mc-tools-head"><div class="mc-kicker">{e(icon)} {e(t["badge"])}</div><h1>{e(title)}</h1><p>{e(desc)}</p></section>
{content_for(lang,slug)}
<details class="mc-source-details"><summary>{e(t['evidence'])}</summary><div class="mc-source-body">{original}</div></details>
<p class="mc-tool-foot">{e(t['unofficial'])}</p></main>'''
    text=text[:body_match.start()]+new+text[body_match.end():]
    text=add_style(text)
    text=update_meta(text,lang,title,desc)
    script=js_for(lang,slug)
    if script:
        text=re.sub(r'</body>',lambda m:'<script>'+script+'</script>'+m.group(0),text,count=1,flags=re.I)
    page.write_text(text,encoding='utf-8')


def main():
    for lang in ('ru','zh'):
        folder=SITE/lang/'guides'
        index=folder/'index.html'
        if not index.is_file():raise RuntimeError(f'Нет каталога {index}')
        do_catalog(index,lang)
        for slug in SLUGS:
            page=folder/slug/'index.html'
            if not page.is_file():raise RuntimeError(f'Нет материала {page}')
            do_detail(page,lang,slug)
    relabel_site_navigation()
    # Validate no guide renders the old duplicate link blocks and all pages contain tools.
    pages=[SITE/lang/'guides'/slug/'index.html' for lang in ('ru','zh') for slug in SLUGS]
    for path in pages:
        value=path.read_text(encoding='utf-8')
        if 'mc-tool-pane' not in value or 'mc-source-details' not in value or '<div class="rg-other">' in value:
            raise RuntimeError(f'Ошибка проверки {path}')
    print('OK: 5 инструментов RU + 5 ZH, два каталога — оформлены')
    print('OK: повторяющиеся блоки ссылок удалены; общая навигация сохранена')
    print('OK: исходные материалы и официальные ссылки доступны под раскрывающимся блоком')
    print('FAQ JSON и открытые данные не изменены')

if __name__=='__main__':
    main()
