"""Map the late current-event access, comparing fixed coordination orders."""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as lex,puente_lexico_10 as b,igualdad_fisica_03 as eq
from instrumentos_pc01 import Trace,witness,receipts,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='ES01_LATE_ACCESS29_passive';life='PC01_TARDIO08_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'criteria_before':'Compare fixed all-legacy-before-bridge, bridge-only reduced coupling, bridge-first recomposition and omission of bridgeA. Same actual+5load3, same stored learned state, no teacher token. Every decoder is unchanged and no route is selected from the answer. Bridge-only has fewer events and must not be called superior without the lost legacy domains. Four current physical scenes are not independent individuals.'}
def combine(legacy,alternative):
    words=sorted(set([r['text']for r in legacy['SPANISH_DECODED']]+alternative['SPANISH_DECODED']))
    return{'legacy':legacy,'alternative':alternative,'SPANISH_DECODED':words,'INSTRUMENTO':'Fixed coordination order, never chosen using a target or observed response.'}
def trial(x):
    data['pre']=physical(x.world,occupation=True);g=e.prepare(x);data['frame_geometry']=g['relational_words_v2']['lexical05'];data['bridge_geometry']=g['lexical_bridges_v10']['near5Bridge'];tr=Trace(x,a.out/'CAMPO_COMPLETO.jsonl.gz',start=x.tick,end=x.tick+360).install()
    if a.case=='bridge_first':
        alternative=b.context(x,bridge='near5Bridge',parameter=5,load=3,probe=False);legacy=lex.context(x,frame='lexical05',parameter=5,load=3,emit_word_queries=False);data['current']=combine(legacy,alternative)
    elif a.case=='bridge_only':
        alternative=b.context(x,bridge='near5Bridge',parameter=5,load=3,probe=False);data['current']=combine({'SPANISH_DECODED':[],'omitted_by_declared_profile':True},alternative)
    elif a.case in('all_current','bridge_no_A'):
        legacy=lex.context(x,frame='lexical05',parameter=5,load=3,emit_word_queries=False);alternative=b.context(x,bridge='near5Bridge',parameter=5,load=3,probe=False,event_a=a.case!='bridge_no_A');data['current']=combine(legacy,alternative)
    else:raise ValueError('Known bounded coordination arms only')
    data['after_current']=physical(x.world,occupation=True);data['trace']=tr.close();data['before_compatibility']=x.tick
    data['less']=e.context(x,value=67,method='B');data['more']=e.context(x,value=120,method='B');data['contact']=e.contact_query(x,frame='contactoA');data['free']=e.contact_query(x,frame='freeLate27');data['time']=e.temporal_query(x,frame='secuenciaA');data['equality_form']=eq.query(x);data['word_forms']=lex.query(x,frame='lexical05');data['bridge_form']=b.query(x,bridge='near5Bridge');data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'current_plus5':data['current']['SPANISH_DECODED'],'bus':data['current']['alternative']['ENTE']['normalized_current_bus'],'less':data['less']['TRADUCCION']['SPANISH_DECODED'],'more':data['more']['TRADUCCION']['SPANISH_DECODED'],'contact':data['contact']['SPANISH_DECODED'],'free':data['free']['SPANISH_DECODED'],'bridge_form':data['bridge_form']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'PC01_LATE_NATIVE_COUPLING_ARCHITECTURES08',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
