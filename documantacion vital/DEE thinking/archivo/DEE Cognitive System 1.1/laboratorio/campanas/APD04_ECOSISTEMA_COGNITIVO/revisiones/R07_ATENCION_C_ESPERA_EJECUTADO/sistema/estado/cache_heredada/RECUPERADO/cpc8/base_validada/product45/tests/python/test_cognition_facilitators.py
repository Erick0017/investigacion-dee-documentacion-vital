"""Public 4.0 facilitators: native operations and external Spanish interface."""
from array import array
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import dee_thinking as dee
from dee_thinking.cognition import create_session, load_session
from dee_thinking.dialogue import ConversationSession, parse, render


def digest(session):
    runtime = session.world.runtime
    return (runtime.current_tick, hashlib.sha256(array("Q", runtime.raw_copy()).tobytes()).hexdigest(),
            hashlib.sha256(array("Q", runtime.clock_copy()).tobytes()).hexdigest())


class CognitionFacilitators(unittest.TestCase):
    def test_real_version(self):
        self.assertEqual(dee.__version__, "4.5.0")
        self.assertEqual(dee.kernel_identity()["kernel_version"], 27)

    def test_grammar_is_not_open_language(self):
        self.assertEqual(parse("¿Qué pasará después?").operation, "predict")
        self.assertEqual(parse("Enseña dos relaciones 3,9 y 3,11").argument, [(3,9),(3,11)])
        self.assertEqual(parse("Guarda la sesión en sesión.deetsnap").argument, "sesión.deetsnap")
        for text in ("resuelve todo", "consulta -1", "avanza -1", "consulta 1.5"):
            with self.assertRaises(ValueError):
                parse(text)

    def test_alias_normalization_rejects_ambiguous_snapshot(self):
        value={"schema":1,"profile":"relaciones","aliases":{
            "Brisa":{"kind":"route","external_id":"0"},
            "brísa":{"kind":"route","external_id":"1"}},"last_reference":None}
        with self.assertRaises(ValueError):
            ConversationSession._validate_metadata(value,"relaciones")

    def test_native_association_and_fixed_decoder(self):
        s = create_session("relaciones")
        train = s.train([7,11], 5)
        self.assertEqual(s.tick, 6)
        self.assertTrue(all(r["status"] == "applied" for r in train["receipts"]))
        before = digest(s)
        s.observe(); s.observe()
        self.assertEqual(before, digest(s))
        result = s.query(13)
        self.assertEqual(result["decoded"], {"q0":25, "q1":29})
        self.assertEqual(s.tick, 11)

    def test_native_sequence_exports_actual_admission(self):
        s=create_session("relaciones");s.train([7,11],5)
        result=s.query_sequence([13,17,19])
        self.assertEqual(s.tick,21)
        self.assertEqual(len(result["steps"]),3)
        self.assertEqual([[o["s_reg"] for o in row["captured"]] for row in result["steps"]],
                         [[25,29],[42,46],[61,65]])
        self.assertTrue(all(receipt["status"]=="applied" for row in result["steps"] for receipt in row["receipts"]))
        self.assertTrue(all(len(row["receipts"])==2 for row in result["steps"]))

    def test_online_composition_and_native_operational_load(self):
        with tempfile.TemporaryDirectory(prefix="dee40-test-") as folder:
            s = create_session("composicion", depth=2)
            s.train_all([(3,9),(3,11)])
            s.set_interface_metadata({"test.external_name":"relación sin tabla de respuestas"})
            path = Path(folder)/"composition.deetsnap"
            s.save_snapshot(path)
            restored = load_session(path, profile="composicion")
            self.assertEqual(digest(s), digest(restored))
            self.assertEqual(s.interface_metadata, restored.interface_metadata)
            answer = restored.query(13)
            self.assertEqual(answer["decoded"], {"stage0":25, "stage1":39})
            with self.assertRaises(ValueError):
                load_session(path, profile="relaciones")

    def test_ui_alias_restores_without_sidecar_or_hidden_reset(self):
        with tempfile.TemporaryDirectory(prefix="dee40-ui-") as folder:
            ui = ConversationSession("continuidad", directory=folder)
            ui.execute("Instancia nueva")
            ui.execute("Presenta experiencia B")
            ui.execute("A esto lo llamaremos brisa")
            state = digest(ui.session)
            ui.execute("Instancia nueva")
            self.assertEqual(digest(ui.session), state)
            ui.execute("Guarda la sesión en sesión.deetsnap")
            path = Path(folder)/"sesión.deetsnap"
            self.assertTrue(path.exists())
            self.assertFalse(path.with_suffix(".deetsnap.ui.json").exists())
            other = ConversationSession("continuidad", directory=folder)
            other.execute("Carga sesión.deetsnap")
            self.assertEqual(ui.aliases, other.aliases)
            self.assertEqual(digest(ui.session), digest(other.session))
            self.assertEqual(other.execute("Por qué")["attribution"], "EXPLICACION_DOCUMENTAL")
            malformed = {"schema":1,"profile":"continuidad","aliases":{"x":{"answer":42}},"last_reference":None}
            other.session.native.set_interface_metadata(other.METADATA_KEY, json.dumps(malformed))
            other.session.save_snapshot(Path(folder)/"invalid_ui.deetsnap")
            prior = digest(ui.session)
            with self.assertRaises(ValueError):
                ui.execute("Carga invalid_ui.deetsnap")
            self.assertEqual(prior, digest(ui.session))

    def test_comparison_marker_is_not_a_fresh_prediction(self):
        ui = ConversationSession("comparacion")
        ui.execute("Instancia nueva"); ui.execute("Observa otra vez")
        forecast = ui.execute("¿Qué pasará después?")
        self.assertEqual(forecast["measurement"]["emission_tick"], 37)
        comparison = ui.execute("Compara esto con lo anterior")
        self.assertIn("discrepancia", comparison["text"])
        after = ui.execute("¿Qué pasará después?")
        self.assertEqual(after["attribution"], "INSTRUMENTO")
        self.assertEqual(after["measurement"]["status"], "OUTSIDE_FORECAST_DOMAIN")

    def test_policy_native_source_not_private_context(self):
        ui = ConversationSession("politica")
        ui.execute("Instancia nueva"); ui.execute("Observa otra vez")
        ui.execute("Compara esto con lo anterior")
        answer = ui.execute("¿Qué fuente necesitas observar?")
        self.assertIn("fuente Q", answer["text"])
        self.assertEqual(ui.session.tick, 11)
        prior = digest(ui.session)
        ui.execute("Muestra el estado")
        self.assertEqual(prior, digest(ui.session))


if __name__ == "__main__":
    unittest.main()
