## ChameleonTemplate


Chameleon template engine implementing Robyn's TemplateInterface.


Usage

``` python
ChameleonTemplate(
    directory, auto_reload=False, encoding="utf-8", restricted_namespace=True
)
```


A standalone alternative to the module-level API: it owns its own template loader and does not require global_init(). Use it like Robyn's built-in JinjaTemplate.


## Parameters


`directory: str`  
Path to the template directory.

`auto_reload: bool = ``False`  
Whether to auto-reload templates on change (use True in development).

`encoding: str = ``"utf-8"`  
Output encoding for rendered templates (defaults to utf-8).

`restricted_namespace: bool = ``True`  
If True, only TAL/METAL/i18n namespaces are allowed. Set to False for Alpine.js/htmx-style attributes (`@click`, :class, etc.).


## Examples

``` python
from chameleon_robyn import ChameleonTemplate

chameleon = ChameleonTemplate('templates/', auto_reload=True)

@app.get('/page')
def page(request):
    return chameleon.render_template('page.pt', title='Hello')
```


## Methods

| Name | Description |
|----|----|
| [render_template()](#render_template) | Render a template and return a 200 Robyn Response. |

------------------------------------------------------------------------


#### render_template()


Render a template and return a 200 Robyn Response.


Usage

``` python
render_template(template_name, **kwargs)
```


##### Parameters


`template_name: str`  
The template file path, relative to the directory given at construction.

`**kwargs: Any`  
Values passed to the template as its model. The key 'encoding' is reserved.


##### Returns


`Response`  
A Robyn Response with the rendered template as its body. The status is always 200

and the Content-Type is always text/html.


##### Raises


`ChameleonRobynException`  
If the model uses the reserved key 'encoding'.
