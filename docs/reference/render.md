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

`**template_data: Any`  
Values passed to the template as its model. The key 'encoding' is reserved by Chameleon and cannot be used.


## Returns


`str`  
The rendered template as a string.


## Raises


`ChameleonRobynException`  
If global_init() has not been called, or the model uses the reserved key 'encoding'.

`ValueError`  
Raised by Chameleon when the template file does not exist.


## Examples

``` python
html = chameleon_robyn.render('emails/welcome.pt', username='Michael')
```
