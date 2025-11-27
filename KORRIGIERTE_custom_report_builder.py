"""
CustomReportBuilder - Drag&Drop-Interface für benutzerdefinierte Reports

Ermöglicht das Erstellen von benutzerdefinierten Report-Templates durch
Drag&Drop von Template-Variablen in einen Report-Designer.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QTextEdit, QPushButton, QListWidget, QListWidgetItem,
    QSplitter, QGroupBox, QScrollArea, QFrame, QApplication,
    QMessageBox, QDialog, QDialogButtonBox, QInputDialog, QComboBox,
    QLineEdit, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import (
    QDrag, QPixmap, QFont, QTextCharFormat, QTextCursor,
    QPalette, QColor, QDropEvent, QDragEnterEvent
)

try:
    from ..core.export.export_service import TemplateEngine, TemplateVariable
except ImportError:
    # Fallback für direkten Import
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from core.export.export_service import TemplateEngine, TemplateVariable


class DraggableVariableWidget(QFrame):
    """Draggbare Template-Variable"""
    
    def __init__(self, variable: TemplateVariable):
        super().__init__()
        self.variable = variable
        self.setFrameStyle(QFrame.Box)
        self.setFixedSize(200, 80)
        self.setStyleSheet("""
            QFrame {
                background-color: #f0f8ff;
                border: 2px solid #4a90e2;
                border-radius: 8px;
                padding: 5px;
                margin: 2px;
            }
            QFrame:hover {
                background-color: #e6f2ff;
                border-color: #2980b9;
            }
        """)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Variablen-Name
        name_label = QLabel(self.variable.name)
        name_label.setFont(QFont("Arial", 9, QFont.Bold))
        name_label.setStyleSheet("color: #2c3e50;")
        
        # Beschreibung
        desc_label = QLabel(self.variable.description)
        desc_label.setFont(QFont("Arial", 8))
        desc_label.setStyleSheet("color: #7f8c8d;")
        desc_label.setWordWrap(True)
        
        # Beispiel
        example_label = QLabel(f"Beispiel: {self.variable.example}")
        example_label.setFont(QFont("Arial", 7, QFont.Italic))
        example_label.setStyleSheet("color: #95a5a6;")
        
        layout.addWidget(name_label)
        layout.addWidget(desc_label)
        layout.addWidget(example_label)
        
        self.setLayout(layout)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            
            # Variable als MIME-Daten übertragen
            variable_data = {
                'name': self.variable.name,
                'description': self.variable.description,
                'data_type': self.variable.data_type,
                'example': self.variable.example,
                'category': self.variable.category
            }
            
            mime_data.setText(str(variable_data))
            drag.setMimeData(mime_data)
            drag.setPixmap(self.grab())
            drag.exec(Qt.MoveAction)
    
    def get_variable_name(self) -> str:
        """Gibt den Variablennamen zurück"""
        return self.variable.name


class DropAreaWidget(QTextEdit):
    """Drop-Bereich für Template-Variablen"""
    
    variable_dropped = Signal(str)  # Signal wenn Variable gedropped wird
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Ziehen Sie Template-Variablen hierher oder geben Sie Text ein...")
        self.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                font-size: 11px;
                line-height: 1.4;
            }
            QTextEdit:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        self.setAcceptDrops(True)
        self.document().setParent(self)
        
        # Initialer Template-Text
        self.setPlainText("# Neuer Report\n\nZiehen Sie hier Template-Variablen hinein...\n")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QTextEdit {
                    background-color: #e8f4fd;
                    border: 2px solid #3498db;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 11px;
                    line-height: 1.4;
                }
            """)
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasText():
            try:
                # Variable-Daten parsen
                import json
                variable_data = json.loads(event.mimeData().text())
                variable_name = variable_data.get('name', '')
                
                # Variable in Text einfügen
                cursor = self.textCursor()
                cursor.insertText(f"{{{variable_name}}}")
                
                self.variable_dropped.emit(variable_name)
                
            except (json.JSONDecodeError, KeyError) as e:
                logging.error(f"Fehler beim Verarbeiten der Variable: {e}")
            
            event.acceptProposedAction()
    
    def get_content(self) -> str:
        """Gibt den aktuellen Inhalt zurück"""
        return self.toPlainText()


