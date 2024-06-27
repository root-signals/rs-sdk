"""Root Signals SDK.

The use should start by creating a :class:`root.client.RootSignals` instance.

Example::

  from root import RootSignals
  client = RootSignals()

"""

from .client import RootSignals

__all__ = ["RootSignals"]
