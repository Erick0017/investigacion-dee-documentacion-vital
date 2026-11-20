"""Comprobante externo de los ZIP finales; no importa DEE ni cambia vidas."""
from __future__ import annotations
import argparse, hashlib, json, zipfile
from datetime import datetime, timezone
from pathlib import Path

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def meta(p):
    p=Path(p); return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def check_file(row):
    p=Path(row['path']); assert p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],p
    return meta(p)
def check_archive(p,manifest_name):
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        rows=json.loads(z.read(manifest_name))['members']
        assert len(z.namelist())==len(set(z.namelist()))
        assert set(z.namelist())=={r['path'] for r in rows}|{manifest_name}
        for row in rows:
            b=z.read(row['path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],row['path']
        return len(rows)+1
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--closure',type=Path,required=True);ap.add_argument('--full-proof',type=Path,required=True);ap.add_argument('--analysis-zip',type=Path,required=True);ap.add_argument('--analysis-tree',type=Path,required=True);ap.add_argument('--recalculations',type=Path,required=True);ap.add_argument('--manual-proof',type=Path,required=True);ap.add_argument('--collaboration-root',type=Path,required=True);ap.add_argument('--deployment-proof',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    c=read(a.closure);f=read(a.full_proof);r=read(a.recalculations);m=read(a.manual_proof)
    assert c['status']=='CLOSED_SCIENTIFIC_CUT'
    assert f['status']=='COMPLETED_WITH_RECORDED_SCOPE' and f['originals_unchanged'] and f['zip_unchanged']
    full=Path(f['zip']);assert sha(full)==f['zip_sha256']
    assert r['all_exact'] and r['all_recalculations_accepted'] and not r['errors'] and r['native_ticks']==0
    assert a.analysis_zip.stat().st_size<=16000000
    with zipfile.ZipFile(a.analysis_zip) as z:
        solid='MANIFIESTO_CONTENEDOR.json' in z.namelist()
        expected_inner_sha=(json.loads(z.read('INDICE_COMPRESION_SOLIDARIA.json'))['original_manifest']['sha256'] if solid else hashlib.sha256(z.read('MANIFIESTO_HASHES.json')).hexdigest())
    analysis_members=check_archive(a.analysis_zip,'MANIFIESTO_CONTENEDOR.json' if solid else 'MANIFIESTO_HASHES.json')
    assert sha(a.analysis_tree/'MANIFIESTO_HASHES.json')==expected_inner_sha
    inner=read(a.analysis_tree/'MANIFIESTO_HASHES.json');names={x['path'] for x in inner['members']}|{'MANIFIESTO_HASHES.json'}
    assert names=={p.relative_to(a.analysis_tree).as_posix() for p in a.analysis_tree.rglob('*') if p.is_file()}
    for row in inner['members']:
        p=a.analysis_tree/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],p
    deployment=None
    if solid:
        assert a.deployment_proof is not None and a.deployment_proof.is_file()
        deployment=read(a.deployment_proof)
        assert deployment['status']=='EXACT_ORIGINAL_TREE_RESTORED' and deployment['all_original_names_and_bytes_preserved']
        assert deployment['original_manifest_sha256']==expected_inner_sha and deployment['original_files']==len(names)
    originals={}
    for name,entry in c['protected_original_checks'].items():originals[name]={k:check_file(entry[k]) for k in ('record','snapshot')}
    active=check_file(c['source_verification']['ACTIVO'])
    selected={k:check_file(c['source_verification'][k]) for k in ('candidate_VIDA','candidate_snapshot')}
    selected['queue_journal']=check_file(c['local_dependencies']['queue_journal'])
    word=Path(m['document']);assert sha(word)==m['sha256']
    collaborator=a.collaboration_root/word.name;assert sha(collaborator)==m['sha256']
    with zipfile.ZipFile(a.analysis_zip) as z:
        matches=[n for n in z.namelist() if Path(n).name==word.name];assert len(matches)==1
        assert hashlib.sha256(z.read(matches[0])).hexdigest()==m['sha256']
    with zipfile.ZipFile(full) as z:
        matches=[n for n in z.namelist() if Path(n).name==word.name];assert len(matches)==1
        assert hashlib.sha256(z.read(matches[0])).hexdigest()==m['sha256']
    result={'schema':'DEE.MUFI01.final.external.verification.v1','status':'DELIVERED_WITH_EXPLICIT_EXPERIMENTAL_SCOPE','created_utc':datetime.now(timezone.utc).isoformat(),'native_ticks_for_this_receipt':0,
      'full_operational_zip':{**meta(full),'proof':meta(a.full_proof),'proof_status':f['status'],'functional_issues_preserved':f.get('service_sequence',{}).get('functional_issues',[])},
      'analysis_zip':{**meta(a.analysis_zip),'outer_members':analysis_members,'lossless_solid_container':solid,'restored_logical_members':len(names),'crc_and_all_member_hashes_verified':True,'immutable_tree_unchanged_after_recalculation':True,'deployment_proof':meta(a.deployment_proof) if a.deployment_proof else None},
      'archived_recalculations':{'cases':len(r['recalculations']),'all_outputs_byte_exact':True,'report':meta(a.recalculations),'native_ticks':0},
      'manual':{**meta(word),'same_bytes_in_collaboration_root_and_full_zip':True,'visual_validation':m['visual_validation'],'render_failure':m.get('render',{}).get('stderr'),'editorial_record':meta(a.manual_proof)},
      'protected_originals_rechecked':originals,'ACTIVO_rechecked':active,'selected_operational_state_rechecked':selected,'selected_life':c['main'],'continuity':meta(a.closure),
      'scope_limits':['Another extraction path on this computer, not evidence from a second physical computer','Archived calculations do not advance DEE or reproduce the native trajectories','The analysis ZIP omits complete operational worlds; the full collaboration ZIP contains selected continuation bundles','Prepared P0 timing is not learned R2; no new NSM65 or general-mind certification','A stopped open epoch requires its paired transport state; no silent snapshot-only replacement']}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'out':str(a.out),'full_bytes':full.stat().st_size,'analysis_bytes':a.analysis_zip.stat().st_size,'recalculations':len(r['recalculations']),'native_ticks':0}))
if __name__=='__main__':main()
