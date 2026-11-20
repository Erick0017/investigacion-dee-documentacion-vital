"""Frozen CTX01 host-failure autopsy, no Native/owner or operational edits."""
from pathlib import Path
import collections,datetime,hashlib,json,runpy
P4=Path(__file__).resolve().parents[1];S2=P4/'estados/candidato_R02/sistema';R=P4.parents[2];C=R/'DEE Cognitive 2.0'
LIFE='ECI02_PI03_REPRO_PI04_C2C_CTX_CUT_01';KEY='DEE.Cognitive.PI04.C2C.coordination.R01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def info(p):return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def main():
    out=P4/'control/C2C_CTX1_FALLO_INFRAESTRUCTURA_R01.json'
    if out.exists():raise FileExistsError('Preserve first technical failure proof')
    primary=P4/'ensayos/PI04_C2C_CTX_CUT4_R01_OP_12.json';d=json.loads(primary.read_text(encoding='utf-8-sig'))
    if d['status']!='failed_preserved' or d['result']is not None:raise ValueError('Exact failed-preserved technical primary required')
    error=json.loads(d['error'])if isinstance(d['error'],str)else d['error'];cut=error['failed_native_future_preserved']
    if error['type']!='FileNotFoundError'or error['native_tick_after_attempt']!=810487 or cut['life_id']!=LIFE:raise ValueError('Unexpected failure/cut')
    parser_path=P4/'codigo/contrastar_finales_E3_pasivo.py';g=runpy.run_path(str(parser_path),run_name='pure_CTX_frozen_parser');parse=g['parse']
    failed=parse(S2/cut['snapshot'],cut['snapshot_sha256'])
    source_pair=C/'reproducibilidad/materiales/PI03_PI04_C2C_POST_DEV_T809763';manifest_path=source_pair/'EXPORTACION_SERVICIO.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    source=parse(source_pair/manifest['native_snapshot'],manifest['snapshot_sha256'])
    if source[0]['physical']['tick']!=809763 or failed[0]['physical']['tick']!=810487:raise ValueError('Expected actual724-tick partial opportunity')
    for key in('N','tick','RAW_sha256','clocks_sha256'):
        if failed[0]['physical'][key]!=cut['physical'][key]:raise ValueError('Failure witness does not match frozen snapshot')
    old={r['id']:r for r in source[5]};current={r['id']:r for r in failed[5]};old_diff=[k for k,v in old.items()if current.get(k)!=v];added=[r for k,r in current.items()if k not in old]
    if old_diff or len(added)!=184 or any(r['status']!=2 for r in added)or failed[4]:raise ValueError('Unexpected inherited receipt change, nonterminal Native input or pending agenda')
    groups=collections.Counter()
    for receipt in added:
        if not 809763<=receipt['requested_tick']<=810487:raise ValueError('New Native input outside actual partial opportunity')
        channels=receipt['channels']
        if len(channels)!=1:raise ValueError('Expected exact single-channel Native events')
        channel=channels[0]
        if channel.startswith('MU.raw.L128.'):groups['FI']+=1
        elif channel.startswith('PI03.TC.R01.'):groups['query_or_copy']+=1
        else:groups['other_MU_sensor']+=1
    home=S2/'estado/servicios_locales'/LIFE/'PI04_C2C_COORDINACION_R01';device=home/'dispositivo';state_file=device/'ESTADO_DISPOSITIVO.json';state=json.loads(state_file.read_text(encoding='utf-8-sig'))
    pending=state['pending'];src=device/'reservoir/0012.resource';target=device/'inflight_minus/0012.resource';prefix_file=source_pair/'artefactos_trabajador/PI04_C2C_COORDINACION_R01/dispositivo/reservoir/0012.resource'
    if pending['phase']!='before_move'or pending['ordinal']!=12 or pending['actual_value']!=7 or pending['actual_operation']!='diferencia'or pending['actual_route']!=-1:raise ValueError('Exact actual pending before-move witness differs')
    if not src.is_file()or target.exists()or target.parent.exists()or src.stat().st_size!=64 or sha(src)!=sha(prefix_file):raise ValueError('Cannot confirm missing-parent/nonmoved-resource technical cause')
    native=json.loads(failed[6][KEY]);journal=home/'eventos.jsonl';lines=journal.read_bytes().splitlines(keepends=True);events=[];chain='00'*32
    for i,line in enumerate(lines):
        value=json.loads(line)
        if value['index']!=i:raise ValueError('Journal index differs')
        chain=hashlib.sha256(bytes.fromhex(chain)+line).hexdigest();events.append(value)
    if native['log_count']!=len(events)or native['log_chain_sha256']!=chain:raise ValueError('Native failure capsule and external journal differ')
    new_events=[e for e in events if e['tick']>=809763]
    terminal=[e for e in new_events if e['kind']=='C2_FAILURE_PRESERVED']
    if not terminal:raise ValueError('Missing recorded preserved instrument failure')
    first=next(e for e in reversed(new_events)if e['kind']=='C2_FIRST_NATIVE_CHOICE')
    arithmetic=next(e for e in reversed(new_events)if e['kind']=='C2_ACTUAL_NATIVE_ARITHMETIC')
    # FI contains173 raw-port inputs AND3 query/support inputs. Classify by its
    # direct recorded receipt IDs, not by a port-name prefix shared with MU.
    prefix_groups=dict(groups)
    fi_ids={int(r['id'])for r in arithmetic['actual']['native_operation']['native_trial']['requests']}
    outer_ids={int(x)for x in native['pending']['request_ids']}
    added_ids={r['id']for r in added}
    if len(fi_ids)!=176 or len(outer_ids)!=4 or not fi_ids<=added_ids or not outer_ids<=added_ids or fi_ids&outer_ids:raise ValueError('Direct recorded FI/outer receipt partition differs')
    groups={'FI':len(fi_ids),'query_or_copy':len(outer_ids),'second_MU_sensor':len(added_ids-fi_ids-outer_ids)}
    if groups!={'FI':176,'query_or_copy':4,'second_MU_sensor':4}:raise ValueError('Actual direct receipt partition differs')
    new_return=[r for r in added if any('.outcome.'in ch for ch in r['channels'])]
    points={}
    for name,site in{'Q':(19,54,5),'A':(18,53,5),'B':(20,53,5),'eligibility_hub':(19,53,3),'SEM4_intercept':(19,55,4),'FI_prior_rejected1':(57,53,63),'FI_prior_rejected2':(6,47,12)}.items():
        i=(site[0]*67+site[1])*67+site[2];points[name]={'site':list(site),'clock':int(failed[2][i]),**g['decode'](failed[1][i])}
    historical_code=P4/'codigo/PI04_GUARDS_OPERATIVOS_CANDIDATOS/C2C_OP1/ANTES/pi04_coordinacion_central_C2C.py'
    proof={'schema':'PI04.C2C.CTX01.infrastructure_failure.passive.R01','inspection_local':datetime.datetime.now().astimezone().isoformat(),
      'primary':info(primary),'transport_status':d['status'],'transport_id':d['id'],'error':{k:v for k,v in error.items()if k!='failed_native_future_preserved'},
      'source_full_prefix':{'manifest':info(manifest_path),'snapshot':source[0]['snapshot'],'physical':source[0]['physical']},
      'preserved_failed_future':failed[0],'actual_partial_Native_ticks':724,'Native_pending_count':len(failed[4]),
      'Native_new_receipts':{'count':len(added),'status_counts':dict(collections.Counter(r['status']for r in added)),'groups':dict(groups),'grouping_by_exact_direct_receipt_IDs':True,'superseded_name_prefix_partition':prefix_groups,'prefix_partition_not_independent_trials':'The3FIquery/support inputs share non-raw names; the earlier prefix-only label173FI+7other was a label split, not a changed total or admission result. Exact partition is176FI+4MU+4query/copy.','all_terminal_applied':True,'old_receipt_differences':old_diff,'IDs_min':min(r['id']for r in added),'IDs_max':max(r['id']for r in added),'new_generic_outcome_events':len(new_return)},
      'Native_failure_progress':{k:native.get(k)for k in('ordinal','ready','admitted','arm','pending','uncertain','halted_reason','log_count','log_chain_sha256')},
      'journal':{'file':info(journal),'lines':len(events),'chain_sha256':chain,'Native_capsule_matches':True,'new_interval_event_kinds':[e['kind']for e in new_events],
        'first_native_choice':first,'actual_arithmetic_before_infrastructure_failure':arithmetic,'failure_event':terminal[-1]},
      'resource_move':{'source':info(src),'same_resource_in_full_prefix':info(prefix_file),'source_identity_equal':sha(src)==sha(prefix_file),'source_path_characters':len(str(src.resolve())),'destination_path_characters':len(str(target.absolute())),'destination':str(target.absolute()),'destination_exists':target.exists(),'destination_parent_exists':target.parent.exists(),'device_existing_directories':[q.name for q in device.iterdir()if q.is_dir()],'device_state':info(state_file),'pending_before_move':pending,'ordinal_still12':state['ordinal']==12,'external_feedback_pending':state.get('feedback_pending')},
      'current_frozen_state_points':points,'historical_failed_code':info(historical_code),'parser_code':info(parser_path),
      'interpretation':[
        'The host failed while moving an existing unchanged64-byte environmental resource to the absent inflight_minus directory. The WinError3 detail identifies that exact os.replace source/destination. The source remains at reservoir and no destination file exists; this bounds the failed effect to the host filesystem setup, not a false Native arithmetic or an observed empty resource.',
        'The first physical selection and actual arithmetic7 occurred before the failure. Device pending records the resulting actual route-1 at810487. It is an external state witness of the actuator intent, not a separately preserved second-reader packet or a successful material resource transfer.',
        'The source paired export stores files; the empty inflight directories are not members and are absent from the imported diagnostic home. The failed code assumes its selected inflight directory already exists. Recreating declared empty schema directories only before a new explicit material operation is an infrastructure correction, not learned repair or an edit of this failed future.',
        'All184 new Native inputs are terminal applied and the preserved Native agenda is empty. The C2C progress and external device intentionally remain pending/uncertain/halted after the host exception. They must not be cleared, retried, promoted or counted as four evaluated context-control opportunities.',
        'This first context-control attempt is unscored for the scientific4-case contrast: no device consequence or generic outcome was reached. It remains evidence of a724-tick partial Native execution and a host failure, not0/4 cognitive performance.',
        'A new named control may start from the same complete known809763 prefix after the declared directory fix; that does not resume or rewrite this adverse810487 future.'
      ],'new_Native_ticks_by_this_analysis':0,'originals_modified':False,'failed_future_cleared':False,'Native_or_GUI_executed':False}
    out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':info(out),'new_receipts':proof['Native_new_receipts'],'partial_ticks':724,'first_choice':first['reader']['choice'],'arithmetic':arithmetic['actual'].get('numeric_result'),'resource_source':info(src),'dest_parent_exists':False,'new_Native_by_analysis':0},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
