from typing import Optional


class ChameleonRobynException(Exception):
    """Base exception for all chameleon-robyn errors (bad configuration, invalid return types, etc.)."""

    pass


class ChameleonRobynNotFoundException(ChameleonRobynException):
    """
    Raised by not_found() to signal a 404 from within a @template-decorated handler.

    The @template decorator catches this exception and renders the template it
    carries with a 404 status code.

    Args:
        message: Optional human-readable description of the 404.
        four04template_file: The 404 template to render, relative to the template folder.
    """

    def __init__(self, message: Optional[str] = None, four04template_file: str = 'errors/404.pt'):
        super().__init__(message)

        self.template_file: str = four04template_file
        self.message: Optional[str] = message
