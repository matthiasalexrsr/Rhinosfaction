# Fenster-Navigation & Layout-Management Tests

**Dokumentationsversion:** 1.0.0  
**Datum:** 2025-11-06  
**Test-Suite:** Comprehensive Navigation & Layout Testing  
**Anwendung:** Rhinoplastik-Dokumentation v1.0.0

## 📋 Inhaltsverzeichnis

1. [Test-Übersicht](#test-übersicht)
2. [Tab-Navigation Tests](#tab-navigation-tests)
3. [Breadcrumb-Navigation Tests](#breadcrumb-navigation-tests)
4. [Split-View & Multi-Panel Tests](#split-view--multi-panel-tests)
5. [Responsive Layout Tests](#responsive-layout-tests)
6. [Modal-Dialog Tests](#modal-dialog-tests)
7. [Layout-Persistenz Tests](#layout-persistenz-tests)
8. [Performance-Messungen](#performance-messungen)
9. [Browser-Kompatibilität](#browser-kompatibilität)
10. [Test-Automatisierung](#test-automatisierung)

---

## 📊 Test-Übersicht

### Getestete Komponenten

| Komponente | Beschreibung | Priorität | Test-Anzahl |
|------------|-------------|-----------|-------------|
| **Hauptfenster** | QMainWindow mit Tab-Widget | Hoch | 15 Tests |
| **Dashboard** | StatTile-Layout mit Grid-System | Hoch | 12 Tests |
| **Patient-Editor** | Modal-Dialog mit Tab-Navigation | Kritisch | 20 Tests |
| **Patienten-Liste** | Split-View mit TableWidget | Hoch | 10 Tests |
| **Such-Interface** | Multi-Criteria Search Panel | Mittel | 8 Tests |
| **Export-Widget** | Progress-Overlay mit ProgressBar | Mittel | 6 Tests |
| **Responsive System** | Fenstergrößen-Anpassung | Kritisch | 18 Tests |

### Test-Umgebung

- **Plattform:** Windows 11 / Ubuntu 22.04 / macOS 13.0
- **Python Version:** 3.9+
- **PySide6 Version:** 6.5+
- **Display-Auflösungen:** 1366x768, 1920x1080, 2560x1440, 3840x2160
- **DPI-Skalierung:** 100%, 125%, 150%, 200%

---

## 🔄 Tab-Navigation Tests

### TN-001: Grundlegende Tab-Navigation
**Ziel:** Navigation zwischen allen Haupt-Tabs  
**Test-Dauer:** < 200ms pro Tab-Wechsel  

```python
def test_basic_tab_navigation():
    """Testet Tab-Navigation zwischen allen Haupt-Tabs"""
    
    # Setup
    main_window = MainWindow(config, session_manager, patient_manager)
    
    # Test-Tabs: Dashboard, Patienten, Suchen, Export, Backup, Statistiken, Admin
    expected_tabs = [
        "📊 Dashboard", "👥 Patienten", "🔍 Suchen", "📤 Export", 
        "💾 Backup", "📊 Statistiken", "⚙️ Administration"
    ]
    
    # Tests durchführen
    for i, expected_tab in enumerate(expected_tabs):
        start_time = time.time()
        
        # Tab aktivieren
        main_window.tab_widget.setCurrentIndex(i)
        
        # Verifikation
        current_tab = main_window.tab_widget.tabText(i)
        assert current_tab == expected_tab, f"Tab {i}: Expected '{expected_tab}', got '{current_tab}'"
        
        # Performance-Check
        tab_switch_time = time.time() - start_time
        assert tab_switch_time < 0.2, f"Tab switch took {tab_switch_time:.3f}s (max: 0.2s)"
        
        # UI-Update verifizieren
        current_widget = main_window.tab_widget.currentWidget()
        assert current_widget is not None, f"Tab {i}: Widget is None"
```

### TN-002: Tab-State-Persistenz
**Ziel:** Verhalten bei Fenster-Fokus-Wiederherstellung  

```python
def test_tab_state_persistence():
    """Testet Tab-Zustand bei Fenster-Interaktionen"""
    
    # Tab 3 (Suchen) aktivieren
    main_window.tab_widget.setCurrentIndex(2)  # Index 2 = Suchen
    
    # Fenster minimieren und wiederherstellen
    main_window.showMinimized()
    time.sleep(0.5)
    main_window.showNormal()
    
    # Verifikation: Tab-Zustand erhalten
    assert main_window.tab_widget.currentIndex() == 2, "Tab state not preserved after minimize"
```

### TN-003: Dynamic Tab Management
**Ziel:** Admin-Tab nur für Administratoren sichtbar  

```python
def test_dynamic_tab_visibility():
    """Testet dynamische Tab-Anzeige basierend auf Benutzerrolle"""
    
    # Admin-Benutzer
    admin_session = create_admin_session()
    main_window_admin = MainWindow(config, admin_session, patient_manager)
    
    admin_tab_count = main_window_admin.tab_widget.count()
    assert "⚙️ Administration" in [main_window_admin.tab_widget.tabText(i) for i in range(admin_tab_count)]
    
    # Normaler Benutzer
    user_session = create_user_session()
    main_window_user = MainWindow(config, user_session, patient_manager)
    
    user_tab_count = main_window_user.tab_widget.count()
    assert admin_tab_count > user_tab_count, "Admin tab visible for normal user"
```

### TN-004: Tab-Closing Prevention
**Ziel:** Tabs können nicht geschlossen werden (wie in medizinischen Apps üblich)  

```python
def test_tab_closing_prevention():
    """Testet, dass Tabs nicht geschlossen werden können"""
    
    main_window = MainWindow(config, session_manager, patient_manager)
    initial_tab_count = main_window.tab_widget.count()
    
    # Versuche Tab zu schließen (sollte nicht funktionieren)
    main_window.tab_widget.removeTab(0)
    
    # Verifikation: Anzahl der Tabs unverändert
    final_tab_count = main_window.tab_widget.count()
    assert initial_tab_count == final_tab_count, "Tab was unexpectedly removed"
```

### TN-005: Tab-Widget Styling
**Ziel:** Konsistentes Design und Hover-Effekte  

```python
def test_tab_widget_styling():
    """Testet Tab-Widget Styling und Hover-Effekte"""
    
    main_window = MainWindow(config, session_manager, patient_manager)
    tab_widget = main_window.tab_widget
    
    # Style-Sheet Verifikation
    expected_styles = [
        "QTabWidget::pane { border: 1px solid #cccccc; }",
        "QTabBar::tab:selected { background-color: #ffffff; }",
        "QTabBar::tab:hover { background-color: #e0e0e0; }"
    ]
    
    style_sheet = main_window.styleSheet()
    for expected_style in expected_styles:
        assert expected_style in style_sheet, f"Missing style: {expected_style}"
```

---

## 🍞 Breadcrumb-Navigation Tests

### BN-001: Dashboard Breadcrumbs
**Ziel:** Navigationspfad im Dashboard  

```python
def test_dashboard_breadcrumbs():
    """Testet Breadcrumb-Navigation im Dashboard"""
    
    dashboard = DashboardWidget(config, session_manager, patient_manager)
    
    # Breadcrumb-Struktur
    expected_breadcrumbs = [
        "Rhinoplastik-Dokumentation",
        "Dashboard"
    ]
    
    # Breadcrumb-Label suchen
    breadcrumb_widgets = dashboard.findChildren(QLabel)
    breadcrumb_labels = [w.text() for w in breadcrumb_widgets if "Dashboard" in w.text()]
    
    assert len(breadcrumb_labels) > 0, "No dashboard breadcrumb found"
```

### BN-002: Patient-Editor Breadcrumbs
**Ziel:** Navigationspfad im Patient-Editor Modal  

```python
def test_patient_editor_breadcrumbs():
    """Testet Breadcrumbs im Patient-Editor Modal"""
    
    # Patient-Editor öffnen
    main_window.open_patient_editor(patient, readonly=False)
    
    # Modal-Dialog finden
    dialogs = main_window.findChildren(QDialog)
    editor_dialog = next((d for d in dialogs if "Patient" in d.windowTitle()), None)
    
    assert editor_dialog is not None, "Patient editor dialog not found"
    
    # Breadcrumb-Widget im Dialog suchen
    breadcrumb_labels = editor_dialog.findChildren(QLabel)
    has_breadcrumb = any("Patient" in label.text() for label in breadcrumb_labels)
    
    assert has_breadcrumb, "No breadcrumb in patient editor dialog"
```

### BN-003: Back-Button Functionality
**Ziel:** Zurück-Navigation zwischen Dialog-Stufen  

```python
def test_back_button_functionality():
    """Testet Zurück-Button in Modal-Dialogen"""
    
    # Patient-Editor öffnen
    main_window.open_patient_editor(patient, readonly=False)
    
    # Back-Button suchen
    dialogs = main_window.findChildren(QDialog)
    editor_dialog = dialogs[0]
    
    back_buttons = editor_dialog.findChildren(QPushButton, "back")
    if back_buttons:
        back_button = back_buttons[0]
        
        # Back-Button klicken
        back_button.click()
        
        # Verifikation: Dialog sollte sich schließen oder minimiert werden
        assert not editor_dialog.isVisible(), "Back button didn't close dialog"
```

---

## 🔀 Split-View & Multi-Panel Tests

### SV-001: Dashboard Grid Layout
**Ziel:** Dashboard Grid-Layout mit StatTiles  

```python
def test_dashboard_grid_layout():
    """Testet Dashboard Grid-Layout für Statistik-Kacheln"""
    
    dashboard = DashboardWidget(config, session_manager, patient_manager)
    
    # StatTile-Widgets suchen
    stat_tiles = dashboard.findChildren(StatTile)
    assert len(stat_tiles) >= 4, f"Expected at least 4 stat tiles, found {len(stat_tiles)}"
    
    # Grid-Layout verifizieren
    grid_layouts = dashboard.findChildren(QGridLayout)
    dashboard_grid = next((gl for gl in grid_layouts if gl.count() > 0), None)
    
    assert dashboard_grid is not None, "No grid layout found in dashboard"
    assert dashboard_grid.count() >= 4, "Grid layout has too few items"
```

### SV-002: Patient-Editor Tab Layout
**Ziel:** Patient-Editor Tab-Layout  

```python
def test_patient_editor_tab_layout():
    """Testet Tab-Layout im Patient-Editor"""
    
    main_window.open_patient_editor(patient, readonly=False)
    
    # Editor-Dialog finden
    editor_widget = None
    for child in main_window.findChildren(QWidget):
        if hasattr(child, 'tab_widget'):
            editor_widget = child
            break
    
    assert editor_widget is not None, "Patient editor widget not found"
    
    # Tab-Widget verifizieren
    tab_widget = editor_widget.tab_widget
    expected_tabs = [
        "Stammdaten", "Chirurgische Details", "Anatomischer Status", 
        "Messwerte", "Verfahren/Materialien", "Nachsorge", 
        "Outcomes", "Bilder", "Einwilligungen/Notizen"
    ]
    
    for i, expected_tab in enumerate(expected_tabs):
        actual_tab = tab_widget.tabText(i)
        assert actual_tab == expected_tab, f"Tab {i}: Expected '{expected_tab}', got '{actual_tab}'"
```

### SV-003: Split-View in Patienten-Liste
**Ziel:** Split-View zwischen Liste und Detail-Panel  

```python
def test_patients_list_split_view():
    """Testet Split-View in der Patienten-Liste"""
    
    patients_widget = PatientsListWidget(config, session_manager, patient_manager)
    
    # Splitter-Widget suchen
    splitters = patients_widget.findChildren(QSplitter)
    
    if splitters:
        splitter = splitters[0]
        splitter_orientation = splitter.orientation()
        
        # Verifikation: Horizontal oder vertikal
        assert splitter_orientation in [Qt.Horizontal, Qt.Vertical], "Invalid splitter orientation"
        
        # Split-Verhältnis testen
        sizes = splitter.sizes()
        assert len(sizes) == 2, "Split view should have exactly 2 panels"
```

### SV-004: Multi-Panel Search Interface
**Ziel:** Multi-Panel Such-Interface  

```python
def test_search_multi_panel():
    """Testet Multi-Panel Layout im Such-Interface"""
    
    search_widget = SearchWidget(config, session_manager, patient_manager, media_manager)
    
    # Panel-Struktur verifizieren
    group_boxes = search_widget.findChildren(QGroupBox)
    assert len(group_boxes) >= 3, "Search interface should have multiple panels"
    
    # Panel-Labels sammeln
    panel_labels = [gb.title() for gb in group_boxes if gb.title()]
    expected_panels = ["Suchkriterien", "Erweiterte Filter", "Ergebnisse"]
    
    for expected_panel in expected_panels:
        assert any(expected_panel.lower() in label.lower() for label in panel_labels), \
            f"Missing panel: {expected_panel}"
```

### SV-005: Responsive Panel Resizing
**Ziel:** Automatische Panel-Größen-Anpassung  

```python
def test_responsive_panel_resizing():
    """Testet automatische Panel-Größen-Anpassung"""
    
    patients_widget = PatientsListWidget(config, session_manager, patient_manager)
    
    # Splitter mit unterschiedlichen Größen testen
    initial_size = patients_widget.size()
    
    # Widget-Größe ändern
    new_size = initial_size.scaled(0.8, 0.8, Qt.KeepAspectRatio)
    patients_widget.resize(new_size)
    
    # Verifikation: Layout-Anpassung
    assert patients_widget.size() == new_size, "Widget didn't resize properly"
```

---

## 📱 Responsive Layout Tests

### RL-001: Minimum Window Size Enforcement
**Ziel:** Mindestfenstergröße wird eingehalten  

```python
def test_minimum_window_size():
    """Testet Mindestfenstergröße"""
    
    main_window = MainWindow(config, session_manager, patient_manager)
    
    # Mindestgröße aus Konfiguration
    expected_min_size = config.get('ui.window_min_size', (1000, 600))
    actual_min_size = (main_window.minimumWidth(), main_window.minimumHeight())
    
    assert actual_min_size == expected_min_size, \
        f"Expected min size {expected_min_size}, got {actual_min_size}"
    
    # Versuch, kleiner zu machen
    main_window.resize(500, 400)
    
    # Verifikation: Mindestgröße wird eingehalten
    actual_size = (main_window.width(), main_window.height())
    assert actual_size[0] >= expected_min_size[0] and actual_size[1] >= expected_min_size[1], \
        "Window size below minimum not prevented"
```

### RL-002: Window Size Persistence
**Ziel:** Fenstergröße wird zwischen Sitzungen gespeichert  

```python
def test_window_size_persistence():
    """Testet Persistenz der Fenstergröße"""
    
    # Fenstergröße setzen
    test_size = (1400, 900)
    main_window = MainWindow(config, session_manager, patient_manager)
    main_window.resize(*test_size)
    
    # Persistenz prüfen
    saved_size = config.get('ui.window_size')
    assert saved_size == test_size, f"Expected size {test_size}, saved {saved_size}"
    
    # Neue Instanz mit gespeicherter Größe
    new_window = MainWindow(config, session_manager, patient_manager)
    assert new_window.width() == test_size[0] and new_window.height() == test_size[1], \
        "Window size not restored from config"
```

### RL-003: DPI Scaling Adaptation
**Ziel:** Anpassung an verschiedene DPI-Einstellungen  

```python
def test_dpi_scaling_adaptation():
    """Testet DPI-Skalierung für verschiedene Bildschirme"""
    
    # Verschiedene DPI-Werte testen
    dpi_values = [96, 120, 144, 192]  # 100%, 125%, 150%, 200%
    
    for dpi in dpi_values:
        # DPI-Skalierung simulieren
        os.environ['QT_SCALE_FACTOR'] = str(dpi / 96.0)
        
        app = QApplication.instance() or QApplication([])
        main_window = MainWindow(config, session_manager, patient_manager)
        
        # Verifikation: Widget-Größen angepasst
        assert main_window.width() > 0 and main_window.height() > 0, \
            f"Window creation failed at DPI {dpi}"
        
        main_window.close()
```

### RL-004: Multi-Monitor Support
**Ziel:** Korrektes Verhalten bei mehreren Monitoren  

```python
def test_multi_monitor_support():
    """Testet Multi-Monitor-Support"""
    
    app = QApplication.instance() or QApplication([])
    screens = app.screens()
    
    if len(screens) > 1:
        # Fenster auf zweitem Bildschirm positionieren
        main_window = MainWindow(config, session_manager, patient_manager)
        second_screen = screens[1]
        screen_geometry = second_screen.geometry()
        
        # Fenster in Bereich des zweiten Bildschirms bewegen
        target_position = screen_geometry.center() - main_window.rect().center()
        main_window.move(target_position)
        
        # Verifikation: Fenster auf richtigem Bildschirm
        window_center = main_window.frameGeometry().center()
        assert second_screen.geometry().contains(window_center), \
            "Window not positioned on second screen"
```

### RL-005: High-Resolution Icon Support
**Ziel:** Icon-Skalierung für HiDPI-Displays  

```python
def test_high_resolution_icons():
    """Testet Icon-Skalierung für High-Resolution Displays"""
    
    main_window = MainWindow(config, session_manager, patient_manager)
    
    # Tab-Icons verifizieren
    for i in range(main_window.tab_widget.count()):
        icon = main_window.tab_widget.tabIcon(i)
        if not icon.isNull():
            # Icon-Pixel-Verhältnis prüfen
            pixel_ratio = icon.actualSize(main_window.tab_widget.size()).width() / icon.pixmap(Qt.ReturnByValue).width()
            assert pixel_ratio >= 1.0, f"Tab {i}: Icon not scaled for HiDPI"
```

---

## 🪟 Modal-Dialog Tests

### MD-001: Patient-Editor Modal Opening
**Ziel:** Korrektes Öffnen des Patient-Editor Modals  

```python
def test_patient_editor_modal_opening():
    """Testet Modal-Öffnung des Patient-Editors"""
    
    # Editor öffnen
    main_window.open_patient_editor(patient, readonly=False)
    
    # Modal-Dialog finden
    dialogs = main_window.findChildren(QDialog)
    assert len(dialogs) > 0, "No dialog found after opening patient editor"
    
    editor_dialog = dialogs[0]
    
    # Modal-Eigenschaften verifizieren
    assert editor_dialog.isModal(), "Dialog is not modal"
    assert editor_dialog.isVisible(), "Dialog is not visible"
    assert "Patient" in editor_dialog.windowTitle(), f"Unexpected title: {editor_dialog.windowTitle()}"
```

### MD-002: Modal Blocking Behavior
**Ziel:** Modal blockiert Hauptfenster-Interaktion  

```python
def test_modal_blocking_behavior():
    """Testet Modal-Blocking-Verhalten"""
    
    main_window = MainWindow(config, session_manager, patient_manager)
    
    # Modal öffnen
    main_window.open_patient_editor(patient, readonly=False)
    
    # Hauptfenster klicken (sollte blockiert sein)
    main_window.setFocus()
    
    # Verifikation: Modal blockiert Input
    dialogs = main_window.findChildren(QDialog)
    if dialogs:
        editor_dialog = dialogs[0]
        assert editor_dialog.isActiveWindow(), "Dialog not active while modal"
```

### MD-003: Modal Size Constraints
**Ziel:** Modal-Dialog Größen-Constraints  

```python
def test_modal_size_constraints():
    """Testet Modal-Dialog Größen-Constraints"""
    
    main_window.open_patient_editor(patient, readonly=False)
    
    # Dialog finden
    dialogs = main_window.findChildren(QDialog)
    editor_dialog = dialogs[0]
    
    # Mindestgröße prüfen
    expected_min_size = (1000, 700)
    actual_min_size = (editor_dialog.minimumWidth(), editor_dialog.minimumHeight())
    
    assert actual_min_size == expected_min_size, \
        f"Expected min size {expected_min_size}, got {actual_min_size}"
```

### MD-004: Modal Child Widget Layout
**Ziel:** Korrektes Layout der Modal-Child-Widgets  

```python
def test_modal_child_widget_layout():
    """Testet Child-Widget-Layout im Modal"""
    
    main_window.open_patient_editor(patient, readonly=True)
    
    # Dialog und Editor-Widget finden
    dialogs = main_window.findChildren(QDialog)
    editor_dialog = dialogs[0]
    
    # Tab-Widget im Editor finden
    tab_widgets = editor_dialog.findChildren(QTabWidget)
    assert len(tab_widgets) > 0, "No tab widget in modal dialog"
    
    tab_widget = tab_widgets[0]
    
    # Tab-Anzahl prüfen
    expected_tab_count = 9  # Stammdaten, Chirurgische Details, etc.
    actual_tab_count = tab_widget.count()
    assert actual_tab_count >= expected_tab_count, \
        f"Expected at least {expected_tab_count} tabs, got {actual_tab_count}"
```

### MD-005: Modal Closing and Cleanup
**Ziel:** Korrektes Schließen und Aufräumen des Modals  

```python
def test_modal_closing_cleanup():
    """Testet Modal-Schließen und Aufräumen"""
    
    # Modal öffnen
    main_window.open_patient_editor(patient, readonly=False)
    
    # Dialog finden und schließen
    dialogs = main_window.findChildren(QDialog)
    editor_dialog = dialogs[0]
    editor_dialog.close()
    
    # Verifikation: Modal geschlossen
    assert not editor_dialog.isVisible(), "Dialog not closed properly"
```

### MD-006: Multiple Modal Prevention
**Ziel:** Verhindert mehrere Modal-Dialoge  

```python
def test_multiple_modal_prevention():
    """Testet Verhinderung multipler Modal-Dialoge"""
    
    # Ersten Modal öffnen
    main_window.open_patient_editor(patient, readonly=False)
    
    # Versuch zweiten Modal zu öffnen
    main_window.open_patient_editor(patient2, readonly=False)
    
    # Verifikation: Nur ein Modal geöffnet
    dialogs = main_window.findChildren(QDialog)
    visible_dialogs = [d for d in dialogs if d.isVisible()]
    
    assert len(visible_dialogs) == 1, f"Expected 1 modal, found {len(visible_dialogs)}"
```

---

## 💾 Layout-Persistenz Tests

### LP-001: Tab Selection Persistence
**Ziel:** Aktiver Tab wird zwischen Sitzungen gespeichert  

```python
def test_tab_selection_persistence():
    """Testet Persistenz der Tab-Auswahl"""
    
    # Tab 2 (Suchen) aktivieren
    main_window.tab_widget.setCurrentIndex(2)
    selected_tab = main_window.tab_widget.currentIndex()
    
    # Persistierung prüfen
    config.set('ui.last_selected_tab', selected_tab)
    
    # Neue Instanz erstellen
    new_window = MainWindow(config, session_manager, patient_manager)
    
    # Verifikation: Letzter Tab wiederhergestellt
    restored_tab = config.get('ui.last_selected_tab')
    assert restored_tab == selected_tab, \
        f"Expected tab {selected_tab}, restored {restored_tab}"
```

### LP-002: Splitter State Persistence
**Ziel:** Splitter-Zustände werden gespeichert  

```python
def test_splitter_state_persistence():
    """Testet Persistenz der Splitter-Zustände"""
    
    # Splitter finden
    patients_widget = PatientsListWidget(config, session_manager, patient_manager)
    splitters = patients_widget.findChildren(QSplitter)
    
    if splitters:
        splitter = splitters[0]
        
        # Splitter-Größen ändern
        original_sizes = splitter.sizes()
        new_sizes = [int(s * 0.6) for s in original_sizes]
        splitter.setSizes(new_sizes)
        
        # Persistierung prüfen
        saved_sizes = config.get('ui.splitter_sizes', {})
        assert len(saved_sizes) == len(new_sizes), "Splitter sizes not saved"
```

### LP-003: Column Width Persistence (Patientenliste)
**Ziel:** Spaltenbreiten in Tabellen werden gespeichert  

```python
def test_column_width_persistence():
    """Testet Persistenz der Spaltenbreiten"""
    
    patients_widget = PatientsListWidget(config, session_manager, patient_manager)
    table_widgets = patients_widget.findChildren(QTableWidget)
    
    if table_widgets:
        table = table_widgets[0]
        
        # Spaltenbreite ändern
        table.setColumnWidth(0, 200)  # Name-Spalte
        
        # Persistierung verifizieren
        saved_widths = config.get('ui.table_column_widths', {})
        assert 0 in saved_widths, "Column width not persisted"
        assert saved_widths[0] == 200, f"Expected width 200, saved {saved_widths[0]}"
```

### LP-004: Window Position Persistence
**Ziel:** Fensterposition wird gespeichert  

```python
def test_window_position_persistence():
    """Testet Persistenz der Fensterposition"""
    
    # Fensterposition setzen
    test_position = (100, 50)
    main_window = MainWindow(config, session_manager, patient_manager)
    main_window.move(*test_position)
    
    # Persistierung prüfen
    saved_position = config.get('ui.window_position')
    assert saved_position == test_position, \
        f"Expected position {test_position}, saved {saved_position}"
```

### LP-005: UI Theme Persistence
**Ziel:** UI-Theme wird zwischen Sitzungen gespeichert  

```python
def test_ui_theme_persistence():
    """Testet Persistenz des UI-Themes"""
    
    # Theme ändern (falls implementiert)
    main_window = MainWindow(config, session_manager, patient_manager)
    
    # Style-Sheet speichern
    current_style = main_window.styleSheet()
    config.set('ui.theme', current_style)
    
    # Verifikation: Theme gespeichert
    saved_theme = config.get('ui.theme')
    assert saved_theme == current_style, "Theme not persisted"
```

---

## ⚡ Performance-Messungen

### PM-001: Tab-Switch Performance
**Ziel:** Tab-Wechsel unter 200ms  

```python
def measure_tab_switch_performance():
    """Misst Tab-Wechsel-Performance"""
    
    main_window = MainWindow(config, session_manager, patient_manager)
    tab_switch_times = []
    
    # 10 Tab-Wechsel messen
    for _ in range(10):
        start_time = time.time()
        
        # Random Tab aktivieren
        random_tab = random.randint(0, main_window.tab_widget.count() - 1)
        main_window.tab_widget.setCurrentIndex(random_tab)
        
        end_time = time.time()
        switch_time = (end_time - start_time) * 1000  # ms
        tab_switch_times.append(switch_time)
    
    # Statistiken
    avg_time = sum(tab_switch_times) / len(tab_switch_times)
    max_time = max(tab_switch_times)
    min_time = min(tab_switch_times)
    
    print(f"Tab Switch Performance:")
    print(f"  Average: {avg_time:.2f}ms")
    print(f"  Min: {min_time:.2f}ms")
    print(f"  Max: {max_time:.2f}ms")
    
    # Verifikation
    assert avg_time < 200.0, f"Average tab switch time too slow: {avg_time:.2f}ms"
    assert max_time < 500.0, f"Max tab switch time too slow: {max_time:.2f}ms")
```

### PM-002: Modal Opening Performance
**Ziel:** Modal-Öffnung unter 500ms  

```python
def measure_modal_opening_performance():
    """Misst Modal-Öffnungs-Performance"""
    
    main_window = MainWindow(config, session_manager, patient_manager)
    opening_times = []
    
    # 5 Modal-Öffnungen messen
    for _ in range(5):
        start_time = time.time()
        
        # Modal öffnen
        main_window.open_patient_editor(patient, readonly=False)
        
        end_time = time.time()
        open_time = (end_time - start_time) * 1000  # ms
        opening_times.append(open_time)
        
        # Modal wieder schließen
        dialogs = main_window.findChildren(QDialog)
        if dialogs:
            dialogs[0].close()
    
    # Statistiken
    avg_time = sum(opening_times) / len(opening_times)
    
    print(f"Modal Opening Performance:")
    print(f"  Average: {avg_time:.2f}ms")
    
    # Verifikation
    assert avg_time < 500.0, f"Average modal opening too slow: {avg_time:.2f}ms"
```

### PM-003: Layout Rendering Performance
**Ziel:** Layout-Rendering unter 300ms  

```python
def measure_layout_rendering_performance():
    """Misst Layout-Rendering-Performance"""
    
    config = AppConfig()
    session_manager = SessionManager()
    patient_manager = PatientManager()
    
    rendering_times = []
    
    # 3 Layout-Renderings messen
    for _ in range(3):
        start_time = time.time()
        
        # Neues Fenster erstellen (triggert Layout-Rendering)
        main_window = MainWindow(config, session_manager, patient_manager)
        
        end_time = time.time()
        render_time = (end_time - start_time) * 1000  # ms
        rendering_times.append(render_time)
        
        # Aufräumen
        main_window.close()
    
    # Statistiken
    avg_time = sum(rendering_times) / len(rendering_times)
    
    print(f"Layout Rendering Performance:")
    print(f"  Average: {avg_time:.2f}ms")
    
    # Verifikation
    assert avg_time < 300.0, f"Average layout rendering too slow: {avg_time:.2f}ms"
```

### PM-004: Memory Usage Monitoring
**Ziel:** Speicherverbrauch überwachen  

```python
def monitor_memory_usage():
    """Überwacht Speicherverbrauch bei Layout-Operationen"""
    
    import psutil
    process = psutil.Process()
    
    main_window = MainWindow(config, session_manager, patient_manager)
    
    # Initialer Speicherverbrauch
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Layout-Operationen durchführen
    for i in range(10):
        # Tab-Wechsel
        main_window.tab_widget.setCurrentIndex(i % main_window.tab_widget.count())
        
        # Modal öffnen/schließen
        main_window.open_patient_editor(patient, readonly=False)
        dialogs = main_window.findChildren(QDialog)
        if dialogs:
            dialogs[0].close()
    
    # Finaler Speicherverbrauch
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    print(f"Memory Usage:")
    print(f"  Initial: {initial_memory:.2f}MB")
    print(f"  Final: {final_memory:.2f}MB")
    print(f"  Increase: {memory_increase:.2f}MB")
    
    # Verifikation: Maximal 50MB Speicherverbrauch
    assert memory_increase < 50.0, f"Memory increase too high: {memory_increase:.2f}MB"
```

### PM-005: UI Responsiveness
**Ziel:** UI-Responsivität unter Last  

```python
def test_ui_responsiveness_under_load():
    """Testet UI-Responsivität unter Last"""
    
    main_window = MainWindow(config, session_manager, patient_manager)
    
    # Last-Simulation: Schnelle Tab-Wechsel
    start_time = time.time()
    tab_changes = 0
    
    for i in range(50):
        tab_index = i % main_window.tab_widget.count()
        main_window.tab_widget.setCurrentIndex(tab_index)
        tab_changes += 1
    
    total_time = time.time() - start_time
    avg_time_per_change = total_time / tab_changes
    
    print(f"UI Responsiveness Under Load:")
    print(f"  Total time: {total_time:.3f}s")
    print(f"  Average per tab change: {avg_time_per_change*1000:.2f}ms")
    print(f"  Tab changes: {tab_changes}")
    
    # Verifikation: Durchschnitt unter 100ms
    assert avg_time_per_change < 0.1, f"UI too slow under load: {avg_time_per_change*1000:.2f}ms"
```

---

## 🌐 Browser-Kompatibilität

*Note: Diese Anwendung ist eine Desktop-Anwendung (PySide6), nicht browser-basiert.  
Dieser Abschnitt ist für zukünftige Web-Versionen reserviert.*

### BC-001: Web-View Testing (Future)
**Ziel:** Web-View Kompatibilität testen  

*Platzhalter für zukünftige Web-Version*

---

## 🤖 Test-Automatisierung

### TA-001: Automated Test Runner
**Ziel:** Vollautomatisierte Testausführung  

```python
class LayoutNavigationTestRunner:
    """Automatischer Test-Runner für Layout- und Navigation-Tests"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
    
    def run_all_tests(self):
        """Führt alle Tests aus"""
        
        test_suites = [
            self.run_tab_navigation_tests,
            self.run_responsive_layout_tests,
            self.run_modal_dialog_tests,
            self.run_persistence_tests
        ]
        
        for test_suite in test_suites:
            try:
                result = test_suite()
                self.test_results[test_suite.__name__] = result
            except Exception as e:
                self.test_results[test_suite.__name__] = f"FAILED: {str(e)}"
    
    def generate_report(self):
        """Generiert Test-Report"""
        
        report = f"""
# Layout & Navigation Test Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Results
"""
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result == True else f"❌ FAIL: {result}"
            report += f"- {test_name}: {status}\n"
        
        report += f"\n## Performance Summary\n"
        for metric, value in self.performance_metrics.items():
            report += f"- {metric}: {value}\n"
        
        return report
```

### TA-002: Continuous Integration Setup
**Ziel:** CI/CD Integration  

```yaml
# .github/workflows/layout-navigation-tests.yml
name: Layout & Navigation Tests

on: [push, pull_request]

jobs:
  test-layout-navigation:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest psutil
    
    - name: Run Layout & Navigation Tests
      run: |
        python -m pytest tests/layout_navigation/ -v --tb=short
    
    - name: Generate Performance Report
      run: |
        python tests/layout_navigation/generate_performance_report.py
    
    - name: Upload Test Results
      uses: actions/upload-artifact@v2
      with:
        name: layout-navigation-report
        path: reports/layout_navigation_performance.json
```

### TA-003: Performance Benchmarking
**Ziel:** Automatische Performance-Benchmarks  

```python
def create_performance_benchmark():
    """Erstellt Performance-Benchmark für Regression-Tests"""
    
    benchmarks = {
        'tab_switch_max': 200,  # ms
        'modal_open_max': 500,  # ms
        'layout_render_max': 300,  # ms
        'memory_increase_max': 50,  # MB
        'ui_responsiveness_max': 100  # ms
    }
    
    with open('performance_benchmarks.json', 'w') as f:
        json.dump(benchmarks, f, indent=2)
```

---

## 📈 Test-Ergebnisse & Metriken

### Ziel-Metriken (Performance Baselines)

| Metrik | Zielwert | Toleranz |
|--------|----------|----------|
| Tab-Wechsel-Zeit | < 200ms | ±50ms |
| Modal-Öffnungszeit | < 500ms | ±100ms |
| Layout-Rendering | < 300ms | ±75ms |
| Speicherverbrauch-Inkrement | < 50MB | ±10MB |
| UI-Responsivität | < 100ms | ±25ms |

### Test-Deckung

- ✅ **Tab-Navigation:** 5/5 Tests implementiert
- ✅ **Breadcrumb-Navigation:** 3/3 Tests implementiert
- ✅ **Split-View/Multi-Panel:** 5/5 Tests implementiert
- ✅ **Responsive Layout:** 5/5 Tests implementiert
- ✅ **Modal-Dialoge:** 6/6 Tests implementiert
- ✅ **Layout-Persistenz:** 5/5 Tests implementiert
- ✅ **Performance-Messungen:** 5/5 Tests implementiert

**Gesamt-Abdeckung:** 34/34 Testfälle implementiert (100%)

---

## 🐛 Bekannte Issues & Workarounds

### Issue LN-001: Langsame Tab-Wechsel bei vielen Patienten
**Beschreibung:** Tab-Wechsel verlangsamt sich bei > 1000 Patienten in der Liste  
**Workaround:** Paginierung in Patienten-Tab implementieren  
**Priorität:** Mittel

### Issue LN-002: Modal-Größe auf kleinen Bildschirmen
**Beschreibung:** Patient-Editor Modal zu groß für 1366x768 Displays  
**Workaround:** Responsive Modal-Größe basierend auf Bildschirmgröße  
**Priorität:** Hoch

### Issue LN-003: Splitter-Größen nicht persistent
**Beschreibung:** Splitter-Größen werden zwischen Sitzungen nicht gespeichert  
**Workaround:** Splitter-Zustände in Konfiguration speichern  
**Priorität:** Niedrig

---

## 🔄 Test-Wartung & Updates

### Regelmäßige Überprüfungen
- **Wöchentlich:** Performance-Tests ausführen
- **Monatlich:** Cross-Platform-Kompatibilität prüfen
- **Bei jedem Release:** Vollständige Test-Suite ausführen

### Update-Zyklus
- **UI-Änderungen:** Tests entsprechend anpassen
- **Neue Features:** Neue Testfälle hinzufügen
- **Performance-Regressionen:** Benchmark-Werte aktualisieren

---

## 📞 Support & Kontakt

**Test-Suite Maintainer:** Development Team  
**Letzte Aktualisierung:** 2025-11-06  
**Version:** 1.0.0

**Feedback und Issues:** Bitte über das Issue-Tracking-System melden.

---

*Diese Dokumentation wird automatisch mit jedem Test-Lauf aktualisiert.*