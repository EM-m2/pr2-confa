import json
import re


def load_fixture(path):
    """Загружает и проверяет тестовый граф"""
    with open(path, encoding="utf-8") as file:
        graph = json.load(file)

    if not isinstance(graph, dict) or not graph:
        raise ValueError("Тестовый граф должен быть объектом JSON")

    for name, children in graph.items():
        if re.fullmatch(r"[A-Z]+", name) is None:
            raise ValueError("Имена пакетов: только A-Z")

        if not isinstance(children, list):
            raise ValueError("Зависимости должны быть списком")

        for child in children:
            if not isinstance(child, str) or child not in graph:
                raise ValueError(f"Неизвестная зависимость: {child}")

    return graph


def build_graph(root, get_children, max_depth, exclude):
    """Строит граф с помощью рекурсивного DFS"""
    graph = {}
    active = set()
    best_depth = {}
    cycles = set()

    def dfs(node, depth):
        """Рекурсивно обходит зависимости узла"""
        graph.setdefault(node, [])

        if depth >= max_depth:
            return

        if depth >= best_depth.get(node, max_depth + 1):
            return

        best_depth[node] = depth
        active.add(node)

        try:
            for child in get_children(node):
                name = child.rsplit("@", 1)[0]

                if exclude and exclude in name:
                    continue

                if child not in graph[node]:
                    graph[node].append(child)

                graph.setdefault(child, [])

                if child in active:
                    cycles.add((node, child))
                else:
                    dfs(child, depth + 1)
        finally:
            active.remove(node)

    dfs(root, 0)
    return graph, sorted(cycles)
