"""Three finite extensions, using already measured questions rather than a new frontier."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import dee_thinking as d
from laboratorio import *
from sesion import Session,install_offpath
from causal_lab import compare_panel


def run(root):
    root=Path(root);e=CaseEvidence(root,'INTEGRATIONS',{'freeze_before_run':True,'families':['native online mobile-to-basal bridge','retention vs consumption and shared-history feedback','common-panel diagnostic reuse'],
        'bridge_references':[12,18],'reserved_reference':18,'long_rest':500,'phase_delays':[0,1,2],'causal_reserved_query':11,'not_general_science_campaign':True})
    bridges=[]
    for reference in [12,18]:
        for arm in ['full','no_body_history','mobile_absent','unpaired']:
            w=d.create_organization('mobile_basal',history=d.BasalHistory.H0,body_only=True)
            spec=w.view('body').spec
            for name,site,direction in [('E_A',d.Coordinate(spec.a.x,spec.a.y-1,spec.a.z),(0,0,-1)),('E_B',d.Coordinate(spec.b.x,spec.b.y+1,spec.b.z),(0,0,1))]:
                i=d.InterfaceSpec();i.name=name;ch=d.ChannelSpec();ch.name=name;ch.injection_site=site;ch.direction=d.Direction(*direction);i.channel=ch;w.declare_interface(i)
            hub=w.view('mobile').spec.ports['hub'];n=w.runtime.dimension
            for name,site,direction in [('mobile_cue',d.Coordinate((hub.x+3)%n,hub.y,hub.z),(-1,0,0)),('mobile_reference',d.Coordinate((hub.x-3)%n,(hub.y-3)%n,hub.z),(1,1,0))]:
                i=d.InterfaceSpec();i.name=name;ch=d.ChannelSpec();ch.name=name;ch.injection_site=site;ch.direction=d.Direction(*direction);i.channel=ch;w.declare_interface(i)
            if arm!='no_body_history':body_experience(w,['A','B'],32)
            else:w.run_until(34)
            # Training was fixed before advancing: install independent source
            # events at their actual T0 frontier, not after inspecting output.
            # A fresh reproduction is a new preparation, not the same MAIN.
            w0=d.create_organization('mobile_basal',history=d.BasalHistory.H0,body_only=True)
            for i in w.interfaces:
                if i.name not in [x.name for x in w0.interfaces]:w0.declare_interface(i)
            ids=[]
            if arm!='no_body_history':ids += [w0.submit('E_A',0,32).id,w0.submit('E_B',0,33).id]
            if arm!='mobile_absent':ids += [w0.submit('mobile_cue',0,32).id,w0.submit('mobile_reference',reference,33 if arm=='unpaired' else 32).id]
            e.snapshot(w0,'BRIDGE_T0_'+str(reference)+'_'+arm);w0.run_until(38);mid=body_panel(w0);q,f=body_probe(w0);w0.run_until(82);ret,f2=body_probe(w0)
            bridges.append({'reference':reference,'arm':arm,'receipts':[receipt(w0.runtime.receipt(i)) for i in ids],'at_t38':mid,'common_probe':q,'retention_probe':ret,'same_Runtime':True,'initial_history_selected_H0':True,'knowledge_delivered_by_online_events':True});e.snapshot(w0,'BRIDGE_FINAL_'+str(reference)+'_'+arm)
    e.json('NATIVE_BRIDGE.json',bridges)
    controls=[]
    for arm in ['paired','unpaired','no_experience']:
        s=Session.create(slots=16)
        if arm=='paired':s.experience(0,12,16)
        elif arm=='unpaired':
            for j,ref in enumerate((12,16)):s.world.submit(f'l{j}.cue',0,0);s.world.submit(f'l{j}.teacher',ref,1)
        s.advance_to(6);s.signal('s0',0);s.advance_to(11);controls.append({'arm':arm,'frame':s.state['frames'][-1]})
    s=Session.create(slots=16,feedback=True);s.experience(0,12,16);s.advance_to(6);s.signal('s1',0);s.advance_to(41)
    loop={'frames':s.state['frames'],'environment':s.state['environment'],'native_state':physical(s.world)};s.save(e.folder/'C08_REPEATED_MAIN_FINAL.deetsnap')
    saturation=Session.create(slots=16);saturation.experience(0,12,16);saturation.advance_to(6)
    for k in range(6):saturation.schedule(4000,k,'environment_experience');saturation.advance_to(11+5*k)
    sat={'frames':saturation.state['frames'],'gap':[f['outputs'][1]['s_reg']-f['outputs'][0]['s_reg'] if all(o['active'] for o in f['outputs']) else None for f in saturation.state['frames']],
         'scope':'six finite contacts, scalar cap vs relative observation; no reset or claim of hidden-history destruction'}
    rest,_=learned_mobile((12,16),cue=0);rest.advance(500);rq,f=mobile_query(rest,29,protocol='after500');e.snapshot(rest,'REST500_MAIN')
    e.json('C08_CONTROLS_REUSE.json',{'controls':controls,'repeated_environment':loop,'saturation':sat,'rest500':rq})
    phase=[]
    for delay in [0,1,2]:
        w=make_body();w.advance(delay);rs=body_experience(w,['A','B']);q,f=body_probe(w);phase.append({'delay':delay,'events':rs,'delta':body_panel(w)['delta'],'response':q['response'],'expected_first_event_FSM':1})
    e.json('C01_PHASE_DOMAIN.json',phase)
    # One actually new query on preserved C05 prefix, not a repeated full case.
    checkpoint=root/'casos/C05/TRANSFER_IN_FLIGHT_12.deetsnap';w=d.OrganizationalWorld.load_snapshot(str(checkpoint));hub=w.view('stage0').spec.ports['response'];cut_site=[(hub.x-2)%127,(hub.y+2)%127,hub.z]
    panel=[{'channel':'receiver_query','value':11,'at':16,'read':21,'view':'stage0','port':'receiver_response'}]
    diag=compare_panel(checkpoint,cut_site,panel);e.json('CAUSAL_RESERVED_PANEL.json',diag);e.json('CAUSAL_PANEL_SPEC.json',{'cut_site':cut_site,'panel':panel})
    return e.finish({'native_bridge':bridges,'C08_control_reuse':'C08_CONTROLS_REUSE.json','phase_domain':phase,'causal_reserved':diag,
                     'dependencies':['C02','C05','C07','C08_INTERFACE_V2'],'count_once_not_independent_demonstrations_per_field':True})

if __name__=='__main__':print(json.dumps({'status':run(sys.argv[1])['status']},indent=2))
