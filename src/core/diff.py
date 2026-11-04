from core.models import Change, Record


COMPARED_FIELDS = ('subject', 'lesson_type', 'teacher', 'room')


def diff(a: list[Record], b: list[Record]) -> list[Change]:
    """
    Сравнивает две версии расписания по ключу занятия.
    Возвращает список изменений: added / removed / changed.
    """
    a_by_key = {r.key(): r for r in a}
    b_by_key = {r.key(): r for r in b}

    changes: list[Change] = []

    for k in a_by_key.keys() - b_by_key.keys():
        changes.append(Change('removed', k))

    for k in b_by_key.keys() - a_by_key.keys():
        changes.append(Change('added', k))

    for k in a_by_key.keys() & b_by_key.keys():
        ra, rb = a_by_key[k], b_by_key[k]
        for field in COMPARED_FIELDS:
            old, new = getattr(ra, field), getattr(rb, field)
            if old != new:
                changes.append(Change('changed', k, field, old, new))

    # сортировка для читаемого вывода: группа → день → пара → неделя
    changes.sort(key=lambda c: (c.key[0], c.key[1], c.key[2], c.key[3]))
    return changes
