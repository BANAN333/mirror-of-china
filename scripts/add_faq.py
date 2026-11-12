
import argparse
import json
import os
import shutil
import subprocess
import sys

from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

FILES = {
    "ru": ROOT / "data" / "ru" / "faq.json",
    "zh": ROOT / "data" / "zh" / "faq.json",
}

VALIDATOR = ROOT / "scripts" / "validate_faq.py"
BACKUP_DIR = ROOT / "backups"

REQUIRED_FIELDS = {
    "id",
    "category",
    "question",
    "answer",
    "source",
    "last_verified",
    "status",
    "notes",
}


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    temporary = path.with_suffix(path.suffix + ".tmp")

    with temporary.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")

    return temporary


def validate_entry(entry, language):
    if not isinstance(entry, dict):
        raise ValueError(f"{language}: запись должна быть JSON-объектом")

    missing = REQUIRED_FIELDS - entry.keys()

    if missing:
        raise ValueError(
            f"{language}: отсутствуют обязательные поля: {sorted(missing)}"
        )

    for field in REQUIRED_FIELDS:
        if field == "source":
            if not isinstance(entry[field], dict):
                raise ValueError(f"{language}: source должен быть объектом")
        elif not isinstance(entry[field], str) or not entry[field].strip():
            raise ValueError(f"{language}: поле {field} пустое или некорректное")

    if entry["status"] not in {
        "draft", "verified", "outdated", "needs_review"
    }:
        raise ValueError(f"{language}: недопустимый status")


def run_validator():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    print(result.stdout)

    if result.stderr:
        print(result.stderr)

    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Добавление новой FAQ-записи в RU и ZH базы"
    )
    parser.add_argument(
        "entry_file",
        nargs="?",
        default="data/new_faq.json",
        help="Путь к файлу с новой RU и ZH записью",
    )

    args = parser.parse_args()
    entry_path = ROOT / args.entry_file

    if not entry_path.exists():
        raise FileNotFoundError(
            f"Файл новой записи не найден: {entry_path}"
        )

    if not VALIDATOR.exists():
        raise FileNotFoundError(f"Не найден валидатор: {VALIDATOR}")

    print("=== ДОБАВЛЕНИЕ FAQ ===")

    new_entries = load_json(entry_path)

    if not isinstance(new_entries, dict):
        raise ValueError("Файл новой записи должен содержать объект")

    if "ru" not in new_entries or "zh" not in new_entries:
        raise ValueError("В файле должны присутствовать записи ru и zh")

    ru_entry = new_entries["ru"]
    zh_entry = new_entries["zh"]

    validate_entry(ru_entry, "RU")
    validate_entry(zh_entry, "ZH")

    if ru_entry["id"] != zh_entry["id"]:
        raise ValueError("ID русской и китайской записей не совпадают")

    new_id = ru_entry["id"]

    databases = {
        language: load_json(path)
        for language, path in FILES.items()
    }

    for language, data in databases.items():
        existing_ids = [
            item.get("id") for item in data.get("items", [])
        ]

        if new_id in existing_ids:
            raise ValueError(
                f"Запись {new_id} уже существует в базе {language.upper()}"
            )

    ru_ids = {item.get("id") for item in databases["ru"]["items"]}
    zh_ids = {item.get("id") for item in databases["zh"]["items"]}

    if ru_ids != zh_ids:
        raise ValueError("Текущие RU и ZH базы уже имеют разные ID")

    if not run_validator():
        raise RuntimeError(
            "Текущие базы не прошли проверку. Добавление отменено."
        )

    databases["ru"]["items"].append(ru_entry)
    databases["zh"]["items"].append(zh_entry)

    today = date.today().isoformat()

    for data in databases.values():
        data["meta"]["last_updated"] = today

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backups = {}

    for language, path in FILES.items():
        backup = BACKUP_DIR / f"faq_{language}_{timestamp}.json"
        shutil.copy2(path, backup)
        backups[language] = backup

    temporary_files = {}

    try:
        for language, path in FILES.items():
            temporary_files[language] = save_json(
                path, databases[language]
            )

        for language, path in FILES.items():
            os.replace(temporary_files[language], path)

        if not run_validator():
            raise RuntimeError("Новая версия баз не прошла проверку")

    except Exception:
        print("Ошибка. Восстанавливаю резервные копии...")

        for language, path in FILES.items():
            shutil.copy2(backups[language], path)

        raise

    finally:
        for temporary in temporary_files.values():
            if temporary.exists():
                temporary.unlink()

    print("Успешно добавлена запись:", new_id)
    print("RU и ZH базы обновлены.")
    print("Резервные копии сохранены в:", BACKUP_DIR)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nОШИБКА: {error}")
        sys.exit(1)
