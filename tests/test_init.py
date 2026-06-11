import pytest

import chameleon_robyn as cr
from chameleon_robyn.exceptions import ChameleonRobynException


def test_cannot_decorate_with_missing_init():
    cr.engine.clear()

    @cr.template('home/index.pt')
    def view_method(a, b, c):
        return {'a': a, 'b': b, 'c': c}

    with pytest.raises(ChameleonRobynException):
        view_method(1, 2, 3)


def test_can_call_init_with_good_path(test_templates_path):
    cr.global_init(str(test_templates_path), cache_init=False)
    cr.engine.clear()


def test_cannot_call_init_with_bad_path(test_templates_path):
    bad_path = test_templates_path / 'missing'
    with pytest.raises(ChameleonRobynException):
        cr.global_init(str(bad_path), cache_init=False)


def test_cannot_call_init_with_empty_path():
    cr.engine.clear()
    with pytest.raises(ChameleonRobynException):
        cr.global_init('', cache_init=False)


def test_cache_init_true_is_noop_when_already_initialized(test_templates_path, tmp_path):
    cr.engine.clear()
    cr.global_init(str(test_templates_path), cache_init=False)
    cr.global_init(str(tmp_path), cache_init=True)
    try:
        # Still serving from the first folder — the second init was skipped.
        html = cr.render('test/hello.pt', name='Cache')
        assert 'Hello, Cache!' in html
    finally:
        cr.engine.clear()


def test_cache_init_false_reinitializes(test_templates_path, tmp_path):
    cr.engine.clear()
    cr.global_init(str(test_templates_path), cache_init=False)
    cr.global_init(str(tmp_path), cache_init=False)
    try:
        # The loader now points at the (empty) new folder, so the template is gone.
        with pytest.raises(ValueError):
            cr.render('test/hello.pt', name='Cache')
    finally:
        cr.engine.clear()


def test_restricted_namespace_rejects_alpine_attributes(test_templates_path):
    cr.engine.clear()
    cr.global_init(str(test_templates_path), cache_init=False)  # restricted by default
    try:
        # Chameleon treats `:class` as an undefined namespace prefix in restricted mode.
        with pytest.raises(KeyError):
            cr.render('test/alpine.pt')
    finally:
        cr.engine.clear()


def test_unrestricted_namespace_allows_alpine_attributes(test_templates_path):
    cr.engine.clear()
    cr.global_init(str(test_templates_path), cache_init=False, restricted_namespace=False)
    try:
        html = cr.render('test/alpine.pt')
        assert '@click' in html
        assert ':class' in html
    finally:
        cr.engine.clear()
