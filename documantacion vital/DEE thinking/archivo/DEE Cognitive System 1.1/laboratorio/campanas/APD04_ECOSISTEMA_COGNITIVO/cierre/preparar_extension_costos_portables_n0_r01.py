"""Añade recálculo portátil de costes al CAS cerrado R04; no ejecuta Native."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();assert not a.out.exists()
    L='laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/';C=L+'cierre/';T=L+'controles_diseno/'
    def sha(rel):return hashlib.sha256((a.root/rel).read_bytes()).hexdigest()
    index=C+'CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R03/RUTAS_Y_HASHES.json'
    script=C+'recalcular_costos_por_etapa_apd04_n0_r04.py'
    files=[index,script]
    spec={'schema':'APD04.CAS.explicit_closed_extension_spec.N0.R05','base':C+'CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R04',
        'base_manifest_sha256':sha(C+'CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R04/MANIFIESTO_CAS.json'),
        'components':[],'files':[{'id':'COST_PORTABLE_'+str(i),'source':r,'bytes':(a.root/r).stat().st_size,'sha256':sha(r)} for i,r in enumerate(files)],
        'jobs':[{'id':'COSTS_SELECTED_CLOSED_STAGES','base':'.','script':script,'args':['--cas',{'input':'.'},'--source-root',{'input':'.'},
            '--source-index',{'input':index},'--comparator',{'input':T+'REFERENCIAS_CUATRO_NIVELES_CERRADO_R03/RESULTADOS_Y_RECURSOS.json'},
            '--json-only','--out','{output}'],'expected':C+'COSTOS_POR_ETAPA_N0_R03/COSTOS_POR_ETAPA_APD04.json','comparison':'bytes','timeout_seconds':900}],
        'pending_not_included':[{'id':'EARLY_FINAL_RESERVE','status':'WAITING_CLOSED_PRIMARY'},{'id':'FULL_EXACT_PROOF','status':'WAITING_ROOT'},{'id':'WORD_1_18','status':'NOT_EDITED_BY_THIS_AGENT'}]}
    with a.out.open('x',encoding='utf8',newline='\n') as f:json.dump(spec,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'new_Native_ticks':0,'ZIP_count':0,'new_portable_cost_recalc':1}))


if __name__=='__main__':main()
