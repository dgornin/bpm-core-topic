"""Оркестратор проверки. ГОТОВЫЙ модуль (порядок — docs/spec/README.md).

1. Нормализация (S1): разбор документа, проверка ссылок, значения по
   умолчанию. Если есть ошибки или документ не удалось нормализовать —
   анализ не запускается, вердикт reject.
2. Анализ нормализованного IR:
   структура процессов (S3, S5) -> права и участники (A4–A7, A11, A14, A15)
   -> действия переходов и самоназначение (S2, A8) -> политика вуза (I), если передан
   непустой пакет.
   Анализ не останавливается на первой ошибке: собираются все находки.
3. Вердикт по находкам (findings.Findings.verdict).

Порядок находок в ответе на прохождение тестов не влияет.
"""

from . import access, effects, policy, structure
from .findings import Findings
from .normalize import normalize


def validate(raw, snapshot, pack=None):
    """Полная проверка сырого IR. Возвращает ``Findings`` (вердикт — ``findings.verdict()``).

    ``raw`` — то, что прочитано из JSON (может быть чем угодно, не только dict);
    ``snapshot`` — снимок платформы; ``pack`` — пакет политики или ``None``.
    """
    ir, findings = normalize(raw, snapshot)
    if ir is None or findings.has_errors():
        return findings

    analysis = Findings()
    cells = access.effective_cells(ir, snapshot)
    structure.check_structure(ir, analysis)
    access.check_access(ir, snapshot, cells, analysis)
    effects.check_effects(ir, snapshot, cells, analysis)
    if pack:  # пустой пакет {} ничего не требует (05, § 5.1, п. 7)
        policy.check_policy(pack, ir, snapshot, cells, analysis)

    findings.extend(analysis)
    return findings
