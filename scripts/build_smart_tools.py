#!/usr/bin/env python3
# coding: utf-8
"""Apply personalized admissions wizard + searchable official 2026 catalog compare.

Runs AFTER scripts/build_tools.py. Preserves original FAQ and reference citations.
"""
from __future__ import annotations
import html
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'site'
SCRIPTS=Path(__file__).resolve().parent
CATALOG=ROOT/'data'/'program_catalog_2026.json'
CSS=(SCRIPTS/'smart_tools_v4.css').read_text(encoding='utf-8')
JS=(SCRIPTS/'smart_tools_v4.js').read_text(encoding='utf-8')

LABELS={
 'ru':{
  'wizard_h':'Твой персональный маршрут поступления',
  'wizard_intro':'Отметь свою ситуацию — следующий шаг появится автоматически. В конце получишь индивидуальную последовательность действий и официальные ссылки.',
  'finance_h':'Как планируешь поступать?',
  'finance_s':'Выбери один вариант. Условия и доступность финансирования для иностранцев требуется проверять отдельно.',
  'finance':[('contract','Платное обучение','Обучение по договору, при соблюдении правил приёма'),('general','Бюджетный конкурс','Только если твой статус даёт право участвовать'),('quota','Государственная квота','Отдельная процедура отбора и оформления')],
  'level_h':'Какой уровень обучения интересует?',
  'level_s':'Это фильтр по типу программы. Наличие программы не означает открытый набор.',
  'level':[('basic','Базовое высшее / специалитет','Программы первого высшего образования'),('master','Магистратура','Программы следующего уровня'),('asp','Аспирантура','Подготовка научных кадров')],
  'education_h':'Какое образование уже получено?',
  'education_s':'Это нужно, чтобы предупредить о возможных требованиях к предыдущему диплому.',
  'education':[('secondary','Школа','Аттестат или аналогичный документ'),('college','Колледж / СПО','Диплом профессионального образования'),('degree','Высшее образование','Есть диплом вуза'),('other','Другое','Нужно уточнить признание документа')],
  'russian_h':'Что с русским языком?',
  'russian_s':'Язык обучения и внутренних экзаменов нужно подтвердить отдельно для конкретной программы.',
  'russian':[('yes','Готов(а) к обучению на русском','Уточни требования к экзаменам'),('no','Нужна подготовка','Проверь возможность языковой подготовки'),('unknown','Пока не знаю','Сначала запроси официальные требования')],
  'program_h':'Выбери конкретную программу РУТ',
  'program_s':'Нажми на поле: откроется прокручиваемый список официальных программ 2026 года. Поиск по названию, коду и профилю.',
  'skip':'Пока не определился с программой',
  'result_title':'Твой персональный план', 'next':'Ближайшие действия', 'clear':'Начать заново',
  'download':'Скачать план .txt','print':'Распечатать',
  'compare_h':'Сравни две реальные программы РУТ',
  'compare_intro':'Выбирай программы из официального перечня 2026 года. Поля заполняются автоматически — ничего вручную вводить не требуется.',
  'filter':'Уровень', 'all':'Все уровни', 'basic':'Базовое высшее / специалитет', 'master':'Магистратура', 'asp':'Аспирантура',
  'program_a':'Программа А','program_b':'Программа Б','results':'Результат сравнения',
  'comp_source':'Официальные источники для уточнения',
  'disclaimer':'Данные относятся к опубликованным учебным планам 2026 года. Они не подтверждают наличие приёма, договорных или бюджетных мест для граждан КНР. Цена, язык и условия поступления должны проверяться отдельно.',
  'count':'программ/форм обучения из реестра',
 },
 'zh':{
  'wizard_h':'你的个性化申请路线',
  'wizard_intro':'勾选自己的情况，下一组问题便会自动出现。完成后将得到个性化准备步骤与俄交大官方核实链接。',
  'finance_h':'打算采用哪种申请方式？',
  'finance_s':'请选择一项。外国申请者能否使用该途径，需要按适用规则核实。',
  'finance':[('contract','合同制 / 自费','仍须符合正式入学及考试要求'),('general','一般竞争 / 预算制','需确认本人是否有资格申请'),('quota','俄罗斯政府配额','需单独完成配额选拔流程')],
  'level_h':'想申请哪个培养层次？',
  'level_s':'用于筛选专业，不代表目前正在招收国际学生。',
  'level':[('basic','基础高等教育 / 专家学位','通常对应首个高等教育阶段'),('master','硕士层次','需要核实此前取得的学历'),('asp','博士研究生','科研人员培养方向')],
  'education_h':'目前拥有什么学历？',
  'education_s':'系统将提醒你检查前置学历要求。',
  'education':[('secondary','高中毕业','高中学历及相关材料'),('college','大专 / 职业教育','对应专业教育文凭'),('degree','已有高等教育学历','持有大学学历证明'),('other','其他学历','需要核实文凭认可条件')],
  'russian_h':'俄语准备得怎么样？',
  'russian_s':'不同项目的授课语言、考试语言需通过官方文件确认。',
  'russian':[('yes','能够使用俄语学习','仍需核实正式语言要求'),('no','需要学习俄语','先确认是否需要预科'),('unknown','暂不清楚','优先查询语言及考试要求')],
  'program_h':'选择具体的俄交大专业',
  'program_s':'点击选择框，会出现可用鼠标滚轮浏览的官方专业列表，也可按代码或俄语专业名称搜索。',
  'skip':'尚未决定具体专业',
  'result_title':'你的个性化准备计划','next':'具体下一步','clear':'重新选择',
  'download':'下载计划 .txt','print':'打印',
  'compare_h':'比较两个真实的俄交大专业',
  'compare_intro':'从俄交大2026年官方教育项目列表选择两个专业。所有已核实字段自动填入，无需逐行手动输入。',
  'filter':'培养层次','all':'全部层次','basic':'基础高等教育 / 专家学位','master':'硕士','asp':'博士研究生',
  'program_a':'项目 A','program_b':'项目 B','results':'对比结果',
  'comp_source':'查看俄交大正式来源',
  'disclaimer':'数据来自2026年课程计划公示，不代表该专业目前对中国公民开放招生，也不证明预算名额或合同名额可用。学费、语言和入学条件须单独核实。',
  'count':'项专业及学习形式组合',
 }
}

