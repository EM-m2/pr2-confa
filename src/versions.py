import operator
import re


VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def version_tuple(text):
    """Преобразует версию в кортеж из трёх чисел"""
    match = VERSION_PATTERN.fullmatch(text)

    if match is None:
        return None

    return tuple(map(int, match.groups()))


def base_tuple(text):
    """Разбирает базовую версию диапазона"""
    parts = text.split(".")

    if not 1 <= len(parts) <= 3:
        raise ValueError(f"Неподдерживаемая версия: {text}")

    if not all(part.isdigit() for part in parts):
        raise ValueError(f"Неподдерживаемая версия: {text}")

    parts += ["0"] * (3 - len(parts))
    return tuple(map(int, parts))


def matches_token(version, token):
    """Проверяет одно условие версии"""
    if token in ("*", "x", "X"):
        return True

    if token.startswith("^"):
        base = base_tuple(token[1:])

        if base[0]:
            upper = (base[0] + 1, 0, 0)
        elif base[1]:
            upper = (0, base[1] + 1, 0)
        else:
            upper = (0, 0, base[2] + 1)

        return base <= version < upper

    if token.startswith("~"):
        text = token[1:]
        base = base_tuple(text)
        upper = (
            (base[0] + 1, 0, 0)
            if "." not in text
            else (base[0], base[1] + 1, 0)
        )
        return base <= version < upper

    comparisons = (
        (">=", operator.ge),
        ("<=", operator.le),
        (">", operator.gt),
        ("<", operator.lt),
    )

    for symbol, compare in comparisons:
        if token.startswith(symbol):
            base = base_tuple(token[len(symbol):])
            return compare(version, base)

    token = token.removeprefix("=")

    if token.endswith((".x", ".*")):
        prefix = tuple(map(int, token.split(".")[:-1]))
        return version[:len(prefix)] == prefix

    if re.fullmatch(r"\d+(?:\.\d+)?", token):
        prefix = tuple(map(int, token.split(".")))
        return version[:len(prefix)] == prefix

    return version == base_tuple(token)


def matches_requirement(version, requirement):
    """Проверяет диапазон с условиями AND и OR"""
    if not requirement.strip():
        raise ValueError("Пустое требование версии")

    return any(
        all(
            matches_token(version, token)
            for token in alternative.split()
        )
        for alternative in requirement.split("||")
    )


def choose_version(versions, requirement):
    """Выбирает наибольшую подходящую стабильную версию"""
    compatible = []

    for text in versions:
        version = version_tuple(text)

        if version is not None:
            if matches_requirement(version, requirement):
                compatible.append((version, text))

    if not compatible:
        raise ValueError(
            f"Не найдена версия для диапазона {requirement}"
        )

    return max(compatible)[1]
