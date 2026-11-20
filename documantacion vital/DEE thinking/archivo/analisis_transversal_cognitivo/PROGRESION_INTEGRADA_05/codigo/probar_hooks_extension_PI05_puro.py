"""Fake forwarding checks only: no engine/source application/world activity."""
from pathlib import Path
from types import SimpleNamespace as NS
import ast,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;P=H.parent;T=H/'FUENTES_EXTENSION30_PI05_R01_PREPARADAS'
def main():
    f=T/'capacidades/pi04_dispatcher.py';sp=importlib.util.spec_from_file_location('PI05_ext_dispatcher_fake',f);d=importlib.util.module_from_spec(sp);sp.loader.exec_module(d)
    calls=[];key='DEE.Cognitive.PI04.C2C.coordination.R01'
    def plugin(name,k=None):
        return NS(KEY=k,validate_literal=lambda row:calls.append((name,'literal')),
            validate=lambda a,row:calls.append((name,'validate')),
            dispatch=lambda a,row,**kw:name,operational_dependencies=lambda a,directory:{'name':name},uncertain=lambda a:False)
    base=plugin('base26',key);effective=plugin('same_body_protocol30',key)
    others={n:plugin(n)for _,n in d.PLUGINS};others['pi04_coordinacion_central_C2C']=base
    extension=NS(effective_component=lambda a,b,for_dependencies=False:effective if a.ext else b,
        operational_dependencies=lambda a,directory:{'present':a.ext},uncertain=lambda a:bool(a.uncertain),code_files=lambda:[])
    d._load=lambda n:extension if n=='pi05_c2c_ofertas_R01'else others[n]
    # is_file guards inspect the existing complete source layout; no module is
    # imported from it. The prepared patch tree intentionally holds deltas only.
    d.__file__=str(P/'estados/candidato/sistema/capacidades/pi04_dispatcher.py')
    row={'modo':'eci01-pi04-c2c-oportunidad'}
    d.validate_literal(row);assert calls[-1]==('base26','literal')
    for present,name in((False,'base26'),(True,'same_body_protocol30')):
        a=NS(ext=present,uncertain=False);d.validate(a,row);assert calls[-1]==(name,'validate')
        assert d.dispatch(a,row,directory='FAKE')==name
        assert d.operational_dependencies(a,'FAKE')['pi04_coordinacion_central_C2C']['name']==name
        assert d.uncertain(a)is False
    assert d.uncertain(NS(ext=True,uncertain=True))is True
    old=(T/'originales/capacidades/pi04_dispatcher.py').read_text('utf8');new=f.read_text('utf8')
    get=lambda s,n:ast.dump(next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef)and x.name==n),include_attributes=False)
    assert all(get(old,n)==get(new,n)for n in('_load','_for','validate_literal'))
    proof={'schema':'DEE.PI05.environment30.forwarding_fake_test.R01','Native_executed':False,'new_ticks':0,
        'dispatcher_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
        'key_absent_uses_original26':True,'key_ready_uses_same_body_effective30':True,
        'uncertain_extension_blocks_material':True,'original_literal_loader_router_AST_unchanged':True,
        'scope':'Dispatch wiring/Fakes only; module transaction and actual Native operation require separate proofs.'}
    out=P/'control/PRUEBAS_HOOK_EXTENSION30_FAKE_R01.json';assert not out.exists();out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof))
if __name__=='__main__':main()
