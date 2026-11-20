"""Portable N0 audit of archived baseline and lexical physical witnesses."""
import argparse,gzip,hashlib,json
from pathlib import Path

def read(p):return json.loads(gzip.decompress(Path(p).read_bytes()))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def examine(value,path='',counts=None,issues=None,receipts=None):
    counts=counts if counts is not None else{'raw_observations':0};issues=issues if issues is not None else[];receipts=receipts if receipts is not None else{}
    if isinstance(value,dict):
        if 'raw'in value and all(k in value for k in('state','s_reg','semantic','direction')):
            n=int(value['raw']);counts['raw_observations']+=1
            dr=[((n>>s)&15)-(16 if((n>>s)&15)>=8 else 0)for s in(48,52,56)]
            if not 0<=n<2**64 or(n&0xffffffff)!=value['state']or((n>>32)&65535)!=value['s_reg']or((n>>60)&15)!=value['semantic']or dr!=value['direction']:issues.append({'path':path,'issue':'RAW field mismatch'})
            if 'clock'in value and not 0<=int(value['clock'])<2**64:issues.append({'path':path,'issue':'Invalid uint64 clock'})
        if 'receipt'in value and isinstance(value['receipt'],dict)and'id'in value:
            key=int(value['id']);r=value['receipt'];old=receipts.get(key)
            if old is not None and old!=r:issues.append({'path':path,'issue':'Conflicting receipt for same native ID'})
            receipts[key]=r
        for k,v in value.items():examine(v,path+'/'+str(k),counts,issues,receipts)
    elif isinstance(value,list):
        for i,v in enumerate(value):examine(v,path+'/'+str(i),counts,issues,receipts)
    return counts,issues,receipts
def witness(value):
    counts,issues,rs=examine(value)
    statuses={}
    for r in rs.values():statuses[r['status']]=statuses.get(r['status'],0)+1
    return{**counts,'native_unique_receipts':len(rs),'receipt_statuses':statuses,'issues':issues}
def audit_baseline(path):
    d=read(path);records=d['records'];old=records['apd02b_old6_parsed']['result']['rows'];forms=records['apd02b_forms6_parsed']['result']['rows'];count=records['apd02b_count_parsed']['result']['rows'][0]
    old_expected={'alfa':-1,'beta':-1,'gamma':1,'delta':-1,'epsilon':-1,'zeta':1}
    old_rows=[{'context':r['result']['rows'][0]['context_signal'],'choice':r['result']['rows'][0]['reader']['formed_native_command']}for r in old]
    form_rows=[]
    for r in forms:
        nr=r['native_numeric']['numeric_reader'];raw=int(nr['observation']['raw']);v=((raw>>32)&65535)-nr['representation_bias']if nr['fixed_site_direction_valid']else None
        a,b=r['raw_operands'];semantic='add'if r['literal_form']in('suma','agrega','total')else'sub';expected=a+b if semantic=='add'else a-b
        form_rows.append({'form':r['literal_form'],'word_sign':r['native_operator_command'],'route':r['native_route_command'],'recalculated_from_RAW':v,'reported':r['numeric_result'],'mathematically_correct_for_original_form':v==expected,'artifact_exists_recorded':r['completed'],'read_tick':nr['tick']})
    parsed=[v['result']for k,v in records.items()if k.endswith('_parsed')];return{'source':str(path),'sha256':sha(path),'life':d['life'],'ticks':[d['initial']['physical']['tick'],d['final']['physical']['tick']],'old':old_rows,'old_matching':sum(x['choice']==old_expected[x['context']]for x in old_rows),'old_total':6,'forms':form_rows,'forms_correct':sum(x['mathematically_correct_for_original_form']for x in form_rows),'forms_total':6,'count':count['numeric_reader']['numeric_result'],'witness':witness(parsed),'scope':'Material diagnostic copy, not MAIN and not independent learners.'}
def audit_language(path):
    d=read(path);rows=[];expected=[-1,-1,1,-1,-1,1,1,-1,1,-1,1,-1]
    for r in d['rows']:
        before=[q['reader']['formed_native_command']for q in r['old_before']];after=[q['reader']['formed_native_command']for q in r['old_after']]
        uses=[]
        for q in r['uses']:
            interaction=q['interaction'];reader=interaction.get('reader',{})if interaction else{}
            uses.append({'literal':q['literal_form'],'native_function':q['native_function_choice'],'function_executed':interaction is not None,'actual_result':reader.get('choice',reader.get('formed_native_command')),'word_read_tick':q['word']['read_tick']})
        rows.append({'arm':r['arm'],'old_before_matching':sum(x==y for x,y in zip(before,expected)),'old_after_matching':sum(x==y for x,y in zip(after,expected)),'old_total':12,'old_before':before,'old_after':after,'uses':uses,'witness':witness(r),'final':r['final']})
    return{'source':str(path),'sha256':sha(path),'rows':rows,'scope':'Six dependent full-snapshot physical AUX branches; generic word-to-function dispatch is prepared, signs are taught. History-specific access interference is not a proof of global erasure.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--lenguaje',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();out={'schema':'APD02.repertoire_recalculation.N0.R1','new_native_ticks':0,'baseline':audit_baseline(a.baseline),'language':audit_language(a.lenguaje)}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps({'out':str(a.salida),'baseline':{k:out['baseline'][k]for k in('old_matching','old_total','forms_correct','forms_total','count')},'language':[(r['arm'],r['old_before_matching'],r['old_after_matching'],r['uses'])for r in out['language']['rows']]},ensure_ascii=False))
if __name__=='__main__':main()
