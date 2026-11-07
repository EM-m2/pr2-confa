import re
import webbrowser
from html import escape
from pathlib import Path


MERMAID_JS = (
    "https://cdn.jsdelivr.net/npm/mermaid@11/"
    "dist/mermaid.esm.min.mjs"
)


def to_mermaid(graph):
    """Преобразует граф зависимостей в синтаксис Mermaid."""
    identifiers = {
        name: f"n{index}"
        for index, name in enumerate(graph)
    }

    lines = ["flowchart TD"]

    for name, identifier in identifiers.items():
        label = name.replace("&", "#amp;")
        label = label.replace('"', "#quot;")
        lines.append(f'    {identifier}["{label}"]')

    for parent, children in graph.items():
        for child in children:
            lines.append(
                f"    {identifiers[parent]} --> {identifiers[child]}"
            )

    return "\n".join(lines) + "\n"


def visualize(graph, root):
    """Сохраняет Mermaid и открывает изображение в браузере."""
    mermaid_text = to_mermaid(graph)
    output = Path("output")
    output.mkdir(exist_ok=True)

    filename = re.sub(r"[^A-Za-z0-9_-]", "_", root)
    source_path = output / f"{filename}.mmd"
    html_path = output / f"{filename}.html"

    source_path.write_text(mermaid_text, encoding="utf-8")

    html_page = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Граф зависимостей {escape(root)}</title>
</head>
<body>
<h2>Граф зависимостей {escape(root)}</h2>
<pre class="mermaid">{escape(mermaid_text)}</pre>
<script type="module">
import mermaid from "{MERMAID_JS}";
mermaid.initialize({{
    startOnLoad: true,
    securityLevel: "strict"
}});
</script>
</body>
</html>
"""

    html_path.write_text(html_page, encoding="utf-8")
    webbrowser.open(html_path.resolve().as_uri())

    return mermaid_text, source_path, html_path
