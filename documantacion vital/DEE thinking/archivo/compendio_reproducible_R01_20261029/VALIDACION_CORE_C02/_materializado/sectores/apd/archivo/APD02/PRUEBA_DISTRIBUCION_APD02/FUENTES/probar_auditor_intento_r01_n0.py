"""N0 fixture exporter/test for the preserved failed proof; never resumes it."""
import argparse,gzip,hashlib,importlib.util,json,shutil
from pathlib import Path
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in('prueba','diagnostico','extraido','salida'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.salida.mkdir(exist_ok=False);root=a.salida;proof=json.loads(a.prueba.read_bytes());(root/'PRUEBA_SERVICIO_APD02.json.gz').write_bytes(gzip.compress(a.prueba.read_bytes(),mtime=0));shutil.copy2(a.diagnostico,root/'DIAGNOSTICO_N0.json');life=proof['exact_import']['life_id'];service=(a.extraido/'trabajo_personal/estado/servicios_locales'/life).resolve();index={'life_id':life,'world_id':proof['exact_import']['world_id'],'by_node':{}}
    def rows(label):return json.loads((proof['results'][label].get('request')or proof['results'][label])['result'])['result']['rows']
    entries=[('new_apd_'+str(i),rows('new_apd_'+str(i))[0])for i in range(2)]+[('new_composition:stage:'+str(i),r)for i,r in enumerate(rows('new_composition')[0]['rows'])]
    for label,row in entries:
        artifact=row['committed_effect'].get('artifact');rel=Path('ARTEFACTOS')/label.replace(':','_');entry={'directory':rel.as_posix(),'artifact':artifact,'copied_actual_file':False}
        if artifact:
            path=(Path(row['effect_directory'])/artifact['relative_path']).resolve(strict=True)
            if not path.is_relative_to(service)or path.stat().st_size!=artifact['bytes']or hashlib.sha256(path.read_bytes()).hexdigest()!=artifact['sha256']:raise ValueError('Not this stopped personal world actual file')
            target=root/rel/artifact['relative_path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target);entry['copied_actual_file']=True
        index['by_node'][label]=entry
    (root/'ARTEFACTOS.json').write_text(json.dumps(index,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    here=Path(__file__).parent;full=load('full_util',here/'recalcular_full_apd02.py');partial=load('partial_R01',here/'auditar_intento_full_r01_apd02.py');quality=load('actual_quality',a.extraido/'sistema/capacidades/evaluador_calidad_apd02.py');origin=full.r4.origin_from_source(a.extraido/'sistema/capacidades/ruta_adaptativa_apd02_04.py');result=partial.calculate(root,raw=full.u,route=full.r4,effect=full.effect,goal=full.goal,quality=quality,origin=origin);(root/'RECALCULO_INTENTO_R01.json').write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps({'checks':result['checks'],'issues':result['issues'],'RAW':result['RAW_serialized_observations'],'copied_actual_files':sum(v['copied_actual_file']for v in index['by_node'].values()),'new_native_ticks':0}));return bool(result['issues'])
if __name__=='__main__':raise SystemExit(main())
