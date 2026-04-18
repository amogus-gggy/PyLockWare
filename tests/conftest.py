"""
Pytest configuration and fixtures for PyLockWare tests
"""
import shutil
import tempfile
from pathlib import Path
import pytest

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test operations"""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def example_project_path():
    """Path to example_project"""
    return Path(__file__).parent.parent / "example_project"


@pytest.fixture
def example_project2_path():
    """Path to example_project2"""
    return Path(__file__).parent.parent / "example_project2"


@pytest.fixture
def example_project3_path():
    """Path to example_project3"""
    return Path(__file__).parent.parent / "example_project3"


@pytest.fixture
def example_project4_path():
    """Path to example_project4"""
    return Path(__file__).parent.parent / "example_project4"


@pytest.fixture
def example_async_project_path():
    """Path to example_async_project"""
    return Path(__file__).parent.parent / "example_async_project"


@pytest.fixture
def example_fastapi_project_path():
    """Path to example_fastapi_project"""
    return Path(__file__).parent.parent / "example_fastapi_project"


@pytest.fixture
def example_pyside6_project_path():
    """Path to example_pyside6_project"""
    return Path(__file__).parent.parent / "example_pyside6_project"


@pytest.fixture
def crackme_project_path():
    """Path to crackme project"""
    return Path(__file__).parent.parent / "crackme"
