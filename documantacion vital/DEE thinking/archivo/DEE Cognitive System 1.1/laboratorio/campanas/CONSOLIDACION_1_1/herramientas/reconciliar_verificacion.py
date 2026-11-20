"""Recover overwritten audit-summary rows from intact native command outputs.

No motor is imported. No trajectory is repeated or given another outcome.
"""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[4]
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out;path=out/'VERIFICACION_EN_CURSO.json';report=read(path);dest=ROOT/'evidencia/diagnosticos/VERIFICADOR_SUPERPOSICION';dest.mkdir(parents=True,exist_ok=False);shutil.copy2(path,dest/'RESUMEN_ANTES_DE_RECONCILIAR.json');cmd=out/'comandos';before=read(cmd/'011_cli_restaurar.stdout');after=read(cmd/'013_cli_observar-componente.stdout');receipt=read(cmd/'009_cli_entrada.stdout');row=after['ENTE']['two_memory.center'];pending=before['physical']['tick']==3221 and row['tick']==3288 and row['active']and row['semantic']==1 and row['direction']==[1,0,0]and receipt['result']['status']=='scheduled'
    check={'passed':pending,'detail':{'initial_loaded_physical':before['physical'],'scheduled_receipt':receipt['result'],'later_native_response':row,'proof':'Recalculated from intact command stdout; not a new execution'}}
    report['checks']['pending_queue_across_processes_new_interaction']=check
    report['checks']['archive_not_changed_by_continuation']={'passed':sha(report['system_zip'])==report['system_sha256'],'detail':'Recomputed from the exact still-sealed archive'}
    files=[]
    for f in sorted(cmd.iterdir()):
        if not f.is_file():continue
        files.append({'name':f.name,'bytes':f.stat().st_size,'sha256':sha(f),'mtime_ns':f.stat().st_mtime_ns});shutil.copy2(f,dest/f.name)
    incident={'schema':'DCS1.1.external_verifier.race.reconciliation.v1','incident':'Profiles controller began at03:20:48UTC while prepare completed at03:20:51UTC. Their report writers overlapped. The profile summary retained six of eight prepare checks; two summary checks and some per-command timing rows were overwritten. All native stdout/stderr and complete checkpoints survived.','scientific_effect':'No sharedRuntime between phases; separate life copies. The overlapping summary is not accepted as its own proof. Functional assertions are recomputed from exact native command outputs. No outcome, decoder or trajectory was changed.','concurrency_limit':'Two-native-worker goal was supervised by owned jobs; global concurrency is not certified for this brief controller transition. Per-job4GiB limits and actual task outputs remain recorded. Do not infer native cognitive effects from host scheduling.','correction':'Exclusive per-output verifier lock and prerequisite prepare-completed check. No rerun of completed experiments.','missing_metadata':'Overwritten per-command host-duration rows are marked unavailable, not reconstructed as invented precise times. Native ticks, receipts, RAW/clocks and source logs remain exact.','recomputed_pending_check':check,'files':files,'original_summary_sha256':sha(dest/'RESUMEN_ANTES_DE_RECONCILIAR.json')}
    put(dest/'RECONCILIACION.json',incident);report['audit_summary_reconciliation']={'source':str(dest/'RECONCILIACION.json'),'sha256':sha(dest/'RECONCILIACION.json'),'native_trajectory_repeated':False,'lost_host_duration_rows_not_fabricated':True};report['raw_command_logs']=files;put(path,report)
    if not pending or not report['checks']['archive_not_changed_by_continuation']['passed']:raise AssertionError('Primary command evidence does not support repaired summary')
    print(json.dumps({'pending_queue_recalculated':pending,'archive_unchanged':True,'native_commands_repeated':0,'primary_logs_preserved':len(files)}))
if __name__=='__main__':main()
