"""chameleon-robyn - Adds integration of the Chameleon template language to Robyn.

Entry points:

- global_init(template_folder, ...): call once at startup to point the engine at your templates.
- @template(...): decorate a Robyn handler; it returns a dict and the decorator renders it to a Response.
- not_found(): raise a friendly 404 from inside a decorated handler.
- render() and response(): render a template to a str or a Response outside the decorator.
- ChameleonTemplate: a standalone engine class matching Robyn's TemplateInterface.

There is no CLI and no environment variable configuration. Docs: https://mkennedy.codes/docs/chameleon-robyn/
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _get_version

from .engine import (
    ChameleonTemplate,
    clear,
    global_init,  # noqa: I001
    not_found,
    render,
    response,
    template,
)
from .exceptions import (
    ChameleonRobynException,
    ChameleonRobynNotFoundException,
)

try:
    __version__ = _get_version('chameleon_robyn')
except PackageNotFoundError:
    __version__ = '0.0.0'

__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__all__ = [
    'template',
    'global_init',
    'clear',
    'not_found',
    'render',
    'response',
    'ChameleonTemplate',
    'ChameleonRobynException',
    'ChameleonRobynNotFoundException',
]
