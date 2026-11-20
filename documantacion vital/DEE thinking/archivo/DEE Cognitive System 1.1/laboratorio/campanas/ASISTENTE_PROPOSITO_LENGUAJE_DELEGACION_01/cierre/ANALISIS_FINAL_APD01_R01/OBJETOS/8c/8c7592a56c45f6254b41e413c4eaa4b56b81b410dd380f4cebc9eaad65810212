"""Record actual editorial result only; do not author DOCX or restore a Runtime."""
import hashlib
import json
import shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
LAB=HERE.parents[1]
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proof=LAB/'documentos/EDICION_MANUAL_APD01.json';x=read(proof)
    word=Path(x['document'])
    expected='2cc8c39640a5926963459ec648f6c3bc446be9b10e5edb6402fd2d74bf429a70'
    assert sha(word)==x['sha256']==expected and word.stat().st_size==136927
    assert x['geometry_preserved']and x['fields_preserved']and x['history_chapters20_31_preserved']
    assert x['render']['pages']==[]and x['render']['returncode']==1
    metadata={'edition':'1.15','relative_ROOT':str(word.relative_to(ROOT)).replace('\\','/'),
        'sha256':expected,'bytes':136927,'authored_by_Root_existing_helper':True,
        'structural_preservation':{'geometry':True,'fields':True,'historical_chapters20_31':True},
        'prior_edition_archived':True,'visual_validation':'NOT_AVAILABLE_RENDER_FAILED',
        'render_returncode':1,'render_pages':0,'render_exact_error':'LibreOffice soffice.exe was not found on PATH',
        'no_desktop_office_fallback_claimed':True,
        'proof_relative_ROOT':str(proof.relative_to(ROOT)).replace('\\','/'),'proof_sha256':sha(proof),
        'new_native_ticks_for_this_record':0,'another_Word_edition_created_by_this_record':False}
    archive=HERE/'_VERSIONES_INSTRUMENTALES/PRE_WORD_RECORD';archive.mkdir(parents=True,exist_ok=False)
    for name in ['COBERTURA.json','DATOS_INCORPORACION_APD01.json']:
        target=HERE/name;shutil.copy2(target,archive/name);data=read(target)
        data['manual_current']=metadata
        target.write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    receipt={'status':'ACTUAL_WORD_EDITION_RECORDED_VISUAL_PENDING_FULL_PENDING','native_ticks':0,
        'DOCX_authored_by_this_tool':False,'manual':metadata,
        'outputs':[{'file':n,'sha256':sha(HERE/n)}for n in ['INFORME_CIENTIFICO.md','COBERTURA.json','DATOS_INCORPORACION_APD01.json']]}
    with(HERE/'ACTUALIZACION_WORD_REAL_N0.json').open('xb')as f:
        f.write((json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()
