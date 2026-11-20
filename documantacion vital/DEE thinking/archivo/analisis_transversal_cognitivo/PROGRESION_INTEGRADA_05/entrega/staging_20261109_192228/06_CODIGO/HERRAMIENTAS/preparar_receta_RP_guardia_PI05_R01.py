"""Prepare additive RP recipe only. Never writes product/RP or executes DEE."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;P=H.parent;OUT=H/'RP_GUARDIA_PI05_R01_PREPARADA'
RECIPE='pi05_guardia_y_sham_transito_R01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(label,path,expected,operation='value',other=None):
    values=[{'step':'trial','path':path}]
    if other is not None:values.append({'step':'trial','path':other})
    return {'label':label,'operation':operation,'values':values,'expected':expected}
def main():
    if OUT.exists():raise ValueError('Preserve prior recipe preparation')
    base=['result','rows',0];variants={}
    for variant,mode,expected in(('guardia','eci01-pi05-fiplus-guardia',1),('sham','eci01-pi05-fiplus-sham',-1)):
        variants[variant]={'batches':[[{'label':'trial','literal':{'modo':mode,'izquierda':14,'derecha':3,'captura':'global'},
           'feedback':'omit','read_path':base+['early_physical_choice'],'expected':expected,
           'stop_on_NULL':True,'stop_on_unapplied_receipt':True,'receipt_paths':[base+['requests']]}]],
           'final_checks':[check('old_start', ['before_tick'],817876),check('old_end',['after_tick'],818074),
               check('old_age198',['after_tick'],198,'difference',['before_tick']),
               check('fixed_q4',base+['calendar','early_reader_tick'],817936),
               check('fixed_q6',base+['calendar','old_reader_tick'],817938),
               check('old176_plus_one',base+['Native_inputs','unique_requested'],177),
               check('all177_admitted',base+['Native_inputs','applied'],177),
               check('zero_rejections',base+['Native_inputs','rejected_or_other'],0),
               check('support_initial_RAW0',base+['support','before','raw'],'0'),
               check('support_persistent_SEM4',base+['support','after','raw'],str(4<<60)),
               check('support_exact_birth_tick',base+['support','request','tick'],817878),
               check('support_exact_load0',base+['support','request','payload'],0),
               check('support_admitted',base+['support','request','receipt','status'],'applied'),
               check('no_preparation_advance',base+['support','no_tick_advance_to_prepare'],True),
               check('no_host_RAW_clock_edits',base+['support','host_RAW_or_clock_writes'],0)],
           'native_receipt_expectations':{'unique_requested':177,'applied':177,'rejected':0,'pending_or_other':0}}
    recipe={'schema':'DEE.reproduction.recipe.v1','id':RECIPE,
       'title':'PI05: contraste causal P0 de guarda y sham sobre tránsito previo a FIplus',
       'revision':'R01_PREPARADA_REPLAY_NATIVE_PENDIENTE','prefix':'PI03_PI05_REAL_PREFI_T817876',
       'code_capsule_key':'PI05_TRANSITO_GUARDIA_R01','required_life_prefix':'ECI02_PI03_REPRO_PI04_PI05_',
       'reproduction_enabled':True,'requires_explicit_material':True,'variants':variants,
       'modalities':{'A':'Documentos y futuros publicados; esta receta no ejecuta recálculo documental por sí sola',
            'B':'Reproducción de intervención legal P0 desde un estado completo real preFI, sólo en copia',
            'C':'No reproduce adquisición del ente ni supone reenseñanza',
            'D':'No atribuir al principal; sólo después de adopción explícita con evidencia separada',
            'E':'Prevenir un contacto en un clon es soporte preparado, no recuperación autónoma o readquisición'},
       'assistance':'El operador prepara oportunidad, interfaz fija, condiciones guardia/sham y comparación14/3. DEE conserva toda la física de los176inputs, el tránsito y los lectoresq4/q6. Ningún resultado esperado entra al literal material.',
       'limitations':'PREPARADA, no resultado Native verificado. +1guarda y−1sham son predicciones preregistradas del evaluador, no respuestas implantadas. Guarda/sham añaden exactamente1nacimientoSEM4state0carga0 a817878; mismaedad198. Sourcecompartido,noindividuosindependientes. Cualquier rechazo/NULL/fallo se conserva; ningún reinicio, limpieza, puerto favorable o transferencia de memoria. El guard persistente exige comprobar funciones posteriores. Esta receta ensaya una vez y no reinserta soporte durantecontinuación.',
       'verification':{'state':'PREPARADA_REPLAY_NATIVE_PENDIENTE','new_generic_RP_Native_replay':False,
            'guard_or_sham_material_execution_by_preparer':False,'scientific_success_not_assumed':True,
            'hypotheses_evaluator_only':{'guardia':1,'sham':-1},'Native_verified_after_actual_closed_registration_only':True},
       'usage':{'listar':'sistema/gestionar.py reproducibilidad listar',
            'verificar':'sistema/gestionar.py reproducibilidad verificar '+RECIPE,
            'reproducir':'sistema/gestionar.py reproducibilidad reproducir '+RECIPE+' --variante guardia --vida ECI02_PI03_REPRO_PI04_PI05_RP_GUARD_01 --destino <DESTINO_ABSOLUTO_NUEVO> --material'},
       'blockers':[]}
    OUT.mkdir();(OUT/'recetas').mkdir()
    file=OUT/'recetas'/(RECIPE+'.json');file.write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    material={'schema':'DEE.PI05.RP.material_request.R01','status':'PENDIENTE_PRESERVACION_Y_REGISTRO_ROOT',
       'complete_pair':{'source':str(P/'pares/REAL_PREFI_T817876'),'manifest_sha256':sha(P/'pares/REAL_PREFI_T817876/EXPORTACION_SERVICIO.json'),
            'future_product_relative':'reproducibilidad/materiales/PI03_PI05_REAL_PREFI_T817876','alias':'PI03_PI05_REAL_PREFI_T817876'},
       'full_code_capsule':{'future_product_relative':'reproducibilidad/codigo_preservado/PI05_TRANSITO_GUARDIA_R01',
            'key':'PI05_TRANSITO_GUARDIA_R01','manifest':'SISTEMA_CODIGO.json','manifest_sha256':None,
            'requirement':'Root must preserve complete final exact source capsule including guard/dispatcher; not just this4file delta. Pin actual manifest before registration.'},
       'frozen_guard_module':{'sha256':sha(H/'FUENTES_GUARDIA_PI05_R01_SELLADAS/capacidades/pi05_guardia_transito_R01.py')},
       'frozen_guard_protocol':{'sha256':sha(H/'FUENTES_GUARDIA_PI05_R01_SELLADAS/capacidades/PROTOCOLO_PI05_GUARDIA_R01.json')},
       'generic_RP_Python_or_gestor_changes_required':False,'Native_executed':False}
    m=OUT/'SOLICITUD_MATERIALES.json';m.write_text(json.dumps(material,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'recipe':str(file),'recipe_sha256':sha(file),'material_request':str(m),'Native_executed':False}))
if __name__=='__main__':main()
