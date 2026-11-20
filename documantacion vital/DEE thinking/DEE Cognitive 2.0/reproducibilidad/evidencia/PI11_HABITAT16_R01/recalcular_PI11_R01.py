"""PI11 documentary recalculation from explicit CLOSED witness exports.

Standard library only. No DEE, Runtime, owner, SQLite, network or process API.
This script neither establishes owner closure nor reproduces Native evolution:
the coordinator must supply a closure declaration with its evidence locator.
Only files below --primarios are read; output must be a new/empty directory.
"""
from pathlib import Path
import argparse,csv,hashlib,json

VERSION='DEE.PI11.documentary_recalculation.R01'
RESERVE_OFFSET=18000
FIELDS=('life_id','ordinal','before_tick','after_tick','Native_ticks','elapsed_before','elapsed_after','reserved',
        'mode','cue','q1_choice','q1_NULL','q2_choice','q2_NULL','query_released','query_granted','query_denied',
        'refresh_FI','actual_FI_choice','reuse_attempt','certificate_valid','certificate_physical_reuse','certificate_useful_reuse',
        'physical_delivered','attributed_useful','actual_failed','returned_failed','q1_delta_before','q1_delta_after',
        'q1_changed','requested_unique_episode','applied_unique_episode','rejected_unique_episode','pending_unique_episode',
        'permissions_after','remaining_stock','witness','witness_sha256')

def need(ok,why):
    if not ok:raise ValueError(why)

def sha(data):return hashlib.sha256(data).hexdigest()

def plain(p,existing=True):
    p=Path(p).absolute()
    for a in(p,*p.parents):
        if a.exists():need(not a.is_symlink()and not(getattr(a.lstat(),'st_file_attributes',0)&1024),'No linked/reparse documentary path')
        else:need(not a.is_symlink(),'No dangling link')
    return p.resolve(strict=existing)

def load(p):return json.loads(p.read_text('utf-8-sig'))

def integer(v,label):need(type(v)is int,label+' must be an exact integer');return v

def bit(v,label):need(type(v)is bool,label+' must be explicit bool');return v

def choice(v,label):need(v is None or type(v)is int and v in(-1,0,1),label+' is -1/0/+1 or NULL');return v

def terminal(status):return status=='applied'or status.startswith('rejected')

def receipts(rows):
    """Deduplicate identities, preserving conflicts and final statuses.

    A pending receipt may legitimately become terminal in a later witness.
    Contradictory terminal receipts are rejected, never arbitrarily selected.
    """
    out={};aliases=0
    for row in rows:
        n=integer(row['id'],'Native input ID');value=row['receipt'];need(value.get('id')==n,'Input/receipt identity mismatch')
        status=value.get('status');need(isinstance(status,str),'Receipt status string required')
        if n not in out:out[n]=value;continue
        aliases+=1;prior=out[n]
        if prior==value:continue
        old=prior['status'];new=status
        need(not(terminal(old)and terminal(new)),'Contradictory final receipts for Native ID '+str(n))
        if terminal(new):out[n]=value
        elif not terminal(old):need(prior==value,'Different unresolved receipts require reconciliation')
    counts={'unique_requested':len(out),'applied':0,'rejected':0,'pending_or_other':0,'receipt_aliases':aliases}
    for value in out.values():
        key='applied'if value['status']=='applied'else'rejected'if value['status'].startswith('rejected')else'pending_or_other'
        counts[key]+=1
    return counts,out

