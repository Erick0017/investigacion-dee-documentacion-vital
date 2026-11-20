"""Recover use from a transformed influence instead of assuming it is waste.

Fixed prospective reader after the observed XYZ11/-XYZ120 -> YZ131
encounter. It introduces native material, not a passive reclassification.
No teacher is reintroduced after that transformation and no audit target
selects the route. Event/word omissions and off-route sham are explicit.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import paisaje_causal_01 as pc,espanol_funcional_01 as e,ensenanza_lexica_03 as f
from instrumentos_pc01 import guard,receipts,sha,witness
from dee_thinking.persistence import encode_metadata
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_CONTINUIDAD28_far_guard';life='PC01_TRANSFORMADO41_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'requests':[],'scope_before':'Fixednativepost-transformreaderat57,18,43tick39844. Supply+XYzero from54,15,43tick39841, orsamepulse+9Ysham. Expectednormalizerisnotqualifiedwithoutcausalnewwordhistory: no-word/no-Acontrolskeepallotheropportunities. Preparedactionpulse-XY7from64,25,47tick39845canjoinatrecoveredXYZroute61,22,47tick39848. NoPythonword-basedactuation. Read-onlyarmomitsactionandtestsanother67tickreturnwith+Y7probe. Narrowcoderecovery/use, notautomaticrecoveryofspatialsemantics orP2.'}
def trial(x):
    data['pre']=physical(x.world,occupation=True);data['lesson']=f.teach(x,frame='lexical05',parameter=1,word='cerca',phase_shift=12,load=3,signal=a.case!='no_word',event_a=a.case!='no_A')
    x.run_until(39835);data['pre_transformation']=witness(x.world,[57,10,35],3);x.run_until(39836);data['transformed']=observe(x.world,[57,10,35]);data['post_transformation']=witness(x.world,[57,10,35],3)
    req=guard(x.world,'PC01.POST41.NORMALIZE',[54,24 if a.case=='sham'else 15,43],39841,direction=(1,1,0),semantic=1,payload=0);data['requests'].append(req)
    if a.case!='read_only':data['requests'].append(guard(x.world,'PC01.POST41.ACTION',[64,25,47],39845,direction=(-1,-1,0),semantic=1,payload=7))
    x.run_until(39843);data['pre_reader']=witness(x.world,[57,18,43],3);x.run_until(39844);data['reader']=observe(x.world,[57,18,43]);data['post_reader']=witness(x.world,[57,18,43],3);data['SPANISH_DECODED']=['cerca'if data['reader']['direction'][0]>0 else'lejos']if e.valid(data['reader'],(1,1,1))or e.valid(data['reader'],(-1,1,1))else[]
    if a.case=='read_only':
        data['requests'].append(guard(x.world,'PC01.POST41.LATER_QUERY',[57,15,43],39908,direction=(0,1,0),semantic=1,payload=7));x.run_until(39911);data['later_read']=observe(x.world,[57,18,43]);data['LATER_SPANISH_DECODED']=['cerca']if e.valid(data['later_read'],(1,1,1))else[]
    else:x.run_until(39848);data['action']=observe(x.world,[61,22,47]);data['NATIVE_ACTION_OBSERVED']=e.valid(data['action'],(0,0,1))
    x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.PC01.transformed_reader41',encode_metadata({'schema':'PC01.post_transform.native_reader.v1','reader_site':[57,18,43],'phase':39844%67,'original_frame':'lexical05','new_context':1,'prepared_normalizer':True,'action_consumptive':a.case!='read_only','not_endogenous_access_choice':True}));x.save(a.out/'LECTOR_TRANSFORMADO_ESTADO_COMPLETO.deetsnap.gz')
    data['old_after']={'less':e.context(x,value=64,method='B'),'more':e.context(x,value=117,method='B'),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5')};data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'transformed':data['transformed'],'reader':data['reader'],'words':data['SPANISH_DECODED'],'action':data.get('NATIVE_ACTION_OBSERVED'),'later_words':data.get('LATER_SPANISH_DECODED'),'less':data['old_after']['less']['TRADUCCION']['SPANISH_DECODED'],'more':data['old_after']['more']['TRADUCCION']['SPANISH_DECODED'],'contact':data['old_after']['contact']['SPANISH_DECODED'],'free':data['old_after']['free']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'PC01_POST_TRANSFORMED_INFLUENCE_NATIVE_READER41',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
