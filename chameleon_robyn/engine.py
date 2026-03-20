import inspect
import os
from functools import wraps
from typing import Any, Callable, Optional, Protocol, Union, runtime_checkable

from chameleon import PageTemplate, PageTemplateLoader
from robyn import Headers, Response, status_codes

from chameleon_robyn.exceptions import (
    ChameleonRobynException,
    ChameleonRobynNotFoundException,
)

__templates: Optional[PageTemplateLoader] = None
template_path: Optional[str] = None


def global_init(template_folder: str, auto_reload=False, cache_init=True, restricted_namespace=True):
    """
    Initialize the Chameleon template engine.

    Args:
        template_folder: Path to the template directory
        auto_reload: Whether to auto-reload templates on change
        cache_init: Whether to cache initialization (skip if already initialized)
        restricted_namespace: If True, only TAL/METAL/i18n namespaces are allowed.
                            If False, allows attribute-based JS frameworks like Alpine.js
                            to use shorthand syntax (@click, :class, etc.)
    """
    global __templates, template_path

    if __templates and cache_init:
        return

    if not template_folder:
        msg = 'The template_folder must be specified.'
        raise ChameleonRobynException(msg)

    if not os.path.isdir(template_folder):
        msg = f"The specified template folder must be a folder, it's not: {template_folder}"
        raise ChameleonRobynException(msg)

    template_path = template_folder
    __templates = PageTemplateLoader(
        template_folder,
        auto_reload=auto_reload,
        restricted_namespace=restricted_namespace,
    )


def clear():
    global __templates, template_path
    __templates = None
    template_path = None


def render(template_file: str, **template_data: dict) -> str:
    if not __templates:
        raise ChameleonRobynException('You must call global_init() before rendering templates.')

    page: PageTemplate = __templates[template_file]
    return page.render(encoding='utf-8', **template_data)


def response(template_file: str, content_type='text/html', status_code=200, **template_data) -> Response:
    html = render(template_file, **template_data)
    return Response(
        status_code=status_code,
        description=html,
        headers=Headers({'Content-Type': f'{content_type}; charset=utf-8'}),
    )


def template(
    template_file: Optional[Union[Callable, str]] = None,
    content_type: str = 'text/html',
    status_code: int = 200,
):
    """
    Decorate a Robyn view method to render an HTML response.

    :param template_file: Optional, the Chameleon template file (path relative to template folder, *.pt).
    :param content_type: The mimetype response (defaults to text/html).
    :param status_code: Default status code for responses.
    :return: Decorator for Robyn route handlers
    """

    wrapped_function = None
    if callable(template_file):
        wrapped_function = template_file
        template_file = None

    def response_inner(f):
        nonlocal template_file
        global template_path

        if not template_path:
            template_path = 'templates'

        if not template_file:
            module = f.__module__
            if '.' in module:
                module = module.split('.')[-1]
            view = f.__name__
            template_file = f'{module}/{view}.html'

            if not os.path.exists(os.path.join(template_path, template_file)):
                template_file = f'{module}/{view}.pt'

        @wraps(f)
        def sync_view_method(*args, **kwargs) -> Response:
            try:
                response_val = f(*args, **kwargs)
                return __render_response(template_file, response_val, content_type, status_code)
            except ChameleonRobynNotFoundException as nfe:
                return __render_response(nfe.template_file, {}, 'text/html', 404)

        @wraps(f)
        async def async_view_method(*args, **kwargs) -> Response:
            try:
                response_val = await f(*args, **kwargs)
                return __render_response(template_file, response_val, content_type, status_code)
            except ChameleonRobynNotFoundException as nfe:
                return __render_response(nfe.template_file, {}, 'text/html', 404)

        if inspect.iscoroutinefunction(f):
            return async_view_method
        else:
            return sync_view_method

    return response_inner(wrapped_function) if wrapped_function else response_inner


def __is_response(resp) -> bool:
    return isinstance(resp, Response)


def __render_response(template_file: str, response_val: Any, content_type: str, status_code: int = 200) -> Response:
    if __is_response(response_val):
        return response_val

    if template_file and not isinstance(response_val, dict):
        msg = f'Invalid return type {type(response_val)}, we expected a dict or Response as the return value.'
        raise ChameleonRobynException(msg)

    model = response_val

    # Pop framework hook before rendering — not a template variable
    response_callback = model.pop('__response_callback__', None)

    html = render(template_file, **model)
    resp = Response(
        status_code=status_code,
        description=html,
        headers=Headers({'Content-Type': f'{content_type}; charset=utf-8'}),
    )

    # Let the app customize the response (e.g., write session cookies)
    if callable(response_callback):
        response_callback(resp)

    return resp


def not_found(four04template_file: str = 'errors/404.pt'):
    msg = 'The URL resulted in a 404 response.'

    if four04template_file and four04template_file.strip():
        raise ChameleonRobynNotFoundException(msg, four04template_file)
    else:
        raise ChameleonRobynNotFoundException(msg)


@runtime_checkable
class TemplateInterface(Protocol):
    """Protocol matching Robyn's TemplateInterface without importing Jinja2."""

    def render_template(self, *args, **kwargs) -> Response: ...


class ChameleonTemplate(TemplateInterface):
    """Chameleon template engine implementing Robyn's TemplateInterface."""

    def __init__(
        self,
        directory: str,
        auto_reload=False,
        encoding='utf-8',
        restricted_namespace=True,
    ):
        self.loader = PageTemplateLoader(
            directory,
            auto_reload=auto_reload,
            restricted_namespace=restricted_namespace,
        )
        self.encoding = encoding

    def render_template(self, template_name: str, **kwargs) -> Response:
        page: PageTemplate = self.loader[template_name]
        rendered = page.render(encoding=self.encoding, **kwargs)
        return Response(
            status_code=status_codes.HTTP_200_OK,
            description=rendered,
            headers=Headers({'Content-Type': 'text/html; charset=utf-8'}),
        )
