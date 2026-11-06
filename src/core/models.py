class Record:
    """
    Одно занятие в расписании.
    """

    def __init__(self, group: str, day: str, pair: int, subject: str,
                 lesson_type: str, teacher: str, room: str, week: str):
        self.group = group
        self.day = day
        self.pair = pair
        self.subject = subject
        self.lesson_type = lesson_type
        self.teacher = teacher
        self.room = room
        self.week = week

    def key(self):
        return (self.group, self.day, self.pair, self.week)

    def __repr__(self) -> str:
        return (f"Record(group='{self.group}', day='{self.day}', "
                f"pair={self.pair}, subject='{self.subject}')")

    def __eq__(self, other) -> bool:
        if not isinstance(other, Record):
            return False
        return self.key() == other.key()

    # Важно для использования в множествах!
    def __hash__(self):
        return hash(self.key())


class Change:
    """
    Одно изменение в расписании.
    """

    def __init__(self, kind, key, field=None, old=None, new=None,
                 record_a=None, record_b=None):
        self.kind = kind  # 'added', 'removed', 'changed'
        self.key = key  # ключ занятия
        self.field = field  # какое поле поменялось
        self.old = old  # старое значение поля
        self.new = new  # новое значение поля
        self.record_a = record_a  # полный объект пары ДО (для changed/removed)
        self.record_b = record_b  # полный объект пары ПОСЛЕ (для changed/added)

    def describe(self) -> str:
        group, day, pair, week = self.key
        week_text = 'нечётная неделя' if week == 'odd' else 'чётная неделя'
        base = f'{group} | {day} | {pair} пара | {week_text}'

        if self.kind == 'added':
            return f'ДОБАВЛЕНО: {base}'
        elif self.kind == 'removed':
            return f'УДАЛЕНО: {base}'
        else:
            return f'ИЗМЕНЕНО: {base} | {self.field}: было «{self.old}», стало «{self.new}»'

    def __repr__(self) -> str:
        return f"Change(kind='{self.kind}', key={self.key})"