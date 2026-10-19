"""Политика вуза — «policy as code» (I.*). ЗАГЛУШКА — реализуйте.

Спецификация: docs/spec/05-conditions-effects-policy.md, § 5.7 (формат пакета и алгоритм).
Пример пакета: examples/policies/demo_topic.json.

Пакет политики пишет не автор конфигурации, а вуз: обязательные ступени
согласования, потолки и полы прав ролей, обязательное разделение обязанностей,
роли, которые должны определяться через запись. Проверка сравнивает с ним
нормализованный IR и итоговые права.

Коды (уровень A): I.must_pass, I.skip_step, I.excess, I.floor,
I.sod_missing, I.bound, I.unbound.
"""


def check_policy(pack, ir, snapshot, cells, findings):
    """Сверяет конфигурацию с пакетом политики ``pack``; ``cells`` — access.effective_cells.

    Вызывается, только если передан ``--policy`` с непустым пакетом. Сейчас заглушка
    ничего не проверяет.
    """
    # TODO(A): must_pass (I.must_pass, I.skip_step), ceilings (I.excess),
    #          floors (I.floor), separate (I.sod_missing), bound_roles (I.bound, I.unbound).
    return None
