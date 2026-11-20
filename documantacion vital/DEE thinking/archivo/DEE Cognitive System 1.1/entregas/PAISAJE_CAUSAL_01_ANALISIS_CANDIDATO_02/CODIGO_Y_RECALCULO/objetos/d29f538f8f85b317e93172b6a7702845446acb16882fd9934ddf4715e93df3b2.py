"""Reacquire a reference through real experience on the mapped/diverted life.

No word is retaught. Matched branches differ only in pairing or the R0 guard;
old spatial/contact/free functions and native communication stay in scope.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import paisaje_causal_01 as pc,espanol_funcional_01 as e,recuperacion_magnitud_26 as m,ensenanza_lexica_03 as f,igualdad_fisica_03 as eq
from instrumentos_pc01 import receipts,sha,witness
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_LIBRE24_divert';life='PC01_INTEGRACION25_'+a.case;s.fork(parent,life,kind='CANDIDATE')
spec={'paired_guard':('paired','on_route'),'paired_sham':('paired','sham'),'unpaired_guard':('unpaired','on_route'),'omitted_guard':('omitted','on_route')}[a.case]
data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'criteria_before':'Actualadditional86referenceexperience plus fixedformat5, paired/unpaired/omitted controls; onlynativeadmittedinputs. ExistingSpanishwordformsnotretaught. Comparisons61,119,70,120 thenpostdesign64,117, with actualspatialevents/contact/free and same-worldcodecommunication interleaved. P0protection, notacquiredstrategy. No target-conditionedselector.','magnitude':[],'spatial':[],'old':[]}
def old(x):return{'tick':x.tick,'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5')}
def trial(x):
    data['pre']=physical(x.world,occupation=True);data['new_experience']=m.reacquire(x,value=86,teaching=spec[0],guard=spec[1]);data['reference_context']=witness(x.world,[50,35,35],3);x.save(a.out/'NUEVA_REFERENCIA_COMPLETA.deetsnap.gz')
    for v in(61,119):data['magnitude'].append({'value':v,'reserved':False,'result':e.context(x,value=v,method='B')})
    for k,L in((-3,4),(5,6)):data['spatial'].append(pc.current_dose(x,parameter=k,load=L))
    data['old'].append(old(x))
    for v in(70,120):data['magnitude'].append({'value':v,'reserved':False,'result':e.context(x,value=v,method='B')})
    data['communication']=pc.communicate_existing_word(x,communication='PC01_integration25_receiver')
    for k,L in((3,2),(-5,4)):data['spatial'].append(pc.current_dose(x,parameter=k,load=L))
    for v in(64,117):data['magnitude'].append({'value':v,'reserved':True,'result':e.context(x,value=v,method='B')})
    data['old'].append(old(x));data['time_form']=e.temporal_query(x,frame='secuenciaA');data['equal_form']=eq.query(x);data['word_forms']=f.query(x,frame='lexical05');data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'magnitude':[[r['value'],r['result']['TRADUCCION']['SPANISH_DECODED']]for r in data['magnitude']],'spatial':[r['SPANISH_DECODED']for r in data['spatial']],'old':[{'contact':r['contact']['SPANISH_DECODED'],'free':r['free']['SPANISH_DECODED']}for r in data['old']],'B_words':data['communication']['B_WORDS_DECODED']}
data['commit']=s.mutate(life,'PC01_REFERENCE_REACQUISITION_WITH_SPATIAL_SOCIAL_CONTINUITY25',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
