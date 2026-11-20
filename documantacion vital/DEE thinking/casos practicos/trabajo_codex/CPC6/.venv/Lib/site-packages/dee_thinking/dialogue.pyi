from dataclasses import dataclass
from pathlib import Path
from typing import Any
from .cognition import Session

@dataclass(frozen=True)
class Command:
    operation: str
    argument: object = None
HELP: str
def normalize(text: str) -> str: ...
def parse(text: str) -> Command: ...
def render(result: dict[str, Any], operation: str) -> dict[str, Any]: ...
class ConversationSession:
    METADATA_KEY: str
    profile: str
    directory: Path
    preparation: dict[str, Any]
    session: Session | None
    aliases: dict[str, dict[str, str]]
    last_reference: dict[str, str] | None
    saved_path: Path | None
    def __init__(self, profile: str = "continuidad", *, directory: str | Path = "sesion", preparation: dict[str, Any] | None = None) -> None: ...
    def execute(self, text: str) -> dict[str, Any]: ...
