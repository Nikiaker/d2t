"""Main window wiring the four views together."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from .data import ScoringFile
from .views import DetailView, DomainView, FileView, InstanceListView


class ScoringApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Triples-to-text human scoring")
        self.resize(1200, 860)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.domain_view = DomainView()
        self.file_view = FileView()
        self.list_view = InstanceListView()
        self.detail_view = DetailView()

        self.stack.addWidget(self.domain_view)   # 0
        self.stack.addWidget(self.file_view)     # 1
        self.stack.addWidget(self.list_view)     # 2
        self.stack.addWidget(self.detail_view)   # 3

        self.domain_view.chosen.connect(self._open_domain)
        self.file_view.back.connect(lambda: self.stack.setCurrentIndex(0))
        self.file_view.chosen.connect(self._open_file)
        self.list_view.back.connect(lambda: self.stack.setCurrentIndex(1))
        self.list_view.open_instance.connect(self._open_instance)
        self.detail_view.back.connect(self._back_to_list)
        self.detail_view.saved.connect(self.list_view.refresh)

        self.stack.setCurrentIndex(0)

    def _open_domain(self, domain: str):
        self.file_view.show_domain(domain)
        self.stack.setCurrentIndex(1)

    def _open_file(self, domain: str, path: str):
        self.list_view.scoring = ScoringFile(path)
        self.list_view.refresh()
        self.detail_view.scoring = self.list_view.scoring
        self.stack.setCurrentIndex(2)

    def _open_instance(self, index: int):
        self.detail_view.open(index)
        self.stack.setCurrentIndex(3)

    def _back_to_list(self):
        self.list_view.refresh()
        self.stack.setCurrentIndex(2)


STYLE = """
QPushButton { padding: 8px 16px; }
QGroupBox { font-weight: bold; margin-top: 12px; padding: 8px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; }
QLabel h2 { }
"""


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv if argv is None else ["scoring_gui"] + argv)
    check_only = "--check" in argv
    app = QApplication(argv)
    app.setStyleSheet(STYLE)
    if check_only:
        import PySide6
        from PySide6.QtCore import qVersion
        print(f"PySide6 {PySide6.__version__} / Qt {qVersion()} — environment OK")
        return 0
    window = ScoringApp()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
