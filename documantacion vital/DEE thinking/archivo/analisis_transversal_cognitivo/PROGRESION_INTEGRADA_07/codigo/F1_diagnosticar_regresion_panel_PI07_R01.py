"""Read only closed PI07 panel primaries, three snapshots and last R03 capture.

No Native, owner, SQLite access, dynamic decoder search or claim that an
uncaptured intermediate trajectory was measured. Writes one new P7 proof.
"""
from pathlib import Path
import hashlib,json,runpy,struct

P=Path(__file__).resolve().parents[1];S=P/'estados/candidato/sistema'
OUT=P/'control/F1_REGRESION_FIPLUS_PANEL_RECALCULADA_PI07_R01.json'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def outer(p):
    d=read(p);return json.loads(d['result'])if isinstance(d['result'],str)else d['result']


def main():
    if OUT.exists():raise FileExistsError(OUT)
    parse_path=P.parent/'PROGRESION_INTEGRADA_05/codigo/contrastar_prefijos_C2C_PI05_pasivo.py'
    assert sha(parse_path)=='5d84e2a21d6650f1dd69d3c677eb32db0aa9da9f0ae0ed315bb2d0992852124b'
    mod=runpy.run_path(str(parse_path),run_name='pure_closed_snapshot_inspection')
    panel_path=P/'control/PI07_PANEL_INTERCALADO_R01.json';panel=read(panel_path)
    assert panel['closed']is True and panel['status']=='STOPPED_PRESERVED'
    fi_path=P/'ensayos/PI07_PANEL_INTERCALADO_R01_FIplus.json';fi=outer(fi_path)
    row=fi['result']['rows'][0];trial=row['original_result']['native_trial'];q=row['query_tick']
    assert q==856256 and fi['before_tick']==856200 and fi['after_tick']==856398
    alfa_path=P/'ensayos/PI07_PANEL_INTERCALADO_R01_alfa.json'
    cards={'source_R03':panel['R03_state_before']['committed_snapshot'],
           'before_FI':outer(alfa_path)['committed_snapshot'],'after_FI':panel['closed_card']}
    views={};source_checks=[]
    for label,card in cards.items():
        path=S/card['snapshot'];before=sha(path);parsed=mod['parse'](path,card['snapshot_sha256'])
        public,raw,clocks=parsed[:3];n=public['physical']['N'];lane=[]
        for z in range(n):
            i=(52*n+48)*n+z
            if raw[i]:lane.append({'site':[52,48,z],'clock':int(clocks[i]),**mod['decode'](raw[i])})
        assert sha(path)==before==card['snapshot_sha256']
        views[label]={'snapshot':public['snapshot'],'physical':public['physical'],
          'all_RAW_nonzero_in_fixed_row_x52_y48':lane,'Native_pending_count':public['pending_count']}
        source_checks.append({'file':str(path),'before_sha256':before,'after_sha256':sha(path)})
    def positions(label):
        rows=views[label]['all_RAW_nonzero_in_fixed_row_x52_y48']
        assert all(r['state']==1 and r['semantic']==1 and r['s_reg']==0 and r['direction']==[0,0,1]for r in rows)
        return sorted(r['site'][2]for r in rows)
    shifts=[]
    for a,b in [('source_R03','before_FI'),('before_FI','after_FI')]:
        dt=views[b]['physical']['tick']-views[a]['physical']['tick']
        pred=sorted((z+dt)%67 for z in positions(a));actual=positions(b)
        assert pred==actual
        shifts.append({'from':a,'to':b,'ticks':dt,'predicted_toroidal_set':pred,'observed_endpoint_set':actual,
          'endpoint_set_match':True,'continuous_path_observed':False,'unique_ancestry_inferred':False})
    receipts=row['all_material_receipts'];ids=[r['id']for r in receipts]
    assert len(ids)==len(set(ids))==176
    assert all(r['receipt']['status']=='applied'for r in receipts)
    assert row['early_physical_choice']==row['old_q6_choice']==-1
    early=row['early_observation'];assert mod['decode'](int(early['raw']))['direction'][0]==-1
    c=trial['frames'][0]['fields']['C'];s=trial['frames'][2]['fields']['S']
    assert c['s_reg']==s['s_reg']==17
    pre=trial['references_pre'];post=trial['references_after']
    assert pre[0]['s_reg']-pre[1]['s_reg']==post[0]['s_reg']-post[1]['s_reg']==-20
    # One existing capture only. Decode every one of its31 frames, inspect only
    # the fixed67-site line; do not sweep the global landscape for a new reader.
    ep10_path=P/'ensayos/PI07_CAMBIO_RES_B_R03_EP10.json';ep10=outer(ep10_path)['result']['rows'][0]
    capture=ep10['external_global_capture'];directory=Path(capture['directory'])
    index=directory/'INDEX.json';assert sha(index)==capture['index_sha256']
    codec_path=P.parent/'PROGRESION_INTEGRADA_05/codigo/observador_global_PI05_R01.py'
    assert sha(codec_path)=='d60d58301fd29ae0aabf577adc2d6f82392ed42f1d691890d095873cdf80f8d6'
    codec=runpy.run_path(str(codec_path),run_name='pure_frozen_frame_codec');trace=[]
    for f in codec['iter_frames'](directory):
        lane=[]
        for z in range(67):
            i=(52*67+48)*67+z;v=struct.unpack_from('<Q',f['raw_bytes'],8*i)[0]
            if v:lane.append({'site':[52,48,z],'clock':struct.unpack_from('<Q',f['clocks_bytes'],8*i)[0],**mod['decode'](v)})
        trace.append({'tick':f['tick'],'complete_RAW_clocks_hashes':f['hashes'],'fixed_row_RAW_nonzero':lane})
    assert len(trace)==31 and sha(index)==capture['index_sha256']
    # This fixed parent coordinate/time is from the already measured FI128
    # protocol. The following is a conditional phase projection, not a frame.
    parent_tick=q-48;dt=parent_tick-views['before_FI']['physical']['tick']
    projected=[{'from_z':z,'to_z':(z+dt)%67}for z in positions('before_FI')]
    assert dt==8 and [r['from_z']for r in projected if r['to_z']==58]==[50]
    result={'schema':'DEE.PI07.F1.closed_panel_FIplus_regression.passive_recalculation.v1',
      'Native_ticks':0,'DEE_imports':0,'sources':[{'file':str(x),'sha256':sha(x)}for x in(panel_path,fi_path,alfa_path,ep10_path,parse_path,codec_path)],
      'panel':{'status':panel['status'],'correct':panel['correct'],'tested':panel['tested'],
        'expected_uses':panel['expected_uses'],'before_tick':panel['before_tick'],'after_tick':panel['after_tick'],
        'new_Native_ticks':panel['new_Native_ticks'],'Native_inputs':panel['Native_inputs'],
        'scientific_stop':panel['scientific_stop'],'principal_modified':panel['principal_modified']},
      'FI':{'before_tick':fi['before_tick'],'after_tick':fi['after_tick'],'query_tick':q,
        'early_tick':row['early_tick'],'early_observation':early,'early_choice':row['early_physical_choice'],
        'old_q6_choice':row['old_q6_choice'],'old_reader':trial['reader'],
        'unique_material_receipts':176,'all_applied':True,'Native_receipt_ids':ids,
        'input_tick':trial['input_tick'],'raw_components':trial['raw_components'],
        'references_pre':pre,'references_after':post,'MU_reference_difference_preserved':-20,
        'observed_C':c,'observed_S':s,'local_query_frames':trial['frames'],
        'actual_material_minus_one_not_NULL':True,'decoder_was_not_changed':True},
      'closed_snapshots':views,'source_snapshot_hashes_before_after':source_checks,
      'last_existing_R03_capture':{'primary':str(ep10_path),'directory':str(directory),
        'index_sha256':capture['index_sha256'],'frames':trace,'coverage':'Full31buffers reconstructed/hash-checked, only fixed row67sites inspected.'},
      'endpoint_translation_checks':shifts,
      'uncaptured_parent_phase_projection':{'parent_site':[52,48,58],'tick':parent_tick,
        'basis_tick':856200,'advance':dt,'projected_fixed_row_positions':projected,
        'predicted_occupied_parent_if_free_plusZ_translation':[52,48,58],
        'measured_intermediate_frame':False,'other_paths_or_encounters_not_excluded':True,
        'supports_prior_mechanism':'Observed C17 rather than intended31 agrees with loss of the14contribution at the previously implicated parent. The missing intermediate frame prevents claiming a newly measured encounter or unique origin.'},
      'scientific_scope':'Material regression of a retained comparison access at this cut. Five named associations still work. Bank difference is preserved; no claim of global content loss, Native memory erasure, learned repair, universal passivity or a unique zero-carrier lineage. Adoption blocked; no query retry or teaching by this analysis.'}
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':str(OUT),'bytes':OUT.stat().st_size,'sha256':sha(OUT),
       'FI_material_choice':-1,'receipt_unique_applied':176,'panel_correct_tested':[5,6],
       'source_row':positions('source_R03'),'before_FI_row':positions('before_FI'),
       'after_FI_row':positions('after_FI'),'parent_projection_only':True,'Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
