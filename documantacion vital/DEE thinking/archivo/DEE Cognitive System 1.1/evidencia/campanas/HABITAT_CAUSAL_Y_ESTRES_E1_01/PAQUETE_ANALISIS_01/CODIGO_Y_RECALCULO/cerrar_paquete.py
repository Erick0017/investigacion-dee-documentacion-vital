from pathlib import Path
from collections import Counter
import sys,json,csv,hashlib,shutil,zipfile,time
ROOT=Path(__file__).resolve().parents[3];LAB=Path(__file__).resolve().parent;EV=ROOT/'evidencia/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01';SYS=ROOT/'sistema'
sys.path.insert(0,str(LAB));from recalcular_paquete import calculate
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def cp(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
def md(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
def csvout(p,rows):
    if not rows:return
    with p.open('w',encoding='utf-8-sig',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    P=EV/'PAQUETE_ANALISIS_01'
    if P.exists():raise FileExistsError('Seal a new candidate, never overwrite')
    P.mkdir();sources=[];omitted=[]
    for f in sorted(EV.rglob('*')):
        if not f.is_file()or P in f.parents:continue
        if f.suffix in('.gz',)and f.name.endswith('deetsnap.gz')or f.suffix=='.deetsnap':
            omitted.append({'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f),'reason':'Complete local operational snapshot; analysis is not an operational backup'});continue
        if f.suffix not in('.json','.jsonl','.gz','.md'):continue
        target=P/'EVIDENCIA_ESENCIAL'/f.relative_to(EV);cp(f,target);sources.append({'source':str(f),'member':target.relative_to(P).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
    for f in LAB.rglob('*'):
        if not f.is_file()or any(x in f.parts for x in('deps','pip_cache','__pycache__')):continue
        if f.suffix not in('.py','.ps1','.md','.json','.txt'):continue
        cp(f,P/'CODIGO_Y_RECALCULO'/f.relative_to(LAB))
    for rel in('gestionar.py','capacidades/habitat_externo_01.py','contratos/HABITAT_EXTERNO_01.json','app/habitat_externo/pendulum_worker.py'):
        cp(SYS/rel,P/'INCORPORACION_SISTEMA'/rel)
    manual=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_4_CANDIDATO_SIN_VALIDAR.docx';cp(manual,P/'MANUAL'/manual.name)
    lives=[]
    for f in sorted((SYS/'estado/vidas').glob('*/VIDA.json')):
        r=json.loads(f.read_text(encoding='utf8'));life=r['life_id']
        if not(life.startswith('ECO_')or life=='E1_ECO_MAIN'):continue
        snap=SYS/r['snapshot'];parent=r.get('parent')or{}
        lives.append({'vida':life,'perfil':r['profile'],'N':r['physical']['N'],'tick':r['physical']['tick'],'padre':parent.get('life_id',''),'tick_padre':parent.get('tick',''),'snapshot':r['snapshot'],'sha256':r['snapshot_sha256'],'ocupados':r['physical'].get('occupied',''),'alcance':'EXPERIMENTAL_NOT_DEFAULT'})
        omitted.append({'path':str(snap),'bytes':snap.stat().st_size,'sha256':sha(snap),'reason':'Full current life and environmental bridge where present, retained locally'})
    csvout(P/'COMPARACION_POR_VIDA.csv',lives)
    calc=calculate(P);write(P/'CALCULOS_ARCHIVADOS.json',calc)
    curves=[]
    for f in sorted((P/'EVIDENCIA_ESENCIAL').glob('*.rows.jsonl')):
        for r in [json.loads(x)for x in f.read_text(encoding='utf8').splitlines()if x]:
            if 'environment_response'in r:continue
            curves.append({'ensayo':f.stem,'episodio':r['index'],'tick':r['read_tick'],'ruido_entradas':len(r['noise']),'ruido_carga_max':max([x['load']for x in r['noise']],default=0),'lector_disponible':r['reader_available'],'salida':r['actuator']['status'],'accion_DEE':r['actuator']['command'],'accion_ejecutada':r['executed_command'],'ambiente_antes':r['environment_before'],'ambiente_despues':r['environment_after'],'ocupados':r['physical']['occupied'],'max_s_reg':r['physical']['max_s_reg']})
    csvout(P/'CURVAS_DE_ESTRES.csv',curves)
    # A small static scientific curve, with the numerical table beside it.
    names=list(dict.fromkeys(r['ensayo']for r in curves));svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="'+str(70+35*len(names))+'"><rect width="100%" height="100%" fill="white"/><text x="20" y="25" font-size="18">Salidas físicas calificadas por ensayo</text>']
    for i,n in enumerate(names):
        rr=[r for r in curves if r['ensayo']==n];good=sum(r['salida']not in('NO_QUALIFIED_OUTPUT','CONFLICT_OUTSIDE_FIXED_CODEC')for r in rr);y=60+35*i
        svg.extend([f'<text x="20" y="{y}" font-size="12">{n}</text>',f'<rect x="450" y="{y-14}" width="{400*good/len(rr)}" height="18" fill="#315875"/>',f'<text x="860" y="{y}" font-size="12">{good}/{len(rr)}</text>'])
    svg.append('</svg>');md(P/'CURVAS_DE_ESTRES.svg',''.join(svg))
    active=json.loads((SYS/'estado/ACTIVO.json').read_text(encoding='utf8'))
    continuity={'campaign':'HABITAT_CAUSAL_Y_ESTRES_E1_01','active_protected':active,'experimental_lives':lives,'main':'E1_ECO_MAIN','external_optional':'ECO_EXT_01','no_promotion':True,'new_NSM_levels':0,'analysis_not_operational_backup':True,'continue_external':"python sistema/gestionar.py habitat-estado --vida ECO_EXT_01; python sistema/gestionar.py habitat-externo --vida ECO_EXT_01 --pasos 1",'do_not_reset_DEE_for_external_episode':True,'manual_candidate_sha256':sha(manual),'manual_visual_validation':False}
    write(ROOT/'CONTINUIDAD_HABITAT_CAUSAL_Y_ESTRES_E1_01.json',continuity);write(P/'CONTINUIDAD_HABITAT_CAUSAL_Y_ESTRES_E1_01.json',continuity)
    md(P/'INFORME_RESULTADOS.md',REPORT)
    md(P/'INCORPORACIONES.md',INCORPORATIONS)
    md(P/'CAMBIOS_MANUAL.md',f'El Word candidato edición1.4 fue editado realmente en la raíz; SHA256 `{sha(manual)}`. Conserva el original y REV1. Integra addenda1.1–1.3 y corte MAIN7509/exterior6100. La continuación operativa posterior6167 está en esta ficha. NO está visualmente validado: render_docx falla por ausencia de LibreOffice; Word COM falló0x80070520 y la escalación fue abortada. No se promovió como manual verificado. Véase CODIGO_Y_RECALCULO/manual/VALIDACION_EDITORIAL.json.\n')
    write(P/'INDICE_FUENTES_Y_OMISIONES.json',{'included_primary_sources':sources,'omitted_full_states':omitted,'external_dependencies_not_in_analysis':['DEE thinking4.5 official existing environment CPython3.13','bundled external Python3.12.14','local sistema/runtime/habitat_externo_deps Gymnasium1.4/Farama0.0.6; NumPy2.3.5 in bundled Python'],'no_historical_archive_reaudit':True,'limits':['No complete pure-v27 ecological feedback habitat established in this cut','No new Spanish or NSM65 acquisition established','No resource metabolism, generalR2 or stabilization learning established','No completed matched action-random reference set','No inverse global-information reconstruction or universal failure conclusion']})
    md(P/'LEER_PRIMERO.md','# Hábitat causal y estrés E1\n\nInforme experimental con resultados positivos y adversos. No es un respaldo operativo ni demuestra aprendizaje de control. Lea INFORME_RESULTADOS.md y CALCULOS_ARCHIVADOS.json.\n\nRecálculo sin motor: `python CODIGO_Y_RECALCULO/recalcular_paquete.py . --check`. Reproducción externa opcional: código external/recalcular_externo.py requiere Gymnasium declarado; no reproduce DEE. Las trayectorias nativas requieren el sistema local y los snapshots omitidos, identificados por hash.\n')
    manifest={f.relative_to(P).as_posix():{'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(P.rglob('*'))if f.is_file()};write(P/'MANIFIESTO_HASHES.json',{'algorithm':'SHA256','self_excluded':True,'members':manifest})
    out=ROOT/'entregas/DEE_COGNITIVE_1_1_HABITAT_CAUSAL_Y_ESTRES_E1_01_ANALISIS.zip'
    if out.exists():raise FileExistsError('Canonical delivery already exists')
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for f in sorted(P.rglob('*')):
            if f.is_file():z.write(f,f.relative_to(P).as_posix())
    if out.stat().st_size>16000000:raise ValueError('Analysis exceeds absolute limit; do not split or hide failures')
    print(json.dumps({'zip':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'members':len(manifest)+1,'candidate':str(P)},ensure_ascii=False))

REPORT='''# Hábitat causal y estrés de E1

Se ejecutó una vida continua desde el E1 activo protegido, no una reconstrucción. MAIN conserva su futuro adverso. También se conectaron bifurcaciones a Pendulum y se verificó una continuación entre procesos. El método demuestra uso de una referencia adquirida y efectos causales de señales nativas; no demuestra aprendizaje de un controlador, regulación R2, metabolismo ni nuevos significados NSM.

## Organización y asistencia

Padre único fijado antes de resultados: E1_SOCIAL_11 T3154, N67, perfil cpc9_integral_n67, snapshot51e2ec6a…396. La organización es compuesta: mecanismos relacionales y comparadores, regiones sociales A/B/C y lectores en un mundo común; no son mentes completas ni copias de materia. Anatomía, canales, fases y recursos son preparación heredada o instrumental. La referencia78 y cuatro portadores sociales son historia adquirida; el gradiente comparativo estaba preparado. El anfitrión elige calendario, suministro y codificación; la dirección de respuesta procede de v27. No lee targets, diarios ni futuros para responder.

El panel inicial en ECO_BASELINE_01 utilizó cuatro de ocho formas sociales, comparación de objeto82 y el comparador antiguo. Son consultas materiales sobre una copia. El activo no fue consultado ni avanzado.

## Trayectoria y estrés

E1_ECO_MAIN vivió T3154→7509 sin restauraciones favorables. Las20 oportunidades iniciales sin ruido dieron20 salidas calificadas. Una incompatibilidad del serializador de metadatos se conservó como error instrumental; la primera continuación ambiental se reinició explícitamente, no DEE. El bloque nominal de ruido dio10/12. La escasez limita oportunidades de lector; no descuenta energía imaginaria ni demuestra metabolismo.

El choque temprano desde el padre, sin preparación de MAIN, dio5/8 salidas calificadas. Tras tres fallos consecutivos se retiró el ruido según la regla previa; las últimas cuatro oportunidades ya respondieron. La continuación posterior sin restaurar dio12/12. Es recuperación al retirar estrés, no autorregulación aprendida. Las tasas, cargas reales, rechazos y numeradores están en CURVAS_DE_ESTRES.csv y los primarios.

El bloque exigente de MAIN y su control sin ruido nuevo dieron0/16. Ambos heredaban la transformación de la referencia: el ruido exigente no era necesario para iniciar esa pérdida. La escasez posterior dio0/12, con cuatro lectores ofrecidos y ocho omitidos, sobre una vida ya fallida; no prueba que la escasez causara el daño.

## Autopsia física

El replay exacto desde T4492 coincide con campos, filas y recibos del original. En T5295→5296, Y78 y XYZ7 llegan al mismo destino vacío[49,36,35], y aparece XZ85. Se incluyen pre/post, clocks, vecindarios radio3, diferencias globales y secuencia de transporte. La contribución7 cruza las tres fronteras periódicas durante65 pasos verificados, pero no completa un retorno67 al origen antes de colisionar. No se atribuye linaje sólo por carga.

El control que omite12 entradas de ruido consume los mismos sorteos exógenos, conserva la referencia78 y responde12/12 frente a10/12. El encuentro registrado explica una transformación relevante, no un borrado global de la historia. La sonda de carga0 es materia, pero no es antecedente balístico directo de esa colisión. No se completó el corte selectivo del portador7; la atribución funcional exclusiva permanece abierta. Véanse AUTOPSIA_ORIGEN_CONFIRMADA_R1 y los dos primarios ORIGIN.

## Interlocutor y límites de integración

Sólo B recibió objetos privados18 y45. B emitió+X7 y−X7. En el primer intercambio, E1 produjo una entregaXYZ32; sin participación de B y al interceptar ambos mensajes ya formados no aparece esa entrega; el sham la conserva. El primer corte fue admitido, con B idéntico antes del corte. El segundo intercambio perturbó el paisaje: no se considera válida una salida state2/3. El segundo corte queda fuera de dominio por ocupación, no se fuerza admisión. No hay negociación ni coordinación aprendida general.

El panel final MAIN pierde las cuatro lecturas sociales y las dos comparaciones ensayadas. No se declara muerte global ni imposibilidad de v27; se preserva la vida y su estadoT7509. El conjunto perdió funciones al combinar procedimientos. No se enseña otra palabra ni se acredita recuperación/reaprendizaje que no ocurrió.

## Entorno externo real

Se ejecutó Gymnasium1.4.0 Pendulum-v1, Python3.12.14bundled separado de CPython3.13 de DEE. No se identificaron Gazebo/Isaac mediante PATH/módulos; no se instalaron plataformas pesadas. El sensor cuantiza sin(theta) a round(73+40sin), limitado1..145; descarta coseno y velocidad. No calcula la comparación. E1 recibe cantidades y cue5 por interfaces existentes. Una dirección nativa+X/−X genera torque+2/−2; ausencia o conflicto genera neutral0. Se fijaron67ticks DEE por0.05s simulado, sin pausa adaptativa de rescate.

Dos semillas ambientales, control de acción anulada y retardo de una muestra sostienen un efecto causal finito. La consolidación externa contiene73 pasos y57 torques no nulos ejecutados;16 salidas se anularon después de producirse.219peticiones=146aplicadas+73rechazadas_por_ocupación. El rechazo del nuevo lector no impidió todas las salidas: existía contexto material anterior; no se fuerza el puerto. Los controles no demuestran qué mecanismo aprendió a controlar el péndulo, porque no se enseñó tal política.

Todas las respuestas externas archivadas se reprodujeron con las acciones guardadas, sin DEE. Esto es reproducción del entorno, distinta del replay nativo y del recálculo aritmético. No hay fricción industrial, LiDAR, robot completo ni caos demostrado. La gravedad sí existe en el modelo y su parámetro pasó un contraste técnico separado.

## Atribución e incorporación

HECHO COMPUTACIONAL: registros exactos, comandos, recibos, métricas y restauración completa del puente. FÍSICA DEE: comparación, transporte, transformaciones e interferencias dentro del motor congelado. CAPACIDAD: uso finito de referencia adquirida, transmisión material y actuación externa. INTERPRETACIÓN: interfaz ambiental útil y vulnerabilidad a historia/encuentros. HIPÓTESIS abierta: selección adaptativa, crecimiento semántico y recuperación general. No se confunden esos niveles.

Se incorporó el puente explícito al gestor como instrumento, no como conocimiento aprendido ni nuevo gestor. ECO_EXT_01 quedó continuableT6167, índice externo25, con estado físico/RNG/wrappers y buffer de demora. Una continuación diagnóstica aparte comprobó funciones anteriores; no se fusionan sus consultas con el futuro protegido. No hubo promoción, el activo sigueT3154. NSM65 no cambia.

## Presupuesto y cobertura

Inicio09:19:28UTC, límite15:19:28UTC,21600s totales. La espera de permisos de red/Word consumió más de cinco horas, contadas sin reiniciar el reloj. Se priorizó la conexión real y controles mínimos al habilitarse Gym. No se completaron un hábitat endógeno cerrado puramentev27, referencias aleatorias extensas, toda la matriz de ruido/distribuciones, un nuevo método de enseñanza española ni regulaciónR2. El hábitat de reservorio es híbrido: su ley ambiental fija está en Python, y no se atribuye al ente. No se presentan esas omisiones como resultados negativos de capacidad.

Motor y original protegidos, datos profundos y snapshots locales. Este ZIP es análisis transportable, no sistema autosuficiente ni respaldo completo. Los localizadores y hashes de omisiones permiten continuar y ampliar el examen sin inventar evidencia.
'''

INCORPORATIONS='''# Incorporaciones y continuidad

Se añadieron al gestor existente `habitat-estado --vida ECO_EXT_01` y `habitat-externo --vida ECO_EXT_01 --pasos 1`. El primero es pasivo; el segundo es una operación externa explícita con proceso de entorno fijo y estado completo persistente. No selecciona un target ni cambia de vida. Su excepción al cerco de procesos sólo pertenece a ese instrumento opt-in; los comandos ordinarios mantienen el cerco. El módulo no importa laboratorio ni evidencia.

El contrato identifica Python, worker y fuente Pendulum por hash. Las dependencias externas se conservan localmente en sistema/runtime/habitat_externo_deps; NumPy pertenece al intérpretebundled. Cloudpickle no está disponible: el camino síncrono probado no lo ejercita, y no se anuncia soporte general de Gym.

Prueba real INCORPORACION_CLI_23: ECO_EXT_01 T6100→6167, índice24→25,67ticks, guardado y lectura en otro proceso. No T0 ni reset silencioso. Conservar el snapshot completo indicado en CONTINUIDAD y esas dependencias. Para resetear un episodio del entorno tras200 pasos use `--reiniciar-entorno` explícito; eso no reinicia DEE.

MAIN T7509 se conserva como futuro adverso, no como nuevo predeterminado. Las ramas listas AA y E1_SOCIAL_11 siguen protegidas y separadas. No se incorporan respuestas de controles a MAIN, ni se cambia NSM65. Los procedimientos de estrés, comunicación y autopsia permanecen ejecutables en laboratorio con sus fuentes exactas y controles, sin declararlos funciones autónomas del ente.
'''
if __name__=='__main__':main()
