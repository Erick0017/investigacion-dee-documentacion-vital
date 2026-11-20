"""Frozen B06 prospective cadence/noise contrasts; same complete A-cut.

Both raw128 frames are queued before either response. No overwrite, retries,
reader changes, summed input, target feedback or repair. Diagnostic forks only.
"""
from __future__ import annotations
import gc,json,os
from pathlib import Path
from ensayar_arbol_b05_r1 import (HERE,LAB,ROOT,SYSTEM,CUT,EXPECTED,E,
    FRONT_SOURCE,front,prepare_frontend,sha,dump,plan,enqueue,
    internal_A_close,native_imports,memory_guard)

REVISION='FI01.B06.cadence_noise.frozen.r1'
CASES=[{'label':'cadence_'+str(dt),'kind':'cadence','delta':dt}for dt in(2,16,67,200)]+[
    {'label':'noise_0','kind':'noise','payload':0,'site':[13,16,17]},
    {'label':'noise_2','kind':'noise','payload':2,'site':[13,16,17]},
    {'label':'noise_32','kind':'noise','payload':32,'site':[13,16,17]},
    {'label':'sham_32','kind':'noise','payload':32,'site':[13,20,17]}]

def execute(a,case,ni,sel,out):
    d,encode,decode,Store,Adapter,now,physical,body,ep=ni
    start=a.tick;g=plan(128,E,67);initial=physical(a.world,occupation=True)
    requests=[];episodes=[];schedule=set();points={'E':E,'D':g['datum_site'],
      'C':g['remote_aggregate_site'],'A':[14,14,15],'B':[16,14,15],
      'precursor':[13,16,17],'sham_site':[13,20,17]}
    points.update({n['id']:n['site']for n in g['nodes']})
    for s in g['generic_sources']:
        points[s['id']+'.source']=s['site']
        points[s['id']+'.meeting']=[(s['site'][i]+s['direction'][i])%67 for i in range(3)]
    for z in(0,-1):
        for x in(-1,0,1):points['actuator_'+str((x,z))]=[(15+2*x)%67,17,(15+2*z)%67]
    values=[[0]*128,[2]+[0]*127]if case['kind']=='cadence'else[[2]+[0]*127]
    leaves=[start+2,start+2+case['delta']]if case['kind']=='cadence'else[start+2]
    for i,(raw,leaf)in enumerate(zip(values,leaves)):
        offered=enqueue(a,raw,level=128,E=E,leaf_tick=leaf,prefix='FI01.B06.raw')
        q=offered['datum_tick']-3;req=offered['requests']+sel.query(a.world,q,5,'MU.selector')
        requests.extend(req);root=offered['root_tick']
        episodes.append({'episode':i,'raw_components':raw,'leaf_tick':leaf,'root_tick':root,
          'datum_tick':offered['datum_tick'],'query_tick':q,'reader_tick':q+6,'request_ids':[r['id']for r in req]})
        schedule.update([leaf-1,leaf,leaf+1,offered['datum_tick']-2,offered['datum_tick']-1,
          offered['datum_tick'],offered['datum_tick']+1,q+6,q+8])
        schedule.update(root+n['join_tick_relative']+dt for n in g['nodes']for dt in(-1,0,1))
        schedule.update(root+s['injection_tick_relative']+dt for s in g['generic_sources']for dt in(0,1,2))
    noise=None
    if case['kind']=='noise':
        tick=episodes[0]['root_tick']+36
        noise={'site':case['site'],'payload':case['payload'],'tick':tick,'direction':[0,0,0],
          'before_scheduling':body.obs(a,case['site'])}
        requests.append(body.send(a,'FI01.B06.unmarked_environment',case['site'],[0,0,0],tick,case['payload']))
        schedule.update([tick-1,tick,tick+1,tick+2,tick+3])
    # Includes complete world, interfaces, pending entries and operational progress.
    pending=out/(case['label']+'.ALL_PENDING.T'+str(a.tick)+'.deetsnap.gz');a.save(pending)
    pending_record={'path':str(pending),'sha256':sha(pending),'tick':a.tick,
      'requested_ids':[r['id']for r in requests],'scope':'Diagnostic full queued pre-window state, not a reconstructed array.'}
    frames=[];readers=[]
    for t in sorted(schedule):
        if t<start:continue
        a.run_until(t);memory_guard()
        frames.append({'tick':a.tick,'fields':{k:body.obs(a,p)for k,p in points.items()}})
        for ep in episodes:
            if t==ep['reader_tick']:readers.append({'episode':ep['episode'],'tick':t,**front.reader(a,ni)})
    common_end=17038 if case['kind']=='cadence'else 16838
    if a.tick>common_end:raise AssertionError('Prospective common horizon violated')
    a.run_until(common_end);memory_guard();passive=physical(a.world,occupation=True)
    from capacidades import mente_acumulativa_r02 as ma
    old=ma.session(a,situations=[{'contexto':c}for c in['alfa','beta','gamma','delta','epsilon','zeta']],
      directory=HERE/'NO_EXTERNAL_ACTIONS',detailed=False)
    return {'revision':REVISION,'label':case['label'],'case':case,'level':128,'initial':initial,
      'geometry':g,'episodes':episodes,'readers':readers,'noise':noise,'all_pending_snapshot':pending_record,
      'frames':frames,'requests':[{**r,'receipt':sel.exact_receipt(a.world.runtime.receipt(r['id']))}for r in requests],
      'passive_common_horizon':passive,'old_six_panel':old,'final':physical(a.world,occupation=True),
      'scope':'Cadence and unmarked legal physical noise; no learned filtering or autonomy attributed. Cadence necessarily changes global391 phase. Each fork has same acquired past.'}