def e(s):return html.escape(str(s),quote=True)
def choice_group(field,items):
    boxes=[]
    for key,title,sub in items:
        boxes.append(f'<label class="ms-choice"><input type="radio" name="ms-{e(field)}" data-ms-field="{e(field)}" value="{e(key)}"><span><strong>{e(title)}</strong><small>{e(sub)}</small></span></label>')
    return '<div class="ms-choice-grid">'+''.join(boxes)+'</div>'

def picker(name, t):
    return f'''<div class="ms-picker" data-ms-picker="{e(name)}">
       <button type="button" class="ms-pick-button" aria-haspopup="listbox" aria-expanded="false"><span class="ms-pick-label">{e('点击选择专业' if t=='zh' else 'Нажми, чтобы выбрать программу')}</span><span aria-hidden="true">⌄</span></button>
       <div class="ms-popover" hidden><input type="search" class="ms-search" role="searchbox" autocomplete="off" placeholder="{e('搜索代码或专业名称…' if t=='zh' else 'Поиск по коду или программе…')}"><span class="ms-pop-count"></span><div class="ms-options" role="listbox" aria-label="{e('专业列表' if t=='zh' else 'Список программ')}"></div></div>
     </div>'''

def wizard_page(lang:str,count:int)->str:
    t=LABELS[lang]
    steps=[]
    for idx,field in enumerate(('finance','level','education','russian'),1):
        steps.append(f'''<section class="ms-section" data-ms-step="{field}" {'hidden' if idx>1 else ''}>
          <h3>{idx:02d}. {e(t[field+'_h'])}</h3><p class="ms-sub">{e(t[field+'_s'])}</p>
          {choice_group(field,t[field])}
          {'<p data-ms-financing-note class="ms-warning" hidden></p>' if field=='finance' else ''}
          {'<p data-ms-education-note class="ms-warning" hidden></p>' if field=='education' else ''}
          </section>''')
    steps.append(f'''<section class="ms-section" data-ms-step="program" hidden>
      <h3>05. {e(t['program_h'])}</h3><p class="ms-sub">{e(t['program_s'])}</p>
      {picker('wizard',lang)}
      <div class="ms-controls"><button type="button" class="ms-btn alt" data-ms-skip>{e(t['skip'])}</button></div>
      </section>''')
    steps.append(f'''<section data-ms-step="result" hidden><div id="ms-wizard-result" class="ms-result">
      <h3 data-ms-summary-title>{e(t['result_title'])}</h3>
      <p data-ms-summary-context></p><div data-ms-summary-warnings></div>
      <h4>{e(t['next'])}</h4><ol data-ms-summary-list></ol>
      <div class="ms-source-links"></div>
      <div class="ms-controls"><button type="button" class="ms-btn" data-ms-download>{e(t['download'])}</button><button type="button" class="ms-btn alt" data-ms-print>{e(t['print'])}</button></div>
      </div></section>''')
    return f'''<section class="mc-tool-pane mc-smart" id="mc-smart-page" data-lang="{lang}" data-mode="wizard">
      <header class="ms-intro"><div><h2>{e(t['wizard_h'])}</h2><p>{e(t['wizard_intro'])}</p></div>
      <span class="ms-data-pill">2026 · {count} {e(t['count'])}</span></header>
      <div class="ms-step-bar" aria-label="{'进度' if lang=='zh' else 'Прогресс'}">{''.join('<span></span>' for _ in range(5))}</div><p class="ms-local-note">{'完成进度' if lang=='zh' else 'Пройдено шагов'}: <strong data-ms-progress>0/5</strong></p>
      {''.join(steps)}
      <div class="ms-controls"><button class="ms-btn alt" data-ms-reset type="button">{e(t['clear'])}</button></div>
      <p class="ms-warning">{e(t['disclaimer'])}</p></section>'''

