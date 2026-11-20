"""One selected replay to resolve the social path and check passive recording."""
from pathlib import Path
import gzip,json,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EV=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA'
def op(case,args):subprocess.run([sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',case,*args],check=True,cwd=ROOT)
def main():
    seal=HERE/'PROTOCOLO_TRAZA_SOCIAL.json'
    if seal.exists():raise FileExistsError('Replay already frozen')
    prefix=json.loads(gzip.decompress((EV/'14_REGRESO_ANTERIOR.json.gz').read_bytes()))['result']
    signature=prefix['INSTRUMENTO']['snapshot_sha256']
    history=[json.loads(s)for s in(ROOT/'sistema/estado/vidas/MA_MAIN_R9/HISTORIA.jsonl').read_text(encoding='utf8').splitlines()]
    candidates=[p for p in(ROOT/'sistema/estado/checkpoints').glob('MA_MAIN_R9.T222559.*.deetsnap.gz')]
    import hashlib
    path=next(p for p in candidates if hashlib.sha256(p.read_bytes()).hexdigest()==signature)
    jobs=json.loads((HERE/'PROTOCOLO_RESERVA_FINAL.json').read_bytes())['public_inputs_fixed_before_results']
    seal.write_text(json.dumps(dict(frozen_monotonic=time.monotonic(),parent_snapshot_sha256=signature,
        checkpoint_relative=path.relative_to(ROOT/'sistema').as_posix(),
        inputs=jobs,purpose='Technical reproduction of the eight already evaluated jobs with passive per-tick records; not eight new independent learning samples.',
        criterion='Final RAW/clocks equality to recorded16_RESERVA_FINAL_MAIN, same material agenda and admitted inputs. Documentary life identities and host artifact path/times may differ. No targets used by the detailed observer.'),indent=2)+'\n',encoding='utf8')
    op('19_FORK_SOCIAL_TRACE',['bifurcar','MA_MAIN_R9','MA_SOCIAL_TRACE','--modalidad','DIAGNOSTIC_COPY','--checkpoint-relativo',path.relative_to(ROOT/'sistema').as_posix()])
    op('20_TRAZA_SOCIAL',['mente-sesion','--vida','MA_SOCIAL_TRACE','--situaciones',json.dumps(jobs,separators=(',',':')),'--detalle'])
if __name__=='__main__':main()
