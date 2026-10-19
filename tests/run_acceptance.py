#!/usr/bin/env python3
"""Приёмочные тесты топика: запускает реализацию на кейсах tests/cases/*/.

    python tests/run_acceptance.py                # все уровни (= --level A)
    python tests/run_acceptance.py --level C      # только уровень C
    python tests/run_acceptance.py --level B      # уровни C и B
    python tests/run_acceptance.py -k unreachable # кейсы, в имени которых есть подстрока
    python tests/run_acceptance.py --list         # список кейсов без запуска

Реализация берётся из переменной окружения BPM_IMPL (командная строка,
разбирается как в shell), по умолчанию — ``python -m bpmcore`` тем же
интерпретатором, которым запущен раннер. Команда выполняется в каталоге
кейса: ``<BPM_IMPL> <command> <args...>`` (аргументы — из expected.json).

Правила сравнения (docs/contract.md):
  * код выхода — точное совпадение;
  * verdict — точное совпадение;
  * все ожидаемые коды находок должны быть среди выданных (лишние не штрафуются);
  * matrix — точное совпадение множества ячеек;
  * message и where не сравниваются.

Код выхода раннера: 0 — все выбранные кейсы прошли, 1 — иначе.
Файлы в tests/ не меняйте: эксперт проверяет решение на исходных тестах.
"""

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
REPO_DIR = TESTS_DIR.parent
CASES_DIR = TESTS_DIR / "cases"
LEVELS = ("C", "B", "A")
RANK = {level: rank for rank, level in enumerate(LEVELS)}
TIMEOUT = 20  # секунд на кейс
STDERR_TAIL = 12  # строк stderr в отчёте


# кейсы


class Case:
    def __init__(self, path):
        self.path = path
        self.name = path.name
        self.meta = _read_json(path / "case.json", default={})
        self.expected = _read_json(path / "expected.json")
        self.level = self.expected.get("level", "C")
        if self.level not in RANK:
            raise ValueError(f"{self.name}: неизвестный уровень {self.level!r} в expected.json")

    @property
    def title(self):
        return self.meta.get("title", "")

    @property
    def description(self):
        return self.meta.get("description", "")

    def argv(self):
        return [self.expected["command"], *self.expected.get("args", [])]


def _read_json(path, default=None):
    if default is not None and not path.exists():
        return default
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def discover(level="A", pattern=""):
    if not CASES_DIR.is_dir():
        return []
    cases = []
    for path in sorted(CASES_DIR.iterdir()):
        if not (path / "expected.json").is_file():
            continue
        case = Case(path)
        if RANK[case.level] <= RANK[level] and pattern in case.name:
            cases.append(case)
    return cases


# запуск реализации


def implementation_command():
    """Команда реализации из BPM_IMPL или ``<этот python> -m bpmcore``.

    Реализация запускается из каталога кейса, поэтому относительные пути
    в BPM_IMPL (``./target/bpmcore``, ``node dist/cli.js``) заранее
    превращаются в абсолютные — от каталога, из которого запущен раннер.
    """
    raw = os.environ.get("BPM_IMPL", "").strip()
    if not raw:
        return [sys.executable, "-m", "bpmcore"]
    if os.name != "nt":
        parts = shlex.split(raw)
    else:
        # Windows: обратные слэши в путях не экранируем, кавычки вокруг частей снимаем.
        parts = shlex.split(raw, posix=False)
        parts = [p[1:-1] if len(p) >= 2 and p[0] == p[-1] == '"' else p for p in parts]
    # имя модуля после -m (``python -m bpmcore``) — не путь, даже если есть такой каталог
    return [p if i and parts[i - 1] == "-m" else _absolute_if_path(p) for i, p in enumerate(parts)]


def _absolute_if_path(part):
    """Существующий файл (``main.py``) или явный путь к каталогу (``./build``) — в абсолютный."""
    if part.startswith("-") or os.path.isabs(part) or not os.path.exists(part):
        return part
    separators = [sep for sep in (os.sep, os.altsep, "/") if sep]
    if os.path.isdir(part) and not part.startswith(".") and not any(s in part for s in separators):
        return part  # голое имя каталога (например, пакета) — скорее имя, чем путь
    return os.path.abspath(part)


def implementation_env():
    """Окружение реализации: корень репозитория в PYTHONPATH (кейс запускается из своего каталога)."""
    env = dict(os.environ)
    paths = [str(REPO_DIR)]
    if env.get("PYTHONPATH"):
        paths.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(paths)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


class Run:
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def stderr_tail(self):
        lines = self.stderr.strip().splitlines()
        return "\n".join(lines[-STDERR_TAIL:])


