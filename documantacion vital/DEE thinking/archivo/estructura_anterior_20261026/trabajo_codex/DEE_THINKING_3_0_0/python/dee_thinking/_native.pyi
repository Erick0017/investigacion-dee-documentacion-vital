from enum import Enum
from typing import Any, Optional, Sequence

__version__: str
KERNEL_MODULUS: int
REDUCER_CAP: int

class Backend(Enum):
    DENSE_SEQUENTIAL: Backend
    DENSE_PARALLEL: Backend
    LAZY: Backend

class TickOptions:
    backend: Backend
    threads: int
    def __init__(self, backend: Backend = ..., threads: int = 1) -> None: ...

class Coordinate:
    x: int
    y: int
    z: int
    def __init__(self, x: int = 0, y: int = 0, z: int = 0) -> None: ...

class Direction:
    dx: int
    dy: int
    dz: int
    def __init__(self, dx: int = 0, dy: int = 0, dz: int = 0) -> None: ...

class Record:
    raw: int
    state: int
    s_reg: int
    dx: int
    dy: int
    dz: int
    semantic: int
    raw_present: bool
    occupied: bool

class Observation:
    tick: int
    coordinate: Coordinate
    raw: int
    clock: int
    record: Record

class Runtime:
    def __init__(self, dimension: int) -> None: ...
    @staticmethod
    def load_snapshot(path: str) -> Runtime: ...
    def save_snapshot(self, path: str) -> None: ...
    def fork(self) -> Runtime: ...
    def diagnostic_fork(self, edits: Sequence[ResearchStateEdit], authorize_diagnostic_intervention: bool) -> Runtime: ...
    def advance(self, count: int = 1): ...
    def run_until(self, target_tick: int): ...
    def pause(self) -> None: ...
    def resume(self) -> None: ...
    def observe(self, coordinate: Coordinate) -> Observation: ...
    def raw_copy(self) -> list[int]: ...
    def clock_copy(self) -> list[int]: ...
    @property
    def current_tick(self) -> int: ...
    @property
    def dimension(self) -> int: ...

class ResearchStateEdit:
    coordinate: Coordinate
    raw: Optional[int]
    clock: Optional[int]
    label: str
    def __init__(self) -> None: ...

class BasalPreset(Enum):
    RELATIONAL_BODY: BasalPreset
    CONTEXTUAL_REWRITE: BasalPreset
class BasalHistory(Enum):
    AB: BasalHistory
    BA: BasalHistory
    H0: BasalHistory
    SIMULTANEOUS: BasalHistory
    SHAM: BasalHistory
class BasalControl(Enum):
    FULL: BasalControl
    NO_ACTION: BasalControl
    RETURN_CUT: BasalControl
    OFF_PATH: BasalControl
    PHASE_MISS: BasalControl
    BARE: BasalControl
    READ_CUT: BasalControl
    ACTION_CUT: BasalControl
class BasalDomainMode(Enum):
    VALIDATED: BasalDomainMode
    RESEARCH: BasalDomainMode
class BasalAvailability(Enum):
    AVAILABLE: BasalAvailability
    MISSING_A: BasalAvailability
    MISSING_B: BasalAvailability
    MISSING_COMPARATOR: BasalAvailability

class BasalConfig:
    preset: BasalPreset
    history: BasalHistory
    control: BasalControl
    domain_mode: BasalDomainMode
    dimension: int
    origin: Coordinate
    action_distance: int
    execution: TickOptions
    seed_snapshot: str
    def __init__(self) -> None: ...
    @staticmethod
    def relational_reference(seed_snapshot: str) -> BasalConfig: ...
    @staticmethod
    def contextual_reference(seed_snapshot: str) -> BasalConfig: ...

class BasalPorts:
    origin: Coordinate
    a: Coordinate
    b: Coordinate
    comparator: Coordinate
    reader_source: Coordinate
    event_sources: list[Coordinate]
    supports: list[Coordinate]
    environmental_sources: list[Coordinate]
    action_site: Optional[Coordinate]
    return_site: Optional[Coordinate]
    bend_site: Optional[Coordinate]
    bend2_site: Optional[Coordinate]

