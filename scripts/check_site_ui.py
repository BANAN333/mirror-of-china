#!/usr/bin/env python3
"""Prevent publication with duplicate navigation or missing RU/ZH platforms."""
from pathlib import Path

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

if errors:
    raise SystemExit('MVP UI validation failed:\n- ' + '\n- '.join(errors))
print('OK: one navbar per page, six RU/ZH platforms, immediate redirect, V5 routes, locale guard')
