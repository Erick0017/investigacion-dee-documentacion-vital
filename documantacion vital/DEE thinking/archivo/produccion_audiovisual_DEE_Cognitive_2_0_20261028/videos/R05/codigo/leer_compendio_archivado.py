"""Read-only logical access to the existing R01 archive; never executes DEE."""
from pathlib import Path
import base64
import gzip
import hashlib
import io
import json
import zipfile

THINKING = Path(__file__).resolve().parents[5]
ARCHIVE = THINKING / 'CPC - Experimentos y mecanismos/DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip'

class ArchivedCompendium:
    def __init__(self):
        self.archive = zipfile.ZipFile(ARCHIVE)
        self.prefix = 'DEE_COMPENDIO_REPRODUCIBLE/'
        self.catalog = json.loads(self.archive.read(self.prefix + 'CATALOGO.json'))
        self.files = {x['path']: x for x in self.catalog['files']}
        self.index = json.loads(self.read('sectores/core/documentacion/INDICE_MIEMBROS.json'))['paths']

    def read(self, name):
        if name not in self.files:
            matches = [k for k in self.files if k.endswith('/' + name)]
            if len(matches) != 1:
                raise KeyError((name, matches))
            name = matches[0]
        f = self.files[name]
        data = self.archive.read(self.prefix + f['storage'])
        if f.get('compression') == 'gzip':
            data = gzip.decompress(data)
        assert hashlib.sha256(data).hexdigest() == f['sha256'], name
        return data

    def json(self, name):
        data = self.read(name)
        return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)

    def mechanism(self, identifier):
        return next(x for x in self.catalog['mechanisms'] if x['id'] == identifier)

    def recovered(self, paths):
        selected = {self.index[p]['sha256']: p for p in paths}
        source = self.read('sectores/core/mecanismos/RECUPERACION_POR_HASH.jsonl.gz')
        found = {}
        with gzip.GzipFile(fileobj=io.BytesIO(source)) as stream:
            for line in stream:
                entry = json.loads(line)
                if entry['sha256'] in selected:
                    data = base64.b64decode(entry['base64'])
                    assert hashlib.sha256(data).hexdigest() == entry['sha256']
                    found[selected[entry['sha256']]] = data
        assert set(found) == set(paths), set(paths) - set(found)
        return found
