from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QFileDialog, QMessageBox, QTableWidgetItem,
)
from PyQt6.uic import loadUi

from parser.parser import parse_sheet
from core.diff import diff
from utils.output_rich import Rich


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setMinimumSize(1100, 700)
        self.setWindowTitle("Офисные технологии — ЛР 3.1: сравнение расписаний")

        self.path_a: str = ""
        self.path_b: str = ""

        ui_path = Path("src/gui/ui/main-window.ui").as_posix()
        loadUi(ui_path, self)

        # подключаем сигналы
        self.btn_a.clicked.connect(self._pick_a)
        self.btn_b.clicked.connect(self._pick_b)
        self.btn_cmp.clicked.connect(self._compare)

        self.table.horizontalHeader().setStretchLastSection(True)

    # ---------- слоты ----------
    def _pick_a(self):
        p, _ = QFileDialog.getOpenFileName(
            self, "Файл A", "", "Excel (*.xls *.xlsx)")
        if p:
            self.path_a = p
            self.lbl_a.setText(Path(p).name)

    def _pick_b(self):
        p, _ = QFileDialog.getOpenFileName(
            self, "Файл B", "", "Excel (*.xls *.xlsx)")
        if p:
            self.path_b = p
            self.lbl_b.setText(Path(p).name)

    def _compare(self):
        if not self.path_a or not self.path_b:
            QMessageBox.warning(self, "Ошибка", "Выберите оба файла.")
            return
        sheet = self.edit_sheet.text().strip()
        if not sheet:
            QMessageBox.warning(self, "Ошибка", "Укажите имя листа.")
            return

        try:
            Rich.enter_log(f"Парсинг A: {Path(self.path_a).name}, лист {sheet}")
            recs_a = parse_sheet(self.path_a, sheet)
            Rich.enter_log(f"Парсинг B: {Path(self.path_b).name}, лист {sheet}")
            recs_b = parse_sheet(self.path_b, sheet)
        except Exception as e:
            Rich.log_error("Ошибка при чтении/парсинге", str(e))
            QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать файл:\n{e}")
            return

        Rich.simple_log(f"A: {len(recs_a)} записей, B: {len(recs_b)} записей")
        changes = diff(recs_a, recs_b)

        added = sum(1 for c in changes if c.kind == 'added')
        removed = sum(1 for c in changes if c.kind == 'removed')
        changed = sum(1 for c in changes if c.kind == 'changed')

        self._fill_table(changes)
        self.lbl_summary.setText(
            f"Записей A: {len(recs_a)}, B: {len(recs_b)} | "
            f"Различий: {len(changes)} "
            f"(добавлено {added}, удалено {removed}, изменено {changed})"
        )
        Rich.success_log("Сравнение завершено")

    def _fill_table(self, changes):
        self.table.setRowCount(0)
        for c in changes:
            row = self.table.rowCount()
            self.table.insertRow(row)
            group, day, pair, week, subgroup = c.key
            week_ru = 'нечёт.' if week == 'odd' else 'чёт.'
            kind_ru = {'added': 'добавлено',
                       'removed': 'удалено',
                       'changed': 'изменено'}[c.kind]

            values = [
                kind_ru, group, day, str(pair), week_ru,
                '' if subgroup is None else str(subgroup),
                c.field or '',
                c.old or '',
                c.new or '',
            ]
            for col, v in enumerate(values):
                item = QTableWidgetItem(v)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)
