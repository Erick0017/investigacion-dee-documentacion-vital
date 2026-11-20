"""Text-only S2 merge; preserve S2 hooks and the product OP4 forwarding fix.

No deployment, Native import, world, query, queue or selector is touched.
"""
from pathlib import Path
import ast
import datetime
import difflib
import hashlib
import json

P = Path(__file__).resolve().parents[1]
R = P.parent.parent.parent
H = P / 'codigo'
S2 = P / 'estados/candidato_R02/sistema'
PRODUCT = R / 'DEE Cognitive 2.0/sistema'
OLD = H / 'PUERTA_GESTOR_PI04_OP1'
OUT = H / 'PUERTA_GESTOR_PI04_S2_OP2'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def once(s, old, new):
    if s.count(old) != 1: raise ValueError('Directed manager source locator changed')
    return s.replace(old, new, 1)
def norm(p): return p.read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def main():
    if OUT.exists(): raise ValueError('Preserve previous proposal')
    actual_bytes = (S2 / 'gestionar.py').read_bytes()
    actual = norm(S2 / 'gestionar.py')
    product = norm(OLD / 'gestionar_ANTES_PRODUCTO.py')
    old_proposal = norm(OLD / 'gestionar.py')
    needle = 'sys.path.insert(0,str(Path(__file__).resolve().parent))\nfrom app.lives import Store,read,SYSTEM_ROOT'
    added_start = '# Fixed transport-only PI04 convenience door, before Store/Native imports.\n'
    insertion = old_proposal[old_proposal.index(added_start):old_proposal.index(needle)]
    parser_start = "    for _name in('pi04-coordinacion-estado','pi04-coordinacion-oportunidad'):\n"
    parser_end = "    for name in('estado','vidas','version','capacidades','perfiles','interactivo'):\n"
    parser_insertion = old_proposal[old_proposal.index(parser_start):old_proposal.index(parser_end)]
    parser_marker = "    sub.add_parser('reproducibilidad',help='listar/verificar/recalcular/reproducir: usar como primer comando, sin --system-root; puerta stdlib previa a Native')\n"
    only_door = once(actual, needle, insertion + needle)
    only_door = once(only_door, parser_marker, parser_marker + parser_insertion)
    old_forward = """    return subprocess.run(command,cwd=product,shell=False,
          creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)).returncode"""
    new_forward = """    completed=subprocess.run(command,cwd=product,shell=False,
          capture_output=True,text=True,encoding='utf-8',errors='strict',
          creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    # CREATE_NO_WINDOW does not reliably inherit console handles on Windows.
    # Capture pipes explicitly, then forward the exact structured output.
    if completed.stdout:sys.stdout.write(completed.stdout);sys.stdout.flush()
    if completed.stderr:sys.stderr.write(completed.stderr);sys.stderr.flush()
    return completed.returncode"""
    merged = once(only_door, old_forward, new_forward)
    expected_product = once(actual, old_forward, new_forward)
    if expected_product != product:
        raise ValueError('There are additional S2/product differences. Preserve and review; do not overwrite')
    reversed_merge = once(once(once(merged, insertion, ''), parser_insertion, ''), new_forward, old_forward)
    if reversed_merge != actual: raise ValueError('The merge changed more than the two CLI insertions and explicit OP4 block')
    for s in (only_door, merged): ast.parse(s)
    OUT.mkdir()
    (OUT / 'gestionar_ANTES_S2.py').write_bytes(actual_bytes)
    (OUT / 'gestionar_ANTES_PRODUCTO.py').write_bytes((OLD / 'gestionar_ANTES_PRODUCTO.py').read_bytes())
    (OUT / 'gestionar_SOLO_PUERTA.py').write_text(only_door, encoding='utf8', newline='')
    (OUT / 'gestionar.py').write_text(merged, encoding='utf8', newline='')
    client = OLD / 'pi04_cliente_acotado.py'
    (OUT / client.name).write_bytes(client.read_bytes())
    (OUT / 'DIFF_PRODUCTO_A_S2.txt').write_text(''.join(difflib.unified_diff(product.splitlines(True), actual.splitlines(True), fromfile='PRODUCTO_OP4_ANTES', tofile='S2_ACTUAL', n=4)), encoding='utf8')
    (OUT / 'DIFF_S2_A_MERGE.txt').write_text(''.join(difflib.unified_diff(actual.splitlines(True), merged.splitlines(True), fromfile='S2_ACTUAL', tofile='S2_PUERTA_MAS_OP4', n=4)), encoding='utf8')
    proof = {'schema': 'PI04.manager_merge.S2.OP2', 'status': 'PREPARED_NOT_INSTALLED',
        'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source_S2_sha256': sha(S2 / 'gestionar.py'), 'source_product_sha256': sha(PRODUCT / 'gestionar.py'),
        'original_product_baseline_sha256': sha(OLD / 'gestionar_ANTES_PRODUCTO.py'),
        'manager_only_door_sha256': sha(OUT / 'gestionar_SOLO_PUERTA.py'),
        'manager_merged_sha256': sha(OUT / 'gestionar.py'), 'client_sha256': sha(OUT / client.name),
        'source_difference': 'Only product OP4 stdout/stderr capture-and-forwarding block is absent in S2; no other textual differences',
        'merge_changes': ['Two bounded PI04 CLI insertions before Store/Native and inside parser',
            'Explicit backport of existing product OP4 subprocess capture-and-forwarding fix'],
        'all_other_S2_hooks_and_text_identical': reversed_merge == actual,
        'merged_equals_existing_product_proposal_normalized': merged == old_proposal,
        'source_S2_unchanged': (S2 / 'gestionar.py').read_bytes() == actual_bytes,
        'Native_ticks': 0, 'queues_or_selectors_opened': False,
        'apply_requires': 'Root confirms Yoked owner closed and all S2 writer locks absent. New CAS must use the actual S2 baseline, never the product baseline.'}
    (OUT / 'PROPUESTA_NO_APLICADA.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    incidence = {'schema': 'PI04.manager_install.CAS_refusal.preserved.v1',
        'recorded_utc': proof['recorded_utc'], 'event_source': 'Root report, not a re-execution of the installer',
        'reported_failure': 'instalar_puerta_gestor_PI04_OP1.py first assertion failed before its backup/copy writes',
        'expected_product_baseline_sha256': proof['original_product_baseline_sha256'],
        'observed_actual_S2_sha256': proof['source_S2_sha256'],
        'CAS_rejection_explained': proof['source_S2_sha256'] != proof['original_product_baseline_sha256'],
        'S2_client_absent': not (S2 / 'app/pi04_cliente_acotado.py').exists(),
        'old_installer_backup_absent': not (H / 'revisiones/ANTES_PUERTA_GESTOR_OP1').exists(),
        'new_merge_proposal': str(OUT), 'Native_ticks': 0,
        'no_root_installer_retry_or_S2_write_by_this_analysis': True,
        'limit': 'The whole live project was not hashed; this is a directed source/CAS explanation, not a claim of project-wide immutability.'}
    path = P / 'control/INCIDENCIA_CAS_PUERTA_GESTOR_OP1.json'
    if path.exists(): raise ValueError('Preserve existing incident record')
    path.write_text(json.dumps(incidence, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(proof, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
