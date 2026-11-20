"""Validate candidate docs against the real CLI parser/transport without importing DEE."""
import argparse,ast,hashlib,importlib.util,json,re,shlex
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--system',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
    if a.salida.exists():raise FileExistsError('Preserve validation')
    contract=json.loads((a.candidate/'ASISTENTE_PROPOSITO_01.json').read_text(encoding='utf8'))
    guide=(a.candidate/'GUIA_ASISTENTE_APD01.md').read_text(encoding='utf8');source=a.system/'gestionar.py'
    tree=ast.parse(source.read_text(encoding='utf8'));function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='parser')
    isolated=ast.Module(body=[function],type_ignores=[]);namespace={'argparse':argparse,'Path':Path}
    exec(compile(isolated,str(source)+'::parser_only','exec'),namespace)
    parser=namespace['parser']();commands=[]
    for name,text in contract['actual_manager_commands'].items():
        argv=shlex.split(text);offset=argv.index('gestionar.py')+1;parsed=parser.parse_args(argv[offset:])
        commands.append({'name':name,'command':parsed.command,'parser_accepts':True})
    transport=a.system/'app/cola_local.py';spec=importlib.util.spec_from_file_location('APD_DOC_TRANSPORT_STDLIB',transport);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    examples=[]
    for index,body in enumerate(re.findall(r'```json\s*\n(.*?)\n```',guide,re.S)):
        rows=json.loads(body);op=module.validate_request({'operacion':'sesion','situaciones':rows,'actuador':'closed','retorno':'real'})
        examples.append({'index':index,'modes':[r['modo']for r in rows],'transport_accepts':op=='sesion','no_native_execution_claimed':True})
    module_names=[contract['implemented_modules'][k]for k in('assistant','numeric','bounded_acquired_content','separate_route','owner','transport','client','paired_import','explicit_epoch_close')]+contract['implemented_modules']['lexical']
    dependencies=[{'file':name,'exists':(a.system/name).is_file(),'sha256':sha(a.system/name)}for name in module_names]
    result={'schema':'APD01.candidate_contract.static_cli_schema_check.v1','native_ticks':0,'DEE_imported':False,
            'gestor_parser_source_sha256':sha(source),'transport_source_sha256':sha(transport),
            'candidate_contract_sha256':sha(a.candidate/'ASISTENTE_PROPOSITO_01.json'),
            'candidate_guide_sha256':sha(a.candidate/'GUIA_ASISTENTE_APD01.md'),
            'parsed_commands':commands,'JSON_examples':examples,'dependencies_read':dependencies,
            'final_state_still_pending':all(contract['selected_life'][k]is None for k in('final_tick','final_snapshot','final_snapshot_sha256','paired_export_directory','paired_export_manifest_sha256')),
            'scope':'Parser function isolated by AST; no full manager import, execute call, Runtime construction, transport journal access or engine import. JSON examples checked only against transport schema, not final-life operational availability.'}
    a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'commands':len(commands),'json_examples':len(examples),'native_ticks':0,'DEE_imported':False,'final_pending':result['final_state_still_pending']}))

if __name__=='__main__':main()