def episode(value,path,root,start):
    need(value.get('version','').startswith('DEE.PI11.'),'A PI11 reached Native witness is required')
    life=value.get('life_id');need(isinstance(life,str)and life,'Exact reached life ID required')
    ordinal=integer(value['ordinal'],'ordinal');before=integer(value['before_tick'],'before_tick');after=integer(value['after_tick'],'after_tick')
    ticks=integer(value['new_native_ticks'],'new_native_ticks');need(after>=before and ticks==after-before,'Native interval accounting differs')
    first=value['first_stage'];second=value['second_stage'];resource=value['resource'];environment=value['environment_after']
    local_start=integer(environment['start_tick'],'environment start_tick');need(local_start==start,'Environmental origin differs between witnesses')
    q1=choice(first['reader']['choice'],'Q1');q2=choice(second['reader']['choice'],'Q2')
    reg=first['register'];access=reg['access'];granted=bit(access['allowed'],'access.allowed');requested=access['native_gate']==1
    refresh=bit(second['refresh_FI'],'refresh_FI');fi=second.get('FI');actual_fi=None if fi is None else choice(fi['old_q6_choice'],'actual FI')
    need(refresh==(fi is not None),'Recorded renewal and actual FI presence differ')
    before_delta=integer(value['Q1_references_before']['A_minus_B'],'Q1 before difference')
    after_delta=integer(value['references_after']['q1']['A_minus_B'],'Q1 after difference')
    physical=bit(resource['physical_delivered'],'physical_delivered');attributed=bit(resource['attributed_useful'],'attributed_useful')
    failed=bit(value['actual_failed'],'actual_failed');returned=bit(value['returned_failed'],'returned_failed')
    need(not attributed or physical,'Attributed useful delivery requires real physical delivery')
    need(failed is(not attributed)and resource['actual_failed']is failed,'Task consequence mismatch')
    rc,unique=receipts(value['requests']);offer=value['offer'];spec=offer['environment']
    certvalid=bit(resource['certificate_valid'],'certificate_valid')
    row={'life_id':life,'ordinal':ordinal,'before_tick':before,'after_tick':after,'Native_ticks':ticks,
         'elapsed_before':before-start,'elapsed_after':after-start,'reserved':before-start>=RESERVE_OFFSET,
         'mode':spec['mode'],'cue':value['environment_spec_at_input']['cue'],'q1_choice':q1,'q1_NULL':q1 is None,'q2_choice':q2,'q2_NULL':q2 is None,
         'query_released':bit(reg['released'],'register.released'),'query_granted':granted,'query_denied':requested and not granted,
         'refresh_FI':refresh,'actual_FI_choice':actual_fi,'reuse_attempt':not refresh,'certificate_valid':certvalid,
         'certificate_physical_reuse':not refresh and physical,'certificate_useful_reuse':not refresh and attributed,'physical_delivered':physical,'attributed_useful':attributed,
         'actual_failed':failed,'returned_failed':returned,'q1_delta_before':before_delta,'q1_delta_after':after_delta,'q1_changed':before_delta!=after_delta,
         'requested_unique_episode':rc['unique_requested'],'applied_unique_episode':rc['applied'],'rejected_unique_episode':rc['rejected'],'pending_unique_episode':rc['pending_or_other'],
         'permissions_after':integer(environment['permissions'],'permissions_after'),'remaining_stock':integer(resource['remaining_stock'],'remaining_stock'),
         'witness':str(path.relative_to(root)).replace('\\','/'),'witness_sha256':sha(path.read_bytes())}
    need(row['query_released']==granted,'Released register must follow actual granted access')
    return row,unique

def _summary(rows,all_receipts):
    need(rows,'No completed witnesses for this life')
    rows=sorted(rows,key=lambda r:r['ordinal'])
    need(len({r['ordinal']for r in rows})==len(rows),'Repeated ordinals must be de-aliased first')
    for left,right in zip(rows,rows[1:]):need(right['before_tick']>=left['after_tick'],'Overlapping Native episode intervals')
    rc,_=receipts(all_receipts);reserved=[r for r in rows if r['reserved']]
    def totals(selected):
        return {key:sum(bool(r[key])for r in selected)for key in(
            'physical_delivered','attributed_useful','actual_failed','returned_failed','q1_NULL','q2_NULL','query_released',
            'query_granted','query_denied','refresh_FI','reuse_attempt','certificate_physical_reuse','certificate_useful_reuse','q1_changed')}
    bymode={mode:{'opportunities':len([r for r in rows if r['mode']==mode]),**totals([r for r in rows if r['mode']==mode])}for mode in sorted({r['mode']for r in rows})}
    transitions=[{'ordinal':r['ordinal'],'tick':r['after_tick'],'before':r['q1_delta_before'],'after':r['q1_delta_after'],
                  'actual_failed':r['actual_failed'],'returned_failed':r['returned_failed']}for r in rows if r['q1_changed']]
    return {'life_id':rows[0]['life_id'],'completed_opportunities':len(rows),'reserved_opportunities':len(reserved),
            'start_tick_first_witness':rows[0]['before_tick'],'end_tick_last_witness':rows[-1]['after_tick'],
            'Native_ticks_completed_witnesses':sum(r['Native_ticks']for r in rows),
            'Native_span':rows[-1]['after_tick']-rows[0]['before_tick'],'uncovered_Native_ticks_between_witnesses':sum(max(0,b['before_tick']-a['after_tick'])for a,b in zip(rows,rows[1:])),
            'totals':totals(rows),'reserved_totals':totals(reserved),'by_environment_mode':bymode,
            'Native_inputs_unique':rc,'q1_choices':[r['q1_choice']for r in rows],'q2_choices':[r['q2_choice']for r in rows],
            'actual_FI_choices':[r['actual_FI_choice']for r in rows],'Q1_transitions':transitions,
            'ordinals_included':[r['ordinal']for r in rows],'ordinals_missing_within_observed_range':[n for n in range(rows[0]['ordinal'],rows[-1]['ordinal']+1)if n not in{r['ordinal']for r in rows}],
            'last_remaining_stock':rows[-1]['remaining_stock'],'last_permissions':rows[-1]['permissions_after'],
            'interpretation_limits':['Closed completed witnesses only. Missing/in-progress files are coverage gaps, not cognitive failures.',
                'Native output zero is retained separately from NULL; no silence fallback.',
                'Certificate, permissions and cached RAW are external environmental/bridge state, not Native memory.',
                'Failed outcome followed by a changed Q1 reference is a recorded association, not exclusive proof of contingent learning.',
                'A Q1 change without immediate utility is retained; no latent learning or future benefit is inferred without later evidence.',
                'Branches with a common prefix are paired controls, not independent replications.']}

