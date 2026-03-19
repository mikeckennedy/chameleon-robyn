import asyncio

from robyn import Response

import chameleon_robyn
import chameleon_robyn as cr


def test_friendly_404_sync_method(setup_global_template):
    @cr.template('home/index.pt')
    def view_method(a, b, c):
        chameleon_robyn.not_found()
        return {'a': a, 'b': b, 'c': c}

    resp = view_method(1, 2, 3)
    assert isinstance(resp, Response)
    assert resp.status_code == 404
    assert '<h1>This is a pretty 404 page.</h1>' in resp.description


def test_friendly_404_custom_template_sync_method(setup_global_template):
    @cr.template('home/index.pt')
    def view_method(a, b, c):
        chameleon_robyn.not_found(four04template_file='errors/other_error_page.pt')
        return {'a': a, 'b': b, 'c': c}

    resp = view_method(1, 2, 3)
    assert isinstance(resp, Response)
    assert resp.status_code == 404
    assert '<h1>Another pretty 404 page.</h1>' in resp.description


def test_friendly_404_async_method(setup_global_template):
    @cr.template('home/index.pt')
    async def view_method(a, b, c) -> Response:
        chameleon_robyn.not_found()
        return {'a': a, 'b': b, 'c': c}

    resp = asyncio.run(view_method(1, 2, 3))
    assert isinstance(resp, Response)
    assert resp.status_code == 404
    assert '<h1>This is a pretty 404 page.</h1>' in resp.description