def main():
    authorization=internal_A_close(LAB/'CIERRE_INTERNO_A.json')
    if sha(SYSTEM/CUT)!=EXPECTED:raise ValueError('Immutable complete cut mismatch')
    os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    ni=native_imports();Store=ni[3];now=ni[5]
    from capacidades import selector_acrecion_nativo as sel
    s=Store();active=sha(SYSTEM/'estado/ACTIVO.json')
    out=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento/B06_CADENCE_NOISE_R1'
    dump(out/'PROTOCOLO.json',{'revision':REVISION,'authorization':authorization,'before_native_ticks':now(),
      'source':CUT,'source_sha256':EXPECTED,'script_sha256':sha(__file__),
      'dependency_hashes':{p.name:sha(p)for p in[FRONT_SOURCE,HERE/'ensayar_arbol_b05_r1.py',HERE/'arbol_en_selector_b05.py',HERE/'arbol_en_selector_b02.py',HERE/'arbol_umbral_adquirido_b01.py']},
      'cases':CASES,'frozen_reader':'Six native classes at each fixedq+6; every arm includes old6 after common horizon',
      'same_raw_tick_per_frame':True,'both_frames_enqueued_before_any_read':True,
      'noise_baseline_existing':'B05_TREE_R1_N128/single_first.json.gz; not repeated under another label',
      'scope':'Four cadence arms preserve352dose; four noise arms addonepulse of0/2/32 or spatialsham to176baseline. Amplitude is not total rate; zero-payload physical pulse is not absence.'})
    rows=[]
    for case in CASES:
        life='FI01_B06_R1_'+case['label']
        if s.life_dir(life).exists():raise FileExistsError(life)
        s.fork('MU_MAIN',life,kind='B06_CADENCE_NOISE_PAIRED_DIAGNOSTIC',checkpoint=CUT);gc.collect();memory_guard()
        p=s.mutate(life,'B06_COMMON_P0_FRONTEND',lambda a:prepare_frontend(a,ni),{'revision':sha(__file__)})
        dump(out/(case['label']+'_PREP.json.gz'),p);del p;gc.collect()
        x=s.mutate(life,'B06_FROZEN_CADENCE_OR_NOISE',lambda a:execute(a,case,ni,sel,out),{'revision':sha(__file__),'case':case})
        dump(out/(case['label']+'.json.gz'),x);r=x['result']
        counts={k:0 for k in('applied','rejected','pending','other')}
        for z in r['requests']:
            st=z['receipt']['status'];counts['applied'if st=='applied'else'rejected'if st.startswith('rejected')else'pending'if st in('queued','pending')else'other']+=1
        row={'case':case['label'],'life':life,'choices':[z['choice']for z in r['readers']],
          'requested':len(r['requests']),**counts,'old_six':[z['reader']['formed_native_command']for z in r['old_six_panel']['rows']],
          'passive_occupied':r['passive_common_horizon']['occupied'],'end_tick':x['physical']['tick'],
          'snapshot_sha256':x['INSTRUMENTO']['snapshot_sha256'],'primary_sha256':sha(out/(case['label']+'.json.gz'))}
        rows.append(row);print(json.dumps(row),flush=True);del x;gc.collect();memory_guard()
    integrity={'immutable_cut_unchanged':sha(SYSTEM/CUT)==EXPECTED,'active_unchanged':sha(SYSTEM/'estado/ACTIVO.json')==active}
    dump(out/'RESUMEN.json',{'rows':rows,'integrity':integrity,'finished_utc':now(),'peak_process_bytes':memory_guard()})
    if not all(integrity.values()):raise AssertionError('Protected source changed')
if __name__=='__main__':main()
