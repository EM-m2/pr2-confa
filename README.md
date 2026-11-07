
# Визуализатор зависимостей npm

Практическая работа №2. Вариант 14.

## Этап 1. Конфигурация

Реализован CLI-интерфейс для ввода параметров анализа.
Добавлена проверка имени пакета, версии, адреса репозитория,
тестового режима, глубины поиска и фильтра пакетов.

## Запуск

./run.sh --package A --source fixtures/chain.json --test \
  --version 1.0.0 --depth 3

## Тестирование

python3 -m unittest discover -s tests -v



## Этап 2. Сбор данных

Реализовано получение метаданных npm-пакетов через HTTP.
Программа извлекает прямые зависимости указанной версии
из JSON-ответа npm Registry. Добавлена обработка ошибок
подключения и некорректных ответов.



## Этап 3. Построение графа зависимостей

Реализован рекурсивный алгоритм DFS для построения
графа транзитивных зависимостей npm-пакетов.

Поддерживаются:
- ограничение глубины обхода;
- фильтрация пакетов по подстроке;
- обнаружение циклических зависимостей;
- работа с реальным npm Registry;
- тестовый режим на основе JSON-файлов.

Тестовые графы содержат пакеты с именами из
заглавных латинских букв.

### Проверка обычного графа

python -m src.main --package A --source fixtures/diamond.json --test --version 1.0.0 --depth 3

### Проверка ограничения глубины

python -m src.main --package A --source fixtures/diamond.json --test --version 1.0.0 --depth 1

### Проверка циклических зависимостей

python -m src.main --package A --source fixtures/cycle.json --test --version 1.0.0 --depth 5

### Проверка фильтрации

python -m src.main --package A --source fixtures/diamond.json --test --version 1.0.0 --depth 3 --exclude C


## Этап 4. Обратные зависимости

Реализован режим поиска обратных зависимостей.

Обратные зависимости — пакеты, которые прямо или
транзитивно зависят от заданного пакета.

Для поиска направления связей графа инвертируются,
после чего используется рекурсивный DFS из этапа 3.

### Запуск

Для включения режима используется параметр --reverse.

Пример:

python -m src.main --package D --source fixtures/chain.json --test --version 1.0.0 --depth 3 --reverse

### Ручная проверка

Обычный граф:

python -m src.main --package D --source fixtures/diamond.json --test --version 1.0.0 --depth 3 --reverse

Ограничение глубины:

python -m src.main --package D --source fixtures/chain.json --test --version 1.0.0 --depth 1 --reverse

Фильтрация:

python -m src.main --package D --source fixtures/diamond.json --test --version 1.0.0 --depth 3 --exclude B --reverse

Циклические зависимости:

python -m src.main --package A --source fixtures/cycle.json --test --version 1.0.0 --depth 3 --reverse

### Реальный npm Registry

В обычном режиме параметр --package задаёт начальный
пакет для построения графа, а --target — пакет,
обратные зависимости которого нужно найти.

Поиск обратных зависимостей ограничивается
исследованным графом, а не всем реестром npm.
