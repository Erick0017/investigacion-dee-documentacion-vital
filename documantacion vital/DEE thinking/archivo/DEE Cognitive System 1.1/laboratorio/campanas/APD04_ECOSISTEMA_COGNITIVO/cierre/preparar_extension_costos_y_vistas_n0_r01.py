"""Especificación explícita N0 siguiente al CAS R03, no sella ni ejecuta Native."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();assert not a.out.exists()
    L='laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/'; C=L+'cierre/';T=L+'controles_diseno/'
    def sha(rel):return hashlib.sha256((a.root/rel).read_bytes()).hexdigest()
    components=[]
    for ident,folder in [('CONVENTIONAL_48',T+'REFERENCIAS_CUATRO_NIVELES_CERRADO_R03'),('LATE_VIEWS_3',T+'EVIDENCIA_TRES_VISTAS_CERRADAS_N0_R03')]:
        components.append({'id':ident,'source':folder,'manifest':'MANIFIESTO.json','manifest_sha256':sha(folder+'/MANIFIESTO.json')})
    paths=[C+'envolver_recalculo_referencias_apd04_n0_r01.py',C+'recalcular_costos_por_etapa_apd04_n0_r03.py',
        C+'COSTOS_POR_ETAPA_N0_R03/COSTOS_POR_ETAPA_APD04.json',C+'COSTOS_POR_ETAPA_N0_R03/COSTOS_POR_ETAPA_APD04.md']
    spec={'schema':'APD04.CAS.explicit_closed_extension_spec.N0.R04','base':C+'CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R03',
        'base_manifest_sha256':sha(C+'CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R03/MANIFIESTO_CAS.json'),
        'components':components,'files':[{'id':'EXPLICIT_'+str(i),'source':rel,'bytes':(a.root/rel).stat().st_size,'sha256':sha(rel)} for i,rel in enumerate(paths)],
        'jobs':[{'id':'CONVENTIONAL_48_ARCHIVED','base':'.','script':C+'envolver_recalculo_referencias_apd04_n0_r01.py',
            'args':['--evidence',{'input':components[0]['source']},'--out','{output}'],'expected':components[0]['source']+'/RECALCULO_INDEPENDIENTE.json','comparison':'bytes','timeout_seconds':900},
            {'id':'LATE_VIEWS_3','base':'.','script':components[1]['source']+'/recalcular_vistas_y_reserva_r03_n0_r01.py',
            'args':['--recalc',{'input':components[1]['source']},'--output','{output}'],'expected':components[1]['source']+'/RECALCULO_CIENTIFICO.json','comparison':'bytes','timeout_seconds':900}],
        'pending_not_included':[{'id':'EARLY_FINAL_RESERVE','status':'WAITING_CLOSED_PRIMARY'},{'id':'FULL_EXACT_PROOF','status':'WAITING_ROOT'},{'id':'WORD_1_18','status':'NOT_EDITED_BY_THIS_AGENT'}]}
    with a.out.open('x',encoding='utf8',newline='\n') as f:json.dump(spec,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'components':len(components),'new_Native_ticks':0,'ZIP_count':0}))


if __name__=='__main__':main()
