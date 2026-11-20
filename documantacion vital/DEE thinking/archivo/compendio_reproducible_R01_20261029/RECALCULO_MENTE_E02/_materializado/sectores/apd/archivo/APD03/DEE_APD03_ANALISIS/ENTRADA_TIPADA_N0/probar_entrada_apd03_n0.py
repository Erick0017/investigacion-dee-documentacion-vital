"""Fixtures del supervisor y transporte. CERO ticks, motor o adquisición DEE.

No existe proceso propietario real: el backend Fake sólo confirma transporte.
Estos resultados nunca constituyen una prueba nativa ni de distribución Full.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("entry_under_N0_test", HERE / "usar_dee.py")
UI = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(UI)
CONFIG = {"control_wait_seconds": .1, "material_wait_seconds": .1, "stop_wait_seconds": .1}


class FakeBackend:
    """Sólo metadatos/recibos. Ninguna función matemática ni política simulada."""
    def __init__(self, root):
        self.root = Path(root)
        self.calls = []
        self.cards = {}
        self.rows = {}
        self.starts = 0
        self.imports = 0
        self.process = None
        self.mode = "completed"
        self.paused = True
        self.tick = 548407

    @property
    def protocol_home(self): return self.root / "trabajo_personal/entrada_sencilla/vidas"

    def record(self, life): return self.cards[life]

    def import_new(self, life):
        if life in self.cards: raise FileExistsError("fixture exists")
        self.imports += 1
        self.cards[life] = {"life_id": life, "world_id": "mock_world_"+life, "physical": {"tick": self.tick}}
        return {"record": self.cards[life], "selected": {"source_life": "APD02_MAIN", "snapshot_sha256": "mock_source_sha_NOT_NATIVE"}}

    def start(self, life, directory):
        if self.process is not None: raise RuntimeError("fixture duplicate owner")
        self.starts += 1
        self.process = object()
        self.paused = True
        return {"pid": -123, "job_name": "MOCK_NO_PROCESS", "started_paused": True}

    def finish_owned(self, timeout):
        self.process = None
        return {"owned_process": False, "MOCK": True}

    def manager(self, args, timeout=None):
        self.calls.append(list(args))
        command = args[0].removeprefix("mente-unificada-")
        if command == "estado": return {"observation": {"running": self.process is not None, "paused": self.paused, "tick": self.tick}}
        request_id = args[args.index("--id")+1]
        if command == "resultado": return {"request": self.rows.get(request_id), "reexecuted": False}
        if command == "pedir":
            payload = {"operacion": "sesion", "situaciones": json.loads(args[args.index("--situaciones")+1]), "retorno": args[args.index("--retorno")+1], "actuador": args[args.index("--actuador")+1]}
            row = {"id": request_id, "payload": UI.canonical(payload), "payload_sha": hashlib.sha256(UI.canonical(payload).encode()).hexdigest(), "status": self.mode}
            self.rows[request_id] = row
            if self.mode == "timeout":
                row["status"] = "processing"
                raise subprocess.TimeoutExpired(["MOCK"], timeout)
            if self.mode == "waiting":
                row["status"] = "queued"
                return {"id": request_id, "admission": "queued", "status": "waiting_or_processing"}
            if self.mode == "rejected": return {"admission": "rejected_queue_capacity", "native_input_submitted": False}
            return {"admission": "queued", "request": row}
        if command == "reanudar": self.paused = False
        if command == "pausar": self.paused = True
        return {"request": {"id": request_id, "status": "completed", "result": "{}"}}


class EntryN0(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dee-ui-n0-")
        self.root = Path(self.temp.name)
        self.backend = FakeBackend(self.root)
        self.ui = UI.Supervisor(self.root, "PERSONAL_N0", self.backend, CONFIG)

    def tearDown(self): self.temp.cleanup()

    def ready(self):
        self.ui.open(new=True)
        self.ui.start()

    def test_new_uses_explicit_complete_import_no_start(self):
        card = self.ui.open(new=True)
        self.assertEqual(self.backend.imports, 1)
        self.assertEqual(self.backend.starts, 0)
        self.assertEqual(card["physical"]["tick"], 548407)

    def test_reopen_preserves_world_no_import(self):
        self.ui.open(new=True)
        reopened = UI.Supervisor(self.root, "PERSONAL_N0", self.backend, CONFIG)
        card = reopened.open()
        self.assertEqual(card["world_id"], "mock_world_PERSONAL_N0")
        self.assertEqual(self.backend.imports, 1)

    def test_new_cannot_overwrite_protocol(self):
        self.ui.open(new=True)
        with self.assertRaises(FileExistsError): self.ui.open(new=True)

    def test_no_implicit_new_on_missing(self):
        with self.assertRaises(FileNotFoundError): self.ui.open()
        self.assertEqual(self.backend.imports, 0)

    def test_duplicate_owner_blocked(self):
        self.ready()
        with self.assertRaises(RuntimeError): self.ui.start()
        self.assertEqual(self.backend.starts, 1)

    def test_start_is_paused_and_resume_is_explicit(self):
        self.ready()
        self.assertTrue(self.backend.paused)
        self.ui.control("reanudar")
        self.assertFalse(self.backend.paused)

    def test_passive_state_sends_no_material(self):
        self.ready()
        result = self.ui.status()
        self.assertTrue(result["INSTRUMENTO"]["no_material_probe"])
        self.assertEqual([c[0] for c in self.backend.calls], ["mente-unificada-estado"])

    def test_literal_no_math_or_route_calculation(self):
        self.ready()
        payload = [{"modo": "apd02", "texto": "suma", "operandos": [18, 7]}]
        self.ui.material(payload)
        args = self.backend.calls[-1]
        self.assertEqual(json.loads(args[args.index("--situaciones")+1]), payload)
        self.assertNotIn("25", args)
        self.assertFalse(self.ui.state["pending_material"])

    def test_waiting_summary_not_complete_row(self):
        self.ready(); self.backend.mode = "waiting"
        result = self.ui.material([{"modo": "apd02", "texto": "suma", "operandos": [2, 3]}])
        self.assertEqual(result["status"], "waiting_or_processing")
        self.assertTrue(self.ui.state["pending_material"])
        with self.assertRaises(RuntimeError): self.ui.material([{"modo": "apd02", "texto": "suma", "operandos": [2, 3]}])
        self.assertEqual(sum(c[0] == "mente-unificada-pedir" for c in self.backend.calls), 1)

    def test_timeout_reopen_same_id_no_resubmit(self):
        self.ready(); self.backend.mode = "timeout"
        with self.assertRaises(subprocess.TimeoutExpired): self.ui.material([{"modo": "apd02", "texto": "suma", "operandos": [2, 3]}])
        saved_id = self.ui.state["pending_material"]["id"]
        reopened = UI.Supervisor(self.root, "PERSONAL_N0", self.backend, CONFIG)
        reopened.open()
        self.backend.rows[saved_id]["status"] = "completed"
        result = reopened.result()
        self.assertEqual(result["request"]["id"], saved_id)
        self.assertFalse(reopened.state["pending_material"])
        self.assertEqual(sum(c[0] == "mente-unificada-pedir" for c in self.backend.calls), 1)

    def test_missing_pending_row_is_not_requeued(self):
        self.ready(); self.backend.mode = "waiting"
        self.ui.material([{"modo": "apd02", "texto": "suma", "operandos": [2, 3]}])
        self.backend.rows.clear()
        result = self.ui.result()
        self.assertIsNone(result["request"])
        self.assertTrue(self.ui.state["pending_material"])
        self.assertEqual(sum(c[0] == "mente-unificada-pedir" for c in self.backend.calls), 1)

    def test_other_payload_same_id_is_rejected(self):
        self.ready(); self.backend.mode = "waiting"
        self.ui.material([{"modo": "apd02", "texto": "suma", "operandos": [2, 3]}])
        pending = self.ui.state["pending_material"]["id"]
        self.backend.rows[pending]["payload_sha"] = "OTHER"
        with self.assertRaises(ValueError): self.ui.result()
        self.assertTrue(self.ui.state["pending_material"])

    def test_uncertain_blocks_material_and_resume(self):
        self.ready(); self.backend.mode = "uncertain"
        self.ui.material([{"modo": "apd02", "texto": "suma", "operandos": [2, 3]}])
        self.assertTrue(self.ui.state["uncertain_preserved"])
        with self.assertRaises(RuntimeError): self.ui.control("reanudar")
        with self.assertRaises(RuntimeError): self.ui.material([{"modo": "apd02", "texto": "suma", "operandos": [4, 5]}])
        self.ui.control("guardar"); self.ui.control("detener")
        self.assertFalse(self.ui.owned)

    def test_definite_admission_reject_clears_only_transport_pending(self):
        self.ready(); self.backend.mode = "rejected"
        result = self.ui.material([{"modo": "apd02", "texto": "suma", "operandos": [2, 3]}])
        self.assertEqual(result["admission"], "rejected_queue_capacity")
        self.assertFalse(self.ui.state["pending_material"])

    def test_stop_uses_only_own_owner_and_reopen(self):
        self.ready(); self.ui.control("guardar"); self.ui.control("detener")
        self.assertFalse(self.ui.owned)
        reopened = UI.Supervisor(self.root, "PERSONAL_N0", self.backend, CONFIG)
        reopened.open(); reopened.start()
        self.assertEqual(self.backend.starts, 2)
        self.assertEqual(self.backend.imports, 1)

    def test_context_and_teacher_are_literal_operator_inputs(self):
        parser = UI.command_parser()
        language = UI.literal_rows(parser.parse_args(["lenguaje", "recuerda", "21", "beta"]))
        teaching = UI.literal_rows(parser.parse_args(["ensenar", "compara", "-1", "--revision"]))
        self.assertEqual(language, [{"modo": "apd02-lenguaje", "texto": "recuerda", "valor": 21, "contexto": "beta"}])
        self.assertEqual(teaching, [{"modo": "apd02-docencia", "texto": "compara", "senal": -1, "revision": True}])

    def test_composition_is_user_order_not_plan(self):
        options = UI.command_parser().parse_args(["componer", "agrega", "resta", "--datos", "4", "8", "3"])
        self.assertEqual(UI.literal_rows(options), [{"modo": "apd02-componer", "formas": ["agrega", "resta"], "datos": [4, 8, 3]}])

    def test_event_json_not_inferred_or_filtered(self):
        path = self.root / "user_event.json"
        value = [{"modo": "apd03-literal-new-protocol", "hecho": 2}]
        path.write_text(json.dumps(value), encoding="utf8")
        options = UI.command_parser().parse_args(["evento", str(path)])
        self.assertEqual(UI.literal_rows(options), value)

    def test_identity_protects_paths_and_devices(self):
        for value in ("../E1", "NUL", "CON.txt", "a.", "a/b", ""):
            with self.assertRaises(ValueError, msg=value): UI.identifier(value)

    def test_single_supervisor_lock(self):
        path = self.root / "entry.lock"
        with UI.SessionLock(path):
            with self.assertRaises(RuntimeError):
                with UI.SessionLock(path): pass
        with UI.SessionLock(path): pass

    def test_candidate_configuration_cannot_launch(self):
        with self.assertRaises(ValueError): UI.DistributionBackend(self.root, {"status": "CANDIDATE_NOT_NATIVE_TESTED"})

    def test_world_mismatch_not_repaired(self):
        self.ui.open(new=True)
        self.backend.cards["PERSONAL_N0"]["world_id"] = "OTHER_WORLD"
        with self.assertRaises(ValueError): self.ui.open()
        self.assertEqual(self.backend.imports, 1)

    def test_no_native_imports_in_wrapper(self):
        tree = ast.parse((HERE / "usar_dee.py").read_text(encoding="utf8"))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): imports += [n.name for n in node.names]
            if isinstance(node, ast.ImportFrom): imports.append(node.module or "")
        self.assertFalse(any(n.split(".")[0] in {"dee_thinking", "numpy", "app", "capacidades"} for n in imports))

    def test_root_resolution_from_existing_system_app(self):
        app = self.root / "sistema/app"
        app.mkdir(parents=True)
        (self.root / "sistema/gestionar.py").write_text("# MOCK path only", encoding="utf8")
        self.assertEqual(UI.default_root(app / "usar_dee.py"), self.root)

    def test_root_resolution_from_distribution_actualizaciones(self):
        folder = self.root / "actualizaciones"
        folder.mkdir()
        (folder / "arrancar.py").write_text("# MOCK path only", encoding="utf8")
        self.assertEqual(UI.default_root(folder / "usar_dee.py"), self.root)

    def test_one_contract_path_in_both_layouts(self):
        expected = self.root / "sistema/contratos/ENTRADA_SENCILLA_APD03.json"
        self.assertEqual(UI.selected_config_path(self.root), expected)
        (self.root / "actualizaciones").mkdir()
        (self.root / "actualizaciones/arrancar.py").write_text("# MOCK", encoding="utf8")
        self.assertEqual(UI.selected_config_path(self.root), expected)

    def test_both_managers_use_interpreter_directory_not_root(self):
        for cls in (UI.DistributionBackend, UI.OriginalBackend):
            backend = cls.__new__(cls)
            backend.root = self.root / ("long_original_root_" * 14)
            backend.python = self.root / "short_runtime/python.exe"
            backend.launcher = backend.root / ("actualizaciones/arrancar.py" if cls is UI.DistributionBackend else "sistema/gestionar.py")
            with patch.object(UI.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout='{"MOCK":true}', stderr="")) as run:
                result = backend.manager(["mente-unificada-estado", "--vida", "PERSONAL_N0"])
            self.assertTrue(result["MOCK"])
            self.assertEqual(run.call_args.kwargs["cwd"], backend.python.parent)
            self.assertTrue(Path(run.call_args.args[0][0]).is_absolute())
            self.assertTrue(Path(run.call_args.args[0][5]).is_absolute())

    def test_owned_job_uses_short_cwd_in_both_layouts(self):
        for cls in (UI.DistributionBackend, UI.OriginalBackend):
            backend = cls.__new__(cls)
            backend.root = self.root / ("long_root_" * 14)
            backend.python = self.root / "short_runtime/python.exe"
            backend.launcher = backend.root / ("actualizaciones/arrancar.py" if cls is UI.DistributionBackend else "sistema/gestionar.py")
            backend.config = {"idle_interval_seconds": .1, "owner_max_seconds": 120, "start_wait_seconds": 1, "memory_limit_bytes": 536870912}
            backend.process = backend.job = backend.pc = None
            backend.streams = []
            states = iter([{"observation": {"running": False}}, {"observation": {"running": True, "wall_utc": UI.now()}}])
            # El segundo timestamp debe generarse después del comienzo, no antes.
            def manager(_):
                first = next(states)
                if first["observation"]["running"]: first["observation"]["wall_utc"] = UI.now()
                return first
            pc = SimpleNamespace(spawn_owned=lambda *a, **k: None)
            with patch.object(UI, "load_module", return_value=pc), patch.object(backend, "manager", side_effect=manager), patch.object(pc, "spawn_owned", return_value=(SimpleNamespace(pid=-123, poll=lambda: None), "MOCK_JOB", "MOCK_NO_PROCESS")) as spawn:
                result = backend.start("PERSONAL_N0", self.root / cls.__name__)
            self.assertEqual(spawn.call_args.kwargs["cwd"], backend.python.parent)
            self.assertEqual(result["job_name"], "MOCK_NO_PROCESS")
            for stream in backend.streams: stream.close()

    def test_APD03_admission_is_explicit_P0_literal(self):
        parser=UI.command_parser()
        self.assertEqual(UI.literal_rows(parser.parse_args(["admitir-apd03"])),[{"modo":"apd03-admitir","consecuencia":"local_useful"}])
        self.assertEqual(UI.literal_rows(parser.parse_args(["admitir-apd03","--consecuencia","file_only"])),[{"modo":"apd03-admitir","consecuencia":"file_only"}])

    def test_new_finite_form_teaching_is_operator_input_not_dictionary_answer(self):
        parser=UI.command_parser()
        for token in("luma","nara"):
            for sign in(-1,1):
                actual=UI.literal_rows(parser.parse_args(["ensenar-nueva",token,str(sign),"--revision"]))
                self.assertEqual(actual,[{"modo":"apd03-docencia","texto":token,"senal":sign,"revision":True}])

    def test_new_language_carries_datum_and_explicit_context_no_result(self):
        actual=UI.literal_rows(UI.command_parser().parse_args(["lenguaje-nuevo","nara","23","gamma"]))
        self.assertEqual(actual,[{"modo":"apd03-lenguaje","texto":"nara","valor":23,"contexto":"gamma"}])
        self.assertNotIn("answer",actual[0]); self.assertNotIn("ruta",actual[0])

    def test_contextual_objective_has_no_next_action_list(self):
        parser=UI.command_parser()
        full=UI.literal_rows(parser.parse_args(["objetivo","diferencia","19","6"]))
        hidden=UI.literal_rows(parser.parse_args(["objetivo","diferencia","19","6","--oculto","--contexto-ambiente","1"]))
        self.assertEqual(full,[{"modo":"apd03-tarea-iniciar","texto":"diferencia","operandos":[19,6],"segundo_visible":True,"contexto_ambiente":0}])
        self.assertEqual(hidden,[{"modo":"apd03-tarea-iniciar","texto":"diferencia","operandos":[19,6],"segundo_visible":False,"contexto_ambiente":1}])
        self.assertFalse(any(k in hidden[0]for k in("acciones","ruta","plan","respuesta")))

    def test_contextual_steps_are_opportunities_not_selected_actions(self):
        parser=UI.command_parser()
        for count in(1,2,3,4):
            self.assertEqual(UI.literal_rows(parser.parse_args(["paso",str(count)])),[{"modo":"apd03-paso","oportunidades":count}])

    def test_panel_is_material_and_estado_stays_passive(self):
        self.ready()
        response=UI.execute(self.ui,["panel","--nuevas","--memorias","--retorno","omit"])
        payload=json.loads(self.backend.calls[-1][self.backend.calls[-1].index("--situaciones")+1])
        self.assertEqual(payload,[{"modo":"apd03-panel","nuevas":True,"memorias":True}])
        UI.execute(self.ui,["estado"])
        self.assertEqual(self.backend.calls[-1][0],"mente-unificada-estado")
        self.assertEqual(sum(c[0]=="mente-unificada-pedir"for c in self.backend.calls),1)

    def test_old_meta_stays_APD02_not_silently_retargeted(self):
        parser=UI.command_parser()
        self.assertEqual(UI.literal_rows(parser.parse_args(["meta","suma","16","5","--oculto"])),[{"modo":"apd02-meta-iniciar","texto":"suma","operandos":[16,5],"segundo_visible":False}])
        self.assertEqual(UI.literal_rows(parser.parse_args(["meta-paso","2"])),[{"modo":"apd02-meta-paso","oportunidades":2}])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", type=Path, required=True)
    options = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(EntryN0)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"schema": "APD03.single_entry.N0_fixtures.v1", "test_kind": "MOCK_TRANSPORT_NOT_NATIVE_OR_DISTRIBUTION", "new_native_ticks": 0,
              "native_processes_created": 0, "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
              "source": {p.name: {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in (HERE/"usar_dee.py", Path(__file__))},
              "limitations": ["No prueba la evolución física, capacidad cognitiva, importación nativa o continuidad de Full.", "La reserva nativa y la extracción exacta requieren autorización y prueba separadas."]}
    options.salida.parent.mkdir(parents=True, exist_ok=True)
    options.salida.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf8")
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__": main()
