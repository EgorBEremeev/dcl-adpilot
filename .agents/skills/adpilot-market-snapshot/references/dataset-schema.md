# Спецификация датасета `<snapshot>.json` для `render_snapshot_svg.py`

Скрипт [render_snapshot_svg.py](../scripts/render_snapshot_svg.py) ожидает JSON-объект в UTF-8 без BOM со следующей структурой.

## Корневые поля

- `meta` *(object, обязательный)* — параметры среза и шкалы графика.
- `totals` *(object, опциональный)* — живые счётчики выдачи по запросам (хранятся для истории и воспроизводимости).
- `clusters` *(array, обязательный)* — список товарных кластеров и ценовых ориентиров.

## Поля `meta`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `snapshot_at` | string | да | ISO-время формирования отчёта |
| `catalog_id` | string | да | Идентификатор каталога (`family_household`) |
| `category_id` | string | да | Код категории (`HM-FU-ST-CH-DIN`) |
| `category_path` | string | да | Относительный путь категории |
| `reference_part_id` | string | да | `part_id` референсного товара |
| `currency` | string | нет | Валюта на осях, по умолчанию `"EUR"` |
| `platform` | string | нет | Платформа в заголовке, по умолчанию `"OLX.bg"` |
| `x_max_eur` | number | нет | Правая граница шкалы X, по умолчанию `130` |
| `x_overflow_label` | string | нет | Подпись справа при обрезке длинного хвоста (например `"→ 220 €+"`) |
| `threshold_eur` | number | нет | Вертикальная пунктирная линия порога (например `58`) |
| `threshold_label` | string | нет | Подпись порога в легенде |

## Поля элемента `clusters[]`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `code` | string | да | Код кластера (`B1`, `B2`, `N1`, `N2`, `P1`–`P3`) |
| `group` | enum | да | `"used"` (синий `●`), `"new"` (красный `●`), `"target"` (зелёный `◆`) |
| `geo` | enum | да | `"bg"` (верхняя зона, Вся Болгария) или `"varna"` (нижняя зона, г. Варна) |
| `min` | number | да | Левая граница диапазона цены |
| `max` | number | да | Правая граница диапазона цены (при точечном значении равна `min`) |
| `peak` | number | да | Положение центра круга/ромба (пик/мода или целевая точка) |
| `count` | number | нет | Число объявлений в кластере; определяет радиус круга (`5..16 px`), для `"target"` игнорируется |
| `lane` | integer | нет | Дорожка внутри зоны (`0..3`, по умолчанию `0`): `0` и `1` — подпись сверху, `2` и `3` — снизу |
| `label` | string | да | Подпись на графике |
| `label_dx` | number | нет | Горизонтальный сдвиг подписи в пикселях (по умолчанию `0`) |
| `label_anchor` | enum | нет | Выравнивание текста: `"middle"` (по умолчанию), `"start"`, `"end"` |

## Минимальный пример

```json
{
  "meta": {
    "snapshot_at": "2026-11-24T16:52:00+02:00",
    "catalog_id": "family_household",
    "category_id": "HM-FU-ST-CH-DIN",
    "category_path": "02-home/furniture/seating_chairs_stools/chairs/dining_chairs",
    "reference_part_id": "HM-FU-ST-CH-DIN-20261124-121840",
    "currency": "EUR",
    "platform": "OLX.bg",
    "x_max_eur": 130,
    "threshold_eur": 58,
    "threshold_label": "Порог реплики (58 €)"
  },
  "totals": {
    "vienski_stol_bg": 46
  },
  "clusters": [
    {
      "code": "B1",
      "group": "used",
      "geo": "bg",
      "min": 10,
      "max": 25,
      "peak": 18,
      "count": 15,
      "lane": 0,
      "label": "B1: 10–25 € (~15 шт.)"
    }
  ]
}
```
