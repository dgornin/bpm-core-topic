"""Нормализация IR: проверки схемы и ссылок (S1). ЗАГЛУШКА — реализуйте.

Спецификация:
  * docs/spec/01-ir-format.md      — формат IR; § 11 — порядок этапов нормализации,
    точки останова, значения по умолчанию, что получает анализ;
  * docs/spec/02-schema-checks.md  — коды S1.* с точными условиями и примерами;
  * docs/spec/05-conditions-effects-policy.md, § 5.1, 5.3, 5.4 — язык условий
    (S1.condition) и действия переходов (S2.effect, S2.effect_type): их проверяют
    модули conditions и effects, а вызывать их нужно отсюда, при разборе переходов
    и create_if моделей.

Что должна делать ``normalize``:
  1. Не менять вход: работать с глубокой копией.
  2. Проверить документ (коды S1.*, а на уровне A ещё S1.condition, S2.effect,
     S2.effect_type) и сложить находки в ``findings``.
  3. Заполнить значения по умолчанию, чтобы анализ (structure, access, ...)
     мог не проверять наличие ключей.
  4. Вернуть ``(ir, findings)``; если документ нельзя анализировать
     (есть ошибки) — ``(None, findings)``.

Подсказка по порядку работы (уровни — tests/levels.json):
  C: документ целиком (объект, версия, app, разделы), ключи и дубликаты,
     процессы, узлы, переходы, ссылки на роли, SoD;
  B: группы, модели и поля, роли и их привязки, ссылки на поля в переходах,
     раздел access (с раскрытием узлов и полей по умолчанию);
  A: условия (переходов и create_if) и действия переходов (effects).
"""

import copy

from .findings import Findings


def normalize(raw, snapshot):
    """Проверяет сырой IR и возвращает ``(ir, findings)``.

    ``raw`` — результат ``json.load`` (может быть любым JSON-значением);
    ``snapshot`` — снимок платформы (внешние модели), см. bpmcore/snapshot.py.

    Сейчас заглушка ничего не проверяет: возвращает копию входа без находок,
    поэтому корректные конфигурации проходят, а сломанные — тоже (и тесты
    на них красные).
    """
    findings = Findings()
    if not isinstance(raw, dict):
        # TODO(C): S1.not_object — сейчас такой вход молча пропускается.
        return None, findings
    ir = copy.deepcopy(raw)

    # TODO(C): S1.version, S1.app, S1.label, S1.section — документ целиком.
    # TODO(C): S1.key, S1.duplicate — ключи разделов.
    # TODO(C): процессы: S1.process_model, S1.node, S1.node_type, S1.assignee,
    #          S1.result, S1.sod; переходы: S1.flow, S1.flow_node, S1.flow_kind,
    #          S1.comment, S1.role_ref; значения по умолчанию узлов и переходов.
    # TODO(B): группы (S1.xmlid), модели и поля (S1.model_kind, S1.model_name,
    #          S1.field, S1.field_name, S1.field_type, S1.relation, S1.inverse,
    #          S1.ondelete, S1.selection, S1.default, S1.unique, S1.create_if),
    #          роли (S1.role_groups, S1.binding), поля переходов (S1.field_ref),
    #          права (S1.access) с раскрытием nodes и fields по умолчанию.
    # TODO(A): условия переходов и create_if -> conditions.lint_condition;
    #          действия переходов -> effects.lint_effect. Место находки передаётся
    #          словарём, например:
    #          lint_condition(flow["condition"], model_key, ir, snapshot, findings,
    #                         {"process": process_key, "flow": flow_key})
    #          lint_condition(model["create_if"], model_key, ir, snapshot, findings,
    #                         {"model": model_key})

    if findings.has_errors():
        return None, findings
    return ir, findings
