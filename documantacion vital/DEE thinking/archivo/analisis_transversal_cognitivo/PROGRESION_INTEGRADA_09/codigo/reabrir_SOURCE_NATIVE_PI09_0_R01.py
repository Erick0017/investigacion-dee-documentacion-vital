"""Root-only mature NATIVE source reopen using actual public gestionar clients.

No new world, code modification, Native input or advance. Existing complete
903603 source is loaded, three STATE calls/save/close, Native prefix compared.
Default plan does not read live cards or SQLite.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,subprocess
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/NATIVE/sistema';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01';KEY='DEE.Cognitive.PI09.selective_registered_consultation.R02';C2C='DEE.Cognitive.PI04.C2C.coordination.R01';FI='DEE.Cognitive.PI07.regulated_FI_access.R01'
OUTPUT=P/'control/REAPERTURA_SOURCE_NATIVE_PI09_R01.json';MARKER=P/'PI09_ROOT_NATIVE_WRITER.lock';TAG='PI09_SOURCE_NATIVE0_R01'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def ref(p):return {'path':str(p),'sha256':sha(p)}
def cli(label,args):
 command=[str(PY),'-I','-B','-X','utf8',str(S/'gestionar.py'),'--system-root',str(S),*args];out=P/'ensayos'/(TAG+'_'+label+'.CLI.stdout.json');err=out.with_name(out.stem+'.stderr.txt')
 with out.open('x',encoding='utf8')as o,err.open('x',encoding='utf8')as e:r=subprocess.run(command,cwd=P,stdout=o,stderr=e,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),timeout=60)
 need(r.returncode==0,'Public CLI failed; preserve exact ID/log and do not resend')
 return read(out),{'command':command,'exit_code':r.returncode,'stdout':ref(out),'stderr':ref(err)}
def control(label,operation):
 value,proof=cli(label,['mente-unificada-'+operation,'--vida',LIFE,'--id',TAG+'_'+label,'--esperar','30']);need(value.get('request',{}).get('status')=='completed','Public control incomplete; inspect same ID');return proof
def state(owner,label,mode):
 identifier=TAG+'_'+label;need(owner.q.get(identifier)is None,'Existing request ID, never resend')
 admitted,p1=cli(label+'_pedir',['mente-unificada-pedir','--vida',LIFE,'--id',identifier,'--situaciones',json.dumps([{'modo':mode}],separators=(',',':')),'--retorno','omit','--actuador','closed','--esperar','0']);need(not str(admitted.get('admission','')).startswith('rejected'),'Public STATE admission rejected')
 p2=control(label+'_reanudar','reanudar');owner.wait(identifier);answer,p3=cli(label+'_resultado',['mente-unificada-resultado','--vida',LIFE,'--id',identifier]);p4=control(label+'_pausar','pausar');row=answer.get('request',{});need(row.get('id')==identifier and row.get('status')=='completed','Same-ID public STATE result missing')
 file=P/'ensayos'/(identifier+'.json')
 with file.open('x',encoding='utf8')as f:json.dump(row,f,ensure_ascii=False,indent=2);f.write('\n')
 return json.loads(row['result']),{'mode':mode,'primary':ref(file),'public_cli':[p1,p2,p3,p4]}
def stocks(view):
 e=view['metadata'];q=json.loads(e[KEY]);c=json.loads(e[C2C]);f=json.loads(e[FI])
 return {'PI09':{'ordinal':q['ordinal'],'total':q['control']['max_ordinal'],'remaining':q['control']['max_ordinal']-q['ordinal']},'C2C':{'ordinal':c['ordinal'],'total':32,'remaining':32-c['ordinal']},'FI':{'ordinal':f['ordinal'],'total':8,'remaining':8-f['ordinal']}}
def main(a):
 if not a.ejecutar:print(json.dumps({'mode':'PLAN_ONLY_NO_STATE_READ','system':str(S),'life_id':LIFE,'tick':903603,'public_operations':['iniciar pausado','pedir/resultado STATE_PI09,C2C,FI','guardar','detener'],'new_Native_inputs':0,'new_ticks':0,'source_code_modified':False}));return
 need(Path(os.sys.executable).resolve()==PY.resolve(),'Root official existing Python required')
 need(not OUTPUT.exists()and not MARKER.exists()and not(RP/'EJECUCION_MATERIAL.lock').exists()and not(S/'estado/ACTIVO.json').exists(),'Fresh output and no Root/RP writer; never clear guards')
 manifest=P/'estados/NATIVE/SISTEMA_CODIGO_PI09.json';code=read(manifest);code_before={r['file']:r['sha256']for r in code['files']}
 need(all(sha(S/name)==digest for name,digest in code_before.items()),'Frozen canonical code closure changed')
 cardfile=S/'estado/vidas'/LIFE/'VIDA.json';card=read(cardfile);beforefile=S/card['snapshot'];need(card['physical']['tick']==903603 and sha(beforefile)==card['snapshot_sha256'],'Exact quiet mature source903603 required')
 parser=load('PI09_source0_passive_parser',RP/'observador_pasivo.py');before=parser.snapshot_view(beforefile);stock_before=stocks(before);need(stock_before=={'PI09':{'ordinal':12,'total':18,'remaining':6},'C2C':{'ordinal':31,'total':32,'remaining':1},'FI':{'ordinal':4,'total':8,'remaining':4}},'Source stock differs; never reset')
 active=C/'sistema/estado/ACTIVO.json';acard=C/'sistema/estado/vidas'/read(active)['life_id']/'VIDA.json';ar=read(acard);protected={str(p):sha(p)for p in(active,acard,C/'sistema'/ar['snapshot'])}
 with MARKER.open('x',encoding='utf8')as f:json.dump({'pid':os.getpid(),'life_id':LIFE,'scope':'Mature source public STATE/save/close0','new_native_inputs':0,'new_ticks':0},f)
 lib=load('PI09_source0_existing_owner',RP/'propietario_diagnostico.py');lib.configure(P,S,PY);rows=[]
 with lib.Owner(LIFE,TAG,system=S)as owner:
  for label,mode,ordinal in(('PI09','eci01-pi09-estado',12),('C2C','eci01-pi04-c2c-estado',31),('FI','eci01-pi07-fi-acceso-estado',4)):
   value,row=state(owner,label,mode);need(value['before_tick']==value['after_tick']==903603 and value['result']['rows'][0]['progress']['ordinal']==ordinal,'STATE altered time/stock');rows.append(row)
  saved=control('guardar','guardar');stopped=control('detener','detener');owner.proc.wait(timeout=60)
 need(owner.proc.poll()==0 and(owner.q.get_meta('owner')or{}).get('running')is False and not owner.q.outstanding(),'Actual source Owner did not close/reconcile')
 current=read(cardfile);afterfile=S/current['snapshot'];after=parser.snapshot_view(afterfile);fields={k:before[k]==after[k]for k in('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase')};changed=[k for k in set(before['metadata'])|set(after['metadata'])if before['metadata'].get(k)!=after['metadata'].get(k)];allowed=lambda k:k=='DEE.Cognitive.System.1.1.life.v1'or k=='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'or k.startswith('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1.queue.')
 stock_after=stocks(after);code_unchanged=all(sha(S/name)==digest for name,digest in code_before.items());principal_unchanged=protected=={name:sha(Path(name))for name in protected};valid=all(fields.values())and all(allowed(k)for k in changed)and stock_before==stock_after and code_unchanged and principal_unchanged
 proof={'schema':'DEE.PI09.mature_source.public_reopening0.R01','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'life_id':LIFE,'closed':True,'owner_closed':True,'new_ticks':0,'new_Native_inputs':0,'initial_tick':903603,'final_tick':current['physical']['tick'],'physical_unchanged':all(fields.values()),'causal_prefix_equal':fields['causal_prefix_sha256'],'Native_field_equalities':fields,'operational_state_valid':valid,'pending_reconciled':True,'snapshot_sha256':current['snapshot_sha256'],'before_snapshot':ref(beforefile),'after_snapshot':ref(afterfile),'source_record_before':card,'source_record_after':current,'stock_before':stock_before,'stock_after':stock_after,'stock_unchanged':stock_before==stock_after,'metadata_changed_keys':sorted(changed),'all_scientific_metadata_literal_unchanged':all(allowed(k)for k in changed),'source_code_manifest':ref(manifest),'source_code_unchanged':code_unchanged,'current_principal_unchanged':principal_unchanged,'public_STATE_rows':rows,'public_save':saved,'public_stop':stopped,'same_life_and_world_no_clone':True,'material_public_use_executed':False,'scope':'Actual mature NATIVE903603 second Owner, public manager STATE/save/close0. Encoded checkpoint may differ only by explicit transport metadata; Native/stock/history remain.'}
 with OUTPUT.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 if valid:need(read(MARKER)['pid']==os.getpid(),'Only own Root mutex may release');MARKER.unlink()
 print(json.dumps({'proof':str(OUTPUT),'sha256':sha(OUTPUT),'valid':valid,'new_ticks':0,'snapshot_sha256':current['snapshot_sha256']}));return 0 if valid else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--ejecutar',action='store_true');raise SystemExit(main(ap.parse_args()))
