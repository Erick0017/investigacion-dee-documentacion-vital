"""Export closed actuator AUX primaries/source bytes, not operative snapshots.

No Native imports/ticks. Refuses export until outer supervision has closed.
"""
from pathlib import Path
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
EV=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
NATIVE=EV/'ACTUADOR_R02_AUX_R01'
OUT=NATIVE/'EVIDENCIA_PORTABLE_R01'
SUP=EV/'ACTUADOR_R02_SUPERVISION_R01'
REV=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/revisiones/ACTUADOR_R02_AUX_R01_EJECUTADO'
LIVES=('APD04_ACTUADOR_REAL_R02','APD04_ACTUADOR_OMIT_R02')


def read(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):
    with path.open('x',encoding='utf8')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')


def main():
    if OUT.exists():raise FileExistsError('Closed export exists; no overwrite or physical repetition')
    outer=read(SUP/'RESULTADO_SUPERVISION.json')
    if outer['final_total_job'].get('job_active_processes')!=0:raise ValueError('Outer owner tree is not closed')
    OUT.mkdir();members=[]
    def copy(source,relative):
        digest=sha(source);target=OUT/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        if sha(target)!=digest or sha(source)!=digest:raise ValueError('Original/exported bytes changed')
        members.append({'source':source.relative_to(ROOT).as_posix(),'exported':relative,
                        'sha256':digest,'bytes':target.stat().st_size})
    index={'schema':'APD04.actuator_R02.portable_primary.N0.r01','lives':{},'source_full_snapshots_omitted':[],
        'scope':'Not an operational backup. Both histories inherit the same complete T639374 parent; '
                'R02 codec is externalP0, not learned policy. Only committed results are used in recalc.'}
    for life in LIVES:
        vida=ROOT/'sistema/estado/vidas'/life/'VIDA.json'
        if not vida.is_file():continue
        record=read(vida);relative='vidas/'+life+'/VIDA_ORIGINAL.json';copy(vida,relative)
        info={'record':relative,'primaries':{}}
        protocol=ROOT/'sistema/estado/entrada_sencilla/vidas'/life/'PROTOCOLO.json'
        if protocol.is_file():copy(protocol,'vidas/'+life+'/PROTOCOLO_ORIGINAL.json')
        marker=vida.parent/'FUTURO_INTERRUMPIDO.json'
        if marker.is_file():copy(marker,'vidas/'+life+'/FUTURO_INTERRUMPIDO.json')
        db=ROOT/'sistema/estado/servicios_persistentes'/life/'cola.sqlite3'
        with sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True)as connection:
            connection.row_factory=sqlite3.Row
            transport=[dict(row)for row in connection.execute(
                'select id,payload,payload_sha,status,started_utc,finished_utc,error from requests where id like ? order by seq',
                ('apd04_actuator_%',))]
        info['transport_rows']=transport;info['original_database']={'path':db.relative_to(ROOT).as_posix(),'sha256':sha(db),'bytes':db.stat().st_size}
        for operation in record['operations']:
            relative=operation.get('result_file','')
            if 'apd04_actuator_'not in relative:continue
            source=ROOT/'sistema/estado/servicios_persistentes'/life/relative
            if sha(source)!=operation['result_sha256']:raise ValueError('Committed primary SHA changed')
            copy(source,relative);info['primaries'][relative]=relative
        index['lives'][life]=info
        snapshot=ROOT/record['snapshot']
        if not snapshot.is_file():snapshot=vida.parent/record['snapshot']
        index['source_full_snapshots_omitted'].append({'life':life,'snapshot_declared':record['snapshot'],
            'sha256':record['snapshot_sha256'],'tick':record['physical']['tick'],
            'scope':'Full local operative snapshot; not included in analysis export. '+str(snapshot)})
        local=NATIVE/life
        if local.is_dir():
            for source in sorted(local.iterdir()):
                if not source.is_file():continue
                if source.name.startswith('RESULTADO_'):
                    # Byte-identical scientific result is already present as its canonical primary.
                    info.setdefault('omitted_duplicate_UI_wrappers',[]).append({'path':source.relative_to(ROOT).as_posix(),
                        'sha256':sha(source),'bytes':source.stat().st_size,'reason':'Canonical complete primary included; UI wrapper not repeated'})
                else:copy(source,'INSTRUMENTO/'+life+'/'+source.name)
    for source in sorted(SUP.iterdir()):
        if source.is_file():copy(source,'SUPERVISION/'+source.name)
    for name in('CIERRE_DOS_AUX.json','CONFIGURACION_LOCAL_NO_INSTALADA.json','PREFIJO_VERIFICADO.json','RECURSOS_DRIVER.json'):
        if(NATIVE/name).is_file():copy(NATIVE/name,name)
    for relative in('MANIFIESTO_FUENTES.json','ejecutar_actuador_r02_aux_r01.py','PLAN_DOS_AUX_CONGELADO_N0.json',
                    'sistema/app/protocolo_apd04.py','sistema/app/usar_dee.py',
                    'sistema/capacidades/ecosistema_apd04.py','sistema/capacidades/sensor_balanceado_apd04.py',
                    'sistema/capacidades/sensor_componentes_apd04.py','sistema/capacidades/acciones_nativas_apd04.py',
                    'sistema/capacidades/ruta_adaptativa_apd02_04.py','sistema/capacidades/lexico_compartido_apd04.py',
                    'sistema/capacidades/asistente_apd03.py','sistema/capacidades/selector_acrecion_nativo.py'):
        copy(REV/relative,'FUENTES_EJECUTADAS/'+relative)
    for name in('resumir_actuador_r02_n0_r01.py','recalcular_panel_actuador_r02_n0.py',
                'contrastar_actuador_r02_portable_n0.py','examinar_panel_local_actuador_n0_r01.py',Path(__file__).name):copy(HERE/name,name)
    criterion=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/CRITERIO_CONTINUACION_Y_RESERVA_R01.json'
    copy(criterion,'CRITERIO_CONTINUACION_Y_RESERVA_R01.json')
    old=EV/'PANEL_HEREDADO_RAW_N0_R01'
    for name in('INDICE_LINEA_ORIGINAL.json','PANEL_EVENTO_ORIGINAL.jsonl.gz'):copy(old/name,'BASELINE_OLD_PANEL/'+name)
    index['old_panel_baseline']={'directory':'BASELINE_OLD_PANEL','scope':'Exact ancestor panel previously executed before common T639374; comparison only, not new teaching.'}
    write(OUT/'INDICE.json',index)
    for name,script in(('RECALCULO_PORTABLE.json','resumir_actuador_r02_n0_r01.py'),
                        ('RECALCULO_PANEL_PORTABLE.json','recalcular_panel_actuador_r02_n0.py')):
        completed=subprocess.run([sys.executable,'-I','-B',str(OUT/script),'--index',str(OUT/'INDICE.json'),'--out',str(OUT/name)],
            capture_output=True,text=True,encoding='utf8')
        if completed.returncode:raise RuntimeError(completed.stderr)
    if read(OUT/'RECALCULO_PORTABLE.json')['discrepancies']:raise ValueError('RAW/action discrepancy in exported results')
    comparison=subprocess.run([sys.executable,'-I','-B',str(OUT/'contrastar_actuador_r02_portable_n0.py'),
        '--evidence',str(OUT),'--out',str(OUT/'CONTRASTE_RETROALIMENTACION_N0.json')],capture_output=True,text=True,encoding='utf8')
    if comparison.returncode:raise RuntimeError(comparison.stderr)
    write(OUT/'MANIFIESTO_ORIGINALES.json',{'members':members,'new_native_ticks':0,
          'self_and_generated_indices_recalc_not_in_original_member_list':True})
    print(json.dumps({'folder':str(OUT),'members':len(members),'bytes':sum(path.stat().st_size for path in OUT.rglob('*')if path.is_file()),
        'portable_RAW_discrepancies':0,'new_native_ticks':0},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
