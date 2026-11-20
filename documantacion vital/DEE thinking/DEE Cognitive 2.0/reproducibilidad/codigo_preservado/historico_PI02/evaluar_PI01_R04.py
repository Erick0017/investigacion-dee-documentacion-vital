"""Reserved PI01 evaluation. Fixed fixtures, no selection of successful forks."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from servicio_ensayo import Owner,P,PY,SYSTEM,append

def freeze():
    path=P/'control/PROTOCOLO_RESERVA_R04.json'
    if path.exists():raise RuntimeError('Already frozen; do not overwrite')
    files=['capacidades/progresion_integrada_01.py','capacidades/pi01_traza_legal_base.py','app/mundo_genesis_apd05.py','app/cola_local.py']
    import importlib.util
    spec=importlib.util.spec_from_file_location('fixture_only',P/'codigo/tarea_acceso_recursos_R04.py')
    # Fixture values copied literally; importing the Native module is unnecessary.
    pairs=[(8,3),(13,5),(17,4),(16,9),(3,12),(15,2),(10,2),(19,11),(7,1),(20,13),(12,4),(18,7),(4,11),(9,2),(14,5),(16,4),(11,6),(20,8)]
    document={'frozen_at':datetime.datetime.now().astimezone().isoformat(),'version':'R04','development_record':'ensayos/RESUMEN_DESARROLLO_R04.json','parent':'ECI02_OPERATIVA_PRINCIPAL_01','N':67,'T':727225,'life_main':'ECI02_PI01_MAIN','controls':['ECI02_PI01_CONTROL_OMIT','ECI02_PI01_CONTROL_NULLED'],'independence':'All three share a prefix; not independent acquisition replicates.18 sequential opportunities per continuous life.','episodes':[{'index':i,'left':l,'right':r,'private_lock':-1 if i<6 or i>=12 else 1,'context_load':[11,17,23,29,101,103][i%6],'gap_periods':[0,1,0,2,1,0][i%6]}for i,(l,r)in enumerate(pairs)],'decoder':'Route at exact q, active SEM1 and direction(0,0,1)=0 or(-1,1,1)=1.0 calls only MAalfa;1 calls only FI earlyq4. Legacy physical decoder unchanged. None has no fallback.','return':'q+268:normalizer3; actual failure echoes chosen action plus valence5. OMIT excludes valence;NULLED retains consequences but action cannot release resources.','criteria_before_reserve':{'minimum_main_actual_resources':15,'denominator':18,'strict_route_and_response_required':'All18 opportunities reported incl silence/rejection. No automatic failure of product on one absent output, but promotion requires no uncertain transport or material legacy regression.','benefit_control':'Main must exceed actual resources of omission control by at least3/18; nulled must release0resources.','retention_panel':['alfa negative','luma positive','nara negative','clasifica negative','suma positive','FI compare positive/negative/material zero','6+7=13 then13-5=8','alfa and luma after chain'],'continuation':'Full paired save, close owner, reload in another process and one additional opportunity without reseeding or resetting Native memory.','promotion':'Only complete final lineage; earlier T727225 retained, no unrelated future merged. If criteria fail, original remains active.'},'budget':{'reserved_opportunities':54,'max_episodes_per_arm':18,'stop':'uncertain/failed_preserved or2consecutive absent route/response signatures; preserve reached future, no fallback.'},'assistance':'P0 opportunity timing, environment, physical opportunity codec and host route-to-access call. DEE carries and changes policy, forms content responses; host evaluates utility after action. No self-initiated opportunity/plan claimed.','code_sha256':{f:hashlib.sha256((SYSTEM/f).read_bytes()).hexdigest()for f in files}}
    path.write_text(json.dumps(document,ensure_ascii=False,indent=2),encoding='utf-8');append({'kind':'RESERVE_FROZEN','file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});print('FROZEN',path)

def run(arm):
    path=P/'control/PROTOCOLO_RESERVA_R04.json';protocol=json.loads(path.read_text(encoding='utf-8'))
    for file,expected in protocol['code_sha256'].items():
        if hashlib.sha256((SYSTEM/file).read_bytes()).hexdigest()!=expected:raise RuntimeError('Code changed since freeze:'+file)
    life={'real':'ECI02_PI01_MAIN','omit':'ECI02_PI01_CONTROL_OMIT','nulled':'ECI02_PI01_CONTROL_NULLED'}[arm];tag='PI01_RES_'+arm.upper()
    pair=SYSTEM.parents[3]/'not_used' # replaced by the known protected canonical root below
    product=P.parent.parent.parent/'DEE Cognitive 2.0'
    pair=product/'sistema/estado/pares_iniciales/ECI02_OPERATIVA_PRINCIPAL_01'
    cmd=[str(PY),'-I','-B','-X','utf8',str(SYSTEM/'gestionar.py'),'--system-root',str(SYSTEM),'mente-unificada-importar','--paquete',str(pair),'--vida',life]
    log=P/'ensayos'/(tag+'_IMPORT.json')
    if log.exists():raise RuntimeError('Do not repeat import or evaluation')
    result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
    log.write_text(json.dumps({'command':cmd,'code':result.returncode,'stdout':result.stdout,'stderr':result.stderr},ensure_ascii=False,indent=2),encoding='utf-8')
    if result.returncode:raise RuntimeError('Import failed; inspect record')
    rows=[]
    with Owner(life,tag)as o:
        o.material(tag+'_PREPARE',{'modo':'eci01-pi01-preparar'})
        o.material(tag+'_ENV',{'modo':'eci01-pi01-ambiente','serie':'evaluacion','brazo':arm})
        for ep in range(18):
            r=o.material(tag+'_EP%02d'%ep,{'modo':'eci01-pi01-paso'},allow_failure=True)
            if r.get('operation')!='sesion':break
            v=r['result']['rows'][0]
            row={'episode':ep,'before':r['before_tick'],'after':r['after_tick'],'route':v['native_decision']['route'],'access':v['selected_access']['access'],'response':v['selected_access']['physical_response'],'accepted':v['external_effect']['accepted'],'resources':v['external_effect']['resources_after'],'private_lock':v['external_effect']['private_lock_used_only_after_action'],'record':tag+'_EP%02d.json'%ep}
            rows.append(row);print(json.dumps(row),flush=True)
            (P/'ensayos'/('RESUMEN_'+tag+'.json')).write_text(json.dumps({'arm':arm,'life':life,'scope':'Reserved fixed R04 evaluation','rows':rows},ensure_ascii=False,indent=2),encoding='utf-8')
            if len(rows)>=2 and all(x['route']is None or x['response']is None for x in rows[-2:]):append({'kind':'RESERVE_STOP','arm':arm,'reason':'two consecutive missing signatures','episode':ep});break
    print('CLOSED',life,len(rows),sum(x['accepted']for x in rows),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');parser.add_argument('--arm',choices=['real','omit','nulled']);args=parser.parse_args()
    if args.freeze:freeze()
    elif args.arm:run(args.arm)
    else:parser.error('Explicit freeze or arm required')
