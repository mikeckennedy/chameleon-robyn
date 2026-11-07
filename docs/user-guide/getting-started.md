# Getting started

Every web framework eventually asks the same question: how do you turn data into HTML? Robyn's answer out of the box is Jinja2. This package offers a second answer, the one people who built on Pyramid or Zope tend to miss the moment they leave: [Chameleon](https://chameleon.readthedocs.io/) page templates.

A Chameleon template is an ordinary HTML file. Open one in a browser before it has ever been rendered and you still see a page, placeholders and all, because the logic lives inside attributes the browser ignores. `tal:repeat` loops, `tal:condition` hides, and `${...}` fills in values with real Python expressions. There is no second language layered over your markup. Your designer can open the file. Your editor can validate it. And chameleon-robyn wires those templates into Robyn with a single decorator: your handler returns a `dict`, and a rendered `Response` comes out the other side.

One honest note before we begin: the project is in alpha. The API is small and unlikely to change much, but there are no stability promises yet.


# Install

``` bash
uv pip install chameleon-robyn
```

Or with pip:

``` bash
pip install chameleon-robyn
```

This brings in `robyn` and `chameleon` as dependencies. Python 3.10 or newer is required.


# The site we are building

This guide follows one project from the first page to the last error message: the website for a small podcast. It has an episode list, a page per episode, a guest directory, a search box, an XML feed for the robots, and the occasional visitor who types a URL that does not exist. Every snippet in the guide comes from that site, and the repository's `example/` folder holds the finished version.


# Project layout

Nothing about the layout is enforced, but this is the shape that makes the rest of the guide read naturally:

``` text
my_app/
├── app.py
└── templates/
    └── home/
        └── index.pt
```

Every template path you hand the library is relative to the `templates/` folder you register at startup. The folder name is yours to choose.


# Your first page

Start with `templates/home/index.pt`. Notice that it is just HTML with two extra ideas: `${name}` to drop in a value, and `tal:repeat` on the element that should repeat.

``` xml
<!DOCTYPE html>
<html>
<body>
    <h1>Hello, ${name}!</h1>
    <ul>
        <li tal:repeat="item items">${item}</li>
    </ul>
</body>
</html>
```

Now `app.py`. Three lines matter: the import, the [global_init()](../reference/global_init.md#chameleon_robyn.global_init) call that says where templates live, and the decorator above the handler.

``` python
from pathlib import Path
from robyn import Robyn
import chameleon_robyn

app = Robyn(__file__)

# Point Chameleon at your templates folder (do this once at startup)
template_folder = (Path(__file__).resolve().parent / 'templates').as_posix()
chameleon_robyn.global_init(template_folder, auto_reload=True)

@app.get('/')
@chameleon_robyn.template('home/index.pt')
async def index(request):
    return {'name': 'World', 'items': ['Robyn', 'Chameleon', 'Python']}

app.start(host='127.0.0.1', port=8000)
```

Run `python app.py` and open <http://127.0.0.1:8000/>. A heading and a three-item list greet you. That handler never touched a string of HTML, and it never will.


# What just happened

- [global_init()](../reference/global_init.md#chameleon_robyn.global_init) told Chameleon where the templates live. It runs once at startup, and its settings are the subject of [Configuration](configuration.md).
- `@template('home/index.pt')` wrapped the handler. The handler returned a `dict`, and every key in it became a variable the template could see.
- The decorator rendered the template and handed back a Robyn `Response` with status 200 and a `Content-Type` of `text/html; charset=utf-8`.
- Robyn's route decorator stayed on the outside. `@template` sits directly above the function, and it is equally happy with `def` and `async def`.

That is the whole mental model. Everything else in this guide is a refinement of it.


# Run the finished examples

Two runnable apps live in the repository. The first shows every feature on the podcast site: episodes and guests, a shared METAL layout, search by query string, the XML feed, a redirect, a cookie set from a rendered page, and a friendly 404. The second is the same app with the episode card pulled out into a reusable partial.

``` bash
git clone https://github.com/mikeckennedy/chameleon-robyn.git
cd chameleon-robyn
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -e ".[examples]"

python example/app.py           # core features
python example-partials/app.py  # the same app using chameleon-partials
# Open http://127.0.0.1:5555
```


# Where to go next

- [The <span class="citation" cites="template">@template</span> decorator](template-decorator.md): the return-value contract, templates that name themselves, async handlers, status codes, redirects, and setting a cookie on a rendered page.
- [Writing templates](templates.md): a TAL cheat sheet, shared layouts with METAL, escaping, Alpine.js and htmx attributes, and chameleon-partials.
- [Friendly 404 pages](not-found.md): one call to [not_found()](../reference/not_found.md#chameleon_robyn.not_found) and the stack trace never reaches the visitor.
- [Rendering outside handlers](lower-level-api.md): [render()](../reference/render.md#chameleon_robyn.render), [response()](../reference/response.md#chameleon_robyn.response), and the standalone [ChameleonTemplate](../reference/ChameleonTemplate.md#chameleon_robyn.ChameleonTemplate) class.
- [Configuration](configuration.md): every [global_init()](../reference/global_init.md#chameleon_robyn.global_init) setting, and the one that bites people in tests.
- [Testing your handlers](testing.md): no server, no client, just function calls.
- [Errors and how to fix them](troubleshooting.md): a field guide to every exception you can meet.
- [How it works](how-it-works.md): a tour of the three source files.
- [FAQ](faq.md)
- [API reference](../reference/index.md)
