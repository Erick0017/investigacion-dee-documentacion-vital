"""Bounded actual render attempts for the two staged complete PI06 documents.

An error is evidence of unavailable QA, never visual approval.
"""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys, time
P = Path(__file__).resolve().parents[1]
RENDER = Path(r'C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1104.22356\skills\documents\render_docx.py')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    d = P/'documentos'
    output = d/'INTENTO_RENDER_PI06_R01.json'
    if output.exists():
        raise FileExistsError('Read the actual existing attempt; do not repeat blindly')
    stage = json.loads((d/'ACTUALIZACION_DOCUMENTAL_PI06_1_33.json').read_text(encoding='utf8'))
    attempts = []
    for label in ('Manual','Compendium'):
        source = Path(stage[label]['output'])
        assert sha(source) == stage[label]['sha256']
        dest = d/('render_'+label+'_1_33_R01')
        cmd = [sys.executable,'-I','-B','-X','utf8',str(RENDER),str(source),'--output_dir',str(dest),'--emit_pdf']
        start = time.monotonic()
        try:
            r = subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',timeout=35,
                               creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            stdout, stderr, code, timeout = r.stdout, r.stderr, r.returncode, False
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or b''; stderr = exc.stderr or b''
            stdout = stdout.decode('utf8',errors='replace') if isinstance(stdout,bytes) else stdout
            stderr = stderr.decode('utf8',errors='replace') if isinstance(stderr,bytes) else stderr
            code, timeout = None, True
        for suffix, text in (('stdout',stdout),('stderr',stderr)):
            with (d/(label+'_render_'+suffix+'_R01.txt')).open('x',encoding='utf8') as f:
                f.write(text)
        attempts.append({'document':label,'source':str(source),'sha256':sha(source),
            'command':cmd,'exit_code':code,'timeout_35s':timeout,'elapsed_seconds':time.monotonic()-start,
            'output_directory':str(dest),'PDFs':[str(p) for p in dest.glob('*.pdf')],
            'PNGs':[str(p) for p in dest.glob('*.png')],
            'stdout':str(d/(label+'_render_stdout_R01.txt')),
            'stderr':str(d/(label+'_render_stderr_R01.txt'))})
    record = {'schema':'DEE.PI06.actual_bounded_render_attempts.R01',
        'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status':'NOT_VALIDATED','manual_sha256':stage['Manual']['sha256'],
        'attempts':attempts,'reviewed_images':[],'rendered_pdf':None,
        'limitations':'Actual skill renderer attempted for both complete DOCX files. No visual approval is inferred. If rendering failed, exact stdout/stderr and return codes are preserved; structure is checked separately.',
        'no_DOCX_or_principal_modified':True,'new_Native_ticks':0}
    with output.open('x',encoding='utf8') as f:
        json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(output),'sha256':sha(output),'attempts':attempts,'visual_QA':'NOT_VALIDATED'},ensure_ascii=False))

if __name__ == '__main__':
    main()
