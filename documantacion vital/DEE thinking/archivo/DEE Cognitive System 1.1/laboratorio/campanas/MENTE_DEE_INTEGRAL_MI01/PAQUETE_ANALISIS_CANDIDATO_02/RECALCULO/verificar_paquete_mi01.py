"""Recalcula evidencia archivada, NO ejecuta DEE ni el simulador externo.

Sólo biblioteca estándar. La presencia de código operativo en el delta no lo
ejecuta ni permite leer respuestas para E1. Salida científica y límites separados.
"""
import argparse,collections,csv,gzip,hashlib,importlib.util,json,sys
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def verify(root,write_reference=False):
    audit=module('mi01_recalc',root/'RECALCULO/recalcular_mi01.py');snap=module('mi01_snapshot',root/'RECALCULO/snapshot_lector.py')
    hashes=[];man=root/'MANIFIESTO_MIEMBROS.json'
    if man.exists():
        expected=read(man)['members']
        for r in expected:
            p=root/r['path'];assert p.is_file(),r['path'];b=p.read_bytes();assert len(b)==r['bytes']and sha(b)==r['sha256'],r['path'];hashes.append(r['path'])
        actual={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}
        assert actual=={r['path']for r in expected}|{'MANIFIESTO_MIEMBROS.json'},'Unexpected/missing package members'
    index=read(root/'INDICE_FUENTES_Y_OMISIONES.json');exact=0
    for r in index['entries']:
        if not r.get('included')or'member'not in r:continue
        b=(root/r['member']).read_bytes()
        if r.get('transport','').startswith('lossless gzip'):b=gzip.decompress(b)
        assert len(b)==r['original_bytes']and sha(b)==r['original_sha256'],r['original'];exact+=1
    calc=audit.calculate(root);assert not calc['raw_validation']['mismatches']
    ref=root/'RECALCULO/CALCULOS_REFERENCIA.json'
    if write_reference:save(ref,calc)
    else:assert calc==read(ref),'Recalculation differs from sealed reference'
    f=calc['frozen_summary'];assert(f['opportunities'],f['useful_contacts'],f['harmful_contacts'],f['external_steps'],f['nonneutral_external_actions'])==(9,0,1,47,1)
    assert(f['native_failure_initiated_questions'],f['unique_valid_B_reply_events'],f['valid_failure_reply_selector_uses'])==(1,1,0)
    # Every authored CSV cell is compared, not only file existence/row count.
    tables=[]
    for t in read(root/'RECALCULO/TABLAS_DATOS.json')['tables']:
        with(root/t['filename']).open(encoding='utf-8-sig',newline='')as handle:rows=list(csv.reader(handle))
        expected=[[str(v)for v in t['headers']],*[[str(v)for v in row]for row in t['rows']]]
        assert rows==expected,t['filename'];tables.append({'file':t['filename'],'rows':len(rows)-1,'all_cells_equal':True})
    selected=read(root/'EVIDENCIA_CAUSAL/ESTADOS_SELECCIONADOS/INDICE_ESTADOS.json');paths={r['id']:root/r['member']for r in selected};summaries={}
    for key,p in paths.items():
        q=snap.Snapshot(p);summaries[key]={k:v for k,v in q.summary().items()if k!='path'}
    def compare(a,b):return snap.compare(snap.Snapshot(paths[a]),snap.Snapshot(paths[b]))
    observer=compare('main_reserved1','observer470_end')
    assert observer['RAW_different_sites']==observer['clock_different_sites']==0
    assert all(observer[k]for k in('pending_equal','channels_equal','receipts_equal','prefix_through_execution_before_metadata_equal'))
    assert observer['different_owner_sections']==[]
    external=compare('main_reserved_end','null_reserved_end');assert external['RAW_different_sites']==1 and external['clock_different_sites']==0
    assert external['differences_sample'][0]['site']==[50,31,35]
    assert external['differences_sample'][0]['a']['s_reg']==87 and external['differences_sample'][0]['b']['s_reg']==92
    free=compare('main_final','free490_end');assert free['RAW_different_sites']==0 and free['clock_different_sites']>0
    assert calc['consecutive_input_free_ticks']['unique_RAW_hashes']==1 and calc['consecutive_input_free_ticks']['distinct_clock_hashes']==68
    before=snap.Snapshot(paths['main_preparation_selected']);after=snap.Snapshot(paths['main_final']);old={r['id']for r in before.receipts};new=[r for r in after.receipts if r['id']not in old];counts=dict(collections.Counter(r['status']for r in new))
    assert len(new)==804 and counts=={2:173,5:613,6:18},counts
    local={}
    for key,site in [('original473_25008',[25,56,41]),('original473_25009',[25,56,41]),('intervention476_25009',[25,56,41]),('intervention477_25009',[25,56,41]),('intervention476_25154',[40,35,55]),('intervention477_25154',[40,35,55]),('second479_25093',[40,30,43]),('second479_25094',[40,30,43])]:
        local[key]=snap.Snapshot(paths[key]).observation(site)
    assert local['original473_25008']['state']==0 and local['original473_25008']['raw']=='0'
    assert local['original473_25009']['s_reg']==338
    assert local['intervention476_25009']['s_reg']==150 and local['intervention477_25009']['s_reg']==338
    assert not audit.material(local['intervention476_25154'])and not audit.material(local['intervention477_25154'])
    assert local['second479_25094']['s_reg']==150 and local['second479_25094']['direction']==[0,0,0]
    q=snap.Snapshot(paths['second479_25093']);byid={r['id']:r for r in q.receipts};actual_turn=[byid[k]for k in(3364,3365)];assert all(r['status']==2 and r['effective_tick']==25091 for r in actual_turn)
    result={'native_ticks':0,'external_simulator_steps':0,'package_members_hashed':len(hashes),'exact_original_export_checks':exact,'primary_RAW_observations_checked':calc['raw_validation']['native_observations_checked'],'primary_RAW_mismatches':calc['raw_validation']['mismatches'],'portable_recalculation_equals_reference':True,'tables':tables,'full_snapshots_checked':summaries,'observer470_recomputed':observer,'external483_recomputed':external,'stationary_RAW_not_clocks_recomputed':free,'receipts_from_full_snapshots':{'unique_new_requests':len(new),'enum2_APPLIED_5_OCCUPIED_6_CONFLICT':counts,'pending_after':after.pending},'local_encounters_from_full_snapshots':local,'second_turn_admission_from_full_snapshot':actual_turn,'frozen_summary':f,'classification_not_automated':'These checks establish data/integrity/arithmetic, not a cognitive PASS, general learning, consciousness, a competent policy or65meanings. Scientific interpretation and coverage remain in the report.','snapshot_scope':'In-flight diagnostic snapshots contain full physical/owner bytes but not all bridge locals; they are not supported operational continuation boundaries. The ZIP is not a complete system backup.'}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raiz',type=Path,default=Path(__file__).resolve().parent.parent);p.add_argument('--salida',type=Path,required=True);p.add_argument('--write-reference',action='store_true');a=p.parse_args();result=verify(a.raiz.resolve(),a.write_reference);save(a.salida,result);print(json.dumps({k:result[k]for k in('native_ticks','external_simulator_steps','package_members_hashed','exact_original_export_checks','primary_RAW_observations_checked','portable_recalculation_equals_reference','frozen_summary')},ensure_ascii=False,indent=2))
