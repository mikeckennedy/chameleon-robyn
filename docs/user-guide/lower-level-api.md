# Rendering outside handlers

The decorator is the front door, and most requests walk through it. But a web app renders HTML in more places than route handlers: the body of a welcome email, an error page built in middleware, a fragment assembled in a helper. For those, the package has a side door with three entry points.


# [render()](../reference/render.md#chameleon_robyn.render): get a string

``` python
html = chameleon_robyn.render('emails/welcome.pt', username='Michael')
```

Returns the rendered template as a `str`, nothing wrapped around it. Keyword arguments are the template variables. It requires [global_init()](../reference/global_init.md#chameleon_robyn.global_init) to have been called and raises [ChameleonRobynException](../reference/ChameleonRobynException.md#chameleon_robyn.ChameleonRobynException) otherwise.


# [response()](../reference/response.md#chameleon_robyn.response): get a Robyn Response

``` python
resp = chameleon_robyn.response('errors/500.pt', status_code=500, error=str(e))
```

Renders the template and wraps it in a `Response` with the given status (default 200) and content type (default `text/html`, with `charset=utf-8` appended). The remaining keyword arguments are the template variables.

This is also the answer to a question that comes up on every login page: how does a decorated handler render a template other than the one in the decorator? Build it with [response()](../reference/response.md#chameleon_robyn.response) and return it. The decorator passes any `Response` through untouched.

``` python
@app.post('/account/login')
@chameleon_robyn.template('account/welcome.pt')
async def login(request):
    user = await authenticate(request)
    if not user:
        return chameleon_robyn.response('account/login_failed.pt', status_code=401)
    return {'user': user}
```


# A reserved variable name

Chameleon's own [render()](../reference/render.md#chameleon_robyn.render) takes the output encoding as a named parameter, so a template variable called `encoding` cannot be passed. The library raises [ChameleonRobynException](../reference/ChameleonRobynException.md#chameleon_robyn.ChameleonRobynException) with a clear message if you try. Rename the key and move on.


# [ChameleonTemplate](../reference/ChameleonTemplate.md#chameleon_robyn.ChameleonTemplate): Robyn's TemplateInterface pattern

Robyn's own templating module exposes a `JinjaTemplate` class with a [render_template()](../reference/ChameleonTemplate.md#chameleon_robyn.ChameleonTemplate.render_template) method. If that is the shape you already use, [ChameleonTemplate](../reference/ChameleonTemplate.md#chameleon_robyn.ChameleonTemplate) has the same one:

``` python
from chameleon_robyn import ChameleonTemplate

chameleon = ChameleonTemplate('templates/', auto_reload=True)

@app.get('/page')
def page(request):
    return chameleon.render_template('page.pt', title='Hello')
```

Points to know:

- It owns its own template loader and neither uses nor requires [global_init()](../reference/global_init.md#chameleon_robyn.global_init). You can mix it with the decorator API in one app, but each has its own folder setting.
- [render_template()](../reference/ChameleonTemplate.md#chameleon_robyn.ChameleonTemplate.render_template) always returns status 200 with `text/html`. For other statuses use [response()](../reference/response.md#chameleon_robyn.response).
- The constructor takes `directory`, `auto_reload`, `encoding` and `restricted_namespace`. See the [reference](../reference/ChameleonTemplate.md).
- It matches Robyn's `TemplateInterface` through a structural Protocol rather than by subclassing Robyn's abstract class. Importing that class would import Jinja2, and this package deliberately has no Jinja2 dependency. [How it works](how-it-works.md) tells the rest of that story.
