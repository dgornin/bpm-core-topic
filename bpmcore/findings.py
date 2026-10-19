"""Находки валидатора и итоговый вердикт. ГОТОВЫЙ модуль.

Находка (finding) — одно замечание к конфигурации: код проверки
(например ``S3.unreachable``), уровень серьёзности, сообщение для аналитика
и место (``where``: процесс, узел, переход, роль, модель...).

Уровни серьёзности:

* ``error``   — конфигурацию нельзя вводить в действие;
* ``warning`` — подозрительно, но допустимо; на вердикт не влияет;
* ``unknown`` — проверка не смогла принять решение.

Вердикт (docs/contract.md, раздел «Вердикт»):

* есть хотя бы один ``error``  -> ``reject``;
* иначе есть хотя бы один ``unknown`` -> ``unknown``;
* иначе -> ``accept``.

Пример::

    findings = Findings()
    findings.error("S3.dead_end", "Из узла нет переходов.", process="topic", node="review")
    findings.warning("S3.return", "Возврат ведёт вперёд.", process="topic", flow="back")
    findings.verdict()  # "reject"
"""

from dataclasses import dataclass, field

ERROR = "error"
WARNING = "warning"
UNKNOWN = "unknown"
LEVELS = (ERROR, WARNING, UNKNOWN)

#: Код выхода CLI для каждого вердикта (docs/contract.md, «Коды выхода»).
EXIT_BY_VERDICT = {"accept": 0, "reject": 1, "unknown": 3}


@dataclass(frozen=True)
class Finding:
    """Одна находка. ``where`` — произвольные пары «что: ключ» для поиска места ошибки."""

    code: str
    level: str
    message: str
    where: dict = field(default_factory=dict)

    def to_json(self):
        return {
            "code": self.code,
            "level": self.level,
            "message": self.message,
            "where": dict(self.where),
        }


class Findings:
    """Накопитель находок в порядке добавления."""

    def __init__(self, items=None):
        self.items = list(items or [])

    def report(self, code, level, message, **where):
        if level not in LEVELS:
            raise ValueError(f"неизвестный уровень находки: {level!r}")
        self.items.append(Finding(code, level, message, where))

    def error(self, code, message, **where):
        self.report(code, ERROR, message, **where)

    def warning(self, code, message, **where):
        self.report(code, WARNING, message, **where)

    def unknown(self, code, message, **where):
        self.report(code, UNKNOWN, message, **where)

    def extend(self, other):
        self.items.extend(other.items)

    def has_errors(self):
        return any(item.level == ERROR for item in self.items)

    def codes(self):
        return {item.code for item in self.items}

    def verdict(self):
        """``reject``, если есть error; иначе ``unknown``, если есть unknown; иначе ``accept``."""
        levels = {item.level for item in self.items}
        for level, verdict in ((ERROR, "reject"), (UNKNOWN, "unknown")):
            if level in levels:
                return verdict
        return "accept"

    def exit_code(self):
        return EXIT_BY_VERDICT[self.verdict()]

    def to_json(self):
        """Тело ответа команды validate (и matrix, если IR не нормализуется)."""
        return {
            "verdict": self.verdict(),
            "findings": [item.to_json() for item in self.items],
        }

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)
