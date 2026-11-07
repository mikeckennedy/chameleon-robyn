# Testing your handlers

The best thing about a decorated handler is that it is still a function. No server needs to start, no HTTP client needs to connect, and nothing needs to be mocked. Call the handler, get a Robyn `Response` back, and assert on it. This is how the package's own test suite works, and it keeps a full run of the suite well under a second.


# Point the engine at test templates

The one piece of setup is telling the engine where the test templates live. Use a fixture that initializes with `cache_init=False`, so each test gets the folder it asks for, and clears afterwards:

``` python
# conftest.py
from pathlib import Path
import pytest
import chameleon_robyn

@pytest.fixture
def templates():
    folder = Path(__file__).parent / 'templates'
    chameleon_robyn.global_init(str(folder), cache_init=False)
    yield
    chameleon_robyn.clear()
```

Skip `cache_init=False` and you meet the sharp edge from [Configuration](configuration.md#calling-it-twice): the first [global_init()](../reference/global_init.md#chameleon_robyn.global_init) in the session wins, every later fixture silently keeps its settings, and you spend an afternoon wondering why the wrong template renders.


# Call the handler

``` python
from robyn import Response
import chameleon_robyn

def test_index_renders(templates):
    @chameleon_robyn.template('home/index.pt')
    def index(request):
        return {'name': 'World', 'items': ['a', 'b']}

    resp = index(None)
    assert isinstance(resp, Response)
    assert resp.status_code == 200
    assert 'Hello, World!' in resp.description
    assert 'text/html' in resp.headers.get('content-type')
```

The rendered HTML is in `resp.description`. Headers are a Robyn `Headers` object with `get()`.

Handlers usually take a `request` argument. Pass `None` or a simple stand-in when the handler does not use it, or test the handler's logic through a helper function that the handler calls.


# Async handlers

Run the coroutine to completion:

``` python
import asyncio

def test_async_detail(templates):
    @chameleon_robyn.template('episodes/detail.pt')
    async def detail(request, episode_id: int):
        return {'episode': {'id': episode_id, 'title': 'Test'}}

    resp = asyncio.run(detail(None, 7))
    assert resp.status_code == 200
```


# Testing a 404

The 404 path is a function call like any other, which makes the "episode does not exist" branch one of the easiest tests you will write:

``` python
def test_missing_episode_is_404(templates):
    @chameleon_robyn.template('episodes/detail.pt')
    def detail(request, episode_id: int):
        chameleon_robyn.not_found()

    resp = detail(None, 999)
    assert resp.status_code == 404
    assert 'not found' in resp.description.lower()
```


# Testing the response callback

The callback receives the built `Response`, so check the header it set:

``` python
def test_login_sets_cookie(templates):
    @chameleon_robyn.template('account/welcome.pt')
    def login(request):
        def set_cookie(resp):
            resp.headers.append('Set-Cookie', 'session=abc; Path=/')
        return {'user': 'michael', '__response_callback__': set_cookie}

    resp = login(None)
    assert resp.headers.get('set-cookie') == 'session=abc; Path=/'
```


# Testing templates on their own

[render()](../reference/render.md#chameleon_robyn.render) returns the HTML as a string, which keeps assertions about markup separate from assertions about handler logic:

``` python
def test_episode_card_shows_title(templates):
    html = chameleon_robyn.render('shared/episode_card.pt', ep={'title': 'Async All the Things'})
    assert 'Async All the Things' in html
```


# What not to test

Chameleon's own behaviour, such as escaping, `tal:repeat` ordering, or the wording of its error messages, is covered by Chameleon's test suite. Spend your tests on what your handlers return and what your templates show.
