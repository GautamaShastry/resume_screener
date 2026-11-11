"""Import every models module so Base.metadata is complete (Alembic, tests)."""

from app.analysis import models as _analysis  # noqa: F401
from app.auth import models as _auth  # noqa: F401
from app.postings import models as _postings  # noqa: F401
from app.quotas import models as _quotas  # noqa: F401
from app.resumes import models as _resumes  # noqa: F401
from app.tasks import models as _tasks  # noqa: F401
