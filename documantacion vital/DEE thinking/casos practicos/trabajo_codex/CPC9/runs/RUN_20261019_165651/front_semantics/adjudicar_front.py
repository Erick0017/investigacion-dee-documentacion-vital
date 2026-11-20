"""Format explicit bounded human adjudications, not threshold-to-meaning AI.

Only this auxiliary front is covered. Root E1 and other CPC9 fronts must be
adjudicated from their own primaries, not overwritten by this local matrix.
"""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def evidence(family,ids):
    return [{'path':'resultados/'+family+'/'+i+'/MEASUREMENTS.json',
             'sha256':sha(ROOT/'resultados'/family/i/'MEASUREMENTS.json')}for i in ids]

def flat_evidence(family,ids):
    return [{'path':'resultados/'+family+'/'+i+'.json','sha256':sha(ROOT/'resultados'/family/(i+'.json'))} for i in ids]


def main():
    plan=json.loads((ROOT/'revision/NSM65_PLAN_CPC9.json').read_text(encoding='utf8'))
    old_path=ROOT/'referencias/CPC8_NSM65_ESTADOS_HISTORICOS.json';old=json.loads(old_path.read_text(encoding='utf8'))
    old_by={e['id']:e for e in old['states']};entries=[]
    for item in plan['entries']:
        row=dict(item)
        row['historical_CPC8_not_current_E1']={'source':str(old_path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(old_path),'state':old_by[item['id']]}
        row['local_adjudication']={'level':'E0','state':'No adquisición semántica afirmada por este frente auxiliar',
            'reason':item['limitacion_y_evidencia_faltante'],'primary':[],
            'scope':'No modifica estados históricos, resultados de otros frentes ni E1 principal.'}
        for key,dim in row['dimensiones_A_J'].items():
            dim['estado']='NO_AFIRMADO_EN_ESTE_FRENTE_AUXILIAR'
            dim['motivo_individual']=item['limitacion_y_evidencia_faltante']
        if item['id']in('NSM65.ONE','NSM65.TWO'):
            two=item['id']=='NSM65.TWO'
            ids=['CB_P01_TWO','CB_H01_TWO_STATES']if two else['CB_P02_ONE_A','CB_P03_ONE_B','CB_H02_ONE_A_STATES','CB_H03_ONE_B_STATES']
            positive=evidence('COUNT_ACCESS_V2',ids)
            controls=evidence('COUNT_ACCESS_V2',['CB_C01_NO_FORM','CB_C02_UNPAIRED','CB_C03_NONE','CB_C04_NO_ROUTE','CB_C05_OFF_GUARD'])
            parent='CB_P01_TWO'if two else'CB_P03_ONE_B'
            causal=evidence('COUNT_ACCESS_CAUSAL_RESTORE',[parent+'_CUT',parent+'_SHAM',parent+'_RESTORE'])
            row['local_adjudication']={'level':'E2','state':'Asociación operacional y conservación auxiliar medidas',
                'reason':'Una misma señal opaca5 asociada después de función de contacto normalizado; lectura114/148 después de experiencia100, causalcut/sham y restore exactos. No se enseñan dos palabras conjuntamente.',
                'primary':positive+controls+causal,
                'scope':'N67/T0-171, unit2/threshold8, 28materiales75interfaces. Categoría operacional limitada por calibración y formato, no significado humano completo.',
                'separate_native_count_front':'Presence normalization PN prueba dosisvariables y cardinalidad acotada en OTRAS vidas, no generalización de esta misma señal aprendida bajo esas dosis.',
                'not_inferred':['No generalización lingüísticaE3 por variar sóloestados','No repertorio conjuntoUNO/DOS','No pertenenciaaE1delroot sinprimariospropios','No negación a partir deNONE']}
            for dim in('A_experiencia_causal','B_relacion_adquirida','C_funcion_posterior','D_forma_adquirida','E_retencion'):
                row['dimensiones_A_J'][dim]={'estado':'EJECUTADO_POSITIVO_AUXILIAR_CON_DOMINIO','evidencia':positive+causal,'alcance':row['local_adjudication']['scope']}
            row['dimensiones_A_J']['F_generalizacion']={'estado':'INVARIANCIA_PARAMETRICA_RESERVADA_PARCIAL','evidencia':positive[1:],
                'alcance':'Estados de actor/medio y papelA/B de una contribución, mismo mecanismo/geom/dosis; no generalización semántica universal.'}
            row['dimensiones_A_J']['I_E1_continuo']={'estado':'AUXILIAR_HASTA_EVIDENCIA_DE_INTEGRACION_ROOT','evidencia':[],
                'alcance':'No se suman individuos ni se cargaun snapshot de este frenteenMAIN.'}
            row['dimensiones_A_J']['J_aporte_externo']={'estado':'PREPARACION_Y_CURRICULO_EXPLICITOS','evidencia':positive,
                'alcance':'Normalización, umbral, guardas, tresrutas y agenda dellector preparados. Asociación y modificaciones físicas producidas porv27.'}
        elif item['id']in('NSM65.I','NSM65.YOU'):
            primaries=evidence('REL_PERSPECTIVE_AUX_V1',['RP_D01_A11_B31','RP_D02_A31_B11','RP_C04_EQUAL_EFFECT_ACTOR_A','RP_C05_EQUAL_EFFECT_ACTOR_B','RP_H01_NEW_EFFECTS','RP_H02_NEW_EFFECTS_ROLE_SWAP'])
            row['local_adjudication']={'level':'E0','state':'Ejecutado parcial: calibracióncontextual, negativo válido para identidad desdefirmasiguales',
                'primary':primaries,'reason':'Dos calibraciones adquiridas producen respuesta relativa, pero actorlabelsA/B conefectosiguales tienenRAW/clocks/recibos/observacionesidénticos. No acción nativa propia, no ligamiento adquiridoemisor/receptor.',
                'scope':'La insuficiencia pertenece a esta interfaz de efectos instrumentados, no es imposibilidadv27 ni refutación de identidadcausal porotrasrutas.'}
            row['dimensiones_A_J']['A_experiencia_causal']={'estado':'CALIBRACION_MATERIAL_EJECUTADA_NO_AGENCIA_PROPIA','evidencia':primaries}
            row['dimensiones_A_J']['C_funcion_posterior']={'estado':'COMPARACION_CONTEXTUAL_POSITIVA_SIN_DEIXIS','evidencia':primaries}
            row['dimensiones_A_J']['F_generalizacion']={'estado':'NUEVAS_CALIBRACIONES_Y_FIRMAS_NO_GENERALIZACION_YO_TU','evidencia':primaries[-2:]}
            action=flat_evidence('ACTION_TRACE_V2',['AV2_P01_A','AV2_P02_B','AV2_H01_NEW_DOSE_A','AV2_H02_NEW_DOSE_B'])
            cuts=flat_evidence('ACTION_TRACE_CAUSAL_RESTORE',['AV2_P01_A_cut_own','AV2_P01_A_cut_consequence','AV2_P01_A_sham','AV2_P01_A_restore','AV2_P02_B_cut_own','AV2_P02_B_cut_consequence','AV2_P02_B_sham','AV2_P02_B_restore'])
            row['native_prerequisite_measured']={'primary':action+cuts,
                'function':'Un emisor nativo conserva traza material local de acción y emite portador real que produce consecuencia común idéntica bajo inversión A/B. Lectores iguales distinguen traza actuante/ajena; cortar traza conserva consecuencia y cortar consecuencia conserva acceso propio.',
                'domain':'N67/T0-32, 26materiales, dos comandos equivalentes y tres lectores preparados; reservas c23+traslación, fuentes externamente solicitadas.',
                'semantic_nonpromotion':'La acción es solicitada externamente. No se aprendió una forma YO/TU, un ligamiento deíctico independiente de región ni una política de agencia. Es evidencia positiva de accesibilidad de origen causal; el negativo RP queda acotado a su interfaz anterior, no generalizado a v27.'}
            row['local_adjudication']['state']='Ejecutado parcial: traza causal accesible; deíxis no demostrada'
            row['local_adjudication']['reason']='El contraste RP de firmas iguales limita aquella interfaz. ACTION_TRACE añade una traza física del emisor que produce una función local diferente con la misma consecuencia común. Falta asociación y transferencia relativa YO/TU fuera de los bancos físicos preparados.'
            row['local_adjudication']['primary']+=action+cuts
        elif item['id']=='NSM65.NOT':
            positives=flat_evidence('CONTENT_REFLECTION_V2',['RR_P01_PLUS','RR_P02_MINUS','RR_H01_NEW_PLUS','RR_H02_NEW_MINUS'])
            controls=flat_evidence('CONTENT_REFLECTION_V2',['RR_C01_OFFPATH_PLUS','RR_C02_OFFPATH_MINUS','RR_C03_NO_R','RR_C04_NO_O','RR_C05_EQUAL'])
            causal=flat_evidence('CONTENT_REFLECTION_CAUSAL_RESTORE',['RR_P01_PLUS_cut_counterload','RR_P01_PLUS_sham','RR_P01_PLUS_restore','RR_P02_MINUS_cut_counterload','RR_P02_MINUS_sham','RR_P02_MINUS_restore'])
            row['native_prerequisite_measured']={'primary':positives+controls+causal,
                'function':'Operador preparado transforma activamente el mismo portador c7 desde +X a -X y desde -X a +X después de comparación nativa de dos operandos adquiridos. Fuera de ruta/carga intervenida produce respuesta activa c7/0, no silencio. Moore26 predice RAW antes de T82 y coincide en seis ramas cualificadas.',
                'domain':'Nuevo T0 N67, 21materiales, reflejo remoto ±9/contra21; función inicial reservada y causal, pero la tercera comparación original falla tras cambiar guardas.',
                'semantic_nonpromotion':'Contrariedad direccional no equivale a negación de contenidos diversos. El operador y sus recursos están preparados; no se adquirió una forma NO, alcance lógico ni selección aprendida del operador. E0 semántico permanece, no se convierte ausencia/cero en NO.'}
        elif item['id']in('NSM65.DO','NSM65.BECAUSE'):
            action=flat_evidence('ACTION_TRACE_V2',['AV2_P01_A','AV2_P02_B','AV2_C01_NO_ACTION','AV2_H01_NEW_DOSE_A','AV2_H02_NEW_DOSE_B'])
            cuts=flat_evidence('ACTION_TRACE_CAUSAL_RESTORE',['AV2_P01_A_cut_own','AV2_P01_A_cut_consequence','AV2_P01_A_sham','AV2_P01_A_restore'])
            row['native_prerequisite_measured']={'primary':action+cuts,
                'function':'Acción material emitida y consecuencia actual viajan por v27 sin sensor callback; traza del origen accesible aun con misma consecuencia. Cortes disocian acceso a traza y efecto común.',
                'semantic_nonpromotion':'La ley acción→consecuencia y geometría son preparadas, no una relación causal arbitraria aprendida ni agencia autodeterminada. Sin nueva forma HACER/PORQUE adquirida, sin nivel semántico positivo por extrapolación.'}
        elif item['id']in('NSM65.MORE','NSM65.THINK','NSM65.IF'):
            primaries=evidence('TWO_MEMORY_CONFIRMATORY',['TM_H01_R29_O17','TM_H02_R17_O29','TM_H03_ORDER_REVERSED_PLUS','TM_H04_ORDER_REVERSED_MINUS','TM_H05_TRANSLATED'])
            row['native_prerequisite_measured']={'primary':primaries,
                'function':'Comparación nativa preparada de dos operandos adquiridos por separado, conservados y consultados sin reinyección, con magnitudes/orden/traslación nuevos.',
                'semantic_nonpromotion':'No atribuir por estoPENSAR/SI general ni una nueva señal léxicaMÁS. La función física cuantitativa y su integración se registran separadamente.'}
        entries.append(row)
    out={'schema':'CPC9.NSM65.auxiliary_human_adjudication.v1','count':65,
         'scope':'Sólo frente_semantics. NO es resumen globalCPC9 ni inventario conjuntoE1. No se borran estados históricos ni resultados de otrosfrentes.',
         'catalogue_sha256':plan['catalogue']['sha256'],'human_authored_rule':'Los dosE2acotadosONE/TWO se adjudican explícitamente por primarios y controles; ningún score automático eleva un significado.',
         'entries':entries}
    path=ROOT/'revision/NSM65_ESTADOS_FRENTE_AUXILIAR.json';path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'path':str(path),'sha256':sha(path),'entries':len(entries)}))


if __name__=='__main__':main()
