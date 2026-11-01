import argparse
from pathlib import Path
from urllib.parse import urlparse
from src.registry import RegistryError, get_dependencies


def parse_args():
    """Получает и проверяет параметры запуска."""
    parser = argparse.ArgumentParser(
        description="Анализ зависимостей npm-пакетов"
    )

    parser.add_argument("--package", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--version", required=True)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--exclude", default="")

    args = parser.parse_args()

    if args.depth < 0:
        parser.error("Глубина не может быть отрицательной")

    if not args.package.strip():
        parser.error("Имя пакета не может быть пустым")

    if not args.version.strip():
        parser.error("Версия не может быть пустой")

    if args.test:
        if not Path(args.source).is_file():
            parser.error("Файл тестового репозитория не найден")
    else:
        url = urlparse(args.source)

        if url.scheme not in ("http", "https") or not url.netloc:
            parser.error("Некорректный URL репозитория")

    return args



def main():
    """Выводит прямые зависимости npm-пакета."""
    args = parse_args()

    if args.test:
        print("Тестовый режим будет добавлен на этапе 3")
        return

    try:
        dependencies = get_dependencies(
            args.source,
            args.package,
            args.version,
        )
    except RegistryError as error:
        print("Ошибка:", error)
        return

    print(f"Зависимости {args.package}@{args.version}:")

    if not dependencies:
        print("Прямых зависимостей нет")

    for name, version in dependencies.items():
        print(f"{name}: {version}")


if __name__ == "__main__":
    main()