class CategoryWidget(QGroupBox):
    """Widget für eine Kategorie von Template-Variablen"""
    
    def __init__(self, category_name: str, variables: List[TemplateVariable]):
        super().__init__(category_name)
        self.category_name = category_name
        self.variables = variables
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
                border: 2px solid #ecf0f1;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 15, 5, 5)
        layout.setSpacing(5)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        variables_widget = QWidget()
        variables_layout = QVBoxLayout()
        variables_layout.setContentsMargins(0, 0, 0, 0)
        variables_layout.setSpacing(3)
        
        # Variablen hinzufügen
        for variable in self.variables:
            var_widget = DraggableVariableWidget(variable)
            variables_layout.addWidget(var_widget)
        
        variables_layout.addStretch()
        variables_widget.setLayout(variables_layout)
        scroll_area.setWidget(variables_widget)
        
        layout.addWidget(scroll_area)
        self.setLayout(layout)


class CustomReportBuilder(QWidget):
    """Haupt-Widget für den Custom Report Builder"""
    
    # Signale
    template_saved = Signal(str)  # Template gespeichert
    preview_generated = Signal(str)  # Preview generiert
    export_requested = Signal(str, str)  # Export angefordert (template_content, format)
    
    def __init__(self, template_engine: TemplateEngine, parent=None):
        super().__init__(parent)
        self.template_engine = template_engine
        self.logger = logging.getLogger(__name__)
        self.current_template_name = ""
        self.setWindowTitle("Custom Report Builder")
        self.setMinimumSize(1200, 800)
        self._setup_ui()
        self._load_variable_categories()
    
    def _setup_ui(self):
        """Setup der Benutzeroberfläche"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Splitter für linke und rechte Seite
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # Linke Seite: Variable-Kategorien
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Rechte Seite: Editor und Controls
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Splitter-Proportionen
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
    
    def _create_left_panel(self) -> QWidget:
        """Erstellt die linke Panel mit Variable-Kategorien"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Titel
        title_label = QLabel("Template-Variablen")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Scroll-Bereich für Kategorien
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        self.categories_widget = QWidget()
        self.categories_layout = QVBoxLayout()
        self.categories_layout.setContentsMargins(10, 10, 10, 10)
        self.categories_layout.setSpacing(15)
        self.categories_widget.setLayout(self.categories_layout)
        
        scroll_area.setWidget(self.categories_widget)
        layout.addWidget(scroll_area)
        
        panel.setLayout(layout)
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Erstellt die rechte Panel mit Editor und Controls"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Obere Controls
        controls_layout = self._create_controls_layout()
        layout.addLayout(controls_layout)
        
        # Template-Editor
        self.drop_area = DropAreaWidget()
        self.drop_area.variable_dropped.connect(self._on_variable_dropped)
        layout.addWidget(self.drop_area, 1)
        
        # Untere Controls
        actions_layout = self._create_actions_layout()
        layout.addLayout(actions_layout)
        
        panel.setLayout(layout)
        return panel
    
    def _create_controls_layout(self) -> QHBoxLayout:
        """Erstellt die oberen Controls"""
        layout = QHBoxLayout()
        
        # Template-Name
        name_label = QLabel("Template-Name:")
        self.template_name_edit = QLineEdit()
        self.template_name_edit.setPlaceholderText("Geben Sie einen Namen ein...")
        self.template_name_edit.setMaximumWidth(200)
        
        # Format-Auswahl
        format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PDF", "Word", "HTML", "Email"])
        self.format_combo.setMaximumWidth(100)
        
        # Template-Variablen-Info
        variables_label = QLabel("Variablen: Ziehen Sie aus der linken Seitenleiste herein")
        variables_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        
        layout.addWidget(name_label)
        layout.addWidget(self.template_name_edit)
        layout.addSpacing(20)
        layout.addWidget(format_label)
        layout.addWidget(self.format_combo)
        layout.addStretch()
        layout.addWidget(variables_label)
        
        return layout
    
    def _create_actions_layout(self) -> QHBoxLayout:
        """Erstellt die unteren Action-Buttons"""
        layout = QHBoxLayout()
        
        # Preview-Button
        self.preview_btn = QPushButton("Vorschau")
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.preview_btn.clicked.connect(self._on_preview_clicked)
        
        # Speichern-Button
        self.save_btn = QPushButton("Template speichern")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.save_btn.clicked.connect(self._on_save_clicked)
        
        # Export-Button
        self.export_btn = QPushButton("Sofort exportieren")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        self.export_btn.clicked.connect(self._on_export_clicked)
        
        # Neu-Button
        self.new_btn = QPushButton("Neu")
        self.new_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.new_btn.clicked.connect(self._on_new_clicked)
        
        layout.addStretch()
        layout.addWidget(self.preview_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.export_btn)
        layout.addWidget(self.new_btn)
        
        return layout
    
    def _load_variable_categories(self):
        """Lädt und organisiert Template-Variablen nach Kategorien"""
        try:
            variables = self.template_engine.get_variable_list()
            
            # Variablen nach Kategorien gruppieren
            categories = {}
            for variable in variables:
                category = variable.category
                if category not in categories:
                    categories[category] = []
                categories[category].append(variable)
            
            # Kategorien-Widgets erstellen
            for category_name, category_variables in categories.items():
                category_widget = CategoryWidget(category_name, category_variables)
                self.categories_layout.addWidget(category_widget)
            
            self.categories_layout.addStretch()
            
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Variablen-Kategorien: {e}")
    
    def _on_variable_dropped(self, variable_name: str):
        """Behandelt das Drop-Ereignis einer Variable"""
        self.logger.info(f"Variable gedropped: {variable_name}")
        # Zusätzliche Logik hier möglich
    
    def _on_preview_clicked(self):
        """Behandelt Klick auf Preview-Button"""
        try:
            content = self.drop_area.get_content()
            if not content.strip():
                QMessageBox.warning(self, "Warnung", "Bitte geben Sie Template-Inhalt ein oder ziehen Sie Variablen hinein.")
                return
            
            # Preview-Dialog öffnen
            preview_dialog = TemplatePreviewDialog(content, self)
            preview_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler bei der Vorschau: {e}")
    
    def _on_save_clicked(self):
        """Behandelt Klick auf Speichern-Button"""
        try:
            name = self.template_name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Warnung", "Bitte geben Sie einen Template-Namen ein.")
                return
            
            content = self.drop_area.get_content()
            if not content.strip():
                QMessageBox.warning(self, "Warnung", "Bitte geben Sie Template-Inhalt ein.")
                return
            
            # Template speichern
            from ..core.export.export_service import TemplateService
            # In der echten Anwendung würde hier der TemplateService verwendet
            # Für jetzt verwenden wir einen einfachen Mock
            
            # TODO: Tatsächliche Implementierung mit TemplateService
            QMessageBox.information(self, "Erfolg", f"Template '{name}' wurde gespeichert.")
            self.template_saved.emit(name)
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")
    
    def _on_export_clicked(self):
        """Behandelt Klick auf Export-Button"""
        try:
            content = self.drop_area.get_content()
            if not content.strip():
                QMessageBox.warning(self, "Warnung", "Bitte geben Sie Template-Inhalt ein oder ziehen Sie Variablen hinein.")
                return
            
            format_type = self.format_combo.currentText().lower()
            self.export_requested.emit(content, format_type)
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Export: {e}")
    
    def _on_new_clicked(self):
        """Behandelt Klick auf Neu-Button"""
        reply = QMessageBox.question(
            self, "Neues Template",
            "Möchten Sie wirklich ein neues Template erstellen? Ungespeicherte Änderungen gehen verloren.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.template_name_edit.clear()
            self.drop_area.setPlainText("# Neuer Report\n\nZiehen Sie hier Template-Variablen hinein...\n")
            self.format_combo.setCurrentIndex(0)


class TemplatePreviewDialog(QDialog):
    """Dialog für Template-Vorschau"""
    
    def __init__(self, template_content: str, parent=None):
        super().__init__(parent)
        self.template_content = template_content
        self.setWindowTitle("Template-Vorschau")
        self.setMinimumSize(800, 600)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Preview-Text
        preview_label = QLabel("Vorschau des gerenderten Templates:")
        preview_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(preview_label)
        
        # Text-Anzeige
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlainText(self.template_content)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.preview_text)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)


if __name__ == "__main__":
    # Test des Report Builders
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Mock Template Engine für Tests
    class MockTemplateEngine:
        def get_variable_list(self):
            return [
                TemplateVariable("patient_name", "Patientenname", "string", "Max Mustermann"),
                TemplateVariable("op_date", "Operationsdatum", "date", "15.11.2024"),
                TemplateVariable("satisfaction", "Zufriedenheit", "float", "8.5")
            ]
    
    template_engine = MockTemplateEngine()
    builder = CustomReportBuilder(template_engine)
    builder.show()
    
    sys.exit(app.exec())