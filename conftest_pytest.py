"""
pytest-Konfiguration für PySide6/Qt6 Integration Tests
"""

import pytest
import sys
from pathlib import Path

# Füge rhinoplastik_app zum Python-Pfad hinzu
rhinoplastik_path = Path(__file__).parent.parent / "rhinoplastik_app"
sys.path.insert(0, str(rhinoplastik_path))

def pytest_configure(config):
    """pytest-Konfiguration"""
    config.addinivalue_line(
        "markers", "qt: marks tests as Qt-related"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )

@pytest.fixture(scope="session")
def qapp_args():
    """Qt Application arguments für Headless-Tests"""
    return ["-platform", "offscreen"]

@pytest.fixture(scope="session")
def qt_application():
    """Qt Application Fixture"""
    from PySide6.QtWidgets import QApplication
    import os
    
    # Setze Offscreen-Platform für Headless-Tests
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    yield app
    
    # Cleanup
    app.quit()

# Mock-Klassen für Tests
class MockConfig:
    def get(self, key, default=None):
        defaults = {
            'ui.window_size': (1200, 800),
            'ui.window_min_size': (1000, 600),
            'app_dir': str(rhinoplastik_path)
        }
        return defaults.get(key, default)

class MockSession:
    def get_user_info(self):
        return {"username": "test", "role": "user"}
    
    def is_admin(self):
        return True
    
    def can_edit(self):
        return True
    
    def validate_session(self):
        return True

class MockPatient:
    def get_patient(self, patient_id):
        return None

@pytest.fixture
def mock_config():
    """Mock Config Fixture"""
    return MockConfig()

@pytest.fixture
def mock_session():
    """Mock Session Fixture"""
    return MockSession()

@pytest.fixture
def mock_patient():
    """Mock Patient Fixture"""
    return MockPatient()

# Test-Collection Modifikationen
def pytest_collection_modifyitems(config, items):
    """Modifiziert Test-Items für Markers"""
    for item in items:
        # Markiere alle Tests in dieser Datei als Qt-Tests
        if "pyside6_qt6_integration" in str(item.fspath):
            item.add_marker(pytest.mark.qt)
            item.add_marker(pytest.mark.integration)
