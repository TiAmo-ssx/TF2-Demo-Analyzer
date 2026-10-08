import os
import sys


def _setup_std_streams():
    """
    PyInstaller 窗口模式（console=False）下，
    sys.stdout / sys.stderr 是 None。

    Flask / Werkzeug 会往 stderr 写日志，
    若不重定向会导致崩溃。
    """

    if sys.stdout is None:
        sys.stdout = open(
            os.devnull,
            "w",
            encoding="utf-8"
        )

    if sys.stderr is None:
        sys.stderr = open(
            os.devnull,
            "w",
            encoding="utf-8"
        )


def main():
    """程序入口"""

    _setup_std_streams()

    from gui.main_window import MainWindow

    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
