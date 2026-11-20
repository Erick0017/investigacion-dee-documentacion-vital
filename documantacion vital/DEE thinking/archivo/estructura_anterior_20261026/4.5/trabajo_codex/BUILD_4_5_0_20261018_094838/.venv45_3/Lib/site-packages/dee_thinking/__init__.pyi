from ._native import *
from ._native import __version__, build_info
from typing import Any
from .cognition import Session as Session, create_session as create_session, load_session as load_session
from .dialogue import ConversationSession as ConversationSession, parse as parse_spanish

RuntimeConfig = TickOptions

def kernel_identity() -> dict[str, object]: ...
def reference_seed_path() -> str: ...
def create_relational_world(
    history: BasalHistory = BasalHistory.AB,
    *,
    origin: tuple[int, int, int] = (15, 15, 15),
    control: BasalControl = BasalControl.FULL,
    domain_mode: BasalDomainMode = BasalDomainMode.VALIDATED,
    backend: Backend = Backend.LAZY,
    threads: int = 1,
) -> BasalWorld: ...
def create_contextual_world(
    *,
    origin: tuple[int, int, int] = (15, 15, 15),
    control: BasalControl = BasalControl.FULL,
    domain_mode: BasalDomainMode = BasalDomainMode.VALIDATED,
    backend: Backend = Backend.LAZY,
    threads: int = 1,
) -> BasalWorld: ...

# See ``_native.pyi``: legacy 2.2.0 names remain available dynamically while
# the additions introduced in 3.0.0 and 3.5.0 have precise declarations.
def create_organization(recipe: str = "mobile_pair", **parameters: Any) -> OrganizationalWorld: ...
def __getattr__(name: str) -> Any: ...

from .consolidated import RepertoireSession as RepertoireSession, IntegratedSession as IntegratedSession, create_integrated_session as create_integrated_session
from .remote_reader import RemoteReaderSession as RemoteReaderSession
