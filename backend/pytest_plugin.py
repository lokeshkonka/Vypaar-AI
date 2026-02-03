
import os
os.environ["TESTING"] = "1"

def pytest_configure(config):

    pass

def pytest_collection_modifyitems(config, items):

    for item in items:
        if "health" in item.nodeid:
            item.add_marker("unit")
