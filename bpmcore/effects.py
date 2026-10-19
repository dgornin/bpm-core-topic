"""Действия переходов (effects) и самоназначение (S2, A8). ЗАГЛУШКА — реализуйте.

Спецификация: docs/spec/05-conditions-effects-policy.md, § 5.4 (действия),
§ 5.5 (связи процессов через fire), § 5.6 (самоназначение).

Две части:

1. ``lint_effect`` — синтаксис одного действия перехода (fire, set, create,
   subscribe) и типы значений: S2.effect, S2.effect_type. Вызывается из
   normalize при разборе перехода, как и conditions.lint_condition.
2. ``check_effects`` — анализ нормализованного IR:
   S2.fire_not_system (warning), S2.system_unused (warning) — связи между
   процессами через fire; A8.self_assign, A8.effect_self_assign,
   A8.effect_launder (warning), A8.effect_claim (warning) — может ли
   участник сам (правом на запись или через действие перехода) сделать себя
   держателем роли.
Все коды этого модуля — уровня A (tests/levels.json).
"""


def lint_effect(effect, model, ir, snapshot, findings, where):
    """Проверяет одно действие перехода процесса над моделью с ключом ``model``.

    ``where`` — словарь с местом действия для находок: ``{"process": ..., "flow": ...}``
    (05, § 5.4.5); передавайте его как ``findings.error("S2.effect", "...", **where)``.
    Почему словарь, а не ``**where`` — см. conditions.lint_condition.

    Сейчас заглушка ничего не проверяет.
    """
    # TODO(A): S2.effect — вид действия, обязательные части, цели и пути;
    #          S2.effect_type — значение подходит полю (§ 5.4.4).
    return None


def check_effects(ir, snapshot, cells, findings):
    """Анализ действий и самоназначения; ``cells`` — результат access.effective_cells.

    Сейчас заглушка ничего не проверяет.
    """
    # TODO(A): S2.fire_not_system, S2.system_unused (§ 5.5);
    #          A8.self_assign — роль может записать поле, через которое она определяется;
    #          A8.effect_* — то же самое через действия переходов (§ 5.6).
    return None
