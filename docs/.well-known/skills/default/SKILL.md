---
name: chameleon-robyn
description: >
  Adds integration of the Chameleon template language to Robyn. Use when writing Python code that uses the chameleon_robyn package.
license: MIT
compatibility: Requires Python >=3.10.
---

# chameleon-robyn

Adds integration of the Chameleon template language to Robyn.

## Installation

```bash
pip install chameleon-robyn
```

## When to use what

| Need | Use |
|------|-----|
| Render a Chameleon template from a Robyn route handler | `@chameleon_robyn.template('home/index.pt') on the handler` |
| Return a friendly 404 page from a handler | `chameleon_robyn.not_found()` |
| Set a cookie or header on a rendered page | `'__response_callback__': callable in the returned dict` |
| Build a rendered Response outside a decorated handler | `chameleon_robyn.response(template_file, **model)` |
| Get rendered HTML as a plain string | `chameleon_robyn.render(template_file, **model)` |
| Use Robyn's built-in template-engine pattern instead of the global API | `ChameleonTemplate(directory).render_template(name, **model)` |
| Use Alpine.js/htmx shorthand attributes in templates | `global_init(..., restricted_namespace=False)` |

## API overview

### Setup & configuration

Initialize the template engine once at app startup.

- `global_init`: Initialize the Chameleon template engine
- `clear`: Reset the template engine to its uninitialized state

### Rendering views

The @template decorator and friendly 404s for Robyn route handlers.

- `template`: Decorate a Robyn view method to render an HTML response
- `not_found`: Render a friendly 404 page from within a @template-decorated handler

### Lower-level rendering

Render templates outside the decorator (middleware, error handlers, emails).

- `render`: Render a Chameleon template to a string (no Response wrapping)
- `response`: Render a Chameleon template and wrap it in a fully-formed Robyn Response

### Robyn TemplateInterface

Standalone template engine class matching Robyn's built-in template pattern.

- `ChameleonTemplate`: Chameleon template engine implementing Robyn's TemplateInterface

### Exceptions

Exception types raised by the library.

- `ChameleonRobynException`: Base exception for all chameleon-robyn errors (bad configuration, invalid return types, etc.)
- `ChameleonRobynNotFoundException`: Raised by not_found() to signal a 404 from within a @template-decorated handler

## Gotchas

1. global_init() is one-shot by default: with cache_init=True, later calls are silently ignored. Pass cache_init=False or call chameleon_robyn.clear() to re-initialize.
2. Bare @template auto-naming resolves lazily at the FIRST REQUEST, not at decoration time — so global_init() may be called after routes are decorated, but the derived {module}/{function}.html|.pt file must exist under the template folder by then.
3. Decorated handlers must return a dict (the template model) or a robyn.Response; any other return type raises ChameleonRobynException at request time.
4. Chameleon's restricted namespace (the default) rejects Alpine.js/htmx shorthand attributes like @click, :class, and x-data. Pass restricted_namespace=False to global_init() to allow them.
5. The 404 path from not_found() always renders with text/html and status 404; the handler's own content_type and status_code do not apply. not_found() only works inside @template-decorated handlers.
6. __response_callback__ is a reserved model key: it must be callable (else ChameleonRobynException), is popped before rendering, and never reaches the template.

## Best practices

- Call global_init(template_folder, auto_reload=dev_mode) exactly once at app startup — e.g. in main() before app.start(); decorating routes at import time first is fine.
- Return plain dicts from handlers; return a robyn.Response only for redirects and other pass-through cases.
- Enable auto_reload only during development so templates stay cached in production.
- Put @template below the Robyn route decorator (closest to the function).
- Use chameleon_robyn.response() or render() in error handlers, middleware, and emails where the decorator doesn't fit.

## End-to-end wiring

A complete, minimal app — routes decorated at import time, engine initialized in `main()`, and the template it renders. The `@template` path is always relative to the folder passed to `global_init()`.

```python
# app.py
from pathlib import Path
from robyn import Robyn
import chameleon_robyn

app = Robyn(__file__)


@app.get('/')
@chameleon_robyn.template('home/index.pt')   # Robyn route decorator OUTERMOST, @template just above the function
async def index(request):
    return {'title': 'Home', 'items': ['a', 'b', 'c']}   # dict == the template model


def main():
    # Init once at startup. Auto-named templates resolve lazily at first request,
    # so calling global_init() here — after the routes are decorated — is the normal pattern.
    templates = (Path(__file__).resolve().parent / 'templates').as_posix()
    chameleon_robyn.global_init(templates, auto_reload=True)  # auto_reload for dev only
    app.start(host='127.0.0.1', port=8000)


if __name__ == '__main__':
    main()
```

```html
<!-- templates/home/index.pt -->
<!DOCTYPE html>
<html lang="en">
<body>
  <h1>${title}</h1>
  <ul>
    <li tal:repeat="item items">${item}</li>
  </ul>
</body>
</html>
```

## Chameleon template syntax (this is TAL, not Jinja)

Chameleon templates are valid XML/HTML where directives live in `tal:`, `metal:`, and `i18n:` attributes. There is no `{% ... %}` or `{{ ... }}` — do not use Jinja/Django syntax. Interpolation uses `${ ... }` and may contain arbitrary Python expressions.

