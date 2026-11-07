# How it works

The whole library is three small files in `chameleon_robyn/`. Everything else in the repository is tests, example apps and this documentation. You can read the source in the time it takes to drink a coffee, and this page is the guided tour, so that when something surprises you, you already know which five lines to look at.


# The global loader

[global_init()](../reference/global_init.md#chameleon_robyn.global_init) creates one Chameleon `PageTemplateLoader` for the template folder and stores it, together with the folder path, in module-level state. That single loader is the engine. [render()](../reference/render.md#chameleon_robyn.render) looks a template up in it by relative path and calls Chameleon's [render()](../reference/render.md#chameleon_robyn.render) with the keyword arguments as the template's variables. [response()](../reference/response.md#chameleon_robyn.response) calls [render()](../reference/render.md#chameleon_robyn.render) and wraps the string in a Robyn `Response` with the requested status and content type. [clear()](../reference/clear.md#chameleon_robyn.clear) drops the stored loader so the next [global_init()](../reference/global_init.md#chameleon_robyn.global_init) starts fresh.


# The decorator

[template()](../reference/template.md#chameleon_robyn.template) returns a wrapper for the handler. It chooses a synchronous or asynchronous wrapper by checking whether the handler is a coroutine function, so `await` happens exactly where it should. Both wrappers do the same four things:

1.  Call the handler.
2.  If the result is a Robyn `Response`, return it unchanged.
3.  If it is a `dict`, copy it, pop `__response_callback__`, render the template, build the `Response`, and call the callback with it.
4.  Otherwise raise [ChameleonRobynException](../reference/ChameleonRobynException.md#chameleon_robyn.ChameleonRobynException).

Both wrappers also catch [ChameleonRobynNotFoundException](../reference/ChameleonRobynNotFoundException.md#chameleon_robyn.ChameleonRobynNotFoundException), which [not_found()](../reference/not_found.md#chameleon_robyn.not_found) raises, and render the template it carries with status 404.

The wrappers use `functools.wraps`, which keeps the original function's name and signature visible. Robyn inspects the handler signature when a route is registered to decide which arguments to pass. That one line is what keeps `request` and typed path parameters working through the decorator.


# Lazy template names

When the template path is omitted, the wrapper derives `<module>/<function>` and checks for the `.html` file on the first request rather than at decoration time. The reason is timing: routes are often decorated at import, before [global_init()](../reference/global_init.md#chameleon_robyn.global_init) has run and before anyone knows where the template folder is. Once the folder is known the resolved name is cached, so the file check happens once per handler, not once per request.


# 404 via an exception

[not_found()](../reference/not_found.md#chameleon_robyn.not_found) is declared `NoReturn`. It raises rather than returns so a handler can call it from inside a nested condition without the surrounding code having to `return` its result. The exception carries the template path and message, and the decorator turns it into a response. This is also why it only works inside decorated handlers: the decorator is the net, and without it there is nothing to catch.


# No Jinja2 dependency

Robyn's `TemplateInterface` lives in a module that imports Jinja2 at the top. Subclassing it would have made Jinja2 a hard dependency of a package whose entire purpose is to let you not use Jinja2. Instead, [ChameleonTemplate](../reference/ChameleonTemplate.md#chameleon_robyn.ChameleonTemplate) implements a local `Protocol` with the same [render_template()](../reference/ChameleonTemplate.md#chameleon_robyn.ChameleonTemplate.render_template) method, marked `runtime_checkable` so `isinstance()` checks still pass. Robyn only cares that the method exists, so the class is interchangeable with `JinjaTemplate` in practice, and your dependency tree stays honest.
