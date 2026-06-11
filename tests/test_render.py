import asyncio

import pytest
from robyn import Response

import chameleon_robyn as cr


def test_cannot_decorate_missing_template(setup_global_template):
    with pytest.raises(ValueError):

        @cr.template('home/missing.pt')
        def view_method():
            return {}

        view_method()


def test_requires_template_for_default_name(setup_global_template):
    with pytest.raises(ValueError):

        @cr.template(None)
        def view_method():
            return {}

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


def test_direct_response_pass_through():
    from robyn import Headers

    @cr.template('home/index.pt')
    def view_method(a, b, c):
        return Response(
            status_code=418,
            description='abc',
            headers=Headers({}),
        )

    resp = view_method(1, 2, 3)
    assert isinstance(resp, Response)
    assert resp.status_code == 418
    assert resp.description == 'abc'


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


def test_chameleon_template_interface(test_templates_path):
    from chameleon_robyn.engine import TemplateInterface

    ct = cr.ChameleonTemplate(str(test_templates_path))
    assert isinstance(ct, TemplateInterface)

    resp = ct.render_template('test/hello.pt', name='Interface')
    assert isinstance(resp, Response)
    assert resp.status_code == 200
    assert isinstance(resp.description, str)
    assert 'Hello, Interface!' in resp.description
