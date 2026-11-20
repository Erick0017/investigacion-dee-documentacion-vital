"""Matched finite lived-state access dose, with the same new actual objects.

The absent-query arm keeps the environment and time, not an empty world. All
arms receive the same final common recovery query. No target enters the API.
"""
from pathlib import Path
import argparse,sys,json,gzip
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'),str(Path(__file__).parent)]
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import acceso_adaptativo_01 as aa,espanol_funcional_01 as e
from instrumentos_pc01 import frame,receipts,sha,native_digest
from avance_acotado import install
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='AA01_RECEPTOR14_down'if'down'in a.case else'AA01_RECEPTOR14_up';life='AA01_CADENCIA21_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'criteria_before':'Eight matched268tick episodes with actual new object magnitudes. Same phase and environmental presentations for allarms; old+alternative, alternativeonly, or nointermediatequery. A final old+alternative assay is common. Code recall is not current magnitude truth. Do not count repeated reads as new individuals.','episodes':[],'frames':[]}
def trial(x):
    install(x,a.out,seconds=220);epoch=x.tick;data['pre']=physical(x.world,occupation=True);data['native_at_start']=native_digest(x.world.runtime);layout=aa._configuration(x).get('recipient_layout');data['frames'].append(frame(x.world));passive='passive'in a.case;old_reader='alternative'in a.case or passive
    for k,value in enumerate((61,119,70,120,63,116,72,118)):
        start=epoch+k*268;x.run_until(start);row={'episode':k,'fixed_start':start,'actual_new_object':value,'pre':physical(x.world),'current_use':e.context(x,value=value,method='B')};old=e.tick_at_or_after(x.tick,phase=10,lead=8);finish=e.tick_at_or_after(old,phase=14)
        if passive:x.run_until(finish);row['recovery']=None;row['intermediate_query_omitted']=True
        else:row['recovery']=aa.recover_recipient(x,old_reader=not old_reader,max_seconds=90)
        if x.tick!=finish:raise AssertionError('Paired environmental/query calendars diverged')
        row['post']=physical(x.world,occupation=True);data['episodes'].append(row)
        if k in(3,7):data['frames'].append(frame(x.world))
    # Same delay and same final query in every arm, irrespective of prior success.
    x.run_until(epoch+8*268);data['final_common_query']=aa.recover_recipient(x,old_reader=True,max_seconds=90);data['frames'].append(frame(x.world));data['receipts']=receipts(x.world.runtime);data['post']=physical(x.world,occupation=True);return{'life':life,'tick':x.tick,'intermediate_queries':[r['recovery']['SPANISH_DECODED']if r.get('recovery')else None for r in data['episodes']],'final_common_query':data['final_common_query']['SPANISH_DECODED'],'occupation':data['post'].get('occupied'),'new_objects':8,'not_new_lexical_acquisitions':True}
try:data['commit']=s.mutate(life,'AA01_MATCHED_QUERY_DOSE_WITH_NEW_EXPERIENCES_21',trial)
except Exception as error:
    data['failure']={'type':type(error).__name__,'detail':str(error)};data['actual_reached_record']=s.record(life)
    if'Cooperative time window ended'not in str(error):raise
finally:
    with gzip.open(a.out/'PRIMARIOS.json.gz','wt',encoding='utf8',compresslevel=9)as f:json.dump(data,f,ensure_ascii=False,separators=(',',':'))
print(json.dumps(data.get('commit',{}).get('result',data.get('failure')),ensure_ascii=False))
