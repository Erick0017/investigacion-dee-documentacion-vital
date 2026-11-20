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

# The native module retains the complete dynamic 2.2.0 surface.  This 3.5.0
# stub types every new contract while allowing type checkers to access legacy
# catalog/protocol symbols that are not yet exhaustively enumerated here.
def __getattr__(name: str) -> Any: ...

class OperationModality(Enum):
    NATIVE_EVOLUTION: OperationModality
    EXPERIENCE_PROTOCOL: OperationModality
    PASSIVE_OBSERVATION: OperationModality
    PHYSICAL_PROBE: OperationModality
    DIAGNOSTIC_FORK: OperationModality
    ASSISTED_RECONSTRUCTION: OperationModality
class CodecType(Enum):
    BOUNDED_INTEGER: CodecType
    BOOLEAN: CodecType
    ENUMERATION: CodecType
    REGISTERED_PATTERN: CodecType
class InputCodec:
    version: str
    type: CodecType
    minimum: int
    maximum: int
    symbols: dict[str,int]
    @property
    def injective(self) -> bool: ...
    def __init__(self) -> None: ...
    def validate(self) -> None: ...
    def encode_integer(self, value: int) -> int: ...
    def encode_symbol(self, value: str) -> int: ...
class InterfaceSpec:
    name: str
    channel: ChannelSpec
    codec: InputCodec
    admission: str
    meaning_location: str
    def __init__(self) -> None: ...
class DecodedOutput:
    physical: Observation
    integer: Optional[int]
    symbols: list[str]
    available: bool
    ambiguous: bool
    ordinary_cap_reached: bool
    status: str
class OutputDecoder:
    version: str
    type: CodecType
    symbols: dict[str,int]
    def __init__(self) -> None: ...
    def decode(self, observation: Observation) -> DecodedOutput: ...
class InitialPlacement:
    site: Coordinate
    raw: int
    clock: int
    role: str
    def __init__(self) -> None: ...
class OrganizationSpec:
    id: str
    recipe_id: str
    ports: dict[str,Coordinate]
    supports: list[Coordinate]
    a: Optional[Coordinate]
    b: Optional[Coordinate]
    comparator: Optional[Coordinate]
    t0_tick: int
    def __init__(self) -> None: ...
class ActionCoupling:
    id: str
    sites: list[Coordinate]
    roles: list[str]
    observation_ticks: list[int]
    scope: str
    def __init__(self) -> None: ...
class OrganizationRecipe:
    id: str
    version: str
    dimension: int
    origin: Coordinate
    parameters: dict[str,int]
    options: dict[str,str]
    placements: list[InitialPlacement]
    interfaces: list[InterfaceSpec]
    organizations: list[OrganizationSpec]
    actions: list[ActionCoupling]
    execution: TickOptions
    t0_tick: int
    domain: str
    def __init__(self) -> None: ...
    @staticmethod
    def mobile_pair(translation: Coordinate = ...) -> OrganizationRecipe: ...
    @staticmethod
    def cascade(depth: int = 4, translation: Coordinate = ...) -> OrganizationRecipe: ...
    @staticmethod
    def native_transfer(translation: Coordinate = ...) -> OrganizationRecipe: ...
    @staticmethod
    def phase(mode: int = 0, origin: Coordinate = ...) -> OrganizationRecipe: ...
    @staticmethod
    def distributed(history_mode: int = 1, origin: Coordinate = ...) -> OrganizationRecipe: ...
    @staticmethod
    def relational(seed: str, history: BasalHistory = ..., keep_reader: bool = False, origin: Coordinate = ...) -> OrganizationRecipe: ...
    @staticmethod
    def contextual(seed: str, origin: Coordinate = ...) -> OrganizationRecipe: ...
    @staticmethod
    def mobile_basal(seed: str, history: BasalHistory = ..., origin: Coordinate = ...) -> OrganizationRecipe: ...
    @staticmethod
    def contingent(seed: str, origin: Coordinate = ...) -> OrganizationRecipe: ...
    @staticmethod
    def information(seed: str, history: BasalHistory = ..., hidden: int = 23, origin: Coordinate = ...) -> OrganizationRecipe: ...
    @staticmethod
    def competition(translation: Coordinate = ...) -> OrganizationRecipe: ...
    @staticmethod
    def predictive(translation: Coordinate = ...) -> OrganizationRecipe: ...
    @staticmethod
    def research(dimension: int, placements: Sequence[InitialPlacement], tick: int = 0) -> OrganizationRecipe: ...
class FunctionalReadout:
    organization_id: str
    tick: int
    relative_tick: int
    observations: dict[str,Observation]
    delta: Optional[int]
    centers_available: bool
    reader_available: bool
    supports_intact: bool
    axis_projection: Optional[int]
    scope: str
