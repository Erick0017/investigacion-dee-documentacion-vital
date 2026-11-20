"""One bounded diagnosis and prepared interception of ignored teaching currents.

The diagnosis edits only a complete fork. The new preparation places six fixed
zero-load semantic4 objects beforeT0. Neither protocol is learned attention.
The frozen selective_native executor is reused via an explicit factory adapter;
its physical law, inputs, decoder and original primary cases are unchanged.
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
from common import ROOT,identity,put,sha,record,receipt,digest,operational,local_context
from integrated import Session
import selective_native as core
import comparison_need as need


def current_candidates(g,tick=76):
    """Content-independent candidate paths. No ancestry inferred from equality."""
    result=[]
    for key,p in g['names'].items():
        result.append({'role':'unused_teaching_cue.'+key,'site':list(need.moved(p['site'],p['cue_direction'],tick-75)),
            'direction':p['cue_direction'],'origin_site':p['site'],'origin_tick':75})
    for key,p in g['actions'].items():
        result.append({'role':'unused_action_resource.'+key,'site':list(need.moved(p['site'],(0,0,1),tick-72)),
            'direction':[0,0,1],'origin_site':p['site'],'origin_tick':72})
    return result


def guard_geometry(case):
    import dee_thinking as d
    p=core.prepare_geometry(tuple(case.get('center',[33,25,42])),16,case.get('backend','LAZY'),0)
    g=p['geometry'];sham=case['guard_mode']=='sham';objects=[]
    for candidate in current_candidates(g,83):
        count=8 # Cue75+8=83; +z action72+8=80.
        q=need.moved(candidate['origin_site'],candidate['direction'],count)
        if sham:q=need.moved(q,(0,1,0),12)
        item=d.InitialPlacement();item.site=d.Coordinate(*q);item.raw=d.pack_record(1,0,0,0,0,4);item.clock=0
        item.role='Prepared stationary zero-load semantic4 interceptor '+candidate['role']+(' offpath sham' if sham else '')
        objects.append(item)
    all_sites=[(o.site.x,o.site.y,o.site.z) for o in p['placements']+objects]
    if len(set(all_sites))!=len(all_sites):raise ValueError('Guard preparation overlaps a material placement')
    p['placements']+=objects
    g['initial_material_sites']=len(p['placements'])
    g['residue_guard']={'schema':'CPC7.residue_guard.geometry.v1','mode':case['guard_mode'],
        'placement_modality':'INITIAL_PREPARATION beforeT0; never a MAIN state edit',
        'objects':[{'site':[v.site.x,v.site.y,v.site.z],'raw':str(v.raw),'clock':str(v.clock),'role':v.role} for v in objects],
        'state':1,'load':0,'direction':[0,0,0],'semantic':4,'clock':'0','sham_shift':[0,12,0] if sham else [0,0,0],
        'resources_extra':6,'criterion':'Intercept declared unpaired-current routes after use and cue formation; consequences must be measured.',
        'scope':'Fixed designer-prepared interception; not autonomous learned scheduling or a consequence-updated regulation policy.'}
    return p


class GuardSession(Session):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.guard_observations=[]
    def advance_to(self,tick):
        super().advance_to(tick)
        if tick in (0,69,74,75,76,79,80,81,82,83,84,133,137,142,204,338):
            self.guard_observations.append({'tick':tick,'sites':[{'site':p['site'],
                'physical':record(self.world,p['site']),'Moore27':local_context(self.world,p['site'])}
                for p in self.geometry['residue_guard']['objects']],
                'observer_scope':'External passive capture; no fields or inputs are modified by this observer'})


def create_guarded(case):
    import dee_thinking as d
    p=guard_geometry(case);recipe=d.OrganizationRecipe.research(67,p['placements'],0);recipe.interfaces=p['interfaces']
    b=getattr(d.Backend,case.get('backend','LAZY'));recipe.execution=d.TickOptions(b,2 if b==d.Backend.DENSE_PARALLEL else 1)
    s=GuardSession(d.OrganizationalWorld.create(recipe),p['geometry'],identity='U0_GUARDED_'+case['id'])
    _live_sessions.append(s)
    return s


_live_sessions=[]


def execute_guarded(case,out,config_hash):
    """Public executor's sole change is the declared preT0 factory."""
    old_factory=core.create
    core.create=create_guarded
    try:m=core.execute(case,out,config_hash)
    finally:core.create=old_factory
    s=_live_sessions.pop();out=Path(out)
    shutil.copyfile(__file__,out/'executed_source/residue_regulation.py')
    m['base_schema']=m['schema'];m['schema']='CPC7.residue_regulation.guarded.v1'
    m['execution_adapter']={'module':'src/residue_regulation.py','sha256':sha(__file__),
        'mechanism':'Factory replaces only initial recipe; selective_native.execute inputs, native evolution and fixed decoder reused unchanged.',
        'frozen_core_sha256':sha(core.__file__)}
    m['executed_source']['residue_regulation.py']=sha(__file__)
    m['guard_observations']=s.guard_observations
    put(out/'MEASUREMENTS.json',m)
    return m


