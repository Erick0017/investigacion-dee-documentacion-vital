"""Recalculate selected R08 claims from exported evidence, without DEE.

This is an evidence recalculation, not a native protocol replay or a new
experiment. Complete operative snapshots remain at the cited local sources.
"""
from pathlib import Path
from array import array
import argparse,base64,gzip,hashlib,json,sys

ROOT=Path(__file__).resolve().parents[1]
def read(path):
    b=Path(path).read_bytes()
    return json.loads(gzip.decompress(b) if b[:2]==b'\x1f\x8b' else b)
def sha(b):return hashlib.sha256(b).hexdigest()
def fields(raw):
    v=int(raw)
    def signed(shift):
        n=(v>>shift)&15
        return n-16 if n&8 else n
    return {'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':(v>>60)&15,
            'direction':[signed(s) for s in (48,52,56)]}
def observations(d):
    if isinstance(d,dict):
        if 'site' in d and 'raw' in d:yield d
        for v in d.values():yield from observations(v)
    elif isinstance(d,list):
        for v in d:yield from observations(v)
def unpack(packet):
    b=gzip.decompress(base64.b64decode(packet['data']))
    assert len(b)==packet['bytes'] and sha(b)==packet['sha256']
    a=array('Q');a.frombytes(b)
    if sys.byteorder!='little':a.byteswap()
    return a
def check():
    central=read(ROOT/'evidencia_central/CENTRAL_R08_DATOS_EXACTOS.json.gz')
    mechanisms=read(ROOT/'infraestructura/FUENTES_MECANISMOS_S06_S11_R08.json')
    principal=read(ROOT/'evidencia_principal/PRINCIPAL_R08_DATOS_EXACTOS.json.gz')
    counts={};snaps={}
    for name,s in central['snapshot_panels'].items():
        raw=unpack(s['complete_buffers']['RAW']);clock=unpack(s['complete_buffers']['clocks'])
        assert len(raw)==len(clock)==s['N']**3
        assert len(s['points'])==sum(bool(v) for v in raw)
        counts[name]={'raw_nonzero':sum(bool(v) for v in raw),'state0_nonzero':sum(bool(v) and (v&0xffffffff)==0 for v in raw)}
        snaps[name]=(raw,clock)
    differences={}
    for t in (719846,719851):
        a,ca=snaps[f'EDAD_T{t}'];b,cb=snaps[f'MINUS_T{t}']
        differences[str(t)]={'RAW':sum(x!=y for x,y in zip(a,b)),'clock':sum(x!=y for x,y in zip(ca,cb))}
    assert differences=={'719846':{'RAW':0,'clock':0},'719851':{'RAW':1,'clock':0}}
    readers={}
    for name,p in central['reader_panels'].items():
        selected=[q for q in p['points'] if q['site'] in p['reader_sites']]
        assert len(selected)==1
        f=fields(selected[0]['raw'])
        assert f['state']>0 and f['semantic']==1 and f['direction'][:2]==[0,0]
        sign=f['direction'][2]
        assert sign==p['output']==p['reader_contract']['formed_native_command']
        assert sign==(1 if name.startswith('EDAD') else -1)
        readers[name]={'input_tick':p['input_tick'],'read_tick':p['tick'],'sign':sign}
    nchecked=0
    for group in (central,mechanisms,principal):
        for p in observations(group):
            f=fields(p['raw'])
            for k,v in f.items():
                if k in p:assert p[k]==v,(k,p['site'],p[k],v)
            nchecked+=1
    comp=mechanisms['cases']['CPC9_COMPOSITION']['data']
    incoming=[fields(v['raw'])['s_reg'] for v in comp['incoming']]
    formed=fields(comp['formed']['raw'])['s_reg']
    after=fields(comp['baseline_consequence210']['raw'])['s_reg']
    assert incoming==[26,30] and formed==56 and after==63
    controls={c['condition']:fields(c['consequence210']['raw'])['s_reg'] for c in comp['conditions']}
    assert controls['cut_arrival_0']==7 and controls['cut_arrival_1']==7
    fi=mechanisms['cases']['FI128_7_7']['data']
    assert fi['early_physical_choice']==0 and fi['old_q6_choice'] is None
    assert int(fi['early_observation']['raw'])!=0
    panel=principal['panel_recount']
    assert panel['requested']==panel['correct_with_full_admission']==12
    assert panel['total_native_inputs']['requested']==panel['total_native_inputs']['applied']==929
    assert all(principal['recomputed_save_restore_equality'].values())
    schedule=read(ROOT/'audio/TIEMPOS_ANCLAS_R08.json')
    rows=schedule['rows'];assert schedule['all_fit'] and not schedule['violations']
    assert rows[0]['first_visual_frame_30fps']==0 and rows[-1]['end_visual_frame_exclusive_30fps']==11700
    assert all(a['end_visual_frame_exclusive_30fps']==b['first_visual_frame_30fps'] for a,b in zip(rows,rows[1:]))
    return {'new_Native_ticks':0,'not_a_native_replay':True,'snapshot_sparse_counts':counts,
       'matched_complete_buffer_differences':differences,'qualified_central_readers':readers,
       'RAW_field_observations_redecoded':nchecked,'composition':{'incoming':incoming,'formed':formed,'later_use':after,'controls':controls},
       'FI128':{'q4_qualified_zero':fi['early_physical_choice'],'q6_no_result':fi['old_q6_choice'],'zero_is_not_RAW0':True},
       'closure_recount':{'responses_concordant':12,'requests':12,'material_applied':929,'material_requested':929},
       'closure_save_restore':'Original complete comparison recalculated locally, sparse exported images only; not a full operative snapshot backup.',
       'scene_frames':11700,'duration_seconds':390,'limitations':['No independent audience test.','No new Native evolution.',
          'Perceptual audio review and independent ASR are not performed by this script.',
          'Complete historical snapshots outside the four paired central RAW/clock buffers are locally cited, not redistributed.']}
def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--out',type=Path);a=p.parse_args();d=check();s=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        with a.out.open('x',encoding='utf8') as f:f.write(s)
    print(s)
if __name__=='__main__':main()
