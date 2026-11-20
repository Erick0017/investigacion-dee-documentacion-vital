"""Directed, supervised prior-mechanism replays; no historical campaign main.

The frozen modules under referencias/ are apparatus, never a response table.
Historical measurements are read only AFTER the new trajectory is complete.
"""
from array import array
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.supervisor import put, sha, run

WHL_SHA = '17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'
PYD_SHA = '20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066'
KERNEL_SHA = 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'


def exact(value):
    if isinstance(value, dict):
        return {k: (str(v) if k in ('raw', 'clock', 'local_clock') and isinstance(v, int) else exact(v)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [exact(v) for v in value]
    return value


def digest(world):
    r = world.runtime
    return {'tick': r.current_tick, 'N': r.dimension,
            'RAW_sha256': hashlib.sha256(array('Q', r.raw_copy()).tobytes()).hexdigest(),
            'clock_sha256': hashlib.sha256(array('Q', r.clock_copy()).tobytes()).hexdigest()}


def operative(world):
    r = world.runtime
    return {'channels': list(r.channel_names), 'metadata': dict(r.snapshot_metadata_entries),
            'paused': r.paused, 'protocol_phase': r.protocol_phase,
            'receipts': [{'id': x.id, 'kind': str(x.kind), 'status': str(x.status),
                          'requested_tick': x.requested_tick, 'effective_tick': x.effective_tick,
                          'channels': list(x.channels), 'reason': x.reason} for x in r.receipts],
            'external_operations': list(world.external_operations)}


def identity():
    import dee_thinking as d
    wheel = ROOT / 'runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
    if not wheel.exists():
        raise FileNotFoundError('Campaign wheel is not yet installed/copied')
    assert sha(wheel) == WHL_SHA
    assert d.__version__ == '4.0.0' and d.kernel_identity()['kernel_version'] == 27
    assert sha(d._native.__file__) == PYD_SHA
    assert 'site-packages' in str(d.__file__) and Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    assert sha(ROOT / 'referencias/producto4/kernel_v27.cpp') == KERNEL_SHA
    with zipfile.ZipFile(wheel) as z:
        assert z.testzip() is None
        for name in z.namelist():
            if name.startswith('dee_thinking/') and not name.endswith('/'):
                assert (Path(d.__file__).parent / Path(name).relative_to('dee_thinking')).read_bytes() == z.read(name)
    return {'python': sys.executable, 'version': d.__version__, 'kernel': d.kernel_identity(),
            'module': d.__file__, 'wheel_sha256': WHL_SHA, 'native_sha256': PYD_SHA,
            'kernel_source_sha256': KERNEL_SHA, 'installed_payload_matches_whl': True}


def observe(world, site):
    from referencias.cpc4_red.common_helpers import observe as obs
    return obs(world, site)


def local_context(world, site):
    n = world.runtime.dimension
    return {','.join(map(str, (x, y, z))): observe(world, tuple((site[i]+v) % n for i, v in enumerate((x,y,z))))
            for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1)}


def relative_prepare(case):
    """Exact effective dual_sustained.prepare recipe, with imports localized.

    Frozen source is preserved byte-exact in referencias/cpc4_relative.
    """
    import dee_thinking as d
    from referencias.cpc4_red.common_helpers import interface
    n=47; shift=case.get('translation',[0,0,0]); centers=[(14,14,14),(32,32,32)]
    pa=((-1,0,0),(-1,1,1),(0,0,1),(0,1,0))
    pb=((0,-1,0),(0,0,-1),(1,-1,-1),(1,0,0))
    placements=[]; interfaces=[]; spec={}; occupied=set()
    def moved(q,v): return tuple((q[i]+v[i])%n for i in range(3))
    def place(q,state,load,dr=(0,0,0),sem=4,clock=0,role='support'):
        if q in occupied: raise ValueError('Initial overlap')
        occupied.add(q); p=d.InitialPlacement(); p.site=d.Coordinate(*q)
        p.raw=d.pack_record(state,load,*dr,sem); p.clock=clock; p.role=role; placements.append(p)
    for j,center in enumerate(centers,1):
        c=moved(center,shift); a=moved(c,(-1,0,0)); b=moved(c,(1,0,0)); phase=260 if j==1 else case.get('second_phase',0)
        place(a,1000,100,sem=1,clock=phase,role=f'memory{j}.A'); place(b,2000,100,sem=1,clock=phase,role=f'memory{j}.B')
        for q,pat,s,clock in ((a,pa,3000,31),(b,pb,4000,41)):
            for i,v in enumerate(pat): place(moved(q,v),s+i,0,clock=clock+i)
        if j==1 and case.get('reader1','persistent')!='absent':
            place(moved(c,(0,-2,0)),6000,7,(0,1,0),4 if case.get('reader1','persistent')=='persistent' else 1,23,'reader1')
        for name,q,offset,dr,state in (('A',a,(0,-1,0),(0,-1,0),5000),('B',b,(0,1,0),(0,1,0),5001)):
            interfaces.append(interface(f'm{j}.{name}',moved(q,offset),dr,state=state))
        interfaces.append(interface(f'm{j}.read',moved(c,(0,-1,0)),(0,1,0)))
        spec[str(j)]={'A':a,'B':b,'comparator':c,'reader':moved(c,(0,-1,0)),'source':moved(c,(0,-2,0))}
    recipe=d.OrganizationRecipe.research(n,placements,0); recipe.interfaces=interfaces
    recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    return d.OrganizationalWorld.create(recipe),spec


def relative_sample(w,spec):
    out={}
    for name,ports in spec.items():
        r={k:observe(w,q) for k,q in ports.items()}; a,b=r['A'],r['B']
        out[name]={'delta':a['s_reg']-b['s_reg'] if a['active'] and b['active'] else None,'physical':r}
    return {'tick':w.runtime.current_tick,'memories':out}


def run_relative(case,out):
    import dee_thinking as d
    w,spec=relative_prepare(case); calls=[]
    for j,key,start in ((1,'history1',0),(2,'history2',260)):
        h=case.get(key,'AB')
        for i,label in enumerate(h if h in ('AB','BA') else ''):
            r=w.submit(f'm{j}.{label}',3,start+i)
            calls.append({'operation':'submit','channel':f'm{j}.{label}','load':3,'tick':start+i,'id':r.id,'call_tick':0})
    for tick in (262,400):
        r=w.probe('m2.read',7,tick); calls.append({'operation':'probe','channel':'m2.read','load':7,'tick':tick,'id':r.id,'call_tick':0})
    points=(0,1,2,259,260,261,262,265,399,400,403,520)
    rows=[]; contexts={}; persistence={}
    for t in points:
        w.run_until(t); rows.append(relative_sample(w,spec))
        if t in (0,259,262,520):
            w.save_snapshot(str(out/f'T{t}.deetsnap'))
        if t in (0,259,260,261,262):
            contexts[str(t)]={k:{a:local_context(w,q[a]) for a in ('A','B')} for k,q in spec.items()}
        if t==399:
            saved=out/'PERSISTENCE399.deetsnap'; w.save_snapshot(str(saved))
            restored=d.OrganizationalWorld.load_snapshot(str(saved))
            persistence['saved_physical_equal']=digest(restored)==digest(w)
            persistence['saved_operational_equal']=operative(restored)==operative(w)
            restored.run_until(403)
        if t==403:
            persistence['continued_physical_equal']=digest(restored)==digest(w)
            persistence['continued_operational_equal']=operative(restored)==operative(w)
    return {'case':case,'initial_preparation':spec,'actual_calls':calls,'rows':rows,'contexts':contexts,
            'final':relative_sample(w,spec),'physical':digest(w),'operative':operative(w),'persistence':persistence,
            'source_recipe':'referencias/cpc4_relative/dual_sustained.py:prepare',
            'classification':'DIRECTED_PRIOR_MECHANISM_REPRODUCTION_NOT_NEW_CPC5_ACQUISITION'}


def run_network(case,out):
    import dee_thinking as d
    from referencias.cpc4_red.regulated_session import NetworkSession
    from referencias.cpc4_red import recipe_v3 as r
    case=dict(case); tr=tuple(case.pop('translation',(0,0,0))); intervention=case.pop('D228_intervention',None)
    s=NetworkSession.create(case,tr); rows=[]; contexts={}; captures={name:{} for name in s.spec['banks']}; edits=[]
    ticks=(0,3,13,15,27,70,80,81,82,85,86,93,94,160,161,227,228,290,291,292,293,294,349,350,416,417,421,424,425,427,430,431,437)
    for t in ticks:
        rows.append(s.run_until(t))
        if t==228 and intervention:
            site=s.spec['centers']['D']; before=observe(s.world,site)
            if not (before['active'] and before['s_reg']==84): raise ValueError('Observed D product outside frozen control contract')
            original=digest(s.world); original_raw=s.world.runtime.raw_copy(); original_clocks=s.world.runtime.clock_copy()
            edit=d.ResearchStateEdit(); edit.coordinate=d.Coordinate(*site)
            edit.raw=0 if intervention=='REMOVE' else before['raw']; edit.label='DIRECTED_PRIOR_REFERENCE_D228_'+intervention
            s.world.save_snapshot(str(out/'BEFORE_D228_DIAGNOSTIC.deetsnap'))
            child=s.world.diagnostic_fork([edit],True)
            changed=[i for i,(a,b) in enumerate(zip(original_raw,child.runtime.raw_copy())) if a!=b]
            assert len(changed)==(1 if intervention=='REMOVE' else 0)
            assert child.runtime.clock_copy()==original_clocks and digest(s.world)==original
            edits.append({'at_tick':228,'intervention':intervention,'before':before,'after':observe(child,site),
                          'RAW_sites_changed':len(changed),'clock_sites_changed':0,'parent_unchanged':True})
            s.world=child; s._commit(); s.save(out/'AFTER_D228_DIAGNOSTIC.deetsnap')
        if t in (81,82,93,94,292,293,294,349,350):
            point=s.spec['regulation']['meeting'] if t in (292,293,294) else s.spec['centers']['D' if t in (93,94) else 'B']
            contexts[str(t)]=local_context(s.world,point)
        for name,bank in s.spec['banks'].items():
            if t==bank['resource_read']: captures[name]['R']=r.observe(s.world,bank['resource_receiver'])
            if t==bank['function_read']: captures[name]['F']=r.observe(s.world,bank['function_receiver'])
        if t in (0,94,228,292,293,294,350,417,437): s.save(out/f'T{t}.deetsnap')
    profiles={}
    for name,cap in captures.items():
        bank=s.spec['banks'][name]
        R=int(cap['R']['active'] and cap['R']['s_reg']==3 and cap['R']['direction']==list(bank['resource_direction']))
        F=int(cap['F']['active'] and cap['F']['s_reg']==7 and cap['F']['direction']==list(bank['supply_direction']))
        profiles[name]=[F,R]
    return {'case':case,'translation':tr,'recipe':s.spec,'trace':rows,'contexts':contexts,'captures':captures,
            'profiles':profiles,'external_utility':sum(2*v[0]+v[1] for v in profiles.values()),
            'physical':digest(s.world),'operative':operative(s.world),'actual_input_calls':s.state['protocol'],'diagnostic_edits':edits,
            'classification':'DIRECTED_PRIOR_MECHANISM_REPRODUCTION_NOT_NEW_CPC5_COMMUNICATION',
            'regulation_modality':'FIXED_EXTERNAL_COUNTERFLOW_INPUT_NATIVE_RESOLUTION_NOT_LEARNED_REGULATION'}


def run_sem01(case,out):
    from referencias.sem01.experiment import run_case
    value=run_case(case,out)
    value['classification']='DIRECTED_PRIOR_MECHANISM_REPRODUCTION_NOT_NEW_CPC5_SEMANTICS'
    return value


def config():
    cases=[
        {'id':'SEM01_A_future_UV','family':'SEM01','case':{'id':'A_future_UV','pairing':{'S1':'U','S2':'V'},'future_events':{'S1':'U','S2':'V'},'mode':'paired'}},
        {'id':'SEM01_B_future_VU','family':'SEM01','case':{'id':'B_future_VU','pairing':{'S1':'V','S2':'U'},'future_events':{'S1':'V','S2':'U'},'mode':'paired'}},
        {'id':'SEM01_unpaired_UV','family':'SEM01','case':{'id':'unpaired_UV','pairing':{'S1':'U','S2':'V'},'future_events':{'S1':'U','S2':'V'},'mode':'unpaired'}},
        {'id':'ABCD_FILTER_FLAT','family':'ABCD','case':{'id':'FILTER_FLAT','roles':True,'A_history':1,'B_history':1,'C_history':1,'D_history':1,'neutralizer':'counterflow'}},
        {'id':'ABCD_NO_FILTER_FLAT','family':'ABCD','case':{'id':'NO_FILTER_FLAT','roles':True,'A_history':1,'B_history':1,'C_history':1,'D_history':1,'neutralizer':'none'}},
        {'id':'ABCD_SHAM_ZERO_FLAT','family':'ABCD','case':{'id':'SHAM_ZERO_FLAT','roles':True,'A_history':1,'B_history':1,'C_history':1,'D_history':1,'neutralizer':'sham'}},
        {'id':'RELATIVE_AB_BA','family':'RELATIVE','case':{'id':'AB_BA','history1':'AB','history2':'BA','second_phase':0,'reader1':'persistent','horizon':520,'translation':[0,0,0]}},
        {'id':'RELATIVE_AB_H0','family':'RELATIVE','case':{'id':'AB_H0','history1':'AB','history2':'H0','second_phase':0,'reader1':'persistent','horizon':520,'translation':[0,0,0]}},
    ]
    return {'frozen_utc':datetime.now(timezone.utc).isoformat(),'cases':cases,
            'selection':'Eight directed old references only; no110-case historical rerun. References count separately from new preparations.',
            'raw_clock_JSON_encoding':'decimal strings; physical snapshot uint64',
            'source_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'referencias').rglob('*.py')}}


def compare_history():
    """Auditor-only comparisons after trajectories; never imported by a world."""
    import shutil
    thinking=ROOT.parents[2]
    practical=thinking/'casos practicos'
    old=practical/'trabajo_codex/CPC4'
    ext=old/'ampliaciones/02_APRENDIZAJE_CONTINUO_RED_ABCD'
    sem=practical/'trabajo_codex/CPC3_SEM01_SIGNIFICADO_ADQUIRIDO'
    folder=ROOT/'resultados/references'
    sources=[]
    for family,source,names in (
        ('cpc4_red',ext/'src/red',('common_helpers.py','recipe_v3.py','dual_session.py','regulated_session.py')),
        ('cpc4_relative',ext/'src',('dual_sustained.py','sustained_regulation.py')),
        ('sem01',sem/'src',('common.py','memory.py','habitat.py','participant.py','experiment.py'))):
        for name in names:
            original=source/name; copied=ROOT/'referencias'/family/name
            sources.append({'source':original.relative_to(thinking).as_posix(),'copy':copied.relative_to(ROOT).as_posix(),
                            'sha256':sha(original),'copy_byte_exact':original.read_bytes()==copied.read_bytes()})
    expected_parents={'CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip':'4a14a81f913a434a8e54e47c0c700d7ee54418bb16913aedded8bf49a3294723',
                      'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip':'1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6'}
    parents=[]
    for name,expected in expected_parents.items():
        p=practical/name; actual=sha(p)
        parents.append({'path':p.relative_to(thinking).as_posix(),'bytes':p.stat().st_size,'sha256':actual,'expected_sha256':expected,'equal':actual==expected})
        assert actual==expected,(name,actual)
    product=thinking/'4.0/DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip'
    with zipfile.ZipFile(product) as z:
        product_members=[]
        for member,target in (
            ('DEE_thinking_4_0_0/source/src/kernel_v27.cpp','kernel_v27.cpp'),
            ('DEE_thinking_4_0_0/PRODUCT_CONTRACT.json','PRODUCT_CONTRACT.json'),
            ('DEE_thinking_4_0_0/source/include/dee_thinking/organizational.hpp','organizational.hpp'),
            ('DEE_thinking_4_0_0/docs/API_AND_SCOPE.md','API_AND_SCOPE.md')):
            data=z.read(member); dst=ROOT/'referencias/producto4'/target
            if not dst.exists(): dst.write_bytes(data)
            assert dst.read_bytes()==data,(member,'copy differs')
            product_members.append({'member':member,'sha256':hashlib.sha256(data).hexdigest(),'copy':dst.relative_to(ROOT).as_posix(),'copy_byte_exact':True})
    configs=json.loads((folder/'EXPERIMENT_CONFIG.json').read_text(encoding='utf-8'))
    comparisons=[]
    for item in configs['cases']:
        actual_path=folder/item['id']/'MEASUREMENTS.json'
        if not actual_path.exists(): continue
        value=json.loads(actual_path.read_text(encoding='utf-8'))
        if item['family']=='SEM01':
            original=sem/'resultados/confirmacion'/item['case']['id']/'MEASUREMENTS.json'
        elif item['family']=='ABCD':
            original=ext/'resultados/red/fixed_counterflow01'/item['case']['id']/'MEASUREMENTS.json'
        else:
            original=ext/'resultados/regulacion/DUAL_CONFIRMATION'/item['case']['id']/'MEASUREMENTS.json'
        dst=ROOT/'referencias/historical_measurements'/f"{item['id']}.json"
        dst.parent.mkdir(parents=True,exist_ok=True)
        if not dst.exists(): shutil.copyfile(original,dst)
        assert sha(original)==sha(dst)
        historical=json.loads(dst.read_text(encoding='utf-8'))
        if item['family']=='SEM01':
            new,prior=value['final'],historical['final']
            equal=new==prior
            functional=[{'signal':v['signal'],'readout':v['anticipation']['emission']['anticipated_class'],
                         'physical':v['anticipation']['emission']['physical'],
                         'consequence':v['evaluation'],'receipts':v['actual_receipts']} for v in value['uses']]
        elif item['family']=='ABCD':
            new,prior=value['physical'],historical['world']
            equal=(new['tick']==prior['tick'] and new['RAW_sha256']==prior['RAW_sha256'] and new['clock_sha256']==prior['clock_sha256'])
            functional={'profiles':value['profiles'],'external_utility':value['external_utility'],'historical_utility':historical['external_utility']}
        else:
            new,prior=value['physical'],historical['digest']
            equal=(new['tick']==prior['tick'] and new['RAW_sha256']==prior['RAW'] and new['clock_sha256']==prior['clocks'])
            functional={'final_deltas':{k:v['delta'] for k,v in value['final']['memories'].items()},'persistence':value['persistence']}
        comparisons.append({'id':item['id'],'original':original.relative_to(thinking).as_posix(),'historical_copy':dst.relative_to(ROOT).as_posix(),
                            'historical_sha256':sha(dst),'new_measurements':actual_path.relative_to(ROOT).as_posix(),'new_sha256':sha(actual_path),
                            'complete_RAW_clock_tick_equal':equal,'new_physical':new,'historical_physical':prior,'functional':functional})
    put(folder/'HISTORICAL_COMPARISON.json',exact({'comparisons':comparisons,'count':len(comparisons),
         'historical_data_read_after_new_trajectory':True,'source_code_reproduction_byte_exact':sources,
         'parents':parents,'product_members':product_members,'product_zip_sha256':sha(product),
         'reference_scope':'Reproductions are not additional independent scientific discoveries. Eight initial identity errors occurred before physics because the campaignwheel was not yet copied; logs retained. One coordination correction copied the exactwheel and gated later failures.'}))
    print(json.dumps({'comparisons':len(comparisons),'complete_state_equal':[x['complete_RAW_clock_tick_equal'] for x in comparisons]}))


def d_controls():
    path=ROOT/'resultados/references/D_ROUTE_CONTROLS_CONFIG.json'
    if not path.exists():
        cases=[{'id':'ABCD_D228_'+operation,'family':'ABCD','case':{'id':'FILTER_N','roles':True,'A_history':1,'B_history':1,
                'C_history':-1,'D_history':1,'neutralizer':'counterflow','D228_intervention':operation}} for operation in ('REMOVE','SHAM')]
        put(path,{'frozen_utc':datetime.now(timezone.utc).isoformat(),'cases':cases,
            'reason':'Directed selective contrast of formed D84 product in the original C-minus context; additional reference diagnostics, not a new architecture.',
            'REMOVE':'RAW zero at observed D84 site228; retain clock and all other sites',
            'SHAM':'Complete same fork operation with RAW restored identically; no physical field changed',
            'parent_REFERENCE':'historical fixed_counterflow01/FILTER_N, expected files unavailable to participant'})
    cfg=json.loads(path.read_text(encoding='utf-8'))
    for item in cfg['cases']:
        if (ROOT/'resultados/references'/item['id']/'MEASUREMENTS.json').exists(): continue
        job=run('ref_'+item['id'],[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--case',item['id']],300)
        if job['exit_code']: break


def reconcile_persistence():
    import dee_thinking as d
    rows=[]
    for name in ('RELATIVE_AB_BA','RELATIVE_AB_H0'):
        folder=ROOT/'resultados/references'/name
        previous=json.loads((folder/'MEASUREMENTS.json').read_text(encoding='utf-8'))
        restored=d.OrganizationalWorld.load_snapshot(str(folder/'PERSISTENCE399.deetsnap'))
        before=digest(restored); receipts399=operative(restored)['receipts']
        restored.run_until(520); after=operative(restored); original=previous['operative']
        raw_differences=[k for k in after if after[k]!=original[k]]
        assert raw_differences==['metadata']
        added=set(after['metadata'])-set(original['metadata'])
        assert added and all(k.startswith('dee_thinking.organizational.v1.') for k in added)
        strip=lambda x:{**x,'metadata':{k:v for k,v in x['metadata'].items() if not k.startswith('dee_thinking.organizational.v1.')}}
        final=digest(restored)
        rows.append({'case':name,'snapshot':(folder/'PERSISTENCE399.deetsnap').relative_to(ROOT).as_posix(),
             'snapshot_sha256':sha(folder/'PERSISTENCE399.deetsnap'),'before':before,'after':final,
             'RAW_clock_tick_future_equal':final==previous['physical'],
             'operative_raw_comparison_false_retained':previous['persistence'],
             'different_top_level_fields':raw_differences,'added_internal_serialization_envelope_keys':sorted(added),
             'external_metadata_receipts_channels_protocol_phase_external_operations_equal':strip(after)==strip(original),
             'receipts_at399':receipts399,'receipts_at520':after['receipts'],
             'scope':'The loadedWorld exposes its organizational serialized envelope in Runtime metadata. Unsaved liveWorld has no such envelope. This is distinct from physics and usable operational-state loss; no field was edited or repaired.'})
    put(ROOT/'resultados/references/PERSISTENCE_RECONCILIATION.json',rows)
    print(json.dumps({'rows':len(rows),'physical':[x['RAW_clock_tick_future_equal'] for x in rows],
          'operative_without_serialization_envelope':[x['external_metadata_receipts_channels_protocol_phase_external_operations_equal'] for x in rows]}))


def finalize():
    folder=ROOT/'resultados/references'; values=[]
    for path in sorted(folder.glob('*/MEASUREMENTS.json')):
        d=json.loads(path.read_text(encoding='utf-8')); name=path.parent.name
        values.append({'case_id':name,'evidence':path.relative_to(ROOT).as_posix(),'sha256':sha(path),
                       'elapsed_seconds':d['elapsed_seconds'],
                       'type':'DIAGNOSTIC_FORK_REFERENCE' if name.startswith('ABCD_D228_') else 'PRIOR_MECHANISM_REPRODUCTION',
                       'modality':'EXPERIENCE_PROTOCOL+NATIVE_EVOLUTION+PASSIVE_OBSERVATION',
                       'horizon':d.get('physical',d.get('final')),
                       'summary':({'utility':d['external_utility'],'profiles':d['profiles'],'edits':d.get('diagnostic_edits',[])} if 'external_utility' in d
                                  else {'readouts':[x['anticipation']['emission']['anticipated_class'] for x in d['uses']],
                                        'utilities':[x['evaluation']['external_utility_for_this_task'] for x in d['uses']]} if 'uses' in d
                                  else {'final_deltas':{k:v['delta'] for k,v in d['final']['memories'].items()},
                                        'receipts':d['operative']['receipts']})})
    historical=json.loads((folder/'HISTORICAL_COMPARISON.json').read_text(encoding='utf-8'))
    reconcile=json.loads((folder/'PERSISTENCE_RECONCILIATION.json').read_text(encoding='utf-8'))
    # An independent same-RAW sham is expected to have the native FILTER_N future.
    thinking=ROOT.parents[2]
    source=thinking/'casos practicos/trabajo_codex/CPC4/ampliaciones/02_APRENDIZAJE_CONTINUO_RED_ABCD/resultados/red/fixed_counterflow01/FILTER_N/MEASUREMENTS.json'
    prior=json.loads(source.read_text(encoding='utf-8'))
    cut=json.loads((folder/'ABCD_D228_REMOVE/MEASUREMENTS.json').read_text(encoding='utf-8'))
    sham=json.loads((folder/'ABCD_D228_SHAM/MEASUREMENTS.json').read_text(encoding='utf-8'))
    equal=(sham['physical']['RAW_sha256']==prior['world']['RAW_sha256'] and sham['physical']['clock_sha256']==prior['world']['clock_sha256'] and sham['physical']['tick']==prior['world']['tick'])
    coverage={
        'references':values,'counts':{'prior_reproductions':8,'diagnostic_trajectories':2,'technical_restore_continuations':4,
        'identity_attempts_before_physics':8,'new_CPC5_architecture_cases':0},
        'historical_physics_equal':all(x['complete_RAW_clock_tick_equal'] for x in historical['comparisons']),
        'D228_control':{'cut_utility':cut['external_utility'],'sham_utility':sham['external_utility'],
             'sham_final_RAW_clock_tick_equals_historical_FILTER_N':equal,'historical_evidence':source.relative_to(thinking).as_posix(),
             'historical_evidence_sha256':sha(source),'actual_cut_fields':cut['diagnostic_edits'],
             'scope':'A formed social product is required for the useful N-bank difference in this finite apparatus. Counterflow changes residual context; it is not a learned attention policy.'},
        'persistence_reconciliation':reconcile,
        'important_adverse_reference':'Second relative memory read400 is rejected_occupied although both memory loads,delta and existing comparator expression remain. Do not call this forgetting or fresh admitted query.',
        'coverage_map':[
          {'antecedent':'SEM01 signal/consequence, anticipation','status':'REPRODUCED','cases':['SEM01_A_future_UV','SEM01_B_future_VU','SEM01_unpaired_UV']},
          {'antecedent':'ABCD acquired products and D->B','status':'REPRODUCED_WITH_SELECTIVE_DIAGNOSTIC','cases':['ABCD_FILTER_FLAT','ABCD_D228_REMOVE','ABCD_D228_SHAM']},
          {'antecedent':'Fixed native counterflow','status':'REPRODUCED','cases':['ABCD_FILTER_FLAT','ABCD_NO_FILTER_FLAT','ABCD_SHAM_ZERO_FLAT']},
          {'antecedent':'Relative memory1 retained while acquiring memory2','status':'REPRODUCED','cases':['RELATIVE_AB_BA','RELATIVE_AB_H0']},
          {'antecedent':'Runtime persistent physical and pending operational future','status':'REPRODUCED_WITH_METADATA_ENVELOPE_RECONCILIATION','cases':['RELATIVE_AB_BA','RELATIVE_AB_H0']},
          {'antecedent':'All110 historical records','status':'NOT_RERUN','reason':'Unnecessary for bounded directed reference coverage'}],
        'NSM_parent_catalog':{'file':'referencias/NSM65_CATALOGO_CPC4.json','sha256':sha(ROOT/'referencias/NSM65_CATALOGO_CPC4.json'),
             'source':'CPC4/NSM65_CATALOGO.json','documentary_only_no_new_meanings_from_copy':True}}
    put(folder/'COVERAGE.json',exact(coverage))
    print(json.dumps({'reference_cases':len(values),'historical_all_equal':coverage['historical_physics_equal'],'D_sham_equal':equal}))


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--case'); parser.add_argument('--output',type=Path); parser.add_argument('--run-all',action='store_true'); parser.add_argument('--compare-history',action='store_true'); parser.add_argument('--d-controls',action='store_true'); parser.add_argument('--reconcile-persistence',action='store_true'); parser.add_argument('--finalize',action='store_true')
    args=parser.parse_args(); folder=ROOT/'resultados/references'; folder.mkdir(parents=True,exist_ok=True)
    if args.compare_history: compare_history(); return
    if args.d_controls: d_controls(); return
    if args.reconcile_persistence: reconcile_persistence(); return
    if args.finalize: finalize(); return
    cfgfile=folder/'EXPERIMENT_CONFIG.json'
    if not cfgfile.exists(): put(cfgfile,config())
    cfg=json.loads(cfgfile.read_text(encoding='utf-8'))
    if args.case:
        cases=list(cfg['cases'])
        dfile=folder/'D_ROUTE_CONTROLS_CONFIG.json'
        if dfile.exists(): cases+=json.loads(dfile.read_text(encoding='utf-8'))['cases']
        item=next(x for x in cases if x['id']==args.case)
        out=args.output.resolve() if args.output else folder/item['id']; out.mkdir(parents=True,exist_ok=True)
        if (out/'MEASUREMENTS.json').exists(): raise FileExistsError('Completed reference must not be overwritten')
        start=time.monotonic(); engine=identity(); put(out/'ENGINE.json',engine)
        value={'SEM01':run_sem01,'ABCD':run_network,'RELATIVE':run_relative}[item['family']](item['case'],out)
        value['elapsed_seconds']=time.monotonic()-start; value['engine']=engine
        value['runner_sha256']=sha(__file__)
        put(out/'MEASUREMENTS.json',exact(value)); print(json.dumps({'id':item['id'],'elapsed_seconds':value['elapsed_seconds']})); return
    if args.run_all:
        jobs=[]
        for item in cfg['cases']:
            if (folder/item['id']/'MEASUREMENTS.json').exists(): continue
            attempt=1
            while (ROOT/'jobs'/('ref_'+item['id']+'_attempt'+str(attempt))).exists(): attempt+=1
            job=run('ref_'+item['id']+'_attempt'+str(attempt),[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--case',item['id']],timeout=300)
            jobs.append(job); put(folder/'JOBS.json',jobs)
            if job['exit_code'] != 0: break
        rows=[]
        for item in cfg['cases']:
            p=folder/item['id']/'MEASUREMENTS.json'
            if p.exists():
                value=json.loads(p.read_text(encoding='utf-8')); rows.append({'id':item['id'],'family':item['family'],'evidence':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'elapsed_seconds':value['elapsed_seconds']})
        put(folder/'RUN_SUMMARY.json',{'references':rows,'count':len(rows),'not_new_CPC5_cases':True})
    else:
        put(folder/'ENGINE.json',identity())


if __name__=='__main__': main()
