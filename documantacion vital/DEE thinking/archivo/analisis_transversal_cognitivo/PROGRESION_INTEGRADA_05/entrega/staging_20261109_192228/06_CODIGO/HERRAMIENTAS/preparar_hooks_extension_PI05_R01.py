"""Prepare extension30 forwarding over the GUARD patch, never edit live S5."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;P=H.parent;S=P/'estados/candidato/sistema'
GUARD=H/'FUENTES_GUARDIA_PI05_R01_SELLADAS';E3=H/'PI05_INTEGRACION_R01_DRAFT/capacidades';OUT=H/'FUENTES_EXTENSION30_PI05_R01_PREPARADAS'
def sha(b):return hashlib.sha256(b).hexdigest()
def once(t,a,b):
    if t.count(a)!=1:raise ValueError('Exact extension hook anchor absent: '+a[:70])
    return t.replace(a,b,1)
def main():
    if OUT.exists():raise ValueError('New extension hook preparation only')
    names=('pi05_c2c_ofertas_R01.py','PROTOCOLO_PI05_C2C_30_R01.json','PROTOCOLO_PI05_C2C_EXTENSION_R01.json')
    original={n:(GUARD/n).read_bytes()for n in('app/cola_local.py','app/mundo_genesis_apd05.py')}
    original['capacidades/pi04_dispatcher.py']=(S/'capacidades/pi04_dispatcher.py').read_bytes()
    if sha(original['app/cola_local.py'])!='b921f1dfa4dfc525e4919e37f2806ec5cff7a9baefb4864f53b7bf8964fdebc3'or sha(original['app/mundo_genesis_apd05.py'])!='1346a48e8dc55e85c287c51a66c4118b3290bd282c48c4345db6321ab0c6f2b8':raise ValueError('Exact prepared GUARD app required')
    if sha(original['capacidades/pi04_dispatcher.py'])!='bcf39b6524ffba9ca793e5aff6c7a960f254d7c1159b2c3454d2a2dc31b7bdc1':raise ValueError('Exact old dispatcher required')
    q=original['app/cola_local.py'].decode('utf8').replace('\r\n','\n')
    modes="('eci01-pi05-c2c-ampliar','eci01-pi05-c2c-extension-estado')"
    a='        for row in rows:\n'
    q=once(q,a,a+"            if row.get('modo')in"+modes+":\n                from capacidades.pi05_c2c_ofertas_R01 import validate_literal\n                validate_literal(row)\n                continue\n")
    o=original['app/mundo_genesis_apd05.py'].decode('utf8').replace('\r\n','\n')
    a='    def validate(self,payload):\n        row=self._eci01_row(payload)\n'
    o=once(o,a,a+"        if row is not None and row.get('modo')in"+modes+":\n            from capacidades import pi05_c2c_ofertas_R01 as extension\n            extension.validate(self.a,row)\n            return\n")
    a='    def execute(self,payload):\n        row=self._eci01_row(payload)\n'
    o=once(o,a,a+"        if row is not None and row.get('modo')in"+modes+":\n            from capacidades import pi05_c2c_ofertas_R01 as extension\n            extension.validate(self.a,row)\n            self.before_mutation('PI05_EXPLICIT_ENVIRONMENT26_TO30_NO_NATIVE_EDIT')\n            value=extension.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':extension.VERSION,'rows':[value]}\n")
    d=original['capacidades/pi04_dispatcher.py'].decode('utf8').replace('\r\n','\n')
    a='def validate(a,row):return _for(row).validate(a,row)'
    b="""def _effective_plugin(a,name,for_dependencies=False):
    base=_load(name)
    if name=='pi04_coordinacion_central_C2C':
        return _load('pi05_c2c_ofertas_R01').effective_component(a,base,for_dependencies=for_dependencies)
    return base
def _material_for(a,row):
    # Only an explicit external-extension key changes the protocol instance.
    # Native actions/results never choose an instrument or expected output.
    original=_for(row)
    if getattr(original,'KEY',None)=='DEE.Cognitive.PI04.C2C.coordination.R01':
        return _load('pi05_c2c_ofertas_R01').effective_component(a,original)
    return original
def validate(a,row):return _material_for(a,row).validate(a,row)"""
    d=once(d,a,b)
    d=once(d,'return _for(row).dispatch(a,row,actuator=actuator,directory=directory)',
        'return _material_for(a,row).dispatch(a,row,actuator=actuator,directory=directory)')
    a="""def operational_dependencies(a,directory):
    return {name:_load(name).operational_dependencies(a,directory)
            for _,name in PLUGINS if Path(__file__).with_name(name+'.py').is_file()}"""
    b="""def operational_dependencies(a,directory):
    result={name:_effective_plugin(a,name,for_dependencies=True).operational_dependencies(a,directory)
            for _,name in PLUGINS if Path(__file__).with_name(name+'.py').is_file()}
    result['PI05_explicit_environment30']=_load('pi05_c2c_ofertas_R01').operational_dependencies(a,directory)
    return result"""
    d=once(d,a,b)
    a="""def uncertain(a):
    return any(_load(name).uncertain(a)for _,name in PLUGINS
               if Path(__file__).with_name(name+'.py').is_file())"""
    b="""def uncertain(a):
    if _load('pi05_c2c_ofertas_R01').uncertain(a):return True
    return any(_effective_plugin(a,name,for_dependencies=True).uncertain(a)for _,name in PLUGINS
               if Path(__file__).with_name(name+'.py').is_file())"""
    d=once(d,a,b)
    a="    return [Path(__file__)]+[root/name for name in names if(root/name).is_file()]"
    b="    paths=[Path(__file__)]+[root/name for name in names if(root/name).is_file()]\n    paths.extend(_load('pi05_c2c_ofertas_R01').code_files())\n    return list(dict.fromkeys(paths))"
    d=once(d,a,b)
    content={'app/cola_local.py':q.encode(),'app/mundo_genesis_apd05.py':o.encode(),'capacidades/pi04_dispatcher.py':d.encode()}
    for name in original:
        if b'\r\n'in original[name]:content[name]=content[name].replace(b'\n',b'\r\n')
    for name in names:content['capacidades/'+name]=(E3/name).read_bytes()
    for name,b in content.items():
        if name.endswith('.py'):ast.parse(b.decode('utf8'))
        else:json.loads(b)
    # The supply component must preserve the already qualified scientific body.
    assert sha((E3/'pi04_coordinacion_central_C2C.py').read_bytes())=='31778467ef0917f74fe422d538b9ed97a8144e05aaff1717dae4124b1ade87dd'
    OUT.mkdir();rows=[]
    for name,b in content.items():
        p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        rows.append({'file':name,'bytes':len(b),'sha256':sha(b),'source_before_sha256':sha(original[name])if name in original else None})
    for name,b in original.items():
        p=OUT/'originales'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    proof={'schema':'DEE.PI05.explicit_environment30_hook_patch.R01','source_system':str(S),'patch_tree':str(OUT),'files':rows,
        'applied':False,'Native_executed':False,'old26_scientific_body_changed':False,'validate_literal_original_unchanged':True,
        'precondition':'Apply guard patch first; then this exact CAS only after all owners closed. Extension itself requires separate explicit26→30 command; no automatic supply.',
        'scope':'KEY-absent material calls use literal old26; explicit KEY selects same body with declared30protocol. No actor action/route or expected result selects a component.'}
    (OUT/'MANIFIESTO_CAMBIOS_PI05.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
