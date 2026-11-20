"""Finite native-need trajectories with exact local pre/post records."""
from pathlib import Path
import argparse,json,sys,time,shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,identity,put,sha,record,digest,operational,receipt,local_context
import order_memory
from integrated import Session
import comparison_need as apparatus


def create(case):
    import dee_thinking as d
    body=order_memory.prepare_geometry(center=tuple(case.get('center',[33,25,33])))
    adapter=apparatus.prepare_geometry(origin=body['geometry']['emission_site'])
    placements=body['placements']+adapter['placements'];ports=body['interfaces']+adapter['interfaces']
    sites=[(p.site.x,p.site.y,p.site.z) for p in placements]
    if len(sites)!=len(set(sites)):raise ValueError('Combined preparation overlaps')
    recipe=d.OrganizationRecipe.research(67,placements,0);recipe.interfaces=ports
    recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    return Session(d.OrganizationalWorld.create(recipe),{'body':body['geometry'],'need':adapter['geometry']})


def run(case,out):
    import dee_thinking as d
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic();engine=identity();s=create(case);w=s.world;g=s.geometry['need']
    for name in ('run_need.py','comparison_need.py'):shutil.copyfile(Path(__file__).parent/name,out/name)
    put(out/'CONFIG.json',{'case':case,'geometry':s.geometry,'source_sha256':sha(__file__),
       'criterion':'Actual native X request after comparison, followed by different source-dependent fields and later common physical use. Emission precedes source contact.',
       'horizon':35,'no_global_uncertainty_classifier':True})
    if case.get('history','AB')!='NONE':s.stimulate(order_memory.experience(case.get('history','AB')))
    if not case.get('reader_omitted'):s.stimulate([{'port':'order.read','payload':7,'tick':2,'kind':'probe','origin':'COMMON_ORDER_READER'}])
    s.stimulate(apparatus.source_protocol(g,case.get('source_value',1),case.get('source_mode','paired')))
    s.stimulate(apparatus.use_protocol(g));rows=[];snaps=[];windows=[];edits=[]
    def snap(label):
        path=out/(label+'.deetsnap');v=s.save(path);v['path']=path.name;snaps.append(v)
    snap('T0')
    for tick in range(36):
        s.advance_to(tick)
        if tick==5 and not case.get('actual_omitted'):s.stimulate(apparatus.actual_protocol(g,case.get('actual',1)))
        if tick==20 and case.get('late_question_edit'):
            # Observe the emitted carrier at the declared next site, never
            # select a route by a hidden scenario target or expected answer.
            candidates=[]
            for name,b in g['branches'].items():
                if not b['dx']:continue
                site=apparatus.moved(b['request_site'],(b['dx'],0,0),1)
                before=record(w,site)
                if before['active'] and before['direction']==[b['dx'],0,0]:candidates.append((name,site,before))
            ds=[];change=[]
            for name,site,before in candidates:
                e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*site);e.raw=0 if case['late_question_edit']=='cut' else int(before['raw']);e.label='Declared diagnostic formed-question '+case['late_question_edit'];ds.append(e)
                change.append({'branch':name,'site':site,'before':before})
            parent=digest(w);child=w.diagnostic_fork(ds,True)
            if digest(w)!=parent:raise AssertionError('Diagnostic mutated MAIN')
            s=Session(child,s.geometry,s.requests,identity='DIAGNOSTIC_'+case['id']);w=s.world
            for r in change:r['after']=record(w,r['site'])
            edits.append({'tick':20,'edits':change,'parent_unchanged':True,'fields':'RAW only; clocks preserved','modality':'DIAGNOSTIC_FORK'})
        row={'tick':tick,'body':order_memory.observations(w,s.geometry['body']),'need':apparatus.capture(w,g)};rows.append(row)
        if tick in (14,15,18,19,20,23,24,28,29):
            windows.append({'tick':tick,'comparison':{k:local_context(w,q) for k,q in g['comparison_hubs'].items()},
                'questions':{k:local_context(w,b['request_site']) for k,b in g['branches'].items()}})
        if tick in (5,15,19,24,29,35):snap('T'+str(tick))
        if tick in (5,15,19,24,29,35):put(out/'INCREMENTAL.json',{'last_complete_tick':tick,'rows':rows,'requests':s.receipts()})
    at={r['tick']:r for r in rows};questions=[];received=[];used=[]
    for name,o in at[19]['need']['questions'].items():
        if o['active'] and o['direction'][0] in (-1,1) and o['direction'][1:]==[0,0]:questions.append({'branch':name,'physical':o})
    for name,o in at[24]['need']['source_contacts'].items():
        if o['active'] and o['direction'][0] in (-1,1) and o['direction'][1] in (-1,1) and o['direction'][2]==0:received.append({'branch':name,'physical':o})
    for name,o in at[29]['need']['later_use'].items():
        if o['active'] and o['direction'][0] in (-1,1) and o['direction'][1] in (-1,1) and o['direction'][2]==1:used.append({'site':name,'physical':o})
    result={'schema':'CPC7.native_need.comparison.measurements.v1','case':case,'engine':engine,'geometry':s.geometry,
        'rows':rows,'local_windows':windows,'snapshots':snaps,'requests':s.receipts(),'diagnostic_edits':edits,
        'native_questions':questions,'received_information':received,'later_physical_use':used,
        'final_physical':digest(w),'final_operative':operational(w),'preparations':1,
        'host_RAW_clock_writes_on_MAIN':[],'elapsed_seconds':time.monotonic()-started,
        'scope':'Finite native comparison-conditioned question, not learned utility-optimal policy or general six-state need detection. Diagnostic edits are separate forks.'}
    put(out/'MEASUREMENTS.json',result);print(json.dumps({'id':case['id'],'questions':len(questions),'received':len(received),'used':len(used),'seconds':result['elapsed_seconds']}),flush=True);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);index=[]
    for case in json.loads(a.config.read_text(encoding='utf-8-sig'))['cases']:
        out=a.out/case['id'];r=json.loads((out/'MEASUREMENTS.json').read_text(encoding='utf-8')) if (out/'MEASUREMENTS.json').exists() else run(case,out)
        index.append({'id':case['id'],'questions':r['native_questions'],'information':r['received_information'],'use':r['later_physical_use'],
                      'evidence':str((out/'MEASUREMENTS.json').resolve()),'sha256':sha(out/'MEASUREMENTS.json')});put(a.out/'INDEX.json',{'cases':index})

if __name__=='__main__':main()
