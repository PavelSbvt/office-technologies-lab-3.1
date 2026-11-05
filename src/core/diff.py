from core.models import Change, Record

# Поля, которые мы проверяем на изменения (остальные — это ключ пары)
COMPARED_FIELDS = ('subject', 'lesson_type', 'teacher', 'room')


def diff(a: list[Record], b: list[Record]) -> list[Change]:
    """
    Сравнивает две версии расписания.
    Возвращает список изменений (добавленные, удалённые, изменённые).
    """

    # 1. Создаем словари для быстрого поиска: {ключ_пары: объект_пары}
    a_by_key = {r.key(): r for r in a}
    b_by_key = {r.key(): r for r in b}

    changes = []

    # 2. Ищем УДАЛЁННЫЕ пары (есть в старом, нет в новом)
    for k in a_by_key.keys() - b_by_key.keys():
        changes.append(Change('removed', k))

    # 3. Ищем ДОБАВЛЕННЫЕ пары (есть в новом, нет в старом)
    for k in b_by_key.keys() - a_by_key.keys():
        changes.append(Change('added', k))

    # 4. Ищем ИЗМЕНЁННЫЕ пары (есть в обоих, но поля отличаются)
    for k in a_by_key.keys() & b_by_key.keys():
        ra, rb = a_by_key[k], b_by_key[k]

        # Проходим по всем важным полям (предмет, тип, препод, аудитория)
        for field in COMPARED_FIELDS:
            old = getattr(ra, field)
            new = getattr(rb, field)

            # Если значение поменялось — фиксируем изменение
            if old != new:
                changes.append(Change('changed', k, field, old, new))

    # 5. Сортируем для красивого вывода: группа -> день -> номер пары -> неделя
    changes.sort(key=lambda c: (c.key[0], c.key[1], c.key[2], c.key[3]))

    return changes