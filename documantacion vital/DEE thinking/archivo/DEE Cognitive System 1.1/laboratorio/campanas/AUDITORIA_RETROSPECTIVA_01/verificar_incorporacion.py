"""Software-only verification; no life load, state restore or material input."""
from pathlib import Path
import argparse,json,subprocess,sys,hashlib,time
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=a.root
sys.path.insert(0,str(Path(__file__).resolve().parent))
from leer_estado import load_json,sha
protected=load_json(r/'evidencia/campanas/AUDITORIA_RETROSPECTIVA_01/PAQUETE_CANDIDATO_01/EVIDENCIA_CAUSAL/ESTADOS_PROTEGIDOS.json')
checks=[]
def check_files():
    for q in protected:
        if 'protected_file'in q:assert sha(Path(q['protected_file']).read_bytes())==q['sha256']
        else:
            assert sha(Path(q['snapshot']).read_bytes())==q['summary']['encoded_sha256']
            assert sha((r/'sistema/estado/vidas'/q['life']/'VIDA.json').read_bytes())==q['VIDA_sha256']
check_files()
aa=r/'evidencia/campanas/ACCESO_ADAPTATIVO_01'
tests=[['inspeccionar-snapshot',str(aa/'PERDIDA_Y_REAPRENDIZAJE_13/wall11/ESTADO_COMPLETO_DESPUES_6.deetsnap.gz'),'--comparar',str(aa/'PERDIDA_Y_REAPRENDIZAJE_13/wall17/ESTADO_COMPLETO_DESPUES_6.deetsnap.gz')],['inspeccionar-snapshot',str(next((r/'sistema/estado/checkpoints').glob('AA01_ACCESO_LISTO_plus.T45857.*'))),'--comparar',str(next((r/'sistema/estado/checkpoints').glob('AA01_ACCESO_LISTO_minus.T45857.*')))],['eventos',str(Path(__file__).parent/'evento_guardia_negativo.txt')]]
for j,arguments in enumerate(tests):
    cmd=[sys.executable,'-I','-B','-X','utf8',str(r/'sistema/gestionar.py'),*arguments];q=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',timeout=60)
    if j<2:
        assert q.returncode==0,(q.stdout,q.stderr);v=json.loads(q.stdout);assert v['INSTRUMENTO']['native_ticks']==0 and v['INSTRUMENTO']['world_restored']is False
        assert v['AUDITOR']['comparison']['RAW_different_sites']==(0 if j==0 else 9)
    else:
        denied=json.loads(q.stdout)
        assert q.returncode!=0 and denied['error']['type']=='PermissionError'and denied['INSTRUMENTO']['status']=='EVENT_SCRIPT_PARTIAL_FAILURE'and denied['INSTRUMENTO']['committed_commands']==0,(q.stdout,q.stderr)
    checks.append({'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'kind':'SOFTWARE_READ_ONLY_NOT_NATIVE_EXPERIMENT','expected_outcome':'external observer'if j<2 else'normal event-script cannot use observer to read undeclared evidence'})
check_files()
files=[r/'sistema/gestionar.py',r/'sistema/capacidades/observador_causal_retrospectivo_01.py',r/'sistema/contratos/OBSERVADOR_CAUSAL_RETROSPECTIVO_01.json']
result={'schema':'DCS1.1.RETROSPECTIVE.incorporation.v1','checks':checks,'protected_snapshots_and_life_records_unchanged':True,'new_native_ticks':0,'no_life_restored_or_created':True,'integrated_files':[{'path':str(f),'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size}for f in files],'no_native_skill_added':True,'no_branch_promoted':True}
a.salida.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'software_checks':len(checks),'new_native_ticks':0,'protected_unchanged':True}))
