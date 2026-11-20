"""Zero-tick equivalence check for the truthful FENCE description correction.

No application imports, Runtime, permission or physical-state changes.
The only admitted AST delta is the descriptive return metadata approved by Root.
"""
from __future__ import annotations
import argparse,ast,hashlib,json
from pathlib import Path

EXTRA={
    'legacy_combined_flag_deprecated_no_universal_history_guarantee',
    'no_undeclared_external_lab_or_evidence_reads_allowed',
    'operational_history_reads_universally_blocked',
}
LEGACY='no_lab_evidence_or_history_reads_allowed'
EXPECTED={
    'app/access_guard.py':'3013068b94db6d391806578722d4744f65e250fc5da8e87d40fbced3c98d1e5f',
    'app/servicio_persistente.py':'d8edc0966eb9f027f5c7ec31b0dbc50a26ad7a9d21fa9b63b99bdfe3de2afafa',
    'gestionar.py':'7b41d94ed96e4c5bbd486273cc59580c335b1b1a83633dcdfd30fd632a117739',
}

def sha(b):return hashlib.sha256(b).hexdigest()
class NormalizeDescription(ast.NodeTransformer):
    def visit_Dict(self,node):
        self.generic_visit(node)
        if any(isinstance(k,ast.Constant) and k.value==LEGACY for k in node.keys):
            pairs=[]
            for k,v in zip(node.keys,node.values):
                if isinstance(k,ast.Constant) and k.value in EXTRA:continue
                if isinstance(k,ast.Constant) and k.value==LEGACY:v=ast.Constant(True)
                pairs.append((k,v))
            node.keys=[k for k,v in pairs];node.values=[v for k,v in pairs]
        # Only the constant scope descriptor returned by install is normalized.
        if any(isinstance(k,ast.Constant) and k.value=='temporary_owner' for k in node.keys):
            for i,k in enumerate(node.keys):
                if isinstance(k,ast.Constant) and k.value=='scope':
                    if not isinstance(node.values[i],ast.Constant) or not isinstance(node.values[i].value,str):
                        raise ValueError('Scope is no longer a literal description')
                    node.values[i]=ast.Constant('NORMALIZED_DESCRIPTOR_ONLY')
        return node

def tree(b):
    return ast.dump(NormalizeDescription().visit(ast.parse(b.decode('utf-8-sig'))),include_attributes=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--system',type=Path,required=True)
    ap.add_argument('--before',type=Path,required=True,help='Exact old three files under original relative paths')
    ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError('Preserve earlier validation')
    rows=[]
    for rel,wanted in EXPECTED.items():
        old=(a.before/rel).read_bytes();new=(a.system/rel).read_bytes()
        if sha(old)!=wanted:raise ValueError('Unrecognized original bytes: '+rel)
        if tree(old)!=tree(new):raise ValueError('Change exceeds return metadata: '+rel)
        parsed=ast.parse(new.decode('utf-8-sig'));legacy=[];truth=[]
        for node in ast.walk(parsed):
            if isinstance(node,ast.Dict):
                values={k.value:v.value for k,v in zip(node.keys,node.values)
                        if isinstance(k,ast.Constant) and isinstance(v,ast.Constant)}
                if LEGACY in values:
                    legacy.append(values[LEGACY]);truth.append({k:values.get(k) for k in EXTRA})
        if rel!='app/access_guard.py':
            if not legacy or any(v is not False for v in legacy):raise ValueError('Overclaim retained')
            for t in truth:
                if t!={'legacy_combined_flag_deprecated_no_universal_history_guarantee':True,
                       'no_undeclared_external_lab_or_evidence_reads_allowed':True,
                       'operational_history_reads_universally_blocked':False}:raise ValueError('Descriptor mismatch')
        rows.append({'relative_SYSTEM':rel,'before_sha256':sha(old),'after_sha256':sha(new),
                     'AST_equal_after_only_approved_descriptor_normalization':True,
                     'native_ticks':0,'permission_logic_unchanged':True})
    result={'schema':'APD01.FENCE.precise_description.N0.v1','native_ticks':0,'files':rows,
            'scope':'Corrects a universal-history-blocking overclaim, not permissions or historical receipts. No Runtime/import/physics replay. This check is not an OS sandbox test or proof of absence of every possible hidden solver.'}
    a.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
