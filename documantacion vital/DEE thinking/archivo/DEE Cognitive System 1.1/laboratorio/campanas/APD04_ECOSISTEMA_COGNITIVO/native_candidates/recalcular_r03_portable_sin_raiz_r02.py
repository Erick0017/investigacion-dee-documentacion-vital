"""Record arithmetic anywhere, including shallow Windows extraction paths.

Uses the exact archived arithmetic functions, but not their local exporter,
canonical-root constants, imports of installed code or entry point. No Native.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',required=True,type=Path)
    args=parser.parse_args();directory=args.evidence.resolve(strict=True)
    manifest=json.loads((directory/'MANIFIESTO.json').read_bytes())
    for member in manifest['members']:
        path=(directory/member['file']).resolve(strict=True)
        if not path.is_relative_to(directory)or path.stat().st_size!=member['bytes']or digest(path)!=member['sha256']:
            raise ValueError('Exported exact member differs: '+member['file'])
    source=directory/'exportar_y_recalcular_wait_r03_post10_n0_r01.py'
    tree=ast.parse(source.read_text(encoding='utf8'))
    required={'read','sha','walk','fields','native_selection','receipts','recalculate'}
    pure=[node for node in tree.body if isinstance(node,(ast.Import,ast.ImportFrom))
          or isinstance(node,ast.FunctionDef)and node.name in required]
    assert {node.name for node in pure if isinstance(node,ast.FunctionDef)}==required
    namespace={'__name__':'archived_primary_record_arithmetic_only'}
    exec(compile(ast.Module(body=pure,type_ignores=[]),str(source),'exec'),namespace)
    result=namespace['recalculate'](directory)
    expected=json.loads((directory/'RECALCULO.json').read_bytes())
    if result!=expected:raise ValueError('The selected primary recalculation differs from the closed recorded calculation.')
    print(json.dumps({'exact_manifest_members_verified':len(manifest['members']),
        'archived_recalculation_equal':True,'no_local_root_or_engine_required':True,
        'new_native_ticks':0,'branches':[{k:r[k]for k in('branch','work_requests_completed','actions','old_work_gain','new_quality','Native_receipts','receipt_statuses')}
            for r in result['branches']]},ensure_ascii=False))


if __name__=='__main__':main()
