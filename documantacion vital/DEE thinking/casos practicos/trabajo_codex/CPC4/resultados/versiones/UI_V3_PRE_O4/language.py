"""Spanish command structure and attributed presentation, never a DEE solver.

The parser does not read a history, target, seed-derived answer or NSM meaning.
Aliases are external forms for declared interface IDs. A physical backend must
explicitly implement each operation before the application can expose it.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shlex
import unicodedata


def keyword(value):
    return "".join(c for c in unicodedata.normalize("NFD", value.lower()) if not unicodedata.combining(c))


@dataclass(frozen=True)
class Command:
    operation: str
    arguments: tuple[str, ...] = ()


def parse(text):
    if not isinstance(text, str) or len(text) > 4096:
        raise ValueError("Orden de texto demasiado larga o inválida")
    tokens = shlex.split(text, posix=False)
    tokens = [x[1:-1] if len(x) >= 2 and x[0] == x[-1] == '"' else x for x in tokens]
    if not tokens or tokens[0].startswith("#"):
        return Command("comment")
    verb = keyword(tokens[0])
    if verb in ("ayuda", "salir", "observar", "diagnostico") and len(tokens) == 1:
        return Command({"ayuda": "help", "salir": "exit", "observar": "observe", "diagnostico": "diagnose"}[verb])
    if verb == "observa" and len(tokens) == 1:
        return Command("observe")
    if verb == "crear" and len(tokens) == 1:
        return Command("create")
    if verb == "crear" and len(tokens) == 3 and keyword(tokens[1]) == "semilla":
        try:
            seed = int(tokens[2])
        except ValueError:
            raise ValueError("Semilla entera explícita requerida") from None
        if str(seed) != tokens[2] or not 0 <= seed <= 4294967295:
            raise ValueError("Semilla fuera de uint32")
        return Command("create", (tokens[2],))
    if verb in ("guardar", "cargar") and len(tokens) == 2 and tokens[1]:
        return Command("save" if verb == "guardar" else "load", (tokens[1],))
    if verb == "avanzar" and len(tokens) == 2:
        try:
            count = int(tokens[1])
        except ValueError:
            raise ValueError("Cantidad entera de ticks requerida") from None
        if str(count) != tokens[1] or not 0 <= count <= 10000:
            raise ValueError("Avance fuera del límite de interfaz0..10000; el dominio físico puede ser menor")
        return Command("advance", (tokens[1],))
    if verb in ("catalogo", "catalogar") and len(tokens) in (1, 2):
        return Command("catalogue", tuple(tokens[1:]))
    if verb == "nombre" and len(tokens) == 3:
        if not tokens[1] or len(tokens[1]) > 40 or any(x.isspace() for x in tokens[1]):
            raise ValueError("El alias debe ser un token de hasta40caracteres")
        return Command("alias", (tokens[1], tokens[2]))
    if verb == "vivir" and len(tokens) == 4:
        return Command("live", tuple(tokens[1:]))
    if verb in ("experiencia", "ensenar") and len(tokens) >= 2:
        return Command("experience", tuple(tokens[1:]))
    if verb in ("consulta", "consultar") and len(tokens) in (2, 3):
        return Command("query", tuple(tokens[1:]))
    if verb in ("mensaje", "comunicar") and len(tokens) == 3:
        return Command("communicate", tuple(tokens[1:]))
    if [keyword(x) for x in tokens] == ["por", "que"]:
        return Command("explain")
    raise ValueError("Orden fuera de la gramática finita; usa ayuda")


class InterfaceAliases:
    """External text->declared interface identity only, never ID->function."""
    def __init__(self, valid_ids, aliases=None):
        self.valid_ids = frozenset(valid_ids)
        self.aliases = {}
        for name, identity in (aliases or {}).items():
            self.add(name, identity)

    def add(self, name, identity):
        if identity not in self.valid_ids or not isinstance(name, str) or not name or len(name) > 40 or any(c.isspace() for c in name):
            raise ValueError("Alias o ID de interfaz no declarado")
        if name in self.valid_ids and name != identity:
            raise ValueError("Un alias no puede usurpar otro ID físico")
        name = keyword(name)
        if name in {keyword(x) for x in self.valid_ids} and name != keyword(identity):
            raise ValueError("Un alias no puede usurpar otro ID físico")
        if name in self.aliases and self.aliases[name] != identity:
            raise ValueError("Alias existente; no se reasigna silenciosamente")
        self.aliases[name] = identity

    def resolve(self, name):
        if name in self.valid_ids:
            return name
        name = keyword(name)
        physical = {keyword(x): x for x in self.valid_ids}
        if name in physical:
            return physical[name]
        if name in self.aliases:
            return self.aliases[name]
        raise ValueError("Forma no registrada en la interfaz; no se infiere significado")

    def as_dict(self):
        return dict(self.aliases)


def catalogue_view(path, selector=None):
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if value.get("schema") != "CPC4.NSM65.documentary.v1" or len(value.get("entries", [])) != 65:
        raise ValueError("Catálogo NSM documental incompatible")
    if selector is None:
        return {"attribution": "EXPLICACION_DOCUMENTAL", "count": 65,
                "scope": value["source_scope"], "ids": [x["id"] for x in value["entries"]]}
    matches = [x for x in value["entries"] if selector == x["id"] or selector == x["forma_es"] or selector in x["variantes_documentadas"]]
    if not matches:
        raise ValueError("Forma o ID no presente en el catálogo versionado")
    return {"attribution": "EXPLICACION_DOCUMENTAL", "entries": matches,
            "scope": "Consultar la ficha no presenta una experiencia ni acredita aprendizaje DEE"}


def render(value):
    """Render only the backend's present measurements, preserving attribution."""
    attribution = value.get("attribution", "INTERFAZ")
    allowed = {"ENTE", "INSTRUMENTO", "INTERFAZ", "EXPLICACION_DOCUMENTAL", "GENERADOR_EXTERNO"}
    if attribution not in allowed:
        attribution = "INTERFAZ"
    # No conversion from an NSM ID, history ID or a user seed to a physical
    # response exists here. The backend must supply the current observation.
    if "physical_output" in value:
        physical = value["physical_output"]
        classification = (" Clase medida=" + str(value["resource_class"])) if value.get("available") and value.get("resource_class") else ""
        return f"{attribution}: t={physical.get('tick')}, RAW={physical.get('raw')}, dirección={physical.get('direction')}, carga={physical.get('s_reg')}.{classification} {value.get('scope', '')}"
    return attribution + ": " + json.dumps(value, ensure_ascii=False)
