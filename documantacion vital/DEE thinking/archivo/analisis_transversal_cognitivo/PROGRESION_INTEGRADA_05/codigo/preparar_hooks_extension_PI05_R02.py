"""Prepare dormant exact-main permission overR01 hooks; oldbody317 remains."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
def main():
    source=H/'preparar_hooks_extension_PI05_R01.py';t=source.read_text('utf8')
    t=t.replace("OUT=H/'FUENTES_EXTENSION30_PI05_R01_PREPARADAS'","OUT=H/'FUENTES_EXTENSION30_PI05_R02_PREPARADAS'")
    a="return _load('pi05_c2c_ofertas_R01').effective_component(a,base,for_dependencies=for_dependencies)"
    b="component=_load('pi05_c2c_ofertas_R01').effective_component(a,base,for_dependencies=for_dependencies)\n        return _load('pi05_permiso_principal_R01').configure(component,a)"
    assert t.count(a)==1;t=t.replace(a,b)
    a="return _load('pi05_c2c_ofertas_R01').effective_component(a,original)"
    b="component=_load('pi05_c2c_ofertas_R01').effective_component(a,original)\n        return _load('pi05_permiso_principal_R01').configure(component,a)"
    assert t.count(a)==1;t=t.replace(a,b)
    a="paths.extend(_load('pi05_c2c_ofertas_R01').code_files())"
    b="paths.extend(_load('pi05_c2c_ofertas_R01').code_files())\\n    paths.append(root/'pi05_permiso_principal_R01.py')"
    assert t.count(a)==1;t=t.replace(a,b)
    a="    for name in names:content['capacidades/'+name]=(E3/name).read_bytes()"
    b=a+"\n    content['capacidades/pi05_permiso_principal_R01.py']=(H/'pi05_permiso_principal_R01_CANDIDATO.py').read_bytes()\n    content['app/pi05_identidad_c2c.py']=(H/'app/pi05_identidad_c2c.py').read_bytes()"
    assert t.count(a)==1;t=t.replace(a,b)
    t=t.replace("'DEE.PI05.explicit_environment30_hook_patch.R01'","'DEE.PI05.explicit_environment30_hook_patch.R02_dormant_exact_permission'")
    ast.parse(t);out=H/'construir_hooks_extension_PI05_R02.py';assert not out.exists();out.write_text(t,encoding='utf8')
    print(json.dumps({'builder':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'Native_executed':False}))
if __name__=='__main__':main()
