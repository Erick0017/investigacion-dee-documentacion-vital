"""Public product4 finite R14 component, not an integrated ABCD controller."""
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
import sys,time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.auditor.passive import digest,record,operation_state,receipt

def put(path,x):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf-8')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    import dee_thinking as d
    out=ROOT/'resultados/auditor/R14_PUBLIC_COMPONENT';out.mkdir(parents=True,exist_ok=True)
    config={'id':'CPC4_A02.R14_PUBLIC_COMPONENT.v1','freeze_utc':datetime.now(timezone.utc).isoformat(),
       'N':67,'cases':[{'id':f'{role}_{actual:+d}','roles':role,'actual':actual,'actual_enabled':True}
           for role in ('P','Q') for actual in (-1,1)]+[{'id':'Q_ACTUAL_OMITTED','roles':'Q','actual':1,'actual_enabled':False}],
       'diagnostic_fork':{'parent':'Q_+1','tick':2,'remove':'first_report','raw':0,'clock':'preserved'},
       'windows':[1,2,6,10,11,14],
       'scope':'Five fresh finite product4 component preparations and one explicit diagnostic fork. Prepared retainP/switchQ law; not new utility learning, not integrated into ABCD, not renewable after resource consumption.',
       'expected_only_for_external_evaluator':'If P carries the matching binary report, retain P; if Q does, mismatch switches Q. This text is never used for inputs or native response.'}
    config_path=out/'EXPERIMENT_CONFIG.json'
    if config_path.exists():raise FileExistsError('Component cutoff already frozen; do not overwrite')
    put(config_path,config);rows=[];started=time.monotonic();fork_data=None
    assert d.__version__=='4.0.0' and d.kernel_identity()['kernel_version']==27
    for case in config['cases']:
        p=d.FinitePolicyParameters();p.roles=d.SourceRole.P_INFORMATIVE if case['roles']=='P' else d.SourceRole.Q_INFORMATIVE
        p.actual_class=case['actual'];p.actual_enabled=case['actual_enabled'];p.execution=d.TickOptions(d.Backend.LAZY,1)
        session=d.FinitePolicySession.create(p);folder=out/case['id'];folder.mkdir()
        calls=[{'operation':'FinitePolicySession.create','tick':0,'mode':'PREPARED_EXPLICIT_ENVIRONMENT',
                'roles':case['roles'],'actual_binary_report':case['actual'],'actual_enabled':case['actual_enabled']}]
        session.save_snapshot(str(folder/'T0.deetsnap'));samples=[]
        for tick in config['windows']:
            session.run_until(tick);calls.append({'operation':'run_until','tick':tick})
            before=digest(session.world);sample=session.observe().as_dict();again=session.observe().as_dict()
            assert sample==again and digest(session.world)==before
            samples.append(sample)
            if tick==2:
                session.save_snapshot(str(folder/'T2_SESSION.deetsnap'))
                if case['id']=='Q_+1':
                    q=session.world.view('selection').spec.ports['first_report']
                    pre=record(session.world.runtime.observe(q));edit=d.ResearchStateEdit();edit.coordinate=q;edit.raw=0;edit.label='DIAGNOSTIC_REMOVE_FORMED_FIRST_REPORT'
                    parent_before=operation_state(session.world);child=session.diagnostic_fork([edit],True)
                    post=record(child.world.runtime.observe(q));assert operation_state(session.world)==parent_before
                    assert post['raw']==0 and post['clock']==pre['clock']
                    fork_data=(child,{'parent_id':case['id'],'start_tick':2,'intervention':{'site':pre['site'],'pre':pre,'post':post,
                        'raw_sites_changed':1,'clock_sites_changed':0,'parent_unchanged':True}})
            if tick in (6,10,14):session.save_snapshot(str(folder/f'T{tick}.deetsnap'))
        result={'case':case,'mode':'PREPARED_PRODUCT_COMPONENT_WITH_CURRENT_REPORT_PROTOCOL',
            'samples':samples,'actual_calls':calls,'receipts':[receipt(r) for r in session.world.runtime.receipts],
            'journal':[{'tick':x.tick,'operation':x.operation,'interface':x.interface_name,'value':x.value,'receipt_id':x.receipt_id,'modality':str(x.modality)} for x in session.journal],
            'final':digest(session.world),'checkpoint':str((folder/'T14.deetsnap').relative_to(ROOT)),
            'selected_source_actions':[x.as_dict() for x in session.world.view('selection').runtime.receipts] if False else samples[-2]['actions'],
            'scope':config['scope']}
        put(folder/'MEASUREMENTS.json',result);rows.append({'id':case['id'],'kind':'FRESH_FINITE_COMPONENT','final':result['final'],
            'policy10':samples[3]['policies'],'action11':samples[4]['actions'],'information14':samples[5]['information'],
            'receipts':result['receipts'],'evidence':str((folder/'MEASUREMENTS.json').relative_to(ROOT))})
    child,meta=fork_data;folder=out/'LATE_REPORT_REMOVE';folder.mkdir();samples=[]
    for tick in (6,10,11,14):child.run_until(tick);samples.append(child.observe().as_dict())
    child.save_snapshot(str(folder/'T14.deetsnap'))
    result={'kind':'DIAGNOSTIC_FORK_NOT_MERGED','metadata':meta,'samples':samples,'final':digest(child.world),
            'scope':'Formed first action exists before this fork; only formed first-report RAW removed at2. This is diagnostic, not autonomous regulation or a new independent fresh individual.'}
    put(folder/'MEASUREMENTS.json',result);rows.append({'id':'LATE_REPORT_REMOVE','kind':'DIAGNOSTIC_FORK',
        'policy10':samples[1]['policies'],'action11':samples[2]['actions'],'information14':samples[3]['information'],
        'evidence':str((folder/'MEASUREMENTS.json').relative_to(ROOT))})
    summary={'component':'FinitePolicySession public4 native implementation','library':d.__version__,'kernel':27,
        'native_sha256':sha(d._native.__file__),'new_fresh_component_preparations':5,'diagnostic_forks':1,
        'independent_ABCD_network_preparations':0,'maximum_tick':14,'rows':rows,
        'elapsed_seconds':time.monotonic()-started,'code_sha256':sha(__file__),'config_sha256':sha(config_path),
        'scope':config['scope'],'closed_reason':'Frozen five fresh cases and one late diagnostic contrast completed; no new search.'}
    put(out/'RUN_SUMMARY.json',summary);print(json.dumps({'status':'MEASURED','fresh':5,'forks':1,'seconds':summary['elapsed_seconds']}))

if __name__=='__main__':main()
