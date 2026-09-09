"""Qt views: domain picker, file picker, instance list, instance detail."""

from __future__ import annotations

import json
import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from .data import DOMAINS, GUIDELINES_PATH, SCORE_COLUMNS, SCORE_LABELS, ScoringFile, list_scoring_files
from .renderers import SourceWidget


class GuidelinesDialog(QDialog):
    """Modal viewer for guidelines.md."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Scoring guidelines")
        self.resize(900, 650)
        layout = QVBoxLayout(self)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        try:
            with open(GUIDELINES_PATH, encoding="utf-8") as fh:
                content = fh.read()
            self.browser.setMarkdown(content)
            if not self.browser.toPlainText().strip():
                self.browser.setPlainText(content)
        except OSError as exc:
            self.browser.setPlainText(
                f"Guidelines file not found at:\n{GUIDELINES_PATH}\n\n({exc})"
            )
        layout.addWidget(self.browser)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(close_btn)
        layout.addLayout(row)


class DomainView(QWidget):
    chosen = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addStretch(2)
        title = QLabel("<h1>Human scoring</h1>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        subtitle = QLabel("Choose a domain to begin")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        layout.addStretch(1)
        box = QVBoxLayout()
        box.setSpacing(12)
        for domain in DOMAINS:
            btn = QPushButton(domain)
            btn.setMinimumHeight(52)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _=False, d=domain: self.chosen.emit(d))
            box.addWidget(btn)
        holder = QWidget()
        holder.setLayout(box)
        holder.setMaximumWidth(420)
        wrap = QHBoxLayout()
        wrap.addStretch(1)
        wrap.addWidget(holder)
        wrap.addStretch(1)
        layout.addLayout(wrap)
        layout.addStretch(3)


class FileView(QWidget):
    chosen = Signal(str, str)  # domain, path
    back = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.domain = ""
        layout = QVBoxLayout(self)
        self.title = QLabel()
        self.title.setTextFormat(Qt.RichText)
        layout.addStretch(2)
        layout.addWidget(self.title)
        layout.addStretch(1)
        self.box = QVBoxLayout()
        self.box.setSpacing(12)
        holder = QWidget()
        holder.setLayout(self.box)
        holder.setMaximumWidth(560)
        wrap = QHBoxLayout()
        wrap.addStretch(1)
        wrap.addWidget(holder)
        wrap.addStretch(1)
        layout.addLayout(wrap)
        layout.addStretch(2)
        back_btn = QPushButton("← Back to domains")
        back_btn.clicked.connect(self.back.emit)
        bl = QHBoxLayout()
        bl.addStretch(1)
        bl.addWidget(back_btn)
        bl.addStretch(1)
        layout.addLayout(bl)

    def show_domain(self, domain: str):
        self.domain = domain
        self.title.setText(f"<h2>Domain: {domain}</h2><p>Choose a scoring file:</p>")
        while self.box.count():
            item = self.box.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for label, path in list_scoring_files(domain):
            btn = QPushButton(label)
            btn.setMinimumHeight(44)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _=False, p=path: self.chosen.emit(domain, p))
            self.box.addWidget(btn)


class _ActivateTable(QTableWidget):
    activated = Signal()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.activated.emit()


class InstanceListView(QWidget):
    open_instance = Signal(int)
    back = Signal()

    COLUMNS = ["ID", "Text<br>Summary", "Text<br>Faithfulness",
               "Triples<br>Additions", "Triples<br>Omissions", "Evaluated"]

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.scoring: ScoringFile | None = None
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.header = QLabel()
        self.header.setTextFormat(Qt.RichText)
        top.addWidget(self.header)
        top.addStretch(1)
        back_btn = QPushButton("← Files")
        back_btn.clicked.connect(self.back.emit)
        top.addWidget(back_btn)
        layout.addLayout(top)
        self.progress = QLabel()
        layout.addWidget(self.progress)
        self.table = _ActivateTable(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels([c.replace("<br>", " ") for c in self.COLUMNS])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.doubleClicked.connect(self._on_activate)
        self.table.activated.connect(lambda: self._activate_row(self.table.currentRow()))
        layout.addWidget(self.table)
        bottom = QHBoxLayout()
        bottom.addStretch(1)
        self.continue_btn = QPushButton("Continue with first unevaluated →")
        self.continue_btn.clicked.connect(self._continue)
        bottom.addWidget(self.continue_btn)
        layout.addLayout(bottom)

    def _on_activate(self, _index):
        self._activate_row(self.table.currentRow())

    def _activate_row(self, row: int):
        if self.scoring is not None and 0 <= row < len(self.scoring.rows):
            self.open_instance.emit(row)

    def _continue(self):
        if self.scoring is None:
            return
        for i in range(len(self.scoring.rows)):
            if not self.scoring.is_evaluated(i):
                self.open_instance.emit(i)
                return

    def refresh(self):
        scoring = self.scoring
        if scoring is None:
            return
        path = scoring.path
        domain = os.path.basename(os.path.dirname(path))
        fname = os.path.basename(path)[: -len("_scoring.csv")]
        self.header.setText(f"<h2>{domain} — {fname}</h2>")
        self.table.setRowCount(len(scoring.rows))
        for r, row in enumerate(scoring.rows):
            cells = [row.get("instance_id", str(r))]
            cells += [scoring.scores(r)[col] or "—" for col in SCORE_COLUMNS]
            cells.append("✓" if scoring.is_evaluated(r) else "")
            for c, val in enumerate(cells):
                item = QTableWidgetItem(val)
                if c == 0:
                    item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(r, c, item)
        self.progress.setText(f"Evaluated: {scoring.evaluated_count()} / {len(scoring.rows)}")
        for c in range(1, 5):
            self.table.resizeColumnToContents(c)
        self.table.setColumnWidth(5, 90)
        self.table.horizontalHeader().setStretchLastSection(True)


class DetailView(QWidget):
    saved = Signal()
    back = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.scoring: ScoringFile | None = None
        self.index = -1
        self._loaded_values: dict[str, str] = {}

        root = QVBoxLayout(self)
        self.title = QLabel()
        self.title.setTextFormat(Qt.RichText)
        root.addWidget(self.title)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: green;")
        root.addWidget(self.status_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        root.addWidget(self.scroll, stretch=1)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(8, 8, 16, 8)
        self.scroll.setWidget(self.content)

        score_box = QGroupBox("Scores (1 = worst … 5 = best)")
        form = QFormLayout(score_box)
        form.setLabelAlignment(Qt.AlignRight)
        self.combos: dict[str, QComboBox] = {}
        for col in SCORE_COLUMNS:
            group, name, hint = SCORE_LABELS[col]
            combo = QComboBox()
            combo.addItems([""] + [str(i) for i in range(1, 6)])
            combo.setMinimumWidth(80)
            combo.setToolTip(hint)
            self.combos[col] = combo
            form.addRow(f"{name} <i>({group})</i>:", combo)
        root.addWidget(score_box)

        buttons = QHBoxLayout()
        self.prev_btn = QPushButton("← Previous")
        self.next_btn = QPushButton("Next →")
        self.return_btn = QPushButton("Return to list")
        self.guidelines_btn = QPushButton("Guidelines")
        self.save_btn = QPushButton("Save")
        self.save_btn.setDefault(True)
        self.prev_btn.clicked.connect(self._prev)
        self.next_btn.clicked.connect(self._next)
        self.return_btn.clicked.connect(self._return)
        self.guidelines_btn.clicked.connect(self._show_guidelines)
        self.save_btn.clicked.connect(self._save)
        buttons.addWidget(self.return_btn)
        buttons.addStretch(1)
        buttons.addWidget(self.guidelines_btn)
        buttons.addWidget(self.save_btn)
        buttons.addWidget(self.prev_btn)
        buttons.addWidget(self.next_btn)
        root.addLayout(buttons)

    # ------------------------------------------------------------------ loading

    def load(self, index: int):
        assert self.scoring is not None
        self.index = index
        row = self.scoring.row(index)
        self._clear_content()

        self.title.setText(
            f"<h2>Instance {row.get('instance_id', index)}</h2>"
            f"<i>Row {index + 1} of {len(self.scoring.rows)}</i>"
        )

        self._add_section("Original structured data")
        try:
            data = json.loads(row.get("input_data") or "")
        except json.JSONDecodeError:
            data = None
        source = SourceWidget(self._domain(), data)
        self.content_layout.addWidget(source)

        self._add_section("Reference text")
        text = QLabel(row.get("generated_text", ""))
        text.setWordWrap(True)
        text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.content_layout.addWidget(text)

        self._add_section("Semantic triples")
        triples = QLabel(
            "<br>".join(t.strip() for t in (row.get("generated_triples") or "").split(";"))
        )
        triples.setFont(QFont("monospace"))
        triples.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.content_layout.addWidget(triples)
        self.content_layout.addStretch(1)

        self._loaded_values = self.scoring.scores(index)
        for col, combo in self.combos.items():
            combo.setCurrentText(self._loaded_values[col] or "")

        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setEnabled(index < len(self.scoring.rows) - 1)
        self.scroll.verticalScrollBar().setValue(0)

    def _domain(self) -> str:
        subdir = os.path.basename(os.path.dirname(self.scoring.path))
        for name, directory in DOMAINS.items():
            if directory == subdir:
                return name
        return subdir

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _add_section(self, title: str):
        label = QLabel(f"<h3>{title}</h3>")
        self.content_layout.addWidget(label)

    # ------------------------------------------------------------------ actions

    def _dirty(self) -> bool:
        current = {col: combo.currentText() for col, combo in self.combos.items()}
        return current != {k: (v or "") for k, v in self._loaded_values.items()}

    def _show_guidelines(self):
        GuidelinesDialog(self).exec()

    def _save(self):
        scores = {col: combo.currentText() for col, combo in self.combos.items()}
        self.scoring.save_scores(self.index, scores)
        self._loaded_values = {k: (v or "") for k, v in scores.items()}
        self.saved.emit()
        self.status_label.setText(f"Saved scores for instance "
                                  f"{self.scoring.row(self.index).get('instance_id', self.index)}.")

    def _confirm_discard(self) -> bool:
        """Returns True if it is safe to leave the instance."""
        if not self._dirty():
            return True
        choice = QMessageBox.question(
            self, "Unsaved scores",
            "You changed scores but did not save them.",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )
        if choice == QMessageBox.Save:
            self._save()
            return True
        return choice == QMessageBox.Discard

    def _prev(self):
        if self._confirm_discard():
            self.load(self.index - 1)

    def _next(self):
        if self._confirm_discard():
            self.load(self.index + 1)

    def _return(self):
        if self._confirm_discard():
            self.back.emit()

    def open(self, index: int):
        self.load(index)
