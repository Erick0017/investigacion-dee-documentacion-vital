"""Frozen 2history x common-input/omission pilot from full saved T520.

No center, clock, support or occupied-cell edit. Inputs use the same existing
channel and real Runtime admission. Effective pre-kernel gates are reconstructed
externally after the receipt, not secretly sampled or fed back into the world.
"""
from datetime import datetime,timezone
import hashlib,json,math,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.auditor.passive import digest,record,receipt,operation_state,neighborhood

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')

def gate(w,site):
    import dee_thinking as d
    g=d.inspect_write_gate(w.runtime,d.Coordinate(*site),False)
    keys=('local_clock','center_available','n_active','hadron','rule_value','survives_material_rule',
          'semantic_protected','write_protected','k','period','phase_remainder','ordinary_increment_condition','branch','demux_status')
    return {k:getattr(g,k) for k in keys}

def sample(w,spec):
    import dee_thinking as d
    memories={}
    for name,ports in spec.items():
        observed={key:record(w.runtime.observe(d.Coordinate(*site))) for key,site in ports.items()}
        a,b=observed['A'],observed['B']
        memories[name]={'delta':a['s_reg']-b['s_reg'] if a['active'] and b['active'] else None,
                       'physical':observed,'gates':{key:gate(w,ports[key]) for key in ('A','B')}}
    return {'tick':w.runtime.current_tick,'memories':memories,
        'context1':{key:neighborhood(w,spec['1'][key]) for key in ('A','B')}}

def reconstructed_effective_gate(pre,applied,site):
    # This dictionary is an external analysis overlay, NOT a Runtime mutation.
    context=pre['context1']['B'];g=dict(pre['memories']['1']['gates']['B']);center=context['center']
    records=[dict(x) for x in context['moore26'].values()]
    if applied:
        source=next(x for x in records if x['site']==site)
        assert source['raw']==0
        source.update(state=5001,semantic=1,s_reg=3,direction=[0,1,0],active=True,raw_present=True)
    n=sum(x['active'] for x in records);sums=[sum(x['direction'][i] for x in records if x['active']) for i in range(3)]
    # Existing tetra support remains present; input admission can only add a
    # record. No removal occurs in this reconstructed boundary stage.
    hadron=g['hadron'];tension=16.0 if hadron and n<7 else 2.5
    rule=math.floor(n*tension/26.0+.5);protected=n>=7 and sums==[0,0,0]
    k=8-n;period=782//k if 0<k<=8 else None
    remainder=center['clock']%period if period is not None else None
    possible=center['state']>0 and center['semantic']!=4 and rule!=0 and not protected and period is not None and remainder==0
    return {'stage':'RECONSTRUCTED_AFTER_NATIVE_ADMISSION_BEFORE_F_V27_NOT_DIRECT_PASSIVE_SAMPLE',
        'receipt_applied':applied,'clock_preserved':center['clock'],'n_active':n,'hadron':hadron,
        'direction_sum':sums,'rule_value':rule,'write_protected':protected,'k':k,'period':period,
        'phase_remainder':remainder,'ordinary_increment_condition':possible,
        'basis':'Receipt status plus exact previous Moore26 and fixed ChannelSpec. Runtime.cpp preserves clock and writes RAW only after checking empty target. This observer never injects the reconstruction.',
        'limits':'Complete survival/ordinary-increment conditions reconstructed for this supported material state; DEMUX remains separately unresolved and actual post-state is retained.'}

