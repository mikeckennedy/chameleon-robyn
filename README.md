# chameleon-robyn

> **Note:** This project is very much in the alpha and early stages of development. Feel free to use it, but no promises on API stability for a few versions.

Every web framework eventually asks the same question: how do you turn data into HTML? [Robyn](https://robyn.tech/) answers with Jinja2 out of the box. This package offers a second answer, the one people who built on Pyramid or Zope tend to miss the moment they leave: [Chameleon](https://chameleon.readthedocs.io/) page templates. Same `.pt` files, same TAL/TALES/METAL expressions, now running on Robyn's Rust-powered runtime.

A Chameleon template is an ordinary HTML file. Open one in a browser before it has ever been rendered and you still see a page, because the logic lives inside attributes the browser ignores. `tal:repeat` loops, `tal:condition` hides, and `${...}` fills in values with real Python expressions. chameleon-robyn wires those templates into Robyn with a single decorator: your handler returns a `dict`, and a rendered `Response` comes out the other side.

## Documentation

Full documentation lives at [mkennedy.codes/docs/chameleon-robyn](https://mkennedy.codes/docs/chameleon-robyn/). This README covers the same ground in short form; the user guide follows one podcast website from its first page to its last error message and goes deeper on each section:

- [Getting started](https://mkennedy.codes/docs/chameleon-robyn/user-guide/getting-started.html), [the @template decorator](https://mkennedy.codes/docs/chameleon-robyn/user-guide/template-decorator.html), [writing templates](https://mkennedy.codes/docs/chameleon-robyn/user-guide/templates.html), [friendly 404 pages](https://mkennedy.codes/docs/chameleon-robyn/user-guide/not-found.html)
- [Rendering outside handlers](https://mkennedy.codes/docs/chameleon-robyn/user-guide/lower-level-api.html), [configuration](https://mkennedy.codes/docs/chameleon-robyn/user-guide/configuration.html), [testing your handlers](https://mkennedy.codes/docs/chameleon-robyn/user-guide/testing.html), [errors and how to fix them](https://mkennedy.codes/docs/chameleon-robyn/user-guide/troubleshooting.html)
- [How it works](https://mkennedy.codes/docs/chameleon-robyn/user-guide/how-it-works.html), [FAQ](https://mkennedy.codes/docs/chameleon-robyn/user-guide/faq.html), and the [API reference](https://mkennedy.codes/docs/chameleon-robyn/reference/)

Coding agents can read [llms-full.txt](https://mkennedy.codes/docs/chameleon-robyn/llms-full.txt) or install the [agent skill](https://mkennedy.codes/docs/chameleon-robyn/skills.html).

## Installation

```bash
uv pip install chameleon-robyn
```

This pulls in `chameleon` and `robyn` as dependencies. Python 3.10 or newer is required.

## Quick start

Three files, three minutes. Here is the shortest path from an empty folder to a rendered page.

**1. Set up your project structure:**

```text
my_app/
├── app.py
└── templates/
    └── home/
        └── index.pt
```

**2. Create a template** (`templates/home/index.pt`). It is plain HTML with two new ideas: `${name}` drops in a value, and `tal:repeat` on an element makes that element repeat.

```xml
<!DOCTYPE html>
<html>
<body>
    <h1>Hello, ${name}!</h1>
    <ul>
        <li tal:repeat="item items">${item}</li>
    </ul>
</body>
</html>
```

**3. Wire it up** (`app.py`). Three lines matter: the import, the `global_init()` call that says where templates live, and the decorator above the handler.

```python
from pathlib import Path
from robyn import Robyn
import chameleon_robyn

app = Robyn(__file__)

# Point Chameleon at your templates folder (do this once at startup)
template_folder = (Path(__file__).resolve().parent / 'templates').as_posix()
chameleon_robyn.global_init(template_folder, auto_reload=True)

@app.get('/')
@chameleon_robyn.template('home/index.pt')
async def index(request):
    return {'name': 'World', 'items': ['Robyn', 'Chameleon', 'Python']}

app.start(host='127.0.0.1', port=8000)
```

That's it. Your handler returns a `dict`, the `@template` decorator renders it through the Chameleon template and wraps the result in a Robyn `Response`. The handler never touched a string of HTML, and it never will. The [getting started guide](https://mkennedy.codes/docs/chameleon-robyn/user-guide/getting-started.html) walks through this in more detail.

## The `@template` decorator

A route handler has two jobs: decide what to show, and show it. `@template` takes the second job away entirely. It intercepts your handler's return value and renders it through a Chameleon template, so the handler reads like a description of the page rather than a construction of it.

### Explicit template path

```python
@app.get('/episodes')
@chameleon_robyn.template('episodes/list.pt')
def episode_list(request):
    return {'episodes': get_all_episodes()}
```

### Auto-naming (convention over configuration)

Leave the path out and the template is named after the code that renders it. A function called `index` in a module called `home_views` looks for `home_views/index.html` first and, if that file doesn't exist, uses `home_views/index.pt`. Your template folder ends up mirroring your view modules, which is a pleasant thing to discover six months later.

```python
# Looks for templates/home_views/index.pt
@app.get('/')
@chameleon_robyn.template()
def index(request):
    return {'message': 'Hello!'}
```

You can even skip the parentheses:

```python
@app.get('/')
@chameleon_robyn.template
def index(request):
    return {'message': 'Hello!'}
```

Two details: a script run directly (`python app.py`) has the module name `__main__`, so the script's file name is used instead and `index()` in `app.py` maps to `app/index.pt` (an existing `__main__/index.pt` is still found for apps built on the old behavior). And the name is resolved at the first request, not when the decorator runs, so `global_init()` can be called after the routes are decorated.

### Async handlers - just works

The decorator notices `async def` and awaits the handler. Nothing to configure.

```python
@app.get('/dashboard')
@chameleon_robyn.template('dashboard.pt')
async def dashboard(request):
    stats = await fetch_stats_from_db()
    return {'stats': stats}
```

### Custom status codes and content types

Templates are not only for HTML pages. An XML feed is a template too, and so is the "created" page after a form post.

```python
# Return a 201 after creating a resource
@app.post('/items')
@chameleon_robyn.template('items/created.pt', status_code=201)
async def create_item(request):
    item = await save_item(request.json())
    return {'item': item}

# Serve an XML feed
@app.get('/feed.xml')
@chameleon_robyn.template('feed.xml', content_type='application/xml')
def xml_feed(request):
    return {'episodes': get_recent_episodes()}
```

### Response pass-through (redirects, errors, etc.)

Sometimes the right answer is not a page at all. If your handler returns a Robyn `Response` object directly, the decorator steps aside and passes it through untouched. This is how you handle redirects, custom error responses, or anything that shouldn't be rendered through a template:

```python
from robyn import Response, Headers

@app.get('/old-page')
@chameleon_robyn.template('home/index.pt')
def old_page(request):
    # This Response is returned as-is - no template rendering
    return Response(
        status_code=302,
        description='',
        headers=Headers({'Location': '/new-page'}),
    )
```

### Modifying the response after rendering (`__response_callback__`)

Here is the classic puzzle. A visitor logs in. You want to render the welcome page, which means returning a dict, and you also want to set a session cookie, which means touching the `Response`. You cannot do both from a dict. Or can you?

Put a callable in your model under the reserved `__response_callback__` key and the decorator invokes it with the freshly built `Response` after rendering:

```python
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

A few details:

- The key is popped before rendering, so it never reaches your template (and your dict isn't mutated - returning a shared model is fine).
- Mutate the `Response` in place; the callback's return value is ignored.
- The value must be callable - anything else raises `ChameleonRobynException`.

Everything the decorator does, including the exact return-value contract, is in [the decorator guide](https://mkennedy.codes/docs/chameleon-robyn/user-guide/template-decorator.html).

## Friendly 404 pages

Sooner or later someone will visit `/episodes/9999`. What they should get is a page in your site's own clothes that points the way home, not a stack trace. Call `not_found()` from any decorated handler:

```python
@app.get('/episodes/:episode_id')
@chameleon_robyn.template('episodes/detail.pt')
async def episode_detail(request, episode_id: int):
    episode = await get_episode(episode_id)
    if not episode:
        chameleon_robyn.not_found()  # Renders errors/404.pt with status 404

    return {'episode': episode}
```

Notice there is no `return` in front of `not_found()`. It never returns; the decorator catches what it raises and sends the 404 page instead. By default it renders `errors/404.pt`, but you can specify any template:

```python
chameleon_robyn.not_found(four04template_file='errors/custom_404.pt')
```

The 404 template receives a `message` variable describing the 404, which you can render with `${message}` if you want. To supply your own message, raise `ChameleonRobynNotFoundException('your text')` directly; the decorator handles it the same way. `not_found()` only works inside `@template`-decorated handlers; see [friendly 404 pages](https://mkennedy.codes/docs/chameleon-robyn/user-guide/not-found.html) for the alternatives.

## Lower-level API

The decorator is the front door. A web app renders HTML in more places than route handlers, though: the body of a welcome email, an error page built in middleware, a fragment assembled in a helper. For those there is a side door.

### `render()` - get an HTML string

```python
html = chameleon_robyn.render('emails/welcome.pt', username='Michael')
# Returns a string, no Response wrapping
```

### `response()` - get a Robyn Response

```python
resp = chameleon_robyn.response('errors/500.pt', status_code=500, error=str(e))
# Returns a fully-formed Robyn Response object
```

One reserved name: a template variable called `encoding` cannot be passed, because Chameleon's own `render()` takes it as a parameter. The library raises `ChameleonRobynException` if you try. More in [rendering outside handlers](https://mkennedy.codes/docs/chameleon-robyn/user-guide/lower-level-api.html).

## `ChameleonTemplate` class (Robyn's TemplateInterface)

If you prefer Robyn's built-in template pattern, `ChameleonTemplate` implements the same `render_template()` interface as Robyn's `JinjaTemplate` (via a structural protocol, so importing `chameleon_robyn` never pulls in Jinja2):

```python
from chameleon_robyn import ChameleonTemplate

chameleon = ChameleonTemplate('templates/', auto_reload=True)

@app.get('/page')
def page(request):
    return chameleon.render_template('page.pt', title='Hello')
```

This is a standalone class with its own template loader - it doesn't require `global_init()`. `render_template()` always returns a 200 `text/html` response.

## `global_init()` reference

All configuration is one call at startup. No environment variables, no config files.

```python
chameleon_robyn.global_init(
    template_folder,              # Path to your templates directory (required)
    auto_reload=False,            # Watch for template changes - use True in development
    cache_init=True,              # Skip re-initialization if already called
    restricted_namespace=True,    # Set to False if using Alpine.js, htmx @attributes, etc.
)
```

### Alpine.js / htmx compatibility

Here is a surprise waiting for anyone who adds a sprinkle of Alpine.js to a Chameleon page. Chameleon's default namespace rules reject attributes like `@click` or `:class` because they look like XML namespace prefixes it has never heard of. If you're using Alpine.js, htmx, or similar libraries, set `restricted_namespace=False`:

```python
chameleon_robyn.global_init(template_folder, restricted_namespace=False)
```

This tells Chameleon to allow any attribute syntax in your templates. Every `global_init()` setting is described in [configuration](https://mkennedy.codes/docs/chameleon-robyn/user-guide/configuration.html).

## Works with chameleon-partials

The episode card appears on the list page and again in search results. Copying it once is fine; copying it a third time is how layouts drift. [chameleon-partials](https://github.com/mikeckennedy/chameleon-partials) provides `render_partial()` for rendering sub-templates (think: reusable components). It works alongside `chameleon-robyn` with no extra configuration - just initialize both at startup:

```python
import chameleon_partials
import chameleon_robyn

chameleon_robyn.global_init(template_folder, auto_reload=dev_mode)
chameleon_partials.register_extensions(template_folder, auto_reload=dev_mode)
```

Then pass `render_partial` through your template context:

```python
import chameleon_partials

@app.get('/')
@chameleon_robyn.template('home/index.pt')
def index(request):
    return {
        'render_partial': chameleon_partials.render_partial,
        'episodes': get_episodes(),
    }
```

And use it in your templates with `tal:replace="structure ..."`:

```xml
<div tal:repeat="ep episodes">
    <div tal:replace="structure render_partial('shared/episode_card.pt', ep=ep)" />
</div>
```

Note: use `tal:replace="structure ..."` (not `${structure ...}`) when rendering partials. The `structure` keyword tells Chameleon to insert the HTML without escaping, and `tal:replace` swaps out the placeholder element entirely.

## Example apps

The repo includes two example apps you can run to see everything in action. Both are the website for a small podcast: episodes, guests, search, a feed, and the occasional lost visitor.

### Setup

Clone the repo and install with the extras you need:

```bash
git clone https://github.com/mikeckennedy/chameleon-robyn.git
cd chameleon-robyn
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install the package with example dependencies
pip install -e ".[examples]"
```

### `example/` - Core features

A Robyn app demonstrating the `@template` decorator, sync and async handlers, METAL macro layout inheritance, response pass-through redirects, a `__response_callback__` cookie example, friendly 404 pages, search with query parameters, and an XML feed with a custom content type.

```bash
python example/app.py
# Open http://127.0.0.1:5555
```

### `example-partials/` - With chameleon-partials

The same app, but refactored to use [chameleon-partials](https://github.com/mikeckennedy/chameleon-partials) for reusable template components. The episode card markup lives in a single `shared/episode_card.pt` partial that's shared across the episodes list and search results pages.

```bash
python example-partials/app.py
# Open http://127.0.0.1:5555
```

Open the two episode list templates side by side and watch a block of card markup collapse into a single `tal:replace` call.

## Template language cheat sheet

Chameleon uses TAL (Template Attribute Language). Most template languages ask you to learn a second syntax; Chameleon asks you to learn a handful of attributes. Here are the ones you will reach for every day:

```xml
<!-- Variable substitution -->
<h1>${title}</h1>
<p>${user.name}</p>

<!-- HTML-safe output (skip auto-escaping) -->
<div tal:replace="structure rich_html_content" />

<!-- Conditionals -->
<div tal:condition="show_banner">Special offer!</div>
<div tal:condition="not items">Nothing here yet.</div>

<!-- Loops -->
<li tal:repeat="item items">${item.name} - $${item.price}</li>

<!-- Repeat with index -->
<tr tal:repeat="row data" class="${'odd' if repeat.row.odd else 'even'}">
    <td>${repeat.row.number}. ${row.title}</td>
</tr>

<!-- Attributes -->
<a href="/items/${item.id}" class="${'active' if is_current else ''}">
    ${item.name}
</a>

<!-- Layout inheritance with METAL macros -->
<!-- layout.pt -->
<html>
<body>
    <main metal:define-slot="content">Default content</main>
</body>
</html>

<!-- page.pt -->
<metal:block use-macro="load: shared/layout.pt">
<div metal:fill-slot="content">
    <h1>My page content here</h1>
</div>
</metal:block>
```

Full docs: [chameleon.readthedocs.io](https://chameleon.readthedocs.io/). The [writing templates](https://mkennedy.codes/docs/chameleon-robyn/user-guide/templates.html) guide covers layouts, escaping, and partials in more depth.

## Testing and troubleshooting

The best thing about a decorated handler is that it is still a function. Tests call it directly and assert on the returned Robyn `Response`, with no server to start; see [testing your handlers](https://mkennedy.codes/docs/chameleon-robyn/user-guide/testing.html). When something goes wrong, [errors and how to fix them](https://mkennedy.codes/docs/chameleon-robyn/user-guide/troubleshooting.html) is a field guide to every exception the library and Chameleon raise, and what to change.

## License

MIT
