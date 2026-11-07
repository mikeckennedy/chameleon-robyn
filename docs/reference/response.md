## response()


Render a Chameleon template and wrap it in a fully-formed Robyn Response.


Usage

``` python
response(
    template_file, content_type="text/html", status_code=200, **template_data
)
```


Useful where the `@template` decorator does not fit: error handlers, middleware, or a handler that renders different templates depending on the request.


## Parameters


`template_file: str`  
The template file path, relative to the template folder.

`content_type: str = ``"text/html"`  
The Content-Type header value (defaults to text/html).

`status_code: int = ``200`  
The HTTP status code for the response (defaults to 200).

`**template_data: Any`  
Values passed to the template as its model.


## Returns


`Response`  
A Robyn Response with the rendered template as its body.


## Raises


`ChameleonRobynException`  
If global_init() has not been called, or the model uses the reserved key 'encoding'.


## Examples

``` python
resp = chameleon_robyn.response('errors/500.pt', status_code=500, error=str(e))
```
