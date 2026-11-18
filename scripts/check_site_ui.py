#!/usr/bin/env python3
"""Check the generated RU/ZH navigation, guide pages, and application routes."""
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

from site_config import SITE_URL

GUIDES = ('admissions', 'documents', 'programs', 'tuition', 'life')
LOCALES = {'ru': 'ru', 'zh': 'zh-CN'}

SITE = Path(__file__).resolve().parent.parent / 'site'
errors = []

def read(relative):
    path = SITE / relative
    if not path.is_file():
        errors.append(f'Missing: {relative}')
        return ''
    return path.read_text(encoding='utf-8')

pages = ['index.html', 'open-data/index.html']
for lang in ('ru', 'zh'):
    pages.extend([
        f'{lang}/index.html',
        f'{lang}/resources/index.html',
        f'{lang}/guides/index.html',
        f'{lang}/checklist/index.html',
    ])
    resources = read(f'{lang}/resources/index.html')
    count = resources.count('class="mc-portal-card"')
    if count != 6 or 'AtomGit / GitCode' not in resources or 'Zenodo' not in resources:
        errors.append(f'{lang}: expected six platforms, got {count}')
    if 'https://doi.org/10.5281/zenodo.24219015' not in resources or 'aria-disabled="true"><strong>Zenodo' in resources:
        errors.append(f'{lang}: Zenodo MVP DOI link must be active')
    for section in ('guides', 'checklist'):
        page = read(f'{lang}/{section}/index.html')
        if f'data-lang="{lang}"' not in page:
            errors.append(f'{lang}/{section}: wrong application language')
        if 'href="../resources/index.html"' not in page:
            errors.append(f'{lang}/{section}: platform navigation uses legacy redirect')
        if 'src="../../assets/admissions_v5.js"' not in page:
            errors.append(f'{lang}/{section}: missing V5 JavaScript')

for relative in pages:
    page = read(relative)
    count = page.count('class="mc-site-nav"')
    if count != 1:
        errors.append(f'{relative}: expected one menu, got {count}')
    if 'class="v5-nav"' in page:
        errors.append(f'{relative}: duplicate V5 navigation')

home = read('index.html')
if 'MIRROR_HOME_GUARD_BEGIN' not in home or 'classList.remove("mc-zh-pending")' not in home:
    errors.append('index.html: language flicker guard missing')

old = read('resources/index.html')
if 'content="0; url=../ru/resources/index.html"' not in old:
    errors.append('legacy resources: not an immediate redirect')
if 'body{display:none!important}' not in old:
    errors.append('legacy resources: intermediate page can flash')
if 'class="mc-site-nav"' in old:
    errors.append('legacy resources: must not show navbar before redirect')

application = read('assets/admissions_v5.js')
if '.mc-lang, .v5-switch' not in application or '.mc-links a[href*=' not in application:
    errors.append('V5: broken plan language switching')


class GuidePage(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.links = {}
        self.official_sources = set()
        self.main_headings = 0
        self.in_main = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'main':
            self.in_main = True
        elif tag == 'h1' and self.in_main:
            self.main_headings += 1
        elif tag == 'meta':
            name = values.get('name') or values.get('http-equiv', '').lower()
            if name:
                self.meta[name] = values.get('content', '')
        elif tag == 'link':
            rel = values.get('rel')
            if rel in ('canonical', 'alternate'):
                self.links[(rel, values.get('hreflang'))] = values.get('href')
        elif tag == 'a' and self.in_main:
            href = values.get('href', '')
            if href.startswith(('https://rut-miit.ru/', 'https://www.rut-miit.ru/',
                                'https://navigator.rut-miit.ru/')):
                self.official_sources.add(href)

    def handle_endtag(self, tag):
        if tag == 'main':
            self.in_main = False


sitemap = ElementTree.fromstring(read('sitemap.xml'))
sitemap_urls = [node.text for node in sitemap.findall('.//{*}loc')]
if len(sitemap_urls) != len(set(sitemap_urls)):
    errors.append('sitemap.xml contains duplicate URLs')

for lang in LOCALES:
    faq = read(f'{lang}/index.html')
    for slug in GUIDES:
        route = f'{lang}/guides/{slug}/'
        relative = route + 'index.html'
        guide = read(relative)
        if f'href="guides/{slug}/index.html"' not in faq:
            errors.append(f'{relative}: no direct link from FAQ')
        if guide.count('class="mc-site-nav"') != 1:
            errors.append(f'{relative}: guide must have one shared menu')
        page = GuidePage()
        page.feed(guide)
        if page.main_headings != 1 or not page.official_sources:
            errors.append(f'{relative}: missing static guide heading or official sources')
        url = SITE_URL + route
        if 'refresh' in page.meta or 'noindex' in page.meta.get('robots', ''):
            errors.append(f'{relative}: guide must be indexable and serve its content directly')
        if page.links.get(('canonical', None)) != url or url not in sitemap_urls:
            errors.append(f'{relative}: canonical or sitemap URL mismatch')
        for alternate, alternate_locale in LOCALES.items():
            if page.links.get(('alternate', alternate_locale)) != f'{SITE_URL}{alternate}/guides/{slug}/':
                errors.append(f'{relative}: missing {alternate_locale} alternate')

if errors:
    raise SystemExit('MVP UI validation failed:\n- ' + '\n- '.join(errors))
print('OK: one navbar per page, six RU/ZH platforms, immediate redirect, V5 routes, and 10 indexable bilingual guides')
