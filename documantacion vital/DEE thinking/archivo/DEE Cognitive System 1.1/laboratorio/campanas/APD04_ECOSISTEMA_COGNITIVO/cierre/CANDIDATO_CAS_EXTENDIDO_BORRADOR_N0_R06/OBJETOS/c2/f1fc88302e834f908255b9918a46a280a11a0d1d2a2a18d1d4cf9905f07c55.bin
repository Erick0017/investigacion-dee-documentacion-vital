"""Local read-only panel/actual lexical-use inventory; no Native imports/ticks."""
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]


def walk(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from walk(child)
    elif isinstance(value,list):
        for child in value:yield from walk(child)


def main():
    spec=importlib.util.spec_from_file_location('panel_exact_RAW_only',HERE/'recalcular_panel_actuador_r02_n0.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    base=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/PANEL_HEREDADO_RAW_N0_R01'
    index=json.loads((base/'INDICE_LINEA_ORIGINAL.json').read_bytes())
    line=gzip.decompress((base/index['exported_line']).read_bytes())
    assert hashlib.sha256(line).hexdigest()==index['original_line_sha256']
    old=json.loads(line)['result']['request']['result']
    if isinstance(old,str):old=json.loads(old)
    expected={(row['family'],row['name']):row['sign']for row in module.panel_rows(old['result']['rows'][0])}
    results=[]
    for life in('APD04_ACTUADOR_REAL_R02','APD04_ACTUADOR_OMIT_R02'):
        path=ROOT/'sistema/estado/vidas'/life/'VIDA.json'
        if not path.is_file():continue
        record=json.loads(path.read_bytes());panels=[];word_uses=[]
        for op in record['operations']:
            relative=op.get('result_file','')
            if'apd04_actuator_'not in relative:continue
            source=ROOT/'sistema/estado/servicios_persistentes'/life/relative
            raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==op['result_sha256']
            primary=json.loads(raw)
            for block in primary['result'].get('rows',[]):
                if block.get('kind')=='APD03_explicit_material_panel':
                    rows=module.panel_rows(block)
                    panels.append({'primary':relative,'rows':rows,
                        'formed_forms':sum(row['family']=='forms'and row['sign']is not None for row in rows),
                        'formed_contexts':sum(row['family']=='memories'and row['sign']is not None for row in rows),
                        'matching_prior_forms':sum(row['family']=='forms'and row['sign']==expected[(row['family'],row['name'])]for row in rows),
                        'matching_prior_contexts':sum(row['family']=='memories'and row['sign']==expected[(row['family'],row['name'])]for row in rows)})
                for row in block.get('rows',[]):
                    if isinstance(row,dict)and row.get('word')is not None:
                        word_uses.append({'episode':row['episode'],'requested_word_environment':row['public_before']['word'],
                            'native_formed_tool_sign':row['word']['reader']['formed_native_command'],
                            'physical_action':row['physical_action']})
        results.append({'life':life,'panels':panels,'actual_APD04_word_queries':word_uses,
                        'tick':record['physical']['tick'],'new_Native_ticks':0})
    print(json.dumps(results,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
