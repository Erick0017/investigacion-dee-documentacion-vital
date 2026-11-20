"""Prepare app-only hooks from exact closed PI08 C sources; no deployment."""
from pathlib import Path
import ast,hashlib,json
P9=Path(__file__).resolve().parents[1]
SOURCE=P9.with_name('PROGRESION_INTEGRADA_08')/'estados/C_R03/sistema'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rep(s,a,b,count=1):
 if s.count(a)!=count:raise ValueError('Ancla de transporte inesperada: '+a[:90])
 return s.replace(a,b)
def build(output):
 output=Path(output)
 if output.exists():raise FileExistsError(output)
 (output/'app').mkdir(parents=True)
 path=SOURCE/'app/mundo_genesis_apd05.py';s=path.read_text('utf8')
 if sha(path)!='2cb1449fd7ad8d6188c52a1ff57d160506e4eff687b0317beab441f2e025ad9c':raise ValueError('Cambió el propietario C heredado')
 old="        from capacidades import pi08_identidad_B_readonly_C_R01 as pi08bc_transport\n        pi08b=pi08bc_transport.component(self.a,pi08b)"
 new="        from capacidades import pi09_transporte_heredado_R02 as pi09_transport\n        pi08b=pi09_transport.component_B(self.a,pi08b)"
 s=rep(s,'\n'+old,'\n'+new,3)
 old="            from capacidades import pi08_identidad_B_readonly_C_R01 as pi08bc_transport\n            pi08b=pi08bc_transport.component(self.a,pi08b)"
 new="            from capacidades import pi09_transporte_heredado_R02 as pi09_transport\n            pi08b=pi09_transport.component_B(self.a,pi08b)"
 s=rep(s,'\n'+old,'\n'+new,2)
 s=rep(s,"\n        from capacidades import pi08_consulta_condicional_C_R03 as pi08c\n", "\n        from capacidades import pi08_consulta_condicional_C_R03 as pi08c\n        from capacidades import pi09_transporte_heredado_R02 as pi09_transport\n        pi08c=pi09_transport.component_C(self.a,pi08c)\n",3)
 s=rep(s,"\n            from capacidades import pi08_consulta_condicional_C_R03 as pi08c\n", "\n            from capacidades import pi08_consulta_condicional_C_R03 as pi08c\n            from capacidades import pi09_transporte_heredado_R02 as pi09_transport\n            pi08c=pi09_transport.component_C(self.a,pi08c)\n",2)
 # Only explicit new prefix selects a plugin. All old branch bodies remain.
 anchor="    def validate(self,payload):\n        row=self._eci01_row(payload)\n"
 s=rep(s,anchor,anchor+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi09-'):\n            from capacidades import pi09_dispatcher_R02 as pi09\n            pi09.validate(self.a,row)\n            return\n")
 anchor="    def execute(self,payload):\n        row=self._eci01_row(payload)\n"
 s=rep(s,anchor,anchor+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi09-'):\n            from capacidades import pi09_dispatcher_R02 as pi09\n            pi09.validate(self.a,row)\n            self.before_mutation('PI09_EXPLICIT_VERSIONED_INSTRUMENT')\n            value=pi09.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':pi09.VERSION,'rows':[value]}\n")
 s=rep(s,"        return result\n\n    def validate", "        from capacidades import pi09_dispatcher_R02 as pi09\n        pi09.operational_dependencies(self.a,self.work_directory)\n        for path in pi09.code_files():\n            self.code_sha256['PI09/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n        return result\n\n    def validate")
 anchor="    def external_uncertainty(self):\n"
 s=rep(s,anchor,anchor+"        from capacidades import pi09_dispatcher_R02 as pi09\n        if pi09.uncertain(self.a):return True\n")
 s=rep(s,"        result['PI08_C']=pi08c.operational_dependencies(self.a,self.work_directory)\n        return result", "        result['PI08_C']=pi08c.operational_dependencies(self.a,self.work_directory)\n        from capacidades import pi09_dispatcher_R02 as pi09\n        result['PI09']=pi09.operational_dependencies(self.a,self.work_directory)\n        return result")
 ast.parse(s);(output/'app/mundo_genesis_apd05.py').write_text(s,encoding='utf8',newline='\n')
 path=SOURCE/'app/cola_local.py';q=path.read_text('utf8')
 if sha(path)!='3403aecf2255c7e51ed0d4749f6172ebdc37fb30facc4292e1160a9cfa69e57e':raise ValueError('Cambió la cola C heredada')
 anchor="            if str(row.get('modo','')).startswith('eci01-pi08-c-'):\n"
 q=rep(q,anchor,"            if str(row.get('modo','')).startswith('eci01-pi09-'):\n                from capacidades.pi09_dispatcher_R02 import validate_literal\n                validate_literal(row)\n                continue\n"+anchor)
 ast.parse(q);(output/'app/cola_local.py').write_text(q,encoding='utf8',newline='\n')
 return [{'file':p.relative_to(output).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(output.rglob('*.py'))]
if __name__=='__main__':
 out=P9/'codigo/HOOKS_PI09_R04_PREPARADOS';rows=build(out)
 (P9/'codigo/HOOKS_PI09_R04_PREPARADOS.json').write_text(json.dumps({'schema':'DEE.PI09.app_transport_hooks.prepared.R01','Native_executed':False,'deployed':False,'source_system':str(SOURCE),'files':rows,'scientific_mente_unificada_B_C_sources_modified':False},ensure_ascii=False,indent=2)+'\n','utf8')
 print(json.dumps({'prepared':str(out),'files':len(rows),'Native_executed':False}))
