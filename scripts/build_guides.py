#!/usr/bin/env python3
"""Build five standalone Chinese information guides for Mirror of China.

Standard-library only; deterministic; no network access. Run AFTER
scripts/build_site.py and scripts/build_distribution.py, since those regenerate
site/index.html and sitemap.xml. This builder never touches FAQ JSON data.
"""
from __future__ import annotations
import html
import json
import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'distribution' / 'guidebook'
DEST = ROOT / 'site' / 'zh' / 'guides'
BASE = 'https://banan333.github.io/mirror-of-china/'
GUARD_START = '<!-- MIRROR_GUIDES_NAV_START -->'
GUARD_END = '<!-- MIRROR_GUIDES_NAV_END -->'


def inline(text: str) -> str:
    """Escape HTML and format only Markdown's simple inline forms."""
    value = html.escape(text, quote=True)
    value = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',
                   lambda m: '<a href="'+html.escape(html.unescape(m[2]),quote=True)+'" rel="noopener noreferrer">'+m[1]+'</a>', value)
    value = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', value)
    value = re.sub(r'`([^`]+)`', r'<code>\1</code>', value)
    return value


def render_md(md: str) -> str:
    blocks=[]; para=[]; listtype=None; items=[]
    def para_flush():
        nonlocal para
        if para:
            blocks.append('<p>'+inline(' '.join(para))+'</p>');para=[]
    def list_flush():
        nonlocal items,listtype
        if items:
            tag = 'ol' if listtype=='ol' else 'ul'
            blocks.append('<'+tag+'>'+''.join('<li>'+inline(i)+'</li>' for i in items)+'</'+tag+'>')
            items=[];listtype=None
    for raw in md.splitlines():
        line=raw.strip()
        if not line:
            para_flush();list_flush();continue
        if line.startswith('# '):
            para_flush();list_flush();blocks.append('<h1>'+inline(line[2:])+'</h1>');continue
        if line.startswith('## '):
            para_flush();list_flush();blocks.append('<h2>'+inline(line[3:])+'</h2>');continue
        if line.startswith('> '):
            para_flush();list_flush();blocks.append('<blockquote>'+inline(line[2:])+'</blockquote>');continue
        li=re.match(r'^(- |\d+\. )(.*)$',line)
        if li:
            para_flush();t='ol' if li[1][0]!='-' else 'ul'
            if listtype is not None and listtype!=t:list_flush()
            listtype=t;items.append(li[2]);continue
        list_flush();para.append(line)
    para_flush();list_flush()
    return '\n'.join(blocks)


