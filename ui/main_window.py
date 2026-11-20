from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QMessageBox, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QAbstractItemView
)
from PySide6.QtCore import Qt

from core.encryption import (
    DEFAULT_MAPPING, load_mapping, save_mapping,
    validate_mapping, encrypt_text, decrypt_text
)


STYLE = """
QMainWindow, QDialog { background-color: #101827; }
QLabel { color: #f8fafc; font-size: 14px; }
QTextEdit {
    background-color: #1e293b; color: #ffffff;
    border: 1px solid #475569; border-radius: 8px;
    padding: 12px; font-size: 16px;
}
QPushButton {
    background-color: #6366f1; color: white;
    padding: 10px 14px; border: 0; border-radius: 8px;
    font-size: 13px; font-weight: bold;
}
QPushButton:hover { background-color: #818cf8; }
QTableWidget {
    background-color: #1e293b; color: white;
    gridline-color: #475569; border: 1px solid #475569;
    alternate-background-color: #263449;
}
QTableWidget QHeaderView::section {
    background-color: #334155; color: white;
    padding: 8px; border: 0; font-weight: bold;
}
QTableWidget::item { padding: 5px; }
"""


class MappingEditor(QDialog):
    def __init__(self, current_mapping, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Your Language Mapping")
        self.resize(590, 700)
        self.setMinimumSize(500, 520)
        self.setStyleSheet(STYLE)
        self.mapping = None

        layout = QVBoxLayout(self)
        heading = QLabel("CUSTOM LANGUAGE MAPPING")
        heading.setStyleSheet("font-size: 21px; color: #818cf8; font-weight: bold;")
        info = QLabel(
            "Map English letters, lowercase letters, numbers or symbols "
            "to your own characters. Example: A → ව, 7 → ෭, @ → ඞ."
        )
        info.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(info)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Original Character", "Your Character"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

        for source, replacement in current_mapping.items():
            self.add_mapping_row(source, replacement)

        controls = QHBoxLayout()
        add_btn = QPushButton("+ ADD")
        remove_btn = QPushButton("REMOVE SELECTED")
        reset_btn = QPushButton("RESET DEFAULT")
        add_btn.clicked.connect(self.add_empty_row)
        remove_btn.clicked.connect(self.remove_selected_rows)
        reset_btn.clicked.connect(self.reset_defaults)
        controls.addWidget(add_btn)
        controls.addWidget(remove_btn)
        controls.addStretch()
        controls.addWidget(reset_btn)
        layout.addLayout(controls)

        dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        dialog_buttons.accepted.connect(self.save_changes)
        dialog_buttons.rejected.connect(self.reject)
        layout.addWidget(dialog_buttons)

    def add_mapping_row(self, source="", replacement=""):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(source))
        self.table.setItem(row, 1, QTableWidgetItem(replacement))

    def add_empty_row(self):
        self.add_mapping_row("", "")
        self.table.setCurrentCell(self.table.rowCount() - 1, 0)
        self.table.editItem(self.table.item(self.table.rowCount() - 1, 0))

    def remove_selected_rows(self):
        rows = sorted({index.row() for index in self.table.selectionModel().selectedRows()},
                      reverse=True)
        if not rows:
            QMessageBox.information(self, "Remove", "Select a row to remove first.")
            return
        for row in rows:
            self.table.removeRow(row)

    def reset_defaults(self):
        self.table.setRowCount(0)
        for source, replacement in DEFAULT_MAPPING.items():
            self.add_mapping_row(source, replacement)

    def save_changes(self):
        # Commit any active cell editor before reading table items
        self.table.clearFocus()
        mapping = {}
        for row in range(self.table.rowCount()):
            source_item = self.table.item(row, 0)
            replacement_item = self.table.item(row, 1)
            source = source_item.text() if source_item else ""
            replacement = replacement_item.text() if replacement_item else ""

            if not source.strip() and not replacement.strip():
                continue
            if not source.strip() or not replacement.strip():
                QMessageBox.warning(
                    self, "Incomplete Row",
                    f"Please complete both columns in row {row + 1}, or remove that row."
                )
                return
            if source in mapping:
                QMessageBox.warning(
                    self, "Duplicate Original",
                    f'"{source}" appears more than once. Each original entry must be unique.'
                )
                return
            mapping[source] = replacement

        error = validate_mapping(mapping)
        if error:
            QMessageBox.warning(self, "Invalid Mapping", error)
            return

        self.mapping = mapping
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mapping = load_mapping()
        self.setWindowTitle("My Language Encryption")
        self.resize(1050, 850)
        self.setMinimumSize(760, 650)
        self.setStyleSheet(STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(14)

        title = QLabel("MY LANGUAGE ENCRYPTION")
        title.setStyleSheet("font-size: 27px; color: #8186ff; font-weight: bold;")
        subtitle = QLabel("Convert your text into your own language")

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter your original text here...")

        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Your result will appear here...")
        self.output_text.setReadOnly(True)

        encrypt_btn = QPushButton("ENCRYPT")
        decrypt_btn = QPushButton("DECRYPT")
        copy_btn = QPushButton("COPY")
        clear_btn = QPushButton("CLEAR")
        edit_btn = QPushButton("EDIT LANGUAGE")

        encrypt_btn.clicked.connect(self.encrypt)
        decrypt_btn.clicked.connect(self.decrypt)
        copy_btn.clicked.connect(self.copy_result)
        clear_btn.clicked.connect(self.clear_all)
        edit_btn.clicked.connect(self.edit_mapping)

        row = QHBoxLayout()
        for button in (encrypt_btn, decrypt_btn, copy_btn, clear_btn):
            row.addWidget(button)

        edit_row = QHBoxLayout()
        edit_row.addWidget(edit_btn)
        edit_row.addStretch()

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(QLabel("INPUT TEXT"))
        layout.addWidget(self.input_text, 1)
        layout.addLayout(row)
        layout.addLayout(edit_row)
        layout.addWidget(QLabel("OUTPUT TEXT"))
        layout.addWidget(self.output_text, 1)

        footer = QLabel("Custom Language Encryption System | Python")
        footer.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(footer)

    def encrypt(self):
        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Warning", "Enter some text first.")
            return
        self.output_text.setPlainText(encrypt_text(text, self.mapping))

    def decrypt(self):
        text = self.input_text.toPlainText()
        if not text.strip():
            text = self.output_text.toPlainText()
            if not text.strip():
                QMessageBox.warning(self, "Warning", "Enter encrypted text first.")
                return
            self.input_text.setPlainText(text)
        self.output_text.setPlainText(decrypt_text(text, self.mapping))

    def copy_result(self):
        result = self.output_text.toPlainText()
        if not result:
            QMessageBox.information(self, "Copy", "There is no output to copy.")
            return
        QApplication.clipboard().setText(result)
        QMessageBox.information(self, "Copied", "Output copied successfully.")

    def clear_all(self):
        self.input_text.clear()
        self.output_text.clear()

    def edit_mapping(self):
        dialog = MappingEditor(self.mapping, self)
        if dialog.exec():
            self.mapping = dialog.mapping
            save_mapping(self.mapping)
            QMessageBox.information(
                self, "Mapping Saved",
                "Your custom language mapping has been saved and is now active."
            )
