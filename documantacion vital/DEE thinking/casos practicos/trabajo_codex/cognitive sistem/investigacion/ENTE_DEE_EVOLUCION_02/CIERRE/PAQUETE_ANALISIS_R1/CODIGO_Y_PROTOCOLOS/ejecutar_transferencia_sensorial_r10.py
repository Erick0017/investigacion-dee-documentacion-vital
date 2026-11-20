"""Finite prospective 2-to8 material transfer and operative continuation."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
EV=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02'
def op(case,args):
    subprocess.run([sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',case,*args],cwd=ROOT,check=True)
def main():
    seal=HERE/'PROTOCOLO_TRANSFERENCIA_SENSORIAL_R10.json'
    if seal.exists():raise FileExistsError('Finite frozen protocol already exists')
    pre='estado/checkpoints/EO02_SENSORIAL_R10_T0.T16893.263657f7e71c.deetsnap.gz'
    post='estado/checkpoints/EO02_SENSORIAL_R10_T0.T18457.76ab5932c016.deetsnap.gz'
    expected=['cfa49335829f81c58f67037d977cb33761b30ab2c23072988400c80fd88706af','ee7c572cf28fb5bb94075160ed26d5b15faef821432987f1a4f6e8f432a62bd2']
    for path,want in zip([pre,post],expected):
        if hashlib.sha256((ROOT/'sistema'/path).read_bytes()).hexdigest()!=want:raise ValueError('Historical complete checkpoint identity')
    frames=[[2,4,3,5,4,4,5,5],[3,5,4,6,5,6,6,6],[4,6,5,7,6,6,7,7],[5,7,6,8,7,8,8,8]]
    extension=[[7,8,8,9,9,10,10,11],[8,9,9,10,10,11,11,13]]
    protocol={'revision':'EO02.R10.2to8_actual_local_services.1','frozen_monotonic':time.monotonic(),
      'source':'Two actual historical2-input experiences [[11,15],[5,10]]; first contact changes native delta6to7',
      'T_parent':post,'U_parent':pre,'parent_sha256':expected,'U_same_experiences_feedback':'omit',
      'age_after_alignment':18457,'external_credit':4,'destination':frames,
      'criterion':'T at least3/4 useful actual worker operations and more useful than U; first response before destination feedback. Otherwise negative/partial; not independent brains or abstract transfer.',
      'operative_same_R10_extension':extension,'return_gate':[[10,11,11,12,12,13,13,14],[11,12,12,13,13,14,14,16]],
      'assistance':'Prepared remote8 fan-in, operator chooses task, same inherited comparison representation; worker admission law is external and computed only after native output',
      'no_source_knowledge_copied':True,'protected_EO02_MAIN_untouched_by_auxiliary_test':True}
    seal.write_text(json.dumps(protocol,indent=2)+'\n',encoding='utf8')
    op('31T_R10_FORK',['bifurcar','EO02_SENSORIAL_R10_T0','AUX_EO02_R10_TRANSFER_T','--modalidad','DIAGNOSTIC_COPY','--checkpoint-relativo',post])
    op('31U_R10_FORK',['bifurcar','EO02_SENSORIAL_R10_T0','AUX_EO02_R10_TRANSFER_U','--modalidad','DIAGNOSTIC_COPY','--checkpoint-relativo',pre])
    op('32U_R10_ALIGN_OMIT',['evolucion-servicio','--vida','AUX_EO02_R10_TRANSFER_U','--observaciones','[[11,15],[5,10]]','--dominio','puertas','--referencia-entorno','4','--reiniciar-entorno','--retorno','omit'])
    for group in ['T','U']:
        op('33'+group+'_R10_TRANSFER_B8',['evolucion-sensorial','--vida','AUX_EO02_R10_TRANSFER_'+group,'--observaciones',json.dumps(frames),'--dominio','trabajadores','--referencia-entorno','4','--reiniciar-entorno'])
    op('34_R10_MISMA_VIDA_B8',['evolucion-sensorial','--vida','EO02_SENSORIAL_R10_T0','--observaciones',json.dumps(extension),'--dominio','trabajadores','--referencia-entorno','4','--reiniciar-entorno'])
    op('35_R10_RETORNO_A8',['evolucion-sensorial','--vida','EO02_SENSORIAL_R10_T0','--observaciones',json.dumps(protocol['return_gate']),'--dominio','puertas','--referencia-entorno','4','--reiniciar-entorno'])
if __name__=='__main__':main()
