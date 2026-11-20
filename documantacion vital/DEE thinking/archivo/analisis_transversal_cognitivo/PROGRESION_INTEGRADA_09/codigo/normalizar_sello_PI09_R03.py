"""Correct Root's expected physical-schema shape after an explicit0-input rejection."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
P=Path(__file__).resolve().parents[1];H=P/'codigo';TARGET=H/'SELLO_PI09_CONSULTA_R02.json'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if sha(TARGET)!='505a403f9d42d4c231f536740d16306ead8d4363731b42ab89ca55afe45f0118':raise ValueError('R02 seal changed; no overwrite')
 failed=read(P/'control/PI09_NATIVE_R02.json');primary=read(P/'ensayos/PI09_NATIVE_R02_001.json');error=json.loads(primary['error']);state=read(P/'ensayos/PI09_NATIVE_R02_000.json');actual=json.loads(state['result'])['result']['rows'][0]['physical']
 if failed['new_Native_ticks']!=0 or not failed['closed'] or primary['status']!='rejected_invalid' or error.get('no_material_input_submitted')is not True or error.get('native_tick_unchanged')is not True or error['detail']!='Actual inherited source has already advanced or differs':raise ValueError('Different/ambiguous failed future; preserve and stop')
 v=read(TARGET);keys=('N','tick','RAW_sha256','clocks_sha256');full=v['source_prefix']['physical']
 if set(actual)!=set(keys) or actual!={k:full[k]for k in keys}:raise ValueError('Actual physical values differ, not a schema mismatch')
 backup=H/'SELLO_PI09_CONSULTA_R02_ANTES_NORMALIZACION_R03.json'
 with backup.open('xb')as f:f.write(TARGET.read_bytes())
 v['source_prefix']['manifest_physical_complete']=full;v['source_prefix']['physical']=actual
 v['Root_schema_correction_R03']={'recorded_utc':datetime.now(timezone.utc).isoformat(),'prior_seal_sha256':sha(backup),'preserved_rejected_id':primary['id'],'rejection_primary_sha256':sha(P/'ensayos/PI09_NATIVE_R02_001.json'),'state0_primary_sha256':sha(P/'ensayos/PI09_NATIVE_R02_000.json'),'reason':'Root supplied occupation/size descriptors in an equality against the four-field existing API. Values agree exactly; only expected shape is corrected.','no_values_tolerated_or_edited':True,'Native_inputs_and_ticks_before_correction':0,'new_request_tag_required':True}
 temp=TARGET.with_name(TARGET.name+'.R03.pending')
 with temp.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
 os.replace(temp,TARGET)
 proof=P/'control/NORMALIZACION_ESQUEMA_SOURCE_PI09_R03.json';proof.write_text(json.dumps({'schema':'DEE.PI09.Root_expected_schema_correction.R03','prior_seal_sha256':sha(backup),'new_seal_sha256':sha(TARGET),'correct_expected_API_physical':actual,'full_original_manifest_descriptors_preserved':full,'Native_state_changed':False,'old_rejection_preserved':str(P/'ensayos/PI09_NATIVE_R02_001.json')},ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'seal_sha256':sha(TARGET),'proof':str(proof),'new_Native_ticks':0}))
if __name__=='__main__':main()
