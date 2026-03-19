# chameleon-robyn

> **Note:** This project is very much in the alpha and early stages of development. Feel free to use it, but no promises on API stability for a few versions.

Use [Chameleon](https://chameleon.readthedocs.io/) page templates in your [Robyn](https://robyn.tech/) web applications. If you've used Chameleon with Pyramid, Flask, or FastAPI, you'll feel right at home - same `.pt` templates, same TAL/TALES/METAL expressions, now running on Robyn's blazing-fast Rust runtime.

## Installation

```bash
uv pip install chameleon-robyn
```

This pulls in `chameleon` and `robyn` as dependencies.

## Quick start

**1. Set up your project structure:**

```
my_app/
├── app.py
└── templates/
    └── home/
        └── index.pt
```

**2. Create a template** (`templates/home/index.pt`):

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

**3. Wire it up** (`app.py`):

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

That's it. Your handler returns a `dict`, the `@template` decorator renders it through the Chameleon template and wraps the result in a Robyn `Response`.

## The `@template` decorator

The decorator is the main way you'll use this package. It intercepts your handler's return value and renders it through a Chameleon template.

### Explicit template path

```python
@app.get('/episodes')
@chameleon_robyn.template('episodes/list.pt')
def episode_list(request):
    return {'episodes': get_all_episodes()}
```

### Auto-naming (convention over configuration)

If you omit the template path, it's derived from the module and function name. A function called `index` in a module called `home_views` looks for `home_views/index.pt` (falling back to `home_views/index.html`):

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

### Async handlers - just works

```python
@app.get('/dashboard')
@chameleon_robyn.template('dashboard.pt')
async def dashboard(request):
    stats = await fetch_stats_from_db()
    return {'stats': stats}
```

### Custom status codes and content types

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

If your handler returns a Robyn `Response` object directly, the decorator passes it through untouched. This is how you handle redirects, custom error responses, or anything that shouldn't be rendered through a template:

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

## Friendly 404 pages

Call `not_found()` from any decorated handler to render a 404 page:

```python
@app.get('/episodes/:episode_id')
@chameleon_robyn.template('episodes/detail.pt')
async def episode_detail(request, episode_id: int):
    episode = await get_episode(episode_id)
    if not episode:
        chameleon_robyn.not_found()  # Renders errors/404.pt with status 404

    return {'episode': episode}
```

By default it renders `errors/404.pt`, but you can specify any template:

```python
chameleon_robyn.not_found(four04template_file='errors/custom_404.pt')
```

## Lower-level API

Sometimes you need to render a template outside of a decorator - in middleware, error handlers, or helper functions.

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

## `ChameleonTemplate` class (Robyn's TemplateInterface)

If you prefer Robyn's built-in template pattern, `ChameleonTemplate` implements `TemplateInterface` - the same abstract base class that Robyn's `JinjaTemplate` uses:

```python
from chameleon_robyn import ChameleonTemplate

chameleon = ChameleonTemplate('templates/', auto_reload=True)

@app.get('/page')
def page(request):
    return chameleon.render_template('page.pt', title='Hello')
```

This is a standalone class with its own template loader - it doesn't require `global_init()`.

## `global_init()` reference

```python
chameleon_robyn.global_init(
    template_folder,              # Path to your templates directory (required)
    auto_reload=False,            # Watch for template changes - use True in development
    cache_init=True,              # Skip re-initialization if already called
    restricted_namespace=True,    # Set to False if using Alpine.js, htmx @attributes, etc.
)
```

### Alpine.js / htmx compatibility

Chameleon's default namespace rules reject attributes like `@click` or `:class` because they look like XML namespace prefixes. If you're using Alpine.js, htmx, or similar libraries, set `restricted_namespace=False`:

```python
chameleon_robyn.global_init(template_folder, restricted_namespace=False)
```

This tells Chameleon to allow any attribute syntax in your templates.

## Works with chameleon-partials

[chameleon-partials](https://github.com/mikeckennedy/chameleon-partials) provides `render_partial()` for rendering sub-templates (think: reusable components). It works alongside `chameleon-robyn` with no extra configuration - just initialize both at startup:

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

The repo includes two example apps you can run to see everything in action.

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

A Robyn app demonstrating the `@template` decorator, sync and async handlers, METAL macro layout inheritance, response pass-through redirects, friendly 404 pages, search with query parameters, and an XML feed with a custom content type.

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

Compare the two to see how partials reduce template duplication - the episode list and search results templates go from inline card markup to a single `tal:replace` call each.

## Template language cheat sheet

Chameleon uses TAL (Template Attribute Language) - a few patterns to get you going:

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

Full docs: [chameleon.readthedocs.io](https://chameleon.readthedocs.io/)

## License

MIT
