"""Python interface for the native DEE thinking 3.0.0 runtime.

The extension and the standalone C++ library are compiled from the same v27
kernel/runtime sources.  Importing this package never imports or delegates to
``dee_universe_v27``.
"""

from ._native import *  # noqa: F403
from ._native import __version__, build_info

from importlib.resources import files as _resource_files

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


def reference_seed_path() -> str:
    """Return the packaged, immutable MBP4 T32 seed used by bounded presets."""

    return str(_resource_files(__package__).joinpath("data", "OBP_FRESH_VALIDATED_T32.deetsnap"))


def create_relational_world(
    history=BasalHistory.AB,  # noqa: F405
    *,
    origin=(15, 15, 15),
    control=BasalControl.FULL,  # noqa: F405
    domain_mode=BasalDomainMode.VALIDATED,  # noqa: F405
    backend=Backend.LAZY,  # noqa: F405
    threads: int = 1,
):
    """Create the bounded relational-body preset from its declared T32 seed."""

    config = BasalConfig.relational_reference(reference_seed_path())  # noqa: F405
    config.history = history
    config.origin = Coordinate(*origin)  # noqa: F405
    config.control = control
    config.domain_mode = domain_mode
    config.execution = TickOptions(backend, threads)  # noqa: F405
    return BasalWorld.create(config)  # noqa: F405


def create_contextual_world(
    *,
    origin=(15, 15, 15),
    control=BasalControl.FULL,  # noqa: F405
    domain_mode=BasalDomainMode.VALIDATED,  # noqa: F405
    backend=Backend.LAZY,  # noqa: F405
    threads: int = 1,
):
    """Create the bounded MBP4 contextual/phase preset before evolution."""

    config = BasalConfig.contextual_reference(reference_seed_path())  # noqa: F405
    config.origin = Coordinate(*origin)  # noqa: F405
    config.control = control
    config.domain_mode = domain_mode
    config.execution = TickOptions(backend, threads)  # noqa: F405
    return BasalWorld.create(config)  # noqa: F405


__all__ = [name for name in globals() if not name.startswith("_")]
