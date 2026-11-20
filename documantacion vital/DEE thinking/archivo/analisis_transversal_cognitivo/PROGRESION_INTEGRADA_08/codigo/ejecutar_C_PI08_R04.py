"""Root-only finite C preparation/six-case owner runner; default plan only.

No DEE import in this supervisor. Actual control is one explicit complete
diagnostic world; no replacement, repeated ambiguous request or promotion.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, hashlib, importlib.util, json, os

P=Path(__file__).resolve().parents[1]; H=P/'codigo'; C=P.parents[2]/'DEE Cognitive 2.0'; RP=C/'reproducibilidad'; PY=C/'motor/python313/python.exe'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01'

def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)
def receipts(items):
    unique={};aliases=0
    for row in items:
        rid=row['id'];receipt=row['receipt'];require(type(rid)is int and receipt['id']==rid,'Actual Native receipt identity required')
        if rid in unique:require(unique[rid]==receipt,'Contradictory receipt alias');aliases+=1
        unique[rid]=receipt
    return unique,aliases

def main(args):
    seal=read(H/'SELLO_PI08_C_R03.json');protocol=read(H/'PROTOCOLO_PI08_C_R02.json')
    require(seal['life_id']==LIFE and seal['protocol_sha256']==sha(H/'PROTOCOLO_PI08_C_R02.json')and protocol['status']=='SEALED_BEFORE_C_NATIVE','Prospective actual-source C seal required')
    system=Path(args.sistema).resolve(strict=True)
    require(system.is_relative_to((P/'estados').resolve())and system.name=='sistema'and not(system/'estado/ACTIVO.json').exists(),'Explicit isolated unselected C system only')
    steps=[{'label':'preparar','literal':{'modo':'eci01-pi08-c-preparar'},'max_ticks':3}]if args.fase=='preparar'else[{'label':'EP%02d'%i,'literal':{'modo':'eci01-pi08-c-episodio'},'max_ticks':2099}for i in range(6)]
    bound=sum(row['max_ticks']for row in steps)
    if not args.ejecutar:
        print(json.dumps({'mode':'PLAN_ONLY_NO_NATIVE','life_id':LIFE,'phase':args.fase,'steps':steps,'finite_Native_bound':bound,'whole_C_bound':12600,'no_adoption':True},ensure_ascii=False,indent=2));return
    budget=read(P/'REGISTRO_CAMPANA.json')['budget'];cutoff=datetime.fromisoformat(budget['new_experimental_uses_cutoff_local']).astimezone(timezone.utc)
    require(datetime.now(timezone.utc)<cutoff,'Scientific deadline reached')
    # Reuse the exact global Native ledger, including A moved into the product.
    loader=importlib.util.spec_from_file_location('PI08_C_shared_ledger',H/'ejecutar_B_PI08_R01.py');ledger=importlib.util.module_from_spec(loader);loader.loader.exec_module(ledger)
    used,lives=ledger.native_ledger();require(used+bound<=budget['Native_ticks_all_branches']and len(lives)<=budget['diagnostic_worlds_all_new'],'Campaign Native/world budget unavailable')
    cardpath=system/'estado/vidas'/LIFE/'VIDA.json';card=read(cardpath)
    expected=seal['source_prefix']['T']+(0 if args.fase=='preparar' else 3)
    require(card['physical']['N']==67 and card['physical']['tick']==expected,'Exact current C cut required; no reset or stale future')
    require(not(system/'estado/vidas'/LIFE/'FUTURO_INTERRUMPIDO.json').exists(),'Preserve interrupted C future')
    locks=system/'estado/locks';require(not locks.exists()or not any(locks.iterdir()),'An owner lock remains; inspect not erase')
    proof=P/'control'/('PI08_C_'+args.fase.upper()+'_R04.json');marker=P/'PI08_ROOT_NATIVE_WRITER.lock'
    require(not proof.exists()and not marker.exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Fresh C phase and one Root writer only')
    activepath=C/'sistema/estado/ACTIVO.json';active=read(activepath);maincardpath=C/'sistema/estado/vidas'/active['life_id']/'VIDA.json';maincard=read(maincardpath)
    protected_paths=[activepath,maincardpath,C/'sistema'/maincard['snapshot']];protected={str(path):sha(path)for path in protected_paths}
    with marker.open('x',encoding='utf8')as out:json.dump({'pid':os.getpid(),'life_id':LIFE,'phase':args.fase,'finite_Native_bound':bound},out)
    loader=importlib.util.spec_from_file_location('PI08_C_owned_driver',RP/'propietario_diagnostico.py');driver=importlib.util.module_from_spec(loader);loader.loader.exec_module(driver);driver.configure(P,system,PY)
    owner=None;error=None;records=[];intervals=[];states={};ids=set();totals=Counter();initial=card['physical']['tick'];proto_bytes=(H/'PROTOCOLO_PI08_C_R02.json').read_bytes();seal_bytes=(H/'SELLO_PI08_C_R03.json').read_bytes()
    def call(label,literal,max_ticks):
        require(datetime.now(timezone.utc)<cutoff,'Deadline before next material operation')
        require((H/'PROTOCOLO_PI08_C_R02.json').read_bytes()==proto_bytes and(H/'SELLO_PI08_C_R03.json').read_bytes()==seal_bytes,'C protocol changed after sealing')
        identifier='PI08_C_'+args.fase.upper()+'_R04_'+label
        value=owner.material(identifier,literal,feedback='real',actuator='closed',allow_failure=True)
        require('before_tick'in value and'after_tick'in value and 0<=value['after_tick']-value['before_tick']<=max_ticks,'Incomplete transport or finite horizon exceeded; preserve SAME request')
        file=P/'ensayos'/(identifier+'.json');intervals.append({'id':identifier,'before_tick':value['before_tick'],'after_tick':value['after_tick'],'primary':str(file),'sha256':sha(file)})
        return value['result']['rows'][0]
    try:
        owner=driver.Owner(LIFE,'PI08_C_'+args.fase.upper()+'_R04')
        with owner:
            states['before']=call('estado_pre',{'modo':'eci01-pi08-c-estado'},0)
            if args.fase=='preparar':require(states['before']['present']is False,'Never reinstall C')
            else:require(states['before']['progress']['ordinal']==0 and states['before']['progress']['ready'],'Closed new C preparation required')
            for step in steps:
                row=call(step['label'],step['literal'],step['max_ticks']);direct,aliases=receipts(row['requests']);counts=Counter(value['status']for value in direct.values())
                require(not ids.intersection(direct),'Historical Native IDs counted as new');ids.update(direct);totals.update(counts)
                require(all(k=='applied'or k.startswith('rejected')for k in counts),'Unknown/pending Native input; stop')
                require(row['Native_inputs']['unique_requested']==len(direct)and row['Native_inputs']['applied']==counts['applied'],'Whole first+second Native receipt denominator differs')
                if args.fase=='preparar':require(row['ready']and len(direct)==1 and counts['applied']==1,'Legal fixed device did not prepare')
                else:
                    first,second=row['first_stage'],row['second_stage'];register=first['sample_register']
                    require(second['sensor']['submitted_state_datum']==row['extra_bit_entered_second_TC']==register['released_bit'],'Actual releasedbit did not enter second TC')
                    require(row['old_metadata_literal_unchanged']and row['no_first_trace_credit_claim'],'Old metadata or attribution changed')
                records.append(row)
            states['after']=call('estado_post',{'modo':'eci01-pi08-c-estado'},0)
            progress=states['after']['progress'];require(progress['ordinal']==(0 if args.fase=='preparar' else 6)and not progress['pending']and not progress['uncertain'],'Final coherent C counter required')
            owner.control('guardar')
    except Exception as exc:error={'type':type(exc).__name__,'message':str(exc),'automatic_retry':False}
    closed=bool(owner is not None and owner.proc is not None and owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running'))
    protected_after={str(path):sha(path)for path in protected_paths}
    if protected_after!=protected:error={'type':'CURRENT_PRINCIPAL_CHANGED','automatic_retry':False}
    final=read(cardpath);opportunities=[row for row in records if'first_stage'in row]
    result={'schema':'DEE.PI08.C.actual_conditional_information_flow.R03','life_id':LIFE,'phase':args.fase,'status':'CLOSED_FINITE_PHASE'if closed and error is None else'STOPPED_PRESERVED','closed':closed,'error':error,
       'initial_tick':initial,'final_tick':final['physical']['tick'],'new_Native_ticks':final['physical']['tick']-initial,'finite_Native_bound':bound,'opportunities_completed':len(opportunities),
       'questions_scheduled':sum(row['first_stage']['sample_register']['question_scheduled']for row in opportunities),'questions_applied':sum(row['first_stage']['sample_register']['question_applied']for row in opportunities),
       'extra_bits_released':sum(row['first_stage']['sample_register']['question_applied_and_signature']for row in opportunities),'joint_useful':sum(not row['actual_failed']for row in opportunities),
       'records':records,'states':states,'intervals':intervals,'Native_inputs':{'unique_requested':len(ids),'status_counts':dict(totals)},'protected_before':protected,'protected_after':protected_after,
       'Native_budget_before':used,'worlds_before':lives,'no_adoption':True,'scope':'One bounded material flow experiment; Native choices/actualbytes retained, technicalbuffer explicit, no causal value-of-information or first-query-credit proof.'}
    with proof.open('x',encoding='utf8')as out:json.dump(result,out,ensure_ascii=False,indent=2);out.write('\n')
    if closed and marker.exists():marker.unlink()
    print(json.dumps({'status':result['status'],'proof':str(proof),'sha256':sha(proof),'closed':closed,'error':error,'opportunities':len(opportunities)},ensure_ascii=False))
    if error:raise SystemExit(1)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--sistema',required=True);parser.add_argument('--fase',choices=('preparar','evaluar'),required=True);parser.add_argument('--ejecutar',action='store_true');main(parser.parse_args())
