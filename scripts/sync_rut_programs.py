#!/usr/bin/env python3
# coding: utf-8
"""Download the 2026 educational-plan registry published by RUT (MIIT).

Only copies factual program labels/level/form/source references. It DOES NOT
assert that enrollment is currently open or that any particular financing is
available to foreign applicants. Uses standard library only.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'data' / 'program_catalog_2026.json'
SOURCE_URLS = [
    'https://rut-miit.ru/sveden/education/programs',
    'https://www.rut-miit.ru/sveden/education/programs',
    'https://miit.ru/sveden/education/programs',
    'https://www.miit.ru/sveden/education/programs',
]
ALLOWED_HOSTS = {'rut-miit.ru', 'www.rut-miit.ru','miit.ru','www.miit.ru'}

class ProgramsHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows=[]; self.row=None; self.cell=None; self.depth=0
        self.ignored=0
    def handle_starttag(self, tag, attrs):
        tag=tag.lower()
        if tag in ('script','style'):
            self.ignored+=1
            return
        if self.ignored: return
        if tag=='tr':
            self.row=[]
        elif tag in ('td','th') and self.row is not None:
            self.cell={'parts':[],'links':[],'kind':tag}
        elif tag=='a' and self.cell is not None:
            attrs=dict(attrs)
            href=attrs.get('href','')
            if href: self.cell['links'].append(href)
        elif tag in ('br','p','div','li') and self.cell is not None:
            self.cell['parts'].append(' ')
    def handle_endtag(self, tag):
        tag=tag.lower()
        if tag in ('script','style'):
            self.ignored=max(0,self.ignored-1)
            return
        if self.ignored:return
        if tag in ('td','th') and self.cell is not None and self.row is not None:
            cell=self.cell
            cell['text']=' '.join(''.join(cell['parts']).split())
            self.row.append(cell)
            self.cell=None
        elif tag=='tr' and self.row is not None:
            if self.row: self.rows.append(self.row)
            self.row=None
    def handle_data(self, data):
        if self.cell is not None and not self.ignored:
            self.cell['parts'].append(data)

def level_group(code:str, level:str)->str:
    l=level.lower()
    if 'аспирантур' in l or re.fullmatch(r'\d\.\d+(?:\.\d+)?',code):return 'asp'
    if 'магистр' in l or 'специализированное высшее' in l:return 'master'
    if 'бакалавр' in l or 'специалитет' in l or 'базовое высшее' in l:return 'basic'
    return 'other'

def discipline(code:str)->str:
    groups={
     '01':'Математика','02':'Компьютерные науки','05':'Науки о Земле','07':'Архитектура',
     '08':'Строительство','09':'IT и информатика','10':'Информационная безопасность',
     '11':'Связь','12':'Приборостроение','13':'Энергетика','15':'Машиностроение',
     '20':'Безопасность','21':'Геодезия и кадастр','23':'Транспорт','25':'Авиация',
     '27':'Управление в технике','28':'Нанотехнологии','29':'Технологии','35':'Природные ресурсы',
     '38':'Экономика и управление','40':'Право','42':'Медиа и коммуникации','43':'Сервис',
     '44':'Педагогика','45':'Лингвистика','46':'История','49':'Спорт','54':'Дизайн',
    }
    return groups.get(code[:2], 'Другие направления')

def discipline_zh(code: str) -> str:
    groups = {
      '01':'数学','02':'计算机科学','05':'地球科学','07':'建筑学','08':'土木工程',
      '09':'信息技术','10':'信息安全','11':'通信技术','12':'仪器技术',
      '13':'能源工程','15':'机械工程','20':'安全工程','21':'测绘与地籍',
      '23':'交通运输','25':'航空技术','27':'技术管理',
      '38':'经济与管理','40':'法律','42':'传媒','43':'服务管理',
      '44':'教育','45':'语言学','46':'历史','49':'体育','54':'设计'
    }
    return groups.get(code[:2], '其他专业领域')

def official_link(href: str, base: str)->str|None:
    u=urljoin(base,href)
    p=urlparse(u)
    if p.scheme=='https' and p.hostname and (p.hostname in ALLOWED_HOSTS or p.hostname.endswith('.miit.ru') or p.hostname.endswith('.rut-miit.ru')):
        return u
    return None

def extract_programs(source_html:str, source_url:str)->list[dict]:
    parser=ProgramsHTML()
    parser.feed(source_html)
    found=[]; seen=set()
    for cells in parser.rows:
        if len(cells)<6 or any(x['kind']!='td' for x in cells[:5]):continue
        code,major,profile,level,mode,desc=(x['text'] for x in cells[:6])
        code=code.strip()
        if not re.fullmatch(r'\d{1,2}\.\d{1,2}\.\d{1,2}|\d\.\d+\.\d+',code):continue
        if not major or major=='-':continue
        if not re.search(r'\bОП\s*2026\b',desc,re.I):continue
        if level_group(code,level)=='other':continue
        profile='' if profile=='-' else profile
        key=(code,major,profile,level,mode)
        if key in seen:continue
        seen.add(key)
        direct=None
        for link in cells[5]['links']:
            good=official_link(link,source_url)
            if good:direct=good;break
        found.append({
            'id': 'rut26-'+str(len(found)+1).zfill(4),
            'code': code, 'name':major, 'profile':profile,
            'degree':level,'group':level_group(code,level),
            'mode':mode,'discipline':discipline(code),'discipline_zh':discipline_zh(code),
            'year':2026,
            'curriculum_url':direct or source_url,
            'registry_url':source_url,
        })
    return sorted(found, key=lambda p:(p['group'],p['code'],p['profile'].casefold(),p['mode']))

def download(url:str)->str:
    req=Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; MirrorOfChinaEducationalCatalog/1.0; independent student research)', 'Accept-Language':'ru-RU,ru;q=0.9', 'Accept':'text/html'})
    with urlopen(req,timeout=24) as resp:
        raw=resp.read(22_000_000)
        charset=resp.headers.get_content_charset() or 'utf-8'
    return raw.decode(charset,errors='replace')

def main():
    ap=argparse.ArgumentParser(description='Синхронизация образовательных программ РУТ с официального реестра')
    ap.add_argument('--html',type=Path,help='Локальный HTML, сохранённый с официального сайта; полезно при сетевых ограничениях')
    ap.add_argument('--source-url',default=SOURCE_URLS[0],help='Адрес официальной HTML-страницы при использовании --html')
    args=ap.parse_args()
    diagnostics=[]
    sources=[(args.source_url,args.html.read_text(encoding='utf-8-sig',errors='replace'))] if args.html else []
    if not sources:
        for url in SOURCE_URLS:
            try:
                print('Загрузка:',url,flush=True)
                sources.append((url,download(url)))
            except Exception as ex:
                diagnostics.append(f'{url}: {type(ex).__name__}: {ex}')
    best=[]; besturl=''
    for url,markup in sources:
        entries=extract_programs(markup,url)
        print('Найдено записей 2026:',len(entries),'из',url,flush=True)
        if len(entries)>len(best):best=entries;besturl=url
        if len(entries)>=30:break
    if len(best)<30:
        raise SystemExit('ОШИБКА: официальный реестр не удалось достоверно прочитать (меньше 30 программ).\n'
            'Ничего не перезаписано. Попробуй открыть https://rut-miit.ru/sveden/education/programs в браузере, '
            'сохранить страницу как HTML и запустить: python .\\scripts\\sync_rut_programs.py --html "путь_к_странице.html"\n'
            +'\n'.join(diagnostics[:4]))
    payload={
        'schema_version':'1.0','source':besturl,'curriculum_year':2026,
        'captured_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'scope':'Official registry rows having links named ОП 2026. Not confirmation of admission or places.',
        'count':len(best),'programs':best,
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    tmp=OUTPUT.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(OUTPUT)
    by_group={v:sum(p['group']==v for p in best) for v in ('basic','master','asp')}
    print(f'ГОТОВО: {OUTPUT} ({len(best)} вариантов программ/форм обучения, {by_group})',flush=True)
    print('ВАЖНО: это программы из образовательного реестра, не гарантированный список открытого приёма иностранных граждан.',flush=True)

if __name__=='__main__': main()
