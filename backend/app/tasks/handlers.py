"""Importing this module registers every task handler with the global registry."""

from app.analysis import handlers as _analysis  # noqa: F401
from app.postings import handlers as _postings  # noqa: F401
from app.resumes import handlers as _resumes  # noqa: F401
