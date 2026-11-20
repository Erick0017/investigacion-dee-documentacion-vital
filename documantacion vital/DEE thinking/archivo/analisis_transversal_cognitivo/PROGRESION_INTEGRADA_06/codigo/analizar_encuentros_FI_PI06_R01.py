"""Retrospective frozen-frame contact analysis, not a new actor reader or lineage."""
from pathlib import Path
from array import array
import argparse,hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1]
OBSERVER=P.parents[2]/'DEE Cognitive 2.0/sistema/capacidades/observador_global_PI05_R01.py'
POINTS={'left_parent':[52,48,58],'left_source':[52,48,56],
        'right_parent':[19,53,25],'right_source':[19,53,23],
        'C':[12,17,18],'S':[14,15,16],'E':[15,15,15],
        'Q_A':[18,53,5],'Q_B':[20,53,5],'MU_A':[14,14,15],'MU_B':[16,14,15],
        'guard_PI05':[19,53,20],'guard_PI03':[19,57,5]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def idx(site,n):return (site[0]*n+site[1])*n+site[2]
def xyz(i,n):return [i//(n*n),(i//n)%n,i%n]
def fields(v):
    ds=[(v>>s)&15 for s in(48,52,56)]
    return {'RAW':str(v),'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':v>>60,
        'direction':[d-16 if d&8 else d for d in ds]}
def point(raw,clock,site,n):
    i=idx(site,n);return {'site':list(site),'clock':int(clock[i]),**fields(raw[i])}
def main(a):
    proof=Path(a.recuento).resolve(strict=True)
    if not proof.is_relative_to(P.resolve()):raise ValueError('Campaign proof only')
    rec=read(proof)
    spec=importlib.util.spec_from_file_location('PI06_exact_frame_codec',OBSERVER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    arms=[]
    for case in rec['cases']:
        results=[]
        for op in case['rows']:
            if 'condition'not in op or op.get('capture')is None:continue
            directory=Path(op['capture']['directory']).resolve(strict=True)
            if not directory.is_relative_to(P.resolve()):raise ValueError('Campaign capture only')
            if sha(directory/'INDEX.json')!=op['capture']['index_sha256']:raise ValueError('Index differs from actual primary')
            snapshots=[];q=op['query_tick'];n=67
            for frame in module.iter_frames(directory):
                raw=array('Q');clock=array('Q');raw.frombytes(frame['raw_bytes']);clock.frombytes(frame['clocks_bytes'])
                if sys.byteorder!='little':raw.byteswap();clock.byteswap()
                # Fixed physical signature, inspected after outcome only. All
                # matching sites are retained; none is assigned an identity.
                candidates=[xyz(i,n)for i,v in enumerate(raw)if (v&0xffffffff)>0 and
                    ((v>>32)&65535)==0 and (v>>60)==1 and ((v>>48)&4095)==0x100]
                left_line=[point(raw,clock,[52,48,z],n)for z in range(n)if raw[idx([52,48,z],n)]!=0]
                parent_neighbors=[]
                if -51<=frame['tick']-q<=-44:
                    for dx in(-1,0,1):
                        for dy in(-1,0,1):
                            for dz in(-1,0,1):
                                site=[(52+dx)%n,(48+dy)%n,(58+dz)%n]
                                parent_neighbors.append(point(raw,clock,site,n))
                snapshots.append({'tick':frame['tick'],'offset_from_query':frame['tick']-q,'hashes':frame['hashes'],
                    'fixed_points':{name:point(raw,clock,site,n)for name,site in POINTS.items()},
                    'active_SEM1_zero_plusZ_matching_sites':candidates,
                    'matching_signature_is_not_unique_carrier_identity':True,
                    'left_line_nonzero_RAW_all_states':left_line,'parent_Moore1_at_contact':parent_neighbors})
            results.append({'label':op['label'],'condition':op['condition'],'query_tick':q,
                'observed_q4':op['observed_q4'],'observed_q6':op['observed_q6'],
                'capture':op['capture'],'frames':snapshots,'frames_verified':len(snapshots),
                'contact_summary':[{'tick':f['tick'],'offset':f['offset_from_query'],
                    'left_parent':f['fixed_points']['left_parent'],'matching_zero_plusZ':f['active_SEM1_zero_plusZ_matching_sites']}
                    for f in snapshots if f['offset_from_query']in(-50,-49,-48,-47,-46,1,3,4,6)],
                'reference_bank_signatures_unchanged_within_captured_window':
                    {name:len({f['fixed_points'][name]['RAW']for f in snapshots})==1 for name in('Q_A','Q_B','MU_A','MU_B')},
                'not_new_instrument_used_to_score_the_actor':True})
        arms.append({'life_id':case['life_id'],'q4_sequence':case['FI_sequence_q4'],'query_tick_gaps':case['actual_query_tick_gaps'],
                     'third_minus_first_query':case['third_minus_first_query'],'operations':results})
    value={'schema':'DEE.PI06.frozen_FI_contacts.retrospective_analysis.R01',
        'recount':{'file':str(proof),'sha256':sha(proof)},'arms':arms,
        'Native_executed':False,'new_Native_ticks':0,'new_material_queries':0,
        'limits':['Signature matching retains all candidates; no unique carrier ancestry is inferred.',
                  'Frames are at recorded boundaries. Missing intervals are not interpolated.',
                  'q+4/q+6 scores are original fixed readers. The contact neighborhood is retrospective explanatory analysis, not a replacement decoder.',
                  'An impairment/reappearance/impairment sequence alone does not establish learning or regulation; compare intact and material sham at the actual same q and age.']}
    output=Path(a.salida).absolute()
    if not output.parent.resolve().is_relative_to((P/'control').resolve()):raise ValueError('New campaign control output only')
    with output.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(output),'sha256':sha(output),'arms':len(arms),
        'verified_frames':sum(x['frames_verified']for c in arms for x in c['operations']),'Native_executed':False}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--recuento',required=True);ap.add_argument('--salida',required=True)
    main(ap.parse_args())
