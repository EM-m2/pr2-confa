import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from functools import lru_cache
from src.versions import choose_version


class RegistryError(Exception):
    """Ошибка обращения к npm Registry."""

@lru_cache(maxsize=256)
def fetch_json(source, package, version=None):
    """Получает метаданные пакета из npm Registry."""
    package_path = quote(package, safe="")
    url = f"{source.rstrip('/')}/{package_path}"

    if version is not None:
        url += "/" + quote(version, safe="")

    request = Request(
        url,
        headers={"Accept": "application/json"}
    )

    try:
        with urlopen(request, timeout=15) as response:
            return json.load(response)
    except HTTPError as error:
        raise RegistryError(
            f"HTTP-ошибка: {error.code}"
        ) from error
    except (URLError, TimeoutError) as error:
        raise RegistryError(
            f"Ошибка подключения: {error}"
        ) from error
    except (ValueError, UnicodeError) as error:
        raise RegistryError(
            "Некорректный ответ сервера"
        ) from error


def get_dependencies(source, package, version):
    """Получает прямые зависимости заданной версии."""
    metadata = fetch_json(source, package, version)

    if not isinstance(metadata, dict):
        raise RegistryError("Неверный формат метаданных")

    dependencies = metadata.get("dependencies", {})

    if not isinstance(dependencies, dict):
        raise RegistryError("Неверный формат dependencies")

    return dependencies


def resolve_version(source, package, requirement):
    """Определяет версию зависимости по диапазону."""
    metadata = fetch_json(source, package)

    if not isinstance(metadata, dict):
        raise RegistryError("Неверные метаданные пакета")

    versions = metadata.get("versions", {})
    tags = metadata.get("dist-tags", {})

    if not isinstance(versions, dict):
        raise RegistryError("Неверный список версий")

    if not isinstance(tags, dict):
        raise RegistryError("Неверные теги версий")

    if requirement in tags:
        return tags[requirement]

    try:
        return choose_version(versions, requirement)
    except ValueError as error:
        raise RegistryError(
            f"Пакет {package}: {error}"
        ) from error


def get_children(source, package_id):
    """Возвращает прямые зависимости с точными версиями."""
    package, version = package_id.rsplit("@", 1)

    dependencies = get_dependencies(
        source,
        package,
        version,
    )

    children = []

    for name, requirement in dependencies.items():
        child_version = resolve_version(
            source,
            name,
            requirement,
        )
        children.append(f"{name}@{child_version}")

    return children
