"""Root Signals SDK.

The use should start by creating a :class:`root.client.RootSignals` instance.

Example::

  from root import RootSignals
  client = RootSignals()

"""

from .__about__ import __version__
from .client import RootSignals

# Note: PEP-396 was rejected but we provide __version__ anyway
# ( https://peps.python.org/pep-0396/ )
__all__ = ["__version__", "RootSignals"]
