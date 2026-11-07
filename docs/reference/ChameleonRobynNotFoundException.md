## ChameleonRobynNotFoundException


Raised by not_found() to signal a 404 from within a `@template`-decorated handler.


Usage

``` python
ChameleonRobynNotFoundException(
    message=None, four04template_file="errors/404.pt"
)
```


The `@template` decorator catches this exception and renders the template it carries with a 404 status code, passing the message to the template as `message`.


## Parameters


`message: Optional[str] = None`  
Optional human-readable description of the 404.

`four04template_file: str = ``"errors/404.pt"`  
The 404 template to render, relative to the template folder.


## Examples

Raise it directly to supply your own message to the 404 template:

``` python
raise ChameleonRobynNotFoundException(f'No episode with id {episode_id}.')
```
