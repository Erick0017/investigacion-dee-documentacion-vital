"""Python interface for the native DEE thinking 4.5.0 runtime.

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


def create_organization(recipe: str = "mobile_pair", **parameters):
    """Convenience only: native factories prepare every physical recipe.

    Changes to ``parameters`` are declared preparation parameters, never an
    adaptive policy. Basal factories obtain the bundled immutable seed.
    """
    origin = parameters.pop("origin", None)
    if origin is not None:
        origin = Coordinate(*origin)  # noqa: F405
    if recipe == "mobile_pair":
        r = OrganizationRecipe.mobile_pair(origin or Coordinate())  # noqa: F405
    elif recipe in ("cascade", "native_transfer", "competition", "predictive"):
        factory = getattr(OrganizationRecipe, recipe)  # noqa: F405
        if recipe == "cascade":
            r = factory(parameters.pop("depth", 4), origin or Coordinate())  # noqa: F405
        else:
            r = factory(origin or Coordinate())  # noqa: F405
    elif recipe == "phase":
        r = OrganizationRecipe.phase(parameters.pop("mode", 0), origin or Coordinate(15,15,15))  # noqa: F405
    elif recipe == "distributed":
        r = OrganizationRecipe.distributed(parameters.pop("history_mode", 1), origin or Coordinate(30,30,30))  # noqa: F405
    elif recipe in ("relational", "contextual", "mobile_basal", "contingent", "information"):
        seed = reference_seed_path()
        o = origin or Coordinate(15,15,15)  # noqa: F405
        h = parameters.pop("history", BasalHistory.AB)  # noqa: F405
        if recipe == "relational":
            r = OrganizationRecipe.relational(seed,h,parameters.pop("keep_reader",False),o)  # noqa: F405
        elif recipe == "mobile_basal":
            r = OrganizationRecipe.mobile_basal(seed,h,o)  # noqa: F405
        elif recipe == "information":
            r = OrganizationRecipe.information(seed,h,parameters.pop("hidden",23),o)  # noqa: F405
        else:
            r = getattr(OrganizationRecipe,recipe)(seed,o)  # noqa: F405
            values = dict(r.parameters); values["history"] = int(h); r.parameters=values
    else:
        raise ValueError(f"Unknown recipe {recipe!r}; use OrganizationRecipe.research for explicit preparations")
    values = dict(r.parameters)
    options = dict(r.options)
    for name, value in parameters.items():
        if isinstance(value,str): options[name]=value
        else: values[name]=value
    r.parameters=values; r.options=options
    return OrganizationalWorld.create(r)  # noqa: F405


from .cognition import create_session, load_session, Session
from .dialogue import ConversationSession, parse as parse_spanish
from .consolidated import RepertoireSession, IntegratedSession, create_integrated_session
from .remote_reader import RemoteReaderSession

__all__ = [name for name in globals() if not name.startswith("_")]
