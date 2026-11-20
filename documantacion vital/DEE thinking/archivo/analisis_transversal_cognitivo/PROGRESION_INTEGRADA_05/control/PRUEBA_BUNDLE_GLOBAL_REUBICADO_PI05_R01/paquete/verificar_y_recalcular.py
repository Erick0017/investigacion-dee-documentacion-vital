"""Self-contained documentary verification/recalculation; never DEE or Native."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--recalcular',action='store_true');ap.add_argument('--grupo',choices=['principal','todos'],default='principal');ap.add_argument('--destino',type=Path);a=ap.parse_args()
    root=Path(__file__).resolve().parent;manifest=json.loads((root/'MANIFIESTO_SHA256.json').read_text(encoding='utf-8'))
    for row in manifest['files']:
        relative=Path(row['path'])
        if relative.is_absolute()or'..'in relative.parts:raise ValueError('Unsafe member path')
        p=root/relative
        if p.stat().st_size!=row['bytes']or sha(p)!=row['sha256']:raise ValueError('Member differs:'+row['path'])
    if not a.recalcular:
        if a.destino:raise ValueError('--destino requires explicit --recalcular')
        print(json.dumps({'mode':'VERIFY_BYTES_ONLY','verified_members':len(manifest['files']),'Native_ticks':0,'DEE_imports':0}));return
    if a.destino is None or a.destino.exists():raise ValueError('Explicit new --destino required')
    for p in(a.destino.absolute(),*a.destino.absolute().parents):
        if p.exists()and(p.is_symlink()or getattr(p.lstat(),'st_file_attributes',0)&1024):raise ValueError('Linked output')
    a.destino.mkdir(parents=True)
    expected=json.loads((root/'ESPERADOS_CONGELADOS.json').read_text(encoding='utf-8'));module=runpy.run_path(str(root/'codigo/recalcular_inventarios_globales_PI05_R02.py'),run_name='pure_portable_global')
    outputs=[]
    for case in expected['comparisons']:
        if a.grupo=='principal'and case['group']!='principal':continue
        out=module['compare'](root/'casos'/case['a'],root/'casos'/case['b'],a.destino/case['id']);actual=json.loads(out.read_text(encoding='utf-8'))
        if actual['frames']!=case['frames']:raise ValueError('Global original-hash/support mismatch:'+case['id'])
        ev=actual['actual_event_comparison']
        ec={'count_a':ev['count_a'],'count_b':ev['count_b'],'common':ev['common_channel_tick_events'],'identical_common':ev['identical_common_requests'],'changed_common':len(ev['request_differences']),'only_a':len(ev['events_only_a']),'only_b':len(ev['events_only_b']),'receipt_outcome_differences':len(ev['receipt_outcome_differences'])}
        if ec!=case['events']:raise ValueError('Native event accounting differs:'+case['id'])
        outputs.append({'case':case['id'],'frames_reconstructed_and_matched':actual['frame_count'],'output':out.relative_to(a.destino).as_posix(),'sha256':sha(out),'event_accounting':ec})
    if any(n=='app'or n.startswith('app.')or n=='dee_thinking'or n.startswith('dee_thinking.')for n in sys.modules):raise RuntimeError('Forbidden app/DEE import')
    report={'mode':'DOCUMENTARY_RECALCULATION_ONLY','Native_ticks':0,'DEE_imports':0,'member_hashes_verified':len(manifest['files']),'comparisons':outputs,'all_frozen_support_and_original_buffer_hashes_match':True,'not_Native_replay':True,'cold_Native_proof_in_bundle':'evidencias/FISICA_RP_GUARDIA_REPRODUCIDA_PI05_R01.json','scope':'Cold Native proof reports a previously executed198tick replay; this command does not execute it. RAW/clocks reconstruction is not a complete operational backup or a new capability of the actor.'}
    with(a.destino/'VERIFICACION_RECALCULO_PORTABLE.json').open('x',encoding='utf-8')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
