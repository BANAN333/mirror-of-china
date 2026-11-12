
import json
import sys
from pathlib import Path
from datetime import date
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent

FILES = {
    "ru": ROOT / "data" / "ru" / "faq.json",
    "zh": ROOT / "data" / "zh" / "faq.json",
}

ALLOWED_STATUSES = {"draft", "verified", "outdated", "needs_review"}

REQUIRED_META = {
    "schema_version", "language", "university",
    "last_updated", "source_of_truth"
}

REQUIRED_FIELDS = {
    "id", "category", "question", "answer",
    "source", "last_verified", "status", "notes"
}

errors = 0
warnings = 0


def error(message):
    global errors
    errors += 1
    print(f"ERROR: {message}")


def warning(message):
    global warnings
    warnings += 1
    print(f"WARNING: {message}")


def valid_date(value):
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def valid_url(value):
    if not isinstance(value, str):
        return False

    parsed = urlparse(value)

    if parsed.scheme != "https" or not parsed.netloc:
        return False

    if any(domain in parsed.netloc.lower()
           for domain in ("example.invalid", "example.com", "localhost")):
        return False

    return True


def load_faq(language, path):
    if not path.exists():
        error(f"Файл не найден: {path}")
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        error(f"Ошибка JSON ({language}): {exc}")
        return None
    except OSError as exc:
        error(f"Не удалось прочитать {path}: {exc}")
        return None

    if not isinstance(data, dict):
        error(f"{language}: корень JSON должен быть объектом")
        return None

    meta = data.get("meta")

    if not isinstance(meta, dict):
        error(f"{language}: отсутствует объект meta")
        return None

    missing_meta = REQUIRED_META - meta.keys()
    if missing_meta:
        error(f"{language}: отсутствуют поля meta: {missing_meta}")

    if meta.get("language") != language:
        error(f"{language}: неверный язык в meta")

    if not valid_date(meta.get("last_updated")):
        error(f"{language}: некорректная дата meta.last_updated")

    if not valid_url(meta.get("source_of_truth")):
        warning(f"{language}: source_of_truth отсутствует или является тестовой ссылкой")

    if not isinstance(data.get("items"), list):
        error(f"{language}: поле items должно быть списком")
        return None

    return data


def validate_items(language, data):
    ids = set()

    for index, item in enumerate(data["items"], start=1):
        prefix = f"{language}, запись {index}"

        if not isinstance(item, dict):
            error(f"{prefix}: ожидался объект")
            continue

        missing = REQUIRED_FIELDS - item.keys()
        if missing:
            error(f"{prefix}: отсутствуют поля {missing}")

        item_id = item.get("id")

        if not isinstance(item_id, str) or not item_id.strip():
            error(f"{prefix}: некорректный ID")
        elif item_id in ids:
            error(f"{prefix}: повторяется ID {item_id}")
        else:
            ids.add(item_id)

        for field in ("category", "question", "answer", "notes"):
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                error(f"{prefix}: поле {field} пустое или некорректное")

        status = item.get("status")

        if status not in ALLOWED_STATUSES:
            error(f"{prefix}: недопустимый статус {status}")
        elif status != "verified":
            warning(f"{prefix}: запись {item_id} не проверена")

        last_verified = item.get("last_verified")
        if not valid_date(last_verified):
            error(f"{prefix}: некорректная дата last_verified")

        source = item.get("source")

        if not isinstance(source, dict):
            error(f"{prefix}: source должен быть объектом")
            continue

        for field in ("url", "title", "type"):
            value = source.get(field)
            if not isinstance(value, str) or not value.strip():
                error(f"{prefix}: отсутствует или пустое поле source.{field}")

        source_url = source.get("url")

        if not valid_url(source_url):
            warning(f"{prefix}: ссылка на источник не является подтверждённым HTTPS-адресом")

        if status == "verified":
            if not valid_url(source_url):
                error(f"{prefix}: verified-запись не может иметь недействительный источник")

            if not valid_date(last_verified):
                error(f"{prefix}: verified-запись должна иметь корректную дату проверки")

    return ids


def main():
    databases = {}

    print("=== ПРОВЕРКА БАЗЫ ЗНАНИЙ ===\n")

    for language, path in FILES.items():
        print(f"Проверка языка: {language}")

        data = load_faq(language, path)

        if data is not None:
            databases[language] = validate_items(language, data)

        print()

    if "ru" in databases and "zh" in databases:
        if databases["ru"] != databases["zh"]:
            error("ID русской и китайской баз не совпадают!")
            print("Только в RU:", databases["ru"] - databases["zh"])
            print("Только в ZH:", databases["zh"] - databases["ru"])
        else:
            print("OK: ID русской и китайской баз совпадают.")

    print("\n=== ИТОГ ===")
    print(f"Ошибок: {errors}")
    print(f"Предупреждений: {warnings}")

    if errors > 0 or len(databases) != 2:
        print("Проверка завершена с ошибками.")
        sys.exit(1)

    print("Критических структурных ошибок нет.")
    sys.exit(0)


if __name__ == "__main__":
    main()
