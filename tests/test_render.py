import asyncio

import pytest
from robyn import Response

import chameleon_robyn as cr
from chameleon_robyn.exceptions import ChameleonRobynException


def test_cannot_decorate_missing_template(setup_global_template):
    @cr.template('home/missing.pt')
    def view_method():
        return {}

    with pytest.raises(ValueError):
        view_method()


def test_requires_template_for_default_name(setup_global_template):
    @cr.template(None)
    def view_method():
        return {}

    with pytest.raises(ValueError):
        view_method()


def test_default_template_name_pt(setup_global_template):
    @cr.template()
    def index(a, b, c):
        return {'a': a, 'b': b, 'c': c, 'world': 'WORLD'}

    resp = index(1, 2, 3)
    assert isinstance(resp, Response)
    assert resp.status_code == 200
    assert isinstance(resp.description, str)
    assert 'Hello default WORLD!' in resp.description


def test_default_template_name_no_parentheses(setup_global_template):
    @cr.template
    def index(a, b, c):
        return {'a': a, 'b': b, 'c': c, 'world': 'WORLD'}

    resp = index(1, 2, 3)
    assert isinstance(resp, Response)
    assert resp.status_code == 200
    assert isinstance(resp.description, str)
    assert 'Hello default WORLD!' in resp.description


def test_default_template_name_html(setup_global_template):
    @cr.template()
    def details(a, b, c):
        return {'a': a, 'b': b, 'c': c, 'world': 'WORLD'}

    resp = details(1, 2, 3)
    assert isinstance(resp, Response)
    assert resp.status_code == 200
    assert isinstance(resp.description, str)
    assert 'Hello default WORLD!' in resp.description


def test_auto_naming_resolves_at_first_request(test_templates_path):
    # Routes are commonly decorated at import time, before global_init() runs in
    # main() — the .html-vs-.pt check must wait until the folder is known.
    cr.engine.clear()

    @cr.template()
    def details(a, b, c):
        return {'a': a, 'b': b, 'c': c, 'world': 'WORLD'}

    cr.global_init(str(test_templates_path), cache_init=False)
    try:
        resp = details(1, 2, 3)
        assert isinstance(resp, Response)
        assert resp.status_code == 200
        assert isinstance(resp.description, str)
        assert 'Hello default WORLD!' in resp.description
    finally:
        cr.engine.clear()


def test_can_decorate_dict_sync_method(setup_global_template):
    @cr.template('home/index.pt')
    def view_method(a, b, c):
        return {'a': a, 'b': b, 'c': c}

    resp = view_method(1, 2, 3)
    assert isinstance(resp, Response)
    assert resp.status_code == 200


def test_can_decorate_dict_async_method(setup_global_template):
    @cr.template('home/index.pt')
    async def view_method(a, b, c):
        return {'a': a, 'b': b, 'c': c}

    resp = asyncio.run(view_method(1, 2, 3))
    assert isinstance(resp, Response)
    assert resp.status_code == 200


def test_direct_response_pass_through(setup_global_template, view_style, make_view, call_view):
    from robyn import Headers

    def body(a, b, c):
        return Response(
            status_code=418,
            description='abc',
            headers=Headers({}),
        )

    view = make_view(view_style, cr.template('home/index.pt'), body)
    resp = call_view(view, 1, 2, 3)
    assert isinstance(resp, Response)
    assert resp.status_code == 418
    assert resp.description == 'abc'


@pytest.mark.parametrize('bad_value', ['just a string', None, 42])
def test_invalid_return_type_raises(setup_global_template, view_style, make_view, call_view, bad_value):
    def body():
        return bad_value

    view = make_view(view_style, cr.template('home/index.pt'), body)
    with pytest.raises(ChameleonRobynException):
        call_view(view)


def test_decorator_instance_can_be_reused(setup_global_template):
    # One @template() instance applied to several functions must auto-derive
    # each function's own template, not leak the first one resolved.
    shared_decorator = cr.template()

    @shared_decorator
    def reuse_one():
        return {}

    @shared_decorator
    def reuse_two():
        return {}

    resp_one = reuse_one()
    resp_two = reuse_two()
    assert isinstance(resp_one.description, str)
    assert isinstance(resp_two.description, str)
    assert 'Reuse template ONE' in resp_one.description
    assert 'Reuse template TWO' in resp_two.description


def test_template_custom_status_and_content_type(setup_global_template):
    @cr.template('test/hello.pt', content_type='application/xml', status_code=201)
    def view_method():
        return {'name': 'World'}

    resp = view_method()
    assert resp.status_code == 201
    assert 'application/xml' in (resp.headers.get('content-type') or '')


def test_render_basic(setup_global_template):
    html = cr.render('test/hello.pt', name='World')
    assert '<h1>Hello, World!</h1>' in html


def test_response_returns_robyn_response(setup_global_template):
    resp = cr.response('test/hello.pt', name='World')
    assert isinstance(resp, Response)
    assert resp.status_code == 200
    assert isinstance(resp.description, str)
    assert 'Hello, World!' in resp.description
    assert 'text/html' in (resp.headers.get('content-type') or '')


def test_response_custom_status(setup_global_template):
    resp = cr.response('test/hello.pt', status_code=404, name='Not Found')
    assert resp.status_code == 404


def test_response_custom_content_type(setup_global_template):
    resp = cr.response('test/hello.pt', content_type='application/xml', name='World')
    assert 'application/xml' in (resp.headers.get('content-type') or '')


def test_chameleon_template_interface(test_templates_path):
    from chameleon_robyn.engine import TemplateInterface

    ct = cr.ChameleonTemplate(str(test_templates_path))
    assert isinstance(ct, TemplateInterface)

    resp = ct.render_template('test/hello.pt', name='Interface')
    assert isinstance(resp, Response)
    assert resp.status_code == 200
    assert isinstance(resp.description, str)
    assert 'Hello, Interface!' in resp.description
