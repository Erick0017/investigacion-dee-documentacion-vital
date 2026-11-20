"""Own-front evidence/source index only; no historical audit or native import."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/seleccion'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    target=EV/'INDICE_SELECCION_FINAL.json'
    if target.exists():raise FileExistsError(target)
    files=[]
    for folder in(HERE,EV):
        for p in sorted(folder.rglob('*')):
            if not p.is_file()or'__pycache__'in p.parts or p==target:continue
            snapshot=p.name.endswith('.deetsnap.gz')
            files.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'local_full_world_snapshot':snapshot,'include_in_analysis':not snapshot,'category':'complete_operational_snapshot'if snapshot else'actual_worker_bytes'if any(x.endswith('.worker')for x in p.parts)else'primary'if p.name.startswith(('MUFI_S','MUFI_G'))else'source'if p.suffix=='.py'else'report_or_protocol_or_recalculation','reason_omitted':'Full world persists locally; analysis carries exact primary records, full RAW/clock extracts for13states and locator/hash. Not a continuation backup.'if snapshot else None})
    r={'schema':'MUFI01.selection.index.v1','front':'MENTE_UNIFICADA_Y_FI01/seleccion','native_processes_still_running':0,'files':files,'local_total_bytes':sum(x['bytes']for x in files),'analysis_recommended_bytes':sum(x['bytes']for x in files if x['include_in_analysis']),'snapshot_count':sum(x['local_full_world_snapshot']for x in files),'final_auxiliary_life':{'snapshot':'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/seleccion/MUFI_S09_CONTINUACION_2.T2700.deetsnap.gz','sha256':'0c9924521ea63b0cdf168ad166b425b7975a6de5a2d4c66039061655c7fe3cc4','not_main':True},'scope':'Ownboundedfront only; no historicalengine/manualaudit. Include all positive/negative primaries and exact executed code. No external upload.'}
    target.write_bytes(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2).encode());print(json.dumps({'files':len(files),'snapshots':r['snapshot_count'],'analysis_bytes':r['analysis_recommended_bytes'],'sha256':sha(target)}))
if __name__=='__main__':main()
