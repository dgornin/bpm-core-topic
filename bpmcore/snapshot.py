"""Снимок платформы по умолчанию. ГОТОВЫЙ модуль.

Снимок описывает модели, которые уже есть на платформе (не создаются
конфигурацией), но на которые конфигурация может ссылаться: пользователи,
контакты, проекты. Формат — docs/spec/01-ir-format.md, § 3.

Содержимое совпадает с файлом spec/snapshot.json (это проверяет ``make lint``).
Другой снимок можно передать опцией ``--snapshot SNAP.json``.
"""

import copy

DEFAULT_SNAPSHOT = {
    "external_models": {
        "res.users": {
            "name": "Пользователь",
            "fields": {
                "name": {"type": "char"},
                "login": {"type": "char"},
                "partner_id": {"type": "many2one", "relation": "res.partner"},
            },
        },
        "res.partner": {
            "name": "Контакт",
            "fields": {
                "name": {"type": "char"},
                "email": {"type": "char"},
            },
        },
        "project.project": {
            "name": "Проект",
            "fields": {
                "name": {"type": "char"},
                "user_id": {"type": "many2one", "relation": "res.users"},
                "privacy_visibility": {"type": "selection"},
            },
        },
    }
}


def default_snapshot():
    """Свежая копия снимка по умолчанию (его можно менять, не боясь испортить оригинал)."""
    return copy.deepcopy(DEFAULT_SNAPSHOT)