def main():
    import dee_thinking as d
    out=ROOT/'resultados/auditor/SUSCEPTIBILITY_PILOT'
    out.mkdir(parents=True,exist_ok=False)
    sources={h:ROOT/'resultados/regulacion/DUAL_CONFIRMATION'/h/'T520.deetsnap' for h in ('AB_AB','BA_AB')}
    config={'id':'CPC4_A02.HISTORY_COMMON_E_B522.v1','freeze_utc':datetime.now(timezone.utc).isoformat(),
        'mode':'EXPERIENCE_PROTOCOL_ON_EXPLICIT_FULL_OPERATIVE_FORKS_NO_RAW_EDITS',
        'sources':{h:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for h,p in sources.items()},
        'histories':['AB_AB','BA_AB'],'arms':['COMMON_E_B522','OMITTED_E'],
        'channel':'m1.B','load':3,'requested_tick':522,'start_tick':520,'horizon':525,
        'observations':'A/B separately,delta,comparator,clock,26neighbors,pre-input gates,receipts and reconstructed post-admission gate',
        'manual_RAW_or_clock_edits':0,'cases':4,
        'purpose':'Finite history x same physical experience interaction; NOT autonomous learned policy. No parameter search or retry if rejected.',
        'followup_rule':'An off-path sham is eligible only after these four runs show a relational or expression effect. No sham included until that condition is observed.'}
    put(out/'EXPERIMENT_CONFIG.json',config);started=time.monotonic();rows=[]
    for history,path in sources.items():
        parent=d.OrganizationalWorld.load_snapshot(str(path));parent_state=operation_state(parent)
        reference=json.loads((path.parent/'MEASUREMENTS.json').read_text(encoding='utf-8'));spec=reference['spec']
        event_spec=next(i.channel for i in parent.interfaces if i.name=='m1.B')
        event_site=[event_spec.injection_site.x,event_spec.injection_site.y,event_spec.injection_site.z]
        assert [event_spec.direction.dx,event_spec.direction.dy,event_spec.direction.dz]==[0,1,0]
        assert event_spec.state==5001 and event_spec.semantic==1
        for arm in config['arms']:
            w=parent.fork();assert operation_state(w)==parent_state
            folder=out/(history+'__'+arm);folder.mkdir()
            before_submit=digest(w);event=None;calls=[]
            if arm=='COMMON_E_B522':
                event=w.submit('m1.B',3,522)
                calls.append({'operation':'submit','call_tick':520,'channel':'m1.B','load':3,'requested_tick':522,'receipt_id':event.id})
            assert digest(w)==before_submit
            trace=[];reconstruction=None;transition=None
            for tick in range(520,526):
                pre=sample(w,spec);trace.append(pre)
                if tick in (522,523,525):w.save_snapshot(str(folder/f'T{tick}.deetsnap'))
                if tick==525:break
                w.advance();calls.append({'operation':'advance','before_tick':tick,'actual_after_tick':w.runtime.current_tick})
                if tick==522:
                    r=w.runtime.receipt(event.id) if event is not None else None
                    applied=r is not None and 'applied'==str(r.status).lower()
                    reconstruction=reconstructed_effective_gate(pre,applied,event_site)
                    post=sample(w,spec)
                    transition={'before':pre,'after':post,'actual_receipt':None if r is None else receipt(r),
                         'effective_gate_external_reconstruction':reconstruction,
                         'change_A':post['memories']['1']['physical']['A']['s_reg']-pre['memories']['1']['physical']['A']['s_reg'],
                         'change_B':post['memories']['1']['physical']['B']['s_reg']-pre['memories']['1']['physical']['B']['s_reg']}
            assert operation_state(parent)==parent_state and sha(path)==config['sources'][history]['sha256']
            result={'id':folder.name,'history':history,'arm':arm,'source':config['sources'][history],
                'initial_fork_equal':True,'parent_unchanged':True,'manual_RAW_or_clock_edits':0,
                'event_site':event_site,'calls':calls,'receipt':None if event is None else receipt(w.runtime.receipt(event.id)),
                'trace':trace,'transition522_523':transition,'final':sample(w,spec),'digest':digest(w),
                'mode':config['mode'],'scope':config['purpose']}
            put(folder/'MEASUREMENTS.json',result);rows.append(result)
    contrasts=[]
    for history in config['histories']:
        full=next(r for r in rows if r['history']==history and r['arm']=='COMMON_E_B522')
        omitted=next(r for r in rows if r['history']==history and r['arm']=='OMITTED_E')
        def expression(r):return [(x['tick'],x['memories']['1']['physical']['comparator']['s_reg'],x['memories']['1']['physical']['comparator']['direction']) for x in r['trace']]
        contrasts.append({'history':history,'admission':full['receipt'],'final_deltas':[full['final']['memories']['1']['delta'],omitted['final']['memories']['1']['delta']],
            'final_A_B_loads':[[r['final']['memories']['1']['physical'][k]['s_reg'] for k in ('A','B')] for r in (full,omitted)],
            'expression_trace_differs':expression(full)!=expression(omitted),
            'relational_trace_differs':[x['memories']['1']['delta'] for x in full['trace']]!=[x['memories']['1']['delta'] for x in omitted['trace']],
            'transition522_523':{'full':full['transition522_523'],'omitted':omitted['transition522_523']}})
    summary={'config_sha256':sha(out/'EXPERIMENT_CONFIG.json'),'trajectories':4,'fresh_preparations':0,
       'full_operative_continuation_forks':4,'native_ticks_per_fork':5,'manual_RAW_clock_edits':0,
       'contrasts':contrasts,'sham_followup_eligible':any(x['relational_trace_differs'] or x['expression_trace_differs'] for x in contrasts),
       'elapsed_seconds':time.monotonic()-started,'source_code_sha256':sha(__file__),
       'scope':config['purpose'],'closed_reason':'Four frozen trajectories completed; no blind search or replay retry.'}
    put(out/'RUN_SUMMARY.json',summary);print(json.dumps({'trajectories':4,'sham_eligible':summary['sham_followup_eligible'],
       'result':[(x['history'],x['admission']['status'],x['final_deltas']) for x in contrasts]}))

if __name__=='__main__':main()
