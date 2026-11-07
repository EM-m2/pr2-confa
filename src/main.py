import argparse
from pathlib import Path
from urllib.parse import urlparse
from src.graph import build_graph, load_fixture
from src.registry import RegistryError, get_children
from src.reverse import find_reverse_dependencies
from src.visualization import visualize

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
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("--target", default=None)
    parser.add_argument("--visualize", action="store_true")

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

    if args.target is not None and not args.target.strip():
        parser.error("Имя целевого пакета не может быть пустым")

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


def show_reverse(args):
    """Выводит обратные зависимости заданного пакета."""
    if args.test:
        graph = load_fixture(args.source)
        targets = [args.target or args.package]
    else:
        if not args.target:
            raise ValueError("Для npm необходимо указать --target")

        root, get_children_func = prepare_source(args)

        graph, _ = build_graph(
            root,
            get_children_func,
            args.depth,
            args.exclude,
        )

        targets = [
            node for node in graph
            if node.rsplit("@", 1)[0] == args.target
        ]

        if not targets:
            raise ValueError("Целевой пакет не найден в графе")

    result = set()

    for target in targets:
        result.update(
            find_reverse_dependencies(
                graph, target, args.depth, args.exclude
            )
        )

    result.difference_update(targets)

    print(f"Обратные зависимости {args.target or args.package}:")

    if result:
        for package in sorted(result):
            print(package)
    else:
        print("Не найдены")


def show_graph(root, graph, cycles):
    """Выводит граф зависимостей в терминал."""
    print(f"Граф зависимостей: {root}")

    for package, children in graph.items():
        text = ", ".join(children) if children else "нет"
        print(f"{package} -> {text}")

    if cycles:
        print("Найдены циклы:")

        for start, end in cycles:
            print(f"{start} -> {end}")



def main():
    """Анализирует и визуализирует зависимости."""
    args = parse_args()

    try:
        if args.reverse:
            show_reverse(args)
            return

        root, get_children_func = prepare_source(args)

        graph, cycles = build_graph(
            root,
            get_children_func,
            args.depth,
            args.exclude,
        )

        show_graph(root, graph, cycles)

        if args.visualize:
            text, source_path, html_path = visualize(
                graph, root
            )

            print("\nMermaid:")
            print(text)
            print("Файл Mermaid:", source_path)
            print("Изображение в браузере:", html_path)

    except (RegistryError, OSError, ValueError, RecursionError) as error:
        print("Ошибка:", error)


if __name__ == "__main__":
    main()