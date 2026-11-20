"""All routes used for every new scene, not host selection of the right memory."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,puente_lexico_10 as z,igualdad_fisica_03 as eq
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_BRIDGE11_full';life='ES01_INTEGRATED12_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'episodes':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'criteria_before':'Union of actually decoded tokens from all old phases and the new bridge. Unique expected token on trained±3/±5, indeterminate on untrained±1. Never choose a result from the correct environmental sign. Selective bus cut must spare older3relations.'}
sequence=[(5,5),(-3,3),(3,5),(-5,3),(5,3),(1,3),(-1,5),(-5,5),(3,3),(5,5),(-3,5),(5,3)]
def trial(x):
 if a.case in('cut_bus','sham_bus'):
  entry=e.prepare(x)['lexical_bridges_v10']['near5Bridge'];name=entry['ports']['cut'if a.case=='cut_bus'else'sham'];r=x.world.submit(name,0,x.tick+1);data['intervention']={'port':name,'id':int(r.id)}
 x.run_until(x.tick+2)
 for j,(k,load)in enumerate(sequence):
  row=e.produce_relations(x,frame='lexical05',bridge='near5Bridge',parameter=k,load=load);row['episode']=j+1;row['physical']=physical(x.world,occupation=True);data['episodes'].append(row)
  if j in(3,11):x.save(a.out/('T'+str(x.tick)+'.deetsnap.gz'))
 if'intervention'in data:data['intervention']['receipt']=exact_receipt(x.world.runtime.receipt(data['intervention']['id']))
 data['word_old']=f.query(x,frame='lexical05');data['word_bridge']=z.query(x,bridge='near5Bridge');data['comparison_forms']=e.query_words(x);data['contact']=e.contact_query(x,frame='contactoA');data['free']=e.contact_query(x,frame='freeRepair5');data['time']=e.temporal_query(x,frame='secuenciaA');data['equal']=eq.query(x);data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'responses':[{'parameter':r['ENTORNO']['actual_parameter'],'word':r['SPANISH_DECODED']}for r in data['episodes']],
  'old_lexicon':data['word_old']['SPANISH_DECODED'],'new_lexicon':data['word_bridge']['SPANISH_DECODED'],'comparisons':data['comparison_forms']['FORMAS_ACCESIBLES'],'contact':data['contact']['SPANISH_DECODED'],'free':data['free']['SPANISH_DECODED'],'equal':data['equal']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_CONNECTED_MULTI_ROUTE_CONTEXTUAL_WORD_USE12',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
