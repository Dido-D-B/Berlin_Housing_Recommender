# berlin_housing/cleaning/__init__.py

"""
Convenience imports for berlin_housing.cleaning.

Usage:
    from berlin_housing.cleaning import clean_census_2022, build_bezirk_enrichment, ...
"""

# Import submodules as module objects for access to their __all__
from . import clean_shared as _clean_shared
from . import clean_bezirk as _clean_bezirk
from . import clean_census as _clean_census
from . import clean_ortsteil as _clean_ortsteil

# Re-export public symbols from each submodule
from .clean_shared import *    # noqa: F401,F403
from .clean_bezirk import *    # noqa: F401,F403
from .clean_census import *    # noqa: F401,F403
from .clean_ortsteil import *  # noqa: F401,F403

# Build a flat __all__ from submodule __all__ lists (if present)
__all__ = (
    list(getattr(_clean_shared, "__all__", []))
    + list(getattr(_clean_bezirk, "__all__", []))
    + list(getattr(_clean_census, "__all__", []))
    + list(getattr(_clean_ortsteil, "__all__", []))
)