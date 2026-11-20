"""Four prospective isolated-world diagnostics of the archived fi60_00413.

Does not instantiate a life, call Store, mutate MAIN, access SQLite or run a
worker. The same complete prefix and future are used; interventions are legal
inputs only. Raw128 after the same passive delay is fixed before observation.
"""
from __future__ import annotations
import gc,gzip,hashlib,importlib.util,json,os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from arbol_umbral_adquirido_b01 import internal_A_close,native_imports,memory_guard
from ensayar_arbol_b05_r1 import dump,sha
LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01'
OUT=EV/'servicio/AUTOPSIA_FASE_R15'
SOURCE=SYSTEM/'estado/checkpoints/MU_MAIN.T62525.25da49a2c759.deetsnap.gz'
EXPECTED='686e22bcb58d5e32368fe4af6e58cc848209fbda3afb5ffc09606ea64da8f8eb'
ORIGINAL_AFTER=SYSTEM/'estado/checkpoints/MU_MAIN.T62564.20823c9e8739.deetsnap.gz'
ORIGINAL_AFTER_SHA='b926a52a66ff0b54433c1c35422c57b8a811d445c2a886e1d24df4ead35b425a'
LABELS=['real','no_datum','sham_datum','no_query']
SHAM=(14,15,23);SHAM_NAME='FI01.R15.sham.scalar29'
E=(15,15,15);S=(14,15,16);A=(14,14,15);B=(16,14,15)
FROZEN=EV/'servicio/SERVICIO_60MIN_FINAL_R11/codigo/capacidades'

def load_observer():
    p=SYSTEM/'capacidades/observador_causal_retrospectivo_01.py'
    sp=importlib.util.spec_from_file_location('pure_R15_observer',p)
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def agenda(observer,path):
    s=observer.Snapshot(path);o=observer.organization(s)
    return {'summary':s.summary(),'channels':s.channels,'pending':s.pending,
      'receipts':s.receipts,'next_event_id':s.next_event_id,'next_sequence':s.next_sequence,
      'owner_protocols':o['protocols'],'owner_interfaces':o['recipe']['interfaces'],
      'metadata':{k:v for k,v in s.metadata.items()if not k.startswith('dee_thinking.organizational.v1.')},
      'scope':'Complete snapshot stays local. Metadata is provenance/operational state, never an input to the native reader.'}

