## global_init()


Initialize the Chameleon template engine.


Usage

``` python
global_init(
    template_folder,
    auto_reload=False,
    cache_init=True,
    restricted_namespace=True
)
```


## Parameters


`template_folder: str`  
Path to the template directory

`auto_reload=``False`  
Whether to auto-reload templates on change

`cache_init=``True`  
Whether to cache initialization (skip if already initialized)

`restricted_namespace=``True`  
If True, only TAL/METAL/i18n namespaces are allowed. If False, allows attribute-based JS frameworks like Alpine.js to use shorthand syntax (<span class="citation" cites="click">@click</span>, :class, etc.)
