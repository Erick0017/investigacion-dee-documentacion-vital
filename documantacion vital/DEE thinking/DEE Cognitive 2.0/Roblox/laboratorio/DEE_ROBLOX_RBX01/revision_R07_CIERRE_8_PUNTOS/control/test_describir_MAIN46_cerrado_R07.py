"""Pure tempfile fixtures; never calls run() or reads Native roots."""
import hashlib
import importlib.util
from pathlib import Path
import stat
import sys
import tempfile
import types
import unittest

sys.dont_write_bytecode = True
SOURCE = Path(__file__).with_name('describir_MAIN46_cerrado_R07.py')
SPEC = importlib.util.spec_from_file_location('main46_descriptor_fixture', SOURCE)
descriptor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(descriptor)


class DescriptorFixtures(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='main46_descriptor_fixture_')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / 'source'
        self.root.mkdir()
        (self.root / 'nested').mkdir()
        (self.root / '.hidden').write_bytes(b'secret')
        (self.root / 'nested/a.bin').write_bytes(b'alpha')
        self.copies = self.base / 'copies'
        self.copies.mkdir()

    def test_stable_complete_hashes_and_shared_stream_copy(self):
        target = self.copies / 'a.blob'
        first = descriptor.inventory(self.root, True, {'nested/a.bin': target}, {'nested/a.bin': 5})
        second = descriptor.inventory(self.root, False)
        self.assertEqual(set(first['files']), {'.hidden', 'nested/a.bin'})
        self.assertEqual(first['directories'], second['directories'])
        for name, row in first['files'].items():
            self.assertEqual(row['stat'], second['files'][name]['stat'])
        self.assertEqual(first['files']['nested/a.bin']['sha256'], hashlib.sha256(b'alpha').hexdigest())
        self.assertEqual(target.read_bytes(), b'alpha')

    def test_oversize_critical_rejected_before_copy_creation(self):
        target = self.copies / 'overcap.blob'
        with self.assertRaises(ValueError):
            descriptor.inventory(self.root, True, {'nested/a.bin': target}, {'nested/a.bin': 4})
        self.assertFalse(target.exists())

    def test_second_sweep_detects_stat_and_path_set_changes(self):
        first = descriptor.inventory(self.root, True)
        (self.root / 'nested/a.bin').write_bytes(b'changed and longer')
        second = descriptor.inventory(self.root, False)
        self.assertNotEqual(first['files']['nested/a.bin']['stat'], second['files']['nested/a.bin']['stat'])
        (self.root / 'new').write_bytes(b'x')
        third = descriptor.inventory(self.root, False)
        self.assertNotEqual(set(first['files']), set(third['files']))

    def test_windows_reparse_attribute_rejected(self):
        fake = types.SimpleNamespace(st_mode=stat.S_IFREG, st_file_attributes=1024)
        with self.assertRaises(ValueError):
            descriptor.unlinked(fake)

    def test_symlink_rejected_when_creation_is_permitted(self):
        link = self.root / 'linked'
        try:
            link.symlink_to(self.root / 'nested/a.bin')
        except OSError as error:
            self.skipTest('Synthetic symlink creation unavailable: ' + str(error))
        with self.assertRaises(ValueError):
            descriptor.inventory(self.root, True)


if __name__ == '__main__':
    unittest.main()
