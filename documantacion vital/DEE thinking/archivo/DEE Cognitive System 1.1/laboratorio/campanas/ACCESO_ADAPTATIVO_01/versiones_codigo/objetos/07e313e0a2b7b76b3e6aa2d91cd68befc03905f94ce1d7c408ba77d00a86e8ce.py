"""A moving diversion replaces a blocking diagnostic wall, never edits RAW.

One prospective fixed pulse diverts the extra -X contribution before the failed
turn. Its offroute sham and an additional native command cut are separate
futures. No response/target chooses the intervention at execution time.
"""
from pathlib import Path
import argparse,sys,json,gzip
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'),str(Path(__file__).parent)]
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import acceso_adaptativo_01 as aa,espanol_funcional_01 as e,paisaje_causal_01 as pc
from dee_thinking.persistence import decode_metadata
from instrumentos_pc01 import guard,receipts,frame,witness,sha
from avance_acotado import install
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);source=a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01/VIDA_INTEGRADA_19/main_read/PRIMARIOS.json.gz';ref=json.loads(gzip.decompress(source.read_bytes()));cut=next(z for z in ref['samples']if z['stage']=='learned');parent=ref['life'];life='AA01_DESVIO24_'+a.case;before=s.record(parent);s.fork(parent,life,kind='DIAGNOSTIC_COPY',checkpoint=cut['record_snapshot']);data={'case':a.case,'life':life,'parent':parent,'full_cut':cut['record_snapshot'],'full_cut_sha256':cut['record_snapshot_sha256'],'reference_primary_sha256':sha(source),'source_sha256':sha(__file__),'scope':'Prepared moving diversion, not learned repair. Hypothesis selected after R20/R23; these are design-stage controls, not a heldout reserve.','requests':[]}
def trial(x):
    install(x,a.out,seconds=220);cfg=decode_metadata(dict(x.world.runtime.snapshot_metadata_entries)[aa.KEY]);ep=cfg['episodes'][cfg['current']];turn=ep['plans']['-1']['turns'][5];site=e.move(turn['site'],(1,0,0),2);encounter=turn['tick']-2
    if a.case=='sham':site=e.move(site,(0,0,1),12)
    data['requests'].append(guard(x.world,'AA01.D24.DIVERT',e.move(site,(0,0,1),-3),encounter-3,direction=(0,0,1),semantic=1,payload=0));data['intervention']={'site':site,'encounter_tick':encounter,'turn':turn,'mechanical_difference_from_R23':'No persistent wall on the desired future +Xoutgoing route'}
    if'cut_command'in a.case:
        for polarity in(-1,1):data['requests'].append(guard(x.world,'AA01.D24.COMMAND.'+str(polarity),e.move(ep['policy_site'],(1,polarity,0),2),ep['epoch']+158,semantic=4,payload=0))
    data['pre']=physical(x.world);data['witnesses']=[];data['frames']=[]
    for target in(turn['tick']-4,turn['tick']-3,turn['tick']-2,turn['tick']-1,turn['tick'],turn['tick']+1,turn['tick']+2,turn['tick']+3):
        x.run_until(target);data['witnesses'].append(witness(x.world,turn['site']));data['frames'].append(frame(x.world))
    data['access']=aa.advance_episode(x,stage='access',max_seconds=90);data['frames'].append(frame(x.world));data['panel']={'less':e.context(x,value=61,method='B'),'more':e.context(x,value=119,method='B'),'near':pc.current_dose(x,parameter=3,load=4),'far':pc.current_dose(x,parameter=-3,load=6),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5')};data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime);return{'life':life,'tick':x.tick,'access':data['access']['SPANISH_DECODED'],'turn_direction':next(row['direction']for row in data['witnesses'][4]['records']if row['site']==turn['site']),'panel':{k:v.get('SPANISH_DECODED',v.get('TRADUCCION',{}).get('SPANISH_DECODED'))for k,v in data['panel'].items()}}
data['commit']=s.mutate(life,'AA01_PREPARED_MOVING_RELAY_DIVERSION_24',trial);data['original_current_pointer_unchanged']=s.record(parent)==before
with gzip.open(a.out/'PRIMARIOS.json.gz','wt',encoding='utf8',compresslevel=9)as f:json.dump(data,f,ensure_ascii=False,separators=(',',':'))
print(json.dumps(data['commit']['result'],ensure_ascii=False))
