from src.graph import build_graph


def find_reverse_dependencies(graph, target, max_depth, exclude):
    """Находит пакеты, зависящие от заданного пакета."""
    if target not in graph:
        raise ValueError(f"Пакет {target} отсутствует в графе")

    name = target.rsplit("@", 1)[0]

    if exclude and exclude in name:
        raise ValueError("Искомый пакет исключён фильтром")

    incoming = {node: [] for node in graph}

    for parent, children in graph.items():
        for child in children:
            incoming.setdefault(child, []).append(parent)

    reversed_graph, _ = build_graph(
        target,
        incoming.__getitem__,
        max_depth,
        exclude,
    )

    return [
        node for node in reversed_graph
        if node != target
    ]
