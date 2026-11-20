"""Revision4 early normalization before measured inherited barriers in the actual lived world, not a new N.

Two new contents are taught after route-strategy experience, then a generic
query accesses one. The native result teaches a simple B region and changes
a later consequence. All opportunities are scheduled before any readout.
Opaque content codes are not newly acquired NSM meanings.
"""
from pathlib import Path
import argparse,sys,json,gzip
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'),str(Path(__file__).parent)]
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,paisaje_causal_01 as pc
from instrumentos_pc01 import guard,receipts,frame,witness,sha
from avance_acotado import install
from dee_thinking.persistence import encode_metadata
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='E1_ACCESO_ADAPTATIVO_01';life='AA01_LOCAL25V4_'+a.case;before=s.record(parent);s.fork(parent,life,kind='CANDIDATE');S=[15,15,15];initial=-1 if'down'in a.case else 1;second=-initial;data={'case':a.case,'life':life,'parent':before,'source_sha256':sha(__file__),'prepared_policy_site':S,'external_contexts':[initial,second],'assistance':'Fixed small alternative geometry within the same N67lived world. Two native feedback outcomes revise the same support. New opposite content experiences follow revision; no content supplied with final query. Native selection is local, no host lookup or per-response reader choice. Opaque code is not new Spanish semantics.','requests':[]}
def trial(x):
    install(x,a.out,seconds=220);start=x.tick;data['epoch']=start;data['pre']=physical(x.world,occupation=True);training={};B={}
    def send(role,site,d,t,payload=0,sem=1):data['requests'].append(guard(x.world,'AA01.L25.'+role,site,start+t,direction=d,semantic=sem,payload=payload))
    def arrive(role,site,d,t,payload=0):send(role,e.move(site,d,-3),d,t-3,payload)
    for j in(-1,1):
        for r in(-1,1):
            E=e.move(e.move(S,(j,0,0),-10),(0,r,0),10);Q=e.move(E,(j,r,1),-4);H=e.move(Q,(0,0,1),-6);key=str(j)+','+str(r);training[key]={'j':j,'r':r,'outcome':E,'query':Q,'source':H}
            send('SUPPORT.'+key+'.pulse',e.move(Q,(1,0,0),6),(0,0,0),13,0,4);send('SUPPORT.'+key+'.feedback',e.move(E,(0,-r,-1),4),(0,0,0),16,0,4)
    for k,(offset,available)in enumerate(((0,initial),(67,second))):
        for key,z in training.items():
            r=z['r'];j=z['j'];tag=str(k)+'.'+key
            arrive('LEARN.'+tag+'.cue',z['source'],(-1,0,0),offset+3,5);arrive('LEARN.'+tag+'.sample',z['source'],(1,0,1),offset+3,11)
            if r!=available:send('ENV.'+tag,z['query'],(1,0,0),offset+8,3)
            arrive('EXPLORE.'+tag,z['query'],(j,r,0),offset+9,5)
            if not(k and'omit_feedback'in a.case):
                shift=1 if k and'unpaired'in a.case else 0
                arrive('FEEDBACK.'+tag+'.1',z['outcome'],(0,-r,-1),offset+13+shift,7);arrive('FEEDBACK.'+tag+'.2',z['outcome'],(0,-r,0),offset+13+shift,7)
    memories={str(r):e.move(S,(1,r,0),4)for r in(-1,1)};content={str(r):(r if'swap'in a.case else-r)for r in(-1,1)}
    for key,M in memories.items():
        if'no_content'not in a.case:arrive('NEW.'+key+'.cue',M,(-1,0,0),94,5);arrive('NEW.'+key+'.event',M,(1,0,content[key]),94,11)
    if'cut_policy'in a.case or'sham_policy'in a.case:
        for r in(-1,1):
            where=e.move(S,(0,r,0),2)
            if'sham_policy'in a.case:where=e.move(where,(1,0,0),12)
            send('POLICY_CUT.'+str(r),where,(0,0,0),91,0,4)
    if'cut_packet'in a.case or'sham_packet'in a.case:
        for key,M in memories.items():
            r=int(key)
            for z in(-1,1):
                where=e.move(M,(1,r,z),1)
                if'sham_packet'in a.case:where=e.move(where,(0,0,1),12)
                send('PACKET_CUT.'+key+'.'+str(z),where,(0,0,0),161,0,4)
    arrive('COMMON_QUERY',S,(1,0,0),157,5)
    for key,M in memories.items():
        r=int(key)
        for z in(-1,1):
            keyB=key+','+str(z);out=e.move(M,(1,r,z),2);hub=e.move(out,(0,0,z),4);effect=e.move(hub,(1,1,z),4);B[keyB]={'hub':hub,'effect':effect,'z':z,'source_outcome':out}
            arrive('B.NORMALIZE_X.'+keyB,out,(-1,0,0),163,0);arrive('B.NORMALIZE_Y.'+keyB,out,(0,-r,0),163,5);arrive('B.ACQUIRE.'+keyB,hub,(1,0,0),167,7);arrive('B.RECALL.'+keyB,hub,(0,1,0),234,7);arrive('B.USE.'+keyB,effect,(-1,-1,0),238,5)
    data['training_geometry']=training;data['new_content_inputs']=content;data['memory_geometry']=memories;data['B_geometry']=B;data['all_future_inputs_fixed_before_outcome']=True;data['samples']=[]
    with gzip.open(a.out/'CAMPOS_LOCALES.jsonl.gz','wt',encoding='utf8',compresslevel=9)as f:
        for relative in(22,23,89,90,94,156,157,161,162,163,164,165,167,233,234,237,238):
            x.run_until(start+relative);f.write(json.dumps(frame(x.world),separators=(',',':'))+'\n');row={'relative_tick':relative,'tick':x.tick,'policy':observe(x.world,S),'memories':{k:observe(x.world,M)for k,M in memories.items()},'B':{k:observe(x.world,item['effect']if relative in(237,238)else item['hub'])for k,item in B.items()}}
            if relative==161:row['memory_witnesses']={k:witness(x.world,M)for k,M in memories.items()}
            data['samples'].append(row)
            if relative==90:data['learned_state_complete']=x.save(a.out/'ESTRATEGIA_Y_CONTENIDOS_PENDIENTES_COMPLETOS.deetsnap.gz')
    data['policy_first']=data['samples'][1]['policy'];data['policy_second']=data['samples'][3]['policy'];data['B_recall']={k:row for k,row in data['samples'][-3]['B'].items()};data['B_use']={k:row for k,row in data['samples'][-1]['B'].items()};data['panel']={'less':e.context(x,value=64,method='B'),'more':e.context(x,value=117,method='B'),'near':pc.current_dose(x,parameter=3,load=4),'far':pc.current_dose(x,parameter=-3,load=6),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5')};data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime);x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.AA01.local25',encode_metadata({'epoch':start,'S':S,'training':training,'memories':memories,'B':B,'prepared_scaffold':True,'not_semantic_target_metadata':True}));return{'life':life,'tick':x.tick,'first':data['policy_first']['direction'],'second':data['policy_second']['direction'],'B_recall':{k:row['direction']for k,row in data['B_recall'].items()},'B_use':{k:row['direction']for k,row in data['B_use'].items()},'panel':{k:v.get('SPANISH_DECODED',v.get('TRADUCCION',{}).get('SPANISH_DECODED'))for k,v in data['panel'].items()}}
try:data['commit']=s.mutate(life,'AA01_ALTERNATIVE_SHORT_ACCESS_BEFORE_INHERITED_BARRIERS_25_V4',trial)
except Exception as error:
    data['failure']={'type':type(error).__name__,'detail':str(error)};data['reached_record']=s.record(life);raise
finally:
    with gzip.open(a.out/'PRIMARIOS.json.gz','wt',encoding='utf8',compresslevel=9)as f:json.dump(data,f,ensure_ascii=False,separators=(',',':'))
data['original_pointer_unchanged']=s.record(parent)==before;print(json.dumps(data.get('commit',{}).get('result',{}),ensure_ascii=False))
