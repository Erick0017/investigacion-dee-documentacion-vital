"""Añade panel24 real y entrypoint corto de vistas; no aplica metadata ni crea ZIP."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();assert not a.out.exists()
    L='laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/';C=L+'cierre/';T=L+'controles_diseno/';E='evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/'
    def sha(rel):return hashlib.sha256((a.root/rel).read_bytes()).hexdigest()
    folder=E+'SEMILLA_PANEL24_DIAGNOSTICO_R01/EVIDENCIA_PORTABLE_N0_R02'
    files=[C+'envolver_recalculo_archivado_apd04_n0_r03.py',T+'recalcular_vistas_y_reserva_r03_n0_r04.py']
    assert sha(folder+'/MANIFIESTO_R02.json')=='3140483d85644aa8dc3425fe60e1588dde0257c14e4fcc3efdf8d5fadfdf0080'
    spec={'schema':'APD04.CAS.explicit_closed_extension_spec.N0.R06','base':C+'CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R05',
        'base_manifest_sha256':sha(C+'CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R05/MANIFIESTO_CAS.json'),
        'components':[{'id':'EXACT_SEED_DIAGNOSTIC_PANEL24','source':folder,'manifest':'MANIFIESTO_R02.json','manifest_sha256':sha(folder+'/MANIFIESTO_R02.json')}],
        'files':[{'id':'PORTABLE_PANEL_'+str(i),'source':r,'bytes':(a.root/r).stat().st_size,'sha256':sha(r)} for i,r in enumerate(files)],
        'jobs':[{'id':'EXACT_SEED_DIAGNOSTIC_PANEL24','base':'.','script':files[0],
            'args':['--evidence',{'input':folder},'--script','recalcular_panel24_r02.py','--out','{output}'],'expected':folder+'/RECALCULO_R02.json','comparison':'bytes','timeout_seconds':900},
            {'id':'LATE_VIEWS_SHORT_PATH_ENTRYPOINT_R04','base':'.','script':files[1],
            'args':['--recalc',{'input':T+'EVIDENCIA_TRES_VISTAS_CERRADAS_N0_R03'},'--output','{output}'],
            'expected':T+'EVIDENCIA_TRES_VISTAS_CERRADAS_N0_R03/RECALCULO_CIENTIFICO.json','comparison':'bytes','timeout_seconds':900}],
        'pending_not_included':[{'id':'EARLY_FINAL_RESERVE','status':'WAITING_CLOSED_PRIMARY'},{'id':'FULL_EXACT_PROOF','status':'WAITING_ROOT'},{'id':'WORD_1_18','status':'NOT_EDITED_BY_THIS_AGENT'}]}
    with a.out.open('x',encoding='utf8',newline='\n') as f:json.dump(spec,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'new_Native_ticks':0,'ZIP_created':0,'diagnostic_only_not_source_seed_queried':True}))


if __name__=='__main__':main()
