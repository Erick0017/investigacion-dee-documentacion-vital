"""One affected zero-tick reopening, with an exact owned process and full snapshot comparison."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,sqlite3,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';LIFE='ECI02_PI03_REPRO_PI04_MAIN_02'
sys.path.insert(0,str(P/'codigo'))
from servicio_ensayo_R02 import Owner
def main():
 a=argparse.ArgumentParser();a.add_argument('--system-root',type=Path,required=True);a.add_argument('--tag',required=True);a.add_argument('--proof',type=Path,required=True);z=a.parse_args()
 s=z.system_root.resolve();assert s in {(C/'sistema').resolve(),(P/'estados/candidato_R02/sistema').resolve()}
 assert z.tag.startswith('PI04_') and not z.proof.exists()
 card=s/'estado/vidas'/LIFE/'VIDA.json';before=json.loads(card.read_text(encoding='utf8'))
 parserpath=P.parents[0]/'PROGRESION_INTEGRADA_01/codigo/PROMOVER_PI01.py'
 spec=importlib.util.spec_from_file_location('pi04_reopen_passive',parserpath);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 v0=m.snapshot_view(s/before['snapshot'])
 with Owner(LIFE,z.tag,system=s) as owner:
  actual=owner.material(z.tag+'_STATE',{'modo':'eci01-pi04-c2c-estado'},feedback='omit')
  assert actual['before_tick']==actual['after_tick']==before['physical']['tick']
  row=actual['result']['rows'][0];progress=row['progress'];device=row['device']
  assert progress['ready'] and progress['admitted'] and progress['arm']=='real'
  assert not any(progress.get(k)for k in ('pending','uncertain','halted_reason'))
  assert not any(device.get(k)for k in ('pending','uncertain','feedback_pending'))
  assert progress['ordinal']==device['ordinal'] and progress['ordinal'] in (23,24)
  owner.control('guardar')
  owned={'pid':owner.proc.pid,'initial':owner.initial,'cmd':owner.cmd}
 after=json.loads(card.read_text(encoding='utf8'));v1=m.snapshot_view(s/after['snapshot']);cmp=m.compare_native(v0,v1,allow_service=True)
 assert cmp['physical_equal'] and cmp['causal_prefix_equal'] and cmp['new_ticks']==0
 db=s/'estado/servicios_persistentes'/LIFE/'cola.sqlite3';con=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
 pending=con.execute("select id,status from requests where status in ('queued','processing','uncertain')").fetchall();con.close();assert not pending
 value={'schema':'PI04.actual_product_reopening.v1','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'life_id':LIFE,'system':str(s),'new_ticks':0,'physical_unchanged':True,'pending_reconciled':True,'operational_state_valid':True,'owner_closed':True,'owned_handle_exit_code':owner.proc.poll(),'snapshot_sha256':after['snapshot_sha256'],'tick':after['physical']['tick'],'comparison':cmp,'state_primary':str(P/'ensayos'/(z.tag+'_STATE.json')),'owned_process':owned,'pending':pending,'actual_progress_ordinal':progress['ordinal'],'actual_environment':device,'scope':'Actual opening, administrative state inspection, save and exact owned closure. No material capacity test was repeated.'}
 with z.proof.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2)
 print(json.dumps({'proof':str(z.proof),'tick':value['tick'],'new_ticks':0}))
if __name__=='__main__':main()
