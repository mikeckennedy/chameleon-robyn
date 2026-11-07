---
name: chameleon-robyn
description: Render Chameleon page templates (.pt files using TAL and METAL) from Robyn web handlers. A handler returns a dict and the @template decorator turns it into a Robyn Response. Use when adding Chameleon templates to a Robyn app, when a handler should return a dict that becomes an HTML page, when a ChameleonRobynException or a Chameleon ValueError, NameError or KeyError appears while rendering, when choosing between @template, response(), render() and ChameleonTemplate, when a 404 page or a cookie must be set on a rendered page, or when Alpine.js or htmx attributes fail to parse in a template.
license: MIT
compatibility: Requires Python >=3.10, robyn>=0.60 and Chameleon. No Jinja2 dependency.
---

# chameleon-robyn

Robyn ships with Jinja2. This package lets a Robyn handler return a plain `dict` and renders it through a Chameleon page template (`.pt`, TAL/METAL syntax, not Jinja syntax) into a `robyn.Response`. Errors from this package are `ChameleonRobynException`; errors about the template itself come from Chameleon (`ValueError` for a missing file, `NameError` for a missing variable, `KeyError` for a disallowed attribute).

## Install

```bash
uv pip install chameleon-robyn   # or: pip install chameleon-robyn
```

## Use

```python
from pathlib import Path
from robyn import Robyn
import chameleon_robyn

app = Robyn(__file__)

@app.get('/episodes/:episode_id')                 # Robyn route decorator outermost
@chameleon_robyn.template('episodes/detail.pt')  # @template directly above the function
async def episode_detail(request, episode_id: int):
    episode = await get_episode(episode_id)
    if not episode:
        chameleon_robyn.not_found()               # renders errors/404.pt, status 404
    return {'episode': episode}                   # the dict is the template model

def main():
    templates = (Path(__file__).resolve().parent / 'templates').as_posix()
    chameleon_robyn.global_init(templates, auto_reload=True)  # once at startup; auto_reload for dev only
    app.start(host='127.0.0.1', port=8000)
```

Template `templates/episodes/detail.pt` (valid HTML; logic lives in `tal:` attributes, interpolation is `${...}`):

```html
<metal:block use-macro="load: ../shared/layout.pt">
<div metal:fill-slot="content">
  <h1>${episode.title}</h1>
  <li tal:repeat="g episode.guests">${g.name}</li>
  <p tal:condition="not episode.guests">No guests.</p>
</div>
</metal:block>
```

## Rules

- A decorated handler must return a `dict` or a `robyn.Response`. Anything else, including `None`, raises `ChameleonRobynException` at request time.
- A returned `Response` passes through untouched. That is how redirects work, and how a handler renders a different template: `return chameleon_robyn.response('other.pt', status_code=401, **model)`.
- All template paths are relative to the folder passed to `global_init()`. The default 404 template is `errors/404.pt`; create it in every app that calls `not_found()`.
- `global_init()` is one-shot by default. With `cache_init=True` (the default) a second call is silently ignored. Pass `cache_init=False` or call `clear()` first to change settings, including in test fixtures.
- Bare `@template` or `@template()` derives `<module>/<function>.html`, falling back to `<module>/<function>.pt`, where `<module>` is the last segment of the module name. For a script run directly (`python app.py`) it is the script's file stem, so `index()` in `app.py` expects `app/index.pt`, with `__main__/index.pt` as a legacy fallback. The name is resolved at the first request, so `global_init()` may run after the routes are decorated.
- `not_found()` only works inside `@template` handlers, because the decorator catches the exception it raises. The 404 always renders as `text/html` with status 404, ignoring the handler's `content_type` and `status_code`. Outside a decorated handler use `response('errors/404.pt', status_code=404, message='...')`.
- Raise `ChameleonRobynNotFoundException('your message')` directly to put a custom message into the 404 template; `not_found()` passes a fixed message as `message`.
- `__response_callback__` is a reserved model key. Its value must be callable (else `ChameleonRobynException`), it is popped from a copy of the dict before rendering, it never reaches the template, and it is called with the built `Response`. Mutate the response in place; the return value is ignored.
- `encoding` is a reserved model key. Chameleon's `render()` takes it as a parameter, so passing it raises `ChameleonRobynException`. Rename the variable.
- Chameleon's default restricted namespace rejects `@click`, `:class`, `x-on:click` and similar Alpine.js or htmx attributes with a `KeyError`. Pass `restricted_namespace=False` to `global_init()` or `ChameleonTemplate`.
- `${...}` output is HTML-escaped. Use `tal:replace="structure expr"` for pre-rendered HTML, including chameleon-partials output. A literal `$` before `{` is written `$${...}`.
- `ChameleonTemplate` has its own loader and ignores `global_init()`. Its `render_template()` always returns status 200 with `text/html`.
- Sync and async handlers both work; the wrapper is chosen automatically. `functools.wraps` preserves the signature, so Robyn still injects `request` and typed path params.
- Templates must be well-formed HTML/XML. There is no `{% %}` or `{{ }}` syntax.

