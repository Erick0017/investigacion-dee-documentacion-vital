"""Post-trajectory extraction of the fixed1182 exploratory access panel."""
import hashlib
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'resultados/integracion'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path,value):
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()));temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)


def main():
    index=[];data=[]
    for path in sorted(BASE.glob('USE_*/MEASUREMENTS.json')):
        m=json.loads(path.read_text(encoding='utf8'))
        if m.get('status')!='MEASURED'or m.get('schema')!='CPC8.integration.right1182.measurements.v1':continue
        source_checks=[{'path':name,'declared':digest,'matches':(path.parent/'executed_source'/name).exists()and sha(path.parent/'executed_source'/name)==digest}for name,digest in m['executed_source'].items()]
        index.append({'case_id':m['case']['id'],'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'preparations':0,'continuations':1,'diagnostic_forks':0,
            'parent':m['parent'],'source_checks':source_checks,'snapshots':[{'path':(path.parent/x['path']).relative_to(ROOT).as_posix(),'sha256':x['sha256'],'exists':(path.parent/x['path']).exists()}for x in m['snapshots']]})
        data.append({'case_id':m['case']['id'],'role':m['case']['role'],'individual':m['parent']['individual'],'entry_tick':m['case']['entry_tick'],
            'query_contract':m['query_contract'],'explicit_query_input':m['explicit_query_input'],'readout1182':m['native_readout'],
            'retention1051':{k:v for k,v in m['retention1051'].items()if k!='exact_readouts'},'new_receipt_statuses':m['new_receipt_statuses'],
            'parent_file_preserved':m['parent_file_preserved']})
    result={'schema':'CPC8.integration.right1182.analysis.v1','data':data,'calculations':{'preparations':0,'controlled_continuations':len(index),
        'source_copies_checked':sum(len(x['source_checks'])for x in index),'source_copy_mismatches':sum(not s['matches']for x in index for s in x['source_checks'])},
        'provisional_reading':[
            'The same paired MAIN acquired newRIGHT786, retained all63previous accessible relations in the1051functional panel, and subsequently answered the explicitRIGHTquery1182 without re-teaching those old relations.',
            'The paired branch yields native(-1,-1,0),load25,value-1,withApplied receipt1179. The omitted-cue and equal-dose cue787/event786 controls yield only the load9probe(-1,0,0), withnullvalue andPROBE_ONLY_OR_INSUFFICIENT_LOAD. No silence/zero conflation is used.',
            'This is a single exploratory instrumental access cadence fixed before its three trajectories. It is not a new confirmatory reserve, autonomous query selection, recovered native whole-chain use or general65-way addressing.',
            'The third branch is another controlled continuation of the same690parent, not a new prepared body. Its own old-knowledge panel1051also retains63/63previous covered values.',
            'No further cadence, geometric family, cleanup or gate opening is used after these results. The earlier failed new-order admission and missing newRIGHTsocial delivery remain part of the evidence.']}
    put(BASE/'RIGHT_ACCESS_INDEX.json',{'schema':'CPC8.integration.right1182.index.v1','cases':index})
    put(BASE/'RIGHT_ACCESS_ANALYSIS.json',result);print(json.dumps(result['calculations']))


if __name__=='__main__':main()
