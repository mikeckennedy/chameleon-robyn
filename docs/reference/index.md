# API Reference


Everything chameleon-robyn exports: setup, the <span class="citation" cites="template">@template</span> decorator, lower-level rendering, and the Robyn TemplateInterface implementation.


## Setup & configuration


Initialize the template engine once at app startup.


[global_init()](global_init.md#chameleon_robyn.global_init)  
Initialize the Chameleon template engine.

[clear()](clear.md#chameleon_robyn.clear)  
Reset the template engine to its uninitialized state.


## Rendering views


The <span class="citation" cites="template">@template</span> decorator and friendly 404s for Robyn route handlers.


[template()](template.md#chameleon_robyn.template)  
Decorate a Robyn view method to render an HTML response.

[not_found()](not_found.md#chameleon_robyn.not_found)  
Render a friendly 404 page from within a <span class="citation" cites="template-decorated">@template-decorated</span> handler.


## Lower-level rendering


Render templates outside the decorator (middleware, error handlers, emails).


[render()](render.md#chameleon_robyn.render)  
Render a Chameleon template to a string (no Response wrapping).

[response()](response.md#chameleon_robyn.response)  
Render a Chameleon template and wrap it in a fully-formed Robyn Response.


## Robyn TemplateInterface


Standalone template engine class matching Robyn's built-in template pattern.


[ChameleonTemplate](ChameleonTemplate.md#chameleon_robyn.ChameleonTemplate)  
Chameleon template engine implementing Robyn's TemplateInterface.


## Exceptions


Exception types raised by the library.


[ChameleonRobynException](ChameleonRobynException.md#chameleon_robyn.ChameleonRobynException)  
Base exception for all chameleon-robyn errors (bad configuration, invalid return types, etc.).

[ChameleonRobynNotFoundException](ChameleonRobynNotFoundException.md#chameleon_robyn.ChameleonRobynNotFoundException)  
Raised by not_found() to signal a 404 from within a <span class="citation" cites="template-decorated">@template-decorated</span> handler.
