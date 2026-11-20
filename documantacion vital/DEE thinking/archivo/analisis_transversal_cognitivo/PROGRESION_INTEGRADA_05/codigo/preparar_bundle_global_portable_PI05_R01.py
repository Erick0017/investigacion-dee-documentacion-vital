"""Prepare compact exact global features; copies only, never engine or ZIP."""
from pathlib import Path
import hashlib,json,runpy,shutil
P5=Path(__file__).resolve().parent.parent
DEST=P5/'fuentes/RECALCULO_GLOBAL_PORTABLE_PI05_R01'

def info(p):
    b=Path(p).read_bytes();return {'path':str(Path(p).resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def copy(source,target):
    before=info(source);target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():raise FileExistsError('No overwrite')
    shutil.copyfile(source,target);after=info(source);actual=info(target)
    if before!=after or actual['sha256']!=before['sha256']or actual['bytes']!=before['bytes']:raise ValueError('Copy/source changed')
    return before
def main():
    if DEST.exists():raise FileExistsError('Preserve existing bundle')
    DEST.mkdir();mapping=[];manifests={}
    recipes={'REAL':'INVENTARIO_REAL_FI_GLOBAL_R01','GUARD':'INVENTARIO_GUARD_FI_GLOBAL_R01','SHAM':'INVENTARIO_SHAM_FI_GLOBAL_R01','B2':'INVENTARIO_REAL_B2_GLOBAL_R01','NONE':'INVENTARIO_NONE_FI_GLOBAL_R01','YOKE':'INVENTARIO_YOKE_FI_GLOBAL_R01'}
    for alias,name in recipes.items():
        source=P5/'control'/name;rows=[]
        for p in sorted(source.iterdir()):
            if p.is_file():rows.append({'member':p.name,'source':copy(p,DEST/'casos'/alias/p.name)})
        mapping.append({'alias':alias,'group':'principal'if alias in('REAL','GUARD','SHAM')else'contrastes_adicionales','source_directory':str(source.resolve()),'copied_directory':'casos/'+alias,'members':rows,'runtime_requires_original_paths':False})
    code=P5/'codigo/recalcular_inventarios_globales_PI05_R02.py';copy(code,DEST/'codigo'/code.name)
    copy(P5/'codigo/verificar_bundle_global_PI05_R01.py',DEST/'verificar_y_recalcular.py')
    evidence=['control/CONTRASTE_CAUSAL_GUARD_SHAM_PI05_R01.json','control/CONTRASTE_SNAPSHOT_COMPLETO_B3_B2_PI05_R01.json','control/CONTRASTE_ORGANIZATIONAL_B3_B2_PI05_R01.json','control/ACUERDO_DOS_RECALCULOS_REAL_NONE_R01.json','control/FISICA_RP_GUARDIA_REPRODUCIDA_PI05_R01.json','fuentes/KERNEL_V27_EXTRACTO_ACTUALIZACION_185_352.txt']
    evidence_sources=[]
    for name in evidence:evidence_sources.append(copy(P5/name,DEST/'evidencias'/Path(name).name))
    cold=json.loads((P5/'control/FISICA_RP_GUARDIA_REPRODUCIDA_PI05_R01.json').read_text(encoding='utf-8'))
    if cold['actual_replay_status']!='COMPLETED'or not cold['all_physical_and_input_equalities_hold']:raise ValueError('Only an actual closed cold replay proof')
    coldtrial=Path(cold['replay_primary']['file'])
    if info(coldtrial)['sha256']!=cold['replay_primary']['sha256']:raise ValueError('Replay primary hash mismatch')
    copy(coldtrial,DEST/'evidencias/COLD_NATIVE_GUARDIA_TRIAL.json')
    module=runpy.run_path(str(code),run_name='pure_bundle_preparation')
    specs=[('REAL_GUARD','REAL','GUARD','REAL_GUARD_R02','principal'),('REAL_SHAM','REAL','SHAM','REAL_SHAM_R02','principal'),('GUARD_SHAM','GUARD','SHAM','GUARD_SHAM_R02','principal'),('B3_B2','REAL','B2','REAL_B3_B2_R02','adicional'),('REAL_NONE','REAL','NONE','REAL_NONE_R01','adicional'),('REAL_YOKE','REAL','YOKE','REAL_YOKE_R01','adicional')]
    expected=[]
    for identifier,aa,bb,old,group in specs:
        original=P5/f'control/RECALCULO_PORTABLE_{old}/RECALCULO_GLOBAL_PORTABLE.json';original_data=json.loads(original.read_text(encoding='utf-8'))
        sa=json.loads((DEST/'casos'/aa/'RESUMEN_GLOBAL.json').read_text(encoding='utf-8'));sb=json.loads((DEST/'casos'/bb/'RESUMEN_GLOBAL.json').read_text(encoding='utf-8'));ev=module['event_diff'](sa,sb)
        expected.append({'id':identifier,'a':aa,'b':bb,'group':group,'source_recalculation':info(original),'frames':original_data['frames'],'events':{'count_a':ev['count_a'],'count_b':ev['count_b'],'common':ev['common_channel_tick_events'],'identical_common':ev['identical_common_requests'],'changed_common':len(ev['request_differences']),'only_a':len(ev['events_only_a']),'only_b':len(ev['events_only_b']),'receipt_outcome_differences':len(ev['receipt_outcome_differences'])}})
    (DEST/'ESPERADOS_CONGELADOS.json').write_text(json.dumps({'schema':'DEE.PI05.portable_global.frozen_documentary_expectations.R01','Native_ticks':0,'comparisons':expected},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (DEST/'MAPA_PROCEDENCIA_Y_REQUISITOS.json').write_text(json.dumps({'schema':'DEE.PI05.portable_global.alias_map.R01','materials':mapping,'additional_evidence_sources':evidence_sources,'requires':['CPython3.10+ standard library','All listed local bundle members and their hashes'],'does_not_require':['DEE engine/WHL/PYD','Original workspace','A running owner','Network or credentials'],'not_full_operational_backup':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    readme='''DEE PI05 · Recálculo global transportable\n\nEste paquete es evidencia documental y una herramienta externa, no otro ente ni un respaldo operativo. No ejecuta DEE y no proporciona datos al participante.\n\nTres condiciones principales: REAL sin guarda, GUARD en la ruta y SHAM fuera de ruta. Los tres contrastes principales vuelven a calcular D(T) global. B2, NONE y YOKE son controles adicionales: NO son experiencias sumables de una misma vida ni réplicas independientes. B4 no se ejecutó.\n\nRequisitos: CPython3.10+ con biblioteca estándar. No requiere motor, originales, red ni rutas D:/C:. Las rutas históricas en procedencias son texto, no dependencias.\n\nVerificar bytes sin calcular: python verificar_y_recalcular.py\nRecálculo principal: python verificar_y_recalcular.py --recalcular --grupo principal --destino ../resultado_principal_NUEVO\nTodos los seis contrastes: python verificar_y_recalcular.py --recalcular --grupo todos --destino ../resultado_todos_NUEVO\nEl destino debe ser nuevo; nunca se modifica el paquete ni un estado operativo.\n\nCada condición contiene69fronteras N67. RAW completo se reconstruye rellenando con0 las posiciones no incluidas y comprobando SHA-256 original de300763uint64LE. Clocks uniformes también se reconstruyen y verifican contra su SHA original. Si no son uniformes, esta receta rechaza el caso y exige el codec completo; no inventa clocks. Se conservan RAW!=0 con state0.\n\nCobertura: q−56…q+10, q+75 yq+142. Los huecos no son trayectorias observadas. Coincidir por carga no identifica un portador. RAW/clocks iguales no equivalen al estado operativo completo: B2/B3convergen físicamente desde817885, pero organizational conserva load17/18.\n\nEl archivo evidencias/FISICA_RP_GUARDIA_REPRODUCIDA_PI05_R01.json informa una reproducción Native ya ejecutada localmente desde un prefijo completo:198ticks,177/177entradas, mismos69hashes completos y ambos lectores. Su primario literal se incluye. Los comandos anteriores SOLO recalculan registros; no repiten esa ejecución, su adquisición ni guardado/reapertura. Los snapshots/prefijos grandes siguen en los localizadores históricos.\n\nGUARD/SHAM demuestra protección P0 preparada en el dominio medido, no regulación aprendida/iniciativa autónoma. Los negativos y los controles quedan conservados. Este paquete no califica globalmente al ente.\n'''
    (DEST/'00_LEER_PRIMERO.txt').write_text(readme,encoding='utf-8')
    files=[{'path':p.relative_to(DEST).as_posix(),'bytes':p.stat().st_size,'sha256':info(p)['sha256']}for p in sorted(DEST.rglob('*'))if p.is_file()]
    (DEST/'MANIFIESTO_SHA256.json').write_text(json.dumps({'schema':'DEE.PI05.portable_global.content_manifest.R01','files':files,'self_hash_excluded':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'directory':str(DEST.resolve()),'files':len(files)+1,'bytes':sum(p.stat().st_size for p in DEST.rglob('*')if p.is_file()),'manifest':info(DEST/'MANIFIESTO_SHA256.json'),'Native_ticks':0,'copied_only_no_ZIP':True}))
if __name__=='__main__':main()
