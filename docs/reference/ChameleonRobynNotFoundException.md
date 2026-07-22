## ChameleonRobynNotFoundException


Raised by not_found() to signal a 404 from within a <span class="citation" cites="template-decorated">@template-decorated</span> handler.


Usage

``` python
ChameleonRobynNotFoundException(
    message=None, four04template_file="errors/404.pt"
)
```


The <span class="citation" cites="template">@template</span> decorator catches this exception and renders the template it carries with a 404 status code, passing the message to the template as `message`.


## Parameters


`message: Optional[str] = None`  
Optional human-readable description of the 404.

`four04template_file: str = ``"errors/404.pt"`  
The 404 template to render, relative to the template folder.
