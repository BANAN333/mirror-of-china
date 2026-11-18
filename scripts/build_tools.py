#!/usr/bin/env python3
# coding: utf-8
"""Add interactive checklists and a budget calculator to the RU/ZH guides."""
from __future__ import annotations
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
SLUGS = ('documents', 'tuition', 'life')

RESET = {'ru': 'Сбросить', 'zh': '清除'}

STYLE = r'''
/* MIRROR_TOOLS_V3 */
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
.mc-field input{width:100%;min-width:0;padding:11px 12px;border:1px solid #cedde9;border-radius:9px;background:#fff;color:#1a3b59;font-size:15px;font-family:inherit}
.mc-field input:focus-visible,.mc-tool-pane button:focus-visible, .mc-tool-pane a:focus-visible{outline:3px solid #e0a634;outline-offset:3px}
.mc-input-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px}
.mc-tool-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:15px}
.mc-tool-btn{font:inherit;font-weight:750;font-size:13px;cursor:pointer;border:1px solid #b8cfdf;border-radius:9px;padding:10px 15px;color:#17466d;background:#f1f7ff}
.mc-tool-btn:hover{background:#dfedfa}
.mc-progress{height:9px;border-radius:99px;background:#e5edf4;overflow:hidden;margin:12px 0}
.mc-progress span{display:block;background:#238a75;height:100%;width:0;transition:width .2s}
.mc-tool-total{font-size:clamp(22px,3vw,32px);color:#123f64;font-weight:900;font-variant-numeric:tabular-nums}
.mc-check-section{margin:17px 0}.mc-check-section h3{font-size:16px;margin:0 0 10px;color:#20496c}
.mc-check-section .mc-tool-choice{margin-bottom:7px}
.mc-tool-foot{font-size:12px;color:#637b92;margin:15px 0 6px;line-height:1.7}
@media(max-width:690px){.mc-input-grid{grid-template-columns:1fr}.mc-tool-pane{padding:19px}}
@media(prefers-reduced-motion:reduce){.mc-progress span{transition:none}}
'''


def e(value: str) -> str:
    return html.escape(str(value), quote=True)


def checkbox_group(lang:str, groups:list[tuple[str,list[str]]], ident:str)->str:
    out=[]
    for i, (title, labels) in enumerate(groups):
        boxes=''.join(f'<label class="mc-tool-choice"><input type="checkbox" data-mc-check="{ident}-{i}-{j}"><span>{e(label)}</span></label>' for j,label in enumerate(labels))
        out.append(f'<section class="mc-check-section"><h3>{e(title)}</h3>{boxes}</section>')
    small='已核对' if lang=='zh' else 'Проверено'
    return (f'<div data-mc-checklist="{ident}"><p class="mc-tool-total"><span data-mc-count>0</span> / <span data-mc-max>0</span></p>'
            f'<div class="mc-progress"><span data-mc-progress></span></div>{"".join(out)}</div>'
            f'<div class="mc-tool-actions"><button type="button" class="mc-tool-btn" data-mc-reset="{ident}">{e(RESET[lang])}</button></div>'
            f'<p class="mc-tool-foot">{e(small)} · '+('只保存在当前浏览器，不代表已提交材料。' if lang=='zh' else 'Отметки хранятся в браузере, а не в личном кабинете университета.')+'</p>')


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
    return {'documents': documents_tool, 'tuition': tuition_tool, 'life': life_tool}[slug](lang)


def js_for(lang: str, slug: str) -> str:
    if slug in ('documents','life'):
        key='mirror-tools-v3-'+slug
        return r'''(()=>{const root=document.querySelector('[data-mc-checklist]');if(!root)return;const boxes=[...root.querySelectorAll('[data-mc-check]')];const key=__KEY__;let selected=[];try{const v=JSON.parse(localStorage.getItem(key)||'[]');if(Array.isArray(v))selected=v;}catch(_){ }boxes.forEach(b=>b.checked=selected.includes(b.dataset.mcCheck));function refresh(){const checked=boxes.filter(b=>b.checked).map(b=>b.dataset.mcCheck);root.querySelector('[data-mc-count]').textContent=checked.length;root.querySelector('[data-mc-max]').textContent=boxes.length;root.querySelector('[data-mc-progress]').style.width=(100*checked.length/Math.max(boxes.length,1))+'%';try{localStorage.setItem(key,JSON.stringify(checked));}catch(_){} }boxes.forEach(b=>b.addEventListener('change',refresh));document.querySelector('[data-mc-reset]').addEventListener('click',()=>{boxes.forEach(b=>b.checked=false);refresh();});refresh();})();'''.replace('__KEY__',json.dumps(key))
    if slug=='tuition':
        strings= {'ru':('Учёба','Жильё','Другие расходы'), 'zh':('学费','住宿','其他支出')}[lang]
        return r'''(()=>{const fields=[...document.querySelectorAll('[data-mc-budget]')];const fmt=new Intl.NumberFormat('__LANG__',{maximumFractionDigits:0});const labels=__LABELS__;function refresh(){const obj={};fields.forEach(f=>obj[f.dataset.mcBudget]=Math.min(100000000,Math.max(0,Number(f.value)||0)));const a=obj.semester*obj.semesters,b=obj.housing*obj.months,c=obj.other*obj.months;document.getElementById('mc-budget-total').textContent=fmt.format(a+b+c);document.getElementById('mc-budget-breakdown').textContent=labels[0]+': '+fmt.format(a)+' ₽ · '+labels[1]+': '+fmt.format(b)+' ₽ · '+labels[2]+': '+fmt.format(c)+' ₽';}fields.forEach(el=>el.addEventListener('input',refresh));refresh();})();'''.replace('__LANG__','zh-CN' if lang=='zh' else 'ru-RU').replace('__LABELS__',json.dumps(strings,ensure_ascii=False))
    return ''


def add_style(text:str)->str:
    if '/* MIRROR_TOOLS_V3 */' not in text:
        text=re.sub(r'</head>',lambda m:'<style>'+STYLE+'</style>'+m.group(0),text,count=1,flags=re.I)
    return text


def do_detail(page:Path, lang:str, slug:str):
    text = page.read_text(encoding='utf-8-sig')
    # Keep the article visible and indexable. The calculator and checklists are
    # optional actions below the guide.
    marker = '<nav class="links"' if lang == 'zh' else '<div class="rg-other">'
    if marker not in text:
        raise RuntimeError(f'Гайд {lang}/{slug}: не найден блок связанных ссылок')
    if 'class="mc-tool-pane"' in text:
        return
    tool = content_for(lang, slug)
    text = text.replace(marker, tool + marker, 1)
    text = add_style(text)
    script = js_for(lang, slug)
    if script:
        text = text.replace('</body>', '<script>' + script + '</script></body>', 1)
    page.write_text(text,encoding='utf-8')


def main():
    for lang in ('ru','zh'):
        folder=SITE/lang/'guides'
        for slug in SLUGS:
            page = folder / slug / 'index.html'
            if not page.is_file():
                raise RuntimeError(f'Нет материала {page}')
            do_detail(page, lang, slug)
    print('OK: инструменты подготовки документов, бюджета и приезда добавлены в гайды RU/ZH')

if __name__=='__main__':
    main()
