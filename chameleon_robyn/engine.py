import inspect
import os
from functools import wraps
from typing import Any, Callable, NoReturn, Optional, Protocol, Union, runtime_checkable

from chameleon import PageTemplate, PageTemplateLoader
from robyn import Headers, Response, status_codes

from chameleon_robyn.exceptions import (
    ChameleonRobynException,
    ChameleonRobynNotFoundException,
)

__templates: Optional[PageTemplateLoader] = None
template_path: Optional[str] = None


def global_init(
    template_folder: str, auto_reload: bool = False, cache_init: bool = True, restricted_namespace: bool = True
) -> None:
    """
    Initialize the Chameleon template engine.

    Call this once at startup, before the first request is rendered. Routes may be
    decorated with `@template` before this runs; auto-named templates are resolved
    lazily at the first request.

    Args:
        template_folder: Path to the template directory. All template paths passed to
            `@template`, render(), response() and not_found() are relative to this folder.
        auto_reload: Whether to re-read templates when they change on disk. Use True in
            development only; it disables caching.
        cache_init: If True (the default) and the engine is already initialized, the call
            is ignored and the earlier settings stay in effect. Pass False to re-initialize
            with new settings (tests do this), or call clear() first.
        restricted_namespace: If True, only TAL/METAL/i18n namespaces are allowed in
            attributes. If False, attribute-based JS frameworks like Alpine.js and htmx can
            use shorthand syntax (`@click`, :class, etc.).

    Raises:
        ChameleonRobynException: If template_folder is empty or is not an existing directory.

    Examples:
        ```python
        from pathlib import Path
        import chameleon_robyn

        templates = (Path(__file__).resolve().parent / 'templates').as_posix()
        chameleon_robyn.global_init(templates, auto_reload=True)  # auto_reload for development only
        ```
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


def clear() -> None:
    """
    Reset the template engine to its uninitialized state.

    After calling this, global_init() must be called again before rendering.
    Mostly useful in tests to isolate template configuration between cases.

    Examples:
        ```python
        import pytest
        import chameleon_robyn

        @pytest.fixture
        def templates(tmp_path):
            chameleon_robyn.global_init(str(tmp_path), cache_init=False)
            yield
            chameleon_robyn.clear()
        ```
    """
    global __templates, template_path
    __templates = None
    template_path = None


def render(template_file: str, **template_data: Any) -> str:
    """
    Render a Chameleon template to a string (no Response wrapping).

    Useful outside of route handlers: emails, middleware, error handlers, etc.

    Args:
        template_file: The template file path, relative to the template folder (e.g. 'emails/welcome.pt').
        **template_data: Values passed to the template as its model. The key 'encoding' is
            reserved by Chameleon and cannot be used.

    Returns:
        The rendered template as a string.

    Raises:
        ChameleonRobynException: If global_init() has not been called, or the model uses the
            reserved key 'encoding'.
        ValueError: Raised by Chameleon when the template file does not exist.

    Examples:
        ```python
        html = chameleon_robyn.render('emails/welcome.pt', username='Michael')
        ```
    """
    if not __templates:
        raise ChameleonRobynException('You must call global_init() before rendering templates.')

    _check_reserved_keys(template_data)
    page: PageTemplate = __templates[template_file]
    return page.render(encoding='utf-8', **template_data)


def response(
    template_file: str, content_type: str = 'text/html', status_code: int = 200, **template_data: Any
) -> Response:
    """
    Render a Chameleon template and wrap it in a fully-formed Robyn Response.

    Useful where the `@template` decorator does not fit: error handlers, middleware, or a
    handler that renders different templates depending on the request.

    Args:
        template_file: The template file path, relative to the template folder.
        content_type: The Content-Type header value (defaults to text/html).
        status_code: The HTTP status code for the response (defaults to 200).
        **template_data: Values passed to the template as its model.

    Returns:
        A Robyn Response with the rendered template as its body.

    Raises:
        ChameleonRobynException: If global_init() has not been called, or the model uses the
            reserved key 'encoding'.

    Examples:
        ```python
        resp = chameleon_robyn.response('errors/500.pt', status_code=500, error=str(e))
        ```
    """
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
) -> Callable:
    """
    Decorate a Robyn view method to render an HTML response.

    The decorated handler returns a dict (the template model). If the template path is
    omitted, it is derived from the module and function name: module/function.html if that
    file exists, otherwise module/function.pt. For a script run directly (module __main__)
    the script's file name is used instead, so index() in app.py maps to app/index.pt; a
    legacy __main__/function.html or .pt is still found if the script-named file does not
    exist. The auto-derived name is resolved at first request, so global_init() may be called after
    route decoration. Handlers that return a Robyn Response are passed through untouched
    (redirects, custom errors). Works with sync and async handlers.

    Place `@template` directly above the handler, below Robyn's route decorator.

    Args:
        template_file: Optional, the Chameleon template file (path relative to template folder, *.pt).
        content_type: The Content-Type header value for rendered responses (defaults to text/html).
        status_code: The HTTP status code for rendered responses (defaults to 200).

    Returns:
        Decorator for Robyn route handlers.

    Raises:
        ChameleonRobynException: At request time, if the handler returns something other than a
            dict or a Robyn Response, or if '__response_callback__' is not callable.

    Examples:
        ```python
        @app.get('/episodes/:episode_id')
        @chameleon_robyn.template('episodes/detail.pt')
        async def episode_detail(request, episode_id: int):
            return {'episode': await get_episode(episode_id)}

        @app.get('/')
        @chameleon_robyn.template  # renders <module>/index.html or <module>/index.pt
        def index(request):
            return {'title': 'Home'}
        ```
    """

    wrapped_function = None
    if callable(template_file):
        wrapped_function = template_file
        template_file = None

    def response_inner(f):
        # Resolved into a local so reusing one decorator instance across several
        # functions can't leak the first function's auto-derived template name.
        resolved_file: Optional[str] = template_file if isinstance(template_file, str) and template_file else None

        def resolve_template_file() -> str:
            # Auto-naming is resolved lazily, at first request, because the template
            # folder is usually not known yet when routes are decorated at import time
            # (apps commonly call global_init() from main()).
            nonlocal resolved_file
            if resolved_file is not None:
                return resolved_file

            module = f.__module__
            if '.' in module:
                module = module.split('.')[-1]
            view = f.__name__
            folder = template_path or 'templates'

            # `python app.py` gives every handler the module name __main__, which is rarely a
            # useful template directory. Prefer the script's file stem (app/index.pt), but keep
            # looking under __main__/ so apps built on the old behavior still resolve.
            module_names = [module]
            code = getattr(f, '__code__', None)
            if module == '__main__' and code is not None:
                module_names.insert(0, os.path.splitext(os.path.basename(code.co_filename))[0])

            candidate = None
            for name in module_names:
                for ext in ('html', 'pt'):
                    option = f'{name}/{view}.{ext}'
                    if os.path.exists(os.path.join(folder, option)):
                        candidate = option
                        break
                if candidate:
                    break
            if candidate is None:
                # Nothing exists yet; report the preferred name so the error points at it.
                candidate = f'{module_names[0]}/{view}.pt'

            if template_path:
                # Only cache once the real template folder is known.
                resolved_file = candidate
            return candidate

        @wraps(f)
        def sync_view_method(*args, **kwargs) -> Response:
            try:
                response_val = f(*args, **kwargs)
                return __render_response(resolve_template_file(), response_val, content_type, status_code)
            except ChameleonRobynNotFoundException as nfe:
                return __render_response(nfe.template_file, {'message': nfe.message}, 'text/html', 404)

        @wraps(f)
        async def async_view_method(*args, **kwargs) -> Response:
            try:
                response_val = await f(*args, **kwargs)
                return __render_response(resolve_template_file(), response_val, content_type, status_code)
            except ChameleonRobynNotFoundException as nfe:
                return __render_response(nfe.template_file, {'message': nfe.message}, 'text/html', 404)

        if inspect.iscoroutinefunction(f):
            return async_view_method
        else:
            return sync_view_method

    return response_inner(wrapped_function) if wrapped_function else response_inner


def __is_response(resp: Any) -> bool:
    return isinstance(resp, Response)


def _check_reserved_keys(template_data: dict) -> None:
    # Chameleon's PageTemplate.render() takes the output encoding as a named parameter,
    # so a model key with the same name collides with it (TypeError deep inside Chameleon).
    if 'encoding' in template_data:
        msg = "'encoding' is reserved by Chameleon's render() and cannot be a template variable; rename the key."
        raise ChameleonRobynException(msg)


def __render_response(template_file: str, response_val: Any, content_type: str, status_code: int = 200) -> Response:
    if __is_response(response_val):
        return response_val

    if template_file and not isinstance(response_val, dict):
        msg = f'Invalid return type {type(response_val)}, we expected a dict or Response as the return value.'
        raise ChameleonRobynException(msg)

    # Copy so popping the framework hook never mutates the handler's dict
    # (handlers may return shared or module-level dicts).
    model = dict(response_val)

    # Pop framework hook before rendering — not a template variable
    response_callback = model.pop('__response_callback__', None)
    if response_callback is not None and not callable(response_callback):
        msg = f'__response_callback__ must be callable, got {type(response_callback)}.'
        raise ChameleonRobynException(msg)

    html = render(template_file, **model)
    resp = Response(
        status_code=status_code,
        description=html,
        headers=Headers({'Content-Type': f'{content_type}; charset=utf-8'}),
    )

    # Let the app customize the response (e.g., write session cookies)
    if response_callback is not None:
        response_callback(resp)

    return resp


def not_found(four04template_file: str = 'errors/404.pt') -> NoReturn:
    """
    Render a friendly 404 page from within a `@template`-decorated handler.

    Raises an exception that the `@template` decorator catches and converts into a
    404 response rendered through the given template. The template receives a
    `message` variable describing the 404. Only works inside handlers decorated
    with `@template`.

    Args:
        four04template_file: The template to render, relative to the template folder
            (defaults to 'errors/404.pt').

    Raises:
        ChameleonRobynNotFoundException: Always; carries the 404 template path.

    Examples:
        ```python
        @app.get('/episodes/:episode_id')
        @chameleon_robyn.template('episodes/detail.pt')
        def episode_detail(request, episode_id: int):
            episode = get_episode(episode_id)
            if not episode:
                chameleon_robyn.not_found()  # renders errors/404.pt with status 404
            return {'episode': episode}
        ```
    """
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
    """
    Chameleon template engine implementing Robyn's TemplateInterface.

    A standalone alternative to the module-level API: it owns its own template
    loader and does not require global_init(). Use it like Robyn's built-in
    JinjaTemplate.

    Args:
        directory: Path to the template directory.
        auto_reload: Whether to auto-reload templates on change (use True in development).
        encoding: Output encoding for rendered templates (defaults to utf-8).
        restricted_namespace: If True, only TAL/METAL/i18n namespaces are allowed.
            Set to False for Alpine.js/htmx-style attributes (`@click`, :class, etc.).

    Examples:
        ```python
        from chameleon_robyn import ChameleonTemplate

        chameleon = ChameleonTemplate('templates/', auto_reload=True)

        @app.get('/page')
        def page(request):
            return chameleon.render_template('page.pt', title='Hello')
        ```
    """

    def __init__(
        self,
        directory: str,
        auto_reload: bool = False,
        encoding: str = 'utf-8',
        restricted_namespace: bool = True,
    ):
        self.loader = PageTemplateLoader(
            directory,
            auto_reload=auto_reload,
            restricted_namespace=restricted_namespace,
        )
        self.encoding = encoding

    def render_template(self, template_name: str, **kwargs: Any) -> Response:
        """
        Render a template and return a 200 Robyn Response.

        Args:
            template_name: The template file path, relative to the directory given at construction.
            **kwargs: Values passed to the template as its model. The key 'encoding' is reserved.

        Returns:
            A Robyn Response with the rendered template as its body. The status is always 200
            and the Content-Type is always text/html.

        Raises:
            ChameleonRobynException: If the model uses the reserved key 'encoding'.
        """
        _check_reserved_keys(kwargs)
        page: PageTemplate = self.loader[template_name]
        rendered = page.render(encoding=self.encoding, **kwargs)
        return Response(
            status_code=status_codes.HTTP_200_OK,
            description=rendered,
            headers=Headers({'Content-Type': 'text/html; charset=utf-8'}),
        )
