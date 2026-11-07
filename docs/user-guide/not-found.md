# Friendly 404 pages

A handler that looks something up and finds nothing should return a proper 404 page, not a stack trace or a bare status. Call [not_found()](../reference/not_found.md#chameleon_robyn.not_found) from any `@template`-decorated handler:

``` python
@app.get('/episodes/:episode_id')
@chameleon_robyn.template('episodes/detail.pt')
async def episode_detail(request, episode_id: int):
    episode = await get_episode(episode_id)
    if not episode:
        chameleon_robyn.not_found()  # Renders errors/404.pt with status 404

    return {'episode': episode}
```

[not_found()](../reference/not_found.md#chameleon_robyn.not_found) never returns. It raises [ChameleonRobynNotFoundException](../reference/ChameleonRobynNotFoundException.md#chameleon_robyn.ChameleonRobynNotFoundException), the decorator catches it, renders the 404 template with status 404 and a `text/html` content type, and returns that `Response`. The handler's own `status_code` and `content_type` settings do not apply to the 404.


# The default template

By default the library renders `errors/404.pt`, relative to your template folder. Create that file in every app that calls [not_found()](../reference/not_found.md#chameleon_robyn.not_found). If it is missing, Chameleon raises a `ValueError` naming the file.

The template receives one variable, `message`, with a short description of the 404. Render it or ignore it:

``` xml
<metal:block use-macro="load: ../shared/layout.pt">

    <h1>Page not found</h1>
    <p>${message}</p>
    [Back to the home page](/)

</metal:block>
```


# A different 404 template

``` python
chameleon_robyn.not_found(four04template_file='errors/custom_404.pt')
```


# Your own message

[not_found()](../reference/not_found.md#chameleon_robyn.not_found) always uses the same generic message. To put your own text in the page, raise the exception directly. The decorator treats it exactly the same way:

``` python
from chameleon_robyn import ChameleonRobynNotFoundException

if not episode:
    raise ChameleonRobynNotFoundException(f'There is no episode {episode_id}.')
```

The second argument is the template path, defaulting to `errors/404.pt`.


# Outside a decorated handler

[not_found()](../reference/not_found.md#chameleon_robyn.not_found) only works inside handlers wrapped with `@template`, because the decorator is what catches the exception. Anywhere else, build the response yourself with [`response()`](lower-level-api.md):

``` python
return chameleon_robyn.response('errors/404.pt', status_code=404, message='No such page.')
```


# Other error pages

For a 500 page or any other status, use [response()](../reference/response.md#chameleon_robyn.response) with the status you need. It works inside decorated handlers too, because a returned `Response` passes through untouched:

``` python
@app.get('/report')
@chameleon_robyn.template('reports/view.pt')
def report(request):
    try:
        data = build_report()
    except ReportError as e:
        return chameleon_robyn.response('errors/500.pt', status_code=500, error=str(e))
    return {'data': data}
```
