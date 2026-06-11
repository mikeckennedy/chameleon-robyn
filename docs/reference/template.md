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


The decorated handler returns a dict (the template model). If the template path is omitted, it is derived from the module and function name: module/function.html if that file exists, otherwise module/function.pt. The auto-derived name is resolved at first request, so global_init() may be called after route decoration. Handlers that return a Robyn Response are passed through untouched (redirects, custom errors). Works with sync and async handlers.


## Parameters


`template_file: Optional[Union[Callable, str]] = None`  
Optional, the Chameleon template file (path relative to template folder, \*.pt).

`content_type: str = ``"text/html"`  
The Content-Type header value for rendered responses (defaults to text/html).

`status_code: int = ``200`  
The HTTP status code for rendered responses (defaults to 200).


## Returns


`Callable`  
Decorator for Robyn route handlers.
