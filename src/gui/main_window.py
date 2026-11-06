from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush, QCloseEvent
from PyQt6.QtWidgets import (
    QWidget, QFileDialog, QMessageBox, QTableWidgetItem,
)
from PyQt6.uic import loadUi

from parser.parser import parse_sheet
from core.diff import diff
from utils.output_rich import Rich
from gui.utils.windows_animations import AnimationsManager


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setMinimumSize(1100, 700)
        self.setWindowTitle("Офисные технологии — ЛР 3.1: сравнение расписаний")

        self.path_a = ""
        self.path_b = ""

        ui_path = Path("src/gui/ui/main-window.ui").as_posix()
        loadUi(ui_path, self)

        self.btn_a.clicked.connect(self.button_a_pressed)
        self.btn_b.clicked.connect(self.button_b_pressed)
        self.btn_cmp.clicked.connect(self.compare_sheets)

        self.table.horizontalHeader().setStretchLastSection(True)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Останавливает воркеры и запускает анимацию закрытия окна.

        :param event: событие закрытия окна
        """

        if getattr(self, "_is_closing", False):
            event.accept()
            return

        Rich.exit_log("Выход из приложения - закрытие главного окна")

        self._is_closing = True

        event.ignore()

        Rich.debug_log("Запуск анимации исчезновения окна")

        self.close_anim = AnimationsManager.animation_of_window_disappearing(
            self, 265)

    def button_a_pressed(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите исходный файл (А)", "", "Excel (*.xls *.xlsx)")
        if file_path:
            self.path_a = file_path
            self.lbl_a.setText(Path(file_path).name)

    def button_b_pressed(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл для сравнения (Б)", "", "Excel (*.xls *.xlsx)")
        if file_path:
            self.path_b = file_path
            self.lbl_b.setText(Path(file_path).name)

    def compare_sheets(self):
        if not self.path_a or not self.path_b:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите оба файла.")
            return

        sheet = self.edit_sheet.text().strip()
        if not sheet:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, укажите имя листа.")
            return

        try:
            Rich.enter_log(f"Парсинг А: {Path(self.path_a).name}, лист {sheet}")
            recs_a = parse_sheet(self.path_a, sheet)

            Rich.enter_log(f"Парсинг Б: {Path(self.path_b).name}, лист {sheet}")
            recs_b = parse_sheet(self.path_b, sheet)

        except Exception as e:
            Rich.log_error("Ошибка при чтении/парсинге", str(e))
            QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать файл:\n{e}")
            return

        Rich.simple_log(f"Исходный: {len(recs_a)} записей, Для сравнения: {len(recs_b)} записей")

        changes = diff(recs_a, recs_b)

        added = sum(1 for c in changes if c.kind == 'added')
        removed = sum(1 for c in changes if c.kind == 'removed')
        changed = sum(1 for c in changes if c.kind == 'changed')

        self.fill_table(changes)

        self.lbl_summary.setText(
            f"Записей А: {len(recs_a)}, Б: {len(recs_b)} | "
            f"Различий: {len(changes)} "
            f"(добавлено {added}, удалено {removed}, изменено {changed})"
        )
        Rich.success_log("Сравнение завершено")

    def fill_table(self, changes):
        self.table.setRowCount(0)

        for c in changes:
            row = self.table.rowCount()
            self.table.insertRow(row)

            group, day, pair, week = c.key
            week_ru = 'нечёт.' if week == 'odd' else 'чёт.'
            kind_ru = {'added': 'добавлено',
                       'removed': 'удалено',
                       'changed': 'изменено'}[c.kind]

            field_text = ''
            old_text = ''
            new_text = ''

            # Вспомогательная функция для сборки красивой строки
            def make_info_string(rec, highlight_field=None):
                if not rec:
                    return ""
                # Если поле выделено (изменилось), пишем "Поле: значение", иначе просто значение
                if highlight_field == 'subject':
                    subj = f"Предмет: {rec.subject}"
                else:
                    subj = rec.subject

                if highlight_field == 'lesson_type':
                    ltype = f"Тип: {rec.lesson_type}"
                else:
                    ltype = f"({rec.lesson_type})"

                if highlight_field == 'teacher':
                    teach = f"Препод: {rec.teacher}"
                else:
                    teach = rec.teacher

                if highlight_field == 'room':
                    room = f"Ауд: {rec.room}"
                else:
                    room = rec.room

                return f"{subj} {ltype} | {teach} | {room}"

            if c.kind == 'changed':
                field_ru = {
                    'subject': 'Предмет',
                    'lesson_type': 'Тип занятия',
                    'teacher': 'Преподаватель',
                    'room': 'Аудитория'
                }.get(c.field, c.field)
                field_text = field_ru

                # Собираем строку с выделением измененного поля
                old_text = make_info_string(c.record_a, c.field)
                new_text = make_info_string(c.record_b, c.field)

            elif c.kind == 'added':
                field_text = "Вся пара"
                if c.record_b:
                    new_text = make_info_string(c.record_b)

            elif c.kind == 'removed':
                field_text = "Вся пара"
                if c.record_a:
                    old_text = make_info_string(c.record_a)

            values = [
                kind_ru, group, day, str(pair), week_ru,
                field_text, old_text, new_text
            ]

            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                # Окрашивание
                if c.kind == 'added':
                    item.setBackground(QBrush(QColor("#1E4D2B")))
                    item.setForeground(QBrush(QColor("#A5D6A7")))
                elif c.kind == 'removed':
                    item.setBackground(QBrush(QColor("#4D1E1E")))
                    item.setForeground(QBrush(QColor("#EF9A9A")))
                elif c.kind == 'changed':
                    item.setBackground(QBrush(QColor("#4D3B1E")))
                    item.setForeground(QBrush(QColor("#FFCC80")))

                self.table.setItem(row, col, item)
