"""Software-only fixtures. No Runtime, imported life, native tick or teaching."""
from pathlib import Path
import ast
import json
import threading
import unittest
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError
sys.path.insert(0, str(Path(__file__).resolve().parent))
import genesis
from visor_pasivo import make_frame


class Simple:
    def __init__(self, **kwargs): self.__dict__.update(kwargs)


class Tests(unittest.TestCase):
    def test_syntax(self):
        for path in Path(__file__).parent.glob('*.py'):
            ast.parse(path.read_text(encoding='utf8'))

    def test_exact_unsigned_frame(self):
        raw = [0] * 27
        raw[13] = (15 << 60) | (15 << 48) | (65535 << 32) | 4294967295
        clocks = [0] * 27
        clocks[13] = 18446744073709551615
        class Runtime:
            dimension, current_tick = 3, 9007199254740993
            def raw_copy(self): return list(raw)
            def clock_copy(self): return list(clocks)
        world = Simple(a=Simple(world=Simple(runtime=Runtime(), interfaces=[])), life='EXPLICIT_SOFTWARE_FIXTURE')
        q = Simple(outstanding=lambda: [], counters=lambda: {})
        frame, previous = make_frame(world, q)
        self.assertEqual(frame['tick'], '9007199254740993')
        self.assertEqual(frame['cells'][0]['clock'], '18446744073709551615')
        self.assertEqual(frame['cells'][0]['raw'], str(raw[13]))
        self.assertEqual(frame['cells'][0]['direction'], [-1, 0, 0])
        self.assertEqual(raw, previous[0])
        self.assertEqual(clocks, previous[1])
        self.assertEqual(frame['counts']['present_state_positive'], 1)
        self.assertEqual(frame['counts']['raw_nonzero'], 1)

    def test_json_no_rounding(self):
        v = genesis.exact_json({'x': 18446744073709551615, 'small': 17, 'rows': [9007199254740993]})
        self.assertEqual(v, {'x': '18446744073709551615', 'small': 17, 'rows': ['9007199254740993']})

    def test_literal_grammar_unknown_never_calls_actor(self):
        class Entry:
            def command_parser(self): raise AssertionError('Unknown must be stopped before parser/actor.')
        with self.assertRaises(LookupError): genesis.literal_command('usar secreto 4 5', Entry())
        with self.assertRaises(ValueError): genesis.literal_command('evento C:/secret.json', Entry())
        with self.assertRaises(ValueError): genesis.literal_command('   ', Entry())

    def test_local_http_and_csrf(self):
        calls = []
        class Fake:
            def status(self): return {'fixture': True, 'x': 18446744073709551615}
            def frame(self): return {'available': False, 'fixture': True}
            def submit(self, action, value): calls.append((action, value)); return {'fixture': True}
        server = genesis.LocalServer(('127.0.0.1', 0), genesis.handler(Fake(), 'TEST_TOKEN'))
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            url = 'http://127.0.0.1:' + str(server.server_port)
            self.assertEqual(json.load(urlopen(url + '/api/status'))['x'], '18446744073709551615')
            self.assertIn(b'G\xc3\x89NESIS', urlopen(url + '/').read())
            request = Request(url + '/api/action', data=b'{"action":"guardar"}', headers={'Content-Type': 'application/json'})
            with self.assertRaises(HTTPError) as blocked: urlopen(request)
            self.assertEqual(blocked.exception.code, 403)
            self.assertFalse(calls)
            request = Request(url + '/api/action', data=b'{"action":"guardar"}',
                headers={'Content-Type': 'application/json', 'X-Genesis-Token': 'TEST_TOKEN'})
            self.assertTrue(json.load(urlopen(request))['fixture'])
            self.assertEqual(calls, [('guardar', None)])
            request = Request(url + '/api/action', data=b'{"action":"guardar"}',
                headers={'Content-Type': 'application/json', 'X-Genesis-Token': 'TEST_TOKEN', 'Origin': 'http://evil.invalid'})
            with self.assertRaises(HTTPError) as blocked: urlopen(request)
            self.assertEqual(blocked.exception.code, 403)
            self.assertEqual(len(calls), 1)
        finally:
            server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__': unittest.main(verbosity=2)
