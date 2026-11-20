"""Same recovery opportunities for opposite learned physical word codes.
No result-dependent reader selection; old prepared-X limitation is tested.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f
from instrumentos_pc01 import guard,receipts,witness,frame,sha
import gzip
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_CONTINUIDAD28_far_guard';life='AA01_CONTENIDO01_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'frozen_design':'All histories use the same +XY zero-load prepared reader and +Y later query. Opposite teacher signals are used only during acquisition. No target-dependent repair or decoder. Native code recall is not spatial truth.','requests':[]}
def word(row):return ['cerca'if row['direction'][0]>0 else'lejos']if e.valid(row,(1,1,1))or e.valid(row,(-1,1,1))else[]
def trial(x):
    data['pre']=physical(x.world,occupation=True);data['initial_field']=frame(x.world)
    data['lesson']=f.teach(x,frame='lexical05',parameter=1,word='lejos'if a.case=='minus'else'cerca',phase_shift=12,load=3,signal=a.case!='no_word',event_a=a.case!='no_A')
    trace=gzip.open(a.out/'CAMPOS_RECUPERACION.jsonl.gz','xt',encoding='utf8',compresslevel=6)
    for tick in range(x.tick,39845):
        x.run_until(tick)
        if tick>=39822:trace.write(json.dumps(frame(x.world),separators=(',',':'))+'\n')
        if tick==39823:data['first_association']={b['id']:observe(x.world,b['hub'])for b in e.prepare(x)['relational_words_v2']['lexical05']['banks']}
        if tick==39835:data['pre_transform']=witness(x.world,[57,10,35])
        if tick==39836:data['after_transform']=observe(x.world,[57,10,35]);data['post_transform']=witness(x.world,[57,10,35])
        if tick==39837:data['requests'].append(guard(x.world,'AA01.COMMON.READER',[54,15,43],39841,direction=(1,1,0),payload=0))
    trace.close();data['reader']=observe(x.world,[57,18,43]);data['SPANISH_DECODED']=word(data['reader']);data['first_complete_state']=x.save(a.out/'PRIMERA_RECUPERACION_COMPLETA.deetsnap.gz')
    data['later']=[]
    for target in(39911,39978):
        data['requests'].append(guard(x.world,'AA01.COMMON.QUERY.'+str(target),[57,15,43],target-3,direction=(0,1,0),payload=7));x.run_until(target);row=observe(x.world,[57,18,43]);data['later'].append({'read':row,'SPANISH_DECODED':word(row)})
    data['old_after']={'less':e.context(x,value=64,method='B'),'more':e.context(x,value=117,method='B'),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5')};data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'first':data['SPANISH_DECODED'],'later':[r['SPANISH_DECODED']for r in data['later']],'old_words':[v.get('SPANISH_DECODED',v.get('TRADUCCION',{}).get('SPANISH_DECODED'))for v in data['old_after'].values()]}
data['commit']=s.mutate(life,'AA01_COMMON_READER_OPPOSITE_CONTENTS_01',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
