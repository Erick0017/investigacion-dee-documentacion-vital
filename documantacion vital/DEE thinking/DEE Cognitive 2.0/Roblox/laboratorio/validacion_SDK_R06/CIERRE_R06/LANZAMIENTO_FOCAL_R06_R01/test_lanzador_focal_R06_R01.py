"""Launcher tests: CLI help, fake FS diagnostics and rejection only; no Native."""
from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,sys,tempfile,unittest
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
RUNTIME=HERE.parents[2]/'RUNTIME_PRIVADO_LOCAL'
spec=importlib.util.spec_from_file_location('focal_external_launcher',RUNTIME/'backend/lanzar_focal_R06_R01.py')
w=importlib.util.module_from_spec(spec);sys.modules[spec.name]=w;spec.loader.exec_module(w)

class LauncherFixtures(unittest.TestCase):
    def test_all_five_cli_help_resolve_under_isolated_path(self):
        before=set(sys.modules)
        for command in w.COMMANDS:
            with self.subTest(command=command),contextlib.redirect_stdout(io.StringIO()):
                try:w.launch(command,['--help'])
                except SystemExit as e:self.assertEqual(e.code,0)
        self.assertNotIn('dee_thinking',set(sys.modules)-before)
        self.assertNotIn('_native',set(sys.modules)-before)
    def test_diagnostic_reads_no_window_or_registry_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'configuracion').mkdir();(root/'estado_demo').mkdir()
            (root/'configuracion/VENTANA_FOCAL_R06.json').write_text('SYNTHETIC_NON_JSON_DO_NOT_READ')
            (root/'estado_demo/PARTICIPANTES_FOCAL_R06.json').write_text('SYNTHETIC_NON_JSON_DO_NOT_READ')
            with patch.object(w,'checked_sources',return_value=root):
                result=w.diagnose(root)
            self.assertTrue(result['focalWindowExists']);self.assertTrue(result['focalParticipantRegistryExists'])
            self.assertEqual(result['instruction'],'DO_NOT_RESEAL_USE_EXISTING_WINDOW')
            self.assertFalse(result['stateOrSQLiteRead']);self.assertFalse(result['windowWritten'])
    def test_existing_window_rejected_before_runpy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'configuracion').mkdir();p=root/'configuracion/VENTANA_FOCAL_R06.json'
            p.write_text('SYNTHETIC_KEEP')
            with patch.object(w,'checked_sources',return_value=root),patch.object(w.runpy,'run_path') as run:
                with self.assertRaises(FileExistsError):w.launch('seal',['--execute-fs-only'],runtime=root)
                run.assert_not_called()
            self.assertEqual(p.read_text(),'SYNTHETIC_KEEP')
    def test_nonallowlisted_command_never_touches_sources(self):
        with patch.object(w,'checked_sources') as check:
            with self.assertRaises(ValueError):w.launch('../not_allowed.py',[])
            check.assert_not_called()
    def test_wrong_freeze_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);f=root/'backend/focal_r06';f.mkdir(parents=True)
            (f/'FUENTES_FOCAL_R06.json').write_text('{"SYNTHETIC":true}')
            with self.assertRaises(ValueError):w.checked_sources(root)
if __name__=='__main__':unittest.main(verbosity=2)