def execute_diagnostic(case,out,config_hash):
    import dee_thinking as d
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic();engine=identity()
    parent_path=ROOT/'resultados/selective_native'/case['parent_id']/'T75.deetsnap'
    parent=Session.load(parent_path);parent.advance_to(76)
    save_parent=parent.save(out/'T76_pre_diagnostic.deetsnap');save_parent['path']='T76_pre_diagnostic.deetsnap'
    before=digest(parent.world);before_op=operational(parent.world);changes=[];edits=[]
    for candidate in current_candidates(parent.geometry,76):
        p=record(parent.world,candidate['site']);matched=p['active'] and p['semantic']==1 and p['direction']==candidate['direction']
        item={**candidate,'before':p,'matched_declared_current_class':matched}
        if matched:
            e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*candidate['site']);e.raw=0 if case['edit_mode']=='cut' else int(p['raw'])
            e.label='Declared moving-current class '+case['edit_mode'];edits.append(e)
        changes.append(item)
    child=parent.world.diagnostic_fork(edits,True)
    assert digest(parent.world)==before and operational(parent.world)==before_op
    s=Session(child,parent.geometry,parent.requests,identity='DIAGNOSTIC_RESIDUES_'+case['id']);w=s.world;g=s.geometry
    for x in changes:x['after']=record(w,x['site'])
    inherited={q['id'] for q in s.requests};snaps=[save_parent];rows=[];windows=[];name_reads=[];lower_reads=[];pending_names={};pending_lower={}
    pm=json.loads((parent_path.parent/'MEASUREMENTS.json').read_text(encoding='utf8'))
    acquisition={k:v for k,v in pm['acquisition'].items() if k in [f['name'] for f in g['forms'][:8]]}
    def snap(tick):
        path=out/('T'+str(tick)+'.deetsnap');info=s.save(path);info['path']=path.name;snaps.append(info)
    snap(76)
    for tick in range(76,339):
        s.advance_to(tick)
        if tick==134:s.stimulate(core.stimulus_for_forms(g,case['bank_values'],range(8,16),134))
        if tick==137:
            for f in g['forms'][8:]:acquisition[f['name']]=record(w,f['hub'])
        if tick==139:
            prior=len(s.requests);s.stimulate([{'port':p['query_port'],'payload':case.get('name_query_payload',11),
                'tick':139,'kind':'probe','origin':'COMMON_OPAQUE_SIGN_ONLY_QUERY_ALL_CANDIDATES'} for p in g['names'].values()])
            pending_names={q['port']:q['id'] for q in s.requests[prior:]}
        if tick==142:
            for key,p in g['names'].items():
                r=record(w,p['site']);rr=receipt(w,pending_names[p['query_port']]);name_reads.append({'name_bank':key,'tick':142,
                    'physical':r,'receipt':rr,**core.decoded_name(r,rr,case.get('name_query_payload',11)),'provenance':'ENTE'})
        if tick in (201,335):
            prior=len(s.requests);s.stimulate([{'port':f['name']+'.signal','payload':5,'tick':tick,'kind':'probe',
                'origin':'FIXED_INTERFACE_LOWER_REPERTOIRE_RETENTION_PANEL'} for f in g['forms'][2:]])
            pending_lower[tick+3]=s.requests[prior:]
        for q in pending_lower.get(tick,[]):
            name=q['port'].split('.')[0];f=next(f for f in g['forms'] if f['name']==name);r=record(w,f['hub']);rr=receipt(w,q['id'])
            lower_reads.append({'form':name,'tick':tick,'physical':r,'receipt':rr,**core.decoded_name(r,rr,5),'provenance':'ENTE'})
        if tick in (76,79,80,81,82,83,84,133,134,137,139,142,201,204,335,338):rows.append(core.capture(s))
        if tick in (76,79,80,81,82,83,84,137,204,338):
            windows.append({'tick':tick,'current_routes':[{'candidate':p,'Moore27':local_context(w,p['site'])} for p in current_candidates(g,tick)],
                'scope':'Declared candidate trajectories, not uniquely reconstructed ancestry'})
        if tick in (84,137,142,204,338):snap(tick)
    calculations={}
    for tick in (204,338):
        observed=[r for r in lower_reads if r['tick']==tick]
        calculations[str(tick)]={'queries':len(observed),'applied':sum(r['receipt']['status']=='applied' for r in observed),
            'covered':sum(r['coverage'] for r in observed),'matches_acquisition':sum(r['coverage'] and r['value']==acquisition[r['form']]['direction'][1] for r in observed)}
    source_bundle=out/'executed_source';source_bundle.mkdir();versions={}
    for filename in ('residue_regulation.py','selective_native.py','common.py','integrated.py'):
        shutil.copyfile(HERE/filename,source_bundle/filename);versions[filename]=sha(HERE/filename)
    m={'schema':'CPC7.residue_regulation.diagnostic.v1','case':case,'engine':engine,'configuration_sha256':config_hash,
        'code_sha256':sha(__file__),'executed_source':versions,'geometry':g,'individual':s.identity,
        'preparations':0,'diagnostic_forks':1,'controlled_continuations':0,
        'parent':{'case_id':case['parent_id'],'snapshot':str(parent_path.relative_to(ROOT)),'sha256':sha(parent_path),
            'source_tick':75,'natural_continuation_to_intervention_tick':76,'parent_physical_before_fork':before,
            'parent_RAW_clocks_and_operational_unchanged_after_fork':True},
        'diagnostic_edits':{'tick':76,'mode':case['edit_mode'],'fields':'RAW only; clocks preserved','candidate_positions':changes,
            'matched_records':len(edits),'rule':'All six fixed candidate positions inspected; cut only active semantic1 record whose direction equals that declared current class. No target/history/classification lookup.'},
        'rows':rows,'local_windows':windows,'acquisition':acquisition,'opaque_name_reads':name_reads,'lower_repertoire_reads':lower_reads,
        'requests':[{**q,'inherited_from_parent':q['id'] in inherited} for q in s.receipts()],
        'calculations':{'lower_repertoire':calculations,'opaque_covered':sum(r['coverage'] for r in name_reads)},
        'snapshots':snaps,'final_physical':digest(w),'final_operational':operational(w),'status':'MEASURED',
        'elapsed_seconds':time.monotonic()-started,
        'scope':'External diagnostic ablation of a declared stream class. It does not become a MAIN regulation mechanism or demonstrate a learned policy.'}
    put(out/'MEASUREMENTS.json',m);print(json.dumps({'id':case['id'],'matched_currents':len(edits),'calculations':m['calculations']}),flush=True)
    return m


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--group',choices=('diagnostic','guarded'),required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf8'));index=[]
    for case in cfg['cases']:
        if case['group']!=a.group:continue
        target=a.out/case['id'];m=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf8')) if (target/'MEASUREMENTS.json').exists() else (execute_diagnostic if a.group=='diagnostic' else execute_guarded)(case,target,sha(a.config))
        index.append({'case_id':case['id'],'path':str((target/'MEASUREMENTS.json').relative_to(ROOT)),'sha256':sha(target/'MEASUREMENTS.json'),
            'preparations':m['preparations'],'diagnostic_forks':m['diagnostic_forks'],'schema':m['schema']})
        put(a.out/('INDEX_'+a.group+'.json'),{'cases':index,'configuration_sha256':sha(a.config),'code_sha256':sha(__file__)})


if __name__=='__main__':main()