## Decision table

| Need | Use |
|---|---|
| Render a template from a Robyn handler | `@chameleon_robyn.template('dir/page.pt')` and return a `dict` |
| Template named after the module and function | bare `@chameleon_robyn.template` |
| Non-200 status or non-HTML content type for a page | `@template('feed.xml', content_type='application/xml', status_code=200)` |
| Redirect from a decorated handler | return `robyn.Response(status_code=302, description='', headers=Headers({'Location': '/x'}))` |
| Render a different template in some branch | return `chameleon_robyn.response('other.pt', status_code=..., **model)` |
| Friendly 404 inside a decorated handler | `chameleon_robyn.not_found()` or `not_found(four04template_file='errors/custom.pt')` |
| 404 with a custom message | `raise ChameleonRobynNotFoundException('message')` |
| 404 or 500 outside a decorated handler | `chameleon_robyn.response('errors/404.pt', status_code=404, message='...')` |
| Set a cookie or header on a rendered page | `'__response_callback__': fn` in the dict; `fn(resp)` does `resp.headers.append('Set-Cookie', ...)` |
| HTML as a string (emails, fragments) | `chameleon_robyn.render('emails/welcome.pt', **model)` |
| Robyn's JinjaTemplate-style engine object | `ChameleonTemplate('templates/').render_template('page.pt', **model)` |
| Alpine.js or htmx attributes in templates | `global_init(..., restricted_namespace=False)` |
| Templates reload on edit | `global_init(..., auto_reload=True)` in development only |
| Re-initialize with new settings (tests) | `global_init(folder, cache_init=False)` and `clear()` in teardown |
| Reusable partials | chameleon-partials: `register_extensions(folder)` at startup, pass `render_partial` in the dict, insert with `tal:replace="structure render_partial('shared/card.pt', item=item)"` |

## API

- `global_init(template_folder: str, auto_reload=False, cache_init=True, restricted_namespace=True) -> None`. Raises `ChameleonRobynException` if the folder is empty or not a directory. No-op when already initialized unless `cache_init=False`.
- `clear() -> None`. Resets to uninitialized; rendering afterwards raises `ChameleonRobynException` until `global_init()` runs again.
- `template(template_file: str | None = None, content_type='text/html', status_code=200)`. Decorator; also usable bare. `charset=utf-8` is appended to the content type.
- `not_found(four04template_file='errors/404.pt') -> NoReturn`. Raises `ChameleonRobynNotFoundException(message, template)`.
- `render(template_file: str, **model) -> str`. Raises `ChameleonRobynException` if uninitialized or `encoding` is in the model; Chameleon raises `ValueError` if the file is missing.
- `response(template_file: str, content_type='text/html', status_code=200, **model) -> robyn.Response`. Same errors as `render()`.
- `ChameleonTemplate(directory: str, auto_reload=False, encoding='utf-8', restricted_namespace=True)` with `.render_template(template_name: str, **model) -> robyn.Response` (always 200, `text/html`).
- `ChameleonRobynException(Exception)`: base for every error this package raises.
- `ChameleonRobynNotFoundException(message=None, four04template_file='errors/404.pt')`: subclass carrying `.message` and `.template_file`.

## Reading an error

```text
chameleon_robyn.exceptions.ChameleonRobynException: Invalid return type <class 'NoneType'>, we expected a dict or Response as the return value.
```

The handler fell off the end without returning the dict, usually after a `not_found()` call was removed. Fix order for rendering problems: initialize (`global_init()` ran, folder exists), then path (relative to the folder, auto-name matches `<module>/<function>`), then model (every `${name}` in the template is a key in the dict), then markup (well-formed, `restricted_namespace` if using Alpine/htmx).

## Resources

- Docs: <https://mkennedy.codes/docs/chameleon-robyn/>
- Decorator guide: <https://mkennedy.codes/docs/chameleon-robyn/user-guide/template-decorator.html>
- Writing templates (TAL cheat sheet, METAL, partials): <https://mkennedy.codes/docs/chameleon-robyn/user-guide/templates.html>
- Errors and fixes: <https://mkennedy.codes/docs/chameleon-robyn/user-guide/troubleshooting.html>
- Testing handlers: <https://mkennedy.codes/docs/chameleon-robyn/user-guide/testing.html>
- API index: <https://mkennedy.codes/docs/chameleon-robyn/llms.txt>
- Full docs for agents: <https://mkennedy.codes/docs/chameleon-robyn/llms-full.txt>
- Every docs page is also served as Markdown by swapping `.html` for `.md`, for example <https://mkennedy.codes/docs/chameleon-robyn/reference/template.md>
- Source: <https://github.com/mikeckennedy/chameleon-robyn>
- Chameleon language reference: <https://chameleon.readthedocs.io/>
