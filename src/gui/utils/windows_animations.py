from PyQt6.QtCore import QPropertyAnimation,QEasingCurve
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget

from utils.output_rich import Rich


class AnimationsManager:
    """
    Класс для функций анимации появления/исчезания окна
    """

    @staticmethod
    def window_appearance_animation(
            window_name: QWidget,
            duration: int = 250
            ) -> QPropertyAnimation:
        """
        Функция для анимирования появления основного окна приложения. Анимирует
        плавное появление окна.

        :param window_name: принимает ссылку объект окна
        :param duration: int - принимает время длительности анимации в миллисекундах

        :return: QPropertyAnimation
        """

        Rich.debug_log(f"Запуск анимации появления окна '{window_name.objectName()}'")

        fade_in = QPropertyAnimation(window_name, b"windowOpacity")
        fade_in.setDuration(duration)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        fade_in.start()

        return fade_in

    @staticmethod
    def animation_of_window_disappearing(
            window_name: QWidget,
            duration: int = 200
            ) -> QPropertyAnimation:
        """
        Функция для анимирования исчезновения основного окна приложения.
        Анимирует плавное исчезновение окна.

        :param window_name: принимает ссылку объект окна
        :param duration: int - принимает время длительности анимации в миллисекундах

        :return: QPropertyAnimation
        """

        fade_anim = QPropertyAnimation(window_name, b"windowOpacity")
        fade_anim.setDuration(duration)
        fade_anim.setStartValue(1.0)
        fade_anim.setEndValue(0.0)
        fade_anim.setEasingCurve(QEasingCurve.Type.InCubic)

        fade_anim.finished.connect(window_name.close)

        fade_anim.start()

        return fade_anim
