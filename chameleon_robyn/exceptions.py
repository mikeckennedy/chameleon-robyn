from typing import Optional


class ChameleonRobynException(Exception):
    """
    Base exception for all chameleon-robyn errors (bad configuration, invalid return types, etc.).

    Examples:
        ```python
        try:
            chameleon_robyn.render('home/index.pt', title='Home')
        except chameleon_robyn.ChameleonRobynException as e:
            log.error('template setup problem: %s', e)
        ```
    """

    pass


class ChameleonRobynNotFoundException(ChameleonRobynException):
    """
    Raised by not_found() to signal a 404 from within a `@template`-decorated handler.

    The `@template` decorator catches this exception and renders the template it
    carries with a 404 status code, passing the message to the template as `message`.

    Args:
        message: Optional human-readable description of the 404.
        four04template_file: The 404 template to render, relative to the template folder.

    Examples:
        Raise it directly to supply your own message to the 404 template:

        ```python
        raise ChameleonRobynNotFoundException(f'No episode with id {episode_id}.')
        ```
    """

    def __init__(self, message: Optional[str] = None, four04template_file: str = 'errors/404.pt'):
        super().__init__(message)

        self.template_file: str = four04template_file
        self.message: Optional[str] = message
