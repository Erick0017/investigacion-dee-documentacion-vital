"""Synthetic wrapper fixtures only; no SQLite, Native, owner or action."""
import argparse,copy,hashlib,importlib.util,json
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('--salida',type=Path,required=True);a=p.parse_args();source=Path(__file__).with_name('probar_asistente2_distribuido.py');s=importlib.util.spec_from_file_location('fixed_proof_only',source);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);rows=[{'modo':'apd02-acumular','valor':0,'demora_periodos':2}];identifier='FIXTURE_SAME_ID';payload=json.dumps({'operacion':'situaciones','situaciones':rows,'retorno':'omit','actuador':'closed'},sort_keys=True,separators=(',',':'));row={'id':identifier,'status':'queued','payload':payload,'payload_sha':hashlib.sha256(payload.encode()).hexdigest()};admission={'id':identifier,'admission':'queued','status':'waiting_or_processing','no_automatic_retry':True};cases=[]
    fixtures=[('real_row_after_summary',admission,{'request':row},True),('row_direct_not_wrapped',admission,row,True),('summary_alone_is_not_pending',admission,admission,False),('capacity_rejection_is_not_pending',{'admission':'rejected_capacity'},row,False),('processing_is_not_paused_queued',admission,{**row,'status':'processing'},False),('different_ID_is_not_same_pending',admission,{**row,'id':'OTHER'},False),('different_literal_payload_rejected',admission,{**row,'payload':'{}'},False),('bad_payload_sha_rejected',admission,{**row,'payload_sha':'0'*64},False)]
    for name,first,observed,expected in fixtures:
        try:value=m.queued_literal(copy.deepcopy(first),copy.deepcopy(observed),identifier,copy.deepcopy(rows));accepted=True;error=None
        except ValueError as exc:accepted=False;error=str(exc)
        cases.append({'name':name,'expected_accepted':expected,'accepted':accepted,'matches':accepted==expected,'error':error})
    result={'schema':'APD02.zero_wait_summary_vs_actual_row.synthetic.N0','helper_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':cases,'issues':[v['name']for v in cases if not v['matches']],'new_native_ticks':0,'owner_starts':0,'queue_reads_or_writes':0,'actions_requeued':0,'scope':'Synthetic admission/row validation only. A real incomplete native goal and a queued transport row remain separate assertions in the unchanged material proof.'}
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'fixtures':len(cases),'issues':result['issues'],'Native':0}));return bool(result['issues'])
if __name__=='__main__':raise SystemExit(main())

