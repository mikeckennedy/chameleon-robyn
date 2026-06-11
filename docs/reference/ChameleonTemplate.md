## ChameleonTemplate


Chameleon template engine implementing Robyn's TemplateInterface.


Usage

``` python
ChameleonTemplate()
```


A standalone alternative to the module-level API: it owns its own template loader and does not require global_init(). Use it like Robyn's built-in JinjaTemplate.


## Parameters


`directory: str`  
Path to the template directory.

`auto_reload=``False`  
Whether to auto-reload templates on change (use True in development).

`encoding=``"utf-8"`  
Output encoding for rendered templates (defaults to utf-8).

`restricted_namespace=``True`  
If True, only TAL/METAL/i18n namespaces are allowed. Set to False for Alpine.js/htmx-style attributes (<span class="citation" cites="click">@click</span>, :class, etc.).


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

`**kwargs`  
Values passed to the template as its model.


##### Returns


`Response`  
A Robyn Response with the rendered template as its body.
