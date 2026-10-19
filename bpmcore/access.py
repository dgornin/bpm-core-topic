"""Роли, права и участники; матрица прав (A4–A7, A11, A14, A15). ЗАГЛУШКА — реализуйте.

Спецификация: docs/spec/04-roles-and-access.md.

Вход — нормализованный IR (после bpmcore.normalize): у прав (раздел access)
уже раскрыты узлы и поля по умолчанию.

Две части:

1. ``effective_cells`` — итоговые права: явные строки раздела access плюс
   неявные права на запись, которые дают входы переходов (inputs).
   Результат — и основа проверок ниже, и ответ команды ``matrix``
   (cli.merge_cells только объединяет дубли и сортирует).
2. ``check_access`` — проверки прав и участников процесса:
   A4.continuity, A5.requires, A5.requires_source (warning),
   A6.assignee_no_action (warning), A6.by_read, A6.no_trigger,
   A7.creator_read, A7.no_creator (warning), A7.required_not_creatable,
   A11.sod_unsatisfiable, A14.assignee_read, A15.related_read (warning).
Все коды этого модуля — уровня B (tests/levels.json).
"""


def effective_cells(ir, snapshot):
    """Итоговые права конфигурации — список ячеек.

    Ячейка — словарь::

        {"role": "author", "model": "topic", "op": "write", "node": "draft",
         "fields": ["x_description", "x_name"]}

    * ``node`` — ключ узла процесса или ``"*"`` (модель без процесса или op = create);
      строка access с несколькими узлами даёт по ячейке на узел;
    * ``fields`` — только для write и create;
    * одна и та же четвёрка (role, model, op, node) может повторяться —
      cli.merge_cells объединит поля и отсортирует результат.

    Сейчас заглушка возвращает пустой список: команда matrix выводит
    ``{"cells": []}``, а проверки прав ничего не видят.
    """
    # TODO(B): явные права из ir["access"] + неявные права на запись из inputs переходов.
    return []


def check_access(ir, snapshot, cells, findings):
    """Проверяет права и участников всех процессов; ``cells`` — результат ``effective_cells``.

    Сейчас заглушка ничего не проверяет.
    """
    # TODO(B): исполнители шагов и роли переходов видят документ (A14, A6.by_read);
    #          у исполнителя есть что нажать (A6.assignee_no_action);
    #          у перехода есть кто-то, кто его выполнит (A6.no_trigger);
    #          непрерывность доступа участника (A4.continuity);
    #          обязательные поля переходов заполнимы (A5.*);
    #          создание документа (A7.*); выполнимость SoD (A11);
    #          видимость связанных записей (A15).
    return None
