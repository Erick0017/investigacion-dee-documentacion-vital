"""Natural coalescence of two acquired loads, common access, explicit re-teaching.

No state edits. Only documentary life metadata is erased on non-evolved
serialization copies when testing equality, never on a living participant.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'))
from app.lives import Store
from app.native_tools import physical,observe,SYSTEM_KEY
from app.process_control import protect_current
from instrumentos_pc01 import guard,receipts,sha,witness,native_digest
from agenda_binaria_pc01 import queue_state
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);life='AA01_PERDIDA13_'+a.case;s.create(life,'fisica_directa',{'N':17});content=17 if'17'in a.case else 11
data={'case':a.case,'life':life,'source_sha256':sha(__file__),'initial_external_content':content,'type':'AuxiliaryN17knowntransportandoccupieddestination; not E1 knowledge','decoder_fixed_before':'state1SEM1direction[1,1,0],Sreg16->opaqueA,Sreg22->opaqueB; all other states abstain. Not NSM semantic acquisition.','requests':[]}
def decode(row):return 'opaqueA'if row['state']==1 and row['semantic']==1 and row['direction']==[1,1,0]and row['s_reg']==16 else'opaqueB'if row['state']==1 and row['semantic']==1 and row['direction']==[1,1,0]and row['s_reg']==22 else None
def trial(x):
    data['pre']=physical(x.world);wall=[8,12 if'sham'in a.case else 3,3]
    if'no_wall'not in a.case:data['requests'].append(guard(x.world,'AA01.LOSS.WALL',wall,0,semantic=4,payload=0))
    if'no_history'not in a.case:data['requests'].append(guard(x.world,'AA01.LOSS.CONTENT',[3,3,3],0,direction=(1,0,0),semantic=1,payload=content))
    data['requests'].append(guard(x.world,'AA01.LOSS.COMMON_QUERY',[13,0,3],7,direction=(0,1,0),semantic=1,payload=5))
    x.run_until(4);data['pre_absorption']=witness(x.world,[8,3,3]);x.run_until(5);data['post_absorption']=witness(x.world,[8,3,3]);x.run_until(6);data['after6']=physical(x.world);data['queue6']=queue_state(x.world.runtime);data['all_native_after6']=native_digest(x.world.runtime);copy=x.world.runtime.fork();copy.erase_snapshot_metadata(SYSTEM_KEY);data['native_after6_excluding_only_documental_life']=native_digest(copy);data['complete6']=x.save(a.out/'ESTADO_COMPLETO_DESPUES_6.deetsnap.gz')
    x.run_until(10);data['read']=observe(x.world,[13,3,3]);data['decoded']=decode(data['read']);data['after10']=physical(x.world)
    copy=x.world.runtime.fork();copy.erase_snapshot_metadata(SYSTEM_KEY);data['native_after10_excluding_only_documental_life']=native_digest(copy)
    if'relearn'in a.case:
        data['explicit_relearning_supplies_the_content_again']=True
        data['requests'].append(guard(x.world,'AA01.LOSS.EXPLICIT_RETEACH',[3,8,3],12,direction=(1,0,0),semantic=1,payload=content));data['requests'].append(guard(x.world,'AA01.LOSS.NEW_QUERY',[13,5,3],19,direction=(0,1,0),semantic=1,payload=5));x.run_until(22);data['relearned_read']=observe(x.world,[13,8,3]);data['relearned_decoded']=decode(data['relearned_read'])
    data['receipts']=receipts(x.world.runtime);data['post']=physical(x.world);return{'life':life,'tick':x.tick,'read':data['decoded'],'relearned':data.get('relearned_decoded'),'causal_state6':data['native_after6_excluding_only_documental_life']}
data['commit']=s.mutate(life,'AA01_NATURAL_CONTENT_LOSS_AND_EXPLICIT_RELEARNING_13',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
