"""Bounded PI08 final accounting. Default plan; --medir reads actual files.

No DEE import, Native query, SQLite access, repair, cleanup or process control.
Only --medir --salida writes one fresh small report under this campaign.
Logical per-path bytes are not allocated disk bytes or reclaimed free space.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,fnmatch,hashlib,json,os,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[2];W=P.parents[4];C=R/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
OLD='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
ENGINE_PINS={
 'python':(C/'motor/python313/python.exe','29d6486dc5fa86c9d19db9d390fdbb62c4830e2b305761723c0b42e6f3596954'),
 'WHL':(C/'sistema/runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl','09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'),
 'PYD':(C/'motor/python313/site-packages/dee_thinking/_native.cp313-win_amd64.pyd','17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'),
 'kernel_source':(R/'4.5/DEE_thinking_4_5_0/source/src/kernel_v27.cpp','fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31')}
def need(b,t):
    if not b:raise ValueError(t)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def ptr(j,p):
    need(p==''or isinstance(p,str)and p.startswith('/'),'Explicit JSON pointer')
    if p=='':return j
    for k in p[1:].split('/'):
        k=k.replace('~1','/').replace('~0','~');j=j[int(k)]if isinstance(j,list)else j[k]
    return j
def plain(p,exists=True):
    q=Path(p);q=q if q.is_absolute()else P/q;q=q.resolve(strict=exists)
    need(q.is_relative_to(W.resolve()),'Only exact workspace sources')
    for n in(q,*q.parents):
        if n.exists():need(not n.is_symlink()and not(getattr(n.lstat(),'st_file_attributes',0)&1024),'Reparse/link refused')
        if n==W.resolve():break
    return q
def stamp(p):
    s=p.stat();return {'bytes':s.st_size,'mtime_ns':s.st_mtime_ns}
def matches_new_life(life):return isinstance(life,str)and 'PI08_'in life and life.startswith('ECI02_PI03_REPRO_')
def direct_children(root):return sorted(q for q in root.iterdir())if root.is_dir()else[]
def count_tree(root,max_files):
    """One lstat per encountered entry; no repeated ancestor scan per file."""
    initial=root.stat();total=0;files=0;dirs=0;unsafe=[];stack=[root]
    if root.is_file():return {'path':str(root),'files':1,'directories':0,'logical_bytes':initial.st_size,'root_mtime_ns_before':initial.st_mtime_ns,'root_mtime_ns_after':root.stat().st_mtime_ns,'reparse_skipped':[]}
    while stack:
        parent=stack.pop();dirs+=1
        with os.scandir(parent)as entries:
            for e in entries:
                st=e.stat(follow_symlinks=False)
                if e.is_symlink()or getattr(st,'st_file_attributes',0)&1024:unsafe.append(str(Path(parent)/e.name));continue
                if e.is_dir(follow_symlinks=False):stack.append(Path(parent)/e.name)
                elif e.is_file(follow_symlinks=False):files+=1;total+=st.st_size;need(files<=max_files,'Bounded campaign count exceeded; do not census wider scope')
    return {'path':str(root),'files':files,'directories':dirs,'logical_bytes':total,'root_mtime_ns_before':initial.st_mtime_ns,'root_mtime_ns_after':root.stat().st_mtime_ns,'reparse_skipped':unsafe}

def main(a):
    config=read(Path(a.config).resolve())if a.config else{}
    if not a.medir:
        print(json.dumps({'mode':'PLAN_ONLY_NO_SCAN_NO_NATIVE','campaign_root':str(P),'limits':read(P/'REGISTRO_CAMPANA.json')['budget'],
          'storage':'P8 entire + shallow PI08-named new RP roots + exact newly created product lives/sidecars/checkpoints + explicit changed files/extractions. Deduplicate overlapping paths; count logical per-path bytes including hardlinks.',
          'Native':'Unique PI08 life cards(P8+product), parent tick subtraction; two F1 forks counted separately from explicit actual proof. Unknown uncheckpointed advance remains a gap, never0byassumption.',
          'pins':{k:{'path':str(v[0]),'expected_sha256':v[1]}for k,v in ENGINE_PINS.items()},
          'requires_root_to_measure':'All scoped Root owners closed, fresh actual closure evidence, exact config for additional roots and code provenance; no automatic repair/test on hash mismatch.'},ensure_ascii=False,indent=2));return
    need(a.salida is not None,'Fresh explicit report path required');out=Path(a.salida).resolve();need(out.is_relative_to(P)and not out.exists(),'One fresh PI08 output only')
    need(not(P/'PI08_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'A declared material writer remains; inspect, do not erase')
    budget=read(P/'REGISTRO_CAMPANA.json')['budget'];issues=[];closure=[]
    for e in config.get('closure_gates',[]):
        q=plain(e['source']);need(sha(q)==e['sha256'],'Actual closure source changed')
        okay=ptr(read(q),e['pointer'])==e['expected'];closure.append({**e,'matches':okay})
        if not okay:issues.append('Actual closure gate false '+str(q))
    if not closure:issues.append('No actual scoped closure gate supplied; report is partial accounting')
    # Deliberately shallow known state hierarchy, never all of documentation vital.
    cardpaths=[]
    for systemhome in direct_children(P/'estados'):
        for folder in direct_children(systemhome/'sistema/estado/vidas'):
            q=folder/'VIDA.json'
            if q.is_file():cardpaths.append(q)
    product_lives=[]
    for folder in direct_children(C/'sistema/estado/vidas'):
        if matches_new_life(folder.name)and(folder/'VIDA.json').is_file():cardpaths.append(folder/'VIDA.json');product_lives.append(folder.name)
    life_rows={};duplicates=[];cardstamps={};cardhashes={}
    for q in cardpaths:
        q=plain(q);cardstamps[str(q)]=stamp(q);j=read(q);life=j['life_id']
        if not matches_new_life(life):continue
        initial=j.get('parent',{}).get('source_tick');current=j['physical']['tick']
        need(type(initial)is int and type(current)is int and current>=initial,'Known complete imported parent/cut required')
        value={'life_id':life,'N':j['physical']['N'],'parent_tick':initial,'current_tick':current,'Native_ticks':current-initial,'snapshot_sha256':j['snapshot_sha256'],'physical':j['physical'],'cards':[str(q)],'availability':j.get('availability')}
        cardhashes[str(q)]=sha(q)
        if life in life_rows:
            old=life_rows[life]
            need(all(old[k]==value[k]for k in('N','parent_tick','current_tick','snapshot_sha256','physical')),'Divergent stores of one identity; never choose largesttick')
            old['cards'].append(str(q));duplicates.append({'life_id':life,'identical_current_store_alias':str(q)})
        else:life_rows[life]=value
    extra_native=0;extra_rows=[]
    for e in config.get('uncheckpointed_advancement_proofs',[]):
        q=plain(e['source']);need(sha(q)==e['sha256'],'Extra recorded-advance proof changed');j=read(q);life=ptr(j,e['life_pointer']);last=ptr(j,e['last_observed_tick_pointer'])
        need(life in life_rows and type(last)is int and last>=life_rows[life]['current_tick'],'Uncheckpointed exact recorded cut required')
        n=last-life_rows[life]['current_tick'];extra_native+=n;extra_rows.append({'life_id':life,'known_saved_tick':life_rows[life]['current_tick'],'last_observed_tick':last,'extra_recorded_Native_ticks':n,'proof':str(q),'unknown_later_advancement':e.get('unknown_later_advancement',False)})
        if e.get('unknown_later_advancement'):issues.append('Unknown later Native advancement '+life)
    forks=0;fork_rows=[]
    for e in config.get('actual_fork_proofs',[]):
        q=plain(e['source']);need(sha(q)==e['sha256'],'Actual fork proof changed');j=read(q);n=ptr(j,e['pointer'])
        need(type(n)is int and 0<=n<=2,'Actual bounded F1fork count, not planned slots')
        forks+=n;fork_rows.append({'source':str(q),'sha256':e['sha256'],'pointer':e['pointer'],'actual_Runtime_forks':n,'not_independent_organisms':True})
    if (P/'control/PI08_F1_CUT_R03.json').is_file()and not fork_rows:issues.append('Actual F1proof exists but Runtimefork count not explicitly bound')
    reserved=config.get('fork_budget_reserved_slots',0)
    need(type(reserved)is int and 0<=reserved<=2,'Only bounded two-fork F1 reserve')
    budget_forks=max(forks,reserved)
    ticks=sum(r['Native_ticks']for r in life_rows.values())+extra_native;worlds=len(life_rows)+budget_forks
    need(all(stamp(Path(q))==v for q,v in cardstamps.items()),'A life card changed during passive accounting')
    roots=[P];root_origins=[{'path':str(P),'origin':'Entire unique PI08campaign, includes documents/QA/newZIP/staging/inside extractions'}]
    for name in ('materiales','codigo_preservado','recetas','verificaciones'):
        for q in direct_children(RP/name):
            if q.name.casefold().startswith('pi08'):
                roots.append(plain(q));root_origins.append({'path':str(q),'origin':'New PI08-prefixed RP '+name})
    for home in(C/'sistema/capacidades',C/'sistema/contratos'):
        for q in direct_children(home):
            if q.is_file()and q.name.casefold().startswith(('pi08','protocolo_pi08','sello_pi08')):
                roots.append(plain(q));root_origins.append({'path':str(q),'origin':'New PI08-prefixed current Cognitive source/contract, no whole product census'})
    for q in(RP/'RECURSOS.json',C/'PROYECTO.json',C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',
      C/'sistema/capacidades/CATALOGO_CAPACIDADES.json',C/'sistema/estado/ACTIVO.json',
      C/'sistema/estado/genesis/SELECCION_PERSONAL.json',C/'aplicacion/GENESIS/SELECCION_CANDIDATA.json',
      C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx',
      R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'):
        if q.is_file():roots.append(plain(q));root_origins.append({'path':str(q),'origin':'Bounded modified current descriptor/document, full logical size conservatively counted'})
    for life in product_lives:
        for name in ('vidas','servicios_locales','servicios_persistentes'):
            q=C/'sistema/estado'/name/life
            if q.exists():roots.append(plain(q));root_origins.append({'path':str(q),'origin':'PI08 new product full life/paired copy '+life})
        for q in direct_children(C/'sistema/estado/checkpoints'):
            if q.is_file()and q.name.startswith(life+'.T'):roots.append(plain(q));root_origins.append({'path':str(q),'origin':'PI08 new product checkpoint '+life})
    for s in config.get('exact_additional_storage_roots',[]):
        q=plain(s['path']);need(q!=W and q!=R and q!=C and q!=RP,'No broad unrelated-tree census')
        roots.append(q);root_origins.append({'path':str(q),'origin':s['origin_evidence']})
    # Modified original operational files are counted at current full logical
    # size, conservatively, separately from their preserved campaign copies.
    for e in config.get('modified_file_manifests',[]):
        q=plain(e['source']);rows=ptr(read(q),e['rows_pointer']);need(len(rows)<=100,'Bounded code-delta list only');home=plain(e['source_root'])
        for row in rows:
            rel=row[e.get('file_key','file')];need(not Path(rel).is_absolute()and'..'not in Path(rel).parts,'Relative known delta')
            item=plain(home/rel);roots.append(item);root_origins.append({'path':str(item),'origin':'Bounded modified operating-file witness '+str(q)})
    reduced=[];overlap=[]
    for q in sorted(set(roots),key=lambda x:(len(x.parts),str(x).casefold())):
        parent=next((x for x in reduced if q.is_relative_to(x)),None)
        if parent is not None:overlap.append({'path':str(q),'already_counted_under':str(parent)})
        else:reduced.append(q)
    storage=[count_tree(q,config.get('maximum_files_per_root',200000))for q in reduced]
    logical=sum(v['logical_bytes']for v in storage);unsafe=[p for v in storage for p in v['reparse_skipped']]
    if unsafe:issues.append('Reparse entries excluded from storage scope; incomplete accounting')
    if any(v['root_mtime_ns_before']!=v['root_mtime_ns_after']for v in storage):issues.append('A measured root timestamp changed during scan; concurrent change must be reviewed')
    pins=[]
    for name,(q,expected)in ENGINE_PINS.items():
        actual=sha(plain(q));pins.append({'name':name,'path':str(q),'expected_sha256':expected,'actual_sha256':actual,'matches':actual==expected,'read_or_import':'HASH_ONLY_NO_EXECUTION'})
        if actual!=expected:issues.append('Frozen engine/source pin mismatch '+name+'; no automatic repair or Native test')
    reg=read(P/'REGISTRO_CAMPANA.json');protected=[]
    for key in ('card','snapshot'):
        e=reg['source_main'][key];q=plain(e['path']);actual=sha(q);protected.append({'name':'original_PI05_'+key,'path':str(q),'expected_sha256':e['sha256'],'actual_sha256':actual,'unchanged':actual==e['sha256']})
        if actual!=e['sha256']:issues.append('Original protected PI05 '+key+' differs')
    expected_code=[]
    for e in config.get('expected_selected_code',[]):
        q=plain(e['path']);actual=sha(q);expected_code.append({**e,'actual_sha256':actual,'matches':actual==e['sha256']})
        if actual!=e['sha256']:issues.append('Selected code differs from expected; SKIP_TEST_NO_MODIFICATION '+str(q))
    limits={'Native_ticks':budget['Native_ticks_all_branches'],'worlds':budget['diagnostic_worlds_all_new'],'all_new_logical_bytes':budget['additional_logical_bytes_including_delivery'],'closure_reserve_bytes':budget['closure_storage_reserved_bytes'],'job_memory_bytes':budget['owned_Native_job_memory_bytes']}
    checks={'ticks_within_fixed_budget':ticks<=limits['Native_ticks'],'worlds_including_actual_forks_within_fixed_budget':worlds<=limits['worlds'],'logical_bytes_within_fixed_final_budget':logical<=limits['all_new_logical_bytes'],'frozen_engine_and_source_hashes_equal':all(v['matches']for v in pins),'original_PI05_card_snapshot_unchanged':all(v['unchanged']for v in protected)}
    result={'schema':'DEE.PI08.final_bounded_ledger_storage.v1','at':datetime.now(timezone.utc).isoformat(),'status':'MATCHED_ACTUAL_SCOPED_ACCOUNTING'if not issues and all(checks.values())else'GAPS_OR_LIMITS_PRESERVED',
      'new_Native_ticks_executed_by_accounting':0,'DEE_imports':0,'closure_gates':closure,'checks':checks,'issues':issues,
      'Native_ledger':{'unique_current_lives':len(life_rows),'actual_Runtime_forks_extra':forks,
        'fork_slots_conservatively_reserved_for_budget':reserved,'budget_accounted_extra_fork_slots':budget_forks,
        'worlds_actually_verified_lower_bound':len(life_rows)+forks,'worlds_total_for_budget':worlds,
        'known_Native_ticks':ticks,'life_rows':list(life_rows.values()),'identical_card_aliases_not_new_worlds':duplicates,
        'fork_proofs':fork_rows,'extra_saved_gap_proofs':extra_rows,'scope':'Imported physical parent subtraction, each life once; forks add worldslots, no concepts or new experiences merely fromcopy. A budget reserve is explicitly not proof a Runtime was created.'},
      'storage':{'measured_logical_bytes':logical,'remaining_to_fixed_final_limit':limits['all_new_logical_bytes']-logical,'includes_current_ZIP_and_QA_and_staging_inside_measured_roots':True,'additional_extractions_require_explicit_roots':True,'root_origins':root_origins,'nonoverlapping_measured_roots':storage,'overlaps_not_counted_twice':overlap,'counts_hardlinked_paths_logically':True,'allocated_disk_bytes_or_reclaimed_space_measured':False,'free_workspace_volume_bytes_now':shutil.disk_usage(W).free,'measurement_precedes_own_output':True,'own_report_conservative_extra_allowance':1000000,'future_outputs_not_yet_created_are_not_measured':True,'historical_peak_not_reconstructed_from_current_count':True,'historical_peak_evidence_as_supplied':config.get('historical_storage_peak_evidence',[])},
      'limits_fixed_not_extended':limits,'engine_and_kernel_source_pins':pins,'original_protected_PI05':protected,'expected_selected_code':expected_code,'Native_functional_tests_performed':False,'automatic_repair_archive_cleanup_or_selection_changes':False}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'report':str(out),'sha256':sha(out),'status':result['status'],'Native_ticks':ticks,'worlds':worlds,'logical_bytes':logical,'checks':checks,'issues':issues},ensure_ascii=False,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--config');ap.add_argument('--medir',action='store_true');ap.add_argument('--salida',type=Path);main(ap.parse_args())