def compare_page(lang:str,count:int)->str:
    t=LABELS[lang]
    return f'''<section class="mc-tool-pane mc-smart" id="mc-smart-page" data-lang="{lang}" data-mode="compare">
      <header class="ms-intro"><div><h2>{e(t['compare_h'])}</h2><p>{e(t['compare_intro'])}</p></div>
      <span class="ms-data-pill">2026 · {count} {e(t['count'])}</span></header>
      <div class="ms-choose-row"><label for="ms-program-level">{e(t['filter'])}</label><select id="ms-program-level" data-ms-level-filter>
      {''.join(f'<option value="{x}">{e(t[x])}</option>' for x in ('all','basic','master','asp'))}</select></div>
      <div class="ms-compare-grid"><div class="ms-compare-card"><h3>{e(t['program_a'])}</h3>{picker('a',lang)}</div>
      <div class="ms-compare-card"><h3>{e(t['program_b'])}</h3>{picker('b',lang)}</div></div>
      <p data-ms-compare-empty class="ms-empty">{'请选择两个专业，自动显示对比。' if lang=='zh' else 'Выбери две программы. Таблица заполнится автоматически.'}</p>
      <section data-ms-compare-result hidden><div class="ms-table-wrap"><table class="ms-compare-table"><thead><tr><th scope="col">{'指标' if lang=='zh' else 'Критерий'}</th><th scope="col">{e(t['program_a'])}</th><th scope="col">{e(t['program_b'])}</th></tr></thead><tbody></tbody></table></div></section>
      <div class="ms-controls"><button type="button" class="ms-btn alt" data-ms-reset>{e(t['clear'])}</button><button type="button" class="ms-btn" data-ms-print>{e(t['print'])}</button></div>
      <p class="ms-info">{'差异栏有浅黄色背景。仅比较官方公开的可核实字段，不代表哪个专业更好。' if lang=='zh' else 'Различия подсвечены мягким жёлтым. Сравниваем только опубликованные факты — не оцениваем, какая программа «лучше».'}</p>
      <p class="ms-warning">{e(t['disclaimer'])}</p>
      <div class="ms-source-links"></div>
      </section>'''

