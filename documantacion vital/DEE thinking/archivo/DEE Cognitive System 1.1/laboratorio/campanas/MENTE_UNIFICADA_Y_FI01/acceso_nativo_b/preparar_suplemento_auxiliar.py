"""Mechanical exact-copy analysis supplement. No native imports/ticks."""
import hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema';EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/acceso_operativo';OUT=LAB/'cierre/AUXILIAR'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    if OUT.exists():raise FileExistsError('Frozen supplement already exists; do not overwrite')
    OUT.mkdir(parents=True);mapping={
      'CODIGO/acceso_nativo_mufi01.py':SYSTEM/'capacidades/acceso_nativo_mufi01.py',
      'CODIGO/gestionar_EJECUTADO_AUX.py':HERE/'gestionar_EJECUTADO_AUX.py',
      'CODIGO/incorporar_auxiliar_despues_cierre.py':HERE/'incorporar_auxiliar_despues_cierre.py',
      'CODIGO/ACCESO_NATIVO_MUFI01.json':SYSTEM/'contratos/ACCESO_NATIVO_MUFI01.json',
      'RECALCULO/recalcular_auxiliar_operativo.py':HERE/'recalcular_auxiliar_operativo.py',
      'RECALCULADO/RECALCULO_AUXILIAR.json':HERE/'RECALCULO_AUXILIAR.json',
      'INCORPORACIONES.md':HERE/'INCORPORACION_AUXILIAR.md'}
    for p in EV.glob('*.json*'):mapping['EVIDENCIA/'+p.name]=p
    for rel,source in mapping.items():
        target=OUT/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        if sha(source)!=sha(target):raise ValueError('Exact copy mismatch')
    r=json.loads((EV/'RESULTADO.json').read_text(encoding='utf8'));states=[]
    for x in r['ready']:
        path=SYSTEM/x['snapshot'];states.append({'life':x['life'],'local_path':str(path),'sha256':sha(path),'bytes':path.stat().st_size,'kind':'Complete READY whole world; omitted from analysis supplement'})
    card=json.loads((SYSTEM/'estado/vidas'/r['working_life']/'VIDA.json').read_text(encoding='utf8'));path=SYSTEM/card['snapshot']
    states.append({'life':r['working_life'],'local_path':str(path),'sha256':sha(path),'bytes':path.stat().st_size,'kind':'Complete consumed future; not READY; omitted from analysis supplement'})
    (OUT/'ESTADOS_COMPLETOS_LOCALES.json').write_text(json.dumps(states,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    plan={'jobs':[{'cwd':'.','argv':['python','-I','-B','RECALCULO/recalcular_auxiliar_operativo.py','--evidencia','EVIDENCIA','--salida','RECORRIDO/RECALCULO_AUXILIAR.json'],'reference':'RECALCULADO/RECALCULO_AUXILIAR.json','reference_sha256':sha(HERE/'RECALCULO_AUXILIAR.json')}],
      'native_ticks_executed_by_recalculation':0,'scope':'Operator-check logs and one material use; complete state restoration is NOT claimed by this analysis supplement.'}
    (OUT/'PLAN_RECALCULO.json').write_text(json.dumps(plan,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    members=[{'file':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(OUT.rglob('*'))if p.is_file()]
    manifest={'members':members,'self_reference_excluded':True,'bytes':sum(x['bytes']for x in members),'member_count':len(members)}
    (OUT/'MANIFIESTO.json').write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'path':str(OUT),'files':len(members)+1,'bytes':manifest['bytes'],'manifest_sha256':sha(OUT/'MANIFIESTO.json')}))
if __name__=='__main__':main()
