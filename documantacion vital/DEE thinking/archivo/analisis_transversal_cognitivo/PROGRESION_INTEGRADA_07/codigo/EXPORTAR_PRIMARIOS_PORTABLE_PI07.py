"""Copy explicitly selected published PI07 primaries/artifacts, no Native.

This creates one new portable evidence directory. It never opens SQLite,
snapshots or an engine, follows a recorded source path, or changes originals.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil

P7 = Path(__file__).resolve().parents[1]
PRODUCT = P7.parents[2] / 'DEE Cognitive 2.0'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def plain(path):
    path = Path(path).absolute()
    for node in (path, *path.parents):
        if node.exists() and (node.is_symlink() or getattr(node.lstat(), 'st_file_attributes', 0) & 1024):
            raise ValueError('No linked source or destination: ' + str(path))
    return path


def source_in_scope(path):
    path = plain(path).resolve(strict=True)
    if not (path.is_relative_to(P7.resolve())
            or path.is_relative_to((PRODUCT / 'reproducibilidad/diagnosticos').resolve())):
        raise ValueError('Explicit in-campaign or diagnostic RP evidence only')
    return path


def decode(primary):
    value = primary.get('result')
    if value is None:
        return []
    if isinstance(value, str):
        value = json.loads(value)
    if 'rows' not in value and isinstance(value.get('result'), dict):
        value = value['result']
    return value.get('rows', [])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--destino', type=Path, required=True)
    parser.add_argument('--sistema', type=Path, required=True)
    parser.add_argument('--primarios', type=Path, nargs='+', required=True)
    args = parser.parse_args()
    destination = plain(args.destino)
    if destination.exists():
        raise FileExistsError(destination)
    if not destination.parent.resolve(strict=True).is_relative_to(P7.resolve()):
        raise ValueError('Packaging destination must be a new directory under PI07')
    system = source_in_scope(args.sistema)
    if system.name != 'sistema':
        raise ValueError('Exact isolated diagnostic system directory required')
    if destination.is_relative_to(system):
        raise ValueError('Do not package inside a diagnostic operational system')
    primaries = [source_in_scope(path) for path in args.primarios]
    if len(set(primaries)) != len(primaries):
        raise ValueError('Duplicate primary source')
    material = []
    products = {}
    for source in primaries:
        data = source.read_bytes()
        doc = json.loads(data.decode('utf-8-sig'))
        rows = decode(doc)
        material.append((source, data))
        for row in rows:
            if isinstance(row.get('actual_effect'),dict)and row['actual_effect'].get('product')is not None:
                artifact=row['actual_effect']['product'];name=artifact['path']
                if not re.fullmatch(r'products/[0-9]{4}\.bin',name):
                    raise ValueError('Fixed bounded C2C product path only')
                envelope=doc.get('result',{})
                if isinstance(envelope,str):envelope=json.loads(envelope)
                life=envelope['committed_snapshot']['life_id']
                if not re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_[A-Za-z0-9_]{1,24}',life):
                    raise ValueError('Explicit C2C diagnostic owner only')
                origin=source_in_scope(system/'estado/servicios_locales'/life/'PI04_C2C_COORDINACION_R01/dispositivo'/name)
                content=origin.read_bytes()
                if len(content)!=64 or artifact['bytes']!=64 or sha(content)!=artifact['sha256']:
                    raise ValueError('Actual C2C product bytes/SHA differ')
                if int.from_bytes(content[:2],'little')!=row['actual_numeric_result']:
                    raise ValueError('C2C actual Native number did not reach real product')
                key=sha(content)
                products.setdefault(key,{'bytes':content,'sources':[]})['sources'].append(origin)
            message = row.get('message')
            if not message or message.get('artifact') is None:
                continue
            artifact = message['artifact']
            name = artifact['file']
            if not re.fullmatch(r'mensaje_[0-9]{4}\.bin', name):
                raise ValueError('Only a fixed bounded message artifact name is admitted')
            life = row.get('life_id')
            folder = ('PI07_REGULACION_ENV_R03'
                      if row.get('version') == 'DEE.PI07.acquired_regulation.perpendicular_environment.R03'
                      else 'PI07_REGULACION_R01'
                      if row.get('version') == 'DEE.PI07.physical_state_selective_regulation.R01'
                      else 'PI07_REGULACION_ENV_R02')
            if life is None:
                # R01 forced cases omit life_id; their explicit published ID
                # is bound to one of the four frozen diagnostic names only.
                match = re.fullmatch(r'PI07_VIAB_(THREAT_PULSE|THREAT_NONE|MSG_PULSE|MSG_NONE)_R01_EPISODIO\.json', source.name)
                if match is None:
                    raise ValueError('An R01 artifact lacks an exact diagnostic identity')
                life = 'ECI02_PI03_REPRO_PI04_PI05_PI07_VIAB_' + match.group(1)
                folder = 'PI07_REGULACION_R01'
            else:
                if not re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_[A-Za-z0-9_]{1,24}', life):
                    raise ValueError('Explicit diagnostic PI07 artifact owner required')
            origin = source_in_scope(system / 'estado/servicios_locales' / life / folder / name)
            content = origin.read_bytes()
            if len(content) != 64 or artifact['bytes'] != 64 or sha(content) != artifact['sha256']:
                raise ValueError('Native message artifact bytes/SHA mismatch')
            key = sha(content)
            if key not in products:
                products[key] = {'bytes': content, 'sources': []}
            products[key]['sources'].append(origin)
    destination.mkdir()
    home = destination / '04_EVIDENCIAS/PRIMARIOS'
    home.mkdir(parents=True)
    index = {'schema': 'DEE.PI07.portable_primary_index.v1', 'primaries': [], 'products': [],
             'new_Native_ticks': 0,
             'scope': 'Copies of explicitly selected published records and actual message bytes; not an executable world backup or a Native replay.'}
    preservation = []
    for number, (source, data) in enumerate(material):
        target = home / ('primary_%04d.json' % number)
        target.write_bytes(data)
        after = source.read_bytes()
        if after != data or target.read_bytes() != data:
            raise RuntimeError('Concurrent source change or copy mismatch; preserve partial export')
        index['primaries'].append({'file': target.relative_to(destination).as_posix(),
                                  'bytes': len(data), 'sha256': sha(data),
                                  'original_basename': source.name,
                                  'source_reference_for_packager_only': str(source)})
        preservation.append({'source': str(source), 'before_sha256': sha(data),
                             'after_sha256': sha(after), 'unchanged': True})
    for key, value in sorted(products.items()):
        target = home / ('product_' + key[:16] + '.bin')
        target.write_bytes(value['bytes'])
        for source in value['sources']:
            if source.read_bytes() != value['bytes']:
                raise RuntimeError('An original artifact changed during export')
        index['products'].append({'file': target.relative_to(destination).as_posix(),
                                 'bytes': 64, 'sha256': key,
                                 'source_reference_for_packager_only': str(value['sources'][0]),
                                 'source_aliases_same_bytes': [str(p) for p in value['sources'][1:]]})
    index_path = home / 'INDICE_PRIMARIOS_PI07.json'
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    proof = {'schema': 'DEE.PI07.portable_primary_export.v1',
             'destination': str(destination), 'primaries': len(material),
             'distinct_actual_message_contents': len(products),
             'original_sources_checked_before_after': preservation,
             'index_sha256': sha(index_path.read_bytes()), 'new_Native_ticks': 0,
             'not_an_experimental_reproduction': True}
    (destination / 'EXPORTACION_DOCUMENTAL.json').write_text(
        json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'destination': str(destination), 'primaries': len(material),
                      'products': len(products), 'index_sha256': proof['index_sha256']}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
