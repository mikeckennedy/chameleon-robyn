## template()


Decorate a Robyn view method to render an HTML response.


Usage

``` python
template(
    template_file=None,
    content_type="text/html",
    status_code=200,
)
```


The decorated handler returns a dict (the template model). If the template path is omitted, it is derived from the module and function name (module/function.pt, falling back to module/function.html). Handlers that return a Robyn Response are passed through untouched (redirects, custom errors). Works with sync and async handlers.


## Parameters


`template_file: Optional[Union[Callable, str]] = None`  
Optional, the Chameleon template file (path relative to template folder, \*.pt).

`content_type: str = ``"text/html"`  
The mimetype response (defaults to text/html).

`status_code: int = ``200`  
Default status code for responses.


## Returns


Decorator for Robyn route handlers.
