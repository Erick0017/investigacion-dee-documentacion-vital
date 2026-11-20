"""Read a genuinely closed F1 cut proof and create a fresh tiny portable index.

No snapshots/worlds are created or modified, no Native import. Without an actual
successful diagnostic cut this refuses an index; it never invents missing data.
"""
from pathlib import Path
import argparse,hashlib,json
P=Path(__file__).resolve().parents[1]
def need(b,t):
    if not b:raise ValueError(t)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,j):
    with p.open('x',encoding='utf-8')as f:json.dump(j,f,ensure_ascii=False,indent=2);f.write('\n')
def main(a):
    proof=Path(a.proof).resolve(strict=True);need(proof.is_relative_to(P),'Only actual PI08proof')
    j=json.loads(proof.read_text('utf-8-sig'))
    need(j.get('closed')is True and j.get('error')is None and j.get('status')=='CLOSED_TWO_OPERATIONS','F1 not actually closed successfully; no inferred cut/index')
    need(j.get('actual_additional_Runtime_forks')==2,'Exact actual identity+cut forks must be recorded')
    row=j['rows'][0];it=row['diagnostic_intervention']
    need(it.get('status')=='DIAGNOSTIC_RAW_CUT_AFTER_STRUCTURAL_IDENTITY'and it.get('diagnostic_edit_applied')is True,'No actual fixed rawcut; do not construct favorable evidence')
    need(it['identity_sham_future_Native_ticks']==0 and it['parent_Native_complete_content_unchanged']is True,'Identity future/parent differs')
    dest=Path(a.destino).resolve();need(dest.is_relative_to(P/'fuentes')and not dest.exists(),'Fresh small P8/fuentes directory only')
    roles={'before':('before_snapshot','Q8_PARENT_BEFORE.deetsnap.gz'),'identity':('identity_sham_snapshot','Q8_IDENTITY_NO_FUTURE.deetsnap.gz'),'cut':('branch_after_snapshot','Q8_BRANCH_AFTER.deetsnap.gz')}
    index={'schema':'DEE.PI08.F1.portable_snapshot_triplet.R03','fixed_site':[52,48,56],'raw_cut_value':0,'clock_edit':None,'identity':None,'identity_report':None,'identity_omission_reason':None,'source_proof_sha256':sha(proof),'scope':'Actual frozen q8 diagnosticcut; no new Native execution or shamfuture.'}
    snapshots=[]
    for role,(field,name)in roles.items():
        e=it[field]['snapshot'];src=Path(e['path']).resolve(strict=True)
        need(src.is_relative_to(P/'estados/F1_CUT_R03')and src.name==name,'Exact F1q8 source only')
        need(src.stat().st_size==e['bytes']and sha(src)==e['sha256'],'Original immutable F1snapshot differs')
        if role=='identity'and a.omitir_identidad:continue
        member='04_EVIDENCIAS/F1_Q8/'+name
        index[role]={'file':member,'bytes':e['bytes'],'sha256':e['sha256'],'source_reference_for_packager_only':str(src)}
        snapshots.append({'source':str(src),'file':member,'bytes':e['bytes'],'sha256':e['sha256']})
    if a.omitir_identidad:
        index['identity_report']={'evidence':{'file':'04_EVIDENCIAS/CONTROL/'+proof.name,'bytes':proof.stat().st_size,'sha256':sha(proof)},
          'full_content_sha256_pointer':'/rows/0/diagnostic_intervention/identity_sham_snapshot/Native_complete_content_sha256',
          'future_ticks_pointer':'/rows/0/diagnostic_intervention/identity_sham_future_Native_ticks'}
        index['identity_omission_reason']='Original full identity snapshot preserved locally; omitted only from15,000,000B analysis package. Included actual proof binds complete-content hash. Portable check does not reparse that omitted binary.'
    dest.mkdir(parents=True,exist_ok=False);idx=dest/'INDICE_F1_Q8_PI08_R03.json';put(idx,index)
    code=P/'codigo/RECALCULAR_SNAPSHOTS_F1_PI08_R03.py'
    addon={'schema':'DEE.PI08.F1.package_config_addon.R03','small_F1_snapshots':snapshots,
      'files_to_append':[{'source':str(idx),'file':'04_EVIDENCIAS/F1_Q8/INDICE_F1_Q8_PI08_R03.json','role':'Actual diagnostic snapshot comparison index'},
        {'source':str(code),'file':'05_RECALCULO/RECALCULAR_SNAPSHOTS_F1_PI08_R03.py','role':'Pure complete RAW/clocks/metadata comparison, no Native'}],
      'portable_verifications_to_append':[{'script':'05_RECALCULO/RECALCULAR_SNAPSHOTS_F1_PI08_R03.py','argv':['--raiz','{EXTRACTION}','--indice','04_EVIDENCIAS/F1_Q8/INDICE_F1_Q8_PI08_R03.json','--salida','{OUTPUT}/F1_SNAPSHOTS.json'],
        'result_file':'F1_SNAPSHOTS.json','result_schema':'DEE.PI08.F1.recalculated_snapshot_cut.R03','expect':{'/all_checks_passed':True,'/new_Native_ticks':0,'/DEE_imports':0}}],
      'actual_q8_tick':it['hook_tick'],'snapshot_payload_bytes':sum(v['bytes']for v in snapshots),'new_Native_ticks':0,'source_proof':str(proof),'source_proof_sha256':sha(proof)}
    put(dest/'CONFIG_F1_Q8_PARA_PLAN.json',addon)
    print(json.dumps({'index':str(idx),'index_sha256':sha(idx),'snapshot_count':len(snapshots),'bytes':addon['snapshot_payload_bytes'],'new_Native_ticks':0},ensure_ascii=False))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--proof',required=True);ap.add_argument('--destino',required=True);ap.add_argument('--omitir-identidad',action='store_true');main(ap.parse_args())
