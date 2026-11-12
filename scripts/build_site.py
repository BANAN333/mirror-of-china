
import json
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "site"

LANGUAGES = {
    "ru": {
        "title": "РУТ (МИИТ) — Информация для иностранных абитуриентов",
	"description": "Официальная информация РУТ (МИИТ) для иностранных абитуриентов: поступление, документы и обучение.",
        "search": "Поиск по вопросам...",
        "heading": "Часто задаваемые вопросы",
        "language": "中文版本",
        "empty": "Ничего не найдено."
    },
    "zh": {
        "title": "俄罗斯交通大学 — 国际学生信息",
	"description": "俄罗斯交通大学（РУТ МИИТ）国际学生招生、申请材料及学习信息。",
        "search": "搜索问题...",
        "heading": "常见问题",
        "language": "Русская версия",
        "empty": "没有找到相关内容。"
    }
}


def load_faq(language):
    path = DATA_DIR / language / "faq.json"

    if not path.exists():
        raise FileNotFoundError(f"Не найден файл: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data.get("items"), list):
        raise ValueError(f"Некорректная структура: {path}")

    return data


def generate_page(language, data):
    settings = LANGUAGES[language]
    items = data["items"]

    cards = []

    for item in items:
        question = escape(item["question"])
        answer = escape(item["answer"])
        category = escape(item.get("category", ""))
        record_id = escape(item["id"])

        source = item.get("source", {})
        source_url = source.get("url", "")
        source_title = escape(source.get("title", "Источник"))

        if source_url.startswith(("https://", "http://")):
            source_html = (
                f'<a href="{escape(source_url, quote=True)}" '
                f'target="_blank" rel="noopener noreferrer">'
                f'{source_title}</a>'
            )
        else:
            source_html = ""

        cards.append(f"""
        <article class="faq-card" data-search="{escape(
            (question + ' ' + answer + ' ' + category).lower(),
            quote=True
        )}">
            <div class="category">{category}</div>
            <h2>{question}</h2>
            <p>{answer}</p>
            <div class="source">{source_html}</div>
            <small>ID: {record_id}</small>
        </article>
        """)

    other_language = "zh" if language == "ru" else "ru"

    content = "\n".join(cards)
    structured_data = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["answer"]
                }
            }
            for item in items
        ]
    }, ensure_ascii=False).replace("<", "\\u003c")

    return f"""<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(settings["title"])}</title>
    <meta name="description" content="{escape(settings['description'], quote=True)}">
    <script type="application/ld+json">
    {structured_data}
    </script>
    <style>
        * {{ box-sizing: border-box; }}

        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f3f5f8;
            color: #202938;
        }}

        header {{
            background: #17365d;
            color: white;
            padding: 35px 20px;
            text-align: center;
        }}

        main {{
            max-width: 950px;
            margin: 30px auto;
            padding: 0 20px;
        }}

        input {{
            width: 100%;
            padding: 15px;
            border: 1px solid #ccd3dd;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 25px;
        }}

        .faq-card {{
            background: white;
            padding: 24px;
            margin-bottom: 18px;
            border-radius: 10px;
            box-shadow: 0 2px 8px #0000000a;
        }}

        .faq-card h2 {{ font-size: 20px; }}

        .faq-card p {{
            line-height: 1.7;
            white-space: pre-line;
        }}

        .category {{
            color: #3973ad;
            font-size: 13px;
            text-transform: uppercase;
        }}

        .source {{ margin: 15px 0; }}

        a {{ color: #2865a5; }}

        small {{ color: #8993a1; }}

        .language {{
            color: white;
            text-decoration: none;
        }}

        footer {{
            text-align: center;
            padding: 25px;
            color: #77808d;
        }}
    </style>
</head>
<body>
    <header>
        <h1>{escape(settings["heading"])}</h1>
        <a class="language" href="../{other_language}/index.html">
            {escape(settings["language"])}
        </a>
    </header>

    <main>
        <input
            type="search"
            id="search"
            placeholder="{escape(settings["search"], quote=True)}"
        >

        <div id="faq-list">
            {content}
        </div>

        <p id="empty" hidden>{escape(settings["empty"])}</p>
    </main>

    <footer>
        RUT (MIIT) | {data["meta"]["last_updated"]}
    </footer>

    <script>
        const search = document.getElementById("search");
        const cards = document.querySelectorAll(".faq-card");
        const empty = document.getElementById("empty");

        search.addEventListener("input", () => {{
            const query = search.value.toLowerCase().trim();
            let visible = 0;

            cards.forEach(card => {{
                const match = card.dataset.search.includes(query);
                card.hidden = !match;
                if (match) visible++;
            }});

            empty.hidden = visible !== 0;
        }});
    </script>
</body>
</html>
"""



def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    databases = {
        language: load_faq(language)
        for language in LANGUAGES
    }

    # Проверяем совпадение ID всех записей в RU и ZH
    ru_ids = {item["id"] for item in databases["ru"]["items"]}
    zh_ids = {item["id"] for item in databases["zh"]["items"]}

    if ru_ids != zh_ids:
        raise ValueError("ID русской и китайской баз не совпадают!")

    # Оставляем только проверенные записи
    published_databases = {}

    for language, data in databases.items():
        verified_items = [
            item for item in data["items"]
            if item.get("status") == "verified"
        ]

        if not verified_items:
            raise ValueError(
                f"{language.upper()}: нет записей со статусом verified. "
                "Публикация отменена."
            )

        published_databases[language] = {
            **data,
            "items": verified_items
        }

    # Дополнительная проверка совпадения ID публикуемых записей
    ru_published_ids = {
        item["id"] for item in published_databases["ru"]["items"]
    }
    zh_published_ids = {
        item["id"] for item in published_databases["zh"]["items"]
    }

    if ru_published_ids != zh_published_ids:
        raise ValueError(
            "ID проверенных записей RU и ZH не совпадают!"
        )

    # Генерируем страницы
    for language, data in published_databases.items():
        output = OUTPUT_DIR / language
        output.mkdir(parents=True, exist_ok=True)

        page = generate_page(language, data)
        (output / "index.html").write_text(page, encoding="utf-8")

        total = len(databases[language]["items"])
        published = len(data["items"])
        skipped = total - published

        print(
            f"{language.upper()}: опубликовано {published}, "
            f"пропущено {skipped}"
        )

    print(f"\nСайт успешно создан: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
