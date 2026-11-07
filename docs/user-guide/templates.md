# Writing templates

Chameleon templates are HTML or XML files where the logic lives in attributes. There is no `{% ... %}` or `{ ... }` syntax. If you know Jinja2, the biggest change is that a template is always a well-formed document, and loops and conditions attach to the element they control. The full language reference is at [chameleon.readthedocs.io](https://chameleon.readthedocs.io/).


# TAL cheat sheet

``` xml
<!-- Variable substitution: any Python expression inside ${ } -->
<h1>${title}</h1>
<p>${user.name.title()} has ${len(items)} item(s)</p>

<!-- Conditionals: the element is omitted entirely when the expression is falsy -->
<div tal:condition="show_banner">Special offer!</div>
<div tal:condition="not items">Nothing here yet.</div>

<!-- Loops -->
<li tal:repeat="item items">${item.name} - $${item.price}</li>

<!-- The repeat variable exposes index, number, even, odd, first and last -->
<tr tal:repeat="row data" class="${'odd' if repeat.row.odd else 'even'}">
    <td>${repeat.row.number}. ${row.title}</td>
</tr>

<!-- Attributes: interpolate directly, or set several with tal:attributes -->
[${item.name}](/items/${item.id})
<a tal:attributes="href item.url; class item.css_class">${item.name}</a>

<!-- Replace element content, or the whole element -->
<span tal:content="message">placeholder shown in a browser preview</span>
<span tal:replace="formatted_date">2024-01-01</span>

<!-- Define a local variable -->
<span tal:define="total sum(i.price for i in items)">Total: ${total}</span>
```

A literal `$` followed by `{` is written `$${...}`, as in the price example above.


# Escaping and `structure`

Everything inserted with `${...}`, `tal:content` or `tal:replace` is HTML-escaped. To insert markup that is already safe, use the `structure` keyword:

``` xml

```

Only do this with HTML you generated or sanitized yourself.


# Shared layouts with METAL

METAL macros are Chameleon's template inheritance. The layout defines slots; each page fills them.

`templates/shared/layout.pt`:

``` xml
<!DOCTYPE html>
<html>
<head><title>${title}</title></head>
<body>
    <main metal:define-slot="content">Default content</main>
</body>
</html>
```

`templates/home/index.pt`:

``` xml
<metal:block use-macro="load: ../shared/layout.pt">

    <h1>${title}</h1>

</metal:block>
```

The `load:` path is resolved relative to the template that uses it, so a page in `home/` reaches the layout with `../shared/layout.pt`. Chameleon also falls back to the template folder, so `shared/layout.pt` works too. The example apps use the relative form.

The layout sees the same variables as the page, so `title` above comes from the handler's dict.


# File extensions

The loader does not care about the extension. `.pt` is the Chameleon convention and auto-naming looks for `.html` first and `.pt` second (see [the decorator guide](template-decorator.md#auto-naming)). Any other extension works with an explicit path; the example apps render `episodes/feed.xml` with `content_type='application/xml'`.


# Alpine.js, htmx and other attribute syntaxes

By default Chameleon runs with a restricted namespace. Attributes such as `@click`, `:class`, or `x-on:click` look like XML namespace prefixes and are rejected with a `KeyError` when the template is parsed. Turn the restriction off at startup:

``` python
chameleon_robyn.global_init(template_folder, restricted_namespace=False)
```

The same flag exists on [`ChameleonTemplate`](../reference/ChameleonTemplate.md). With it off, any attribute syntax is passed through to the browser.


# Reusable components with chameleon-partials

[chameleon-partials](https://github.com/mikeckennedy/chameleon-partials) adds `render_partial()` for rendering a sub-template from inside a template. It uses its own loader, so initialize both packages at startup with the same folder:

``` python
import chameleon_partials
import chameleon_robyn

chameleon_robyn.global_init(template_folder, auto_reload=dev_mode)
chameleon_partials.register_extensions(template_folder, auto_reload=dev_mode)
```

Pass `render_partial` through the handler's dict:

``` python
@app.get('/')
@chameleon_robyn.template('home/index.pt')
def index(request):
    return {
        'render_partial': chameleon_partials.render_partial,
        'episodes': get_episodes(),
    }
```

Then insert the partial with `tal:replace="structure ..."`:

``` xml

    <div tal:replace="structure render_partial('shared/episode_card.pt', ep=ep)" />

```

`structure` stops Chameleon from escaping the partial's HTML, and `tal:replace` swaps out the placeholder element. The `example-partials/` app in the repository is the core example app refactored this way; compare its episode list template with the one in `example/`.
