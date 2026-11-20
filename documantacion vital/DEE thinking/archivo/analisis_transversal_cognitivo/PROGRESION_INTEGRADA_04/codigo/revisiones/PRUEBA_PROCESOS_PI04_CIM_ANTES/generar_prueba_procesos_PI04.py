"""Query actual scoped Windows processes. No Native imports or process control.

Only processes whose command lines identify the two DEE systems, PI04 campaign
or affected life IDs are retained. Unknown scoped Python runners are blockers.
This never terminates a process, removes a lock or rewrites an owner cache.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess,sys
P4=Path(__file__).resolve().parents[1];C=P4.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';S2=P4/'estados/candidato_R02/sistema'
LIFE='ECI02_PI03_REPRO_PI04_MAIN_02';PARENT='ECI02_PI03_MAIN'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--salida',type=Path);args=ap.parse_args()
    stamp=datetime.datetime.now(datetime.timezone.utc);out=args.salida or P4/'control'/('PROCESOS_PI04_'+stamp.strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    if out.exists():raise FileExistsError('Do not overwrite a process observation')
    if not out.absolute().resolve().is_relative_to((P4/'control').resolve()):raise ValueError('Process proof destination must stay under PI04 control')
    terms=[str(S),str(S2),str(P4),LIFE,PARENT]
    # Data is embedded as escaped PowerShell literals, never interpolated into
    # a shell command or executed as project code. All output is scoped first.
    literals=','.join("'"+x.replace("'","''")+"'"for x in terms)
    ps="$ErrorActionPreference='Stop'; $terms=@("+literals+"); $rows=@(Get-CimInstance Win32_Process | Where-Object { $line=$_.CommandLine; $ok=$false; if($line) { foreach($term in $terms) { if($line.IndexOf($term,[System.StringComparison]::OrdinalIgnoreCase) -ge 0) { $ok=$true; break } } }; $ok -and $_.ProcessId -ne $PID } | ForEach-Object { [pscustomobject]@{ ProcessId=$_.ProcessId; ParentProcessId=$_.ParentProcessId; Name=$_.Name; ExecutablePath=$_.ExecutablePath; CommandLine=$_.CommandLine; CreationDateUtc= if($_.CreationDate){$_.CreationDate.ToUniversalTime().ToString('o')}else{$null} } }); ConvertTo-Json -InputObject $rows -Depth 4 -Compress"
    proc=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',ps],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=30)
    query_ok=proc.returncode==0;rows=[]
    if query_ok:
        rows=json.loads(proc.stdout.lstrip('\ufeff')or'[]')
        if isinstance(rows,dict):rows=[rows]
    allowed_helpers=('generar_prueba_procesos_PI04.py','construir_decision_final_PI04.py','verificar_adapter_PI04_revisado_estatico.py')
    evidence=[];blockers=[]
    for row in rows:
        command=row.get('CommandLine')or'';name=(row.get('Name')or'').lower()
        own=row['ProcessId']==os.getpid()or any(helper in command for helper in allowed_helpers)
        relevant_interpreter=name.startswith(('python','pythonw','py.'))or name in('powershell.exe','pwsh.exe')
        native_owner='gestionar.py'in command and any(k in command for k in('mente-unificada-iniciar','--vida','--system-root'))
        GUI='genesis.py'in command.lower()
        blocked=not own and(native_owner or GUI or relevant_interpreter)
        item={**row,'classification':'EXPLICIT_READONLY_HELPER'if own else'AFFECTED_OR_UNKNOWN_SCOPED_WRITER'if blocked else'OTHER_SCOPED_PROCESS_NOT_CLASSIFIED_AS_OWNER','blocks_material_migration':blocked}
        evidence.append(item)
        if blocked:blockers.append(item)
    proof={'schema':'DEE.PI04.actual_scoped_windows_process_observation.v1','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Actual Get-CimInstance Win32_Process command-line inspection scoped to exact DEE product/candidate/campaign paths and affected PI03/PI04 life IDs. No claim about unrelated processes or inaccessible command lines.',
       'affected_life_ids':[LIFE,PARENT],'query_success':query_ok,'query_returncode':proc.returncode,'query_error':None if query_ok else proc.stderr[-4000:],
       'observer_pid':os.getpid(),'evidence':evidence or[{'kind':'SUCCESSFUL_EMPTY_SCOPED_PROCESS_QUERY'if query_ok else'PROCESS_QUERY_FAILED','returncode':proc.returncode}],
       'blockers':blockers,'no_live_affected_writers':query_ok and not blockers,
       'criterion':'No scoped Native owner, GUI or unknown Python/PowerShell runner, excluding this explicitly named readonly helper and known readonly decision/static-review tools. Cached running:false is not used as process evidence.',
       'limitations':['Command-line scope does not prove absence of all conceivable writers. Incorporation also checks world locks, coherent queue state, source hashes and current selectors.','A proof with blockers or query failure must not be rewritten as a no-writer result. Generate a new observation after ordinary owners close.'],'Native_imports':0,'processes_stopped':0,'locks_or_caches_modified':False}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(out.resolve()),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'query_success':query_ok,'blockers':len(blockers),'no_live_affected_writers':proof['no_live_affected_writers']},ensure_ascii=False))
    if not query_ok:raise SystemExit(2)
if __name__=='__main__':main()
