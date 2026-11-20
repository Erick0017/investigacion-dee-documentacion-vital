"""Prepare a narrow isolated PI07 owner/queue delta; Root alone --aplicar.

No product/engine/old scientific module is modified. Default only writes the
reviewable candidate source and manifests under this campaign's codigo.
"""
from pathlib import Path
import argparse,ast,hashlib,json,os,uuid
P=Path(__file__).resolve().parents[1];H=P/'codigo';S=P/'estados/candidato/sistema';DEST=H/'FUENTES_PI07_R02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def regular(p):
 for x in(p,*p.parents):
  if x.exists()and(x.is_symlink()or getattr(x.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked source/target')
def replace_once(t,old,new):
 if t.count(old)!=1:raise ValueError('Exact unchanged dispatch anchor required: '+old[:70])
 return t.replace(old,new,1)
def transformed_world(t):
 t=replace_once(t,"        return result\n\n    def validate", "        from capacidades import pi07_regulacion_R01 as pi07\n        pi07.operational_dependencies(self.a,self.work_directory)\n        for path in pi07.code_files():\n            self.code_sha256['PI07/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n        return result\n\n    def validate")
 mark="        row=self._eci01_row(payload)\n"
 # The same anchor occurs in validate and execute; isolate their source spans.
 start=t.index('    def validate(');end=t.index('    def execute(',start)
 v=t[start:end];v=replace_once(v,mark,mark+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi07-'):\n            from capacidades import pi07_regulacion_R01 as pi07\n            pi07.validate(self.a,row)\n            return\n");t=t[:start]+v+t[end:]
 start=t.index('    def execute(');end=t.index('    def _eci01_row(',start)
 v=t[start:end];v=replace_once(v,mark,mark+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi07-'):\n            from capacidades import pi07_regulacion_R01 as pi07\n            pi07.validate(self.a,row)\n            self.before_mutation('PI07_EXPLICIT_NEW_TC_SENSOR_FIXED_ACTUATOR_PROTOCOL')\n            value=pi07.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':pi07.VERSION,'rows':[value]}\n");t=t[:start]+v+t[end:]
 t=replace_once(t,"        result['PI04']=pi04.operational_dependencies(self.a,self.work_directory)\n        return result", "        result['PI04']=pi04.operational_dependencies(self.a,self.work_directory)\n        from capacidades import pi07_regulacion_R01 as pi07\n        result['PI07']=pi07.operational_dependencies(self.a,self.work_directory)\n        return result")
 t=replace_once(t,'    def external_uncertainty(self):\n','    def external_uncertainty(self):\n        from capacidades import pi07_regulacion_R01 as pi07\n        if pi07.uncertain(self.a):return True\n')
 return t
def transformed_queue(t):
 return replace_once(t,'        for row in rows:\n',"        for row in rows:\n            if str(row.get('modo','')).startswith('eci01-pi07-'):\n                from capacidades.pi07_regulacion_R01 import validate_literal\n                validate_literal(row)\n                continue\n")
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def main(a):
 proofpath=P/'control/HOOKS_PI07_R02_PREPARADOS.json';newfiles=('capacidades/pi07_regulacion_R01.py','capacidades/PROTOCOLO_PI07_R01.json')
 if not a.aplicar:
  if DEST.exists()or proofpath.exists():raise FileExistsError('Preserve the earlier candidate/proof')
  rows=[]
  for name,transform in(('app/mundo_genesis_apd05.py',transformed_world),('app/cola_local.py',transformed_queue)):
   source=S/name;regular(source);old=source.read_text('utf-8-sig');new=transform(old);ast.parse(new);target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(new,encoding='utf8')
   rows.append({'file':name,'before_sha256':sha(source),'after_sha256':sha(target),'scope':'Only new PI07 prefix/operational-dependency/code-fingerprint/uncertainty hooks; all old branches literal.'})
  newrows=[]
  for name in newfiles:
   source=H/Path(name).name;regular(source)
   if source.suffix=='.py':ast.parse(source.read_bytes())
   else:
    p=read(source)
    if p['origin']!=[8,40,50]or p['N']!=67 or p['initial_reference_payloads']!={'A':0,'B':2}or p['delay_laps']!=6:raise ValueError('Only the declared final RAW-clear P0 geometry')
   target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());newrows.append({'file':name,'bytes':source.stat().st_size,'sha256':sha(source)})
  proof={'schema':'DEE.PI07.isolated_owner_addition.R01','dispatcher_files':rows,'new_files':newrows,'Native_executed':False,'product_modified':False,'applied':False,'original_scientific_modules_modified':False}
  save(proofpath,proof);print(json.dumps({'proof':str(proofpath),'sha256':sha(proofpath),'Native_executed':False}));return
 output=P/'control/HOOKS_PI07_R02_APLICADOS.json'
 if output.exists():raise FileExistsError('Do not apply twice or blindly retry')
 if (S/'estado/ACTIVO.json').exists()or(P/'PI07_ROOT_NATIVE_WRITER.lock').exists():raise ValueError('Only closed unselected S7')
 locks=S/'estado/locks'
 if locks.exists()and any(locks.iterdir()):raise ValueError('An owner lock remains')
 proof=read(proofpath)
 for row in proof['dispatcher_files']:
  if sha(S/row['file'])!=row['before_sha256']or sha(DEST/row['file'])!=row['after_sha256']:raise ValueError('Dispatcher CAS differs before writes')
 for row in proof['new_files']:
  if sha(DEST/row['file'])!=row['sha256']or(S/row['file']).exists():raise ValueError('Fresh qualified PI07 files only')
 backup=H/'ORIGINALES_HOOKS_PI07_R02';backup.mkdir(exist_ok=False)
 for row in proof['dispatcher_files']:
  p=backup/row['file'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((S/row['file']).read_bytes())
 for row in proof['new_files']:
  target=S/row['file'];regular(target)
  with target.open('xb')as f:f.write((DEST/row['file']).read_bytes())
 for row in proof['dispatcher_files']:
  target=S/row['file'];regular(target);tmp=target.with_name(target.name+'.PI07_'+uuid.uuid4().hex+'.tmp');tmp.write_bytes((DEST/row['file']).read_bytes())
  if sha(target)!=row['before_sha256']:raise ValueError('Concurrent source change; preserve candidate')
  os.replace(tmp,target)
  if sha(target)!=row['after_sha256']:raise ValueError('Applied source identity differs')
 proof.update(applied=True,Native_ticks=0,originals_preserved_in=str(backup),system=str(S));save(output,proof);print(json.dumps({'proof':str(output),'sha256':sha(output),'Native_executed':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
