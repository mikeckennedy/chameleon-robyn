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
