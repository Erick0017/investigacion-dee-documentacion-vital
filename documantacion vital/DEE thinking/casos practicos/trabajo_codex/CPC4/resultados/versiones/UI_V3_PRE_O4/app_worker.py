"""Persistent Native MAIN for the finite CPC4 demonstration.

One process owns one Runtime. Preparing, experience, passive observation and
physical query are distinct operations. No expected-answer files are read.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import random
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import channel
from src.common import identity, sha
from src.language import InterfaceAliases
from src.phase_language import FORMS, KEY as LEXICAL_KEY, metadata, teach_slot, query_word, late_lexical_cut

APP_KEY = "cpc4.demonstration.neutral.v1"
STAGES = {"CREATED": 0, "AFTER_NATIVE_CONSEQUENCES": 169,
          "FIRST_WORD_EXPERIENCE": 172, "WORDS_EXPERIENCED": 200,
          "FIRST_WORD_QUERY": 239, "FINITE_COMPLETE": 267}
FIELDS = {"version", "translation", "stage", "word_order", "aliases"}
_SIGNAL_ONLY = False
_READ_ATTEMPTS = []


def audit(event, args):
    if not _SIGNAL_ONLY or event != "open":
        return
    path = args[0]
    mode = args[1] if len(args) > 1 else None
    flags = args[2] if len(args) > 2 else 0
    reading = (isinstance(mode, str) and "r" in mode) or (mode is None and isinstance(flags, int) and not flags & (os.O_WRONLY | os.O_RDWR))
    if not reading or not isinstance(path, (str, bytes, os.PathLike)):
        return
    text = str(path).replace("\\", "/").casefold()
    _READ_ATTEMPTS.append(text)
    if any(x in text for x in ("/resultados/", "/experimentos/", "/staging/", "measurements.json", ".jsonl", "cpc3", "sem01")):
        raise PermissionError("Signal-only query cannot read generator/results/history files")


sys.addaudithook(audit)


def point(value):
    return (value.x, value.y, value.z)


def direction(value):
    return (value.dx, value.dy, value.dz)


def validate(world, value):
    """Check a loaded operative state without creating/preparing another world."""
    if not isinstance(value, dict) or set(value) != FIELDS or value["version"] != 1:
        raise ValueError("Metadatos de demostración incompatibles")
    shift = value["translation"]
    if not isinstance(shift, list) or len(shift) != 3 or any(type(x) is not int or not 0 <= x < channel.N for x in shift):
        raise ValueError("Traslación neutral inválida")
    stage, order = value["stage"], value["word_order"]
    if stage not in STAGES or world.runtime.current_tick != STAGES[stage]:
        raise ValueError("La fase declarada no coincide con el tick físico")
    expected_length = {"CREATED": 0, "AFTER_NATIVE_CONSEQUENCES": 0,
                       "FIRST_WORD_EXPERIENCE": 1, "WORDS_EXPERIENCED": 2,
                       "FIRST_WORD_QUERY": 2, "FINITE_COMPLETE": 2}[stage]
    if not isinstance(order, list) or len(order) != expected_length or len(set(order)) != len(order) or any(x not in FORMS for x in order):
        raise ValueError("Cronología neutral de palabras inválida")
    if not isinstance(value["aliases"], dict) or len(value["aliases"]) > 64:
        raise ValueError("Alias externos inválidos")
    aliases = InterfaceAliases(FORMS, value["aliases"])
    if aliases.as_dict() != value["aliases"] or aliases.resolve("HAY") != "W1" or aliases.resolve("NO") != "W2":
        raise ValueError("Formas externas no normalizadas o reasignadas")
    recipe = world.recipe
    if world.runtime.dimension != 67 or recipe.dimension != 67 or recipe.t0_tick != 0 or recipe.placements:
        raise ValueError("Preparación Research finita distinta")
    expected = {x.name: x for x in channel.dual_interfaces(tuple(shift), receiver_basis="z")}
    actual = {x.name: x for x in world.interfaces}
    if len(actual) != len(world.interfaces) or set(actual) != set(expected) or set(world.runtime.channel_names) != set(actual):
        raise ValueError("Canales/contratos físicos no corresponden a la preparación")
    for name, item in actual.items():
        left, right = item.channel, expected[name].channel
        if (left.name, point(left.injection_site), direction(left.direction), left.state, left.semantic,
            left.allow_experience, left.allow_probe) != (right.name, point(right.injection_site), direction(right.direction), right.state, right.semantic,
                                                      right.allow_experience, right.allow_probe):
            raise ValueError("Geometría/admisión de interfaz modificada: " + name)
    if any(str(r.status) == "scheduled" for r in world.runtime.receipts):
        raise ValueError("La fase quiescente contiene entradas externas pendientes; no es una consulta de señal sola")
    return channel.describe_dual(tuple(shift), receiver_basis="z"), aliases


class Application:
    def __init__(self, output):
        import dee_thinking as d
        self.d = d
        wheels = list((ROOT / "runtime").glob("dee_thinking-4.0.0-*.whl"))
        if len(wheels) != 1:
            raise RuntimeError("Se requiere exactamente el WHL4 oficial incluido en runtime")
        self.identity = identity(wheels[0])
        self.output = Path(output)
        self.output.mkdir(parents=True, exist_ok=True)
        self.world = None
        self.spec = None
        self.neutral = None
        self.aliases = None

    def commit(self):
        self.neutral["aliases"] = self.aliases.as_dict()
        self.world.runtime.set_snapshot_metadata(APP_KEY, json.dumps(self.neutral, separators=(",", ":")))

    def require(self):
        if self.world is None:
            raise ValueError("No hay MAIN: usa crear o cargar")

    def create(self, seed=None):
        if self.world is not None:
            raise ValueError("Ya existe MAIN; crear no reinicia silenciosamente la sesión")
        # Seed changes only a common toroidal translation. It NEVER selects
        # a history, class, teacher, decoder or predicted answer.
        shift = (0, 0, 0) if seed is None else tuple(random.Random(int(seed) + axis).randrange(channel.N) for axis in range(3))
        self.world, self.spec = channel.prepare_dual(self.d, shift, receiver_basis="z")
        self.aliases = InterfaceAliases(FORMS, {"hay": "W1", "no": "W2"})
        self.neutral = {"version": 1, "translation": list(shift), "stage": "CREATED", "word_order": [], "aliases": self.aliases.as_dict()}
        self.commit()
        validate(self.world, self.neutral)
        return {"attribution": "INTERFAZ", "status": "NUEVA_PREPARACION_T0", "tick": 0, "translation": list(shift),
                "scope": "Dos organizaciones finitas en un Runtime: A y B distribuida; no dos cuerpos basales plenamente renovables. La semilla sólo traslada la geometría."}

    def live(self, a, policy, context):
        self.require()
        if self.neutral["stage"] != "CREATED":
            raise ValueError("El episodio corporal se recibe una sola vez desde T0")
        signs = {"+": 1, "-": -1}
        policies = {"coherente": 1, "invertida": -1}
        if a not in signs or context not in signs or policy not in policies:
            raise ValueError("Usa vivir +/- coherente|invertida +/-; son condiciones explícitas de experiencia, no respuestas")
        from src.channel_dual import run_native
        case = {"A_history": signs[a], "B_policy": policies[policy], "future_context": signs[context]}
        self.world, evidence = run_native(self.world, self.spec, case, self.output / "EPISODIO_NATIVO")
        del case
        self.neutral["stage"] = "AFTER_NATIVE_CONSEQUENCES"
        self.commit()
        return {"attribution": "INSTRUMENTO", "status": "MISMO_MAIN_TRAS_EXPERIENCIA_Y_COMUNICACION", "tick": 169,
                "A_emission": evidence["A_emission"], "B_responses": evidence["B_common_responses"],
                "actual_bank_captures": evidence["bank_captures"],
                "scope": "Experiencias por interfaces declaradas, mensaje A→B y consecuencias nativas. El contexto ambiental fue una condición externa declarada; no se leyó la acción para escoger el acontecimiento."}

    def teach(self, text):
        self.require()
        if self.neutral["stage"] not in ("AFTER_NATIVE_CONSEQUENCES", "FIRST_WORD_EXPERIENCE"):
            raise ValueError("Hay exactamente dos experiencias léxicas después del episodio corporal")
        form = self.aliases.resolve(text)
        order = self.neutral["word_order"]
        if form in order:
            raise ValueError("La segunda forma debe ser la otra interfaz; no se fabrica entrenamiento ilimitado")
        index = len(order)
        lesson = teach_slot(self.world, self.spec, self.output, form, ("plus", "minus")[index], (169, 197)[index])
        order.append(form)
        self.neutral["stage"] = "FIRST_WORD_EXPERIENCE" if index == 0 else "WORDS_EXPERIENCED"
        self.commit()
        return {"attribution": "GENERADOR_EXTERNO", "tick": self.world.runtime.current_tick,
                "lesson": lesson, "scope": "El sensor externo actual envía el MISMO report físico a ambas regiones; sólo la forma coincidente adquiere la relación. El resultado del sensor no se guarda como mapa en la sesión."}

    def query(self, text):
        global _SIGNAL_ONLY
        self.require()
        stage = self.neutral["stage"]
        if stage not in ("WORDS_EXPERIENCED", "FIRST_WORD_QUERY"):
            raise ValueError("Consulta fuera del dominio finito: dos experiencias y luego dos sondas, sin reinicio")
        index = 0 if stage == "WORDS_EXPERIENCED" else 1
        form = self.aliases.resolve(text)
        if form != self.neutral["word_order"][index]:
            raise ValueError("Esta preparación finita consulta en el orden de enseñanza; no se cambia una ruta para resolver otra pregunta")
        metadata(self.world, self.spec, self.neutral["word_order"], "APP_QUERYING", index)
        start = len(_READ_ATTEMPTS)
        _SIGNAL_ONLY = True
        try:
            response = query_word(self.world, self.spec, form, (236, 264)[index])
        finally:
            _SIGNAL_ONLY = False
        response["python_read_audit"] = {"observed_reads": _READ_ATTEMPTS[start:],
                                           "scope": "Python open audit, not OS sandbox or native fopen interceptor"}
        self.neutral["stage"] = "FIRST_WORD_QUERY" if index == 0 else "FINITE_COMPLETE"
        self.commit()
        return response

    def observe(self):
        self.require()
        return {"attribution": "INSTRUMENTO", "tick": self.world.runtime.current_tick,
                "stage": self.neutral["stage"], "digest": channel.digest(self.world),
                "current_physical_records": {name: channel.observe(self.world, site) for name, site in {**self.spec["centers"], **self.spec["lexical_hubs"]}.items()},
                "scope": "Observación pasiva actual; no nueva consulta ni respuesta recuperada de una transcripción."}

    def diagnose(self):
        """Explicit instrument operation, never a hidden operational fallback."""
        self.require()
        if self.neutral["stage"] != "FIRST_WORD_EXPERIENCE" or self.neutral["word_order"] != ["W1"]:
            raise ValueError("Diagnóstico publicado sólo enT172 después de enseñar HAY primero; MAIN no se adelanta ni repara")
        before = channel.digest(self.world)
        before_receipts = [channel.receipt(self.world, r.id) for r in self.world.runtime.receipts]
        before_metadata = self.world.runtime.snapshot_metadata(APP_KEY)
        values = []
        for mode in ("reference", "memory_cut", "sham"):
            folder = self.output/("DIAGNOSTICO_"+uuid.uuid4().hex)/mode
            folder.mkdir(parents=True)
            if mode == "reference":
                child, edit = self.world.fork(), None
            else:
                child, edit = late_lexical_cut(self.world, self.spec, mode)
            lesson = teach_slot(child, self.spec, folder, "W2", "minus", 197)
            responses = [query_word(child, self.spec, form, tick) for form,tick in (("W1",236),("W2",264))]
            path = folder/"CONTRAFACTUAL_FINAL267.deetsnap"
            child.save_snapshot(str(path))
            values.append({"mode": mode, "diagnostic_edit": edit,
                           "second_external_current_experience": lesson,
                           "panel": responses, "child_final": channel.digest(child),
                           "snapshot": str(path.resolve()), "snapshot_sha256": sha(path)})
            del child
        unchanged = (channel.digest(self.world) == before
                     and [channel.receipt(self.world,r.id) for r in self.world.runtime.receipts] == before_receipts
                     and self.world.runtime.snapshot_metadata(APP_KEY) == before_metadata)
        if not unchanged:
            raise RuntimeError("Diagnostic isolation invariant violated")
        return {"attribution": "INSTRUMENTO", "modality": "EXPLICIT_DIAGNOSTIC_FORKS",
                "parent_physical_before": before, "parent_physical_after": channel.digest(self.world),
                "parent_unchanged": unchanged, "counterfactuals": values,
                "scope": "Tres copias completas: referencia, corte localizado W1 y sham13. Sus sondas y consecuencias pertenecen al instrumento; ningún fork vuelve a MAIN y esto no es introspección ni reparación del ente."}

    def save(self, path):
        self.require()
        self.commit()
        validate(self.world, self.neutral)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise FileExistsError("No se sobrescribe una captura existente")
        temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
        self.world.save_snapshot(str(temporary))
        os.replace(temporary, path)
        return {"attribution": "INTERFAZ", "status": "SNAPSHOT_OPERATIVO_GUARDADO", "path": str(path.resolve()), "sha256": sha(path), "physical": channel.digest(self.world)}

    def load(self, path):
        # Validate the candidate first. A rejected load cannot replace MAIN.
        candidate = self.d.OrganizationalWorld.load_snapshot(str(path))
        raw = candidate.runtime.snapshot_metadata(APP_KEY)
        if raw is None or len(raw) > 65536:
            raise ValueError("Snapshot sin contrato de aplicación neutral compatible")
        neutral = json.loads(raw)
        spec, aliases = validate(candidate, neutral)
        self.world, self.spec, self.aliases, self.neutral = candidate, spec, aliases, neutral
        return {"attribution": "INTERFAZ", "status": "MISMO_ESTADO_OPERATIVO_RESTAURADO", "path": str(Path(path).resolve()),
                "sha256": sha(path), "physical": channel.digest(self.world), "stage": neutral["stage"],
                "scope": "No crea otro cuerpo ni reinstala materia/canales; restaura Runtime, cola, recibos, interfaces y metadatos neutrales."}

    def execute(self, request):
        op, args = request["operation"], request.get("arguments", [])
        if op == "create": return self.create(args[0] if args else None)
        if op == "live" and len(args) == 3: return self.live(*args)
        if op == "experience" and len(args) == 1: return self.teach(args[0])
        if op == "query" and len(args) == 1: return self.query(args[0])
        if op == "observe": return self.observe()
        if op == "diagnose": return self.diagnose()
        if op == "save" and len(args) == 1: return self.save(args[0])
        if op == "load" and len(args) == 1: return self.load(args[0])
        if op == "alias" and len(args) == 2:
            self.require(); self.aliases.add(args[0], args[1]); self.commit()
            return {"attribution": "INTERFAZ", "aliases": self.aliases.as_dict(), "scope": "Alias externos texto→ID; no asociación funcional escrita en DEE"}
        if op == "explain":
            return {"attribution": "EXPLICACION_DOCUMENTAL", "scope": "A y B adquieren relaciones por encuentros. La consecuencia actual pasa por un sensor externo fijo; la palabra coincide con un report idéntico en ambas regiones. La consulta física actual combina con el estado retenido; no es introspección ni semántica NSM universal."}
        raise ValueError("Operación fuera del protocolo físico publicado; ayuda distingue capacidades disponibles")


def main(output):
    app = Application(output)
    print(json.dumps({"ready": True, "identity": app.identity}), flush=True)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            if request.get("operation") == "exit":
                print(json.dumps({"ok": True, "result": {"attribution": "INTERFAZ", "status": "CERRADO"}}), flush=True)
                break
            result = app.execute(request)
            response = {"ok": True, "result": result}
        except Exception as error:
            response = {"ok": False, "error": type(error).__name__, "message": str(error)}
        print(json.dumps(response, ensure_ascii=False), flush=True)