def main():
    if OUT.exists():raise FileExistsError('Preserve previous execution; no implicit replay: '+str(OUT))
    auth=internal_A_close(LAB/'CIERRE_INTERNO_A.json')
    if sha(SOURCE)!=EXPECTED or sha(ORIGINAL_AFTER)!=ORIGINAL_AFTER_SHA:raise ValueError('Explicit complete historical sources differ')
    for name in('mente_unificada_01.py','percepcion_cruda_fi01.py','selector_acrecion_nativo.py'):
        # The exact running service implementations, not a subtly edited reader.
        if sha(SYSTEM/'capacidades'/name)!=sha(FROZEN/name):raise ValueError('Frozen/current scientific implementation differs: '+name)
    ob=load_observer();p=ob.Snapshot(SOURCE);owner=ob.organization(p)
    if p.tick!=62525 or p.N!=67 or p.pending or owner['protocols']:raise ValueError('Not the complete empty-queue source')
    if int(p.observation(list(SHAM))['raw'])!=0:raise ValueError('Prospective sham site contains causal RAW; never clear')
    vector=[0]*128;vector[0]=19;vector[2]=2
    protocol={'schema':'FI01.autopsy.R15.prospective','authorization':auth,'code_sha256':sha(__file__),
      'source':str(SOURCE),'source_sha256':EXPECTED,'original_after':str(ORIGINAL_AFTER),'original_after_sha256':ORIGINAL_AFTER_SHA,
      'original_before_tick':62525,'diagnostic_prefix_idle_ticks':23,'schedule':{'start':62548,'query':62556,'scalar_or_sham':62559,'fixed_read':62562,'end':62564,'passive_end':62698},
      'arms':{'real':'Three query pulses + S29','no_datum':'Same three query pulses, datum omitted','sham_datum':'Same three query pulses +29 at legal peripheral sham','no_query':'S29 only; all three query pulses omitted'},
      'common_sham_interface':{'name':SHAM_NAME,'site':list(SHAM),'direction':[0,0,0],'state':1,'semantic':1,'registered_in_every_arm':True},
      'common_future_raw128':{'components':vector,'begin':62698,'reader':'Existing six fixed MU.current classes at q+6','expected_time':{'leaf':62700,'query':62754,'datum':62757,'read':62760,'end':62896}},
      'relevant_phase_candidate':62560,'future_no_external_workers':True,'no_Main_Store_SQLite_or_life_import':True,
      'units':'Four dependent forks of one actual past, not four independent learners.',
      'dependency_hashes':{name:sha(SYSTEM/'capacidades'/name)for name in('mente_unificada_01.py','percepcion_cruda_fi01.py','selector_acrecion_nativo.py','observador_causal_retrospectivo_01.py')},
      'cautions':['Ablations change dose; sham preserves scalar dose but not its anatomical neighborhood.','An empty fixed reader alone does not imply erased content.','A service-epoch metadata copy is not an independently resumed service journal.']}
    dump(OUT/'PROTOCOLO.json',protocol)
    dump(OUT/'FUENTE_AGENDA.json.gz',agenda(ob,SOURCE))
    # Only now import the official engine. Pure source checks above executed zero ticks.
    os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    ni=native_imports();d,encode,decode,Store,Adapter,now,physical,body,ep=ni
    from dee_thinking.persistence import load_world_snapshot
    from capacidades import mente_unificada_01 as mu,percepcion_cruda_fi01 as raw,selector_acrecion_nativo as sel
    summaries=[]
    for label in LABELS:
        memory_guard();world,_=load_world_snapshot(SOURCE);a=Adapter(world);del world
        initial=physical(a.world,occupation=True)
        if initial['RAW_sha256']!=p.summary()['RAW_sha256']:raise ValueError('Restoration differs from source physical RAW')
        raw.declare(a,SHAM_NAME,SHAM,(0,0,0))
        rows=[];saved=[]
        def save(tag):
            path=OUT/'snapshots'/(label+'_'+tag+'.deetsnap.gz');path.parent.mkdir(parents=True,exist_ok=True);a.save(path)
            saved.append({'tag':tag,'tick':a.tick,'path':str(path),'sha256':sha(path)})
        def capture(tag):
            pts={'E':E,'S':S,'A':A,'B':B,'sham':SHAM,'neutral_first_step':(15,16,14),'neutral_axial_first_step':(15,16,15)}
            pts.update({'around.'+'.'.join(map(str,delta)):tuple((E[i]+delta[i])%67 for i in range(3))for delta in __import__('itertools').product(range(-3,4),repeat=3)})
            rows.append({'tag':tag,'tick':a.tick,'physical':physical(a.world,occupation=True),'fields':{k:mu.observation(a,v)for k,v in pts.items()}})
        save('62525_COMMON');a.run_until(62548);capture('before_protocol')
        rs=[]
        # Preserve original submission order: datum first, then three generic queries.
        if label in('real','no_query'):rs.append(raw.submit(a,'MU.current.datum',S,(0,0,0),62559,29))
        elif label=='sham_datum':rs.append(raw.submit(a,SHAM_NAME,SHAM,(0,0,0),62559,29))
        if label!='no_query':rs.extend(sel.query(a.world,62556,5,'MU.selector'))
        save('62548_QUEUED')
        answer=None
        for t in range(62554,62565):
            memory_guard();a.run_until(t);capture('phase_window')
            if t==62562:answer=mu.current_read(a)
        receipts=raw.receipts(a,rs);save('62564_POST')
        post=physical(a.world,occupation=True)
        a.run_until(62698);memory_guard();capture('after_passive_2N');save('62698_PASSIVE')
        common=raw.frame(a,vector,detailed=True);memory_guard();save('62896_COMMON_RAW128')
        result={'arm':label,'initial':initial,'requests':receipts,'phase_frames':rows,'fixed_scalar_reader':answer,'phase_post':post,
          'common_raw128':common,'snapshots':saved,'final':physical(a.world,occupation=True),'peak_bytes':memory_guard(),
          'isolation':'World only from explicit complete snapshot; no Store mutation, external process or service journal is run.'}
        dump(OUT/(label+'.json.gz'),result)
        summaries.append({'arm':label,'scalar_choice':answer['choice'],'common_choice':common['reader']['choice'],
          'references_after_scalar':[row for row in rows if row['tick']==62564][0]['fields'],
          'references_before_common':common['references_pre'],'references_after_common':common['references_after'],
          'requests':len(receipts),'applied':sum(r['receipt']['status']=='applied'for r in receipts),'end_tick':a.tick,'snapshots':saved})
        print(json.dumps({'arm':label,'scalar_choice':answer['choice'],'common_choice':common['reader']['choice'],'end_tick':a.tick}),flush=True)
        del a,result,rows,common;gc.collect();memory_guard()
    dump(OUT/'RESUMEN.json',{'protocol_sha256':sha(OUT/'PROTOCOLO.json'),'arms':summaries,'source_unchanged':sha(SOURCE)==EXPECTED,'original_after_unchanged':sha(ORIGINAL_AFTER)==ORIGINAL_AFTER_SHA})
    # Passive parse/export only, after all native worlds have been released.
    for label in LABELS:
        for tag in('62525_COMMON','62548_QUEUED','62564_POST','62698_PASSIVE','62896_COMMON_RAW128'):
            path=OUT/'snapshots'/(label+'_'+tag+'.deetsnap.gz')
            dump(OUT/'agendas'/(label+'_'+tag+'.json.gz'),agenda(ob,path))
    comparisons={}
    for tag in('62525_COMMON','62564_POST','62698_PASSIVE','62896_COMMON_RAW128'):
        ss={label:ob.Snapshot(OUT/'snapshots'/(label+'_'+tag+'.deetsnap.gz'))for label in LABELS}
        comparisons[tag]={label:ob.compare(ss['real'],ss[label],sample_limit=300)for label in LABELS[1:]}
        if tag=='62564_POST':comparisons[tag]['original_vs_real']=ob.compare(ob.Snapshot(ORIGINAL_AFTER),ss['real'],sample_limit=300)
        for label,s in ss.items():
            for field,arr in(('RAW',s.raw),('clocks',s.clocks)):
                b=ob.pbytes(arr);key=ob.sha(b);f=OUT/'fields'/(key+'.u64le.gz');f.parent.mkdir(parents=True,exist_ok=True)
                if not f.exists():
                    with f.open('xb')as w:
                        with gzip.GzipFile(filename='',fileobj=w,mode='wb',mtime=0)as z:z.write(b)
        del ss;gc.collect()
    dump(OUT/'COMPARACIONES_COMPLETAS.json.gz',comparisons)
    print(json.dumps({'output':str(OUT),'complete':True,'four_world_diagnostics':True,'MAIN_advanced':False}),flush=True)

if __name__=='__main__':main()
