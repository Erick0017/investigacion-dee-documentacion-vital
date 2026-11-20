"""Same-life bounded operational incorporation, no diagnostic-state transplant."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from aplicar_B_main import run,mu,panel
def main():
    p=HERE/'PROTOCOLO_MAIN_CRUDOS_B_R1.json'
    if p.exists():raise FileExistsError('Existing protocol/progress protected')
    p.write_text(json.dumps({'revision':'B.MAIN.RAW.R1','source_cut':'MU_MAIN T32301 reached by its own19experiences and3actual chains, no reset',
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'extension':'Explicit P0 B05 geometry, fixed six-class current reader, existing stops retained and spill stop admitted only if complete RAW0.',
      'frames':[{'raw0':19,'other':0},{'raw0':19,'raw1':2,'other':0},{'raw0':19,'raw127':2,'other':0}],
      'host':'One scalar per128distinct physical sources, all same tick. No host sum, sign, response, target, bank or teacher in these frames.',
      'criteria':'Existing acquired reference must participate; inspect actual directions/data and all receipts. After every frame2Nticks then six old memory uses without teaching. End one real two-stage transaction and save. Do not repair if any output is adverse.',
      'scope':'Only3MAIN frames, not128individually relevant variables proved in MAIN. Independent same-prefix contrast family checks allindices separately and remains separately attributed.'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    run('B_MAIN_08_PREPARAR_128','unificada-preparar-crudos','--vida','MU_MAIN','--nivel','128')
    for k,index in enumerate((None,1,127),1):
        values=[0]*128;values[0]=19
        if index is not None:values[index]=2
        mu('B_MAIN_09_TRAMA128_'+str(k),[{'modo':'crudos','componentes':values}])
        panel('B_MAIN_10_RETENCION_TRAMA_'+str(k))
    mu('B_MAIN_11_CADENA_TRAS_CARGA_INICIO',[{'modo':'cadena-iniciar','contexto':'gamma','valores':[25,3]}])
    run('B_MAIN_11_GUARDAR_PENDIENTE','guardar','--vida','MU_MAIN')
    mu('B_MAIN_11_CADENA_TRAS_CARGA_FIN',[{'modo':'cadena-finalizar'}])
    run('B_MAIN_12_CORTE_PRE_CONTINUO','guardar','--vida','MU_MAIN')
if __name__=='__main__':main()
