"""Frozen PI01 twelve-use panel on the one current PI02 candidate; author-only.

No world/module is opened at import. Root invokes freeze, then panel only after
the current complete R04 candidate is safely closed. No --nueva, old checkpoint,
teaching, fallback, implicit repair or resubmission exists in this script.
"""
from pathlib import Path
import argparse,ast,datetime,hashlib,json,os,sys

P=Path(__file__).resolve().parent.parent
LIFE='ECI02_PI02_MAIN'
PREFIX='PI02_RET_FINAL'
PROTOCOL=P/'control/PROTOCOLO_PANEL_RETENCION_PI02.json'
SUMMARY=P/'ensayos/RESUMEN_RETENCION_PI02.json'
PAUSE_HABITAT={'modo':'eci01-pi02-pausar-habitat'}
REFERENCE=P.parent/'PROGRESION_INTEGRADA_01/codigo/conservar_y_reabrir_R04.py'
PANEL=[
    ('luma',{'modo':'apd04-palabra','texto':'luma'},1),
    ('nara',{'modo':'apd04-palabra','texto':'nara'},-1),
    ('clasifica',{'modo':'apd04-palabra','texto':'clasifica'},-1),
    ('suma',{'modo':'apd04-palabra','texto':'suma'},1),
    ('alfa',{'modo':'memoria','operacion_memoria':'usar','contexto':'alfa'},-1),
    ('FIplus',{'modo':'eci01-balance','izquierda':14,'derecha':3},1),
    ('FIminus',{'modo':'eci01-balance','izquierda':2,'derecha':11},-1),
    ('FIzero',{'modo':'eci01-balance','izquierda':6,'derecha':6},0),
    ('number13',{'modo':'eci01-aritmetica-directa','operacion':'suma','izquierda':6,'derecha':7},13),
    ('number8',None,8),
    ('alfa_after',{'modo':'memoria','operacion_memoria':'usar','contexto':'alfa'},-1),
    ('luma_after',{'modo':'apd04-palabra','texto':'luma'},1),
]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sequence():return[{'label':label,'literal':literal,'auditor_only_expected':expected}for label,literal,expected in PANEL]
def response(result,label):
    row=result['result']['rows'][0]
    if label.startswith('FI'):return row['early_physical_choice']
    if label.startswith('number'):return row['numeric_result']
    if label.startswith('alfa'):row=row['result']['rows'][0]
    return row['reader']['formed_native_command']
def canonical_requests(result,label):
    row=result['result']['rows'][0]
    if label.startswith('FI'):return row['all_material_receipts']
    if label.startswith('number'):return row['native_operation']['native_trial']['requests']
    if label.startswith('alfa'):row=row['result']['rows'][0]
    return row['requests']
def count_receipts(items):
    records={}
    for item in items:
        receipt=item['receipt'];identifier=receipt['id']
        if type(identifier)is not int or identifier!=item['id']:raise ValueError('Exact receipt identity differs')
        if identifier in records and records[identifier]!=receipt:raise ValueError('Conflicting alias of Native receipt')
        records[identifier]=receipt
    statuses=[item['status']for item in records.values()]
    return {'requested_unique':len(records),'applied':sum(s=='applied'for s in statuses),'rejected':sum(s.startswith('rejected')for s in statuses),'pending_or_other':sum(s!='applied'and not s.startswith('rejected')for s in statuses),'native_ids':sorted(records)}
def write_summary(value):
    SUMMARY.parent.mkdir(parents=True,exist_ok=True)
    temp=SUMMARY.with_name(SUMMARY.name+'.writing')
    if temp.exists():raise ValueError('Prior partial summary write preserved; reconcile before continuing')
    with temp.open('x',encoding='utf-8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temp,SUMMARY)

def freeze():
    if PROTOCOL.exists():raise ValueError('Frozen panel exists; inspect/reuse it, never replace after observing answers')
    source=ast.parse(REFERENCE.read_text(encoding='utf-8-sig'))
    original=next(ast.literal_eval(node.value)for node in source.body if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PANEL'for t in node.targets))
    if original!=PANEL:raise ValueError('Twelve historical witnesses differ from the original PI01 panel')
    protocol={'schema':'PI02.twelve_use_retention.frozen.v1','frozen_utc':now(),'life':LIFE,'prefix':PREFIX,'script_sha256':sha(Path(__file__)),
        'source_protocol':{'path':str(REFERENCE),'sha256':sha(REFERENCE),'same_twelve_literals_expected_values_and_order':True},
        'sequence':sequence(),'requested_witnesses':12,'prelude':{'id':PREFIX+'_HABITAT_OFF','literal':PAUSE_HABITAT,'outside_panel_denominator':True,'required_ticks':0,'scope':'Operator disables the prepared external R04 bridge; Native itself continues normally during the panel. Absent habitat must be an explicit no-op; active/uncertain transactions must reject rather than be dropped.'},
        'chain':'number8 receives only the actual first Native numeric result of6+7 as its left operand, subtracting5. No expected13 fallback; if no integer is physically formed, stop at that point and preserve all performed/not-performed denominators.',
        'criterion':'12/12 concordant valid first responses, distinct material0 and NULL. Not a general cognitive PASS or a new acquisition claim.',
        'assistance':'Operator chooses fixed twelve uses, sequence and decoder. Generic queries are material. No teacher or return feedback; this is a representative conservation panel.',
        'stop':'Any uncertain/failed operation stops with its future preserved. No automatic retry, old-checkpoint restoration, repair, phase search or favourable reader replacement.'}
    PROTOCOL.parent.mkdir(parents=True,exist_ok=True);PROTOCOL.write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'frozen_protocol':str(PROTOCOL),'sha256':sha(PROTOCOL),'new_native_ticks':0},ensure_ascii=False))

