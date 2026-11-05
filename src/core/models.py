class Record:
    """
    Одно занятие в расписании.
    Класс для хранения информации о нём.
    """

    def __init__(self, group: str, day: str, pair: int, subject: str, subgroup: str,
                 lesson_type: str, teacher: str, room: str, week: str):
        # Просто сохраняем все значения в поля объекта
        self.group = group            # группа, например 'БВТ-251'
        self.day = day                # день недели: ПН, ВТ, СР...
        self.pair = pair              # номер пары: 1, 2, 3...
        self.subject = subject        # название предмета
        self.subgroup = subgroup      # подгруппа (1 или 2), 0 если вся группа
        self.lesson_type = lesson_type  # тип: 'лек', 'прак', 'лаб'
        self.teacher = teacher        # преподаватель
        self.room = room              # аудитория
        self.week = week              # 'odd' или 'even'

    def key(self):
        """
        По этим полям узнаём, что это за занятие.
        """

        return (self.group, self.day, self.pair, self.week, self.subgroup)

    def __repr__(self) -> str:
        """
        Как объект будет выглядеть при print().
        """

        return (f"Record(group='{self.group}', day='{self.day}', "
                f"pair={self.pair}, subject='{self.subject}')")

    def __eq__(self, other) -> bool:
        """
        Сравнение двух записей (нужно для поиска различий).
        """

        if not isinstance(other, Record):
            return False
        return self.key() == other.key()


class Change:
    """
    Одно изменение в расписании.
    """

    def __init__(self, kind, key, field=None, old=None, new=None):
        self.kind = kind      # 'added', 'removed', 'changed'
        self.key = key        # ключ занятия
        self.field = field    # какое поле поменялось
        self.old = old        # старое значение
        self.new = new        # новое значение

    def describe(self) -> str:
        """
        Вернуть понятную строку с описанием изменения.
        """

        group, day, pair, week, subgroup = self.key

        if week == 'odd':
            week_text = 'нечётная неделя'
        else:
            week_text = 'чётная неделя'

        base = f'{group} | {day} | {pair} пара | {week_text}'

        if subgroup:
            base += f', подгруппа {subgroup}'

        if self.kind == 'added':
            return f'ДОБАВЛЕНО: {base}'
        elif self.kind == 'removed':
            return f'УДАЛЕНО: {base}'
        else:
            return f'ИЗМЕНЕНО: {base} | {self.field}: было «{self.old}», стало «{self.new}»'

    def __repr__(self) -> str:
        return f"Change(kind='{self.kind}', key={self.key})"
    