"""Deriva fichas de cierre desde registros existentes; cero ticks, sin motor.

No altera snapshots, vidas, ACTIVO ni resultados originales. Este índice del
investigador nunca se importa como memoria o respuesta al participante.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,time

LAB=Path(__file__).resolve().parents[1]
ROOT=LAB.parents[2]
EV=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def emit(p,o):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    budget=read(LAB/'PRESUPUESTO.json')
    checks=[]
    for name,x in budget['protected'].items():
        checks.append({'life':name,'record_sha256':sha(x['record']),
            'record_unchanged':sha(x['record'])==x['record_sha256'],
            'snapshot_sha256':sha(x['snapshot']),
            'snapshot_unchanged':sha(x['snapshot'])==x['sha256']})
    if not all(x['record_unchanged'] and x['snapshot_unchanged'] for x in checks):
        raise ValueError('A protected original differs; do not seal silently')
    active=read(ROOT/'sistema/estado/ACTIVO.json')
    if active['life_id']!='MA_MAIN_R9' or active['tick']!=230379:
        raise ValueError('Unexpected active change; no global promotion authorized by this closure')
    names=['MA02_MAIN_5','MA02_MAIN','MA02_MEMORIA_SEPARADA',
           'MA02_SELECTOR_P1_H1','MA02_SELECTOR_P1_H0','MA02_PENDIENTE_CONTROL',
           'MA02_COMPOSICION_PLUS_LISTA','MA02_COMPOSICION_PLUS_USO']
    lives=[]
    for name in names:
        p=ROOT/'sistema/estado/vidas'/name/'VIDA.json';r=read(p)
        snap=ROOT/'sistema'/r['snapshot']
        if sha(snap)!=r['snapshot_sha256']:raise ValueError('Snapshot differs: '+name)
        lives.append({k:r.get(k) for k in('life_id','profile','branch','parent','snapshot','snapshot_sha256','physical')}
                     |{'record_sha256':sha(p),'complete_snapshot_bytes':snap.stat().st_size})
    final=next(x for x in lives if x['life_id']=='MA02_MAIN_5')
    if final['physical']['tick']!=11196:raise ValueError('Unexpected final life tick')
    cap={
      'schema':'MA02.capabilities.by.life.v1','no_NSM65_level_increase':True,
      'rows':[
       {'life':'MA02_MAIN_5','tick':11196,'current_access':{'alfa':-1,'beta':1,'gamma':1,'delta':-1,'epsilon':-1},
        'current_panel':{'requested':5,'valid':5,'correct_against_own_teaching':5},
        'retention_reserve':{'material_queries':64,'valid':64,'correct':64,'input_applied':448,'input_requested':448},
        'ordinary_queries_in_selected_genealogy':{'requested':154,'valid_and_teaching_concordant':152,'no_answer':2},
        'genealogy_native_requests':{'requested':1133,'applied':1131,'rejected':2,'pending':0},
        'actual_MAIN_workers':{'accepted':10,'commit':4,'copies_excluded':True},
        'acquisition':'Own three→four signs; selective revision; composition consumed two accesses; explicit readquisition; declared P0 extension then own fifth sign.',
        'assistance':'Operator context/tool/initiation; fixed phase/codec/resources/decoder. Worker algorithms/eligibility external.',
        'limitations':['Five opaque correspondences, not five policies or meanings','Current alfa−/beta+ are mixed: no valid joint output; consuming composition occurred in its past, not current matching contents','No P2/R2 or learned improvement of action utility','No social participant learning newly integrated','Current final panel is finite evidence, not all future states']},
       {'life':'MA02_MAIN','tick':3625,'current_access':{'alfa':-1,'beta':1,'gamma':1,'delta':-1},
        'current_panel':{'requested':4,'valid':4,'correct':4},'integration':'Same new T0 genealogy before fifth preparation; own useful destructive composition and explicit readquisition already in past'},
       {'life':'MA02_MEMORIA_SEPARADA','tick':2486,'current_access':{'alfa':-1,'beta':-1,'gamma':1,'delta':-1},
        'integration':'Exact preserved fork before consuming composition, not source used to repair MAIN'},
       {'life':'MA02_COMPOSICION_PLUS_LISTA','tick':2616,'current_contents':{'alfa':1,'beta':1,'gamma':1,'delta':-1},
        'current_capability':'Prepared native consuming composition +/+→+ demonstrated on a fork by existing manager; gamma/delta used afterwards. Ready state not consumed.',
        'integration':'Actually reached R10 history from original complete MAIN T2486, explicitly imported; not knowledge copied into MAIN_5'},
       {'life':'MA02_SELECTOR_P1_H1','tick':129,'prepared_future_query_tick':197,'certified_first_end_tick':212,
        'new_capacity':'Same generic request selects Y by prior physical contact, acquired content− used; first use only',
        'integration':'Independent complementary life; fork before use; not MAIN_5 knowledge'},
       {'life':'MA02_SELECTOR_P1_H0','tick':129,'prepared_future_query_tick':197,'certified_first_end_tick':212,
        'new_capacity':'Without historical contact same generic request selects X, acquired content+ used; first use only',
        'integration':'Independent complementary life; not no-teaching control: both contents were taught'},
       {'life':'MA_MAIN_R9','tick':230379,'integration':'Previous active/protected, unchanged; earlier functional domain retained, no MA02 knowledge transferred'},
       {'life':'MA_U0_ACUMULATIVO_AUX','tick':740,'integration':'Previous complementary learned state unchanged; no MA02 history attributed'},
       {'life':'MA02_PENDIENTE_CONTROL','integration':'Exact pending-state diagnostic fork, restored actual external12Bfile then verified in a new directory; its success is not a second MAIN commit'}]}
    continuity={
      'schema':'DEE.Cognitive.System.1.1.MA02.continuity.v1','campaign':'MENTE_ACUMULATIVA_R02',
      'state':'NATIVE_CLOSED_READY_FOR_EXACT_ARCHIVE_VERIFICATION',
      'registered_utc':datetime.now(timezone.utc).isoformat(),
      'scientific_cut':final,'lives':lives,'active_unchanged':active,
      'no_global_promotion':True,'no_trained_fields_transferred_between_different_lives':True,
      'classification':'New declared T0 N67 anatomy and its complete-state descendants, not a continuation of historical E1/R9/U0.',
      'main_history':'R03B own three→four acquisitions, R04 selective revision, manager importT1414, material use/tools, consuming toroidal composition, explicit readquisition, exact forkT3625, P0 fifth-context extension and own fifth experience, repeated use and pending-worker continuation.',
      'current_capabilities_file':'laboratorio/campanas/MENTE_ACUMULATIVA_R02/CAPACIDADES_ANTES_DESPUES.json',
      'next_operation':'Bifurcar MA02_MAIN_5 con nombre nuevo, mente2-estado y mente2-sesion con entradas nuevas sin targets. Para P1 bifurcar H1/H0 antes del único uso certificado.',
      'required_operational_files':['sistema/gestionar.py','sistema/app','sistema/capacidades/mente_acumulativa_r02.py','sistema/capacidades/selector_p1_ma02.py','sistema/capacidades/eo02_trabajador_local.py','sistema/contratos','sistema/estado/vidas and complete referenced snapshots','official compatible CPython3.13 x64 and declared thinking4.5runtime'],
      'analysis_ZIP_not_operational_backup':True,
      'auxiliary_final_recalculation':{'file':'evidencia/campanas/MENTE_ACUMULATIVA_R02/mecanismo_repetible/RECALCULO_MECANISMO_MA02_R06_FINAL.json','primary_cases':58,'exact_RAW_checks':173231,'discrepancies':0,'no_P2_R2':True},
      'limits':['No learned general access/action policy P2/R2','Composition consumes individual access; re-teaching is explicit','Passive low occupancy is not unlimited capacity','P1ready snapshots include future query/resource queues','Host initiates opportunities and chooses task context'],
      'budget':{'start_utc':budget['start_utc'],'limit_utc':budget['limit_utc'],
          'deadline_monotonic':budget['deadline_monotonic'],'current_monotonic':time.monotonic(),
          'not_restarted':True},
      'verification_outside_archives':'Final external verification receipts identify exact sealed ZIP hashes; no archive stores its own hash.'}
    emit(LAB/'CAPACIDADES_ANTES_DESPUES.json',cap)
    emit(ROOT/'CONTINUIDAD_MENTE_ACUMULATIVA_R02.json',continuity)
    proof={'new_ticks':0,'protected':checks,'active_unchanged':active,
           'selected_full_snapshots':lives,'all_protected_bytes_unchanged':True}
    emit(EV/'cierre/PROTECCION_Y_CORTE_FINAL.json',proof)
    print(json.dumps({'new_ticks':0,'final_life':final['life_id'],'tick':final['physical']['tick'],
                      'snapshot_sha256':final['snapshot_sha256'],'protected_originals':len(checks)},ensure_ascii=False))
if __name__=='__main__':main()
