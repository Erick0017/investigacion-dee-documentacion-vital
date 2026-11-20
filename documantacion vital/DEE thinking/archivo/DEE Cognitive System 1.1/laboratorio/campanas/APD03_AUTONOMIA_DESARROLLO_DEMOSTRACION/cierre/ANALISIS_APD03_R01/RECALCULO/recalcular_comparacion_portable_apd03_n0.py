"""Portable adapter of the unchanged closed comparison calculator.

All reads use archived package members. Original absolute source names are
retained only as provenance metadata after checking the actual member hash
and byte length. No original path is opened, no DEE module is imported and
no policy or provider is run. This is not another comparator trajectory.
"""
import argparse,hashlib,importlib.util,json,sys,tempfile
from pathlib import Path


def read(path):return json.loads(Path(path).read_bytes())


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();root=args.evidence.resolve();target=args.out.resolve()
    if target.is_relative_to(root):raise ValueError('Output must stay outside archived evidence')
    preserved=read(root/'COMPARACION_FUNCIONAL_Y_COSTE_MAIN_REFERENCIAS.json')
    mapping={}
    def add(relative,metadata):
        path=(root/relative).resolve()
        if not path.is_relative_to(root):raise ValueError('Unexpected archive escape')
        if not isinstance(metadata,dict)or not {'file','bytes','sha256'}<=set(metadata):raise ValueError('Bad preserved provenance')
        if path.stat().st_size!=metadata['bytes']or sha(path)!=metadata['sha256']:raise ValueError('Archive differs from closed source '+str(relative))
        if path in mapping and mapping[path]!=metadata:raise ValueError('Ambiguous provenance mapping')
        mapping[path]=metadata
    add('REFERENCIAS/EVIDENCIA/PROGRAMA_PROSPECTIVO.json',preserved['program_source'])
    add('MAIN/RESULTADOS/RECALCULO_MAIN_FINAL.json',preserved['main_recalculation_source'])
    for metadata in preserved['main_primary_sources']:
        # Only a basename is used, never an absolute historical path.
        add(Path('MAIN/EVIDENCIA_MAIN/EVENTOS')/Path(metadata['file']).name,metadata)
    add('MAIN/EVIDENCIA_MAIN/SESIONES_UI_NUEVAS.jsonl.gz',preserved['main_UI_source'])
    add('RECURSOS/TOTAL_TREE/RESULTADO_SUPERVISION.json',preserved['main']['resources_outer_TOTAL']['source'])
    add('MAIN/RECURSOS_OS_NATIVE/RESULTADO.json',preserved['main']['resources_native_only_IO_class8']['source'])
    for reference in preserved['references']:
        policy=reference['policy'];component='WSLS_ESTANDAR'if policy=='wsls_estandar'else'REFERENCIAS'
        add(Path(component)/'EVIDENCIA'/policy/'resumen.json',reference['summary_source'])
        add(Path(component)/'EVIDENCIA'/policy/'eventos_primarios.jsonl',reference['primary_source'])
    source=root/'CODIGO_DE_CIERRE/generar_comparacion_funcional_n0.py'
    spec=importlib.util.spec_from_file_location('closed_comparison_calculator',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    def archived_source(path):
        actual=Path(path).resolve()
        if actual not in mapping:raise ValueError('Unmapped source requested; original reads forbidden')
        metadata=mapping[actual]
        if actual.stat().st_size!=metadata['bytes']or sha(actual)!=metadata['sha256']:raise ValueError('Source changed during recalculation')
        return dict(metadata)
    module.source=archived_source
    with tempfile.TemporaryDirectory(prefix='apd03_comparison_recalc_')as work:
        previous=sys.argv
        try:
            sys.argv=[str(source),'--main-stage',str(root/'MAIN'),'--three',str(root/'REFERENCIAS/EVIDENCIA'),
                '--standard',str(root/'WSLS_ESTANDAR/EVIDENCIA'),'--supervision',str(root/'RECURSOS/TOTAL_TREE/RESULTADO_SUPERVISION.json'),
                '--program',str(root/'REFERENCIAS/EVIDENCIA/PROGRAMA_PROSPECTIVO.json'),'--out',work]
            module.main()
        finally:sys.argv=previous
        result=Path(work)/'COMPARACION_FUNCIONAL_Y_COSTE_MAIN_REFERENCIAS.json'
        if result.read_bytes()!=(root/'COMPARACION_FUNCIONAL_Y_COSTE_MAIN_REFERENCIAS.json').read_bytes():raise ValueError('Closed comparison not exactly reproduced')
        value=read(result)
        if len(value['checks'])!=362 or not all(row['verified']for row in value['checks']):raise ValueError('362 causal/task/resource checks not recovered')
        with target.open('xb')as stream:stream.write(result.read_bytes())
    print(json.dumps({'archived_comparison_checks':362,'byte_identical':True,'source_members_verified':len(mapping),
        'original_paths_opened':0,'new_native_ticks':0,'new_provider_calls':0,'sha256':sha(target)}))


if __name__=='__main__':main()