def recalculate(primary_root,output,closure_proof):
    root=plain(primary_root);need(root.is_dir(),'Explicit frozen primaries directory required')
    proof=plain(closure_proof);declaration=load(proof)
    need(declaration.get('closed_for_documentary_read')is True and isinstance(declaration.get('closure_evidence'),(str,dict,list)),'Coordinator declaration of closure with evidence locator required; this script does not inspect a live owner')
    destination=plain(output,False);need(destination!=root and root not in destination.parents,'Output must be separate from primaries')
    need(not destination.exists()or destination.is_dir()and not any(destination.iterdir()),'Output must be NEW/empty, never overwrite evidence')
    paths=sorted(root.rglob('episodio_*.json'));need(paths,'No completed Native witness files located; not a cognitive-failure result')
    lives={};aliases=[];seen={};source_manifest=[]
    for candidate in paths:
        p=plain(candidate);need(root in p.parents,'Witness escaped explicit primary root')
        value=load(p);need('life_id'in value and'ordinal'in value,'Unexpected non-witness matching episodio_*.json')
        key=(value['life_id'],value['ordinal']);digest=sha(p.read_bytes())
        if key in seen:
            need(seen[key]==digest,'Distinct witness bytes for same life/ordinal')
            aliases.append(str(p.relative_to(root)));continue
        seen[key]=digest;life=value['life_id'];start=value['environment_after']['start_tick']
        bucket=lives.setdefault(life,{'start':start,'rows':[],'receipts':[]})
        row,_=episode(value,p,root,bucket['start']);bucket['rows'].append(row);bucket['receipts'].extend(value['requests'])
        source_manifest.append({'relative_file':str(p.relative_to(root)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':digest})
    summaries={life:_summary(bucket['rows'],bucket['receipts'])for life,bucket in sorted(lives.items())}
    result={'schema':VERSION,'Native_executed':False,'DEE_imported':False,'SQLite_opened':False,
            'reserve_rule':'before_tick - environment_start_tick >= 18000; first episode interval crossing threshold is not retrospectively reserved',
            'closed_declaration':declaration,'closure_proof_sha256':sha(proof.read_bytes()),
            'source_manifest':source_manifest,'witness_file_aliases_excluded':aliases,'by_life':summaries,
            'cross_life_comparison':'Raw life summaries only; shared prefix, actual exposures and return arms must be interpreted from the protocol. No pooled intelligence score.'}
    rows=sorted((row for b in lives.values()for row in b['rows']),key=lambda row:(row['life_id'],row['ordinal']))
    destination.mkdir(parents=True,exist_ok=True)
    with(destination/'EPISODIOS_PI11.csv').open('x',encoding='utf-8',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
    with(destination/'RESUMEN_PI11.json').open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--primarios',required=True);parser.add_argument('--salida',required=True);parser.add_argument('--cierre',required=True)
    args=parser.parse_args();out=recalculate(args.primarios,args.salida,args.cierre)
    print(json.dumps({'schema':VERSION,'Native_executed':False,'lives':list(out['by_life']),'output':str(Path(args.salida).absolute())},ensure_ascii=False))
