"""A related but different environment where blind reuse can be harmful."""
from pathlib import Path
import json,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def op(case,args):subprocess.run([sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',case,*args],check=True,cwd=ROOT)
def main():
    p=HERE/'PROTOCOLO_TRANSFERENCIA_CONTRARIA.json'
    if p.exists():raise FileExistsError('Preserve the first contrary-transfer protocol')
    parents=json.loads((HERE/'PROTOCOLO_TRANSFERENCIA_COMPUESTA_C_DESDE_FUENTE.json').read_bytes())['parents']
    raw=[[6,19],[10,23],[15,28]]
    p.write_text(json.dumps({'fixed_before_execution':True,'frozen_monotonic':time.monotonic(),'parents':parents,'raw_observations':raw,'destination_capacity_credit':6,'environment_not_injected':True,'histories_used':['T','U'],'opportunities':3,'first_response_before_feedback':True,'purpose':'A different relation can make the source14 acquired content harmful; no assumption training is always better.'},indent=2)+'\n',encoding='utf8')
    for row in parents:
        if row['group']not in('T','U'):continue
        life='AUX_EO02_CONTRARIA_'+row['group']
        op('29'+row['group']+'_FORK',['bifurcar',row['life'],life,'--modalidad','DIAGNOSTIC_COPY','--checkpoint-relativo',row['parent_checkpoint']])
        op('30'+row['group']+'_CONTRARIA',['evolucion-servicio','--vida',life,'--dominio','trabajadores','--observaciones',json.dumps(raw,separators=(',',':')),'--referencia-entorno','6','--reiniciar-entorno'])
if __name__=='__main__':main()
