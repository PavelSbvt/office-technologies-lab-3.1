import re
import pandas as pd
from core.models import Record


def clean_text(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    return re.sub(r'\s+', ' ', str(value).strip())


def clean_number(value) -> int | None:
    s = clean_text(value)
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def parse_sheet(path: str, sheet_name: str) -> list[Record]:
    df = pd.read_excel(path, sheet_name=sheet_name, header=None)

    header_row = 0
    for i in range(min(30, len(df))):
        if clean_text(df.iat[i, 0]) == 'Группа':
            header_row = i
            break
    else:
        raise ValueError("Не найдена строка заголовков (нет слова 'Группа')")

    body = df.iloc[header_row + 1:].copy()
    body[0] = body[0].ffill()
    body[1] = body[1].ffill()
    body[8] = body[8].ffill()

    records = []

    for _, row in body.iterrows():
        # Левая часть (нечетная)
        subject_odd = clean_text(row.iloc[3])
        if subject_odd:
            group = clean_text(row.iloc[0])
            day = clean_text(row.iloc[1])
            pair = clean_number(row.iloc[2])

            if group and day and pair is not None:
                records.append(Record(
                    group=group, day=day, pair=pair, subject=subject_odd,
                    lesson_type=clean_text(row.iloc[5]).lower(),
                    teacher=clean_text(row.iloc[6]),
                    room=clean_text(row.iloc[7]),
                    week='odd'
                ))

        # Правая часть (четная)
        subject_even = clean_text(row.iloc[10])
        if subject_even:
            group = clean_text(row.iloc[0])
            day = clean_text(row.iloc[8])
            pair = clean_number(row.iloc[9])

            if group and day and pair is not None:
                records.append(Record(
                    group=group, day=day, pair=pair, subject=subject_even,
                    lesson_type=clean_text(row.iloc[12]).lower(),
                    teacher=clean_text(row.iloc[13]),
                    room=clean_text(row.iloc[14]),
                    week='even'
                ))

    return records