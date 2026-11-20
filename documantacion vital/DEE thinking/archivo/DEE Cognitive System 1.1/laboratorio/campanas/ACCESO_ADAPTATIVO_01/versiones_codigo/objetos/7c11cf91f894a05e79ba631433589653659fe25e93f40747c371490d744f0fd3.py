"""One finite question from existing full post-use worlds, no new teaching.

Separates a new receiver's access from the older R14geometry. All four possible
ports are treated equally; neither the old content nor a correct word is read
from case labels, logs, teacher interfaces or metadata.
"""
from pathlib import Path
import argparse,sys,json,gzip
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'),str(Path(__file__).parent)]
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import acceso_adaptativo_01 as aa,espanol_funcional_01 as e
from dee_thinking.persistence import decode_metadata
from instrumentos_pc01 import frame,witness,guard,receipts,sha,native_digest
from avance_acotado import install
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);source=a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01';checkpoint=None
if a.case.startswith('main'):
    parent='E1_ACCESO_ADAPTATIVO_01';primary=json.loads(gzip.decompress((source/'MAIN_CONFIRMATORIO_36/main/PRIMARIOS.json.gz').read_bytes()));cut=primary['commands'][17]['result'];tick=cut['INSTRUMENTO']['tick'];expected=cut['INSTRUMENTO']['snapshot_sha256'];checkpoint=next(path.relative_to(a.system).as_posix()for path in(s.state/'checkpoints').glob(parent+'.T'+str(tick)+'.*.deetsnap.gz')if sha(path)==expected)
elif a.case.startswith('negative'):parent='AA01_SEPARADO33_up_no_content'
elif a.case.startswith('opposite'):parent='AA01_SEPARADO33_up_swap'
elif a.case.startswith('matched'):parent='AA01_SEPARADO33_up'
else:parent='AA01_API34_api_down_local'if'down'in a.case else'AA01_API34_api_up_local'
life='AA01_DIAG_B38_'+a.case;before=s.record(parent);s.fork(parent,life,kind='DIAGNOSTIC_COPY',checkpoint=checkpoint);data={'case':a.case,'life':life,'parent':before,'explicit_historical_full_cut':checkpoint,'source_sha256':sha(__file__),'purpose':'No content, word, old reference or taught-copy is supplied. Probe dose and historical-reader supply are declared instrument factors, not autonomous choices. Four potential Bports share one whole world.','requests':[]}
def trial(x):
    install(x,a.out,seconds=120);cfg=aa._configuration(x);layout=cfg.get('recipient_layout')
    if not layout or layout.get('codebook')!='OPAQUE_Z':
        m=decode_metadata(dict(x.world.runtime.snapshot_metadata_entries)['DEE.Cognitive.System.1.1.AA01.local25'])
        if m['S']!=[15,15,50]:raise ValueError('Do not silently apply an old or another local receiver layout')
        layout={'B':m['B'],'phase':(m['epoch']+240)%67,'old_phase':(m['epoch']+236)%67,'codebook':'OPAQUE_Z'}
    B=layout['B'];data['layout']=layout;data['pre']=physical(x.world,occupation=True);data['complete_native_before']=native_digest(x.world.runtime);data['pre_frame']=frame(x.world);data['columns_before']={key:[observe(x.world,[item['effect'][0],item['effect'][1],z])for z in range(67)]for key,item in B.items()};old=e.tick_at_or_after(x.tick,phase=layout['old_phase'],lead=8);target=e.tick_at_or_after(old,phase=layout['phase']);dose=0 if'zero'in a.case else 3 if'low'in a.case else 7;both='both'in a.case
    for key,item in B.items():
        if both:data['requests'].append(guard(x.world,'AA01.B38.OLD.'+key,e.move(item['hub'],(0,1,0),-3),old-3,direction=(0,1,0),semantic=1,payload=7))
        data['requests'].append(guard(x.world,'AA01.B38.ALTERNATE.'+key,e.move(item['effect'],(1,1,0),-3),target-3,direction=(1,1,0),semantic=1,payload=dose))
    x.run_until(old);data['old_reads']={key:observe(x.world,item['hub'])for key,item in B.items()};x.run_until(target-1);data['pre_query_context']={key:witness(x.world,item['effect'])for key,item in B.items()};x.run_until(target);data['reads']={key:observe(x.world,item['effect'])for key,item in B.items()};data['opaque_codes']=sorted(set(('Z-'if row['direction'][2]<0 else'Z+')for row in data['reads'].values()if row['state']==1 and row['semantic']==1 and row['direction'][:2]==[1,1]and abs(row['direction'][2])==1));data['post_frame']=frame(x.world);data['receipts']=receipts(x.world.runtime);data['post']=physical(x.world,occupation=True);return{'life':life,'tick':x.tick,'historical_reader_supplied':both,'alternative_dose':dose,'codes':data['opaque_codes'],'old':{key:row['direction']for key,row in data['old_reads'].items()},'read':{key:row['direction']for key,row in data['reads'].items()}}
data['commit']=s.mutate(life,'AA01_DECLARED_B_ACCESS_CONTRAST_WITHOUT_RETEACHING_38',trial);data['original_current_pointer_unchanged']=s.record(parent)==before
with gzip.open(a.out/'PRIMARIOS.json.gz','wt',encoding='utf8',compresslevel=9)as f:json.dump(data,f,ensure_ascii=False,separators=(',',':'))
print(json.dumps(data['commit']['result'],ensure_ascii=False))
