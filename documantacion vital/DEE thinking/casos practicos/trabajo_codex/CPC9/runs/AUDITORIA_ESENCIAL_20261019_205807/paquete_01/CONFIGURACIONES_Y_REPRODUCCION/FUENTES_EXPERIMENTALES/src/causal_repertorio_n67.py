"""Auditor cut/sham on one actually acquired travelling form, never MAIN edits."""
from pathlib import Path
from copy import deepcopy
import argparse,gc,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src')]
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from repertorio_n67 import N67RepertoireSession,move
from integracion.relational_pair import physical
from ejecutar_retorno import write

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',default='KN_D02_K65');p.add_argument('--out',required=True,type=Path);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    folder=ROOT/'resultados/repertorio_n67'/a.source;original=json.loads((folder/'MEDICIONES.json').read_text(encoding='utf8'))
    path=folder/'T310.deetsnap.gz';filehash=hashlib.sha256(path.read_bytes()).hexdigest()
    parent=N67RepertoireSession.load(path);before=physical(parent.world)
    form=parent.geometry['forms'][0];site=move(form['hub'],(0,1,0),39);actual=parent.observe(site)
    if not(actual['active']and actual['s_reg']==44 and actual['direction']==[0,1,0]):raise ValueError('No qualified actual F00 material at predicted310 location; cut disallowed')
    result={'schema':'CPC9.repertoire.N67.causal.v1','status':'PREDICTED','parent':str(path.relative_to(ROOT)),
        'parent_sha256':filehash,'site':site,'before':actual,'preparations':0,'diagnostic_forks':2,'technical_restored_continuations':1,
        'prediction_before_ticks':'Removing F00 acquired44 carrier at310 reduces its first338 qualified reading; the other64 remain readable. Sham/restore final444 full RAW/clocks/receipts match original. No fork result returns to operational world.',
        'rows':[]}
    write(a.out/'MEDICIONES.json',result)
    query_by_tick={}
    for q in original['queries']:
        if q['tick']>310:query_by_tick.setdefault(q['tick'],[]).append(q)
    for condition in('restore','cut_F00','sham_F00'):
        if condition=='restore':world=parent.world.fork()
        else:
            edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=0 if condition=='cut_F00'else int(actual['raw']);edit.clock=None;edit.label=condition
            world=parent.world.diagnostic_fork([edit],True)
        s=N67RepertoireSession(world,parent.geometry,deepcopy(parent.state))
        row={'condition':condition,'clock_preserved':s.observe(site)['clock']==actual['clock'],'queries':[]}
        for tick,queries in sorted(query_by_tick.items()):
            s.run_until(tick)
            row['queries'].extend({'tick':tick,'form':q['form'],'query_index':q['query_index'],'expected_auditor_direction':q['expected_auditor_direction'],'physical':s.observe(q['hub'])}for q in queries)
        s.run_until(444)
        row.update(final_physical=physical(world),full_final_equal=physical(world)==original['final_physical'],
            receipts_equal=s.receipts()==original['requests'],parent_unchanged=physical(parent.world)==before)
        if condition!='cut_F00'and not(row['full_final_equal']and row['receipts_equal']):raise AssertionError('Technical continuation mismatch')
        if not(row['clock_preserved']and row['parent_unchanged']):raise AssertionError('Audit contaminated clocks or parent')
        result['rows'].append(row);write(a.out/'MEDICIONES.json',result);del s,world;gc.collect()
    result.update(status='MEASURED',parent_file_unchanged=hashlib.sha256(path.read_bytes()).hexdigest()==filehash)
    write(a.out/'MEDICIONES.json',result)
    print(json.dumps({'status':result['status'],'conditions':[{'condition':v['condition'],'exact444':v['full_final_equal']}for v in result['rows']]}))
if __name__=='__main__':main()
