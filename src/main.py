
import argparse
from pathlib import Path
from urllib.parse import urlparse

from src.graph import build_graph, load_fixture
from src.registry import RegistryError, get_children


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
        try:
            url = urlparse(args.source)
            if url.scheme not in ("http", "https") or not url.netloc:
                parser.error("Некорректный URL репозитория")
        except ValueError:
            parser.error("Некорректный URL репозитория")

    return args


def prepare_source(args):
    """Подготавливает источник зависимостей для DFS."""
    if args.test:
        fixture = load_fixture(args.source)

        if args.package not in fixture:
            raise ValueError(
                f"Пакет {args.package} отсутствует в тестовом графе"
            )

        return args.package, fixture.__getitem__

    def npm_children(package_id):
        """Получает зависимости из реального npm Registry."""
        return get_children(args.source, package_id)

    return f"{args.package}@{args.version}", npm_children


def main():
    """Строит и выводит граф зависимостей."""
    args = parse_args()

    try:
        root, get_children_func = prepare_source(args)

        graph, cycles = build_graph(
            root,
            get_children_func,
            args.depth,
            args.exclude,
        )

    except (RegistryError, OSError, ValueError, RecursionError) as error:
        print("Ошибка:", error)
        return

    print(f"Граф зависимостей: {root}")

    for package, children in graph.items():
        text = ", ".join(children) if children else "нет"
        print(f"{package} -> {text}")

    if cycles:
        print("Найдены циклы:")

        for start, end in cycles:
            print(f"{start} -> {end}")


if __name__ == "__main__":
    main()
