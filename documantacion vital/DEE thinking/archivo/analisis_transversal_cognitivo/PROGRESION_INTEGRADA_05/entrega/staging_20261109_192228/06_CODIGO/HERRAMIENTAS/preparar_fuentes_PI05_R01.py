"""Build a reviewed PI05 patch tree only; never applies it to a system/world."""
from pathlib import Path
import argparse, ast, hashlib, json

HERE=Path(__file__).resolve().parent
OLD_C2C='51c27c6bf9cfd58f53f812268a855e2a47d458450141d585cf098939b5c27ab4'
def sha(b):return hashlib.sha256(b).hexdigest()
def replace_once(text,old,new):
    if text.count(old)!=1:raise ValueError('Exact single static anchor absent: '+old[:70])
    return text.replace(old,new,1)
def regular(path):
    for p in(path,*path.parents):
        if p.exists()and(p.is_symlink()or getattr(p.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked source/destination')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sistema-source',type=Path,required=True);ap.add_argument('--destino',type=Path,required=True)
    ar=ap.parse_args();src=ar.sistema_source.resolve(strict=True);out=ar.destino.absolute();regular(src);regular(out)
    if out.exists():raise ValueError('New unused patch output only; no in-place installation')
    original={name:(src/name).read_bytes()for name in('app/cola_local.py','app/mundo_genesis_apd05.py','capacidades/pi04_coordinacion_central_C2C.py')}
    if sha(original['capacidades/pi04_coordinacion_central_C2C.py'])!=OLD_C2C:raise ValueError('Exact preserved C2C OP2 baseline required')
    queue=original['app/cola_local.py'].decode('utf8').replace('\r\n','\n')
    anchor="        for row in rows:\n"
    queue=replace_once(queue,anchor,anchor+"            if str(row.get('modo','')).startswith('eci01-pi05-'):\n                from capacidades.pi05_transito_causal_R01 import validate_literal\n                validate_literal(row)\n                continue\n")
    owner=original['app/mundo_genesis_apd05.py'].decode('utf8').replace('\r\n','\n')
    anchor="        return result\n\n    def validate(self,payload):"
    owner=replace_once(owner,anchor,"        from capacidades import pi05_transito_causal_R01 as pi05\n        for path in pi05.code_files():\n            self.code_sha256['PI05/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n"+anchor)
    anchor="    def validate(self,payload):\n        row=self._eci01_row(payload)\n"
    owner=replace_once(owner,anchor,anchor+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi05-'):\n            from capacidades import pi05_transito_causal_R01 as pi05\n            pi05.validate(self.a,row)\n            return\n")
    anchor="    def execute(self,payload):\n        row=self._eci01_row(payload)\n"
    owner=replace_once(owner,anchor,anchor+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi05-'):\n            from capacidades import pi05_transito_causal_R01 as pi05\n            pi05.validate(self.a,row)\n            self.before_mutation('PI05_EXPLICIT_TRANSIT_INSTRUMENT_OR_EXTERNAL_CONTROL')\n            value=pi05.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':pi05.VERSION,'rows':[value]}\n")
    c2c=original['capacidades/pi04_coordinacion_central_C2C.py'].decode('utf8')
    c2c=replace_once(c2c,'def _opportunity_body(a,directory):',
        "# PI05 external-control bridge only: original20 plan stays literal; no Native call/reader/codec change.\n"+
        "def _pi05_yoked_signal(a,m,calendar):\n    if m['ordinal']<20:return _pure().replay_signal(m['plan'],m['ordinal'],calendar)\n    return _module('pi05_yoke_futuros_R01').replay_signal(a,m,calendar)\n\n\n"+
        'def _opportunity_body(a,directory):')
    c2c=replace_once(c2c,'        raise ValueError("The predeclared20-opportunity yoked control is exhausted; no invented future signals")',
        '        _module("pi05_yoke_futuros_R01").validate_future(a,m)  # explicit separately registered PI05 ordinals20/21 only')
    c2c=replace_once(c2c,'_pure().replay_signal(m["plan"],m["ordinal"],normalized) # verify BEFORE material input',
        '_pi05_yoked_signal(a,m,normalized) # verify BEFORE material input; original20 or separately declared PI05 future')
    c2c=replace_once(c2c,'_pure().replay_signal(m["plan"],m["ordinal"],normalized)\n                     if m["arm"]=="yoked"',
        '_pi05_yoked_signal(a,m,normalized)\n                     if m["arm"]=="yoked"')
    content={'app/cola_local.py':queue.encode(),'app/mundo_genesis_apd05.py':owner.encode(),
             'capacidades/pi04_coordinacion_central_C2C.py':c2c.encode()}
    for name in('app/cola_local.py','app/mundo_genesis_apd05.py'):
        if b'\r\n'in original[name]:content[name]=content[name].replace(b'\n',b'\r\n')
    for name in('observador_global_PI05_R01.py','pi05_transito_causal_R01.py','pi05_yoke_futuros_R01.py','PROTOCOLO_PI05_TRANSITO_R01.json'):
        content['capacidades/'+name]=(HERE/name).read_bytes()
    for name,b in content.items():
        if name.endswith('.py'):ast.parse(b.decode('utf8'),filename=name)
        elif name.endswith('.json'):json.loads(b)
    out.mkdir(parents=True,exist_ok=False)
    files=[]
    for name,b in content.items():
        p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        files.append({'file':name,'bytes':len(b),'sha256':sha(b),'source_before_sha256':sha(original[name])if name in original else None})
    before=out/'originales';before.mkdir()
    for name,b in original.items():
        p=before/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    proof={'schema':'DEE.PI05.static_source_patch.R01','applied_to_system':False,'Native_executed':False,
           'source_system':str(src),'patch_tree':str(out),'files':files,
           'scope':'PI05-only transport branch, prospective external capture, declared two-slot external yoked control; original20 plan and Native scientific API call order/readers unchanged'}
    (out/'MANIFIESTO_CAMBIOS_PI05.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
