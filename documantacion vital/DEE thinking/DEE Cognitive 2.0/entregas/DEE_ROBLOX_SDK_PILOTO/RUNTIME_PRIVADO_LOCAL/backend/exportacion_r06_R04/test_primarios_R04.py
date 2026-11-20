"""Pure relative primary locators: no Native, DB, sockets or operational files."""
from pathlib import Path
from copy import deepcopy
from types import SimpleNamespace
from unittest import mock
import ast
import hashlib
import importlib.util
import stat
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "exportar_capacidades_cerradas_R04.py"
OLD_SOURCE = HERE.parent / "exportacion_r06_R03/exportar_capacidades_cerradas_R03.py"


class PrimaryLocatorR04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("_pure_primary_locator_R04", SOURCE)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.source_pins = {path: hashlib.sha256(path.read_bytes()).hexdigest()
                           for path in (SOURCE, OLD_SOURCE)}

    @classmethod
    def tearDownClass(cls):
        for path, expected in cls.source_pins.items():
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise AssertionError("Exporter source changed during pure fixture")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="sdk_primary_r04_pure_")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.worker = self.base / "CURRENT_WORKER"
        self.folder = self.worker / "DEE_SDK_ASSISTED_CAPABILITIES_R06"
        self.folder.mkdir(parents=True)
        self.primary = self.folder / "ext_cap_01234567-89ab-cdef-0123-456789abcdef.json"
        self.primary.write_bytes(b'{"synthetic":true,"nativeValue":null}\n')

    def test_relative_windows_and_unix_locators_resolve_same_current_worker_file(self):
        relative = self.primary.relative_to(self.worker).as_posix()
        windows = relative.replace("/", "\\")
        expected = self.primary.resolve()
        self.assertEqual(self.module.primary_source(self.worker, relative), expected)
        self.assertEqual(self.module.primary_source(self.worker, windows), expected)
        self.assertEqual(self.module.raw(expected), self.primary.read_bytes())

    def test_absolute_drive_unc_traversal_and_ambiguous_components_are_rejected(self):
        for locator in (
            str(self.primary.resolve()), "C:\\outside\\primary.json", "C:primary.json",
            "\\\\server\\share\\primary.json", "/outside/primary.json",
            "../primary.json", "folder\\..\\primary.json", "folder/../primary.json",
            "./primary.json", "folder//primary.json", "folder\\\\primary.json",
            "folder/file.json:alternate", "",
        ):
            with self.subTest(locator=locator), self.assertRaises(ValueError):
                self.module.primary_source(self.worker, locator)

    def test_reparse_parent_is_rejected_without_creating_real_link(self):
        original = Path.lstat
        reparse = self.folder

        def fake_lstat(path, *args, **kwargs):
            if path == reparse:
                return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=1024)
            return original(path, *args, **kwargs)

        with mock.patch.object(Path, "lstat", new=fake_lstat), self.assertRaisesRegex(
                ValueError, "NO_LINK_OR_REPARSE"):
            self.module.primary_source(self.worker, self.primary.relative_to(self.worker).as_posix())

    def test_copy_preserves_other_mechanisms_locator_hash_check_and_portable_names(self):
        old = ast.parse(OLD_SOURCE.read_text("utf-8-sig"))
        new = ast.parse(SOURCE.read_text("utf-8-sig"))
        kinds = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        old_nodes = {node.name: node for node in old.body if isinstance(node, kinds)}
        new_nodes = {node.name: node for node in new.body if isinstance(node, kinds)}
        self.assertEqual(set(new_nodes), set(old_nodes) | {"primary_source"})

        class AllowedExportChanges(ast.NodeTransformer):
            def visit_Call(self, node):
                self.generic_visit(node)
                if (isinstance(node.func, ast.Name) and node.func.id == "contained"
                        and len(node.args) == 2 and isinstance(node.args[0], ast.Name)
                        and node.args[0].id == "worker"):
                    node.func.id = "primary_source"
                return node
            def visit_Constant(self, node):
                if isinstance(node.value, str):
                    node.value = node.value.replace(
                        "RECALCULAR_CAPACIDADES_R06_R03.py", "RECALCULAR_CAPACIDADES_R06_R04.py"
                    ).replace("Evidencia cerrada SDK/CAP R06 revision R03.",
                              "Evidencia cerrada SDK/CAP R06 revision R04.")
                return node

        for name, old_node in old_nodes.items():
            expected = deepcopy(old_node)
            if name == "export":
                expected = AllowedExportChanges().visit(expected)
            with self.subTest(mechanism=name):
                self.assertEqual(ast.dump(new_nodes[name], include_attributes=False),
                                 ast.dump(expected, include_attributes=False))
        export = new_nodes["export"]
        exact_hash_calls = [
            node for node in ast.walk(export)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "literal" and node.args
            and isinstance(node.args[0], ast.Name) and node.args[0].id == "primary"
            and any(keyword.arg == "expected" and isinstance(keyword.value, ast.Name)
                    and keyword.value.id == "locator" for keyword in node.keywords)
        ]
        self.assertEqual(len(exact_hash_calls), 1)
        self.assertEqual(self.module.SCHEMA, "DEE.Roblox.SDK.closed_capability_evidence.R06.R04")
        text = SOURCE.read_text("utf-8-sig")
        self.assertIn("RECALCULAR_CAPACIDADES_R06_R04.py", text)
        self.assertNotIn("RECALCULAR_CAPACIDADES_R06_R03.py", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)

