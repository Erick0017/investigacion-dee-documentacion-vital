"""Stubs for the consolidated C++ bindings exported by ``._native``.

This is a typing include, not a second extension module. Preparation factories
describe an untrained initial geometry; protocol helpers queue physical inputs.
"""
from typing import Any, NotRequired, Optional, TypedDict
from ._native import (
    Coordinate, Direction, EventReceipt, Observation, OrganizationRecipe,
    OrganizationalWorld, TickOptions,
)

class FormGeometry(TypedDict):
    index: int
    name: str
    hub: list[int]

class NativeGeometry(TypedDict):
    schema: str
    kind: str
    N: int
    K: int
    scope: str
    initial_state_available: bool
    parameters: dict[str, int]
    ticks: dict[str, int]
    ports: dict[str, str]
    sites: dict[str, list[int]]
    directions: dict[str, list[int]]
    forms: list[FormGeometry]
    initial_material_sites: int
    interfaces: int
    plane_gap: int
    translation: NotRequired[list[int]]
    body: NotRequired[dict[str, Any]]
    need: NotRequired[dict[str, Any]]
    banks: NotRequired[dict[str, dict[str, Any]]]
    names: NotRequired[dict[str, dict[str, Any]]]
    action_inputs: NotRequired[dict[str, dict[str, Any]]]
    actions: NotRequired[dict[str, dict[str, Any]]]
    traditional_datasource_interfaces_installed: NotRequired[bool]
    shared_interface_policy: NotRequired[str]
    residue_guard: NotRequired[dict[str, Any]]
    integrated_revision: NotRequired[dict[str, Any]]

class PhysicalReadoutDict(TypedDict):
    tick: int
    site: list[int]
    raw: str
    clock: str
    state: int
    s_reg: int
    semantic: int
    direction: list[int]
    active: bool

class ReadoutReceiptDict(TypedDict):
    id: int
    status: str
    kind: str
    requested_tick: int
    effective_tick: Optional[int]
    channels: list[str]
    reason: str

class DirectionalReadoutDict(TypedDict):
    physical: PhysicalReadoutDict
    receipt: Optional[ReadoutReceiptDict]
    applied: bool
    covered: bool
    coverage: bool
    value: Optional[int]
    status: str
    ordinary_cap_reached: bool
    modality: str
    scope: str

class RepertoireOptions:
    dimension: int
    forms: int
    plane_gap: int
    translation: Coordinate
    revision_interfaces: bool
    revision_form: int
    execution: TickOptions
    def __init__(self) -> None: ...

class IntegratedOptions:
    center: Coordinate
    guard_mode: str
    body_source_load: int
    revision_interfaces: bool
    execution: TickOptions
    def __init__(self) -> None: ...

class FormDescriptor:
    @property
    def index(self) -> int: ...
    @property
    def name(self) -> str: ...
    @property
    def hub(self) -> Coordinate: ...

class NativePreparation:
    def __init__(self) -> None: ...
    @property
    def recipe(self) -> OrganizationRecipe: ...
    @property
    def kind(self) -> str: ...
    @property
    def domain(self) -> str: ...
    @property
    def forms(self) -> list[FormDescriptor]: ...
    @property
    def sites(self) -> dict[str, Coordinate]: ...
    @property
    def directions(self) -> dict[str, Direction]: ...
    @property
    def ticks(self) -> dict[str, int]: ...
    @property
    def ports(self) -> dict[str, str]: ...
    @property
    def parameters(self) -> dict[str, int]: ...
    @property
    def initial_state_available(self) -> bool: ...
    def create_world(self) -> OrganizationalWorld: ...
    def geometry(self) -> NativeGeometry: ...

class DirectionalReadout:
    @property
    def physical(self) -> Observation: ...
    @property
    def receipt(self) -> Optional[EventReceipt]: ...
    @property
    def applied(self) -> bool: ...
    @property
    def covered(self) -> bool: ...
    @property
    def coverage(self) -> bool: ...
    @property
    def ordinary_cap_reached(self) -> bool: ...
    @property
    def value(self) -> Optional[int]: ...
    @property
    def status(self) -> str: ...
    @property
    def modality(self) -> str: ...
    @property
    def scope(self) -> str: ...
    def as_dict(self) -> DirectionalReadoutDict: ...

def prepare_repertoire(options: RepertoireOptions = ...) -> NativePreparation: ...
def prepare_integrated_u0(options: IntegratedOptions = ...) -> NativePreparation: ...
def preparation_for_world(world: OrganizationalWorld) -> NativePreparation: ...
def attach_preparation_descriptor(
    world: OrganizationalWorld, preparation: NativePreparation,
) -> None: ...
def experience_form(
    world: OrganizationalWorld, preparation: NativePreparation,
    form_index: int, current_sign: int, at_tick: int,
    cue_load: int = 5, event_load: int = 11,
) -> list[EventReceipt]: ...
def query_form(
    world: OrganizationalWorld, preparation: NativePreparation,
    form_index: int, payload: int, at_tick: int,
) -> EventReceipt: ...
def revise_form(
    world: OrganizationalWorld, preparation: NativePreparation,
    form_index: int, current_sign: int, at_tick: int,
    method: str = "double_teacher", mode: str = "treatment",
    cue_load: int = 5, event_load: int = 11,
) -> list[EventReceipt]: ...
def read_directional_response(
    world: OrganizationalWorld, site: Coordinate, receipt_id: int,
    probe_load: int, expected_read_tick: Optional[int] = None,
) -> DirectionalReadout: ...
def read_form_response(
    world: OrganizationalWorld, preparation: NativePreparation,
    form_index: int, receipt_id: int, probe_load: int,
    expected_read_tick: Optional[int] = None,
) -> DirectionalReadout: ...
