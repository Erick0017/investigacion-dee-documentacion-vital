"""Root-only explicit environmental FI8 supply, no Native tick/input."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,os
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/DISCOVERY/sistema';RP=C/'reproducibilidad';L='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01';TAG='PI09_FI8_ADMIT_R01';OUT=P/'control/ADMISION_FI8_DISCOVERY_PI09_R01.json';LOCK=P/'PI09_ROOT_NATIVE_WRITER.lock'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main(a):
 if not a.ejecutar:print(json.dumps({'mode':'PLAN_ONLY','life_id':L,'operations':['eci01-pi09-fi-lote-admitir','eci01-pi09-fi-lote-estado'],'new_Native_inputs':0,'new_ticks':0}));return
 assert not OUT.exists()and not LOCK.exists()and not(RP/'EJECUCION_MATERIAL.lock').exists()
 assert read(P/'control/ADOPCION_PRODUCTO_PI09.json')['phase']=='COMMITTED'and read(P/'control/INSTALACION_FI8_R01_APLICADA.json')['applied']
 active=C/'sistema/estado/ACTIVO.json';ar=read(active);acard=C/'sistema/estado/vidas'/ar['life_id']/'VIDA.json';ac=read(acard);protected={str(p):sha(p)for p in(active,acard,C/'sistema'/ac['snapshot'])}
 card=S/'estado/vidas'/L/'VIDA.json';start=read(card);assert start['physical']['tick']==907543 and not(S/'estado/ACTIVO.json').exists()
 parser=load('PI09_FI8_passive_parser',RP/'observador_pasivo.py');before=parser.snapshot_view(S/start['snapshot']);assert 'DEE.Cognitive.PI09.FI_lot8.R01'not in before['metadata']
 LOCK.write_text(json.dumps({'pid':os.getpid(),'life_id':L,'scope':'Explicit environmental FI lot8 admission0','Native_bound':0}),'utf8')
 lib=load('PI09_existing_FI8_owner',RP/'propietario_diagnostico.py');lib.configure(P,S,C/'motor/python313/python.exe');ops=[]
 with lib.Owner(L,TAG,system=S)as owner:
  for i,mode in enumerate(('eci01-pi09-fi-lote-admitir','eci01-pi09-fi-lote-estado')):
   r=owner.material(TAG+'_%02d'%i,{'modo':mode},feedback='omit',actuator='closed');assert r['before_tick']==r['after_tick']==907543
   row=r['result']['rows'][0];assert row['new_native_ticks']==0
   if i==0:assert row['admitted']and row['physical_unchanged']and row['all_old_metadata_literal_unchanged']
   assert row['old_FI_ordinal']==7 and row['new_lot_remaining']==8
   ops.append({'mode':mode,'actual':row,'primary':{'path':str(P/'ensayos'/(TAG+'_%02d.json'%i)),'sha256':sha(P/'ensayos'/(TAG+'_%02d.json'%i))}})
  owner.control('guardar')
 assert owner.proc.poll()==0 and not owner.q.outstanding()and not(owner.q.get_meta('owner')or{}).get('running')
 current=read(card);after=parser.snapshot_view(S/current['snapshot']);equal={k:before[k]==after[k]for k in ('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase')};assert all(equal.values())and protected=={p:sha(Path(p))for p in protected}
 value={'schema':'DEE.PI09.explicit_FI_lot8.actual_admission0.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'life_id':L,'initial_tick':907543,'final_tick':current['physical']['tick'],'new_ticks':0,'new_Native_inputs':0,'closed':True,'owner_closed':True,'Native_equalities':equal,'physical_unchanged':True,'principal_unchanged':True,'new_environmental_offers':8,'old_FI_ordinal_preserved':7,'old_FI_remaining_preserved':1,'not_energy_or_learning':True,'operations':ops,'snapshot_sha256':current['snapshot_sha256'],'scope':'Explicit new external opportunity lot, old metadata literal and Native prefix preserved; not a reset, new reference, memory copying, or learned recovery.'}
 OUT.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8');assert read(LOCK)['pid']==os.getpid();LOCK.unlink();print(json.dumps({'proof':str(OUT),'sha256':sha(OUT),'new_ticks':0,'closed':True,'new_offers':8}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ejecutar',action='store_true');main(p.parse_args())
