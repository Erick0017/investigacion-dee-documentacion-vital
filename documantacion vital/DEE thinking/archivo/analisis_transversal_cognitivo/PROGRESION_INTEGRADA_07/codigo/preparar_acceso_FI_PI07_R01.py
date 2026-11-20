"""Prepare explicit access/fixed selected-outer routing, Root applies closed."""
from pathlib import Path
import argparse,ast,hashlib,json,os,uuid
P=Path(__file__).resolve().parents[1];H=P/'codigo';S=P/'estados/candidato/sistema';D=H/'FUENTES_ACCESO_FI_PI07_R01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main(a):
 planfile=P/'control/ACCESO_FI_PI07_PREPARADO_R01.json'
 if not a.aplicar:
  if D.exists()or planfile.exists():raise FileExistsError('Preserve prior prepared source')
  D.mkdir();rows=[]
  for name in('pi07_acceso_FI_regulado_R01.py','PROTOCOLO_PI07_ACCESO_FI_R01.json'):
   source=H/name;target=D/'capacidades'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
   if source.suffix=='.py':ast.parse(source.read_bytes())
   elif read(source).get('status')!='SEALED_BEFORE_NEW_FI_TESTS':raise ValueError('Actual prospective access protocol required')
   rows.append({'file':'capacidades/'+name,'bytes':source.stat().st_size,'sha256':sha(source),'before_sha256':None})
  for name in('app/mundo_genesis_apd05.py','app/cola_local.py'):
   source=S/name;old=source.read_text('utf8');new=old.replace('pi07_regulacion_R03','pi07_acceso_FI_regulado_R01')
   if new==old or new.replace('pi07_acceso_FI_regulado_R01','pi07_regulacion_R03')!=old:raise ValueError('Import-only existing instrument facade change required')
   ast.parse(new);target=D/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(new,encoding='utf8');rows.append({'file':name,'before_sha256':sha(source),'bytes':target.stat().st_size,'sha256':sha(target)})
  name='capacidades/acceso_integrado_eci01.py';source=S/name;old=source.read_text('utf8');needle='def dispatch(a, row, *, actuator="closed", directory=None):\n    validate(a, row)'
  if old.count(needle)!=1:raise ValueError('Exact outer dispatcher point required')
  new=old.replace(needle,needle+'\n    if row.get("modo") == "eci01-balance":\n        from capacidades import pi07_acceso_FI_regulado_R01 as access\n        if access.routes_selected_legacy(a,row):\n            return access.dispatch(a,{"modo":access.QUERY,"izquierda":row["izquierda"],"derecha":row["derecha"]},actuator=actuator,directory=directory)')
  ast.parse(new);target=D/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(new,encoding='utf8');rows.append({'file':name,'before_sha256':sha(source),'bytes':target.stat().st_size,'sha256':sha(target)})
  protected={n:sha(S/'capacidades'/n)for n in('pi07_regulacion_R01.py','PROTOCOLO_PI07_R01.json','pi07_regulacion_R02.py','PROTOCOLO_PI07_R02.json','pi07_regulacion_R03.py','PROTOCOLO_PI07_R03.json','acceso_eci01.py','acciones_nativas_apd04.py','pi05_transito_causal_R01.py','pi04_coordinacion_central_C2C.py')}
  save(planfile,{'schema':'DEE.PI07.new_explicit_functional_FI_access.delta.v1','status':'PREPARED_BEFORE_NEW_ACCESS_NATIVE','files':rows,'preserved':protected,'Native_executed':False,'product_modified':False,'default_routing':'Only outer acceso_integrado.dispatch, exact selected CAND plus committed FI_access flag/hash/all_outer_FI_requests. Internal acceso.balance/arithmetic/C2C unchanged; no operand/result-dependent routing.','limits':'Historical198tick API regression remains. New access adds fixed TC query/sensor/efference/pulse and calendar; outcome remains old earlyq4. No new anatomy or learned timing.'})
  print(json.dumps({'plan':str(planfile),'sha256':sha(planfile),'files':len(rows),'Native_executed':False}));return
 plan=read(planfile);out=P/'control/ACCESO_FI_PI07_APLICADO_R01.json'
 if out.exists()or(P/'PI07_ROOT_NATIVE_WRITER.lock').exists()or(S/'estado/ACTIVO.json').exists():raise ValueError('Fresh closed isolated system only')
 if(S/'estado/locks').exists()and any((S/'estado/locks').iterdir()):raise ValueError('Live owner lock remains')
 for row in plan['files']:
  target=S/row['file']
  if sha(D/row['file'])!=row['sha256']or(row['before_sha256']is None and target.exists())or(row['before_sha256']is not None and sha(target)!=row['before_sha256']):raise ValueError('Exact source CAS failed')
 for name,h in plan['preserved'].items():
  if sha(S/'capacidades'/name)!=h:raise ValueError('Historical source changed')
 backup=H/'ORIGINALES_ACCESO_FI_PI07_R01';backup.mkdir(exist_ok=False)
 for row in plan['files']:
  target=S/row['file']
  if target.exists():
   original=backup/row['file'];original.parent.mkdir(parents=True,exist_ok=True);original.write_bytes(target.read_bytes())
  temp=target.with_name(target.name+'.ACCESS_'+uuid.uuid4().hex+'.tmp');temp.write_bytes((D/row['file']).read_bytes());os.replace(temp,target)
 for name,h in plan['preserved'].items():
  if sha(S/'capacidades'/name)!=h:raise RuntimeError('Protected scientific source altered')
 plan.update(status='SOURCE_APPLIED_ZERO_NATIVE_NOT_YET_USED',new_native_ticks=0,backup=str(backup));save(out,plan);print(json.dumps({'proof':str(out),'sha256':sha(out),'Native_executed':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
