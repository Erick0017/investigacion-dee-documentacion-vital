"""Bind identity only after explicit CLOSED; never modify prospective payloads."""
import argparse,hashlib,json
from pathlib import Path
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--material',type=Path,required=True);p.add_argument('--corte',type=Path,required=True);p.add_argument('--sello',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();material=read(a.material);cut=read(a.corte);seal=read(a.sello)
    if material['status']!='CANDIDATE_NOT_EXECUTED'or material['schema']!='DEE.collaboration.APD02.prospective_paired_operational.R01':raise ValueError('Exact prospectively fixed candidate required')
    if seal['campaign']!='APD02_CONTINUIDAD_CALIDAD_ADAPTACION'or'CLOSED'not in seal.get('authorization',''):raise ValueError('Only explicit final maintainer closure binds this test')
    if seal['source_cut']['sha256']!=sha(a.corte):raise ValueError('Closed source cut bytes differ from the authorized seal')
    main=cut['main'];service=cut['persistent_service']
    if cut['issues']or service['owner_stopped']is not True or service['pending_or_uncertain']:raise ValueError('Source cut not complete/stopped')
    if len(seal['lives'])!=1 or seal['lives'][0]['life_id']!=main['life_id']or seal['lives'][0]['snapshot_sha256']!=main['snapshot_sha256']:raise ValueError('Closure and selected exact source differ')
    fixed=material['service_protocol'];encoded=json.dumps(fixed,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8');result={**material,'status':'CLOSED_FOR_EXACT_ARCHIVE_PROOF','source_cut':{'life_id':main['life_id'],'tick':main['tick'],'snapshot_sha256':main['snapshot_sha256'],'cut_file_sha256':sha(a.corte),'paired_manifest_sha256':cut['paired_export']['manifest_sha256'],'seal_sha256':sha(a.sello)},'material_settings_sha256':hashlib.sha256(encoded).hexdigest(),'prospective_original_file_sha256':sha(a.material),'binding_scope':'Only actual CLOSED identity/provenance filled. Every stimulus, teacher beta−, codec, time and continuation remains unchanged. Baseline+ is required for a new-revision claim, never retargeted.'}
    if result['service_protocol']!=material['service_protocol']:raise AssertionError('Binding may not change any actor payload')
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'protocol':str(a.salida),'sha256':sha(a.salida),'material_settings_sha256':result['material_settings_sha256'],'new_native_ticks':0}))
if __name__=='__main__':raise SystemExit(main())
