"""Incorpora únicamente el cierre temprano archivado a prosa DRAFT, no al Word."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();assert not a.out.exists();r=a.root;L=r/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
    base=L/'manual/BORRADOR_MANUAL_APD04_R04_INFORMES_EXTERNOS.json';data=json.loads(base.read_bytes())
    folder=L/'controles_diseno/EVIDENCIA_RESERVA_TEMPRANA_CERRADA_N0_R08';result=json.loads((folder/'RECALCULO_CIENTIFICO.json').read_bytes());case=result['cases'][0]
    assert case['completed_work']==14 and case['planned_work_opportunities']==43
    assert case['new_committed_Native_IDs']==243 and case['committed_Native_status_enum_counts']=={'2':169,'5':74}
    data['schema']='APD04.same_logical_manual.chapter35.prose.DRAFT.R05.early_closed.external_verification'
    data['front']['cover_cut']='Edición documental 1.18. APD04 incorpora dos asociaciones adicionales, un taller situado y contrastes de actuación dependiente de historia. Corte operativo seleccionado: APD04_SEMILLA_COLABORADOR_R01 T654959. La reserva temprana terminó con14 de43 oportunidades y un futuro incierto, no una hora completa del protocolo. La prueba del ZIP Full exacto se acredita en un informe externo asociado a sus hashes.'
    additions=[{'style':'Heading2','text':'35 9 Reserva temprana de vista persistente'},
        {'style':'Normal','text':'APD04_PERSISTENCIA_TEMPRANA_RESERVA_R01 nació como bifurcación completa del pasado seguro MAIN T639374, no desdeT0 ni mediante reparación del REAL post10. Se preparó la misma vista persistente antes de la exposición. Su supervisión duró4624,535226 segundos; ese tiempo de pared no acredita haber completado la agenda reservada de60 minutos.'},
        {'type':'table','rows':[['Alcance','Resultado cerrado','Límite'],['Oportunidades','43 previstas;15 enviadas;14 con resultado;28 no enviadas','Una petición processing: event017; no contar actividad desconocida como cero'],['Actuación','7 INSPECT,2 WAIT,1 USE,4 NULL;10 válidas y11 elegibles','Ganancia antigua2 y calidad nueva2;0 WAIT correctas'],['Entradas Native','243 IDs comprometidos:169 aplicados y74 rejected_occupied','Sólo el alcance comprometido; no toda la actividad del futuro incierto']]},
        {'style':'Normal','text':'Se presentaron externamente las fuentes0 a6, no veinte fuentes inspeccionadas por Native. El único USE pidió clasifica, pero utilizó la caché27/v0 cuando el objeto real ya era14/v1 y su etiqueta no era pertinente al objetivo. El signo Native positivo era coherente con comparar27 frente a referencia20: no fue un error aritmético ni una generalización al valor14, que no se entregó a esa herramienta. No añadió ganancia útil. Las dos esperas se produjeron ante fuentes relevantes y no cumplieron el criterio nuevo.'},
        {'style':'Normal','text':'El último compromiso fue T664324, snapshot14d450f7495c5a9041ec706b7a3e55a335de9885c1e81a24aa657bddab886bbe, ocupación297588 y máximo s_reg4524. Los Jobs propios cerraron sin procesos activos, pero STOP no quedó confirmado. Se conservó apd04_early_persistent_r01_event_017 y el futuro no comprometido; no existe un FULL actual que lo convierta en continuación normal certificada. No se concluye destrucción global de memoria o recuperación autónoma. La vista temprana no resolvió en este dominio la conservación y selección útil sostenidas.'}]
    for item in data['chapter']:
        text=item.get('text','')
        if item.get('style')=='Heading2':
            for number in range(12,8,-1):
                if text.startswith('35 '+str(number)+' '):item['text']='35 '+str(number+1)+' '+text.split(' ',2)[2];break
        if 'El cierre de la reserva temprana se incorpora sólo desde sus primarios finales.'in text:
            item['text']=text.replace('El cierre de la reserva temprana se incorpora sólo desde sus primarios finales.','El cierre temprano se conserva con sus resultados, rechazos y futuro incierto; los eventos no ejecutados no cuentan como capacidades o fallos observados.')
        if item.get('style')=='Source' and text.startswith('Fuentes cerradas APD04:'):
            item['text']=text.replace('referencias convencionales48.','referencias convencionales48; reserva tempranaR08 con14 de43 oportunidades y108 verificaciones sin discrepancias.')
    at=next(i for i,x in enumerate(data['chapter'])if x.get('text')=='35 10 Estado seleccionado y diagnóstico de acceso')
    data['chapter'][at:at]=additions
    for pending in data['pending_root_updates']:
        if pending['id']=='EARLY_FINAL_RESERVE':pending.update(status='CLOSED_WITH_PRESERVED_UNCOMMITTED_FUTURE',
            final_committed_tick=664324,source='laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/controles_diseno/EVIDENCIA_RESERVA_TEMPRANA_CERRADA_N0_R08',
            action_before_approval='Cierre científico incorporado desde R08. No promover esta rama como FULL operativo ni borrar su pending.')
    data['prose_baseline']=str(base.relative_to(r));data['early_primary_sha256']=hashlib.sha256((folder/'RECALCULO_CIENTIFICO.json').read_bytes()).hexdigest()
    assert data['status']=='DRAFT' and all(all(len(row)==3 for row in x['rows'])for x in data['chapter']if x.get('type')=='table')
    with a.out.open('x',encoding='utf8',newline='\n')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'chapter_items':len(data['chapter']),'status':'DRAFT','Word_edited':False,'new_Native_ticks':0}))


if __name__=='__main__':main()
