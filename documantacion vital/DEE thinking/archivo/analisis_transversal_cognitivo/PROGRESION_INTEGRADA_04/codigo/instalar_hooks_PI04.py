"""Opt-in PI04 instrument hooks in the isolated code copy only; zero Native."""
from pathlib import Path
import ast,hashlib,json,shutil
P=Path(__file__).resolve().parents[1];S=P/'estados/candidato/sistema'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def main():
    assert not(S/'estado/ACTIVO.json').exists(),'Never patch a selected product here'
    proof=P/'control/HOOKS_PI04_R01.json';assert not proof.exists()
    backup=P/'codigo/antes_hooks_R01';backup.mkdir()
    changes=[]
    edits={
    'app/cola_local.py':[("        for row in rows:\n", "        for row in rows:\n            if str(row.get('modo','')).startswith('eci01-pi04-'):\n                from capacidades.pi04_dispatcher import validate_literal\n                validate_literal(row)\n                continue\n")],
    'app/mundo_genesis_apd05.py':[
    ('        return result\n\n    def validate',"        from capacidades import pi04_dispatcher as pi04\n        pi04.operational_dependencies(self.a,self.work_directory)\n        for path in pi04.code_files():\n            self.code_sha256['PI04/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n        return result\n\n    def validate"),
    ('    def validate(self,payload):\n        row=self._eci01_row(payload)',"    def validate(self,payload):\n        row=self._eci01_row(payload)\n        if row is not None and str(row.get('modo','')).startswith('eci01-pi04-'):\n            from capacidades import pi04_dispatcher as pi04\n            pi04.validate(self.a,row)\n            return"),
    ('    def execute(self,payload):\n        row=self._eci01_row(payload)',"    def execute(self,payload):\n        row=self._eci01_row(payload)\n        if row is not None and str(row.get('modo','')).startswith('eci01-pi04-'):\n            from capacidades import pi04_dispatcher as pi04\n            pi04.validate(self.a,row)\n            self.before_mutation('PI04_EXPLICIT_DIAGNOSTIC_PROTOCOL')\n            value=pi04.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':pi04.VERSION,'rows':[value]}"),
    ("        return result\n\n    def external_uncertainty", "        from capacidades import pi04_dispatcher as pi04\n        result['PI04']=pi04.operational_dependencies(self.a,self.work_directory)\n        return result\n\n    def external_uncertainty"),
    ('    def external_uncertainty(self):\n',"    def external_uncertainty(self):\n        from capacidades import pi04_dispatcher as pi04\n        if pi04.uncertain(self.a):return True\n")]
    }
    for rel,patches in edits.items():
        f=S/rel;old=f.read_text(encoding='utf-8-sig');new=old
        for before,after in patches:
            assert new.count(before)==1,('Ambiguous hook',rel,before)
            new=new.replace(before,after)
        ast.parse(new,filename=rel)
        b=backup/Path(rel).name;shutil.copyfile(f,b)
        before=sha(f);f.write_text(new,encoding='utf-8')
        changes.append({'file':rel,'before_sha256':before,'after_sha256':sha(f),'literal_before':str(b)})
    src=P/'codigo/pi04_dispatcher.py';dst=S/'capacidades/pi04_dispatcher.py';assert not dst.exists();shutil.copyfile(src,dst)
    changes.append({'file':'capacidades/pi04_dispatcher.py','sha256':sha(dst),'new':True})
    with proof.open('x',encoding='utf-8')as f:json.dump({'schema':'DEE.PI04.opt_in_hooks.v1','system':str(S),'changes':changes,'new_Native_ticks':0,'original_product_modified':False,'no_policy_decisions_in_dispatcher':True},f,ensure_ascii=False,indent=2)
    print(json.dumps({'proof':str(proof),'changes':len(changes),'Native_ticks':0}))
if __name__=='__main__':main()
