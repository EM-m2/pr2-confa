import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class RegistryError(Exception):
    """Ошибка обращения к npm Registry."""


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
