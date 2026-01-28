"""Pytest plugin for lazy app loading."""
import os
os.environ["TESTING"] = "1"

def pytest_configure(config):
    """Lazy load app only when tests run."""
    pass

def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add markers for test categories
        if "health" in item.nodeid:
            item.add_marker("unit")
