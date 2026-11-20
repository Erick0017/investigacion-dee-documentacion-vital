"""Prepare a two-file CAS proposal only. Never applies it or opens a world.

Root must reconcile the failed owner/job and prove the unadvanced C prefix
before applying these exact files to the isolated C system, under a fresh tag.
"""
from pathlib import Path
import ast, hashlib, json, shutil

P = Path(__file__).resolve().parents[1]
H = P / 'codigo'
S = P / 'estados/C_R03/sistema'
DEST = H / 'FIX_C_IDENTIDAD_TRANSPORTE_R01_PREPARADO'
WORLD = Path('app/mundo_genesis_apd05.py')
ADAPTER = Path('capacidades/pi08_identidad_B_readonly_C_R01.py')
B = Path('capacidades/pi08_revision_flexible_B_R01.py')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if DEST.exists():
        raise ValueError('Preserve prior proposal; no implicit overwrite/application')
    world = (S / WORLD).read_text('utf-8-sig')
    line = 'from capacidades import pi08_revision_flexible_B_R01 as pi08b'
    if world.count(line) != 5:
        raise ValueError('Exact five existing C owner imports required')
    output = []
    for row in world.splitlines(keepends=True):
        output.append(row)
        if row.strip() == line:
            indent = row[:len(row)-len(row.lstrip())]
            output.append(indent + 'from capacidades import pi08_identidad_B_readonly_C_R01 as pi08bc_transport\n')
            output.append(indent + 'pi08b=pi08bc_transport.component(self.a,pi08b)\n')
    text = ''.join(output); ast.parse(text)
    # Removing only the ten adapter lines must recover the exact scientific
    # owner text (universal newline normalization is explicit in this proposal).
    restored = ''.join(row for row in text.splitlines(keepends=True) if 'pi08bc_transport' not in row)
    if restored != world or sha(S / B) != 'aebe20a4566046957b274b07b942a3843ab4b612a9214791ff38edeb6bc53480':
        raise ValueError('Unexpected scientific source change')
    (DEST / WORLD.parent).mkdir(parents=True)
    (DEST / ADAPTER.parent).mkdir()
    (DEST / WORLD).write_text(text, encoding='utf8', newline='\n')
    shutil.copyfile(H / ADAPTER.name, DEST / ADAPTER)
    ast.parse((DEST / ADAPTER).read_text('utf8'))
    originals = DEST / 'ORIGINALES'; (originals / WORLD.parent).mkdir(parents=True)
    shutil.copyfile(S / WORLD, originals / WORLD)
    science = [B, Path('capacidades/pi08_consulta_condicional_C_R03.py'),
               Path('capacidades/pi08_consulta_condicional_C_segunda_R02.py'),
               Path('capacidades/PROTOCOLO_PI08_B_R01.json'), Path('capacidades/PROTOCOLO_PI08_C_R02.json'),
               Path('capacidades/SELLO_PI08_B_R01.json'), Path('capacidades/SELLO_PI08_C_R03.json')]
    plan = {'schema': 'DEE.PI08.C.identity_transport.CAS_proposal.R01', 'applied': False, 'Native_executed': False,
        'system': str(S), 'source_failure_proof': str(P / 'control/PI08_C_PREPARAR_R03.json'),
        'life_id': 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01',
        'required_before_Root_apply': ['Fresh actual owner/job reconciliation; do not assume the historical child PID.',
            'C card still T875451, same physical/causal prefix; no C KEY and no enqueued C material request.',
            'No writer; preserve failed startup proof/lock/marker before any permitted reconciliation.',
            'Root CAS only the two files; use a new technical tag, no reimport, restoration or replay of ambiguous IDs.'],
        'files': [{'relative': str(WORLD), 'before_sha256': sha(S / WORLD), 'after_sha256': sha(DEST / WORLD), 'proposal': str(DEST / WORLD)},
                  {'relative': str(ADAPTER), 'before_sha256': None, 'after_sha256': sha(DEST / ADAPTER), 'proposal': str(DEST / ADAPTER)}],
        'scientific_files_literal': [{'file': str(S / file), 'sha256': sha(S / file)} for file in science],
        'scientific_Native_API_sensor_timing_decoder_policy_changes': False,
        'diagnosis': 'Frozen B rejects PI08_C_ before reaching its already-sealed additional_readonly_life_ids. External exact-C private namespace resolves only this transport access.'}
    proof = P / 'control/PLAN_FIX_C_IDENTIDAD_TRANSPORTE_PI08_R01.json'
    with proof.open('x', encoding='utf8') as stream:
        json.dump(plan, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'plan': str(proof), 'sha256': sha(proof), 'applied': False, 'files': plan['files']}))


if __name__ == '__main__':
    main()
