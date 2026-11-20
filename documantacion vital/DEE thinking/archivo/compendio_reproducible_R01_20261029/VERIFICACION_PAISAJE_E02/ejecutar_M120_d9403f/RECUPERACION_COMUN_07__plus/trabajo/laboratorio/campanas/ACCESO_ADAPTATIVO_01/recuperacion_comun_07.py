"""Prospective common old+alternate recovery, without re-teaching content.

All future access resources are fixed before the first reading. The fixed
alternative X contribution is explicit. Opposite codes can follow physically
different retained routes; neither the observer nor a target selects one.
"""
from pathlib import Path
import argparse,sys,json,gzip
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f
from instrumentos_pc01 import guard,receipts,sha,witness,frame
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_CONTINUIDAD28_far_guard';life='AA01_RECUPERACION07_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'frozen_before':'All six historical banks and one fixed alternative get common opportunities, independent of their response. Old query39890precedes alternate39911. No word, correct reference or learned fields are supplied after acquisition. The alternate contributes fixedX, not a reconstruction of arbitrary erased content. Native use cancelsYwiththe same resource for both possible Xsigns.','requests':[]}
def decode(row):return ['cerca'if row['direction'][0]>0 else'lejos']if e.valid(row,(1,1,1))or e.valid(row,(-1,1,1))else[]
def act(row):return row['state']==1 and row['semantic']==1 and abs(row['direction'][0])==1 and row['direction'][1:]==[0,1]
def trial(x):
    data['pre']=physical(x.world,occupation=True);data['lesson']=f.teach(x,frame='lexical05',parameter=1,word='lejos'if'minus'in a.case else'cerca',phase_shift=12,load=3,signal='no_word'not in a.case,event_a='no_A'not in a.case);entry=e.prepare(x)['relational_words_v2']['lexical05'];data['acquired_before_access']=data['lesson']['ENTE']['post_signal'];data['acquisition_tick']=x.tick
    def send(name,site,d,t,load):data['requests'].append(guard(x.world,'AA01.R07.'+name,site,t,direction=d,semantic=1,payload=load))
    def arrive(name,site,d,t,load):send(name,e.move(site,d,-3),d,t-3,load)
    if'no_old_query'not in a.case:
        for bank in entry['banks']:arrive('OLD.'+bank['id'],bank['hub'],(0,1,0),39890,7)
    if'old_only'not in a.case:
        send('ALTERNATE',[54,24 if'alt_sham'in a.case else 15,43],(1,1,0),39908,0)
    outputs={}
    if'read_only'not in a.case:
        for bank in entry['banks']:
            for sign in(-1,1):
                site=e.move(bank['hub'],(sign,1,1),4);outputs['old.'+bank['id']+'.'+str(sign)]=site;arrive('USE.OLD.'+bank['id']+'.'+str(sign),site,(0,-1,0),39894,7)
        for sign in(-1,1):
            site=e.move([57,18,43],(sign,1,1),4);outputs['alternate.'+str(sign)]=site;arrive('USE.ALT.'+str(sign),site,(0,-1,0),39915,7)
    data['all_access_inputs_scheduled_before_first_read']=True
    x.run_until(39835);data['pre_transform']=witness(x.world,[57,10,35]);x.run_until(39836);data['same_old_collision_site']=observe(x.world,[57,10,35]);data['opposite_path_site']=observe(x.world,[31,10,35]);data['before_first_query']=x.save(a.out/'AVANCE_SIN_SONDAS_HASTA_39836_COMPLETO.deetsnap.gz')
    x.run_until(39890);data['old_reader']={b['id']:observe(x.world,b['hub'])for b in entry['banks']};data['old_words']=sorted(set(w for row in data['old_reader'].values()for w in decode(row)));data['after_old_complete']=x.save(a.out/'DESPUES_LECTOR_ANTIGUO_COMPLETO.deetsnap.gz');x.run_until(39894);data['old_actions']={key:observe(x.world,site)for key,site in outputs.items()if key.startswith('old.')}
    x.run_until(39910);data['pre_alternate']=witness(x.world,[57,18,43]);x.run_until(39911);data['alternate_reader']=observe(x.world,[57,18,43]);data['alternate_words']=decode(data['alternate_reader']);x.run_until(39915);data['alternate_actions']={key:observe(x.world,site)for key,site in outputs.items()if key.startswith('alternate.')};data['union_words']=sorted(set(data['old_words']+data['alternate_words']));data['native_use']={'old':[key for key,row in data['old_actions'].items()if act(row)],'alternate':[key for key,row in data['alternate_actions'].items()if act(row)]};data['complete_after_recovery']=x.save(a.out/'RECUPERACION_Y_USO_COMPLETO.deetsnap.gz')
    data['old_after']={'less':e.context(x,value=64,method='B'),'more':e.context(x,value=117,method='B'),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5')};data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime);return{'life':life,'tick':x.tick,'old_words':data['old_words'],'alternate_words':data['alternate_words'],'union':data['union_words'],'native_use':data['native_use'],'other_words':[r.get('SPANISH_DECODED',r.get('TRADUCCION',{}).get('SPANISH_DECODED'))for r in data['old_after'].values()]}
data['commit']=s.mutate(life,'AA01_COMMON_ACCESS_WITHOUT_CONTENT_RETEACHING_07',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