```html
<!-- Interpolation: any Python expression inside ${ } -->
<h1>Hello, ${user.name.title()}!</h1>
<p>You have ${len(items)} item(s).</p>

<!-- Loop -->
<li tal:repeat="item items">${item.name} — ${item.price}</li>

<!-- The repeat variable exposes index/number/even/odd/first/last -->
<li tal:repeat="item items" class="${'odd' if repeat.item.odd else 'even'}">
  ${repeat.item.number}. ${item}
</li>

<!-- Condition (element is omitted entirely when falsy) -->
<div tal:condition="user">Welcome back, ${user.name}.</div>
<div tal:condition="not user">Please sign in.</div>

<!-- Set element content / replace whole element -->
<span tal:content="message">placeholder shown only in a browser preview</span>
<span tal:replace="formatted_date">2024-01-01</span>

<!-- Set attributes (semicolon-separated); escaping is automatic -->
<a tal:attributes="href item.url; class item.css_class">${item.name}</a>

<!-- Define a reusable local variable -->
<span tal:define="total sum(i.price for i in items)">Total: ${total}</span>
```

Escaping is on by default (`${expr}` is HTML-escaped). Use `structure` to emit already-safe HTML without escaping: `<div tal:replace="structure rich_html_content" />`.

## Shared layouts with METAL macros

METAL is how Chameleon does template inheritance / partials — the equivalent of Jinja's `{% extends %}`/`{% block %}`.

```html
<!-- templates/shared/layout.pt -->
<html>
  <head><title>${title}</title></head>
  <body>
    <main metal:define-slot="content">default content</main>
  </body>
</html>
```

```html
<!-- templates/home/index.pt -->
<metal:block use-macro="load: shared/layout.pt">
<div metal:fill-slot="content">
  <h1>${title}</h1>
</div>
</metal:block>
```

## Template resolution & project layout

With an explicit path (`@template('episodes/detail.pt')`) the string is resolved relative to the `global_init()` folder. With the bare form (`@template` or `@template()`) the path is derived as `{last segment of module}/{function_name}.html`, falling back to `.pt` if the `.html` file does not exist on disk. Auto-naming resolves lazily at the first request — not at decoration time — so decorating routes at import and calling `global_init()` later from `main()` works.

```
my_app/
├── app.py                 # routes at import time; global_init() in main()
├── templates/
│   ├── home/index.pt      # bare @template on home.index() finds this
│   ├── errors/404.pt      # default target of not_found()
│   └── shared/layout.pt   # METAL macros
└── static/
```

## Robyn specifics

Sync and async handlers both work with the same decorator — async is detected automatically, no flag needed. Handlers receive Robyn's `request` plus any typed route params (`@app.get('/episodes/:episode_id')` → `def detail(request, episode_id: int)`), and the decorator forwards them untouched. Returning a `robyn.Response` from a decorated handler skips templating entirely — that's how redirects work:

```python
from robyn import Headers, Response

@app.get('/old-page')
@chameleon_robyn.template('home/index.pt')
def old_page(request):
    return Response(status_code=302, description='', headers=Headers({'Location': '/new-page'}))
```

## Setting cookies/headers on a rendered page (`__response_callback__`)

To render a template AND tweak the final `Response` (the classic case: a session cookie after login), put a callable under the reserved `__response_callback__` key in the returned dict. It is popped before rendering (never reaches the template, never mutates your dict) and called with the built `Response` — mutate it in place; the return value is ignored.

```python
@app.post('/account/login')
@chameleon_robyn.template('account/welcome.pt')
async def login(request):
    token = await sign_in(request)

    def set_cookie(resp):
        resp.headers.append('Set-Cookie', f'session={token}; HttpOnly; Path=/')

    return {'user': token.user, '__response_callback__': set_cookie}
```

## Standalone engine (Robyn's TemplateInterface pattern)

`ChameleonTemplate` mirrors Robyn's built-in `JinjaTemplate` usage and needs no `global_init()` — it owns its own loader. It matches Robyn's interface through a structural Protocol, so importing `chameleon_robyn` never pulls in Jinja2.

```python
from chameleon_robyn import ChameleonTemplate

chameleon = ChameleonTemplate('templates/', auto_reload=True)

@app.get('/page')
def page(request):
    return chameleon.render_template('page.pt', title='Hello')  # always a 200 Response
```

## Reusable components with chameleon-partials

The [chameleon-partials](https://github.com/mikeckennedy/chameleon-partials) package works alongside chameleon-robyn with no extra configuration: initialize both at startup, pass `render_partial` through the model, and insert with `tal:replace="structure ..."` (the `structure` keyword prevents escaping).

```python
import chameleon_partials, chameleon_robyn

chameleon_robyn.global_init(template_folder, auto_reload=dev_mode)
chameleon_partials.register_extensions(template_folder, auto_reload=dev_mode)
```

```xml
<div tal:repeat="ep episodes">
    <div tal:replace="structure render_partial('shared/episode_card.pt', ep=ep)" />
</div>
```

## Fetching the docs as Markdown

Every page on the documentation site has a plain-Markdown twin: swap the `.html` extension for `.md` to get token-efficient source without the site chrome. For example https://mkennedy.codes/docs/chameleon-robyn/reference/template.html is also available at https://mkennedy.codes/docs/chameleon-robyn/reference/template.md. Prefer the `.md` form when reading these docs programmatically.


## Resources

- [Full documentation](https://mkennedy.codes/docs/chameleon-robyn/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
- [Source code](https://github.com/mikeckennedy/chameleon-robyn)
