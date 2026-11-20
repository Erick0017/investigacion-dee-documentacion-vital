"""Continue a full lived E1+B state; test common opposite-content recovery.

No target word, numeric reference, old snapshot or teaching content is supplied.
The alternate contributes X/Y only. The received Z content must come from B.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
from instrumentos_pc01 import guard,receipts,sha,witness
from dee_thinking.persistence import decode_metadata,encode_metadata
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='AA01_CONECTADO10_initialdown_r1'if'down'in a.case else'AA01_CONECTADO10_initialup_r1';life='AA01_RECEPTOR14_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'design_before':'Four fixed old Bports and four post-use effects are queried equally. Same+XYresource supplied independent of code; Zsign is not supplied. Old-reader failure and alternative recovery are separated. Source content cut/sham occurs only on the declared Bpost-use routes. This is received-code recovery, not a new magnitude judgment.','requests':[]}
def decode(row):return 'menos'if e.valid(row,(1,1,-1))else'más'if e.valid(row,(1,1,1))else None
def trial(x):
    data['pre']=physical(x.world,occupation=True);meta=decode_metadata(dict(x.world.runtime.snapshot_metadata_entries)['DEE.Cognitive.System.1.1.AA01.connected10']);B=meta['B'];goal=meta['goal_tick'];old=e.tick_at_or_after(x.tick,phase=(goal+71)%67,lead=8);target=old+4;data['calendar']={'old_query':old,'alternative':target,'parent_goal':goal};data['prepared_B']=B
    def send(name,site,d,t,payload=7,semantic=1):data['requests'].append(guard(x.world,'AA01.R14.'+name,site,t,direction=d,semantic=semantic,payload=payload))
    for key,item in B.items():
        send('OLD.'+key,e.move(item['hub'],(0,1,0),-3),(0,1,0),old-3)
        if'cut'in a.case or'sham'in a.case:
            site=e.move(item['effect'],(0,0,item['z']),-6)
            if'sham'in a.case:site=e.move(site,(1,0,0),12)
            send('B_CONTENT_CUT.'+key,site,(0,0,0),target-7,0,4)
        if'old_only'not in a.case:send('ALTERNATIVE.'+key,e.move(item['effect'],(1,1,0),-3),(1,1,0),target-3,7)
    data['all_future_accesses_fixed_before_old_read']=True;x.run_until(old);data['old_reads']={key:observe(x.world,item['hub'])for key,item in B.items()};data['old_decoded']=sorted(set(d for row in data['old_reads'].values()if(d:=decode(row))is not None));x.run_until(target-1);data['pre_alternative_witness']={key:witness(x.world,item['effect'])for key,item in B.items()};x.run_until(target);data['recovered_reads']={key:observe(x.world,item['effect'])for key,item in B.items()};data['recovered_decoded']=sorted(set(d for row in data['recovered_reads'].values()if(d:=decode(row))is not None));data['first_recovery_complete']=x.save(a.out/'RECUPERACION_RECEPTOR_COMPLETA.deetsnap.gz')
    data['new_experience']=e.context(x,value=70,method='B');later=e.tick_at_or_after(x.tick,phase=target%67,lead=3)
    for key,item in B.items():send('LATER.'+key,e.move(item['effect'],(0,1,0),-3),(0,1,0),later-3,7)
    x.run_until(later);data['later_reads']={key:observe(x.world,item['effect'])for key,item in B.items()};data['later_decoded']=sorted(set(d for row in data['later_reads'].values()if(d:=decode(row))is not None));data['receipts']=receipts(x.world.runtime);data['post']=physical(x.world,occupation=True)
    x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.AA01.B_recovery14',encode_metadata({'B':B,'phase':target%67,'old_phase':old%67,'no_Z_content_supplied':True,'reader_inputs_are_prepared_not_self_selected':True}));return{'life':life,'tick':x.tick,'old':data['old_decoded'],'recovered':data['recovered_decoded'],'later':data['later_decoded'],'new_experience_words':data['new_experience']['TRADUCCION']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'AA01_COMMON_RECOVERY_OF_RECEIVED_Z_CONTENT_14',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