class ResilienceObservation:
    functional: FunctionalReadout
    missing_supports: list[Coordinate]
    ordinary_cap_sites: list[str]
    representable_cap_sites: list[str]
    recovery_claim: str
class TraceSample:
    id: str
    tick: int
    observation: Observation
    relative_to_origin: Coordinate
    unwrapped: list[int]
    coverage: str
class MobileSegment:
    id: str
    birth_site: Coordinate
    direction: Direction
    birth_tick: int
    last_tick: int
    expected_load: Optional[int]
    expected_semantic: Optional[int]
    correspondence_stopped: bool
    def __init__(self) -> None: ...
class TraceSession:
    sample_budget: int
    sites: dict[str,Coordinate]
    segments: list[MobileSegment]
    samples: list[TraceSample]
    capture_stopped: bool
    def __init__(self) -> None: ...
    def capture(self, runtime: Runtime, origin: Coordinate = ...) -> None: ...
    def export_trace(self, path: str) -> None: ...
    @staticmethod
    def load_trace(path: str) -> TraceSession: ...
class EncounterObservation:
    tick_before: int
    tick_after: int
    destination: Coordinate
    before: Observation
    after: Observation
    direct_ballistic_contributors: list[Observation]
    destination_gate: WriteGateObservation
    branch: str
    attribution_scope: str
def observe_encounter(before: Runtime, after: Runtime, destination: Coordinate) -> EncounterObservation: ...
class DiagnosticEditReceipt:
    site: Coordinate
    label: str
    tick: int
    raw_before: int
    raw_after: int
    clock_before: int
    clock_after: int
    modality: OperationModality
class ReconstructionSpec:
    source_sites: list[Coordinate]
    destination_sites: list[Coordinate]
    copy_raw: bool
    copy_clocks: bool
    authorize_assisted_reconstruction: bool
    def __init__(self) -> None: ...
class QueryStep:
    input_tick: int
    read_tick: int
    input: int
    receipt_ids: list[int]
    targets: list[Coordinate]
    captured: list[Observation]
class QueryProtocol:
    id: str
    kind: str
    modality: OperationModality
    steps: list[QueryStep]
    next_capture: int
class OrganizationView:
    @property
    def spec(self) -> OrganizationSpec: ...
    @property
    def runtime(self) -> Runtime: ...
    def observe(self) -> FunctionalReadout: ...
    def resilience(self) -> ResilienceObservation: ...
class OrganizationalWorld:
    @staticmethod
    def create(recipe: OrganizationRecipe) -> OrganizationalWorld: ...
    @staticmethod
    def attach(runtime: Runtime, recipe: OrganizationRecipe, specs: Sequence[OrganizationSpec]) -> OrganizationalWorld: ...
    @staticmethod
    def load_snapshot(path: str) -> OrganizationalWorld: ...
    @property
    def runtime(self) -> Runtime: ...
    @property
    def recipe(self) -> OrganizationRecipe: ...
    @property
    def organization_ids(self) -> list[str]: ...
    @property
    def interfaces(self) -> list[InterfaceSpec]: ...
    @property
    def protocols(self) -> list[QueryProtocol]: ...
    @property
    def diagnostic_edits(self) -> list[DiagnosticEditReceipt]: ...
    @property
    def external_operations(self) -> list[str]: ...
    def view(self, id: str) -> OrganizationView: ...
    def declare_interface(self, spec: InterfaceSpec) -> None: ...
    def submit(self, name: str, value: int, at_tick: int) -> EventReceipt: ...
    def submit_symbol(self, name: str, value: str, at_tick: int) -> EventReceipt: ...
    def probe(self, name: str, value: int, at_tick: int) -> EventReceipt: ...
    def probe_symbol(self, name: str, value: str, at_tick: int) -> EventReceipt: ...
    def observe(self, organization: str, port: str) -> Observation: ...
    def decode(self, organization: str, port: str, decoder: OutputDecoder) -> DecodedOutput: ...
    def declare_decoder(self, name: str, decoder: OutputDecoder) -> None: ...
    def decoder(self, name: str) -> OutputDecoder: ...
    def advance(self, count: int = 1) -> TickInfo: ...
    def run_until(self, absolute_tick: int) -> TickInfo: ...
    def start_mobile_sequence(self, id: str, inputs: Sequence[int], first_tick: int = 6, interval: int = 5) -> None: ...
    def fork(self) -> OrganizationalWorld: ...
    def diagnostic_fork(self, edits: Sequence[ResearchStateEdit], authorize: bool) -> OrganizationalWorld: ...
    def assisted_reconstruction(self, source: OrganizationalWorld, spec: ReconstructionSpec) -> OrganizationalWorld: ...
    def set_trace(self, trace: TraceSession) -> None: ...
    def trace(self) -> TraceSession: ...
    def capture_trace(self) -> None: ...
    def save_snapshot(self, path: str, include_trace: bool = True) -> None: ...
