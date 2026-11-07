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


The decorated handler returns a dict (the template model). If the template path is omitted, it is derived from the module and function name: module/function.html if that file exists, otherwise module/function.pt. For a script run directly (module **main**) the script's file name is used instead, so index() in app.py maps to app/index.pt; a legacy **main**/function.html or .pt is still found if the script-named file does not exist. The auto-derived name is resolved at first request, so global_init() may be called after route decoration. Handlers that return a Robyn Response are passed through untouched (redirects, custom errors). Works with sync and async handlers.

Place `@template` directly above the handler, below Robyn's route decorator.


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


## Raises


`ChameleonRobynException`  
At request time, if the handler returns something other than a dict or a Robyn Response, or if '**response_callback**' is not callable.


## Examples

``` python
@app.get('/episodes/:episode_id')
@chameleon_robyn.template('episodes/detail.pt')
async def episode_detail(request, episode_id: int):
    return {'episode': await get_episode(episode_id)}

@app.get('/')
@chameleon_robyn.template  # renders <module>/index.html or <module>/index.pt
def index(request):
    return {'title': 'Home'}
```
