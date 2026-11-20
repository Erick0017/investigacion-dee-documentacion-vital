"""Finite U0 question -> own acquired bank -> native use -> later opaque sign.

The two candidate memory banks belong to the same fresh Runtime as the learned
order body. No datasource carrier is separately supplied to the question path.
All potential action/name paths are prepared; the host never selects one from
the contents read. Additional lower banks test retention after new experience.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE/'endogenous'))
from common import ROOT,identity,put,sha,record,receipt,digest,operational,interface,local_context
from integrated import Session
import order_memory
import repertoire_reference as repertoire
import comparison_need as need
import body_source


def prepare_geometry(center=(33,25,42),k=16,backend='LAZY',body_source_load=0):
    """Pure preT0 recipe assembly, including explicit shared-interface policy."""
    if k!=16:raise ValueError('First selective-native contract fixes16 banks')
    body=body_source.prepare_geometry(center=tuple(center),source_load=body_source_load)
    prior=need.prepare_geometry(origin=body['geometry']['emission_site'])
    placements=body['placements']+prior['placements']
    ports=body['interfaces']+[p for p in prior['interfaces'] if '.actual.' in p.name]
    base,_=repertoire.geometry({'N':67,'K':16,'plane_gap':2})
    forms=deepcopy(base['forms']);n=67;banks={}
    for index,(lane,s) in enumerate((('left',-1),('right',1))):
        branch=prior['geometry']['branches'][lane+'.different']
        q=need.moved(branch['request_site'],(s,0,0),51,n)
        forms[index]['hub']=list(q)
        banks[lane]={'form':forms[index]['name'],'hub':list(q),'request_site':branch['request_site'],
            'request_direction':s,'question_tick':19,'information_tick':70,
            'question_distance':51,'native_reader':'Comparison-conditioned horizontal question, not a host probe'}
    # All16 are new, untrained preparations. L01/2 are deliberately relocated;
    # this is not the unmodified CPC5 isolated-plane recipe.
    for f in forms:
        h=tuple(f['hub']);name=f['name']
        ports.append(interface(name+'.signal',need.moved(h,(-1,0,0),-3),(-1,0,0)))
        for v,label in ((1,'plus'),(-1,'minus')):
            dr=(1,v,0);ports.append(interface(name+'.event.'+label,need.moved(h,dr,-3),dr))
    action_inputs={};actions={};names={}
    for lane,b in banks.items():
        s=b['request_direction'];q=tuple(b['hub'])
        for v,label in ((-1,'minus'),(1,'plus')):
            at72=need.moved(q,(s,v,0),2)
            action_name='own.use.'+label
            # Left/right target coincide at72. Only ONE physical input is
            # scheduled per content-independent opportunity; no duplicate host
            # requests are hidden behind two logical roles.
            if action_name not in action_inputs:
                site=need.moved(at72,(0,0,1),-3)
                ports.append(interface(action_name,site,(0,0,1)))
                action_inputs[action_name]={'site':list(site),'target':list(at72),'input_tick':69,
                    'read_tick':72,'roles':[],'direction':[0,0,1]}
                actions[action_name]={'site':list(at72),'read_tick':72,'possible_roles':[]}
            elif action_inputs[action_name]['target']!=list(at72):raise ValueError('Shared opportunity no longer coincides')
            action_inputs[action_name]['roles'].append(lane)
            actions[action_name]['possible_roles'].append(lane)
            anchor=need.moved(at72,(s,v,1),3)
            code=lane+'.'+label;teach='own.name.teach.'+code;query='own.name.query.'+code
            cue=(-s,0,-1)
            ports.append(interface(teach,need.moved(anchor,cue,-3),cue))
            ports.append(interface(query,need.moved(anchor,(-1,0,0),-3),(-1,0,0)))
            names[code]={'lane':lane,'candidate_direction_y':v,'site':list(anchor),'teach_port':teach,
                'teach_input_tick':72,'association_tick':75,'query_port':query,'query_tick':139,'read_tick':142,
                'cue_direction':list(cue),'prior_action_tick':72,
                'scope':'Fixed opaque cue paired after native use; all candidate routes receive it'}
    sites=[(p.site.x,p.site.y,p.site.z) for p in placements]
    if len(sites)!=len(set(sites)):raise ValueError('Initial placements overlap')
    if len({p.name for p in ports})!=len(ports):raise ValueError('Duplicate interface name')
    geometry={'schema':'CPC7.selective_native.geometry.v1','N':67,'body':body['geometry'],
        'need':{'prefix':prior['geometry']['prefix'],'comparison_hubs':prior['geometry']['comparison_hubs'],
            'branches':{k:{f:v for f,v in b.items() if f!='source_contact'} for k,b in prior['geometry']['branches'].items()},
            'ticks':{'comparison':15,'question':19,'information':70,'action':72,'association':75,'name_query':139,'name_read':142}},
        'forms':forms,'banks':banks,'action_inputs':action_inputs,'actions':actions,'names':names,
        'initial_material_sites':len(placements),'interfaces':len(ports),
        'shared_interface_policy':'Coincident physical action ports are one shared resource; schedule once per unique interface, not once per possible branch.',
        'traditional_datasource_interfaces_installed':False,
        'scope':'New fixed geometry; native question selects one of two own acquired banks. Other14 have explicit fixed-interface retention panels.'}
    return {'placements':placements,'interfaces':ports,'geometry':geometry,'backend':backend}


def create(case):
    import dee_thinking as d
    prepared=prepare_geometry(tuple(case.get('center',[33,25,42])),16,case.get('backend','LAZY'),case.get('body_source_load',0))
    recipe=d.OrganizationRecipe.research(67,prepared['placements'],0);recipe.interfaces=prepared['interfaces']
    b=getattr(d.Backend,case.get('backend','LAZY'));recipe.execution=d.TickOptions(b,2 if b==d.Backend.DENSE_PARALLEL else 1)
    return Session(d.OrganizationalWorld.create(recipe),prepared['geometry'],identity='U0_SELECTIVE_'+case['id'])


def stimulus_for_forms(geometry,values,indices,tick):
    result=[]
    for i in indices:
        f=geometry['forms'][i];v=values[i]
        if v not in(-1,1):raise ValueError('Actual directional consequence outside fixed sensor domain')
        result += [{'port':f['name']+'.signal','payload':5,'tick':tick,'kind':'submit','origin':'CURRENT_OPAQUE_FORM'},
            {'port':f['name']+'.event.'+('plus' if v==1 else 'minus'),'payload':11,'tick':tick,'kind':'submit','origin':'CURRENT_OBSERVED_DIRECTIONAL_CONSEQUENCE'}]
    return result


def capture(s):
    w=s.world;g=s.geometry
    return {'tick':int(w.runtime.current_tick),'body':order_memory.observations(w,g['body']),
        'questions':{k:record(w,b['request_site']) for k,b in g['need']['branches'].items() if b['dx']},
        'own_banks':{k:record(w,b['hub']) for k,b in g['banks'].items()},
        'action_sites':{k:record(w,b['site']) for k,b in g['actions'].items()},
        'name_sites':{k:record(w,b['site']) for k,b in g['names'].items()}}


def decoded_name(p,rr,payload):
    valid=rr['status']=='applied' and p['active'] and p['semantic']==1 and p['s_reg']>payload and p['direction'] in ([-1,-1,0],[-1,1,0])
    return {'coverage':bool(valid),'value':p['direction'][1] if valid else None}


def execute(case,out,config_hash):
    import dee_thinking as d
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic();engine=identity()
    provenance={};edits=[];start=0;inherited_ids=set();inherited_acquisition={}
    if case.get('parent_id'):
        path=out.parent/case['parent_id']/'T20.deetsnap';parent=Session.load(path)
        inherited_ids={q['id'] for q in parent.requests};before=digest(parent.world);before_op=operational(parent.world)
        changes=[];research=[]
        for name,b in parent.geometry['need']['branches'].items():
            if not b['dx']:continue
            site=need.moved(b['request_site'],(b['dx'],0,0),1);p=record(parent.world,site)
            e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*site)
            e.raw=0 if case['edit_mode']=='cut' else int(p['raw']);e.label='Declared formed-question '+case['edit_mode']
            research.append(e);changes.append({'role':name,'site':list(site),'before':p})
        child=parent.world.diagnostic_fork(research,True)
        assert digest(parent.world)==before and operational(parent.world)==before_op
        s=Session(child,parent.geometry,parent.requests,identity='DIAGNOSTIC_'+case['id']);start=20
        for x in changes:x['after']=record(s.world,x['site'])
        edits=[{'tick':20,'changes':changes,'fields':'RAW only; clock preserved','parent_unchanged':True}]
        provenance={'parent_case':case['parent_id'],'parent_snapshot':str(path.relative_to(ROOT)),
            'parent_snapshot_sha256':sha(path),'parent_physical':before,'parent_operational_unchanged':True}
        parent_measurements=path.parent/'MEASUREMENTS.json'
        inherited_acquisition=json.loads(parent_measurements.read_text(encoding='utf8'))['acquisition']
        provenance['acquisition_auditor_source']={'path':str(parent_measurements.relative_to(ROOT)),
            'sha256':sha(parent_measurements),'scope':'Earlier primary observations for post-evolution comparison only; never an input, decoder, or participant memory'}
    else:
        s=create(case)
        s.stimulate(order_memory.experience(case.get('history','AB')))
        s.stimulate([{'port':'order.read','payload':7,'tick':2,'kind':'probe','origin':'COMMON_EXPERIENCED_BODY_READER'}])
        s.stimulate(stimulus_for_forms(s.geometry,case['bank_values'],range(8),0))
    w=s.world;g=s.geometry;rows=[];windows=[];snaps=[];name_reads=[];lower_reads=[];pending_lower={};acquisition=deepcopy(inherited_acquisition);predictions=[]
    versions={};bundle=out/'executed_source';bundle.mkdir()
    for relative in ['selective_native.py','common.py','integrated.py','order_memory.py','repertoire_reference.py','endogenous/comparison_need.py','endogenous/body_source.py']:
        src=HERE/relative;target=bundle/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target);versions[relative]=sha(src)
    put(out/'CONFIG.json',{'case':case,'configuration_sha256':config_hash,'executed_source':versions,'geometry':g,
        'frozen_decoder':'Applied active semantic1 direction[-1,+/-1,0] and load above query; no expected content input',
        'modality_separation':'Initial body and route preparation; real experiences; native question; common physical action probes; external later name cue; physical later sign query',
        'no_external_query_to_L01_L02_at67':True,'no_traditional_datasource':True})
    def snap(tick):
        p=out/('T'+str(tick)+'.deetsnap');v=s.save(p);v['path']=p.name;snaps.append(v)
    snap(start)
    observe={3,5,14,15,18,19,20,21,69,70,71,72,73,74,75,76,133,134,137,138,139,140,141,142,143,201,204,335,338}
    decisive={69,70,71,72,74,75,141,142}
    boundaries={20,69,70,74,75,142,338}
    pending_names={}
    for tick in range(start,case.get('horizon',338)+1):
        s.advance_to(tick)
        if tick==3:
            for f in g['forms'][:8]:acquisition[f['name']]=record(w,f['hub'])
        if tick==5:
            predictions.append({'emission_tick':5,'target_tick':15,'physical':record(w,g['body']['emission_site']),
                'provenance':'ENTE','scope':'Actual pre-outcome physical emission; no external error fed back'})
            put(out/'PREDICCIONES.json',predictions)
        if tick==11:s.stimulate(need.actual_protocol(g['need'],case['actual']))
        if tick==69:
            s.stimulate([{'port':p,'payload':7,'tick':69,'kind':'probe','origin':'COMMON_NATIVE_USE_RESOURCE_ALL_CANDIDATES'} for p in g['action_inputs']])
        if tick==72 and case.get('name_mode','paired')!='omitted':
            delay=int(case.get('name_mode')=='unpaired')
            s.stimulate([{'port':q['teach_port'],'payload':5,'tick':72+delay,'kind':'submit','origin':'OPAQUE_CUE_AFTER_NATIVE_INFORMATION_AND_USE'} for q in g['names'].values()])
        if tick==134:
            s.stimulate(stimulus_for_forms(g,case['bank_values'],range(8,16),134))
        if tick==137:
            for f in g['forms'][8:]:acquisition[f['name']]=record(w,f['hub'])
        if tick==139:
            prior=len(s.requests);s.stimulate([{'port':q['query_port'],'payload':case.get('name_query_payload',5),
                'tick':139,'kind':'probe','origin':'COMMON_OPAQUE_SIGN_ONLY_QUERY_ALL_CANDIDATES'} for q in g['names'].values()])
            pending_names={q['port']:q['id'] for q in s.requests[prior:]}
        if tick==142:
            for key,q in g['names'].items():
                p=record(w,q['site']);rr=receipt(w,pending_names[q['query_port']])
                name_reads.append({'name_bank':key,'input_tick':139,'tick':142,'physical':p,'receipt':rr,
                    **decoded_name(p,rr,case.get('name_query_payload',5)),'provenance':'ENTE'})
        if tick in (201,335):
            prior=len(s.requests);s.stimulate([{'port':f['name']+'.signal','payload':5,'tick':tick,'kind':'probe',
                'origin':'FIXED_INTERFACE_LOWER_REPERTOIRE_RETENTION_PANEL'} for f in g['forms'][2:]])
            pending_lower[tick+3]=s.requests[prior:]
        for q in pending_lower.get(tick,[]):
            form=q['port'].split('.')[0];f=next(x for x in g['forms'] if x['name']==form);p=record(w,f['hub']);rr=receipt(w,q['id'])
            lower_reads.append({'form':form,'input_tick':q['tick'],'tick':tick,'physical':p,'receipt':rr,
                **decoded_name(p,rr,5),'provenance':'ENTE'})
        if tick in observe:rows.append(capture(s))
        if tick in decisive:
            windows.append({'tick':tick,'own_banks':{k:local_context(w,b['hub']) for k,b in g['banks'].items()},
                'action_sites':{k:local_context(w,b['site']) for k,b in g['actions'].items()},
                'name_sites':{k:local_context(w,b['site']) for k,b in g['names'].items()},
                'scope':'Exact local windows; uncovered segments are declared predictions, not unique reconstructed ancestry.'})
        if tick in boundaries and tick!=start:snap(tick)
        if tick in boundaries:put(out/'PROGRESS.json',{'last_complete_tick':tick,'rows':rows,'name_reads':name_reads,'lower_reads':lower_reads,'snapshots':snaps})
    # All classifications/calculations below are auditor work AFTER evolution.
    at={r['tick']:r for r in rows}
    questions=[]
    if 19 in at:
        questions=[{'branch':k,'physical':v} for k,v in at[19]['questions'].items() if v['active'] and v['direction'] in ([-1,0,0],[1,0,0])]
    information=[{'bank':k,'physical':v} for k,v in at[70]['own_banks'].items() if v['active'] and v['direction'][0] in(-1,1) and v['direction'][1] in(-1,1) and v['direction'][2]==0]
    actions=[{'shared_site':k,'physical':v} for k,v in at[72]['action_sites'].items() if v['active'] and v['direction'][0] in(-1,1) and v['direction'][1] in(-1,1) and v['direction'][2]==1]
    useful=[r for r in name_reads if r['coverage']]
    expected_information_values={r['physical']['direction'][1] for r in information}
    lower_calculations={}
    for tick in (204,338):
        rr=[r for r in lower_reads if r['tick']==tick]
        lower_calculations[str(tick)]={'queries':len(rr),'applied':sum(r['receipt']['status']=='applied' for r in rr),
            'covered':sum(r['coverage'] for r in rr),'matches_acquisition':sum(r['coverage'] and r['value']==acquisition.get(r['form'],{}).get('direction',[None,None])[1] for r in rr)}
    result={'schema':'CPC7.selective_native.measurements.v1','case':case,'engine':engine,'configuration_sha256':config_hash,
        'code_sha256':sha(__file__),'executed_source':versions,'geometry':g,'individual':s.identity,
        'preparations':0 if start else 1,'diagnostic_forks':int(bool(start)),'controlled_continuations':0,
        'parent':provenance,'same_RUNTIME_after_boundary':True,'rows':rows,'local_windows':windows,
        'requests':[{**q,'inherited_from_parent':q['id'] in inherited_ids} for q in s.receipts()],
        'native_questions':questions,'native_selected_information':information,'native_actions':actions,
        'opaque_name_reads':name_reads,'lower_repertoire_reads':lower_reads,'acquisition':acquisition,
        'calculations':{'own_information_records':len(information),'unique_action_records':len(actions),
            'opaque_queries':len(name_reads),'opaque_queries_applied':sum(r['receipt']['status']=='applied' for r in name_reads),
            'opaque_covered':len(useful),'opaque_matches_earlier_information':sum(r['value'] in expected_information_values for r in useful),
            'lower_repertoire':lower_calculations},
        'diagnostic_edits':edits,'predictions':predictions,'snapshots':snaps,
        'final_physical':digest(w),'final_operational':operational(w),
        'resources':{'basic_buffers_bytes':32*67**3,'initial_material_sites':g['initial_material_sites'],'interfaces':g['interfaces'],
            'acquired_forms':16,'shared_action_opportunities':2,**repertoire.memory()},
        'host_RAW_clock_writes_on_MAIN':[],'native_answer_reads_targets_or_teaching_map':False,
        'elapsed_seconds':time.monotonic()-started,'status':'MEASURED',
        'scope':'New fixed same-Runtime integration. Comparison selects own learned bank; common resources realize use and a later externally taught opaque sign. No universal language or autonomous utility policy claim.'}
    put(out/'MEASUREMENTS.json',result)
    print(json.dumps({'id':case['id'],'question':len(questions),'information':len(information),'actions':len(actions),
        'opaque':[(r['name_bank'],r['value']) for r in useful],'lower':lower_calculations,'seconds':result['elapsed_seconds']}),flush=True)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--group',choices=['pilot','diagnostic','reserve','language_control'],default='pilot');a=p.parse_args()
    cfg=json.loads(a.config.read_text(encoding='utf8'));index=[]
    for case in cfg['cases']:
        if case['group']!=a.group:continue
        target=a.out/case['id']
        m=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf8')) if (target/'MEASUREMENTS.json').exists() else execute(case,target,sha(a.config))
        index.append({'case_id':case['id'],'evidence':str((target/'MEASUREMENTS.json').relative_to(ROOT)),
            'sha256':sha(target/'MEASUREMENTS.json'),'calculations':m['calculations'],'parent':m['parent']})
        put(a.out/('INDEX_'+a.group+'.json'),{'configuration_sha256':sha(a.config),'code_sha256':sha(__file__),'cases':index})

if __name__=='__main__':main()
