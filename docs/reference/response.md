## response()


Render a Chameleon template and wrap it in a fully-formed Robyn Response.


Usage

``` python
response(
    template_file, content_type="text/html", status_code=200, **template_data
)
```


## Parameters


`template_file: str`  
The template file path, relative to the template folder.

`content_type=``"text/html"`  
The Content-Type header value (defaults to text/html).

`status_code=``200`  
The HTTP status code for the response (defaults to 200).

`**template_data`  
Values passed to the template as its model.


## Returns


`Response`  
A Robyn Response with the rendered template as its body.
