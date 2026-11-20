"""Portable worker-interruption verification; no DEE import or execution."""
import argparse,gzip,hashlib,json,struct
from pathlib import Path


def canonical(q):return json.dumps(q,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
def load(path):return json.loads(gzip.decompress(path.read_bytes())if path.suffix=='.gz'else path.read_bytes())
def calc(root):
    d=load(root/'INTERRUPCION.json.gz');physical=load(root/'ESTADOS_FINALES.json.gz');checks={};sources=[];summary=[];raw_count=0
    def check(label,value):checks[label]=bool(value)
    for name in('INTERRUPCION.json.gz','ESTADOS_FINALES.json.gz','PREPARACION.json'):
        b=(root/name).read_bytes();sources.append({'file':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    for key,f in physical['frames'].items():
        size=f['N']**3;raw=[0]*size;clocks=[int(f['clock_default'])]*size
        for index,value in f['raw_nonzero']:raw[index]=int(value)
        for index,value in f['clock_exceptions']:clocks[index]=int(value)
        for label,values in(('RAW',raw),('clocks',clocks)):
            if any(type(v)is not int or not 0<=v<2**64 for v in values):raise ValueError('Exact uint64 required')
            digest=hashlib.sha256(b''.join(struct.pack('<Q',v)for v in values)).hexdigest();raw_count+=len(values)
            check(key+'_'+label,digest==f[label+'_sha256'])
    for arm in d['arms']:
        label=arm['label'];cut=arm['cut_after_actual_output'];check(label+'_no_harness_error','error'not in arm)
        before=arm['actual_file_before_cut'];partial=arm['partial_worker_receipt'];actual=(root/arm['exported_actual_worker_output']['file']).read_bytes()
        check(label+'_actual_written_bytes',partial['actual_write_and_readback_already_occurred']and len(actual)==before['bytes']==partial['output_bytes']and hashlib.sha256(actual).hexdigest()==before['sha256']==partial['output_sha256'])
        initial=arm['initial_owner'];later=arm['after_reload'];first=arm['after_stop'];terminal=arm['work_terminal'];payload=json.loads(terminal['payload'])
        check(label+'_literal_payload_identity',hashlib.sha256(canonical(payload)).hexdigest()==terminal['payload_sha'])
        check(label+'_explicit_generic_public_work',payload=={'operacion':'sesion','situaciones':[{'modo':'trabajo','valores':[3,11]}],'retorno':'omit'})
        check(label+'_one_actual_native_advance',later['tick']==first['tick']==initial['tick']+11)
        check(label+'_output_not_duplicated_or_changed',arm['output_files_after_first_process']==arm['output_files_after_reload'])
        check(label+'_same_id_deduplicated',arm['duplicate_same_id']['admission']=='existing_same_transport_request')
        check(label+'_same_terminal_after_reload',arm['work_after_reload']['status']==terminal['status'])
        check(label+'_reload_no_idle_or_material_replay',later['physical']==first['physical']and later['material_calls']==first['material_calls']and later['idle_ticks']==initial['idle_ticks'])
        check(label+'_paused_and_stopped',later['paused']and not later['running'])
        check(label+'_expected_protocol_outcome',terminal['status']==('uncertain'if cut else'completed')and later['uncertain_external_result']==cut)
        f=next(x for x in physical['arms']if x['label']==label);check(label+'_full_field_witness_matches_receipt',f['physical']['RAW_sha256']==later['physical']['RAW_sha256']and f['physical']['clocks_sha256']==later['physical']['clocks_sha256'])
        summary.append({'label':label,'native_tick':later['tick'],'external_output_bytes':len(actual),'terminal_status':terminal['status'],'paused':later['paused'],'uncertain':later['uncertain_external_result'],'second_process_no_retry':True})
    check('matched_final_RAW_and_clocks_not_complete_causal_state',len({a['frame_key']for a in physical['arms']})==1)
    return {'schema':'DEE.unified.worker_interrupt_recalculation.v1','sources':sources,'complete_uint64_checked':raw_count,'checks':checks,'issues':[k for k,v in checks.items()if not v],'arms':summary,
        'scope':'Recalculation of archived actual files/receipts/full RAW/clocks. NOT native reproduction, learning or equality of complete causal state; CUT and SHAM differ in external acknowledgement and protocol uncertainty.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();result=calc(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'issues':result['issues'],'complete_uint64':result['complete_uint64_checked']}));return bool(result['issues'])
if __name__=='__main__':raise SystemExit(main())
