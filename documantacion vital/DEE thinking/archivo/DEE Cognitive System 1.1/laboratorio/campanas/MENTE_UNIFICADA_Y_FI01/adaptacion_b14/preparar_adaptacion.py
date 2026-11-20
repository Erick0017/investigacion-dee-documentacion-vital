"""Mechanical evidence staging after physical close; no native imports."""
import hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema';EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/adaptacion_b14';OUT=LAB/'cierre/ADAPTACION'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    if OUT.exists():raise FileExistsError('Do not overwrite frozen adaptation supplement')
    OUT.mkdir(parents=True)
    mapping={'INFORME_ADAPTACION_B14.md':HERE/'INFORME_ADAPTACION_B14.md','CODIGO/adaptacion_c2_b14.py':HERE/'adaptacion_c2_b14.py',
      'CODIGO/frontend_b01_r2.py':LAB/'transferencia_b/frontend_b01_r2.py','CODIGO/eo02_trabajador_local.py':SYSTEM/'capacidades/eo02_trabajador_local.py',
      'CODIGO/selector_acrecion_nativo.py':SYSTEM/'capacidades/selector_acrecion_nativo.py','CODIGO/mente_acumulativa_r02.py':SYSTEM/'capacidades/mente_acumulativa_r02.py',
      'RECALCULO/recalcular_adaptacion.py':HERE/'recalcular_adaptacion.py','RECALCULADO/RECALCULO_ADAPTACION.json':HERE/'RECALCULO_ADAPTACION.json'}
    for p in EV.rglob('*'):
        if p.is_file():mapping['EVIDENCIA/'+p.relative_to(EV).as_posix()]=p
    for rel,source in mapping.items():
        dst=OUT/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dst)
        if sha(source)!=sha(dst):raise ValueError('Exact source copy differs')
    summary=json.loads((EV/'RESUMEN.json').read_text(encoding='utf8'));states=[]
    for arm in summary['arms']:
        for x in arm['opportunities']:
            p=SYSTEM/x['snapshot']
            if sha(p)!=x['snapshot_sha256']:raise ValueError('Saved complete state changed')
            states.append({'life':arm['life'],'tick':x['end_tick'],'local_path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'omitted':'Full world with interfaces, queues and external per-task state. Analysis is not an operational backup.'})
    (OUT/'ESTADOS_COMPLETOS_LOCALES.json').write_text(json.dumps(states,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    plan={'jobs':[{'cwd':'.','argv':['python','-I','-B','RECALCULO/recalcular_adaptacion.py','--evidencia','EVIDENCIA','--salida','RECORRIDO/RECALCULO_ADAPTACION.json'],'reference':'RECALCULADO/RECALCULO_ADAPTACION.json','reference_sha256':sha(HERE/'RECALCULO_ADAPTACION.json')}],
      'native_ticks_in_recalculation':0,'scope':'Archived first-use/adaptation primary calculation; not native re-execution or an alternate-law adaptive trajectory.'}
    (OUT/'PLAN_RECALCULO.json').write_text(json.dumps(plan,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    members=[{'file':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(OUT.rglob('*'))if p.is_file()]
    manifest={'members':members,'self_reference_excluded':True,'member_count':len(members),'bytes':sum(x['bytes']for x in members)}
    (OUT/'MANIFIESTO.json').write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'files':len(members)+1,'bytes':manifest['bytes'],'manifest_sha256':sha(OUT/'MANIFIESTO.json'),'path':str(OUT)}))
if __name__=='__main__':main()
