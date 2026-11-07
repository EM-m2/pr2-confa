
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



## Этап 5. Визуализация графа зависимостей

Реализована визуализация графа зависимостей
на языке диаграмм Mermaid.

Программа:
- строит граф зависимостей с помощью DFS;
- преобразует граф в текстовый формат Mermaid;
- сохраняет Mermaid-код в файл .mmd;
- создаёт HTML-страницу с SVG-диаграммой;
- открывает визуализацию в браузере.

Для визуализации используется флаг --visualize.

### Пример запуска

python -m src.main --package A --source fixtures/chain.json --test --version 1.0.0 --depth 3 --visualize

### Ручное тестирование

Пакет A:

python -m src.main --package A --source fixtures/chain.json --test --version 1.0.0 --depth 3 --visualize

Пакет B:

python -m src.main --package B --source fixtures/diamond.json --test --version 1.0.0 --depth 3 --visualize

Пакет C:

python -m src.main --package C --source fixtures/cycle.json --test --version 1.0.0 --depth 3 --visualize

### Файлы результата

Генерируемые файлы сохраняются в output/:
- *.mmd — текстовое описание Mermaid;
- *.html — визуализация графа.

Для отображения HTML необходим доступ к CDN Mermaid.

### Сравнение с npm

Для сравнения используется штатная команда npm ls --all.

Она выводит дерево установленных пакетов.

Python-программа получает зависимости самостоятельно,
через npm Registry. Команда npm ls используется
только при ручной проверке и сравнении результатов.

Возможные причины расхождений:
- разная глубина анализа;
- выбор версий зависимостей;
- особенности дедупликации npm;
- обработка дополнительных типов зависимостей.

Фактические результаты сравнения трёх пакетов
необходимо зафиксировать после выполнения проверок.
