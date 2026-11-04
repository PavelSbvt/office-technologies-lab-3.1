from PyQt6.QtCore import QPoint, QThread, Qt
from PyQt6.QtGui import QCloseEvent, QKeyEvent, QMouseEvent, QResizeEvent
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QMainWindow, QMessageBox, QWidget)
from PyQt6.uic import loadUi


class MainWindow(QWidget):
    """
    Класс для ui окна на PyQt6 для
    """
    def __init__(self):
        """
        Создаёт главное окно, загружает интерфейс и подключает сигналы.
        """

        super().__init__()

        self.setObjectName("MainWindow")
        self.setMinimumSize(900, 650)
        self.setWindowTitle("Офисные технологии - лабораторная работа 3.1")


