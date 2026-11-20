"""MA02 R07: sparse global RAW correction, transport and causal reserved use.

Does not edit primaries or import DEE. The executed exporter swapped X and Z
in global sparse coordinates only. Corrected coordinates must reproduce the
recorded complete RAW-array hash in every frame before spatial interpretation.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

SPEC=importlib.util.spec_from_file_location('common_archived',Path(__file__).with_name('recalcular_entrada_comun.py'))
c=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(c)
N=67;V=[(1,0,0),(0,1,0),(1,1,0),(-1,1,0)]
def site(v,k,z=0):return tuple((33+k*v[j]+(z if j==2 else 0))%N for j in range(3))
GATES=[site(v,4,s)for v in V for s in(-1,1)]


def corrected_frame(frame,transpose=True):
    result={};buf=bytearray(N**3*8)
    for o in frame['nonzero_raw']:
        # Historical stored [k%N,(k//N)%N,k//N²], native index=(xN+y)N+z.
        if transpose:z,y,x=o['site']
        else:x,y,z=o['site']
        p=(x,y,z)
        if p in result:raise ValueError('Duplicate physical sparse coordinate')
        raw=int(o['raw']);clock=int(o['clock'])
        if not (0<raw<2**64 and 0<=clock<2**64):raise ValueError('Non-exact uint64 field')
        struct.pack_into('<Q',buf,((x*N+y)*N+z)*8,raw)
        result[p]={'site':list(p),'raw':o['raw'],'clock':o['clock'],**c.raw_fields(raw)}
    return result,hashlib.sha256(buf).hexdigest()


def calculate(root,revision_name='R07',transpose=True):
    audit=c.Audit(root);cases=[];worlds={};checklist=[]
    def check(name,value):
        checklist.append({'check':name,'observed':bool(value)})
        if not value:audit.issues.append({'check':name,'issue':'not established'})
    for arm in ('CONCORDANT','MIXED','CUT','SHAM'):
        name='MA02_'+revision_name+'_RES_'+arm+'.R07.json.gz';x=audit.load(name)
        revision=next(r for r in x['rows']if r['kind']=='revision')
        joint=next(r for r in x['rows']if r['kind']=='joint')
        audit.check_observation(revision['hub'],name+':revision')
        histories={0:-1,1:revision['new_signal'],2:1,3:-1}
        maps={};frame_hashes=[]
        for frame in joint['frames_global_sparse']:
            mapped,digest=corrected_frame(frame,transpose);maps[frame['tick']]=mapped
            check(name+': corrected complete RAW hash@'+str(frame['tick']),digest==frame['RAW_sha256'])
            frame_hashes.append({'tick':frame['tick'],'nonzero_RAW_records':len(mapped),
                                 'RAW_sha256_reconstructed':digest,'RAW_sha256_recorded':frame['RAW_sha256'],
                                 'clocks_sha256_recorded_unreconstructed':frame['clocks_sha256']})
        worlds[arm]={'maps':maps,'frames':{f['tick']:f for f in joint['frames_global_sparse']},'joint':joint}
        check(name+': consecutive global coverage',sorted(maps)==list(range(2613,2692)))
        for o in joint['fixed_panel']:
            audit.check_observation(o,name+':joint gate')
            raw=maps[joint['read_tick']].get(tuple(o['site']),{}).get('raw','0')
            check(name+': corrected map agrees local API gate'+str(o['site']),raw==o['raw'])
        decoded=c.decode(joint['fixed_panel'],[(33,33,27),(33,33,39)])
        check(name+': fixed joint RAW decoder',decoded['decoded_sign']==joint['decoded_sign'])
        post=[]
        for row in x['rows']:
            if row['kind']!='query':continue
            for o in row['fixed_panel']:audit.check_observation(o,name+':post gate')
            for frame in row['frames']:
                for o in frame['sites']:audit.check_observation(o,name+':post frame'+str(frame['tick']))
            answer=c.decode(row['fixed_panel'],GATES,{site(v,4,s):s for v in V for s in(-1,1)})
            check(name+': post-query fixed RAW decoder@'+str(row['input_tick']),answer['decoded_sign']==row['decoded_sign'])
            rs=[r for r in x['receipts']if row['input_tick']<=r['tick']<=row['input_tick']+7]
            cue=[r for r in rs if r['name'].startswith('common.token.')]
            post.append({'context_for_scoring_only':row['request_token'],'input_tick':row['input_tick'],
                         **answer,'history_sign_for_scoring_only':histories[row['request_token']],
                         'correct':answer['decoded_sign']==histories[row['request_token']],
                         'all_receipts':c.receipt_summary(rs),'cue_receipts':c.receipt_summary(cue)})
        new=[r for r in x['receipts']if r['tick']>x['initial']['tick']]
        teach=[r for r in new if r['tick']==revision['input_tick']]
        cases.append({'file':name,'arm':arm,'parent_tick':x['initial']['tick'],
                      'parent_snapshot_sha256':x['initial']['sha256'],
                      'revision':{'input_tick':revision['input_tick'],'teacher_sign_for_auditor':revision['new_signal'],
                                  'hub_RAW':revision['hub']['raw'],'hub_fields':c.raw_fields(revision['hub']['raw']),
                                  'receipts':c.receipt_summary(teach),'input_records':teach},
                      'joint':{'input_tick':joint['input_tick'],'second_tick':joint['second_tick'],'read_tick':joint['read_tick'],**decoded,
                               'intervention':joint['intervention'],'frame_hashes':frame_hashes},
                      'post_queries':post,'post_correct':sum(q['correct']for q in post),'post_requested':len(post),
                      'new_receipts':c.receipt_summary(new),
                      'final_snapshot_reference':{k:x['final'][k]for k in('bytes','sha256')}})
    check('all four branches exact complete parent hash',len({q['parent_snapshot_sha256']for q in cases})==1)
    con=worlds['CONCORDANT'];sham=worlds['SHAM'];cut=worlds['CUT'];t0=2622;origin=(33,33,27)
    check('concordant and sham all recorded full RAW/clocks hashes equal',all(con['frames'][t]['RAW_sha256']==sham['frames'][t]['RAW_sha256'] and con['frames'][t]['clocks_sha256']==sham['frames'][t]['clocks_sha256']for t in range(2613,2692)))
    check('cut branch before cut equals concordant RAW/clocks',all(con['frames'][t]['RAW_sha256']==cut['frames'][t]['RAW_sha256'] and con['frames'][t]['clocks_sha256']==cut['frames'][t]['clocks_sha256']for t in range(2613,t0)))
    cpre=con['maps'][t0];cpost=cut['maps'][t0]
    diff=[list(p)for p in sorted(set(cpre)|set(cpost))if cpre.get(p,{}).get('raw','0')!=cpost.get(p,{}).get('raw','0')]
    check('cut alters only the formed first record RAW at2622',diff==[list(origin)] and origin not in cpost)
    check('cut preserves complete recorded clock hash at2622',con['frames'][t0]['clocks_sha256']==cut['frames'][t0]['clocks_sha256'])
    first=cpre[origin];trajectory=[];wraps=[];last_pos=origin
    for tick in range(t0,2689):
        dt=tick-t0;pos=((33-dt)%N,33,(27-dt)%N);o=con['maps'][tick].get(pos)
        copies=sum(v['raw']==first['raw']for v in con['maps'][tick].values())
        check('first contribution transport observed@'+str(tick),o is not None and o['raw']==first['raw'] and copies==1)
        if tick>t0:
            axes=[axis for axis in range(3)if abs(pos[axis]-last_pos[axis])>1]
            if axes:wraps.append({'tick':tick,'from':list(last_pos),'to':list(pos),'axes':axes})
        trajectory.append({'tick':tick,'site':list(pos),'raw':o['raw']if o else None,'clock':o['clock']if o else None,
                           'matching_RAW_count_globally':copies})
        last_pos=pos
    incoming_positions=[(34,33,28),(33,34,28),(32,32,27)]
    incoming=[con['maps'][2688][p]for p in incoming_positions]
    product=con['maps'][2689][origin]
    check('three observed predecessors meet product position',all(tuple((o['site'][j]+o['direction'][j])%N for j in range(3))==origin for o in incoming))
    check('joint load equals observed three contribution loads',sum(o['s_reg']for o in incoming)==product['s_reg'])
    check('joint changes first raw and forms pureZ negative',product['raw']!=first['raw'] and product['direction']==[0,0,-1])
    result={'schema':'DEE.MA02.archived_'+revision_name+'_spatial_correction.v1','new_dee_ticks':0,
            'coordinate_correction':({'applies_only_to':'frames_global_sparse[*].nonzero_raw[*].site',
                'original_exporter':'[k%N,(k//N)%N,k//N²]','native_index':'(x*N+y)*N+z',
                'corrected_coordinate':'[stored_z,stored_y,stored_x]','primaries_modified':False,
                'full_RAW_vector_reconstruction':'Little-endian uint64 vector, zero at all unlisted RAW sites, checked against existing complete array hash every frame',
                'full_clock_vector':'Not reconstructed: clocks of RAW-zero sites absent; recorded complete-array clock hashes only.'} if transpose else {
                'applies_only_to':None,'native_exporter':'[k//N²,(k//N)%N,k%N]',
                'native_index':'(x*N+y)*N+z','primaries_modified':False,
                'full_RAW_vector_reconstruction':'Little-endian uint64 vector, zero at all unlisted RAW sites, checked against existing complete array hash every frame',
                'full_clock_vector':'Not reconstructed: clocks of RAW-zero sites absent; recorded complete-array clock hashes only.'}),
            'sources':audit.sources,'cases':cases,'checks':checklist,'observations_checked':audit.observations,
            'first_contribution':{'formed_tick':t0,'origin':list(origin),'raw':first['raw'],'fields':c.raw_fields(first['raw']),
                'per_tick_transport':trajectory,'observed_periodic_crossings':wraps,
                'return_encounter_tick':2689,'return_position':list(origin),'return_after_ticks':67,
                'before_encounter':incoming,'product':product,'cut_RAW_differences_at2622':diff},
            'issues':audit.issues,
            'scope_and_limits':[
                'Four branches share a complete MA02_MAIN T2486 parent; queries and cut/sham are reserved new executions already archived, not independent learners.',
                ('The attempted beta revision has matched three requested inputs but NOT matched admitted dose: concordant/cut/sham apply2/3 with third rejected_occupied, mixed3/3. Treat realized-dose and post-load differences as a confound of the mixed contrast.' if revision_name=='R07' else 'The revised R08 protocol uses four compensated inputs. Counts, admitted dose and observed hub loads are recalculated separately below; R07 unequal-admission limitations remain valid for the original R07 records.'),
                'Concordant and exact sham produce−; selective external cut of the already formed first contribution prevents the joint command, while other two contents remain usable afterward. This establishes a local causal contribution, not autonomous repair.',
                'Global sparse RAW coverage includes all nonzero records, including SEM4 state0. It does not reconstruct clocks of zeroRAW sites, interfaces, agendas or complete causal-state equality.',
                'Observed every-tick unique RAW transport plus two periodic crossings and the selective cut support this particular recurrence. Equal RAW alone is not treated as universal carrier identity; after the three-way encounter multiple antecedents are retained.',
                'The composition is partly destructive: gamma/delta remain accessible; alpha/beta fail the published later reader. Beta input can itself be rejected; do not classify every missing response as physical erasure.',
                'Gate geometry, resources, calendar and query initiation are prepared P0. This limited physical combination of acquired contents is not learned conjunction, general language, P2/R2, or E1-wide integration.' ]}
    if revision_name!='R07':
        admission=[]
        for case in cases:
            rows=case['revision']['input_records']
            admission.append({'arm':case['arm'],'requested':len(rows),'applied':sum(r['receipt']['status']=='applied'for r in rows),
                'requested_dose':sum(r['value']for r in rows),'applied_dose':sum(r['value']for r in rows if r['receipt']['status']=='applied'),
                'hub_fields':case['revision']['hub_fields']})
        check('R08 all four requested/admitted dose38 and equal hub load442',all(a['requested']==a['applied']==4 and a['requested_dose']==a['applied_dose']==38 and a['hub_fields']['s_reg']==442 for a in admission))
        transitions=[]
        # Enumerate ALL nonzero RAW directional records, including state0,
        # projecting onto each child site. No equality-of-load lineage shortcut.
        for tick in range(t0+1,2690):
            dt=tick-t0;dest=((33-dt)%N,33,(27-dt)%N)
            previous=con['maps'][tick-1]
            parents=[o for o in previous.values()if o['direction']!=[0,0,0] and
                tuple((o['site'][j]+o['direction'][j])%N for j in range(3))==dest]
            target=previous.get(dest,{'site':list(dest),'raw':'0','clock':None,**c.raw_fields(0)})
            expected_count=3 if tick==2689 else 1
            check('R08 every directional predecessor enumerated@'+str(tick),len(parents)==expected_count)
            check('R08 previous target has state0@'+str(tick),target['state']==0)
            transitions.append({'tick':tick,'destination':list(dest),'pre_target':target,'possible_directional_sources':parents,
                'source_count':len(parents),'child':con['maps'][tick].get(dest),
                'interpretation':'Enumerated directional predecessor candidates plus observed transition; clocks at zeroRAW targets are unknown, not assumed empty.'})
        result['matched_revision']=admission
        result['first_contribution']['directional_predecessor_transitions']=transitions
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();x=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True)
    a.salida.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'issues':len(x['issues']),'global_RAW_frames_verified':sum(len(q['joint']['frame_hashes'])for q in x['cases']),
        'answers':{q['arm']:q['joint']['decoded_sign']for q in x['cases']},'wraps':x['first_contribution']['observed_periodic_crossings']},ensure_ascii=False))
    return 1 if x['issues']else 0

if __name__=='__main__':raise SystemExit(main())
