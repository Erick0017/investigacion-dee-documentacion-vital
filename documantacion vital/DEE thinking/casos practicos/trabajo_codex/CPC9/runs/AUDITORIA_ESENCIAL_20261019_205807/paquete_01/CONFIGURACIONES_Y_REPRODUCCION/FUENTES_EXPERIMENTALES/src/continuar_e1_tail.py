"""After the adverse integrated65 challenge, continue rather than reset E1."""
from pathlib import Path
import argparse,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from vida_repertorio_extension import MainWithRepertoire
from integracion.relational_pair import physical
from ejecutar_retorno import write
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',required=True,type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--omit-new',action='store_true');a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);s=MainWithRepertoire.load(a.parent)
    if s.tick!=2353:raise ValueError('Exact selected2353 continuation required')
    started=time.monotonic();ph=hashlib.sha256(a.parent.read_bytes()).hexdigest()
    r={'schema':'CPC9.E1.post_interference.continuation.v1','case_id':'E1_TAIL_NO_NEW'if a.omit_new else'E1_MAIN_TAIL_2353_2493',
       'continuity_type':'AUDITOR_COUNTERFACTUAL_CONTINUATION'if a.omit_new else'MAIN_CONTINUATION','preparations':0,'continuations':1,
       'parent':{'sha256':ph,'path':str(a.parent),'identifier':s.identifier},'initial_physical':physical(s.world),
       'configuration':json.loads((ROOT/'configuraciones/E1_TAIL_2353_2491.json').read_text()),'MAIN_RAW_clock_edits':[],'frames':[],'snapshots':[],'status':'PREDICTIONS_WRITTEN'}
    write(a.out/'MEDICIONES.json',r)
    if not a.omit_new:
        for index,role in((0,'event.minus'),(64,'event.plus')):
            form=s.repertoire.geometry['forms'][index];s.repertoire.input(form['ports']['cue'],5,2354);s.repertoire.input(form['ports'][role],11,2354)
    for tick,role in((2424,'read.plus'),(2491,'read.minus')):
        for form in s.repertoire.geometry['forms']:s.repertoire.input(form['ports'][role],7,tick-3,True)
    for tick in(2416,2483):s.two_memory.input('quantity.reader',7,tick,True)
    for tick,role in((2426,'plus_port'),(2493,'minus_port')):
        for name in sorted({v[role]for v in s.geometry['cpc9_life']['count_repeated_readers']}):s.input(name,7,tick-3,'probe','OLD_COUNT_AFTER_INTERFERENCE_NO_RETEACHING')
    for tick in(2425,2492):
        for bank in s.geometry['joint_names'].values():s.input(bank['query_port'],17,tick-3,'probe','OLD_JOINT_AFTER_INTERFERENCE_NO_RETEACHING')
    for tick in(2353,2354,2357,2416,2417,2423,2424,2425,2426,2483,2484,2490,2491,2492,2493):
        s.run_until(tick);r['frames'].append({'tick':tick,'view':s.view(),'physical':physical(s.world),
           'repertoire':[{'id':f['id'],'physical':s.repertoire.observe(f['hub'])}for f in s.repertoire.geometry['forms']]})
        if tick in(2357,2424,2493):
            path=a.out/f'T{tick}.deetsnap.gz';r['snapshots'].append({'path':path.name,'storage':s.save(path),'physical':physical(s.world),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        r.update(last_complete_tick=tick,requests=s.receipts(),status='RUNNING',elapsed_seconds=time.monotonic()-started);write(a.out/'MEDICIONES.json',r)
    r.update(status='MEASURED',final_physical=physical(s.world),parent_file_unchanged=hashlib.sha256(a.parent.read_bytes()).hexdigest()==ph);write(a.out/'MEDICIONES.json',r)
    print(json.dumps({'status':r['status'],'tick':s.tick,'case':r['case_id'],'seconds':r['elapsed_seconds']}))
if __name__=='__main__':main()