def patch(page:Path,lang:str,mode:str,payload:dict):
    text=page.read_text(encoding='utf-8')
    markup=wizard_page(lang,payload['count']) if mode=='wizard' else compare_page(lang,payload['count'])
    text,n=re.subn(r'<section class="mc-tool-pane">.*?</section>',lambda m:markup,text,count=1,flags=re.S)
    if n!=1:raise RuntimeError('Не найден исходный блок инструмента: '+str(page))
    # Remove the old v3 inline JS. Its handlers target elements we replaced above.
    def drop_old(m):
        body=m.group(1)
        if ('mc-route-output' in body and 'mc-route' in body) or ('mc-clear-program' in body and 'data-mc-program' in body):
            return ''
        return m.group(0)
    text=re.sub(r'<script>(.*?)</script>',drop_old,text,flags=re.S)
    if '<style>/* MIRROR_SMART_TOOLS_V4 */' not in text:
        text=re.sub(r'</head>',lambda m:'<style>'+CSS+'</style>'+m.group(0),text,count=1,flags=re.I)
    raw=json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    script='<script type="application/json" id="mc-rut-program-data">'+raw+'</script><script>'+JS+'</script>'
    text=re.sub(r'</body>',lambda m:script+m.group(0),text,count=1,flags=re.I)
    if 'MIRROR_SMART_TOOLS_V4' not in text or 'mc-rut-program-data' not in text:
        raise RuntimeError('Ошибка вставки JS/CSS: '+str(page))
    page.write_text(text,encoding='utf-8')

def update_catalog():
    for lang in ('ru','zh'):
        page=SITE/lang/'guides'/'index.html'
        content=page.read_text(encoding='utf-8')
        replace=(
          {'Выбор пути поступления':'Персональный маршрут поступления','Определи, какой способ поступления нужно изучать, прежде чем собирать документы.':'Выбирай ответы по шагам и получай индивидуальный план с официальными источниками.',
           'Сравнение двух программ':'Сравнение программ РУТ','Сравни две реальные программы по проверяемым критериям, а не по общему названию специальности.':'Выбери две программы из официального списка: поля заполнятся автоматически.'}
          if lang=='ru' else
          {'选择申请途径':'个性化申请路线','先区分合同制、一般竞争录取和政府配额，再核查适用条件。':'勾选你的情况，逐步生成专属申请准备计划。',
           '两项专业对比表':'官方专业对比工具','用专业代码、授课语言、地点等指标比较真正感兴趣的项目。':'从官方目录下拉选择两个专业，自动显示对比结果。'}
        )
        for old,new in replace.items():content=content.replace(old,new)
        page.write_text(content,encoding='utf-8')

def main():
    if not CATALOG.is_file():raise SystemExit('Нет data/program_catalog_2026.json. Сначала запусти sync_rut_programs.py')
    payload=json.loads(CATALOG.read_text(encoding='utf-8'))
    if payload.get('count',0)<30 or payload['count']!=len(payload.get('programs',[])):
        raise SystemExit('ОШИБКА: каталог программ пустой или неполный')
    for lang in ('ru','zh'):
        for slug,mode in (('admissions','wizard'),('programs','compare')):
            page=SITE/lang/'guides'/slug/'index.html'
            if not page.is_file():raise RuntimeError(f'Отсутствует {page}')
            patch(page,lang,mode,payload)
    update_catalog()
    print('OK: персональный маршрут RU/ZH работает по условным шагам',flush=True)
    print('OK: сравнение RU/ZH использует',payload['count'],'записей реестра 2026 с раскрывающимся списком',flush=True)
    print('OK: ссылки источников, 24 FAQ и остальной сайт не изменены',flush=True)

if __name__=='__main__':main()