def run():
    frozen=read(PROTOCOL)
    if frozen['life']!=LIFE or frozen['sequence']!=sequence()or frozen['script_sha256']!=sha(Path(__file__))or frozen['prelude']['literal']!=PAUSE_HABITAT:raise ValueError('Frozen panel/script/life mismatch')
    if SUMMARY.exists():raise ValueError('Panel already started; reconcile existing IDs/future instead of repeating it')
    # Existing supervised owner/queue, imported only when Root deliberately runs.
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from servicio_ensayo import Owner,append
    state={'schema':'PI02.retention_panel.progress.v1','life':LIFE,'protocol':str(PROTOCOL),'protocol_sha256':sha(PROTOCOL),'started_utc':now(),'no_teacher':True,'feedback':'omit','rows':[],'planned_witnesses':12,'prelude':None,'status':'RUNNING','scope':'Current continuous candidate; no old-cut panel or aggregate of branches.'}
    previous=None
    with Owner(LIFE,'PI02_RETENTION_FINAL')as owner:
        ids=[PREFIX+'_HABITAT_OFF']+[PREFIX+'_%02d_%s'%(i,label)for i,(label,_,_)in enumerate(PANEL)]
        if any(owner.q.get(identifier)is not None for identifier in ids):raise ValueError('A planned ID already exists; never submit it again under a new ID')
        try:
            prelude=owner.material(ids[0],PAUSE_HABITAT,feedback='omit')
            if prelude['before_tick']!=prelude['after_tick']:raise ValueError('Habitat disable unexpectedly advanced Native time; preserve and inspect')
            state['prelude']={'id':ids[0],'literal':PAUSE_HABITAT,'result':prelude,'before_tick':prelude['before_tick'],'after_tick':prelude['after_tick'],'prepared_external_apparatus_only':True,'not_a_learned_regulation_action':True}
            state['initial_tick']=prelude['after_tick'];write_summary(state)
            for index,(label,literal,expected)in enumerate(PANEL):
                actual=literal
                if actual is None:
                    if type(previous)is not int:
                        state.update(status='STOPPED_NO_FORMED_PREDECESSOR',stop_index=index,stop_reason='No actual Native integer from the preceding sum; expected13 is not supplied as fallback')
                        append({'kind':'PI02_PANEL_STOP','life':LIFE,'index':index,'reason':state['stop_reason']});break
                    actual={'modo':'eci01-aritmetica-directa','operacion':'diferencia','izquierda':previous,'derecha':5}
                result=owner.material(ids[index+1],actual,feedback='omit')
                value=response(result,label);valid=type(value)is int
                if label=='number13':previous=value
                counts=count_receipts(canonical_requests(result,label))
                entry={'index':index,'label':label,'id':ids[index+1],'literal':actual,'expected_auditor_only_after_decoding':expected,'response':value,'formed_valid':valid,'concordant':valid and value==expected,'before_tick':result['before_tick'],'after_tick':result['after_tick'],'native_denominators':counts,'primary':str(P/'ensayos'/(ids[index+1]+'.json'))}
                if state['rows']and entry['before_tick']!=state['rows'][-1]['after_tick']:raise ValueError('Panel Native history has a time gap; do not hide it')
                state['rows'].append(entry);state['final_tick']=entry['after_tick'];write_summary(state)
                print(json.dumps(entry,ensure_ascii=False),flush=True)
            else:state['status']='COMPLETED'
        except BaseException as exc:
            state.update(status='STOPPED_ERROR_FUTURE_PRESERVED',error=repr(exc),finished_utc=now());write_summary(state);raise
        finally:
            rows=state['rows'];allids=[n for row in rows for n in row['native_denominators']['native_ids']]
            state['denominators']={'planned':12,'material_panel_requests_completed':len(rows),'valid_responses':sum(row['formed_valid']for row in rows),'correct':sum(row['concordant']for row in rows),'incorrect':sum(row['formed_valid']and not row['concordant']for row in rows),'abstention':sum(not row['formed_valid']for row in rows),'not_performed':12-len(rows),'native_requested_unique':len(set(allids)),'native_applied':sum(row['native_denominators']['applied']for row in rows),'native_rejected':sum(row['native_denominators']['rejected']for row in rows),'pending_or_other':sum(row['native_denominators']['pending_or_other']for row in rows),'aliases_not_counted':len(allids)-len(set(allids)),'prelude_excluded':True}
            state['retention_criterion_met']=state['status']=='COMPLETED'and len(rows)==12 and all(row['concordant']for row in rows)
            state['finished_utc']=now();write_summary(state)
    state['owner_closed_coherently']=True;write_summary(state)
    print(json.dumps({'summary':str(SUMMARY),'life':LIFE,'status':state['status'],'denominators':state['denominators'],'criterion_met':state['retention_criterion_met'],'final_tick':state.get('final_tick')},ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=('freeze','panel'));args=parser.parse_args();{'freeze':freeze,'panel':run}[args.operation]()
