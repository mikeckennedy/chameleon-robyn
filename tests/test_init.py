import pytest

import chameleon_robyn as cr
from chameleon_robyn.exceptions import ChameleonRobynException


def test_cannot_decorate_with_missing_init():
    cr.engine.clear()

    with pytest.raises(ChameleonRobynException):

        @cr.template('home/index.pt')
        def view_method(a, b, c):
            return {'a': a, 'b': b, 'c': c}

        view_method(1, 2, 3)


def test_can_call_init_with_good_path(test_templates_path):
    cr.global_init(str(test_templates_path), cache_init=False)
    cr.engine.clear()


def test_cannot_call_init_with_bad_path(test_templates_path):
    bad_path = test_templates_path / 'missing'
    with pytest.raises(ChameleonRobynException):
        cr.global_init(str(bad_path), cache_init=False)
