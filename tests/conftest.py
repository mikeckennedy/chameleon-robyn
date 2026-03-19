from pathlib import Path

import pytest

import chameleon_robyn as cr


@pytest.fixture
def test_templates_path(pytestconfig):
    return Path(pytestconfig.rootdir, 'tests', 'templates')


@pytest.fixture
def setup_global_template(test_templates_path):
    cr.global_init(str(test_templates_path), cache_init=False)
    yield
    cr.engine.clear()
