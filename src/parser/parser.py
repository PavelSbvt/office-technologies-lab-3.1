import re
from typing import Optional

import pandas as pd

from core.models import Record


DAY_VALUES = {'ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ'}


def _norm_str(value) -> str:
    """Приводит значение к строке: strip + схлопывание пробелов."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    s = str(value).strip()
    s = re.sub(r'\s+', ' ', s)
    return s


def _norm_pair(value) -> Optional[int]:
    """№ пары → int, иначе None."""
    s = _norm_str(value)
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def _norm_subgroup(value) -> Optional[int]:
    s = _norm_str(value)
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def _find_header_row(df: pd.DataFrame) -> int:
    """Ищет строку, где в колонке 0 стоит 'Группа'."""
    for i in range(min(30, len(df))):
        if _norm_str(df.iat[i, 0]) == 'Группа':
            return i
    raise ValueError('Не найдена строка заголовков (нет ячейки "Группа" в колонке A)')


def _row_to_records(row: pd.Series, week: str,
                    cols: tuple) -> list[Record]:
    """
    cols — индексы колонок в порядке:
    (group, day, pair, subject, subgroup, lesson_type, teacher, room)
    """
    g, d, p, subj, sub, ltype, teach, room = (row.iloc[c] for c in cols)

    subject = _norm_str(subj)
    if not subject:
        return []                      # пустая ячейка — пропускаем

    group = _norm_str(g)
    day = _norm_str(d)
    pair = _norm_pair(p)
    if not group or not day or pair is None:
        return []                      # неполная запись

    return [Record(
        group=group,
        day=day,
        pair=pair,
        subject=subject,
        subgroup=_norm_subgroup(sub),
        lesson_type=_norm_str(ltype).lower(),
        teacher=_norm_str(teach),
        room=_norm_str(room),
        week=week,
    )]


def parse_sheet(path: str, sheet_name: str) -> list[Record]:
    """
    Читает один лист .xls/.xlsx и возвращает плоский список занятий.
    Ожидает структуру «расписание ИАиИТ»:
      A: Группа, B: День недели, C: № пары, D: Предмет, E: Подгр,
      F: Тип зан., G: Преподаватель, H: Аудитория  — нечётная неделя
      I: День недели, J: № пары, K: Предмет, L: Подгр,
      M: Тип зан., N: Преподаватель, O: Аудитория — чётная неделя
    """
    df = pd.read_excel(path, sheet_name=sheet_name, header=None)

    header_row = _find_header_row(df)
    body = df.iloc[header_row + 1:].copy()

    # Объединённые ячейки «Группа» и «День недели» заполнены только в первой
    # строке блока — протягиваем вниз.
    body[0] = body[0].ffill()    # Группа
    body[1] = body[1].ffill()    # День недели (левая половина)
    body[8] = body[8].ffill()    # День недели (правая половина)

    records: list[Record] = []
    for _, row in body.iterrows():
        # левая половина (нечётная неделя): A..H
        records.extend(_row_to_records(row, 'odd', (0, 1, 2, 3, 4, 5, 6, 7)))
        # правая половина (чётная неделя): A (группа) + I..O
        records.extend(_row_to_records(row, 'even', (0, 8, 9, 10, 11, 12, 13, 14)))

    return records
