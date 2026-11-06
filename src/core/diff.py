from core.models import Change, Record

COMPARED_FIELDS = ('subject', 'lesson_type', 'teacher', 'room')

def diff(a: list[Record], b: list[Record]) -> list[Change]:
    """Сравнивает две версии расписания."""
    a_by_key = {r.key(): r for r in a}

    b_by_key = {}
    for r in b:
        k = r.key()
        b_by_key[k] = r

    changes = []

    # 1. Удаленные (есть в А, нет в Б)
    for k in a_by_key.keys() - b_by_key.keys():
        changes.append(Change('removed', k, record_a=a_by_key[k]))

    # 2. Добавленные (есть в Б, нет в А)
    for k in b_by_key.keys() - a_by_key.keys():
        changes.append(Change('added', k, record_b=b_by_key[k]))

    # 3. Измененные (есть в обоих, но поля отличаются)
    for k in a_by_key.keys() & b_by_key.keys():
        ra, rb = a_by_key[k], b_by_key[k]
        for field in COMPARED_FIELDS:
            old = getattr(ra, field)
            new = getattr(rb, field)
            if old != new:
                # Передаем оба объекта ra и rb
                changes.append(Change('changed', k, field, old, new, record_a=ra, record_b=rb))

    # Сортировка
    changes.sort(key=lambda c: (c.key[0], c.key[1], c.key[2], c.key[3]))
    return changes