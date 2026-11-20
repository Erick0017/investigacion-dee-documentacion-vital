"""Finalize compact continuity from Root's actual hashed closure facts.

No selectors, code, Word, state or products are written. Root supplies the
actual final principal and commands; missing facts stay missing or block a
claimed adoption. Source hashes are independently checked as frozen bytes.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,csv,hashlib,json
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--hechos-root',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);args=ap.parse_args()
    fb=args.hechos_root.read_bytes();facts=json.loads(fb);need(facts['schema']=='DEE.PI10.root_final_facts.R01'and facts.get('facts_finalized')is True,'Actual finalized Root closure facts, not a template or forecast')
    out=args.salida.absolute();need(not out.exists(),'New maps destination only')
    selected=facts['principal_final'];need(selected['N']==67 and type(selected['tick'])is int and selected['tick']>=922371 and selected['selected']is True,'Explicit actual selected principal, not maximum unrelated tick')
    need(facts['adoption_status']in('COMMITTED','NOT_ADOPTED'),'Explicit Root adoption decision')
    needed={'selection_proof','full_state_manifest','snapshot','manual','campaign_report','scientific_capability_matrix','scientific_coverage'}
    sources=[];seen=set()
    for entry in facts['sources']:
        role=entry['role'];file=Path(entry['file']).absolute();need(file.is_file(),'Missing final proof: '+str(file));data=file.read_bytes()
        need(sha(data)==entry['sha256'],'Changed/mismatched final source: '+str(file));seen.add(role)
        sources.append({'role':role,'absolute_path':str(file),'bytes':len(data),'sha256':sha(data),'evidence_kind':entry.get('evidence_kind','Root-supplied proof, exact bytes checked'),
          'read_scope':entry.get('read_scope','Byte identity checked; substantive interpretation remains in the named source')})
    need(needed<=seen,'Missing decisive final source roles: '+repr(sorted(needed-seen)))
    need(facts['manual']['internal_edition']and facts['manual']['identifier']=='DCS11-MM-001','Actual current Manual identity/edition')
    need(isinstance(facts.get('actual_commands'),list)and facts['actual_commands'],'Real usable/reproduction commands supplied by Root, not invented')
    checks=facts.get('closure_checks',{})
    if facts['adoption_status']=='COMMITTED':
        need(checks.get('local_gain_criterion_met')is True and checks.get('physical_resource_gain_met')is True,'No adopted improvement without actual reserved resource gain')
        need(checks.get('legacy12_correct')==12 and checks.get('legacy12_total')==12,'Observed gain2 requires12/12 conservation; no retrospective tolerance change')
        need(checks.get('use_after_reopen_observed')is True and checks.get('cold_Native_replay_verified')is True,'Actual useful reopening and cold acquisition reproduction are required')
        need({'adoption_proof','legacy_panel','reopen_use','cold_replay'}<=seen,'Missing evidence for claimed adoption')
    result={'schema':'DEE.PI10.final_continuity_transfer.R01','cut_utc':datetime.now(timezone.utc).isoformat(),'source_root_facts_sha256':sha(fb),
      'principal_before':facts['principal_before'],'principal_final':selected,'adoption_status':facts['adoption_status'],'manual':facts['manual'],
      'genealogy':facts['genealogy'],'closure_checks':checks,'actual_commands':facts['actual_commands'],'source_map':sources,
      'live_state_not_observed_by_this_builder':True,'Native_executed':False,'DEE_imported':False,
      'scientific_bounds':['Reserved Real-versus-NoFail gain is local; yoke wins the full12 and ties the reserved9, so no true-contingency superiority is demonstrated.',
        'The operation schedule, physical guards, codecs, fixed chain and environment law remain external preparation.',
        'Legacy coverage belongs to its actual panel tick; do not restamp it as another full panel at the final later tick.',
        'The small ZIP and standalone Native snapshots do not replace complete coherent local services, SQLite, environment, receipts and artifacts.'],
      'preserved_adverse':'R01 stopped atT928974 after4complete/5attempted; active diagonal(+X,+Z) was outside its fixed codec. This future remains preserved, not silently repaired or merged.',
      'pending_or_limits':facts.get('pending_or_limits',[])}
    out.mkdir()
    with(out/'CONTINUIDAD_PI10_FINAL.json').open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    with(out/'MAPA_RUTAS_DECISIVAS_PI10.csv').open('x',encoding='utf-8',newline='')as f:
        columns=['role','absolute_path','bytes','sha256','evidence_kind','read_scope'];w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(sources)
    proof={'schema':'DEE.PI10.final_maps_build.R01','Native_executed':False,'DEE_imported':False,'files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in out.iterdir()}}
    with(out/'VERIFICACION_MAPAS.json').open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(out),'principal':selected['life_id'],'T':selected['tick'],'adoption':facts['adoption_status'],'Native_executed':False}))
if __name__=='__main__':main()
