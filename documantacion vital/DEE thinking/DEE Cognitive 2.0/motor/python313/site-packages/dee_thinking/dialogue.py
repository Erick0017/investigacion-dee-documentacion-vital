"""Explicit Spanish commands and fixed presentation of native measurements.

The parser structures requests only. External aliases are interface references,
not learned DEE associations. No previous response is stored for answering.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import unicodedata

from .cognition import create_session, load_session


def normalize(text):
    if not isinstance(text, str):
        raise TypeError("La solicitud debe ser texto")
    folded = "".join(c for c in unicodedata.normalize("NFKD", text.casefold())
                     if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", folded.strip(" \t\r\n¿?¡!.,"))


@dataclass(frozen=True)
class Command:
    operation: str
    argument: object = None


def parse(text):
    value = normalize(text)
    fixed = {
        "ayuda": "help", "que puedo preguntar": "help", "salir": "exit",
        "instancia nueva": "new", "crear instancia": "new",
        "observa otra vez": "sense", "observa el entorno": "sense",
        "muestra el estado": "observe", "observa": "observe",
        "que pasara despues": "predict", "predice antes de observar": "predict",
        "predice": "predict", "ocurrira lo mismo": "predict",
        "compara esto con lo anterior": "compare", "compara": "compare",
        "que fuente necesitas observar": "source", "que informacion necesitas": "source",
        "que informacion llego": "information",
        "cual llegara primero": "arrival_order", "si cambia la ruta": "route_variant",
        "por que": "why", "retira el mediador": "remove_mediator",
        "retira mediador": "remove_mediator", "avanza el entorno": "advance",
        "guarda la sesion": "save", "continua desde la sesion guardada": "load",
        "carga la sesion": "load",
    }
    if value in fixed:
        return Command(fixed[value])
    for prefix in ("presenta experiencia ", "experiencia "):
        if value.startswith(prefix):
            return Command("experience", text.strip()[len(prefix):].strip())
    match = re.fullmatch(r"(?:consulta(?: nueva)?|pregunta)\s+([0-9]+)", value)
    if match:
        return Command("query", int(match.group(1)))
    match = re.fullmatch(r"consulta secuencia\s+([0-9]+(?:\s*,\s*[0-9]+){0,49})", value)
    if match:
        return Command("query_sequence", [int(x.strip()) for x in match.group(1).split(",")])
    match = re.fullmatch(r"consulta\s+(.+?)\s+con\s+([0-9]+)", value)
    if match:
        return Command("query_named", (match.group(1), int(match.group(2))))
    match = re.fullmatch(r"ensena relaciones\s+con senal\s+([0-9]+)\s+y referencias\s+([0-9]+)\s+y\s+([0-9]+)", value)
    if match:
        return Command("train", tuple(int(x) for x in match.groups()))
    match = re.fullmatch(r"ensena dos relaciones\s+([0-9]+)\s*,\s*([0-9]+)\s+y\s+([0-9]+)\s*,\s*([0-9]+)", value)
    if match:
        a, b, c, d = (int(x) for x in match.groups())
        return Command("train_all", [(a, b), (c, d)])
    match = re.fullmatch(r"avanza\s+([0-9]+)(?:\s+ticks)?", value)
    if match:
        return Command("advance", int(match.group(1)))
    match = re.fullmatch(r"\s*a esto lo llamaremos\s+(.+?)\s*[.!]?\s*", text, re.I)
    if match:
        return Command("name", match.group(1).strip())
    match = re.fullmatch(r"\s*a la ruta\s+([12])\s+la llamaremos\s+(.+?)\s*", text, re.I)
    if match:
        return Command("name_route", (int(match.group(1))-1, match.group(2).strip()))
    match = re.fullmatch(r"\s*(?:guarda|guardar)\s+(?:la sesi[oó]n\s+)?(?:en\s+)?(.+?)\s*", text, re.I)
    if match:
        return Command("save", match.group(1).strip())
    match = re.fullmatch(r"\s*(?:carga|cargar|contin[uú]a desde)\s+(.+?)\s*", text, re.I)
    if match:
        return Command("load", match.group(1).strip())
    raise ValueError("Entrada fuera de la gramática. Escribe «ayuda».")


HELP = (
    "Órdenes: Instancia nueva; Observa otra vez; Muestra el estado; "
    "¿Qué pasará después?; Compara esto con lo anterior; ¿Qué fuente necesitas observar?; "
    "Presenta experiencia A/B; A esto lo llamaremos X; Avanza [n ticks]; "
    "Guarda la sesión [en ruta]; Carga ruta; Salir. "
    "Perfil relaciones: Enseña relaciones con señal 5 y referencias 7 y 11; Consulta nueva 13. "
    "Perfil composicion: Enseña dos relaciones 3,9 y 3,11; Consulta nueva 13. "
    "También: Consulta secuencia 13,17,19; A la ruta 1 la llamaremos brisa; Consulta brisa con 13. "
    "Cada perfil informa su dominio finito. Las palabras son interfaz externa; "
    "no existe un modelo de lenguaje ni un diccionario de respuestas aprendidas."
)


def _unsupported(result):
    status = str(result.get("status", ""))
    return (result.get("modality") == "INTERFACE_NOT_NATIVE_ANSWER"
            or status.startswith(("OUTSIDE_", "UNSUPPORTED", "OPERATION_NOT_", "NO_PENDING", "INTERFACE_LIMIT")))


def render(result, operation):
    """Translate current native output. The complete measurement stays attached."""
    if not isinstance(result, dict):
        raise TypeError("Una medición nativa debe exponer su contrato de datos")
    output = {"attribution": "ENTE", "operation": operation, "measurement": result}
    if _unsupported(result):
        output.update(attribution="INSTRUMENTO", text=(
            "La operación no tiene una nueva respuesta física dentro de este perfil/ventana: "
            + str(result.get("status", "dominio no declarado")) + ". No se devuelve una respuesta guardada."))
        return output
    if operation == "predict":
        values = result.get("prediction_set", [])
        status = str(result.get("status", ""))
        if "COMPARISON" in status or result.get("comparison_marker_present"):
            output.update(attribution="INSTRUMENTO", text="El registro actual es una comparación, no una nueva predicción.")
        elif values == [True] or values == [1]:
            output["text"] = "La emisión física actual indica llegada para el objetivo declarado."
        elif values == [False] or values == [0]:
            output["text"] = "La emisión física actual indica ausencia para el objetivo declarado."
        else:
            output["text"] = "La emisión actual no resuelve una predicción única. Ausencia de emisión no se convierte en cero."
    elif operation in ("compare", "sense"):
        comparisons = result.get("comparisons", [])
        decoder = result.get("comparison_decoder", {})
        presentation = decoder.get("presentation")
        if presentation in ("coincidencia_direccional", "discrepancia_direccional"):
            output["text"] = "El producto físico actual expresa " + presentation.replace("_direccional", "") + ". No se interpreta como pronóstico."
        elif len(comparisons) == 1 and comparisons[0].get("presentation"):
            output["text"] = "El producto físico actual expresa " + str(comparisons[0]["presentation"]) + "."
        else:
            output["text"] = "Se ejecutó la interacción declarada. Sus recibos y lecturas físicas determinan qué se aplicó."
    elif operation == "source":
        actions = result.get("actions", [])
        source = result.get("source")
        physical = result.get("physical_output")
        if len(actions) == 1:
            source = actions[0].get("source")
            physical = actions[0].get("physical", actions[0].get("physical_output"))
        if source in ("P", "Q") and physical:
            output["text"] = "La acción física actual se dirige a la fuente " + source + ". No se atribuye una necesidad introspectiva ni utilidad general."
        else:
            output.update(attribution="INSTRUMENTO", text="No hay una acción actual única de fuente en esta lectura; no se consulta el historial para sustituirla.")
    elif operation == "observe":
        output.update(attribution="INSTRUMENTO", text="Lectura pasiva actual: no avanza el mundo ni atribuye percepción al ente.")
    elif operation == "experience":
        output.update(attribution="INSTRUMENTO", text="Solicitud de experiencia física realizada. Scheduled no equivale a Applied; se conservan los recibos reales.")
    elif operation in ("train", "train_all"):
        output.update(attribution="INSTRUMENTO", text="Protocolo físico de enseñanza ejecutado en la misma organización. El par de entradas no es una tabla de respuestas escrita por Python.")
    elif operation in ("query", "query_named"):
        output["text"] = "Respuesta física a la consulta nueva. Se muestran las etapas y sus lecturas; no se consulta una tabla de resultados."
    elif operation == "query_sequence":
        output.update(attribution="INSTRUMENTO", text="Panel de respuestas físicas capturadas durante el protocolo nativo recién ejecutado sobre MAIN. Las consultas pueden transformar la relación; las capturas no son una tabla de respuestas del entrenamiento.")
    elif operation == "information":
        if result.get("information"):
            output["text"] = "Productos informativos presentes en esta lectura; los nombres humanos son traducción externa del contrato."
        else:
            output.update(attribution="INSTRUMENTO", text="Esta lectura no contiene un producto informativo disponible; no se sustituye por el dato privado del entorno.")
    else:
        output["text"] = "Medición actual de la operación nativa declarada."
    return output


class ConversationSession:
    """Text interface over one native MAIN. Restores validate before assignment."""
    METADATA_KEY = "dee.dialogue.es.v1"

    def __init__(self, profile="continuidad", *, directory="sesion", preparation=None):
        self.profile = profile
        self.directory = Path(directory)
        self.preparation = dict(preparation or {})
        self.session = None
        self.aliases = {}
        self.last_reference = None
        self.saved_path = None

    def _need(self):
        if self.session is None:
            raise ValueError("No hay una instancia; crea una o carga un snapshot explícito.")

    def _metadata(self):
        return {"schema": 1, "profile": self.profile, "aliases": self.aliases,
                "last_reference": self.last_reference,
                "scope": "External interface references only; no answers, policies or hidden truth"}

    def _persist_names(self):
        values = self.session.interface_metadata
        values[self.METADATA_KEY] = json.dumps(self._metadata(), ensure_ascii=False, separators=(",", ":"))
        self.session.set_interface_metadata(values)

    @staticmethod
    def _validate_metadata(data, profile):
        if data.get("schema") != 1 or data.get("profile") != profile:
            raise ValueError("El snapshot no corresponde al perfil textual elegido")
        aliases = data.get("aliases")
        if not isinstance(aliases, dict) or len(aliases) > 128:
            raise ValueError("Nombres de interfaz no válidos")
        for name, target in aliases.items():
            if not isinstance(name, str) or not 0 < len(name) <= 80 or not isinstance(target, dict):
                raise ValueError("Nombre de interfaz inválido")
            if set(target) != {"kind", "external_id"} or not all(isinstance(v, str) and len(v) <= 80 for v in target.values()):
                raise ValueError("Referencia de interfaz inválida")
        normalized_targets = {}
        for name, target in aliases.items():
            key = normalize(name)
            if not key or (key in normalized_targets and normalized_targets[key] != target):
                raise ValueError("Nombres normalizados ambiguos en el snapshot")
            normalized_targets[key] = target
        reference = data.get("last_reference")
        if reference is not None and (not isinstance(reference, dict) or set(reference) != {"kind", "external_id"}
                                      or not all(isinstance(v, str) and len(v) <= 80 for v in reference.values())):
            raise ValueError("Referencia actual inválida")
        return aliases, reference

    def execute(self, text):
        command = parse(text)
        op, argument = command.operation, command.argument
        if op == "help":
            return {"attribution": "INSTRUMENTO", "text": HELP}
        if op == "exit":
            return {"attribution": "INSTRUMENTO", "text": "Fin solicitado; no se reinició la organización.", "exit": True}
        if op == "new":
            if self.session is not None:
                return {"attribution": "INSTRUMENTO", "text": "MAIN ya existe; no se recrea ni se borra su experiencia."}
            self.session = create_session(self.profile, **self.preparation)
            self.last_reference = {"kind": "instance", "external_id": "MAIN"}
            self._persist_names()
            return {"attribution": "INSTRUMENTO", "text": "Preparación nueva explícita, perfil " + self.profile + ".", "measurement": self.session.observe()}
        if op == "load":
            path = Path(argument) if argument else self.saved_path or self.directory / "sesion.deetsnap"
            if argument and not path.is_absolute():
                path = self.directory / path
            restored = load_session(path, profile=self.profile)
            packed = restored.interface_metadata.get(self.METADATA_KEY)
            names, reference = self._validate_metadata(json.loads(packed), self.profile) if packed else ({}, None)
            # Only after full format/profile/metadata validation replace MAIN.
            self.session, self.aliases, self.last_reference = restored, names, reference
            self.saved_path = path
            return {"attribution": "INSTRUMENTO", "text": "Estado físico, protocolo y nombres restaurados; no se instaló otro cuerpo.", "measurement": restored.observe()}
        self._need()
        if op in ("name", "name_route"):
            reference_to_name = self.last_reference
            if op == "name_route":
                port, name = argument
                if self.profile != "relaciones":
                    raise ValueError("Las dos rutas nombrables pertenecen al perfil relaciones")
                reference_to_name = {"kind":"route", "external_id":str(port)}
            else:
                name = str(argument).strip()
            if not reference_to_name or not 0 < len(name) <= 80 or len(self.aliases) >= 128:
                raise ValueError("Hace falta un referente actual y un nombre de 1–80 caracteres, con presupuesto disponible")
            if not normalize(name):
                raise ValueError("El nombre queda vacío después de normalizar la gramática")
            if any(normalize(old) == normalize(name) and old != name and reference != reference_to_name
                   for old, reference in self.aliases.items()):
                raise ValueError("Ese nombre normalizado ya referencia otro componente; no se elige una ruta silenciosamente")
            self.last_reference = reference_to_name
            self.aliases[name] = dict(reference_to_name)
            self._persist_names()
            return {"attribution": "INSTRUMENTO", "text": "«" + name + "» es un nombre externo de interfaz; no una asociación funcional adquirida por DEE."}
        if op == "save":
            path = Path(argument) if argument else self.directory / "sesion.deetsnap"
            if argument and not path.is_absolute():
                path = self.directory / path
            self._persist_names()
            result = self.session.save_snapshot(path)
            self.saved_path = path
            return {"attribution": "INSTRUMENTO", "text": "Snapshot integral guardado; no necesita sidecar textual.", "snapshot": result}
        if op == "why":
            return {"attribution": "EXPLICACION_DOCUMENTAL", "text": (
                "La preparación declara fuentes, rutas y reglas de acceso. El kernel v27 ejecuta la evolución; "
                "el programa sólo traduce lecturas actuales. Esta explicación de contrato no prueba una causa "
                "necesaria ni es introspección. Los contrastes causales requieren un fork diagnóstico explícito."),
                "current_measurement": self.session.observe()}
        if op in ("arrival_order", "route_variant", "remove_mediator"):
            method = getattr(self.session.native, op, None)
            if method is None:
                return {"attribution": "INSTRUMENTO", "text": "El perfil actual no publica esa operación física/diagnóstica. No se deduce una respuesta de la configuración.", "status": "OPERATION_NOT_IMPLEMENTED_IN_PROFILE"}
            from .cognition import record
            return render(record(method()), op)
        if op == "experience":
            value = str(argument)
            target = next((v for k, v in self.aliases.items() if normalize(k) == normalize(value)), None)
            if target and target["kind"] == "sensor":
                value = target["external_id"]
            result = self.session.experience(value.upper())
            self.last_reference = {"kind": "sensor", "external_id": value.upper()}
        elif op == "train":
            signal, first_reference, second_reference = argument
            result = self.session.train([first_reference, second_reference], signal)
            self.last_reference = {"kind": "relation", "external_id": "two-physical-routes"}
        elif op == "train_all":
            result = self.session.train_all(argument)
            self.last_reference = {"kind": "relation", "external_id": "two-composed-physical-relations"}
        elif op == "query":
            result = self.session.query(argument)
            self.last_reference = {"kind": "query", "external_id": str(argument)}
        elif op == "query_named":
            name, value = argument
            target = next((v for k,v in self.aliases.items() if normalize(k)==normalize(name)), None)
            if not target or target["kind"] != "route" or target["external_id"] not in ("0","1"):
                raise ValueError("La forma no referencia una ruta registrada; no se inventa una asociación")
            result = self.session.query_port(int(target["external_id"]), value)
        elif op == "query_sequence":
            result = self.session.query_sequence(argument)
        elif op == "advance":
            result = self.session.advance(30 if argument is None else argument)
        elif op == "information":
            result = self.session.observe()
        else:
            result = getattr(self.session, op)()
            if op in ("sense", "observe"):
                self.last_reference = {"kind": "observation", "external_id": "current"}
        self._persist_names()
        output = render(result, op)
        if normalize(text) == "ocurrira lo mismo":
            output["interface_notice"] = "Esta frase solicita una nueva predicción de la variable declarada; no acredita comparar episodios arbitrarios."
        return output


__all__ = ["Command", "ConversationSession", "HELP", "normalize", "parse", "render"]
