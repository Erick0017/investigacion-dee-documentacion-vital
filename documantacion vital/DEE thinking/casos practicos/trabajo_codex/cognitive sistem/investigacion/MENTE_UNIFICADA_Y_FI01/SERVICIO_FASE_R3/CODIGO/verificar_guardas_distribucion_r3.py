"""Zero-tick unit check of the protective collaboration example guard."""
import argparse,hashlib,importlib.util,json,tempfile
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    source=Path(__file__).resolve().parent/'distribucion/arrancar.py'
    spec=importlib.util.spec_from_file_location('collaboration_UI_only',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    root=Path(tempfile.mkdtemp(prefix='MUFI-distribution-guard-'));state=root/'trabajo_personal/estado';card=state/'vidas/PERSONAL_BOUND/VIDA.json';card.parent.mkdir(parents=True)
    card.write_text(json.dumps({'life_id':'PERSONAL_BOUND','persistent_service':{'sidecar_directory':'servicios_persistentes/PERSONAL_BOUND'}}),encoding='utf8')
    (state/'ACTIVO.json').write_text(json.dumps({'life_id':'PERSONAL_BOUND'}),encoding='utf8')
    before=card.read_bytes();calls=[]
    def forbidden(*args,**kwargs):calls.append(args);raise AssertionError('UI guard must reject before invoking the native manager')
    m.ROOT=root;m.call=forbidden
    try:m.example(5,life='NEW_COPY');raise AssertionError('Incomplete bare fork was accepted')
    except ValueError as error:message=str(error)
    checks={'no_native_command':not calls,'no_new_life_or_result_folder':not(state/'vidas/NEW_COPY').exists()and not(root/'trabajo_personal/resultados/NEW_COPY').exists(),'original_fixture_unchanged':card.read_bytes()==before,'actionable_paired_import_error':'mente-unificada-exportar'in message and'mente-unificada-importar'in message}
    result={'schema':'DEE.collaboration.R3.UI_guard_unit.v1','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'new_native_ticks':0,'DEE_imports':False,'checks':checks,'issues':[k for k,v in checks.items()if not v],'error_message':message,'scope':'Synthetic document-index fixture only. This tests prevention of an incomplete bare service fork, not native physics, learning or full-package usability.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'checks':checks}));return bool(result['issues'])

if __name__=='__main__':raise SystemExit(main())
