"""Synthetic/config-only checks; never validates a live paired world."""
import argparse,copy,hashlib,importlib.util,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--material',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    here=Path(__file__).parent;source=here/'vincular_control_omit_n0.py';spec=importlib.util.spec_from_file_location('omit_binder_n0',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    fixed=json.loads(a.material.read_bytes());assert hashlib.sha256(a.material.read_bytes()).hexdigest()==m.FIXED_SHA
    parent='a'*64;resolved=copy.deepcopy(fixed);resolved['snapshot_sha256']=parent;resolved['status']='SYNTHETIC_IDENTITY_BINDING_NOT_A_REAL_PARENT'
    derived,diff=m.bind(fixed,resolved,{'snapshot_sha256':parent},'APD02_SYNTHETIC_CONTROL','mockomit_')
    assert len(derived['events'])==17 and all(e['payload']['retorno']=='omit'for e in derived['events'])
    assert all(x['path']in('/life','/prefix')or x['path'].endswith('/payload/retorno')for x in diff)
    actual=[s for e in derived['events']for s in e['payload']['situaciones']if s['modo']=='apd02']
    assert len(actual)==14
    edited=copy.deepcopy(resolved);edited['events'][2]['payload']['situaciones'][0]['operandos'][0]+=1
    try:m.bind(fixed,edited,{'snapshot_sha256':parent},'APD02_SYNTHETIC_CONTROL','mockomit_')
    except ValueError:rejected=True
    else:rejected=False
    assert rejected
    result={'schema':'APD02.quality_control_binder.synthetic_N0.v1','native_ticks':0,'world_loaded':False,'paired_package_imported_or_verified':False,'material_sha256':m.FIXED_SHA,'checks':{'fixed_17_events':True,'APD_primitives_14':True,'feedback_only_scientific_differences':True,'modified_operand_rejected':True},'synthetic_binding_diff':diff,'scope':'Only transform/allowlist testing on copied configuration objects. No real parent, native capacity, service continuity or outcome tested.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    if a.salida.exists():raise FileExistsError('Keep every test revision')
    a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
