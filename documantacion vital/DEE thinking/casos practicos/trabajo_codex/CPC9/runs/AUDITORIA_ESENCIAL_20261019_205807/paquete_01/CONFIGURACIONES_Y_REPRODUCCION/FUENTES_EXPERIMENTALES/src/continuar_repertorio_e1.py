"""Actual later experiences in the living MAIN; auditor outcomes never fed back."""
from pathlib import Path
import argparse,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from vida_repertorio_extension import MainWithRepertoire
from integracion.relational_pair import physical
from ejecutar_retorno import write
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--case',default='E1_MAIN_K65_1907_2353');p.add_argument('--omit-events',action='store_true');p.add_argument('--unpaired',action='store_true');a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic();s=MainWithRepertoire.load(a.parent)
    if s.tick!=1907:raise ValueError('Frozen extension requires actual1907 parent')
    parent_hash=hashlib.sha256(a.parent.read_bytes()).hexdigest();extension=s.attach_instruments(65)
    r={'schema':'CPC9.E1.repertoire.extension.measurements.v1','case_id':a.case,'status':'PREDICTIONS_WRITTEN',
       'preparations':0,'continuations':1,'continuity_type':'AUDITOR_COUNTERFACTUAL_CONTINUATION'if a.omit_events or a.unpaired else'MAIN_CONTINUATION',
       'parent':{'sha256':parent_hash,'path':str(a.parent),'identifier':s.identifier},'configuration':json.loads((ROOT/'configuraciones/E1_EXTENSION_K65_1907.json').read_text()),
       'instrumental_extension':extension,'MAIN_RAW_clock_edits':[],'frames':[],'snapshots':[],'auditor_experiences':[],'queries':[],'initial_physical':physical(s.world)}
    write(a.out/'MEDICIONES.json',r)
    captures={1907,1912,2152,2219,2286,2353};events={};off=1909
    for begin,end,t0 in((0,8,0),(8,16,80),(16,32,160),(32,65,240)):
        for index in range(begin,end):
            form=s.repertoire.geometry['forms'][index];sign=1 if index%2==0 else-1
            s.repertoire.input(form['ports']['cue'],5,off+t0+int(a.unpaired))
            if not a.omit_events:s.repertoire.input(form['ports']['event.plus'if sign==1 else'event.minus'],11,off+t0)
            r['auditor_experiences'].append({'form':form['id'],'actual_event_direction':[1,sign,0],'input_tick':off+t0,'omitted':a.omit_events,'unpaired':a.unpaired})
            count=0;t=off+t0+70
            while t<=2353:
                s.repertoire.input(form['ports']['read.plus'if count%2==0 else'read.minus'],7,t-3,True)
                q={'tick':t,'form':form['id'],'query_index':count,'hub':form['hub'],'expected_auditor_direction':[0,sign,1 if count%2==0 else 0]}
                r['queries'].append(q);events.setdefault(t,[]).append(q);captures.update((t-1,t));t+=67;count+=1
    for tick in(1957,2024,2091,2158,2225,2292):
        index=(tick-1957)//67
        for name in sorted({v['plus_port']if index%2==0 else v['minus_port']for v in s.geometry['cpc9_life']['count_repeated_readers']}):s.input(name,7,tick-3,'probe','OLD_COUNT_NO_RETEACHING_DURING65_EXTENSION')
        captures.add(tick)
    for tick in(1947,2014,2081,2148,2215,2282,2349):s.two_memory.input('quantity.reader',7,tick,True);captures.update((tick,tick+1))
    for tick in(1956,2023,2090,2157,2224,2291):
        for bank in s.geometry['joint_names'].values():s.input(bank['query_port'],17,tick-3,'probe','OLD_JOINT_NO_RETEACHING_DURING65_EXTENSION')
        captures.add(tick)
    for tick in sorted(captures):
        s.run_until(tick);r['frames'].append({'tick':tick,'physical':physical(s.world),'view':s.view(),
            'repertoire_queries':[{'form':q['form'],'query_index':q['query_index'],'expected_auditor_direction':q['expected_auditor_direction'],'physical':s.repertoire.observe(q['hub'])}for q in events.get(tick,[])]})
        if tick in(1907,1912,2152,2219,2353):
            path=a.out/f'T{tick}.deetsnap.gz';r['snapshots'].append({'path':path.name,'storage':s.save(path),'physical':physical(s.world),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        r.update(last_complete_tick=s.tick,requests=s.receipts(),elapsed_seconds=time.monotonic()-started,status='RUNNING');write(a.out/'MEDICIONES.json',r)
    r.update(status='MEASURED',final_physical=physical(s.world),parent_file_unchanged=hashlib.sha256(a.parent.read_bytes()).hexdigest()==parent_hash)
    write(a.out/'MEDICIONES.json',r)
    print(json.dumps({'case':a.case,'status':r['status'],'tick':s.tick,'preparations':0,'seconds':r['elapsed_seconds']}))
if __name__=='__main__':main()
