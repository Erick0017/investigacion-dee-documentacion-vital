"""Prepare a local two-file PI06 dispatcher extension; Root --aplicar only S6.

No Native import/owner/execution or current-product writes. The plugin itself
is supplied separately. Every prior handler remains literal and ordered alike.
"""
from pathlib import Path
import argparse,ast,hashlib,json,os,uuid
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';SOURCE=C/'sistema';S=P/'estados/candidato/sistema'
DEST=P/'codigo/FUENTES_HOOKS_PI06_R01';PROOF=P/'control/HOOKS_PI06_PREPARADOS_R01.json'
EXPECTED={'app/mundo_genesis_apd05.py':'6b988948f50cd5d3b1faec61a5368714de175c182ffafb36fb23e476f06796f5',
 'app/cola_local.py':'d6cc7534495a7c9941422b0e1515681f8895b4bdef07e05521ad0253c0b4f626'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(text,old,new):
 if text.count(old)!=1:raise ValueError('Unique source contract changed: '+old)
 return text.replace(old,new)
def candidates():
 old={}
 for name,h in EXPECTED.items():
  f=SOURCE/name
  if sha(f)!=h:raise ValueError('Current product source changed; review instead of overwriting')
  old[name]=f.read_text('utf-8-sig')
 owner=old['app/mundo_genesis_apd05.py'];changes=[]
 def edit(oldtext,newtext):
  nonlocal owner
  owner=once(owner,oldtext,newtext);changes.append((oldtext,newtext))
 anchor="        return result\n\n    def validate(self,payload):"
 edit(anchor,"        from capacidades import pi06_organizacion_R01 as pi06\n        pi06.operational_dependencies(self.a,self.work_directory)\n        for path in pi06.code_files():\n            self.code_sha256['PI06/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n"+anchor)
 anchor="    def validate(self,payload):\n        row=self._eci01_row(payload)\n"
 edit(anchor,anchor+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi06-'):\n            from capacidades import pi06_organizacion_R01 as pi06\n            pi06.validate(self.a,row)\n            return\n")
 anchor="    def execute(self,payload):\n        row=self._eci01_row(payload)\n"
 edit(anchor,anchor+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi06-'):\n            from capacidades import pi06_organizacion_R01 as pi06\n            pi06.validate(self.a,row)\n            self.before_mutation('PI06_DECLARED_FINITE_ORGANIZATION_PROTOCOL')\n            value=pi06.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':pi06.VERSION,'rows':[value]}\n")
 anchor="        result['PI04']=pi04.operational_dependencies(self.a,self.work_directory)\n        return result"
 edit(anchor,"        result['PI04']=pi04.operational_dependencies(self.a,self.work_directory)\n        from capacidades import pi06_organizacion_R01 as pi06\n        result['PI06']=pi06.operational_dependencies(self.a,self.work_directory)\n        return result")
 anchor="    def external_uncertainty(self):\n"
 edit(anchor,anchor+"        from capacidades import pi06_organizacion_R01 as pi06\n        if pi06.uncertain(self.a):return True\n")
 restored=owner
 for oldtext,newtext in reversed(changes):restored=once(restored,newtext,oldtext)
 if restored!=old['app/mundo_genesis_apd05.py']:raise AssertionError('Prior owner code changed')
 queue=old['app/cola_local.py'];anchor="        for row in rows:\n"
 extra="            if str(row.get('modo','')).startswith('eci01-pi06-'):\n                from capacidades.pi06_organizacion_R01 import validate_literal\n                validate_literal(row)\n                continue\n"
 queue=once(queue,anchor,anchor+extra)
 if once(queue,anchor+extra,anchor)!=old['app/cola_local.py']:raise AssertionError('Prior queue code changed')
 out={'app/mundo_genesis_apd05.py':owner,'app/cola_local.py':queue}
 for value in out.values():ast.parse(value)
 return out
def regular(p):
 for q in(p,*p.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked isolated source or target')
def main(a):
 generated=candidates()
 if not a.aplicar:
  if DEST.exists()or PROOF.exists():raise FileExistsError('Preserve prior candidate version')
  rows=[]
  for name,value in generated.items():
   f=DEST/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(value,encoding='utf8')
   rows.append({'file':name,'before_sha256':EXPECTED[name],'after_sha256':sha(f),'bytes':f.stat().st_size})
  proof={'schema':'DEE.PI06.dispatcher_preparation.R01','files':rows,'prior_owner_and_queue_text_literal_preserved':True,
   'plugin':'capacidades/pi06_organizacion_R01.py','plugin_contract':['VERSION','MODES','validate_literal','validate','dispatch','code_files','operational_dependencies','uncertain'],
   'scope':'New prefix routing and declared code/dependency/uncertainty only; no engine, reader or Native policy change. No plugin execution in this builder.',
   'Native_executed':False,'new_ticks':0,'applied_to_isolated_system':False,'product_changed':False}
  with PROOF.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
  print(json.dumps({'proof':str(PROOF),'sha256':sha(PROOF),'files':rows},ensure_ascii=False));return
 # Root-only actual application, always confined to this campaign's isolated system.
 proof=json.loads(PROOF.read_text('utf8'));applied=P/'control/HOOKS_PI06_APLICADOS_R01.json'
 if applied.exists():raise FileExistsError('No blind second application')
 regular(S)
 if not S.is_dir()or(S/'estado/ACTIVO.json').exists():raise ValueError('Only unselected isolated S6')
 locks=S/'estado/locks'
 if locks.exists()and any(locks.iterdir()):raise ValueError('Scoped writers/locks present; wait for actual close')
 plugin=S/'capacidades/pi06_organizacion_R01.py'
 if not plugin.is_file():raise ValueError('Install and review the PI06 plugin before activating its dispatcher')
 ast.parse(plugin.read_bytes())
 for row in proof['files']:
  regular(S/row['file']);regular(DEST/row['file'])
  if sha(S/row['file'])!=row['before_sha256']or sha(DEST/row['file'])!=row['after_sha256']:raise ValueError('Exact CAS failed before any source write')
 backup=P/'codigo/ORIGINALES_HOOKS_PI06_R01';backup.mkdir(exist_ok=False)
 for row in proof['files']:
  target=S/row['file'];b=target.read_bytes();old=backup/row['file'];old.parent.mkdir(parents=True,exist_ok=True);old.write_bytes(b)
  tmp=target.with_name(target.name+'.PI06_'+uuid.uuid4().hex+'.tmp');tmp.write_bytes((DEST/row['file']).read_bytes())
  if sha(target)!=row['before_sha256']:raise ValueError('Concurrent isolated source change')
  os.replace(tmp,target)
  if sha(target)!=row['after_sha256']:raise ValueError('Applied isolated source differs')
 proof.update(applied_to_isolated_system=True,plugin_sha256=sha(plugin),system=str(S),originals_preserved_in=str(backup))
 with applied.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(applied),'sha256':sha(applied),'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
