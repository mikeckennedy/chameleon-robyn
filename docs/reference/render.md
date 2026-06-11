## render()


Render a Chameleon template to a string (no Response wrapping).


Usage

``` python
render(
    template_file,
    **template_data,
)
```


Useful outside of route handlers: emails, middleware, error handlers, etc.


## Parameters


`template_file: str`  
The template file path, relative to the template folder (e.g. 'emails/welcome.pt').

`**template_data: dict`  
Values passed to the template as its model.


## Returns


`str`  
The rendered template as a string.


## Raises


`ChameleonRobynException`  
If global_init() has not been called.
