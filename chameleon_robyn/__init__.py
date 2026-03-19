"""chameleon-robyn - Adds integration of the Chameleon template language to Robyn."""

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
