"""Archived zero-tick paired-import checks, not omitted-world restoration."""
import argparse,hashlib,json
from pathlib import Path
def load(p):return json.loads(p.read_bytes())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def calculate(ev):
    old=ev/'FASE_R3_PREPARACION_R01';new=ev/'FASE_R3_PREPARACION_R02';p=load(new/'PREPARACION.json');r=load(new/'IMPORTACION_Y_CIERRE_0TICKS.json');failed=load(old/'OPERACION_1.json');manifest=new/'PAQUETE_PADRE_FINAL_R11/EXPORTACION_SERVICIO.json';m=load(manifest);issues=[];checks={}
    def check(k,v):
        checks[k]=bool(v)
        if not v:issues.append(k)
    check('R01_is_instrument_preflight_rejection',failed['returncode']==2 and'Export has missing or unindexed files'in failed['stderr'])
    check('parent_manifest_exact',digest(manifest)==p['manifest_sha256']and m['snapshot_sha256']=='c2f5c43806de20b1009d9bea3a41503135bf7c914f2691691ecb3bbb7b47d610')
    check('repeated_read_only_validation',p['second_verification_identical_no_sidecars']is True)
    check('all_originals_unchanged',p['protected_before']==p['protected_after']==r['protected_before']==r['protected_after'])
    check('new_identity_not_T0',r['candidate']['life_id']==r['candidate']['world_id']=='MU_MAIN_FASE_R3'and r['candidate']['branch']=='EXPLICIT_IMPORTED_CONTINUITY'and r['candidate']['parent']['encoded_sha256']==m['snapshot_sha256'])
    for key in('N','tick','RAW_sha256','clocks_sha256'):check('native_field_'+key,r['candidate']['physical'][key]==m['physical'][key])
    check('zero_ticks_recorded',r['new_native_ticks']==p['new_native_ticks']==0 and r['candidate']['physical']['tick']==68924)
    check('local_import_and_epoch_close_completed',all(x['returncode']==0 for x in r['operations'])and len(r['operations'])==2)
    check('all_recorded_native_comparisons',not r['issues']and all(r['checks'].values()))
    out0=json.loads(r['operations'][0]['stdout']);out1=json.loads(r['operations'][1]['stdout'])
    check('import_received_full_parent',out0['identity']['source_snapshot_sha256']==m['snapshot_sha256']and out0['verification']['members_verified']==len(m['members']))
    def walk(x):
        if isinstance(x,dict):
            yield x
            for v in x.values():yield from walk(v)
        elif isinstance(x,list):
            for v in x:yield from walk(v)
    closings=[x for x in walk(out1)if x.get('closed_epoch')is True and'native_ticks_advanced'in x]
    check('explicit_technical_epoch_close_zero_ticks',len(closings)==1 and closings[0]['native_ticks_advanced']==0 and closings[0]['physical_before']==closings[0]['physical_after'])
    return {'schema':'DEE.unified.R3.archived_zero_tick_preparation.v1','issues':issues,'checks':checks,'sources':[{'file':str(f.relative_to(ev)).replace('\\','/'),'bytes':f.stat().st_size,'sha256':digest(f)}for f in(old/'OPERACION_1.json',new/'PREPARACION.json',new/'IMPORTACION_Y_CIERRE_0TICKS.json',manifest)],'parent_snapshot_sha256':m['snapshot_sha256'],'imported_then_closed_snapshot_sha256':r['candidate']['snapshot_sha256'],'parent_tick':m['physical']['tick'],'new_identity':r['candidate']['life_id'],'indexed_operational_members':len(m['members']),'validator_sha256':p['validator_sha256'],'scope':'Recalculation of archived identity/field-comparison receipts and manifest, including legitimate negative R01. Complete parent native state/SQLite/artifacts remain local or in the operational package, not this reduced analysis; their full member hashes were checked during original import, not re-read here. No native restore, new tick, phase-flag installation, B0 teaching or content repair is performed.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'issues':r['issues'],'checks':len(r['checks'])}));return bool(r['issues'])
if __name__=='__main__':raise SystemExit(main())
