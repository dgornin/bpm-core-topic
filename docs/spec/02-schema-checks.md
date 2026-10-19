# 02. Проверки схемы IR: коды `S1.*`

Нормализация IR ([01-ir-format.md](01-ir-format.md)) выдаёт находки класса `S1`
(«схема и ссылки»). Здесь перечислены все коды `S1.*`, кроме `S1.condition`
(проверка условий описана в [05-conditions-effects-policy.md](05-conditions-effects-policy.md)).

Для каждого кода указано:

- **уровень топика** (C или B) — из [tests/levels.json](../../tests/levels.json);
- **уровень находки** — у всех кодов `S1.*` это `error`: любая такая находка
  даёт вердикт `reject` и код выхода 1;
- **этап** нормализации (таблица этапов — [01-ir-format.md § 11.1](01-ir-format.md#111-порядок-этапов-и-точки-останова));
- точное **условие** срабатывания и что происходит с проверкой дальше;
- ключи **`where`**;
- мини-пример фрагмента IR;
- **кейсы** в `tests/cases`, которые проверяют код.

## Общие соглашения

- **Сколько находок.** Одна находка на каждое нарушение: две неизвестные роли
  в `by` — две находки `S1.role_ref`. Тесты сравнивают только **множество**
  кодов, поэтому число повторов на тесты не влияет.
- **`where`** — объект с ключами из списка у кода; значения берутся из IR как
  есть (ключ модели, роли, процесса, узла, перехода; имя поля). `cell` —
  индекс ячейки в исходном списке `access`, с нуля. Если у кода указано
  «`where` пуст», выдаётся `{}`. `where` и `message` тестами не сравниваются,
  но нужны человеку, который читает отчёт.
- **`message`** — свободный текст для аналитика (рекомендуется по-русски:
  что не так и как исправить).
- **Порядок находок** в выводе не важен; удобно выдавать их в порядке этапов.
- Слова «ключ», «подпись», «имя поля», «xmlid», «путь» используются в смысле
  [01-ir-format.md § 2](01-ir-format.md#2-лексика-ключи-подписи-имена) и
  [§ 8.2](01-ir-format.md#82-пути-по-полям). «Известная роль» — ключ элемента
  `roles`, «известная модель» — ключ элемента `models`, «известный узел /
  переход» — ключ узла / перехода этого же процесса, прошедший проверку
  `S1.node` / `S1.flow` (это важно для `S1.flow_node` и `S1.sod`).
  **Исключение** — этапы 9–11 (`live_nodes`, `nodes` строк прав), условия и
  действия переходов: там «узлы процесса модели» — значения `key` всех узлов
  процесса как записаны, включая узлы с находкой `S1.node` (раздел 01,
  § 11.1). Разница видна только в лишних кодах: `S1.node` и так даёт `reject`.

## Сводная таблица

| Код | Уровень | Этап | `where` | Кейсы |
|---|---|---|---|---|
| `S1.not_object` | C | 0 | — | `ir-not-object` |
| `S1.version` | C | 1 | — | `ir-version-number` |
| `S1.app` | C | 2 | — | `ir-app-key-invalid`, `ir-app-key-too-long` |
| `S1.label` | C | 2a, 5–8 | зависит от места | `ir-label-app-missing`, `ir-label-app-too-long`, `ir-label-node-missing`, `ir-label-flow-control-char` |
| `S1.section` | C | 3 | — | `ir-section-not-list` |
| `S1.key` | C | 4 | — | `ir-key-invalid`, `ir-key-item-not-object` |
| `S1.duplicate` | C | 4, 6 | — / `model` | `ir-duplicate-role`, `ir-duplicate-field` |
| `S1.xmlid` | B | 5 | `group` | `ir-xmlid-invalid`, `ir-xmlid-implied-invalid` |
| `S1.model_name` | B | 6 | `model` | `ir-model-name-no-prefix`, `ir-model-name-too-long`, `ir-model-name-default-too-long` |
| `S1.model_kind` | B | 6 | `model` | `ir-model-kind-unknown` |
| `S1.field` | B | 6 | `model` | `ir-field-not-object` |
| `S1.field_name` | B | 6 | `model` (+ `field`) | `ir-field-name-no-prefix`, `ir-field-name-reserved`, `ir-field-name-too-long` |
| `S1.field_type` | B | 6 | `model`, `field` | `ir-field-type-unknown` |
| `S1.default` | B | 6 | `model`, `field` | `ir-default-integer-string`, `ir-default-selection-unknown`, `ir-default-on-text` |
| `S1.selection` | B | 6 | `model`, `field` | `ir-selection-flat`, `ir-selection-missing` |
| `S1.relation` | B | 6 | `model`, `field` | `ir-relation-unknown`, `ir-relation-one2many-external` |
| `S1.inverse` | B | 6 | `model`, `field` | `ir-inverse-missing`, `ir-inverse-not-many2one` |
| `S1.ondelete` | B | 6 | `model`, `field` | `ir-ondelete-unknown` |
| `S1.unique` | B | 6, 10 | `model` | `ir-unique-unknown-field`, `ir-unique-text-field`, `ir-unique-live-nodes-unknown` |
| `S1.role_groups` | B | 7 | `role` | `ir-role-groups-unknown`, `ir-role-groups-missing` |
| `S1.binding` | B | 7 | `role` (+ `model`) | `ir-binding-write-uid`, `ir-binding-not-user`, `ir-binding-unknown-model`, `ir-binding-path-unknown-field` |
| `S1.process_model` | C | 8 | `process` | `ir-process-model-reference`, `ir-process-model-twice` |
| `S1.node` | C | 8 | `process` | `ir-node-duplicate`, `ir-node-key-invalid`, `ir-node-key-too-long` |
| `S1.node_type` | C | 8 | `process`, `node` | `ir-node-type-unknown` |
| `S1.assignee` | C | 8 | `process`, `node` | `ir-assignee-on-end` |
| `S1.result` | C | 8 | `process`, `node` | `ir-result-unknown` |
| `S1.role_ref` | C | 8 | `process`, `node` / `flow` | `ir-role-ref-assignee`, `ir-role-ref-by`, `ir-role-ref-release` |
| `S1.flow` | C | 8 | `process` (+ `flow`) | `ir-flow-duplicate-key`, `ir-flow-sequence-not-int` |
| `S1.flow_node` | C | 8 | `process`, `flow` | `ir-flow-node-unknown` |
| `S1.flow_kind` | C | 8 | `process`, `flow` | `ir-flow-kind-unknown` |
| `S1.comment` | C | 8 | `process`, `flow` | `ir-comment-unknown` |
| `S1.field_ref` | B | 8 | `process`, `flow` | `ir-field-ref-requires-unknown`, `ir-field-ref-requires-magic`, `ir-field-ref-inputs-list` |
| `S1.sod` | C | 8 | `process` | `ir-sod-unknown-flow` |
| `S1.create_if` | B | 9 | `model` | `ir-create-if-no-process` |
| `S1.access` | B | 11 | `cell` (+ `role`) / `role`, `model` | `ir-access-*` (9 кейсов), `fix-access-nodes-node-objects` |

«Зелёные» кейсы этой части (ни одной находки, `accept`, код 0):
[`ir-green-demo`](../../tests/cases/ir-green-demo/),
[`ir-green-demo-policy`](../../tests/cases/ir-green-demo-policy/),
[`ir-green-minimal`](../../tests/cases/ir-green-minimal/),
[`ir-green-features`](../../tests/cases/ir-green-features/),
[`ir-green-limits`](../../tests/cases/ir-green-limits/).
Ошибки ввода (код 4, не находки):
[`ir-input-not-json`](../../tests/cases/ir-input-not-json/),
[`ir-input-empty`](../../tests/cases/ir-input-empty/).

---

## Документ целиком (этапы 0–3)

### `S1.not_object` — IR не объект

**Уровень:** C · **находка:** error · **этап:** 0 · **дальше:** стоп

**Условие.** Корень JSON — не объект (массив, строка, число, `true`/`false`,
`null`). Если файл вообще не JSON, это не находка, а ошибка ввода с кодом 4.

**where:** пуст.

**Пример.** `[{"ir_version": "0.1", "app": {...}}]` — конфигурация обёрнута в массив.

**Кейсы:** [`ir-not-object`](../../tests/cases/ir-not-object/).

### `S1.version` — неподдерживаемая версия

**Уровень:** C · **находка:** error · **этап:** 1 · **дальше:** стоп

**Условие.** Ключа `ir_version` нет, или его значение не равно **строке**
`"0.1"`. Число `0.1`, строки `"0.10"`, `"0.1 "`, `"1"` — ошибка.

**where:** пуст.

**Пример.** `{"ir_version": 0.1, "app": {...}}`

**Кейсы:** [`ir-version-number`](../../tests/cases/ir-version-number/).

### `S1.app` — нет корректного приложения

**Уровень:** C · **находка:** error · **этап:** 2 · **дальше:** стоп
(название приложения уже не проверяется)

**Условие.** `app` отсутствует или не объект, либо `app.key` отсутствует или не
является ключом (`[a-z][a-z0-9_]{0,30}`).

**where:** пуст.

**Пример.** `"app": {"key": "Demo", "name": "Демо"}`; ключ из 32 символов.

**Кейсы:** [`ir-app-key-invalid`](../../tests/cases/ir-app-key-invalid/),
[`ir-app-key-too-long`](../../tests/cases/ir-app-key-too-long/).

### `S1.section` — раздел не список

**Уровень:** C · **находка:** error · **этап:** 3 · **дальше:** стоп

**Условие.** Разделы проверяются по порядку `groups`, `models`, `roles`,
`processes`, `access`. Отсутствующий раздел становится `[]`. Присутствующий
раздел, значение которого не JSON-массив (объект, строка, число, `null`), даёт
одну находку, и нормализация сразу прекращается — следующие разделы не
проверяются. Находка `S1.label` о названии приложения (этап 2a), если была,
остаётся в выводе.

**where:** пуст.

**Пример.** `"models": {"topic": {"key": "topic", "name": "Тема"}}`

**Кейсы:** [`ir-section-not-list`](../../tests/cases/ir-section-not-list/).

### `S1.label` — неверная подпись

**Уровень:** C · **находка:** error · **этапы:** 2a, 5, 6, 7, 8 · **дальше:**
проверка продолжается

**Условие.** Значение не является подписью: не строка, пустая строка, длиннее
128 символов (кодовых точек) или содержит символ с кодом меньше 32 (табуляция,
перевод строки и т. п.). Проверяемые места:

| Место | Когда проверяется | where |
|---|---|---|
| `app.name` | всегда (если `app.key` корректен) | `app` (= `app.key`) |
| `groups[].name` | у каждой группы-объекта | `group` |
| `models[].name` | у каждой модели-объекта | `model` |
| `fields[].label` | у поля-объекта с корректным именем (§ `S1.field_name`) | `model`, `field` |
| `roles[].name` | у каждой роли | `role` |
| `processes[].name` | у процесса с известной моделью (иначе процесс не проверяется, см. `S1.process_model`) | `process` |
| `nodes[].name` | у узла, прошедшего `S1.node` | `process`, `node` |
| `flows[].label` | у перехода, прошедшего `S1.flow`; если `label` нет, подписью служит `key` и ошибки быть не может | `process`, `flow` |

Подпись варианта `selection` и значение по умолчанию поля `char` проверяются
теми же правилами, но дают коды `S1.selection` и `S1.default`.

**Пример.**
```json
{"key": "approve", "label": "Утвердить\tтему", "from": "review", "to": "published", "by": ["head"]}
```

**Кейсы:** [`ir-label-app-missing`](../../tests/cases/ir-label-app-missing/),
[`ir-label-app-too-long`](../../tests/cases/ir-label-app-too-long/) (129 символов),
[`ir-label-node-missing`](../../tests/cases/ir-label-node-missing/),
[`ir-label-flow-control-char`](../../tests/cases/ir-label-flow-control-char/);
граница 128 символов кириллицей допустима —
[`ir-green-limits`](../../tests/cases/ir-green-limits/).

---

## Ключи разделов (этап 4)

### `S1.key` — неверный ключ элемента

**Уровень:** C · **находка:** error · **этап:** 4 · **дальше:** продолжить

**Условие.** Для каждого элемента разделов `groups`, `models`, `roles`,
`processes` (раздел `access` ключей не имеет): элемент не объект, или у него нет
`key`, или `key` не строка, или строка не является ключом. Такой элемент не
участвует в проверке повторов. Группы и модели-объекты с неверным ключом всё
равно проходят этапы 5–6 (поэтому, например, модель с ключом `"Note"` получит
ещё и `S1.model_name`: имя по умолчанию `x_demo_Note` неверно; модель без ключа —
тоже). Из-за точки останова A роли, процессы и права в этом случае уже не
проверяются.

**where:** пуст (раздел и значение ключа — в `message`).

**Пример.** `{"key": "Head", "name": "Заведующий", "groups": ["head"]}`;
`"roles": [..., "reviewer"]`.

**Кейсы:** [`ir-key-invalid`](../../tests/cases/ir-key-invalid/),
[`ir-key-item-not-object`](../../tests/cases/ir-key-item-not-object/).

### `S1.duplicate` — повтор ключа или имени поля

**Уровень:** C · **находка:** error · **этапы:** 4 и 6 · **дальше:** продолжить

**Условие.** Два случая:

1. (этап 4) В одном разделе `groups` / `models` / `roles` / `processes` два
   элемента с одинаковым корректным ключом. Находка выдаётся на каждый повтор
   (второй, третий, …). Одинаковые ключи в **разных** разделах допустимы.
   `where` пуст.
2. (этап 6) В одной модели два поля с одинаковым корректным именем (в том числе
   явное `x_name`, описанное дважды). Повтор при этом проверяется дальше как
   обычное поле. `where`: `model`.

Повторы ключей узлов и переходов — это `S1.node` и `S1.flow`, а не
`S1.duplicate`.

**Пример.**
```json
"roles": [
  {"key": "head", "name": "Заведующий", "groups": ["head"]},
  {"key": "head", "name": "Заведующий кафедрой", "groups": ["head"]}
]
```

**Кейсы:** [`ir-duplicate-role`](../../tests/cases/ir-duplicate-role/),
[`ir-duplicate-field`](../../tests/cases/ir-duplicate-field/).

---

## Группы (этап 5)

### `S1.xmlid` — неверный xmlid группы

**Уровень:** B · **находка:** error · **этап:** 5 · **дальше:** продолжить

**Условие.** У группы-объекта:

- `xmlid` задан (не отсутствует и не `null`) и не является xmlid
  (`[a-z0-9_]+\.[a-z0-9_]+`, строка) — одна находка;
- каждый элемент `implied` (после подстановки значения по умолчанию), который не
  является xmlid, — по находке на элемент. `implied` — список.

Существует ли такая группа в Odoo, ядро не проверяет.

**where:** `group`.

**Пример.** `{"key": "head", "name": "Заведующий", "xmlid": "group_department_head"}`;
`{"key": "teacher", "name": "Преподаватель", "implied": ["base_group_user"]}`.

**Кейсы:** [`ir-xmlid-invalid`](../../tests/cases/ir-xmlid-invalid/),
[`ir-xmlid-implied-invalid`](../../tests/cases/ir-xmlid-implied-invalid/).

---

## Модели и поля (этап 6)

Модели проверяются по порядку; внутри модели — техническое имя, название, вид,
вставка `x_name`, поля по порядку, первая часть `unique`. Внутри поля — объект,
имя, зарезервированность, повтор, подпись, тип, `default`, `selection`, связь.

### `S1.model_name` — неверное техническое имя модели

**Уровень:** B · **находка:** error · **этап:** 6 · **дальше:** продолжить

**Условие.** Техническое имя (`model`, а если его нет — `x_<app.key>_<key>`) не
строка, не соответствует `x_[a-z0-9_]+` или длиннее 63 символов. Одна находка
на модель.

**where:** `model` (ключ модели).

**Пример.** `{"key": "topic", "name": "Тема", "model": "demo_topic"}`

**Кейсы:** [`ir-model-name-no-prefix`](../../tests/cases/ir-model-name-no-prefix/),
[`ir-model-name-too-long`](../../tests/cases/ir-model-name-too-long/) (64 символа),
[`ir-model-name-default-too-long`](../../tests/cases/ir-model-name-default-too-long/)
(имя по умолчанию 65 символов); 63 символа допустимы —
[`ir-green-limits`](../../tests/cases/ir-green-limits/).

### `S1.model_kind` — неизвестный вид модели

**Уровень:** B · **находка:** error · **этап:** 6 · **дальше:** продолжить

**Условие.** `kind` (по умолчанию `"document"`) не равен `"document"` или
`"reference"`.

**where:** `model`.

**Пример.** `{"key": "topic", "name": "Тема", "kind": "catalog"}`

**Кейсы:** [`ir-model-kind-unknown`](../../tests/cases/ir-model-kind-unknown/).

### `S1.field` — поле не объект

**Уровень:** B · **находка:** error · **этап:** 6 · **дальше:** следующее поле

**Условие.** Элемент `fields` не JSON-объект.

**where:** `model`.

**Пример.** `"fields": [{"name": "x_name", ...}, "x_deadline"]`

**Кейсы:** [`ir-field-not-object`](../../tests/cases/ir-field-not-object/).

### `S1.field_name` — неверное имя поля

**Уровень:** B · **находка:** error · **этап:** 6

**Условие.** Два случая:

1. `name` отсутствует, не строка или не соответствует `x_[a-z0-9_]{1,40}`
   (то есть длиннее 42 символов, без префикса `x_`, с заглавными буквами и т. п.).
   **Дальше:** поле больше не проверяется и не считается описанным (ссылки на
   него из `unique` дадут `S1.unique`). `where`: `model`.
2. Имя корректно, но зарезервировано: `x_active` или `x_studio_state`.
   **Дальше:** проверка поля продолжается. `where`: `model`, `field`.

**Пример.** `{"name": "description", "type": "text", "label": "Аннотация"}`;
`{"name": "x_active", "type": "boolean", "label": "Активна"}`.

**Кейсы:** [`ir-field-name-no-prefix`](../../tests/cases/ir-field-name-no-prefix/),
[`ir-field-name-reserved`](../../tests/cases/ir-field-name-reserved/),
[`ir-field-name-too-long`](../../tests/cases/ir-field-name-too-long/) (43 символа;
42 допустимы — [`ir-green-limits`](../../tests/cases/ir-green-limits/)).

### `S1.field_type` — неподдерживаемый тип поля

**Уровень:** B · **находка:** error · **этап:** 6 · **дальше:** поле больше не
проверяется (`default`, `selection`, связь)

**Условие.** `type` отсутствует или не входит в список: `char`, `text`, `html`,
`integer`, `float`, `boolean`, `date`, `datetime`, `selection`, `many2one`,
`one2many`, `many2many`.

**where:** `model`, `field`.

**Пример.** `{"name": "x_budget", "type": "monetary", "label": "Бюджет"}`

**Кейсы:** [`ir-field-type-unknown`](../../tests/cases/ir-field-type-unknown/).

### `S1.default` — недопустимое значение по умолчанию

**Уровень:** B · **находка:** error · **этап:** 6 · **дальше:** продолжить

**Условие.** В поле есть ключ `default` (любое значение, включая `null`), и
значение не подходит типу поля по таблице
[01-ir-format.md § 7.2](01-ir-format.md#72-значения-по-умолчанию-полей-default):
`char` — подпись; `integer` — целое число (не `true`/`false`, не дробное, не
строка); `boolean` — `true`/`false`; `selection` — строка, равная ключу одного
из вариантов (варианты берутся из тех элементов `selection`, которые являются
непустыми списками); у остальных типов `default` недопустим вовсе.

**where:** `model`, `field`.

**Пример.** `{"name": "x_seats", "type": "integer", "label": "Мест", "default": "3"}`

**Кейсы:** [`ir-default-integer-string`](../../tests/cases/ir-default-integer-string/),
[`ir-default-selection-unknown`](../../tests/cases/ir-default-selection-unknown/),
[`ir-default-on-text`](../../tests/cases/ir-default-on-text/).

### `S1.selection` — неверные варианты выбора

**Уровень:** B · **находка:** error · **этап:** 6 · **дальше:** продолжить

**Условие.** У поля типа `selection` значение `selection` отсутствует, пусто
(`[]`) или содержит элемент, который не является списком ровно из двух
элементов `[ключ, подпись]`, где первый — ключ, второй — подпись. Одна находка на
поле. Повторы вариантов не проверяются.

**where:** `model`, `field`.

**Пример.** `{"name": "x_level", "type": "selection", "label": "Уровень", "selection": ["bachelor", "master"]}`
(правильно: `[["bachelor", "Бакалавриат"], ["master", "Магистратура"]]`).

**Кейсы:** [`ir-selection-flat`](../../tests/cases/ir-selection-flat/),
[`ir-selection-missing`](../../tests/cases/ir-selection-missing/).

### `S1.relation` — связь на неизвестную или неподходящую модель

**Уровень:** B · **находка:** error · **этап:** 6 · **дальше:** продолжить

**Условие.** Для полей `many2one`, `one2many`, `many2many`:

1. `relation` не разрешается ни одним из способов
   [01-ir-format.md § 7.1](01-ir-format.md#71-поля-fields): не ключ модели
   приложения, не техническое имя модели приложения и не имя внешней модели из
   снимка платформы (в том числе `relation` отсутствует).
2. Поле `one2many`, а `relation` не указывает на модель приложения (внешняя
   модель или не разрешилась). Для неразрешённой `relation` у `one2many`
   выдаются обе находки.

**where:** `model`, `field`.

**Пример.** `{"name": "x_company_id", "type": "many2one", "label": "Организация", "relation": "res.company"}`
(в снимке по умолчанию `res.company` нет);
`{"name": "x_partner_ids", "type": "one2many", "label": "Контакты", "relation": "res.partner", "inverse": "x_topic_id"}`.

**Кейсы:** [`ir-relation-unknown`](../../tests/cases/ir-relation-unknown/),
[`ir-relation-one2many-external`](../../tests/cases/ir-relation-one2many-external/).

### `S1.inverse` — нет обратного поля one2many

**Уровень:** B · **находка:** error · **этап:** 6 · **дальше:** продолжить

**Условие.** Поле `one2many` ведёт на модель приложения, но среди полей,
описанных у целевой модели в IR, нет поля с именем `inverse` (в том числе
`inverse` не задан), либо такое поле есть, но его тип не `many2one`. На какую
модель ведёт найденное `many2one`, не проверяется.

**where:** `model`, `field` (поле `one2many`).

**Пример.**
```json
{"name": "x_note_ids", "type": "one2many", "label": "Замечания", "relation": "note", "inverse": "x_topic"}
```
при том что в модели `note` поле называется `x_topic_id`.

**Кейсы:** [`ir-inverse-missing`](../../tests/cases/ir-inverse-missing/),
[`ir-inverse-not-many2one`](../../tests/cases/ir-inverse-not-many2one/).

### `S1.ondelete` — неподдерживаемый ondelete

**Уровень:** B · **находка:** error · **этап:** 6 · **дальше:** продолжить

**Условие.** У поля `many2one` значение `ondelete` (по умолчанию `"restrict"`
для обязательного поля и `"set null"` для необязательного) не равно
`"restrict"`, `"set null"` или `"cascade"`. У других типов `ondelete`
игнорируется.

**where:** `model`, `field`.

**Пример.** `{"name": "x_supervisor_id", "type": "many2one", "label": "Руководитель", "relation": "res.users", "ondelete": "set default"}`

**Кейсы:** [`ir-ondelete-unknown`](../../tests/cases/ir-ondelete-unknown/).

### `S1.unique` — неверное ограничение уникальности

**Уровень:** B · **находка:** error · **этапы:** 6 и 10 · **дальше:** продолжить

**Условие.** Проверка в две части.

Этап 6 — для каждого элемента `unique` модели одна находка, если: элемент не
объект; `fields` отсутствует или пуст; хотя бы одно имя в `fields`
не является ни именем поля, описанного в этой модели (с корректным именем,
включая автоматическое `x_name`), ни `create_uid`. Другие служебные поля
(`id`, `create_date`, …) недопустимы.

Этап 10 (выполняется, только если точка A пройдена) — для каждого ограничения:

- если в `fields` есть поля типов `one2many`, `many2many`, `text`, `html` — одна
  находка;
- если задан `live_nodes` (не `null`) и при этом у модели нет процесса, или
  `live_nodes` не является непустым списком строк, или содержит ключ, которого
  нет среди узлов процесса модели, — ещё одна находка.

**where:** `model`.

**Пример.** `"unique": [{"fields": ["x_description"]}]` (поле `text`);
`"unique": [{"fields": ["x_name"], "live_nodes": ["review", "approved"]}]`.

**Кейсы:** [`ir-unique-unknown-field`](../../tests/cases/ir-unique-unknown-field/),
[`ir-unique-text-field`](../../tests/cases/ir-unique-text-field/),
[`ir-unique-live-nodes-unknown`](../../tests/cases/ir-unique-live-nodes-unknown/);
корректное ограничение с `create_uid` и `live_nodes` —
[`ir-green-features`](../../tests/cases/ir-green-features/).

---

## Роли (этап 7)

Этапы 7–11 выполняются только если точка останова A пройдена (на этапах 2a–6
нет ни одной ошибки).

### `S1.role_groups` — роль без групп или с неизвестной группой

**Уровень:** B · **находка:** error · **этап:** 7 · **дальше:** продолжить

**Условие.** `groups` роли отсутствует, `null` или пустой список, либо хотя бы
один элемент не является ключом группы из раздела `groups` (xmlid Odoo вроде
`base.group_user` здесь не подходит). Одна находка на роль.

**where:** `role`.

**Пример.** `{"key": "student", "name": "Студент", "groups": ["students"]}`

**Кейсы:** [`ir-role-groups-unknown`](../../tests/cases/ir-role-groups-unknown/),
[`ir-role-groups-missing`](../../tests/cases/ir-role-groups-missing/).

### `S1.binding` — неверная привязка роли

**Уровень:** B · **находка:** error · **этап:** 7 · **дальше:** продолжить

**Условие.** `bindings` (по умолчанию `{}`):

1. не объект (в том числе `null` или список) — одна находка, `where`: `role`;
   остальные проверки привязок этой роли не выполняются.

Иначе для каждой пары `модель: путь` — **не больше одной** находки, проверки
по порядку до первой сработавшей:

2. `модель` не ключ модели приложения (техническое имя, внешняя модель,
   опечатка) — `where`: `role`;
3. путь не разрешается от этой модели по правилам
   [01-ir-format.md § 8.2](01-ir-format.md#82-пути-по-полям) (не строка, пустая
   строка, неизвестное поле, переход через не-связь) — `where`: `role`, `model`;
4. среди имён пути есть `write_uid` (на любой позиции) — `where`: `role`, `model`;
5. последнее поле пути не `many2one` и не `many2many` или ведёт не на
   `res.users` — `where`: `role`, `model`.

**Пример.** `"bindings": {"topic": "write_uid"}`;
`"bindings": {"topic": "x_contact_id"}`, где `x_contact_id` — many2one на
`res.partner`; `"bindings": {"topic": "create_uid.manager_id"}`.

**Кейсы:** [`ir-binding-write-uid`](../../tests/cases/ir-binding-write-uid/),
[`ir-binding-not-user`](../../tests/cases/ir-binding-not-user/),
[`ir-binding-unknown-model`](../../tests/cases/ir-binding-unknown-model/),
[`ir-binding-path-unknown-field`](../../tests/cases/ir-binding-path-unknown-field/);
корректный путь через внешнюю модель `x_project_id.user_id` —
[`ir-green-features`](../../tests/cases/ir-green-features/).

---

## Процессы, узлы, переходы (этап 8)

Процессы проверяются по порядку. Внутри процесса: модель, название, все узлы
по порядку, затем все переходы по порядку, затем `sod`. После всех процессов —
проверка «один процесс на модель».

### `S1.process_model` — процесс привязан не к той модели

**Уровень:** C · **находка:** error · **этап:** 8

**Условие.** Три случая:

1. `model` процесса не ключ модели приложения (неизвестный ключ, техническое
   имя вида `x_demo_topic`). **Дальше:** остальное в процессе (название, узлы,
   переходы, `sod`) не проверяется. Модель при этом остаётся без процесса,
   поэтому ячейки прав с `nodes` на неё дадут ещё `S1.access`.
2. Модель найдена, но её `kind` не `"document"` (справочник). **Дальше:**
   процесс проверяется как обычно.
3. (после всех процессов) `model` процесса совпадает с `model` одного из
   **предыдущих** процессов списка: находка на каждый следующий процесс.
   Значения `model` сравниваются как записаны, среди **всех** процессов, в
   том числе получивших находку по случаю 1 или 2: два процесса на одну
   неизвестную модель дают у второго процесса две находки (случаи 1 и 3).

**where:** `process`.

**Пример.** Модель `topic` объявлена с `"kind": "reference"`, а процесс
`topic` привязан к ней; второй процесс `topic_fast` с `"model": "topic"`.

**Кейсы:** [`ir-process-model-reference`](../../tests/cases/ir-process-model-reference/),
[`ir-process-model-twice`](../../tests/cases/ir-process-model-twice/).

### `S1.node` — неверный или повторный ключ узла

**Уровень:** C · **находка:** error · **этап:** 8 · **дальше:** узел больше не
проверяется (название, тип, исполнитель…)

**Условие.** `key` узла отсутствует, не строка, не является ключом или совпадает
с ключом **предыдущего** корректного узла этого процесса. Узел с неверным
ключом не считается известным узлом (переходы в него дадут `S1.flow_node`).

**where:** `process`.

**Пример.** `{"key": "on-hold", "name": "Отложена"}`; второй узел `review`.

**Кейсы:** [`ir-node-duplicate`](../../tests/cases/ir-node-duplicate/),
[`ir-node-key-invalid`](../../tests/cases/ir-node-key-invalid/),
[`ir-node-key-too-long`](../../tests/cases/ir-node-key-too-long/) (32 символа;
31 допустим — [`ir-green-limits`](../../tests/cases/ir-green-limits/)).

### `S1.node_type` — неизвестный тип узла

**Уровень:** C · **находка:** error · **этап:** 8 · **дальше:** продолжить

**Условие.** `type` (по умолчанию `"step"`) не равен `"step"`, `"xor"` или
`"end"`. Узел с неизвестным типом не считается шагом, поэтому если у него есть
`assignee`, будет ещё и `S1.assignee`.

**where:** `process`, `node`.

**Пример.** `{"key": "published", "name": "Опубликована", "type": "finish"}`

**Кейсы:** [`ir-node-type-unknown`](../../tests/cases/ir-node-type-unknown/).

### `S1.assignee` — исполнитель не у шага

**Уровень:** C · **находка:** error · **этап:** 8 · **дальше:** продолжить

**Условие.** У узла задан `assignee` (не отсутствует и не `null`), а тип узла
(после подстановки по умолчанию) не `"step"`. Проверяется независимо от
`S1.role_ref`: неизвестная роль-исполнитель у завершения даёт обе находки.

**where:** `process`, `node`.

**Пример.** `{"key": "published", "name": "Опубликована", "type": "end", "assignee": "author"}`

**Кейсы:** [`ir-assignee-on-end`](../../tests/cases/ir-assignee-on-end/).

### `S1.result` — неизвестный итог завершения

**Уровень:** C · **находка:** error · **этап:** 8 · **дальше:** продолжить

**Условие.** Узел типа `"end"`, и `result` (по умолчанию `"done"`) не равен
`"done"`, `"rejected"` или `"cancelled"`. У узлов других типов `result` не
проверяется.

**where:** `process`, `node`.

**Пример.** `{"key": "rejected", "name": "Отклонена", "type": "end", "result": "declined"}`

**Кейсы:** [`ir-result-unknown`](../../tests/cases/ir-result-unknown/).

### `S1.role_ref` — ссылка на неизвестную роль

**Уровень:** C · **находка:** error · **этап:** 8 · **дальше:** продолжить

**Условие.** По находке на каждую ссылку, которая не является ключом роли из
раздела `roles` (ключ группы тоже не подходит):

| Место | where |
|---|---|
| `nodes[].assignee` (если не `null`) | `process`, `node` |
| каждый элемент `nodes[].release` | `process`, `node` |
| каждый элемент `flows[].by` | `process`, `flow` |
| каждый элемент `flows[].notify` | `process`, `flow` |

Роли в условиях (`actor`) и действиях (`subscribe`) проверяются по правилам
[05-conditions-effects-policy.md](05-conditions-effects-policy.md).

**Пример.** `{"key": "review", "name": "На утверждении", "assignee": "reviewer"}`;
`"by": ["head", "teacher"]`, где `teacher` — группа.

**Кейсы:** [`ir-role-ref-assignee`](../../tests/cases/ir-role-ref-assignee/),
[`ir-role-ref-by`](../../tests/cases/ir-role-ref-by/),
[`ir-role-ref-release`](../../tests/cases/ir-role-ref-release/).

### `S1.flow` — неверный ключ перехода или sequence

**Уровень:** C · **находка:** error · **этап:** 8

**Условие.** Два случая:

1. `key` перехода отсутствует, не строка, не является ключом или совпадает с
   ключом **предыдущего** корректного перехода этого процесса. **Дальше:**
   переход больше не проверяется (подпись, концы, роли, поля, условие,
   действия) и не считается известным переходом (ссылки на него из `sod` дадут
   `S1.sod`). `where`: `process`.
2. `sequence` (по умолчанию `(позиция + 1) * 10`) не целое число: строка, дробное
   (`40.0` тоже), `true`/`false`, `null`. **Дальше:** проверка продолжается.
   `where`: `process`, `flow`.

**Пример.** Второй переход с `"key": "approve"`; `"sequence": "40"`.

**Кейсы:** [`ir-flow-duplicate-key`](../../tests/cases/ir-flow-duplicate-key/),
[`ir-flow-sequence-not-int`](../../tests/cases/ir-flow-sequence-not-int/).

### `S1.flow_node` — переход ссылается на неизвестный узел

**Уровень:** C · **находка:** error · **этап:** 8 · **дальше:** продолжить

**Условие.** `from` (и отдельно `to`) отсутствует или не равен ключу известного
узла этого процесса. Если неверны оба конца — две находки.

**where:** `process`, `flow`.

**Пример.** `{"key": "approve", "label": "Утвердить", "from": "review", "to": "publish", "by": ["head"]}`

**Кейсы:** [`ir-flow-node-unknown`](../../tests/cases/ir-flow-node-unknown/).

### `S1.flow_kind` — неизвестный вид перехода

**Уровень:** C · **находка:** error · **этап:** 8 · **дальше:** продолжить

**Условие.** `kind` (по умолчанию `"normal"`) не равен `"normal"` или `"return"`.

**where:** `process`, `flow`.

**Пример.** `{"key": "rework", ..., "kind": "back"}`

**Кейсы:** [`ir-flow-kind-unknown`](../../tests/cases/ir-flow-kind-unknown/).

### `S1.comment` — неизвестный режим комментария

**Уровень:** C · **находка:** error · **этап:** 8 · **дальше:** продолжить

**Условие.** `comment` (по умолчанию `"none"`) не равен `"none"`, `"optional"`
или `"required"`.

**where:** `process`, `flow`.

**Пример.** `{"key": "reject", ..., "comment": "mandatory"}`

**Кейсы:** [`ir-comment-unknown`](../../tests/cases/ir-comment-unknown/).

### `S1.field_ref` — неверное поле в requires / inputs

**Уровень:** B · **находка:** error · **этап:** 8 · **дальше:** продолжить

**Условие.** По находке на каждый элемент:

- элемент `requires` или `inputs`, который не является именем поля, описанного
  в модели процесса (включая автоматическое `x_name`), или является служебным
  полем (`id`, `create_uid`, `write_uid`, `create_date`, `write_date`);
- элемент `inputs`, который является полем типа `one2many` или `many2many`
  (в `requires` такие поля допустимы).

**where:** `process`, `flow`.

**Пример.** `"requires": ["x_annotation"]`; `"requires": ["create_date"]`;
`"inputs": ["x_reviewer_ids"]` для many2many-поля.

**Кейсы:** [`ir-field-ref-requires-unknown`](../../tests/cases/ir-field-ref-requires-unknown/),
[`ir-field-ref-requires-magic`](../../tests/cases/ir-field-ref-requires-magic/),
[`ir-field-ref-inputs-list`](../../tests/cases/ir-field-ref-inputs-list/).

### `S1.sod` — неверная пара разделения обязанностей

**Уровень:** C · **находка:** error · **этап:** 8 · **дальше:** продолжить

**Условие.** По находке на каждый элемент `sod`, который не является списком
ровно из двух элементов, каждый из которых — ключ известного перехода этого
процесса. Пара из двух одинаковых ключей на уровне схемы допустима (её
невыполнимость — забота анализа прав).

**where:** `process`.

**Пример.** `"sod": [["submit", "approval"]]` — перехода `approval` нет.

**Кейсы:** [`ir-sod-unknown-flow`](../../tests/cases/ir-sod-unknown-flow/).

---

## Условие создания (этап 9)

### `S1.create_if` — условие создания у модели без процесса

**Уровень:** B · **находка:** error · **этап:** 9 · **дальше:** продолжить

**Условие.** У модели есть ключ `create_if` (с любым значением, включая
`null`), а процесса у модели нет. Если процесс есть, само условие проверяется
по правилам условий (код `S1.condition`, см. [05-conditions-effects-policy.md](05-conditions-effects-policy.md)).

**where:** `model`.

**Пример.** `{"key": "note", "name": "Замечание", "kind": "reference", "create_if": {"actor": "head"}}`

**Кейсы:** [`ir-create-if-no-process`](../../tests/cases/ir-create-if-no-process/).

---

## Права (этап 11)

### `S1.access` — неверная ячейка прав

**Уровень:** B · **находка:** error · **этап:** 11 · **дальше:** продолжить со
следующей ячейки или проверки

**Условие.** Ячейки проверяются по порядку, `i` — индекс ячейки. Проверки
внутри ячейки:

| № | Нарушение | where | Дальше |
|---|---|---|---|
| 1 | `role` не ключ роли (в том числе ключ группы) | `cell` | ячейка пропускается |
| 2 | `model` не ключ модели приложения (в том числе техническое имя или внешняя модель) | `role`, `cell` | ячейка пропускается |
| 3 | `op` не `read` / `write` / `create` / `unlink` | `role`, `cell` | ячейка пропускается |
| 4 | `nodes` задан (не `null`), а у модели нет процесса | `role`, `cell` | продолжить |
| 5 | `nodes` задан, процесс есть, но `nodes` не непустой список строк из ключей узлов процесса (в том числе `[]`) | `role`, `cell` | продолжить |
| 6 | `nodes` задан и `op` = `create` (дополнительно к 4/5, если они сработали) | `role`, `cell` | продолжить |
| 7 | `op` — `write` или `create`, и `fields` (по умолчанию все поля модели) не список или содержит имя, которого нет среди полей, описанных в модели (служебные поля сюда не входят) | `role`, `cell` | продолжить |
| 8 | роль привязанная (`bindings` не пуст), модели ячейки нет в её `bindings`, `op` ≠ `create`; `see_all` не освобождает | `role`, `model` | продолжить |

`fields` у `read` / `unlink` не проверяется. Пустой список `fields` у `write` /
`create` допустим.

**Пример.**
```json
{"role": "teacher", "model": "topic", "op": "read"}
{"role": "author", "model": "topic", "op": "create", "nodes": ["draft"]}
{"role": "head", "model": "topic", "op": "read", "nodes": ["review", "published", "archived"]}
```

**Кейсы:**
[`ir-access-unknown-role`](../../tests/cases/ir-access-unknown-role/) (1),
[`ir-access-unknown-model`](../../tests/cases/ir-access-unknown-model/) (2),
[`ir-access-bad-op`](../../tests/cases/ir-access-bad-op/) (3),
[`ir-access-nodes-no-process`](../../tests/cases/ir-access-nodes-no-process/) (4),
[`ir-access-unknown-node`](../../tests/cases/ir-access-unknown-node/) (5),
[`ir-access-empty-nodes`](../../tests/cases/ir-access-empty-nodes/) (5),
[`fix-access-nodes-node-objects`](../../tests/cases/fix-access-nodes-node-objects/) (5: объекты узлов вместо ключей),
[`ir-access-create-with-nodes`](../../tests/cases/ir-access-create-with-nodes/) (6),
[`ir-access-write-unknown-field`](../../tests/cases/ir-access-write-unknown-field/) (7),
[`ir-access-no-binding`](../../tests/cases/ir-access-no-binding/) (8).

---

## Чего проверки схемы не делают

Эти ситуации **не** дают находок `S1.*` (некоторые ловят анализы других
классов). Лишние находки на них учитываются при сравнении реализаций.

- Совпадение технических имён разных моделей, а также ключа одной модели с
  техническим именем другой. Находок нет, но куда ведут ссылки в такой
  конфигурации, не определено (см. «Входы вне контракта»).
- Тип значений `required`, `see_all`, `start`, `auto`, `system`, `default`
  перехода: используется только их истинность.
- Повторы: вариантов `selection`, имён в `unique[].fields`, элементов `groups`
  роли, `by`, `notify`, `requires`, `inputs`, `release`, `nodes` и `fields`
  ячеек прав (нормализация их просто удаляет).
- На какую модель ведёт обратное поле `inverse` (важно только, что это
  `many2one` в целевой модели).
- `result` у узлов, отличных от `end`; значение `sequence` (отрицательные и
  повторяющиеся допустимы); порядок узлов и переходов.
- Число стартовых узлов, достижимость, тупики, развилки, завершения — это
  проверки структуры (`S3.*`, `S5.*`, [03-structure.md](03-structure.md)).
- Достаточность прав: видит ли исполнитель документ, может ли кто-то заполнить
  `requires`, выполнима ли пара `sod` из одинаковых переходов — анализ прав
  (`A*`, [04-roles-and-access.md](04-roles-and-access.md)).
- Существует ли в Odoo группа с указанным `xmlid`.
- Ключи `fields` у ячеек `read` / `unlink`; неизвестные ключи любых объектов.

## Входы вне контракта

На входах ниже поведение не определено, и тестов на них нет. Реализация не
должна падать с трейсбеком; рекомендуется выдать находку ближайшего по смыслу
кода (указан в скобках) и вердикт `reject`:

- элемент `nodes`, `flows` или `access` — не объект (`S1.node`, `S1.flow`,
  `S1.access`);
- процесс без ключа `model` (`S1.process_model`);
- узел без ключа `key` вовсе (`S1.node`);
- `null` или значение не-списочного типа там, где ожидается список; код
  по месту:

  | Где | Рекомендуемый код |
  |---|---|
  | `fields` модели | `S1.field` |
  | `unique` модели | `S1.unique` |
  | `implied` группы | `S1.xmlid` |
  | `groups` роли | `S1.role_groups` |
  | `nodes` процесса | `S1.node` |
  | `flows` процесса | `S1.flow` |
  | `sod` процесса | `S1.sod` |
  | `by`, `notify` перехода; `release` узла | `S1.role_ref` |
  | `requires`, `inputs` перехода | `S1.field_ref` |
  | `effects` перехода | `S2.effect` (раздел 05, § 5.9) |
- список или объект там, где ожидается строка: ключ или ссылка
  (`relation`, `from`, `to`, `model` процесса, `assignee`, элементы `by`,
  `notify`, `release`, `groups` роли, пары `sod`, `role` / `model` / `op` и
  элементы `fields` строки прав) или значение из перечня (`type` поля, узла и
  действия, `result`, `kind`, `comment`). Код — по месту (`S1.role_ref`,
  `S1.field_type`, `S1.flow_kind`, `S1.access`, …). Исключение: элементы
  `nodes` строки прав — в контракте (строка 5 у `S1.access`, кейс
  [`fix-access-nodes-node-objects`](../../tests/cases/fix-access-nodes-node-objects/));
- `bindings` роли — `true` или число, и у этой роли есть строка прав
  (`S1.binding`; `null`, список и строка — в контракте, случай 1);
- строка там, где ожидается список (например, `"by": "head"`), — частный
  случай пункта о не-списках выше. Эталон перебирает такую строку по символам
  (`"by": ""` для него — пустой список), реализация не обязана так делать;
- `unique[].fields`, заданный не списком, а объектом или строкой (`S1.unique`);
- поле `one2many`, целевая модель которого содержит в `fields` не-объект
  (`S1.field` у целевой модели);
- переход, у которого одновременно неверный ключ (`S1.flow`) и нецелый
  `sequence`;
- совпадение технических имён моделей (или ключа одной модели с техническим
  именем другой) вместе со ссылкой `relation` или путём через такое имя
  (раздел 01, § 7.1): на какую модель ведёт ссылка, не определено.