class BasalObservation:
    absolute_tick: int
    relative_tick: int
    availability: BasalAvailability
    a: Optional[Observation]
    b: Optional[Observation]
    comparator: Optional[Observation]
    delta: Optional[int]
    axis_projection: Optional[int]
    supports: list[Observation]

class BasalWorld:
    @staticmethod
    def create(config: BasalConfig) -> BasalWorld: ...
    @staticmethod
    def attach(runtime: Runtime, config: BasalConfig, ports: BasalPorts, t0_tick: int) -> BasalWorld: ...
    @staticmethod
    def load_snapshot(path: str) -> BasalWorld: ...
    @property
    def config(self) -> BasalConfig: ...
    @property
    def ports(self) -> BasalPorts: ...
    @property
    def t0_tick(self) -> int: ...
    @property
    def runtime(self) -> Runtime: ...
    def advance(self, count: int = 1): ...
    def observe(self) -> BasalObservation: ...
    def fork(self) -> BasalWorld: ...
    def diagnostic_fork(self, edits: Sequence[ResearchStateEdit], authorize_diagnostic_intervention: bool) -> BasalWorld: ...
    def save_snapshot(self, path: str) -> None: ...

class LocalSiteObservation:
    offset: Coordinate
    site: Coordinate
    raw: int
    clock: int
    record: Record
    raw_present: bool
    active_for_rule: bool
class WriteGateObservation:
    site: Coordinate
    absolute_tick: int
    local_clock: int
    center: Record
    center_available: bool
    n_active: int
    direction_sum: Direction
    tetra_pattern: Optional[int]
    hadron: bool
    rule_value: int
    survives_material_rule: bool
    semantic_protected: bool
    write_protected: bool
    k: int
    period: Optional[int]
    phase_remainder: Optional[int]
    ordinary_increment_condition: bool
    branch: str
    demux_status: str
    neighbors: list[LocalSiteObservation]
class SiteTransition:
    site: Coordinate
    tick_before: int
    tick_after: int
    raw_before: int
    raw_after: int
    clock_before: int
    clock_after: int
    changed_fields: list[str]
    classification: str
def inspect_write_gate(runtime: Runtime, site: Coordinate, include_neighbors: bool = True) -> WriteGateObservation: ...
def compare_site_transition(before: Runtime, after: Runtime, site: Coordinate) -> SiteTransition: ...

class TrackedSite:
    id: str
    site: Coordinate
    def __init__(self) -> None: ...
class TraceFrame:
    tick: int
    observations: list[Observation]
class TraceTransition:
    tick_before: int
    tick_after: int
    ids: list[str]
    changes: list[SiteTransition]
    scope: str
class PassiveTracker:
    def __init__(self, sites: Sequence[TrackedSite], frame_budget: int = 4096) -> None: ...
    def capture(self, runtime: Runtime) -> TraceFrame: ...
    @property
    def frames(self) -> list[TraceFrame]: ...
    @property
    def transitions(self) -> list[TraceTransition]: ...
    @property
    def frame_budget(self) -> int: ...
    @property
    def capture_stopped(self) -> bool: ...
    def clear_trace(self) -> None: ...

class AppliedDiagnosticEdit:
    site: Coordinate
    label: str
    raw_before: int
    raw_after: int
    clock_before: int
    clock_after: int
    raw_changed: bool
    clock_changed: bool
    touches_declared_support: bool
class DiagnosticComparison:
    parent_tick: int
    horizon: int
    edits: list[AppliedDiagnosticEdit]
    raw_different_sites: int
    clock_different_sites: int
    reference_observation: BasalObservation
    diagnostic_observation: BasalObservation
    parent_unchanged: bool
    modality: str
def compare_diagnostic_fork(parent: BasalWorld, edits: Sequence[ResearchStateEdit], horizon: int, authorize_diagnostic_intervention: bool) -> DiagnosticComparison: ...

def build_info() -> dict[str, object]: ...

# The native module retains the complete dynamic 2.2.0 surface.  This 3.0.0
# stub types every new contract while allowing type checkers to access legacy
# catalog/protocol symbols that are not yet exhaustively enumerated here.
def __getattr__(name: str) -> Any: ...
