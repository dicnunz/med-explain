import importlib
import pytest

@pytest.mark.parametrize("mod", ["app", "summary"])
def test_import(mod):
    """Ensure key modules can be imported."""
    importlib.import_module(mod)
