# Установка и запуск

Нужен только Python 3.10 или новее. Внешних зависимостей нет: и скелет
решения, и раннер тестов используют одну стандартную библиотеку.

## 1. Python 3.10+

Проверьте, что уже установлено:

```bash
python3 --version      # macOS / Linux
py --version           # Windows
```

Если версия ниже 3.10 или Python нет:

| ОС | Как поставить |
|---|---|
| macOS | `brew install python@3.12` или установщик с python.org |
| Ubuntu 22.04+ / Debian 12+ | уже есть 3.10 / 3.11: `sudo apt install python3 python3-venv make` |
| Fedora | `sudo dnf install python3 make` |
| Windows 10/11 | `winget install Python.Python.3.12` или установщик с python.org (отметьте «Add python.exe to PATH») |

По желанию — менеджеры версий:

- [uv](https://docs.astral.sh/uv/): `uv python install 3.12`, затем
  `uv venv` и `uv run python tests/run_acceptance.py --level C`;
- [pyenv](https://github.com/pyenv/pyenv) (Windows — pyenv-win):
  `pyenv install 3.12 && pyenv local 3.12` (файл `.python-version` уже в `.gitignore`).

## 2. Репозиторий

```bash
git clone <URL-вашего-форка> bpm-core
cd bpm-core
```

Виртуальное окружение **не обязательно** (ставить нечего). Если хотите
команду `bpmcore` вместо `python -m bpmcore`:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
bpmcore validate examples/demo_topic.json
```

## 3. Запуск тестов

С `make` (macOS, Linux, WSL, Git Bash с установленным make):

```bash
make test-c        # уровень C
make test-b        # уровни C и B
make test-a        # все уровни (то же, что make test-all и make test)
make lint          # компиляция пакета + сверка встроенного снимка со spec/snapshot.json
```

Без `make` (в том числе Windows):

```bash
python3 tests/run_acceptance.py --level C       # Windows: py tests\run_acceptance.py --level C
python3 tests/run_acceptance.py --level B
python3 tests/run_acceptance.py                 # все уровни
```

Полезные опции раннера:

| Опция | Что делает |
|---|---|
| `--level C\|B\|A` | уровень (включает все уровни ниже) |
| `-k строка` | только кейсы, в имени которых есть подстрока: `-k xor` |
| `-v` | печатать и прошедшие кейсы |
| `--list` | перечислить кейсы без запуска |

Запуск реализации руками на одном кейсе:

```bash
cd tests/cases/<имя-кейса>
python3 -m bpmcore validate ir.json          # из корня: python3 -m bpmcore validate tests/cases/<имя>/ir.json
cat expected.json                            # что ожидается
```

Чтобы `python -m bpmcore` работал из каталога кейса, либо выполните
`pip install -e .`, либо задайте `PYTHONPATH` = корень репозитория. Раннер
делает это сам.

### Что вы увидите на старте

Скелет запускается и ничего не находит: на любую конфигурацию отвечает
`accept`. Поэтому сразу проходят только «зелёные» кейсы (корректные
конфигурации) и кейсы на нечитаемый файл, а все кейсы с ошибками красные.
Так и задумано: ваша задача — сделать красные кейсы зелёными, не сломав
зелёные. В конце отчёта раннер печатает итог вида
`C: 35/85, B: 1/71, A: 0/68` (числа зависят от версии кейсов). Пока есть
непрошедшие кейсы, раннер завершается с кодом 1 и `make` пишет
`make: *** [test-c] Error 1` — это не сбой установки.

## 4. IDE

Корень репозитория — рабочий каталог. Конфигурации запуска:

- модуль `bpmcore`, параметры `validate examples/demo_topic.json`;
- скрипт `tests/run_acceptance.py`, параметры `--level C -k unreachable`.

Отладчик удобно запускать на одном кейсе через `-k`.

## Частые проблемы

| Симптом | Причина и решение |
|---|---|
| `python3: command not found` (Windows) | Используйте `py` или `python`: `make test-c PYTHON=py` |
| `make: command not found` | Запускайте раннер напрямую (см. выше). macOS: `xcode-select --install`; Ubuntu: `sudo apt install make`; Windows: `winget install GnuWin32.Make` или `choco install make` |
| `No module named bpmcore` при ручном запуске | Запускайте из корня репозитория или выполните `pip install -e .` |
| `SyntaxError` в скелете или раннере | Python старше 3.10 — обновите |
| Кракозябры вместо кириллицы в консоли Windows | `set PYTHONUTF8=1` (cmd) или `$env:PYTHONUTF8=1` (PowerShell); либо `chcp 65001` |
| `stdout — не JSON` в отчёте раннера | Реализация печатает в stdout что-то кроме ответа. Отладку пишите в stderr: `print(..., file=sys.stderr)` |
| `реализация не ответила за 20 с` | Почти всегда — бесконечный цикл при обходе графа с циклом (возвраты на доработку!). Храните множество посещённых узлов |
| Свой пример даёт код 4, хотя JSON верный | Файл сохранён в UTF-8 **с BOM** или в другой кодировке — пересохраните в UTF-8 без BOM |
| В GitHub Actions красный шаг `level B` / `level A`, но прогон зелёный | Так задумано: шаги B и A не роняют прогон, по ним видно, какой уровень пройден. Шаг `level C` обязателен |
| После обновления топика тесты «поехали» | Подтяните свежие `tests/` из основного репозитория (README, раздел «Для эксперта») и посмотрите `CHANGELOG.md` |
