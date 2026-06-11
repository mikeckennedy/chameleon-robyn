import pytest
from robyn import Response

import chameleon_robyn as cr
from chameleon_robyn.exceptions import ChameleonRobynException


def test_response_callback_invoked_and_model_not_mutated(setup_global_template):
    callback_responses = []
    model = {'a': 1, 'b': 2, 'c': 3, '__response_callback__': callback_responses.append}

    @cr.template('home/index.pt')
    def view_method():
        return model

    resp = view_method()
    assert isinstance(resp, Response)
    assert resp.status_code == 200
    assert len(callback_responses) == 1
    assert callback_responses[0] is resp

    # The handler's dict is copied before the hook is popped, so a shared or
    # module-level model keeps working on subsequent requests.
    assert '__response_callback__' in model
    view_method()
    assert len(callback_responses) == 2


def test_response_callback_must_be_callable(setup_global_template):
    @cr.template('home/index.pt')
    def view_method():
        return {'a': 1, 'b': 2, 'c': 3, '__response_callback__': 'not-a-function'}

    with pytest.raises(ChameleonRobynException):
        view_method()
