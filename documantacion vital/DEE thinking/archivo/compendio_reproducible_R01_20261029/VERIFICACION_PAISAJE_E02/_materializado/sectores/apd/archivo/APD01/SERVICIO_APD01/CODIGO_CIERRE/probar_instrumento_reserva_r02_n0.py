"""Pure instrumentation fixtures for the R02 transient-file observer/prefix."""
import argparse,ast,hashlib,importlib.util,json
from pathlib import Path
def module(path):
    s=importlib.util.spec_from_file_location(path.stem,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class Entry:
    def __init__(self,name,size,vanish=False):self.name=name;self.size=size;self.vanish=vanish
    def is_file(self):return True
    def stat(self):
        if self.vanish:raise FileNotFoundError('Synthetic disappearing WAL fixture; not an actual operational SQLite file')
        return type('Size',(),{'st_size':self.size})()
class Parent:
    def __init__(self,entries):self.entries=entries
    def glob(self,pattern):return self.entries
class QueuePath:
    name='cola.sqlite3'
    def __init__(self,entries):self.parent=Parent(entries)
def main():
    p=argparse.ArgumentParser();p.add_argument('--reserva',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();here=Path(__file__).parent;h=module(here/'ensayo_servicio_apd_r02.py');builder=module(here/'preparar_reserva_apd_r02.py');config=json.loads((a.reserva/'CONFIG_READY.json').read_bytes());protocol=json.loads((a.reserva/'PROTOCOLO.json').read_bytes());checks={}
    vanished=h.passive_queue_size(QueuePath([Entry('cola.sqlite3',100),Entry('cola.sqlite3-wal',50,True)]));checks['disappearing_WAL_is_passive_absence_not_error']=vanished['bytes']==100 and vanished['transient_members_disappeared_during_stat']==['cola.sqlite3-wal']
    normal=h.passive_queue_size(QueuePath([Entry('cola.sqlite3',100),Entry('cola.sqlite3-wal',50)]));checks['available_sizes_still_counted']=normal['bytes']==150 and normal['transient_members_disappeared_during_stat']==[]
    checks['protocol_rebuild_exact_values']=builder.build(config)==protocol;checks['all480_new_ids']=len(protocol['events'])==480 and len({e['id']for e in protocol['events']})==480 and all(e['id'].startswith('apd61_')for e in protocol['events']);checks['seven_old_queued_rows_preserved']=len(protocol['inherited_pending_rows'])==7 and all(r['id'].startswith('apd60_')and r['status']=='queued'for r in protocol['inherited_pending_rows']);checks['same_reached_tick188466']=protocol['initial_cut']['tick']==188466;checks['R01_minutes_not_credited']=protocol['prior_interrupted_reserve']['R01_minutes_credited_to_R02']==0
    checks['builder_selftests_all_true']=builder.self_test()['all_true'];checks['old_harness_bytes_preserved']=hashlib.sha256((here/'ensayo_servicio_apd_r01.py').read_bytes()).hexdigest()=='1bb0b448a266e8dcc5ef794a63496fff12f4ff51611c956aff46c1fe43e57274';checks['old_frozen_harness_same_bytes']=hashlib.sha256((a.reserva.parent/'RESERVA_CONGELADA_R01/ensayo_servicio_apd_r01.py').read_bytes()).hexdigest()=='1bb0b448a266e8dcc5ef794a63496fff12f4ff51611c956aff46c1fe43e57274'
    result={'schema':'DEE.APD01.R02_instrument_only_tests.N0.v1','checks':checks,'all_true':all(checks.values()),'native_ticks':0,'Runtime_created':False,'scope':'Synthetic transient-file race fixtures and exact literal protocol reconstruction only, not an actual DEE failure/recovery or cognitive success.'}
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(result));return not result['all_true']
if __name__=='__main__':raise SystemExit(main())
