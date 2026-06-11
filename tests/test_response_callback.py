import pytest
from robyn import Response

import chameleon_robyn as cr
from chameleon_robyn.exceptions import ChameleonRobynException


def test_response_callback_invoked_and_model_not_mutated(setup_global_template, view_style, make_view, call_view):
    callback_responses = []
    model = {'a': 1, 'b': 2, 'c': 3, '__response_callback__': callback_responses.append}

    view = make_view(view_style, cr.template('home/index.pt'), lambda: model)

    resp = call_view(view)
    assert isinstance(resp, Response)
    assert resp.status_code == 200
    assert len(callback_responses) == 1
    assert callback_responses[0] is resp

    # The handler's dict is copied before the hook is popped, so a shared or
    # module-level model keeps working on subsequent requests.
    assert '__response_callback__' in model
    call_view(view)
    assert len(callback_responses) == 2


def test_response_callback_must_be_callable(setup_global_template, view_style, make_view, call_view):
    view = make_view(
        view_style,
        cr.template('home/index.pt'),
        lambda: {'a': 1, 'b': 2, 'c': 3, '__response_callback__': 'not-a-function'},
    )

    with pytest.raises(ChameleonRobynException):
        call_view(view)
