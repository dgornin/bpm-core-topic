"""Интерфейс командной строки. ГОТОВЫЙ модуль (контракт — docs/contract.md).

    python -m bpmcore validate IR.json [--policy PACK.json] [--snapshot SNAP.json]
    python -m bpmcore matrix   IR.json [--snapshot SNAP.json]

Коды выхода: 0 accept, 1 reject, 3 unknown, 4 ошибка входа (файл не читается
или не JSON), 2 ошибка аргументов (её печатает argparse).

Менять этот модуль можно, но контракт должен остаться прежним: по нему
реализацию проверяют приёмочные тесты и эксперт.
"""

import argparse
import json
import sys

from . import access
from .normalize import normalize
from .snapshot import default_snapshot
from .validate import validate

EXIT_INPUT_ERROR = 4
WRITE_OPS = ("write", "create")


class InputError(Exception):
    """Входной файл не читается или не является JSON."""


def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except OSError as exc:
        raise InputError(f"не удалось прочитать {path}: {exc.strerror or exc}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InputError(f"{path}: некорректный JSON ({exc})") from exc


def load_snapshot(path):
    return load_json(path) if path else default_snapshot()


# команды


def run_validate(args):
    raw = load_json(args.ir)
    policy = load_json(args.policy) if args.policy else None
    snapshot = load_snapshot(args.snapshot)
    findings = validate(raw, snapshot, policy)
    return findings.to_json(), findings.exit_code()


def run_matrix(args):
    raw = load_json(args.ir)
    snapshot = load_snapshot(args.snapshot)
    ir, findings = normalize(raw, snapshot)
    if ir is None or findings.has_errors():
        return findings.to_json(), findings.exit_code()
    cells = access.effective_cells(ir, snapshot)
    return {"cells": merge_cells(cells)}, 0


def merge_cells(cells):
    """Приводит ячейки к виду из контракта: одна запись на (role, model, op, node).

    На входе — то, что вернула ``access.effective_cells``: словари с ключами
    role, model, op, node и (для write/create) fields; одна и та же четвёрка
    может встречаться несколько раз — тогда списки полей объединяются.
    На выходе — список, отсортированный по (role, model, op, node),
    поля отсортированы, ``fields`` есть только у write и create.
    """
    merged = {}
    for cell in cells:
        key = (cell["role"], cell["model"], cell["op"], cell.get("node") or "*")
        fields = merged.setdefault(key, set())
        if cell["op"] in WRITE_OPS:
            fields.update(cell.get("fields") or [])
    out = []
    for (role, model, op, node), fields in sorted(merged.items()):
        item = {"role": role, "model": model, "op": op, "node": node}
        if op in WRITE_OPS:
            item["fields"] = sorted(fields)
        out.append(item)
    return out


# разбор аргументов и вывод


def build_parser():
    parser = argparse.ArgumentParser(
        prog="bpmcore",
        description="Валидатор конфигураций процессов согласования (IR v0.1).",
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="КОМАНДА")

    p_validate = sub.add_parser("validate", help="проверить конфигурацию, выдать вердикт и находки")
    p_validate.add_argument("ir", help="файл конфигурации (IR, JSON)")
    p_validate.add_argument("--policy", help="пакет политики вуза (JSON)")
    p_validate.add_argument("--snapshot", help="снимок платформы (JSON); по умолчанию встроенный")
    p_validate.set_defaults(handler=run_validate)

    p_matrix = sub.add_parser("matrix", help="вывести итоговую матрицу прав")
    p_matrix.add_argument("ir", help="файл конфигурации (IR, JSON)")
    p_matrix.add_argument("--snapshot", help="снимок платформы (JSON); по умолчанию встроенный")
    p_matrix.set_defaults(handler=run_matrix)
    return parser


def emit(payload):
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    # Явно UTF-8: в консоли Windows кодировка по умолчанию может быть не UTF-8.
    sys.stdout.buffer.write(text.encode("utf-8"))
    sys.stdout.flush()


def main(argv=None):
    args = build_parser().parse_args(argv)  # при ошибке аргументов: SystemExit(2)
    try:
        payload, code = args.handler(args)
    except InputError as exc:
        payload, code = {"error": str(exc)}, EXIT_INPUT_ERROR
    emit(payload)
    return code

