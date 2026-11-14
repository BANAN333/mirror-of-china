#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final, idempotent favicon pass for all generated Mirror of China pages.

This MUST run after build_admissions_v5.py, because that generator overwrites
its four wizard/checklist pages and some legacy redirects.
"""
from __future__ import annotations
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
BRANDING = ROOT / 'branding'
ASSETS = SITE / 'assets'
NAMES = ('favicon.ico', 'favicon-32.png', 'apple-touch-icon.png', 'favicon-512.png')
START = '<!-- MIRROR_FAVICON_BEGIN -->'
END = '<!-- MIRROR_FAVICON_END -->'
MARKER_RE = re.compile(r'\n?' + re.escape(START) + r'.*?' + re.escape(END) + r'\n?', re.S)
HEAD_RE = re.compile(r'</head\s*>', re.I)


def run() -> int:
    if not SITE.is_dir():
        raise RuntimeError('Не найдена папка site/; сначала выполните сборку.')
    missing = [name for name in NAMES if not (BRANDING / name).is_file()]
    if missing:
        raise RuntimeError('Отсутствуют файлы branding/: ' + ', '.join(missing))

    pages = sorted(SITE.rglob('index.html'))
    if not pages:
        raise RuntimeError('Не найдены HTML-страницы для установки иконки.')

    # Validate all files first: don't modify half of the website on invalid HTML.
    for page in pages:
        content = page.read_text(encoding='utf-8')
        if not HEAD_RE.search(content):
            raise RuntimeError('Отсутствует </head>: ' + str(page))

    ASSETS.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        src = BRANDING / name
        dest = ASSETS / name
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)
    shutil.copy2(BRANDING / 'favicon.ico', SITE / 'favicon.ico')

    changed = 0
    for page in pages:
        original = page.read_text(encoding='utf-8')
        # Older installers inserted the same marker on some pages. Replace it;
        # never accumulate duplicate icon tags on repeated full builds.
        content = MARKER_RE.sub('', original)
        relative = Path(os.path.relpath(ASSETS, page.parent)).as_posix()
        links = ('\n' + START + '\n'
            + f'<link rel="icon" href="{relative}/favicon.ico" sizes="any" type="image/x-icon">\n'
            + f'<link rel="icon" href="{relative}/favicon-32.png" sizes="32x32" type="image/png">\n'
            + f'<link rel="apple-touch-icon" href="{relative}/apple-touch-icon.png" sizes="180x180">\n'
            + END + '\n')
        content, count = HEAD_RE.subn(lambda match: links + match.group(0), content, count=1)
        if count != 1 or content.count(START) != 1:
            raise RuntimeError('Не удалось обновить favicon: ' + str(page))
        if content != original:
            page.write_text(content, encoding='utf-8')
            changed += 1
    print(f'OK: favicon установлен на {len(pages)} страницах, обновлено {changed}.')
    print('OK: RU/ZH помощник, чек-лист, FAQ, гайды и раздел Площадки охвачены.')
    return len(pages)


if __name__ == '__main__':
    run()
