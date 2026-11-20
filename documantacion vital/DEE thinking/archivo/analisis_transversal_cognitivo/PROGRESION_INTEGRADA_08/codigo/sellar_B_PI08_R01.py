"""Root-only prospective B seal AFTER actual A adoption. Default read-only.

No Native import or C/system write. --sellar changes only these PI08 draft
protocol/seal files before B is admitted; the literal draft is preserved.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, os

P = Path(__file__).resolve().parents[1]
H = P/'codigo'
C = P.parents[2]/'DEE Cognitive 2.0'
A = 'ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
ROLES = ('real', 'none', 'yoked', 'reference')


def read(path): return json.loads(Path(path).read_text('utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(ok, message):
    if not ok: raise ValueError(message)


def bounded(path, roots):
    path = Path(path).resolve(strict=True)
    require(any(path.is_relative_to(root.resolve()) for root in roots), 'Path outside declared PI08/stable RP stores')
    for node in (path, *path.parents):
        require(not node.is_symlink() and not(getattr(node.lstat(), 'st_file_attributes', 0)&1024), 'No links/reparse points')
    return path


def main(args):
    adoption_path = P/'control/ADOPCION_PRODUCTO_PI08.json'
    adoption = read(adoption_path)
    require(adoption.get('phase') == 'COMMITTED' and adoption.get('life_id') == A, 'Actual A adoption is required before B')
    evaluation_path = P/'control/EVALUACION_CONSOLIDACION_A_PI08_R01.json'
    evaluation = read(evaluation_path)
    require(evaluation['all_fixed_evidence_gates_met'] and all(v['result'] for v in evaluation['gates'].values()), 'A evidence gates incomplete')
    active = read(C/'sistema/estado/ACTIVO.json'); card = read(C/'sistema/estado/vidas'/A/'VIDA.json')
    require(active['life_id'] == card['life_id'] == A and card['physical']['N'] == 67 and card['physical']['tick'] >= 860622, 'Protect the actual adopted A and its verified public-use continuation')
    pair = bounded(args.prefijo, [P, C/'reproducibilidad/materiales'])
    manifest_path = pair/'EXPORTACION_SERVICIO.json'; manifest = read(manifest_path)
    physical = {k: manifest['physical'][k] for k in ('N', 'tick', 'RAW_sha256', 'clocks_sha256')}
    require(manifest['life_id'] == A and manifest['physical']['tick'] == card['physical']['tick'], 'Exact complete current adopted-A prefix required')
    require(physical == {k: card['physical'][k] for k in physical}, 'Prefix physical state differs from actual adopted A')
    require(manifest['schema'] == 'DEE.persistent_service.paired_export.v1', 'Complete paired export required')
    require(sha(pair/manifest['native_snapshot']) == manifest['snapshot_sha256'], 'Prefix snapshot corrupted')
    seen = set(); total = 0
    for row in manifest['members']:
        rel = PurePosixPath(row['file'])
        require(not rel.is_absolute() and ':' not in row['file'] and '\\' not in row['file'] and all(v not in ('.', '..') for v in rel.parts), 'Unsafe paired member')
        require(row['file'] not in seen, 'Duplicate paired member')
        seen.add(row['file']); file = bounded(pair.joinpath(*rel.parts), [pair])
        require(file.is_file() and file.stat().st_size == row['bytes'] and sha(file) == row['sha256'], 'Incomplete paired member: '+row['file'])
        total += row['bytes']
    require({'VIDA.deetsnap.gz', 'cola.sqlite3'} <= seen and any(v.startswith('artefactos_trabajador/') for v in seen), 'RAW/clocks-only source cannot initialize B')
    protocol_file = H/'PROTOCOLO_PI08_B_R01.json'; draft = protocol_file.read_bytes(); p = json.loads(draft)
    require(p['status'] == 'DRAFT_PENDING_ACTUAL_A_ADOPTION', 'Preserve the existing B seal; no resealing after outcomes')
    source = {'alias': pair.name, 'path': str(pair), 'manifest_sha256': sha(manifest_path), 'snapshot_sha256': manifest['snapshot_sha256'],
              'life_id': A, 'N': 67, 'T': physical['tick'], 'physical': physical, 'members_verified': len(seen), 'bytes_verified': total}
    lives = {role: 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_'+role.upper()+'_01' for role in ROLES}
    p['status'] = 'SEALED_BEFORE_B_NATIVE'; p['source_A'] = source
    p['A_adoption_proof_sha256'] = sha(adoption_path)
    protocol_bytes = (json.dumps(p, ensure_ascii=False, indent=2)+'\n').encode('utf8')
    names = ['pi08_revision_flexible_B_R01.py', 'pi08_revision_flexible_B_episodio_R01.py']
    files = {name: sha(H/name) for name in names}
    originals = {'pi07_regulacion_R03.py': '40648fd81c5b1f278ee9c18d0d464c5a4b5e9fd808054afe6ff072a10fda0ac5',
                 'PROTOCOLO_PI07_R03.json': 'f69e8558799558a1ccceb70e0684a061a971b9521ad8985205d1662aea55d269', **p['dependencies_sha256']}
    for name, digest in originals.items():
        # Provenance check against the actual adopted product, not a temporary
        # campaign dependency. The hook installer will copy these literal files.
        require(sha(C/'sistema/capacidades'/name) == digest, 'Adopted inherited source differs: '+name)
    files.update(originals)
    seal = {'schema': 'DEE.PI08.B.after_A_adoption.seal.R01', 'sealed_utc': datetime.now(timezone.utc).isoformat(),
            'A_adopted': True, 'A_adoption_proof_sha256': sha(adoption_path), 'A_evidence_gates_sha256': sha(evaluation_path),
            'protocol_sha256': hashlib.sha256(protocol_bytes).hexdigest(), 'source_prefix': source,
            'research_life_ids': lives,
            'conservation_life_id': 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_CONSERVACION_01',
            'conservation_permissions': ['state', 'operational_dependencies', 'uncertain'],
            'conservation_START_and_B_EPISODE_forbidden': True,
            'additional_readonly_life_ids': ['ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01'],
            'C_readonly_permissions': ['state', 'operational_dependencies', 'uncertain'],
            'C_START_and_B_EPISODE_forbidden': True,
            'files_sha256': files, 'Native_executed_by_this_seal': False,
            'B_adoption_authorized': False, 'A_remains_protected_if_B_fails': True}
    if args.sellar:
        backup = P/'control/B_R01_BORRADOR_LITERAL_PRESELLADO.json'
        require(not backup.exists() and not (H/'SELLO_PI08_B_R01.json').exists(), 'Preserve prior seal/draft')
        with backup.open('xb') as out: out.write(draft)
        temporary = protocol_file.with_name(protocol_file.name+'.PI08_SEALING')
        with temporary.open('xb') as out: out.write(protocol_bytes); out.flush(); os.fsync(out.fileno())
        os.replace(temporary, protocol_file)
        with (H/'SELLO_PI08_B_R01.json').open('x', encoding='utf8') as out:
            json.dump(seal, out, ensure_ascii=False, indent=2); out.write('\n')
    print(json.dumps({'mode': 'SEALED_ROOT_ONLY' if args.sellar else 'READ_ONLY_READY_TO_SEAL',
          'Native_executed': False, 'source_prefix': source, 'research_life_ids': lives,
          'protocol_sha256': seal['protocol_sha256'], 'permutation': p['controls']['yoke_permutation'],
          'maximum_Native_ticks_four_arms': 93600}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prefijo', required=True, help='Actual complete paired export of current adopted A after its declared public verification')
    parser.add_argument('--sellar', action='store_true')
    main(parser.parse_args())