def run_case(case):
    """Запускает реализацию на кейсе. Ошибки запуска превращаются в AssertionError с пояснением."""
    command = implementation_command() + case.argv()
    try:
        proc = subprocess.run(
            command,
            cwd=case.path,
            env=implementation_env(),
            capture_output=True,
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        raise AssertionError(f"- реализация не ответила за {TIMEOUT} с (зацикливание?)") from None
    except OSError as exc:
        raise AssertionError(
            f"- не удалось запустить реализацию {command[0]!r}: {exc}. Проверьте BPM_IMPL."
        ) from None
    return Run(
        proc.returncode,
        proc.stdout.decode("utf-8", errors="replace"),
        proc.stderr.decode("utf-8", errors="replace"),
    )


# сравнение


def parse_stdout(run):
    text = run.stdout.strip()
    if not text:
        raise AssertionError(_with_stderr(run, f"пустой stdout (код выхода {run.returncode})"))
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        preview = text if len(text) < 400 else text[:400] + " ..."
        raise AssertionError(
            _with_stderr(
                run,
                f"stdout — не JSON ({exc.msg}, строка {exc.lineno}); код выхода "
                f"{run.returncode}.\n  stdout: {preview}",
            )
        ) from None
    if not isinstance(payload, dict):
        raise AssertionError(f"stdout должен быть JSON-объектом, получено: {type(payload).__name__}")
    return payload


def _with_stderr(run, message):
    tail = run.stderr_tail()
    if tail:
        message += "\n  stderr (конец):\n    " + tail.replace("\n", "\n    ")
    return message


def cell_key(cell):
    if not isinstance(cell, dict):
        raise AssertionError(f"ячейка матрицы должна быть объектом, получено: {cell!r}")
    parts = [cell.get(name) for name in ("role", "model", "op", "node")]
    if not all(isinstance(part, str) for part in parts):
        raise AssertionError(f"role, model, op и node ячейки должны быть строками, получено: {cell!r}")
    fields = cell.get("fields")
    if fields is not None:
        if not isinstance(fields, list) or not all(isinstance(f, str) for f in fields):
            raise AssertionError(f"fields ячейки должен быть списком строк, получено: {cell!r}")
        fields = tuple(fields)
    return (*parts, fields)


def format_cell(key):
    role, model, op, node, fields = key
    text = f"{role} {op} {model} @ {node}"
    if fields is not None:
        text += f" fields={list(fields)}"
    return text


def compare(case, run):
    """Сравнивает ответ реализации с expected.json; при расхождении — AssertionError со списком."""
    exp = case.expected
    problems = []
    payload = None
    try:
        payload = parse_stdout(run)
    except AssertionError as exc:
        problems.append(str(exc))

    if run.returncode != exp["exit_code"]:
        problems.append(
            _with_stderr(run, f"код выхода: ожидался {exp['exit_code']}, получен {run.returncode}")
            if payload is not None
            else f"код выхода: ожидался {exp['exit_code']}, получен {run.returncode}"
        )

    if payload is not None:
        if "verdict" in exp:
            problems += compare_verdict(exp, payload)
        elif "cells" in exp:
            problems += compare_cells(exp, payload)
        elif not isinstance(payload.get("error"), str):
            problems.append('ожидался ответ об ошибке входа: {"error": "..."}')

    if problems:
        raise AssertionError("\n".join(f"- {p}" for p in problems))


def compare_verdict(exp, payload):
    problems = []
    verdict = payload.get("verdict")
    if verdict != exp["verdict"]:
        problems.append(f"verdict: ожидался {exp['verdict']!r}, получен {verdict!r}")
    findings = payload.get("findings")
    if not isinstance(findings, list):
        problems.append('в ответе нет списка "findings"')
        return problems
    well_formed = [f for f in findings if isinstance(f, dict) and isinstance(f.get("code"), str)]
    malformed = [f for f in findings if not (isinstance(f, dict) and isinstance(f.get("code"), str))]
    if malformed:
        problems.append(
            f'находка должна быть объектом со строковым "code", получено: {malformed[0]!r}'
            + (f" (и ещё {len(malformed) - 1})" if len(malformed) > 1 else "")
        )
    got = {f["code"] for f in well_formed}
    missing = sorted(set(exp.get("codes", [])) - got)
    if missing:
        problems.append(
            f"не найдены ожидаемые коды: {', '.join(missing)}"
            f" (ожидались: {', '.join(exp.get('codes', [])) or '—'};"
            f" получены: {', '.join(sorted(got)) or '—'})"
        )
    return problems


def compare_cells(exp, payload):
    cells = payload.get("cells")
    if not isinstance(cells, list):
        return ['в ответе нет списка "cells"']
    try:
        keys = [cell_key(c) for c in cells]
    except AssertionError as exc:
        return [str(exc)]
    got = set(keys)
    want = {cell_key(c) for c in exp["cells"]}
    problems = []
    quads = [key[:4] for key in keys]
    if len(set(quads)) != len(quads):
        problems.append("в cells есть повторяющиеся ячейки: (role, model, op, node) должна встречаться один раз")
    lacking = sorted(want - got, key=str)
    extra = sorted(got - want, key=str)
    if lacking:
        problems.append(
            "матрица: не хватает ячеек:\n    " + "\n    ".join(format_cell(k) for k in lacking)
        )
    if extra:
        problems.append(
            "матрица: лишние ячейки:\n    " + "\n    ".join(format_cell(k) for k in extra)
        )
    return problems


# unittest


class AcceptanceCase(unittest.TestCase):
    """Один кейс каталога tests/cases — один тест."""

    def __init__(self, case):
        super().__init__("runTest")
        self.case = case

    def id(self):
        return f"{self.case.level} {self.case.name}"

    def __str__(self):
        return self.id()

    def shortDescription(self):
        return self.case.title or None

    def runTest(self):
        compare(self.case, run_case(self.case))


class ReportResult(unittest.TestResult):
    def __init__(self, stream, verbose):
        super().__init__()
        self.stream = stream
        self.verbose = verbose
        self.passed = []
        self.failed = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed.append(test)
        if self.verbose:
            self.stream.write(f"ok    {test.id()}\n")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.failed.append((test, str(err[1])))
        self.stream.write(f"FAIL  {test.id()}\n")

    def addError(self, test, err):
        # ошибка самого раннера (битый expected.json и т. п.) — показываем как есть
        super().addError(test, err)
        self.failed.append((test, f"ошибка раннера: {err[0].__name__}: {err[1]}"))
        self.stream.write(f"ERROR {test.id()}\n")


def build_suite(cases):
    return unittest.TestSuite(AcceptanceCase(case) for case in cases)


def load_tests(loader, tests, pattern):
    """Для ``python -m unittest tests.run_acceptance``; уровень — из BPM_LEVEL (по умолчанию A)."""
    return build_suite(discover(os.environ.get("BPM_LEVEL", "A")))


# отчёт


def report(result, cases, level, out):
    if result.failed:
        out.write("\n" + "=" * 72 + "\nНЕ ПРОШЛИ\n" + "=" * 72 + "\n")
        for test, message in result.failed:
            case = test.case
            out.write(f"\n[{case.level}] {case.name}")
            if case.title:
                out.write(f" — {case.title}")
            out.write("\n")
            if case.description:
                out.write(f"  Суть: {case.description}\n")
            out.write(f"  Команда: (cd tests/cases/{case.name} && <impl> {' '.join(case.argv())})\n")
            out.write("  " + message.replace("\n", "\n  ") + "\n")

    failed_names = {test.case.name for test, _ in result.failed}
    parts = []
    for lvl in LEVELS[: RANK[level] + 1]:
        of_level = [c for c in cases if c.level == lvl]
        ok = sum(1 for c in of_level if c.name not in failed_names)
        parts.append(f"{lvl}: {ok}/{len(of_level)}")
    total_ok = len(cases) - len(failed_names)
    out.write("\n" + ", ".join(parts) + f"  (всего {total_ok}/{len(cases)})\n")
    out.write("ВСЕ КЕЙСЫ ПРОШЛИ\n" if not failed_names else "ЕСТЬ НЕПРОШЕДШИЕ КЕЙСЫ\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Приёмочные тесты топика bpm-core.")
    parser.add_argument(
        "--level",
        choices=LEVELS,
        default="A",
        type=str.upper,
        help="уровень: C — только C; B — C и B; A — все (по умолчанию)",
    )
    parser.add_argument("-k", dest="pattern", default="", help="только кейсы с подстрокой в имени")
    parser.add_argument("-v", "--verbose", action="store_true", help="печатать и прошедшие кейсы")
    parser.add_argument("--list", action="store_true", help="только перечислить кейсы")
    args = parser.parse_args(argv)

    out = sys.stdout
    if hasattr(out, "reconfigure"):
        out.reconfigure(encoding="utf-8", errors="replace")

    try:
        cases = discover(args.level, args.pattern)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        out.write(f"Не удалось прочитать кейсы: {exc}\n")
        return 1
    if not cases:
        out.write("Не найдено ни одного кейса (tests/cases/*/expected.json).\n")
        return 1
    if args.list:
        for case in cases:
            out.write(f"{case.level}  {case.name}  {case.title}\n")
        return 0

    command = implementation_command()
    if not command or shutil.which(command[0]) is None:
        out.write(
            f"Не найдена программа реализации {command[0] if command else ''!r}. "
            "Проверьте переменную BPM_IMPL (docs/contract.md).\n"
        )
        return 1
    out.write(f"Реализация: {' '.join(command)}\n")
    out.write(f"Кейсов: {len(cases)} (уровень {args.level}" + ("" if args.level == "C" else " и ниже") + ")\n\n")
    result = ReportResult(out, args.verbose)
    build_suite(cases).run(result)
    report(result, cases, args.level, out)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
