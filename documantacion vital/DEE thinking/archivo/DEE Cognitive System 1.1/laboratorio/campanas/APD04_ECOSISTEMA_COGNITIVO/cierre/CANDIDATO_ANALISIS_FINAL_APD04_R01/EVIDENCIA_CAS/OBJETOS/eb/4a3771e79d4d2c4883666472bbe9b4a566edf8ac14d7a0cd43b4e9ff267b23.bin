"""Reproduce el modelo convencional archivado, sin su capturador Windows no usado.

Preserva y verifica los bytes originales. Sólo elimina del AST import ctypes y
resources(), función que no participa en replay/trajectory/choose/commit. No
relaja la cerca, no sustituye ctypes, no ejecuta recursos ni un experimento DEE.
"""
import argparse,ast,hashlib,importlib.util,json,types
from pathlib import Path
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists()
    report=json.loads((a.evidence/'RESULTADOS_Y_RECURSOS.json').read_bytes())
    script=a.evidence/'ejecutar_recalcular_referencias_niveles_n0_r03.py'
    assert hashlib.sha256(script.read_bytes()).hexdigest()==report['sources_sha256'][script.name]
    spec=importlib.util.spec_from_file_location('archived_conventional_replay',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    def model_without_unused_capture(path):
        data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==report['sources_sha256'][path.name]
        tree=ast.parse(data,filename=str(path));body=[];removed=[]
        for node in tree.body:
            if isinstance(node,ast.Import) and [x.name for x in node.names]==['ctypes']:removed.append('import ctypes');continue
            if isinstance(node,ast.FunctionDef) and node.name=='resources':removed.append('resources');continue
            body.append(node)
        assert removed==['import ctypes','resources']
        tree.body=body
        assert not any(isinstance(node,ast.Name)and node.id=='ctypes' for node in ast.walk(tree))
        obj=types.ModuleType('archived_conventional_model_without_resource_capture');obj.__file__=str(path)
        exec(compile(tree,str(path),'exec'),obj.__dict__)
        assert not hasattr(obj,'resources') and not hasattr(obj,'ctypes')
        return obj
    m.model=model_without_unused_capture
    m.dump(a.out,m.replay(a.evidence))
if __name__=='__main__':main()
