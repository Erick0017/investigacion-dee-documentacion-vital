"""Close the existing campaign record with actual separate science/publication witnesses."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
P=Path(__file__).resolve().parents[1]
def read(q): return json.loads(q.read_text('utf-8-sig'))
def sha(q): return hashlib.sha256(q.read_bytes()).hexdigest()
def ref(q): return {'path':str(q),'sha256':sha(q),'bytes':q.stat().st_size}
def main():
    path=P/'REGISTRO_CAMPANA.json';j=read(path)
    if 'cierre_cientifico_y_operativo' in j: raise ValueError('Do not repeat closed registry')
    closure=P/'control/CIERRE_CIENTIFICO_PI08_R01.json'
    pub=P/'documentos/PUBLICACION_CIERRE_1_36.json'
    sync=P/'control/CIERRE_4JSON_PI08_1_36_APLICADO_R02.json'
    c=read(closure);p=read(pub);s=read(sync)
    if not c['closed'] or not c['all_scoped_Native_writers_closed'] or p['edition']!='1.36' or not s['applied']:
        raise ValueError('Actual closed science/document publication/metadata application required')
    j['phase_before_final_closure']=j['phase'];j['phase']='SCIENCE_AND_OPERATION_CLOSED'
    j['cierre_cientifico_y_operativo']={
        'at_utc':datetime.now(timezone.utc).isoformat(),
        'actual_principal':c['main_actual'],
        'science':ref(closure),'publication':ref(pub),'metadata':ref(sync),
        'Native_ticks_actual':87963,'world_slots_actual':10,
        'all_new_experimental_Native_work_closed':True,'budget_not_reset_or_increased':True,
        'B_adopted':False,'C_adopted':False,'F1_cut_executed':False,
        'historical_reanudacion_and_start_phase_not_current_work':True,
        'delivery_verification_is_separate':'control/VERIFICACION_ZIP_FINAL_PI08_R01.json',
        'delivery_verification_executed_at_this_registry_cut':False,
        'this_registry_does_not_claim_a_future_ZIP_exists':True,
        'Native_ticks_by_this_update':0,'DEE_imports':0}
    before=P/'control/REGISTRO_ANTES_CIERRE_PI08_R01.json'
    with before.open('xb') as f: f.write(path.read_bytes())
    temp=path.with_name(path.name+'.CIERRE_WRITING')
    with temp.open('x',encoding='utf-8') as f: json.dump(j,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temp,path)
    print(json.dumps({'record':ref(path),'previous_literal':ref(before),'Native_ticks_by_update':0}))
if __name__=='__main__': main()
