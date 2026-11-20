"""Stage public permission hooks on REAL's existing owner, no deployment."""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';SOURCE=P/'estados/REAL/sistema';STAGE=H/'PERMISO_PI10_R01_PREPARADO'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_exact(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==data
 else:
  with p.open('xb')as f:f.write(data)
owner=SOURCE/'app/mundo_genesis_apd05.py';text=owner.read_text('utf-8-sig');before=sha(owner)
anchor='        pi10_transport.install(self.a)\n';assert text.count(anchor)==1
text=text.replace(anchor,anchor+'        from capacidades import pi10_permiso_operativo_R01 as pi10_permission\n        pi10_permission.install(self.a)\n')
for method in('validate','execute'):
 start=text.index('    def '+method+'(self,payload):');end=text.index('\n    def ',start+8)if'\n    def 'in text[start+8:]else len(text);part=text[start:end];anchor='        pi10_transport.validate_external(self.a,row,payload=payload)\n';assert part.count(anchor)==1
 extra='        from capacidades import pi10_permiso_operativo_R01 as pi10_permission\n        pi10_permission.validate_external(self.a,row,payload=payload)\n        if pi10_permission.routes_public(self.a,row):\n'
 if method=='validate':extra+='            pi10_permission.validate_public(self.a,row)\n            return\n'
 else:extra+="            pi10_permission.validate_public(self.a,row)\n            self.before_mutation('PI10_EXACT_PUBLIC_INHERITED_FI8_ACCESS')\n            value=pi10_permission.execute_public(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':pi10_permission.VERSION,'rows':[value]}\n"
 text=text[:start]+part.replace(anchor,anchor+extra)+text[end:]
anchor='        for path in (*pi10.code_files(),*pi10_transport.code_files()):\n';assert text.count(anchor)==1
text=text.replace(anchor,'        for path in (*pi10.code_files(),*pi10_transport.code_files(),*pi10_permission.code_files()):\n');ast.parse(text)
permission=H/'pi10_permiso_operativo_R01.py';ast.parse(permission.read_text('utf8'));write_exact(STAGE/'app/mundo_genesis_apd05.py',text.encode('utf8'));write_exact(STAGE/'capacidades'/permission.name,permission.read_bytes())
report={'schema':'DEE.PI10.public_permission.staged_owner_delta.R01','product_modified':False,'Native_executed':False,'source_owner':str(owner),'source_owner_sha256':before,'files':[{'file':p.relative_to(STAGE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in(STAGE/'app/mundo_genesis_apd05.py',STAGE/'capacidades'/permission.name)],'scope':'Owner hook/public FI8/C2C permission only. No actor/protocol/Native bank or clock modification. Diagnostic public retention dormant until REAL18. Actual deployment/testing and coherent code-closure update still required.','contract_schema':'DEE.PI10.exact_operational_permission.v1','contract_file':'contratos/PI10_USO_OPERATIVO_R01.json'}
write_exact(STAGE/'PLAN.json',(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'stage':str(STAGE),'manifest_sha256':sha(STAGE/'PLAN.json'),'Native':0}))
