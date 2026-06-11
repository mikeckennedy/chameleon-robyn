import asyncio
import inspect
from functools import wraps
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


@pytest.fixture(params=['sync', 'async'])
def view_style(request):
    """Parametrizes a test across both decorator code paths — the sync and async
    wrappers in @template must stay behaviorally identical."""
    return request.param


@pytest.fixture
def make_view():
    """Build a sync or async handler from a plain body function and decorate it."""

    def _make(style, decorator, body):
        if style == 'sync':

            @decorator
            @wraps(body)
            def view(*args, **kwargs):
                return body(*args, **kwargs)

            return view

        @decorator
        @wraps(body)
        async def async_view(*args, **kwargs):
            return body(*args, **kwargs)

        return async_view

    return _make


@pytest.fixture
def call_view():
    """Call a decorated handler, running async handlers to completion."""

    def _call(view, *args, **kwargs):
        if inspect.iscoroutinefunction(view):
            return asyncio.run(view(*args, **kwargs))
        return view(*args, **kwargs)

    return _call
