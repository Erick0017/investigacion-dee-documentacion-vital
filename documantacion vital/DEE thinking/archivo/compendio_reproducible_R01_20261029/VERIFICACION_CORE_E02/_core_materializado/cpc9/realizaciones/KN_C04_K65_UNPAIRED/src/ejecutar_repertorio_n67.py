"""External progressive experiences; scoring never selects a native answer."""
from pathlib import Path
import argparse,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src')]
from repertorio_n67 import N67RepertoireSession
from integracion.relational_pair import physical
from ejecutar_retorno import write
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--mode',choices=['paired','opposite','unpaired','no_event'],default='paired');p.add_argument('--k',type=int,default=65);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic();s=N67RepertoireSession.create(a.k)
    r={'schema':'CPC9.repertoire.N67.measurements.v1','case_id':a.case,'configuration':vars(a)|{'out':str(a.out)},'geometry':s.geometry,
       'preparations':1,'MAIN_RAW_clock_edits':[],'frames':[],'snapshots':[],'auditor_experiences':[],'queries':[],'status':'SCHEDULED'}
    group_bounds=((0,8,0),(8,16,80),(16,32,160),(32,65,240));captures={0,3,80,83,160,163,240,243,310,377,444};events={}
    for begin,end,t0 in group_bounds:
        for index in range(begin,min(end,a.k)):
            form=s.geometry['forms'][index];sign=(1 if index%2==0 else-1)*(-1 if a.mode=='opposite'else 1)
            s.input(form['ports']['cue'],5,t0+int(a.mode=='unpaired'))
            if a.mode!='no_event':s.input(form['ports']['event.plus'if sign==1 else'event.minus'],11,t0)
            r['auditor_experiences'].append({'form':form['id'],'actual_event_direction':[1,sign,0],'input_tick':t0,'mode':a.mode})
            count=0;t=t0+3+67
            first_full=t0+3+67*max(1,(243-(t0+3)+66)//67)
            while t<=444:
                role='read.plus'if count%2==0 else'read.minus';s.input(form['ports'][role],7,t-3,True)
                query={'tick':t,'form':form['id'],'hub':form['hub'],'query_index':count,'expected_auditor_direction':[0,sign,1 if count%2==0 else 0],
                    'full_repertoire_round':1+(t-first_full)//67 if t>=first_full else None}
                # Round numbers are documentary; exact per-form query index is the contract.
                r['queries'].append(query);events.setdefault(t,[]).append(query);captures.update((t-1,t));t+=67;count+=1
    write(a.out/'MEDICIONES.json',r)
    for tick in sorted(captures):
        s.run_until(tick);samples=[{'form':q['form'],'query_index':q['query_index'],'expected_auditor_direction':q['expected_auditor_direction'],'physical':s.observe(q['hub'])}for q in events.get(tick,[])]
        r['frames'].append({'tick':tick,'physical':physical(s.world),'queries':samples})
        if tick in(0,3,243,310,444):
            path=a.out/f'T{tick}.deetsnap.gz';r['snapshots'].append({'path':path.name,'storage':s.save(path),'physical':physical(s.world)})
        r.update(last_complete_tick=tick,requests=s.receipts());write(a.out/'MEDICIONES.json',r)
    r.update(status='MEASURED',final_physical=physical(s.world),elapsed_seconds=time.monotonic()-started,source_sha256=hashlib.sha256((ROOT/'src/repertorio_n67.py').read_bytes()).hexdigest())
    write(a.out/'MEDICIONES.json',r)
    print(json.dumps({'case':a.case,'status':r['status'],'k':a.k,'native_ticks':s.tick,'requests':len(s.receipts()),'seconds':time.monotonic()-started}))
if __name__=='__main__':main()
