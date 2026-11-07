## not_found()


Render a friendly 404 page from within a `@template`-decorated handler.


Usage

``` python
not_found(four04template_file="errors/404.pt")
```


Raises an exception that the `@template` decorator catches and converts into a 404 response rendered through the given template. The template receives a `message` variable describing the 404. Only works inside handlers decorated with `@template`.


## Parameters


`four04template_file: str = ``"errors/404.pt"`  
The template to render, relative to the template folder (defaults to 'errors/404.pt').


## Raises


`ChameleonRobynNotFoundException`  
Always; carries the 404 template path.


## Examples

``` python
@app.get('/episodes/:episode_id')
@chameleon_robyn.template('episodes/detail.pt')
def episode_detail(request, episode_id: int):
    episode = get_episode(episode_id)
    if not episode:
        chameleon_robyn.not_found()  # renders errors/404.pt with status 404
    return {'episode': episode}
```
