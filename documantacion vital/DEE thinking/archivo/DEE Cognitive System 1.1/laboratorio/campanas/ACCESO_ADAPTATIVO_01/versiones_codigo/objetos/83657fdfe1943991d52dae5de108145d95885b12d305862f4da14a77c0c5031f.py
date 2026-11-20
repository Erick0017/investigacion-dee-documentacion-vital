"""Directed passive replay of MAIN's already executed post-use interval.

Only the declared cut/sham adds matter. Baseline future inputs reproduce the
six old-function calls exactly. First departure from a simple Ztransport model
is saved with whole native pre/post state and radius3 context, not inferred by
unique inverse history. Native micro-checkpoints are diagnostic, not substitutes
for an operational owner snapshot/protocol call stack.
"""
from pathlib import Path
import argparse,sys,json,gzip,tempfile,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'),str(Path(__file__).parent)]
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,paisaje_causal_01 as pc
from instrumentos_pc01 import frame,witness,guard,receipts,sha,native_digest
from avance_acotado import install
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);source=a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01/MAIN_CONFIRMATORIO_36/main/PRIMARIOS.json.gz';ref=json.loads(gzip.decompress(source.read_bytes()));cut=next(q for q in ref['samples']if q['stage']=='use');parent=ref['life'];life='AA01_TRAZA_B39_'+a.case;before=s.record(parent);s.fork(parent,life,kind='DIAGNOSTIC_COPY',checkpoint=cut['record_snapshot']);expected=ref['commands'][17]['result']['physical'];data={'case':a.case,'life':life,'parent_current':before,'source_sha256':sha(__file__),'reference_primary_sha256':sha(source),'full_start_cut':cut['record_snapshot'],'full_start_cut_sha256':cut['record_snapshot_sha256'],'reference_end_before_first_late_B_question':expected,'requests':[],'trajectory':[],'coarse_global':[],'panel':{},'interpretation_scope':'Native transport-model departure plus causal cut/sham. Not a lineage claim from equal loads. No original target/ref/word is retaught.','no_added_audit_probes':True}
def keep_native(rt,name):
    with tempfile.TemporaryDirectory(prefix='aa01-micro-')as folder:
        p=Path(folder)/'native.deetsnap';rt.save_snapshot(str(p));b=p.read_bytes();out=a.out/(name+'.native.gz')
        with gzip.open(out,'wb',compresslevel=9)as f:f.write(b)
        return{'file':out.name,'compressed_sha256':sha(out),'uncompressed_sha256':hashlib.sha256(b).hexdigest(),'native_bytes':len(b),'not_a_complete_owner_continuation':True}
def trial(x):
    install(x,a.out,seconds=220);origin=[27,11,38];direction=(0,0,-1);epoch=x.tick;data['pre']=physical(x.world,occupation=True);data['origin']=origin;data['initial_read']=observe(x.world,origin)
    if a.case!='baseline':
        site=e.move(origin,direction,4)
        if a.case=='sham':site=e.move(site,(1,0,0),12)
        data['requests'].append(guard(x.world,'AA01.TRACE39.'+a.case,site,epoch+3,semantic=4,payload=0))
    original=x.run_until;departure=False
    def observed(target):
        nonlocal departure
        while x.tick<target:
            tick=x.tick;site=e.move(origin,direction,tick-epoch);nextsite=e.move(origin,direction,tick+1-epoch);pre_rt=x.world.runtime.fork()if not departure else None;pre_record=observe(x.world,site)
            original(tick+1);after_record=observe(x.world,nextsite)
            if not departure:
                data['trajectory'].append({'from_tick':tick,'source_position':site,'source':pre_record,'destination':after_record,'unique_lineage_not_assumed':True})
                if not e.valid(after_record,direction):
                    departure=True
                    from app.native_tools import observe as view
                    def context(rt,q):
                        from dee_thinking import _native as d
                        from dee_thinking.consolidated import exact_observation
                        return{'tick':int(rt.current_tick),'site':q,'radius':3,'records':[exact_observation(rt.observe(d.Coordinate(*[(q[i]+v[i])%67 for i in range(3)])))for v in((u,v,w)for u in range(-3,4)for v in range(-3,4)for w in range(-3,4))]}
                    data['first_transport_model_departure']={'tick':x.tick,'expected_next_site':nextsite,'before':context(pre_rt,nextsite),'after':witness(x.world,nextsite),'native_pre':keep_native(pre_rt,'ANTES_DESVIO'),'native_post':keep_native(x.world.runtime,'DESPUES_DESVIO'),'before_complete_fields':frame_from_rt(pre_rt),'after_complete_fields':frame(x.world)}
            if x.tick%32==0:data['coarse_global'].append(physical(x.world,occupation=True))
    def frame_from_rt(rt):
        class PassiveWorld:pass
        w=PassiveWorld();w.runtime=rt;return frame(w)
    x.run_until=observed
    try:
        for value in(73,121):data['panel'][str(value)]=e.context(x,value=value,method='B')
        data['panel']['near']=pc.current_dose(x,parameter=5,load=3);data['panel']['far']=pc.current_dose(x,parameter=-5,load=3);data['panel']['contact']=e.contact_query(x,frame='contactoA');data['panel']['free']=e.contact_query(x,frame='freeRepair5')
    finally:x.run_until=original
    data['post']=physical(x.world,occupation=True);data['post_frame']=frame(x.world);data['receipts']=receipts(x.world.runtime);data['same_reference_end_fields']={k:data['post'][k]==expected[k]for k in('tick','RAW_sha256','clocks_sha256')};return{'life':life,'tick':x.tick,'departure_tick':data.get('first_transport_model_departure',{}).get('tick'),'same_reference_end_fields':data['same_reference_end_fields'],'panel':{k:v.get('SPANISH_DECODED',v.get('TRADUCCION',{}).get('SPANISH_DECODED'))for k,v in data['panel'].items()}}
try:data['commit']=s.mutate(life,'AA01_DIRECTED_PASSIVE_REPLAY_AND_NATIVE_CUT_39',trial)
except Exception as error:
    data['failure']={'type':type(error).__name__,'detail':str(error)};data['reached_record']=s.record(life);raise
finally:
    with gzip.open(a.out/'PRIMARIOS.json.gz','wt',encoding='utf8',compresslevel=9)as f:json.dump(data,f,ensure_ascii=False,separators=(',',':'))
print(json.dumps(data.get('commit',{}).get('result',{}),ensure_ascii=False))
