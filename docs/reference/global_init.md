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


Call this once at startup, before the first request is rendered. Routes may be decorated with `@template` before this runs; auto-named templates are resolved lazily at the first request.


## Parameters


`template_folder: str`  
Path to the template directory. All template paths passed to `@template`, render(), response() and not_found() are relative to this folder.

`auto_reload: bool = ``False`  
Whether to re-read templates when they change on disk. Use True in development only; it disables caching.

`cache_init: bool = ``True`  
If True (the default) and the engine is already initialized, the call is ignored and the earlier settings stay in effect. Pass False to re-initialize with new settings (tests do this), or call clear() first.

`restricted_namespace: bool = ``True`  
If True, only TAL/METAL/i18n namespaces are allowed in attributes. If False, attribute-based JS frameworks like Alpine.js and htmx can use shorthand syntax (`@click`, :class, etc.).


## Raises


`ChameleonRobynException`  
If template_folder is empty or is not an existing directory.


## Examples

``` python
from pathlib import Path
import chameleon_robyn

templates = (Path(__file__).resolve().parent / 'templates').as_posix()
chameleon_robyn.global_init(templates, auto_reload=True)  # auto_reload for development only
```
