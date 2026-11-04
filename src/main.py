import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow
from gui.utils.windows_animations import AnimationsManager
from utils.output_rich import Rich


if __name__ == "__main__":
    App = QApplication(sys.argv)

    Rich.enter_log("Показ главного окна приложения")
    Rich.print_spacer()

    MainWin = MainWindow()
    MainWin.setWindowOpacity(0.0)
    MainWin.show()
    MainWin.fade_in_anim = AnimationsManager.window_appearance_animation(MainWin, 320)

    sys.exit(App.exec())
