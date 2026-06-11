## not_found()


Render a friendly 404 page from within a <span class="citation" cites="template-decorated">@template-decorated</span> handler.


Usage

``` python
not_found(four04template_file="errors/404.pt")
```


Raises an exception that the <span class="citation" cites="template">@template</span> decorator catches and converts into a 404 response rendered through the given template. The template receives a `message` variable describing the 404. Only works inside handlers decorated with <span class="citation" cites="template">@template</span>.


## Parameters


`four04template_file: str = ``"errors/404.pt"`  
The template to render, relative to the template folder (defaults to 'errors/404.pt').


## Raises


`ChameleonRobynNotFoundException`  
Always; carries the 404 template path.
