"""Python interface for the native DEE thinking 2.2.0 runtime.

The extension and the standalone C++ library are compiled from the same v27
kernel/runtime sources.  Importing this package never imports or delegates to
``dee_universe_v27``.
"""

from ._native import *  # noqa: F403
from ._native import __version__, build_info

# The native configuration object controls the scheduler only; dimension and
# physical state remain explicit Runtime construction arguments.
RuntimeConfig = TickOptions  # noqa: F405


def kernel_identity() -> dict[str, object]:
    """Return the immutable public identity of the embedded v27 kernel."""

    return {
        "kernel_version": 27,
        "kernel_modulus": KERNEL_MODULUS,  # noqa: F405
        "reducer_cap": REDUCER_CAP,  # noqa: F405
        "native_module": build_info()["native_module"],
    }


__all__ = [name for name in globals() if not name.startswith("_")]
