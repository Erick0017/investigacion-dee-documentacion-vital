"""Selección dirigida de APD; conserva originales y no ejecuta el motor."""
from pathlib import Path
import hashlib,json,zipfile,shutil,re
W=Path(__file__).resolve().parent;ROOT=W.parents[1];ARCH=ROOT/'archivo/DEE Cognitive System 1.1';SYS=ROOT/'DEE Cognitive 2.0/sistema'
STAGE=W/'sector_apd/stage';STAGE.mkdir(parents=True,exist_ok=True)
SOURCES=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def add(f,relative):
    f=Path(f);data=f.read_bytes();target=STAGE/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    SOURCES.append(dict(original=str(f),relative=relative,sha256=sha(data),bytes=len(data)));return relative
def member(z,p,relative):
    data=z.read(p);target=STAGE/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    SOURCES.append(dict(original=str(z.filename),member=p,relative=relative,sha256=sha(data),bytes=len(data)));return relative
def snapshot(name):
    roots=[ARCH/'sistema/estado/checkpoints',SYS/'estado/checkpoints']
    candidates=[p/name for p in roots if (p/name).is_file()]
    if not candidates:raise FileNotFoundError(name)
    return add(candidates[0],'padres/'+name)
def prepare():
    # Los ZIP cerrados son fuentes de extracción; ninguno se anida en la entrega.
    archives=[('APD01','DEE_ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_ANALISIS.zip'),('APD02','DEE_APD02_CONTINUIDAD_CALIDAD_ADAPTACION_ANALISIS.zip'),('APD03','DEE_APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION_ANALISIS.zip'),('APD04','DEE_APD04_ECOSISTEMA_COGNITIVO_ANALISIS.zip'),('APD05','DEE_APD05_GENESIS_SIN_LLM_ANALISIS.zip')]
    counts=[]
    for camp,name in archives:
        path=ARCH/'entregas'/name
        with zipfile.ZipFile(path) as z:
            picked=[]
            if 'INDICE_OBJETOS_Y_ALIASES.json' in z.namelist():
                ix=json.loads(z.read('INDICE_OBJETOS_Y_ALIASES.json'))
                for namespace in ix['namespaces']:
                    if namespace['id'] in ('PRUEBA_PAQUETE_EXACTO','DELTA_OPERATIVO'):continue
                    for row in namespace['members']:
                        low=row['path'].lower()
                        if any(x in low for x in ('manual','prompt_recibido','documentos/','presupuesto','manifiesto','inventario')):continue
                        if not low.endswith(('.py','.json','.json.gz','.jsonl','.jsonl.gz','.csv','.bin','.sqlite3','.deetsnap.gz')):continue
                        storage=ix['objects'][row['sha256']]['storage'];data=z.read(storage)
                        if sha(data)!=row['sha256']:raise ValueError('Object hash mismatch')
                        member(z,storage,'archivo/'+camp+'/'+namespace['id']+'/'+row['path'])
            for i in z.infolist():
                parts=Path(i.filename).parts
                if i.is_dir() or any(x.lower() in ('__pycache__','node_modules') for x in parts):continue
                low=i.filename.lower()
                if not low.endswith(('.py','.json','.json.gz','.jsonl','.jsonl.gz','.csv','.csv.gz','.bin','.deetsnap.gz')):continue
                if any(x in low for x in ('manifest','hashes','inventario','presupuesto','recursos','fuentes_y_omisiones')):continue
                if any(x in low for x in ('documentos/','manual/','grabacion_parcial/','full_genesis/phase_','gui_walk/fuentes_ejecutadas/')):continue
                # Copias funcionales y primarios, sin Word, motor, vídeos ni informes repetidos.
                relative='archivo/'+camp+'/'+i.filename
                picked.append(member(z,i.filename,relative))
            counts.append(dict(campaign=camp,archive=str(path),archive_sha256=sha(path.read_bytes()),members=len(picked)))
    camp=ARCH/'laboratorio/campanas'
    specs=[
      ('lexico',camp/'ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/lenguaje',['ensayar_lexico_r01.py','ensayar_lexico_r04.py','lexico_extensible_r04.py']),
      ('ruta04',camp/'APD02_CONTINUIDAD_CALIDAD_ADAPTACION/mecanismo',['ejecutar_r04_abab.py','traza_retorno_demorado_r04.py','PROTOCOLO_R04_ABAB.json','ejecutar_corte_r04.py','PROTOCOLO_CORTE_R04.json']),
      ('sensor03',camp/'APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/mecanismo',['cribar_sensor_balanceado_apd03_r02.py','sensor_balanceado_apd03_r02.py','CRIBADO_SENSOR_BALANCEADO_R02.json']),
      ('calidad',camp/'APD02_CONTINUIDAD_CALIDAD_ADAPTACION/calidad',['probar_calidad_apd02.py','evaluador_calidad_apd02.py','proveedores_prueba_apd02.py']),
    ]
    for label,d,names in specs:
        for name in names:add(d/name,'protocolos/'+label+'/'+name)
    for name in ['APD02_MAIN.T391957.8b146c72922f.deetsnap.gz','APD02_MAIN.T548407.1175587c1ab9.deetsnap.gz']:
        snapshot(name)
    # R04 léxico exige el padre exacto anterior, nunca el puntero moderno.
    expected='af0150596f4e114f2a8a35e3cd4d3648ce10feb3e775c00b09fb2526b83bb429'
    matches=[]
    for folder in [ARCH/'sistema/estado/checkpoints',SYS/'estado/checkpoints']:
        matches.extend(p for p in folder.glob('APD01_LEX_R03_paired.T108212.*') if sha(p.read_bytes())==expected)
    if matches:add(matches[0],'padres/'+matches[0].name)
    else:counts.append(dict(missing='Padre léxico R04',expected_snapshot_sha256=expected))
    (W/'sector_apd/seleccion.json').write_text(json.dumps(dict(sources=SOURCES,archives=counts),ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(dict(source_files=len(SOURCES),bytes=sum(x['bytes'] for x in SOURCES),archives=counts),ensure_ascii=False))
if __name__=='__main__':prepare()
