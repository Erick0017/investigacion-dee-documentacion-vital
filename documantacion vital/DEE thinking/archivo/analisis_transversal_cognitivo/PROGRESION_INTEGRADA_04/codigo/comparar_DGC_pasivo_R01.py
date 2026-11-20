"""Compare two CLOSED new C2C observer diagnostics; stdlib and frozen files only.

Usage: python comparar_DGC_pasivo_R01.py --full PRIMARY --compact PRIMARY
       --output NEW_JSON [--system PATH]
No primary, snapshot or journal is modified.  This never imports DEE.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, runpy

P4=Path(__file__).resolve().parents[1]
KEY='DEE.Cognitive.PI04.DGC.q4_observation.R01'
HISTORY_KEYS=('DEE.Cognitive.PI04.C2.coordination.R01','DEE.Cognitive.PI04.C2B.coordination.R01')

def sha(b):return hashlib.sha256(b).hexdigest()
def info(path):
    b=path.read_bytes();return {'path':str(path.resolve()),'bytes':len(b),'sha256':sha(b)}
def primary(path):
    d=json.loads(path.read_text(encoding='utf-8-sig'))
    return json.loads(d['result'])if isinstance(d.get('result'),str)else d
def journal(path):
    chain='00'*32;events=[]
    for line in path.read_bytes().splitlines(keepends=True):
        e=json.loads(line)
        if e['index']!=len(events):raise ValueError('Journal index/line mismatch')
        chain=sha(bytes.fromhex(chain)+line);events.append(e)
    if not events or events[-1]['kind']!='DG_COMPLETED':raise ValueError('Completed closed DGC journal required')
    return events,chain
def point(frame,site):
    sample=next(x for x in frame['observations']if x['site']==site)
    return {k:sample[k]for k in ('site','raw','clock','state','s_reg','semantic','direction')}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--full',type=Path,required=True);ap.add_argument('--compact',type=Path,required=True)
    ap.add_argument('--system',type=Path,default=P4/'estados/candidato_R02/sistema')
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError('Never overwrite a completed or failed proof')
    parser_path=P4/'codigo/contrastar_finales_E3_pasivo.py'
    parse=runpy.run_path(str(parser_path),run_name='pure_DGC_snapshot_parser')['parse']
    results={};parsed={};sources={};frames={};journal_evidence={}
    for arm in ('full','compact'):
        path=getattr(args,arm);d=primary(path);r=d['result']['rows'][0]
        if r['version']!='PI04.DGC.q4_observation.NEW_DIAGNOSTIC.R01'or r['recording']!=arm or r['condition']!='single':raise ValueError('Exact DGC revision and two single recording modes required')
        if r['before_tick']!=800379 or r['after_tick']!=801161 or r['new_native_ticks']!=782:raise ValueError('Only predeclared matched782-tick source800379 diagnostic')
        if not r['all_inputs_applied']or r['requested']!=4 or r['applied']!=4:raise ValueError('No passivity inference with differing/rejected material input')
        if any(r[k]for k in ('efference_count','generic_return_count','arithmetic_calls','actuator_calls')):raise ValueError('Not the no-actuator observer diagnostic')
        cut=d['committed_snapshot'];v=parse(args.system/cut['snapshot'],cut['snapshot_sha256'])
        if v[0]['physical']!={k:cut['physical'][k]for k in ('N','tick','RAW_sha256','clocks_sha256')}:raise ValueError('Snapshot differs from committed primary')
        if v[4]:raise ValueError('Closed Native agenda required')
        meta=json.loads(v[6][KEY])
        if meta['pending']is not None or meta['uncertain']or not meta['completed']:raise ValueError('Incomplete DGC metadata; preserve without passivity conclusion')
        log=Path(r['frames'][0]['journal']['file']);events,chain=journal(log)
        if len(events)!=meta['log_count']or chain!=meta['log_chain_sha256']:raise ValueError('Closed journal is not paired with the actual snapshot')
        f={e['frame']['relative_to_query']:e['frame']for e in events if e['kind']=='DG_PASSIVE_FRAME'}
        if set(f)!=set(range(-1,9)):raise ValueError('Ten predeclared phase frames required')
        if any(len(x['observations'])!=(448 if arm=='full' else 0)for x in f.values()):raise ValueError('ROI coverage does not match the declared observer treatment')
        if arm=='full'and r['q4_Q_observation']!=f[4]['q4_Q_from_existing_ROI_no_additional_read']:raise ValueError('Q4 observation does not refer to its existing ROI sample')
        if arm=='compact'and(r['q4_Q_sample_present']or r['q4_Q_observation']is not None):raise ValueError('Compact must not read or invent a Q4 sample')
        for k in HISTORY_KEYS:
            if sha(v[6][k].encode('utf-8'))!=meta['source_history_sha256'][k]:raise ValueError('Historical C2/B capsule changed during this diagnostic')
        results[arm]=r;parsed[arm]=v;frames[arm]=f
        sources[arm]={'primary':info(path),'snapshot':v[0]['snapshot'],'physical':v[0]['physical'],'life_id':r['life_id'],'journal':info(log)}
        journal_evidence[arm]={'lines':len(events),'chain_sha256':chain,'metadata_log_count':meta['log_count'],'metadata_pending':meta['pending'],'historical_capsules_unchanged':True}
    a=parsed['full'];b=parsed['compact'];rf=results['full'];rc=results['compact']
    meta_diffs=[]
    def allowed(k):return k==KEY or k=='DEE.Cognitive.System.1.1.life.v1'or k.startswith('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1')
    for key in sorted(set(a[6])|set(b[6])):
        x=a[6].get(key);y=b[6].get(key)
        if x!=y:meta_diffs.append({'key':key,'declared_logging_transport_identity_only':allowed(key),'full_sha256':sha(x.encode())if x is not None else None,'compact_sha256':sha(y.encode())if y is not None else None})
    comparisons=[]
    for rel in range(-1,9):comparisons.append({'relative_to_query':rel,'global_physical_hashes_exact':frames['full'][rel]['physical']==frames['compact'][rel]['physical'],'full_ROI':448,'compact_ROI':0})
    same_inputs=[(x['channel'],x['payload'],x['requested_tick'],x['receipt'])for x in rf['requests']]==[(x['channel'],x['payload'],x['requested_tick'],x['receipt'])for x in rc['requests']]
    checks={'same_four_material_requests_and_receipts':same_inputs,'same_calendar':rf['calendar']==rc['calendar'],
            'all10_global_frame_hashes_exact':all(x['global_physical_hashes_exact']for x in comparisons),
            'whole_RAW_bytes_exact':a[7]==b[7],'whole_clocks_bytes_exact':a[8]==b[8],
            'interfaces_exact':a[3]==b[3],'agenda_exact':a[4]==b[4],
            'all_Native_receipt_history_exact':a[5]==b[5],
            'pre_metadata_causal_prefix_exact':a[0]['causal_prefix_sha256']==b[0]['causal_prefix_sha256'],
            'same_necessary_six_site_q6_reader':rf['reader']==rc['reader'],
            'old_C2_capsule_exact_across_arms':a[6][HISTORY_KEYS[0]]==b[6][HISTORY_KEYS[0]],
            'closed_B_capsule_exact_across_arms':a[6][HISTORY_KEYS[1]]==b[6][HISTORY_KEYS[1]],
            'metadata_differences_only_declared_logging_transport_identity':all(x['declared_logging_transport_identity_only']for x in meta_diffs)}
    selected={str(rel):{name:point(frames['full'][rel],site)for name,site in {'Q':[19,54,5],'single_datum':[18,54,6],'SEM4_intercept':[19,55,4],'q6_equality_reader':[19,56,3],'eligibility_hub':[19,53,3]}.items()}for rel in (3,4,5,6,7,8)}
    q4=point(frames['full'][4],[19,54,5]);q4material_zero=q4['state']>0 and q4['semantic']==1 and q4['s_reg']==0 and q4['direction']==[0,1,-1]
    proof={'schema':'PI04.DGC.new_observer_diagnostic.closed_passive_comparison.R01','inspection_local':datetime.datetime.now().astimezone().isoformat(),
           'sources':sources,'analysis_code':info(Path(__file__)),'parser_code':info(parser_path),'journal_verification':journal_evidence,
           'passivity_checks':checks,'all_predeclared_checks_pass':all(checks.values()),'frame_comparisons':comparisons,'metadata_differences':meta_diffs,
           'full_recorded_field_evidence':selected,'q4_Q_sample':q4,'q4_material_zero_signature':q4material_zero,
           'old_q6_sensor_choices':{k:v['reader']['choice']for k,v in results.items()},
           'not_automatic_approval':True,'interpretation':[
             'This is a NEW observer diagnostic at the actually reached complete T800379 cut, not a replay of the original equality failure or a restoration of MAIN.',
             'Both clones received the same three material zero queries and the same datum5 on the old single+Z interface. Full added4480passive ROI observations, including the existing Q sample atq+4; compact omitted those observations while retaining the same necessary six-siteq+6 sensor.',
             'If all predeclared checks pass, the additional ROI/Q4 observation is passive within this exact source, input schedule, phase and782-tick horizon. The comparison does not establish neutrality of material queries, all future observation, or arbitrary instruments.',
             'A distinguishable q+4 material-zero signature, if present, is an external observation of the source-state evolution. This no-actuator diagnostic does not by itself demonstrate Native use, acquired sensor choice, repair of FI admission, or learning through a complete environment-return loop.',
             'The metadata exclusions are explicit life identity, DGC logging state and persistent-service bookkeeping only. Exact RAW/clocks is not labelled equality of the complete operational worlds.'
           ],'new_Native_ticks_by_analysis':0,'DEE_imports':0,'Native_recorded_by_Root':{'clones':2,'ticks_each':782,'total':1564},'originals_modified':False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':info(args.output),'checks':checks,'q4_Q':q4,'q4_zero':q4material_zero,'q6_choices':proof['old_q6_sensor_choices']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