def page(title: str, desc: str, canonical: str, body: str, links: str, article: bool) -> str:
    schema={'@context':'https://schema.org','@type':'Article' if article else 'CollectionPage',
            'headline':title,'description':desc,'inLanguage':'zh-CN',
            'mainEntityOfPage':canonical}
    if article:
        schema.update({'author':{'@type':'Organization','name':'Зеркало Поднебесной — independent student research project'},
                       'datePublished':'2026-11-13','dateModified':'2026-11-13'})
    jsonld=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    h=lambda x:html.escape(x,quote=True)
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{h(title)} | 天朝之镜</title>
<meta name="description" content="{h(desc)}"/>
<meta name="robots" content="index,follow"/>
<link rel="canonical" href="{h(canonical)}"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="{h(title)}"/>
<meta property="og:url" content="{h(canonical)}"/>
<script type="application/ld+json">{jsonld}</script>
<style>
:root{{color-scheme:light}}*{{box-sizing:border-box}}body{{margin:0;font-family:system-ui,-apple-system,'Noto Sans SC','Microsoft YaHei',sans-serif;background:#f5f8fd;color:#19304e;line-height:1.8}}.wrap{{max-width:880px;margin:0 auto;padding:24px}}a{{color:#1762b0;text-decoration:underline;text-underline-offset:3px}}a:hover{{color:#0b3c75}}nav{{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:25px}}.sheet{{padding:clamp(20px,4vw,45px);background:white;border:1px solid #e0e9f3;border-radius:20px;box-shadow:0 7px 34px #172b4d10}}h1{{font-size:clamp(24px,4vw,36px);line-height:1.3;margin:0 0 24px}}h2{{font-size:22px;line-height:1.4;padding-top:16px;margin-top:28px;border-top:1px solid #e8edf5}}p,li{{font-size:16px}}blockquote{{margin:18px 0;padding:15px 20px;border-left:4px solid #408bd4;background:#eff6fd;color:#365375}}li{{margin:7px 0}}ul,ol{{padding-left:23px}}code{{background:#f0f3f9;border-radius:5px;padding:2px 5px}}.links{{margin-top:36px;padding-top:20px;border-top:2px solid #edf2f8}}.links a{{display:inline-block;margin:7px 15px 7px 0}}footer{{font-size:13px;color:#617590;margin-top:23px}}@media(max-width:550px){{.wrap{{padding:12px}}.sheet{{border-radius:12px}}}}</style></head>
<body><div class="wrap"><nav><a href="{h(BASE)}zh/index.html">← 中文 FAQ</a><a href="{h(BASE)}zh/guides/index.html">专题指南</a><a href="{h(BASE)}open-data/">开放数据</a></nav>
<main class="sheet">{body}<div class="links"><strong>继续阅读：</strong><div>{links}</div></div></main>
<footer>独立学生信息整理项目「Зеркало Поднебесной」。不是俄罗斯交通大学官方网站。资料核对日期：2026-11-13。</footer></div></body></html>'''


def insert_nav(path: Path, href: str, label: str):
    if not path.is_file():
        raise RuntimeError('Не найден сайт: '+str(path))
    old=path.read_text(encoding='utf-8-sig')
    fragment=f'''{GUARD_START}<aside style="max-width:980px;margin:18px auto;padding:16px 22px;border:1px solid #81a7c6;border-radius:12px;background:#f1f7fd;color:#203e5c;font-family:system-ui,sans-serif"><strong>留学专题指南：</strong> <a href="{href}">{label}</a> · 5 篇独立中文文章，附学校官方来源。</aside>{GUARD_END}'''
    if (GUARD_START in old)!=(GUARD_END in old):
        raise RuntimeError('Непарные маркеры ссылок на гиды: '+str(path))
    if GUARD_START in old:
        old=old[:old.index(GUARD_START)]+old[old.index(GUARD_END)+len(GUARD_END):]
    match=re.search(r'<main\b[^>]*>',old,re.IGNORECASE)
    if match:
        old=old[:match.end()]+fragment+old[match.end():]
    elif '</body>' in old:
        old=old.replace('</body>',fragment+'</body>',1)
    else:raise RuntimeError('Не найден маркер main/body в '+str(path))
    path.write_text(old,encoding='utf-8')


def sitemap_add(urls: list[str]):
    path=ROOT/'site'/'sitemap.xml'
    if not path.exists():raise RuntimeError('Сначала запусти build_site.py и build_distribution.py')
    ns='http://www.sitemaps.org/schemas/sitemap/0.9'
    xhtml='http://www.w3.org/1999/xhtml'
    ET.register_namespace('',ns);ET.register_namespace('xhtml',xhtml)
    tree=ET.parse(path); r=tree.getroot()
    existing={x.text for x in r.findall(f'.//{{{ns}}}loc')}
    for url in urls:
        if url in existing:continue
        e=ET.SubElement(r,f'{{{ns}}}url')
        loc=ET.SubElement(e,f'{{{ns}}}loc');loc.text=url
        existing.add(url)
    tree.write(path,encoding='utf-8',xml_declaration=True)


def main():
    meta=json.loads((SOURCE/'guides.json').read_text(encoding='utf-8'))
    if len(meta)!=5 or len({x['slug'] for x in meta})!=5:
        raise RuntimeError('Ожидаются пять уникальных материалов')
    if not (ROOT/'data'/'ru'/'faq.json').is_file() or not (ROOT/'site'/'zh'/'index.html').is_file():
        raise RuntimeError('Запусти из проекта после сборки сайта. Не найден data/ru/faq.json или site/zh/index.html')
    DEST.mkdir(parents=True,exist_ok=True)
    links=''.join(f'<li><a href="{html.escape(x["slug"],quote=True)}/index.html">{html.escape(x["title"])}</a></li>' for x in meta)
    index_title='俄罗斯交通大学：中国申请者的五大专题指南'
    index_desc='入学申请、材料准备、专业选择、学费与住宿生活。独立中文指南，附俄罗斯交通大学官方来源。'
    idx_body='<h1>'+index_title+'</h1><blockquote>独立学生资料整理项目，非学校官方招生公告。相关招生规定以当年官网为准。</blockquote><p>按具体问题选择专题，所有材料均附原始大学来源：</p><ol>'+links+'</ol>'
    index_url=BASE+'zh/guides/'
    (DEST/'index.html').write_text(page(index_title,index_desc,index_url,idx_body,'<a href="../index.html">查看24组双语FAQ</a>',False),encoding='utf-8')
    urls=[index_url]
    for x in meta:
        slug=x['slug']; src=SOURCE/'zh'/f'{slug}.md'
        if not re.fullmatch('[a-z-]+',slug):raise RuntimeError('Недопустимый slug')
        md=src.read_text(encoding='utf-8')
        if not all(u in md for u in x['sources']):
            raise RuntimeError('Отсутствуют официальные ссылки в '+str(src))
        out=DEST/slug;out.mkdir(parents=True,exist_ok=True)
        url=index_url+slug+'/'
        others=''.join('<a href="../'+html.escape(t['slug'])+'/index.html">'+html.escape(t['title'])+'</a>' for t in meta if t['slug']!=slug)
        (out/'index.html').write_text(page(x['title'],x['description'],url,render_md(md),others,True),encoding='utf-8')
        urls.append(url)
    insert_nav(ROOT/'site'/'zh'/'index.html', './guides/index.html','查看专题指南')
    insert_nav(ROOT/'site'/'index.html','./zh/guides/index.html','中国申请者指南')
    sitemap_add(urls)
    assert len(list(DEST.glob('*/index.html')))==5
    for x in meta:
        p=DEST/x['slug']/'index.html'
        t=p.read_text(encoding='utf-8')
        assert '<html lang="zh-CN">' in t and 'application/ld+json' in t
        assert 'https://rut-miit.ru/' in t
        assert x['title'] in t
    print('OK: 5 самостоятельных HTML-гайдов созданы, индекс готов')
    print('OK: ссылки добавлены на главную и китайскую FAQ-страницу')
    print('OK: sitemap.xml содержит 6 новых адресов (индекс + 5 статей)')
    print('Исходники статей: distribution/guidebook/zh/*.md')
    print('Сайт: site/zh/guides/index.html')
    print('ВАЖНО: после каждой сборки сайта заново запускай scripts/build_guides.py последним.')

if __name__=='__main__':
    try:main()
    except Exception as exc:raise SystemExit('ОШИБКА: '+str(exc))
