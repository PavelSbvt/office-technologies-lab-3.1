from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Record:
    """Одно занятие в расписании (одна «клетка» после разворота)."""
    group: str
    day: str            # ПН/ВТ/СР/ЧТ/ПТ/СБ
    pair: int
    subject: str
    subgroup: Optional[int]
    lesson_type: str    # лек/прак/лаб
    teacher: str
    room: str
    week: str           # 'odd' (нечётная) | 'even' (чётная)

    def key(self) -> tuple:
        """Ключ занятия: по нему сопоставляем записи между версиями."""
        return (self.group, self.day, self.pair, self.week, self.subgroup)


@dataclass
class Change:
    """Одно различие между версиями."""
    kind: str                       # 'added' | 'removed' | 'changed'
    key: tuple
    field: Optional[str] = None     # для 'changed' — какое поле поменялось
    old: Optional[str] = None
    new: Optional[str] = None

    def describe(self) -> str:
        group, day, pair, week, subgroup = self.key
        week_ru = 'нечёт.' if week == 'odd' else 'чёт.'
        sub = f', подгр. {subgroup}' if subgroup else ''
        base = f'{group} | {day} | {pair} пара | {week_ru}{sub}'
        if self.kind == 'added':
            return f'ДОБАВЛЕНО: {base}'
        if self.kind == 'removed':
            return f'УДАЛЕНО: {base}'
        return f'ИЗМЕНЕНО: {base} | {self.field}: «{self.old}» → «{self.new}»'
    