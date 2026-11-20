"""Existing gestor imports complete learned states; never creates/trains a life."""
import gzip,hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];EV=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02/mecanismo_repetible'
def main():
    for suffix,life in[('TOUCH','MA02_SELECTOR_P1_H1'),('NO_TOUCH','MA02_SELECTOR_P1_H0')]:
        src=EV/('MA02_P1_OPERATION_'+suffix+'_ADMIT.deetsnap.gz');out=EV/('MA02_P1_IMPORT_'+suffix+'.json.gz')
        if out.exists():raise FileExistsError(out)
        argv=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'sistema/gestionar.py'),'importar-estado',str(src),life,'--perfil','fisica_directa','--sha256',hashlib.sha256(src.read_bytes()).hexdigest()]
        p=subprocess.run(argv,text=True,encoding='utf8',capture_output=True,timeout=30)
        record={'schema':'MA02.P1.system_import.1','identifier':'MA02_P1_IMPORT_'+suffix,'argv':argv,'source_snapshot_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'gestor_sha256':hashlib.sha256((ROOT/'sistema/gestionar.py').read_bytes()).hexdigest(),'adapter_sha256':hashlib.sha256((ROOT/'sistema/capacidades/selector_p1_ma02.py').read_bytes()).hexdigest(),'no_new_ticks_or_teaching':True}
        try:record['result']=json.loads(p.stdout)
        except json.JSONDecodeError:pass
        out.write_bytes(gzip.compress(json.dumps(record,ensure_ascii=False,sort_keys=True).encode(),mtime=0));print(json.dumps({'life':life,'code':p.returncode,'stdout':p.stdout[:200]},ensure_ascii=False),flush=True)
        if p.returncode:raise RuntimeError(p.stderr)
if __name__=='__main__':main()
