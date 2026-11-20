"""Controlled administrative race model, no evolution or new life is committed.

The first record read is an actual older full MAINrecord; load then returns its
actual current full state. A mock commit observes which immutable snapshot the
genealogy describes. No source snapshot/record or RAW/clock is edited.
"""
from pathlib import Path
import argparse,sys,json,gzip
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01')]
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from instrumentos_pc01 import sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);source=a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01/MAIN_CONFIRMATORIO_36/main/PRIMARIOS.json.gz';d=json.loads(gzip.decompress(source.read_bytes()));old=d['initial_record'];life=d['life'];actual=s.record(life);original_record=s.record;calls=0;observed={}
def changing_record(name=None):
    global calls
    if name==life:
        calls+=1
        if calls==1:return old
    return original_record(name)
def inspect_commit(record,adapter,operation,**kwargs):
    observed.update({'genealogical_parent_sha256':record['parent']['snapshot_sha256'],'genealogical_parent_tick':record['parent']['tick'],'actual_loaded_physical':physical(adapter.world),'actual_current_source_sha256':actual['snapshot_sha256'],'correct_actual_source_identity':record['parent']['snapshot_sha256']==actual['snapshot_sha256'],'no_new_life_committed':True});return record
s.record=changing_record;s.commit=inspect_commit;s.fork(life,'AA01_RACE41_NOT_COMMITTED_'+a.case,kind='DIAGNOSTIC_COPY');data={'case':a.case,'scope':'Technical controlled change between two legitimate source reads, not a cognitive simulation or a claim this race occurred historically. Mock commit writes no life.','source_sha256':sha(__file__),'store_source_sha256':sha(a.system/'app/lives.py'),'old_source_tick':old['physical']['tick'],'current_source_tick':actual['physical']['tick'],'observed':observed,'source_current_pointer_unchanged':original_record(life)==actual};(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(observed))
