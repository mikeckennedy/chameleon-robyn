# The <span class="citation" cites="template">@template</span> decorator

A route handler has two jobs: decide what to show, and show it. `@template` takes the second job away entirely. Your handler gathers data and returns a `dict`. The decorator finds the template, renders it, builds the `Response`, and sets the headers. You never see a string of HTML in Python again, and the handler reads like a description of the page rather than a construction of it.


# The contract

Everything the decorator does follows from one rule about what your handler returns:

| Handler returns | What the decorator does |
|----|----|
| a `dict` | Renders the template with the dict as its variables and returns a 200 `Response` (or the status you configured). |
| a Robyn `Response` | Returns it untouched. No template is rendered. This is the escape hatch for redirects and hand-built responses. |
| anything else | Raises [ChameleonRobynException](../reference/ChameleonRobynException.md#chameleon_robyn.ChameleonRobynException) at request time. `None`, strings and numbers are all rejected. |

Return the dict directly. The decorator copies it before rendering, so returning a shared or module-level dict is safe.


# Explicit template path

The podcast's episode list is the plainest possible case:

``` python
@app.get('/episodes')
@chameleon_robyn.template('episodes/list.pt')
def episode_list(request):
    return {'episodes': get_all_episodes()}
```

The path is relative to the folder passed to [global_init()](../reference/global_init.md#chameleon_robyn.global_init). Any file extension works; `.pt` is the convention, and the same site renders a `.xml` feed with the same decorator.


# Auto-naming

Leave the path out and the decorator names the template after the code that renders it. The rule has three steps:

1.  Take the last segment of the handler's module name and the function name.
2.  Look for `<module>/<function>.html` under the template folder.
3.  If that file does not exist, use `<module>/<function>.pt`.

So `index()` in `views/home_views.py` renders `home_views/index.html` if it exists, otherwise `home_views/index.pt`. Your template folder ends up mirroring your view modules, which is a pleasant thing to discover six months later.

``` python
# Looks for templates/home_views/index.pt
@app.get('/')
@chameleon_robyn.template()
def index(request):
    return {'message': 'Hello!'}
```

The parentheses are optional:

``` python
@app.get('/')
@chameleon_robyn.template
def index(request):
    return {'message': 'Hello!'}
```

Two details are worth knowing:

- A script run directly (`python app.py`) has the module name `__main__`, which would make for a strange folder name. The library uses the script's file name instead, so `index()` in `app.py` maps to `app/index.pt`. If no such file exists but `__main__/index.html` or `__main__/index.pt` does, that is used, so apps built on the old behavior keep working.
- The name is resolved at the first request, not when the decorator runs. That is what lets you decorate routes at import time and call [global_init()](../reference/global_init.md#chameleon_robyn.global_init) later from `main()`. The file only has to exist by the time the first visitor arrives.


# Async handlers

Nothing to configure. The decorator notices `async def` and awaits the handler, so the episode page can go to the database like any other coroutine:

``` python
@app.get('/dashboard')
@chameleon_robyn.template('dashboard.pt')
async def dashboard(request):
    stats = await fetch_stats_from_db()
    return {'stats': stats}
```

Robyn's typed path parameters pass straight through:

``` python
@app.get('/episodes/:episode_id')
@chameleon_robyn.template('episodes/detail.pt')
async def episode_detail(request, episode_id: int):
    return {'episode': await get_episode(episode_id)}
```


# Status codes and content types

Templates are not only for HTML pages. The podcast feed is a Chameleon template too, and so is a "created" page after a form post:

``` python
# Return a 201 after creating a resource
@app.post('/items')
@chameleon_robyn.template('items/created.pt', status_code=201)
async def create_item(request):
    item = await save_item(request.json())
    return {'item': item}

# Serve an XML feed
@app.get('/feed.xml')
@chameleon_robyn.template('episodes/feed.xml', content_type='application/xml')
def xml_feed(request):
    return {'episodes': get_recent_episodes()}
```

The `charset=utf-8` suffix is added to the content type for you. These settings apply to rendered responses only. A pass-through `Response` keeps its own status and headers, and a 404 from [not_found()](../reference/not_found.md#chameleon_robyn.not_found) always renders as `text/html` with status 404.


# Redirects and other pass-through responses

Sometimes the right answer is not a page at all. Return a Robyn `Response` and the decorator steps aside:

``` python
from robyn import Response, Headers

@app.get('/old-page')
@chameleon_robyn.template('home/index.pt')
def old_page(request):
    return Response(
        status_code=302,
        description='',
        headers=Headers({'Location': '/new-page'}),
    )
```

The same rule lets one handler choose between templates at runtime: build the alternative with [`response()`](lower-level-api.md) and return it.


# Setting cookies or headers on a rendered page

Here is the classic puzzle. A visitor logs in. You want to render the welcome page, which means returning a dict, and you also want to set a session cookie, which means touching the `Response`. You cannot do both from a dict. Or can you?

Put a callable under the reserved key `__response_callback__` in the returned dict. After rendering, the decorator calls it with the `Response` it just built:

``` python
from robyn import Response

@app.post('/account/login')
@chameleon_robyn.template('account/welcome.pt')
async def login(request):
    user = await authenticate(request)
    if not user:
        return chameleon_robyn.response('account/login_failed.pt', status_code=401)

    token = create_session_token(user)

    def set_session_cookie(resp: Response):
        resp.headers.append('Set-Cookie', f'session={token}; HttpOnly; Path=/')

    return {
        'user': user,
        '__response_callback__': set_session_cookie,
    }
```

Rules for the callback:

- It is removed from the model before rendering, so the template never sees it, and your dict is not modified.
- Change the `Response` in place. The return value is ignored.
- It must be callable. Anything else raises [ChameleonRobynException](../reference/ChameleonRobynException.md#chameleon_robyn.ChameleonRobynException).


# Decorator order

Robyn's route decorator goes on the outside and `@template` goes directly above the function. Robyn reads the handler's signature when the route is registered, and the decorator preserves the original signature, so `request` and path parameters keep flowing exactly as they did before.

``` python
@app.get('/episodes')                          # outermost
@chameleon_robyn.template('episodes/list.pt')  # directly above the function
def episode_list(request):
    ...
```
