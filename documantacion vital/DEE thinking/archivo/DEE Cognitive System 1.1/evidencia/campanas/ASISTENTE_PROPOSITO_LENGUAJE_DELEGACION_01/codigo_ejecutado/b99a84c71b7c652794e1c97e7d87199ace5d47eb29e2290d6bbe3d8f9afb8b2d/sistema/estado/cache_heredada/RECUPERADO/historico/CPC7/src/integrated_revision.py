"""One M1 revision in a continuing guarded U0, not a separate K2 apparatus.

Four empty auxiliary interfaces are declared atT0 in every candidate. The
current consequence selects the same fixed input codec in treatment and sham;
the host does not inspect the old learned direction to compensate it.
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
from common import ROOT,identity,put,sha,interface,record,receipt,digest,operational,local_context
import selective_native as core
import residue_regulation as regulation
import comparison_need as need


_sessions=[]


def validate_case(case):
    if len(case['bank_values'])!=16 or any(type(v) is not int or v not in (-1,1) for v in case['bank_values']):
        raise ValueError('Exactly sixteen current-experience values required before preparing any Runtime')
    if type(case['new_sign']) is not int or case['new_sign'] not in (-1,1):raise ValueError('Current consequence codec is binary')
    if case['revision_mode'] not in ('treatment','offpath_sham'):raise ValueError('Explicit revision modality required')


def prepare_geometry(case):
    validate_case(case);p=regulation.guard_geometry(case);g=p['geometry'];hub=g['forms'][2]['hub'];ports={}
    for mode,shift in (('treatment',(0,0,0)),('offpath_sham',(0,0,55))):
        for value,label in ((-1,'minus'),(1,'plus')):
            direction=(-1,value,0);target=need.moved(hub,shift,1);site=need.moved(target,direction,-3)
            name='revision.second.'+mode+'.'+label;p['interfaces'].append(interface(name,site,direction));ports[mode+'.'+label]=name
    g['interfaces']=len(p['interfaces']);g['integrated_revision']={'schema':'CPC7.integrated_revision.geometry.v1',
        'form':'L03','hub':hub,'input_tick':402,'revision_contact':405,'next_panel_input':469,'next_panel_read':472,
        'auxiliary_ports':ports,'auxiliary_sham_shift':[0,0,55],'auxiliary_sham_plane':60,
        'fixed_protocol':'Current opaque cue5 + current ordinary event11 + second teacher11 through a declared direction(-1,current_sign,0).',
        'scope':'One directed consequence update, not a host-computed correction from the old memory. All four empty ports present beforeT0 in every world.'}
    if len({v.name for v in p['interfaces']})!=len(p['interfaces']):raise ValueError('Duplicate interface name')
    return p


def create(case):
    import dee_thinking as d
    p=prepare_geometry(case);r=d.OrganizationRecipe.research(67,p['placements'],0);r.interfaces=p['interfaces'];r.execution=d.TickOptions(d.Backend.LAZY,1)
    s=regulation.GuardSession(d.OrganizationalWorld.create(r),p['geometry'],identity='U0_INTEGRATED_REVISION_'+case['id']);_sessions.append(s);return s


def execute(case,out,config_hash):
    validate_case(case);started=time.monotonic();out=Path(out);old_factory=core.create;core.create=create
    try:base=core.execute({**case,'horizon':338},out,config_hash)
    finally:core.create=old_factory
    s=_sessions.pop();w=s.world;g=s.geometry
    base_path=out/'BASE338_MEASUREMENTS.json';shutil.copyfile(out/'MEASUREMENTS.json',base_path)
    rows=[];windows=[];snaps=[];responses=[];pending=[]
    for tick in range(339,473):
        s.advance_to(tick)
        if tick==402:
            # The actual current event in CONFIG, not a value inferred from a
            # prior response, drives the fixed sensor port in both arms.
            s.stimulate(core.stimulus_for_forms(g,[case['new_sign']]*16,[2],402))
            label='plus' if case['new_sign']==1 else 'minus';port=g['integrated_revision']['auxiliary_ports'][case['revision_mode']+'.'+label]
            s.stimulate([{'port':port,'payload':11,'tick':402,'kind':'submit','origin':'CURRENT_CONSEQUENCE_FIXED_SECOND_TEACHER_CODEC'}])
        if tick==469:
            count=len(s.requests);s.stimulate([{'port':f['name']+'.signal','payload':5,'tick':469,'kind':'probe','origin':'COMMON_FOURTEEN_FORM_POST_REVISION_PANEL'} for f in g['forms'][2:]])
            pending=s.requests[count:]
        if tick==472:
            for q in pending:
                name=q['port'].split('.')[0];f=next(v for v in g['forms'] if v['name']==name);p=record(w,f['hub']);rr=receipt(w,q['id'])
                responses.append({'form':name,'input_tick':469,'tick':472,'physical':p,'receipt':rr,**core.decoded_name(p,rr,5),'provenance':'ENTE'})
        if tick in (401,402,403,404,405,406,468,469,470,471,472):
            rows.append({'tick':tick,'forms':{f['name']:record(w,f['hub']) for f in g['forms'][2:]}})
            windows.append({'tick':tick,'revised_form_Moore27':local_context(w,g['forms'][2]['hub']),
                'scope':'Exact local neighborhood of the declared revised form; other paths not uniquely reconstructed.'})
        if tick in (401,402,404,405,406,468,469,471,472):
            path=out/('T'+str(tick)+'.deetsnap');info=s.save(path);info['path']=path.name;snaps.append(info)
    # Audit comparisons happen only after all native trajectories have ended.
    other=[r for r in responses if r['form']!='L03'];revised=next(r for r in responses if r['form']=='L03')
    old_acquisition=base['acquisition']
    calculations={'post_revision_panel':{'queries':len(responses),'applied':sum(r['receipt']['status']=='applied' for r in responses),
        'covered':sum(r['coverage'] for r in responses)},
        'revised_form':{'coverage':revised['coverage'],'physical_value':revised['value'],'matches_current_experienced_consequence':revised['coverage'] and revised['value']==case['new_sign']},
        'other_thirteen':{'queries':len(other),'applied':sum(r['receipt']['status']=='applied' for r in other),'covered':sum(r['coverage'] for r in other),
            'matches_original_acquisition':sum(r['coverage'] and r['value']==old_acquisition[r['form']]['direction'][1] for r in other)}}
    for name in ('integrated_revision.py','residue_regulation.py'):
        shutil.copyfile(HERE/name,out/'executed_source'/name)
    versions={**base['executed_source'],'integrated_revision.py':sha(__file__),'residue_regulation.py':sha(regulation.__file__)}
    m={'schema':'CPC7.integrated_revision.measurements.v1','case':case,'engine':identity(),'configuration_sha256':config_hash,
        'code_sha256':sha(__file__),'executed_source':versions,'individual':s.identity,'preparations':1,'diagnostic_forks':0,'controlled_continuations':0,
        'same_RUNTIME':True,'geometry':g,'base338':{'path':base_path.name,'sha256':sha(base_path),
            'scope':'Primary subrecord of this same preparation through338, not a second independent case.',
            'final_physical':base['final_physical'],'final_operational':base['final_operational'],
            'calculations':base['calculations'],'opaque_name_reads':base['opaque_name_reads']},
        'rows':rows,'local_windows':windows,'responses':responses,'calculations':calculations,
        'requests':s.receipts(),'guard_observations':s.guard_observations,'snapshots':base['snapshots']+snaps,
        'final_physical':digest(w),'final_operational':operational(w),
        'host_RAW_clock_writes_on_MAIN':[],'old_readout_or_future_target_used_by_stimulus':False,
        'resources':{'initial_material_sites':g['initial_material_sites'],'interfaces':g['interfaces'],'extra_revision_ports':4,'extra_revision_input_requests':3},
        'status':'MEASURED','elapsed_seconds':time.monotonic()-started,
        'scope':'Single guarded U0 first uses own selected memory, acquires a later sign and eight additional correspondences, queries14 in204/338, then receives one directed new consequence forL03 and a postrevision14-form panel472. Prepared geometry, not learned regulation scheduling.'}
    put(out/'MEASUREMENTS.json',m);print(json.dumps({'id':case['id'],'baseline338':base['calculations']['lower_repertoire']['338'],'post472':calculations}),flush=True);return m


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf8'));index=[]
    for case in cfg['cases']:
        validate_case(case);target=a.out/case['id'];m=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf8')) if (target/'MEASUREMENTS.json').exists() else execute(case,target,sha(a.config))
        index.append({'case_id':case['id'],'path':str((target/'MEASUREMENTS.json').relative_to(ROOT)),'sha256':sha(target/'MEASUREMENTS.json'),'schema':m['schema'],'preparations':1,'diagnostic_forks':0})
        put(a.out/'INDEX_ALL.json',{'cases':index,'configuration_sha256':sha(a.config),'code_sha256':sha(__file__)})


if __name__=='__main__':main()
