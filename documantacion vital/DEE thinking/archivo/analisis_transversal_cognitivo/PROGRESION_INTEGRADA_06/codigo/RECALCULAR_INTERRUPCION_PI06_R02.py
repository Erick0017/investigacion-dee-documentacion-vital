"""Small causal-primary recount plus exactlybounded offline frame inspection."""
from pathlib import Path
from array import array
import hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1]
OBSERVER=P.parents[2]/'DEE Cognitive 2.0/sistema/capacidades/observador_global_PI05_R01.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def fields(v):
    ds=[(v>>s)&15 for s in(48,52,56)]
    return {'RAW':str(v),'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':v>>60,
        'direction':[x-16 if x&8 else x for x in ds]}
def frames(module,capture,limit):
    path=Path(capture['directory']).resolve(strict=True)
    if not path.is_relative_to(P.resolve())or sha(path/'INDEX.json')!=capture['index_sha256']:raise ValueError('Exact currentcapture only')
    result=[];gen=module.iter_frames(path)
    try:
        for frame in gen:
            raw=array('Q');clock=array('Q');raw.frombytes(frame['raw_bytes']);clock.frombytes(frame['clocks_bytes'])
            if sys.byteorder!='little':raw.byteswap();clock.byteswap()
            site=[52,48,50];i=(site[0]*67+site[1])*67+site[2]
            line=[]
            for z in range(47,54):
                j=(52*67+48)*67+z
                if raw[j]:line.append({'site':[52,48,z],'clock':int(clock[j]),**fields(raw[j])})
            result.append({'tick':frame['tick'],'hashes':frame['hashes'],
                'contact':{'site':site,'clock':int(clock[i]),**fields(raw[i])},'line_z47_53_nonzero_RAW':line})
            if len(result)>=limit:break
    finally:gen.close()
    return {'inspected_frames':len(result),'total_frames_reported_by_index':capture['captured_frames'],
        'full_record_exhaustively_reconstructed':len(result)==capture['captured_frames'],
        'selection':'First4interruptionframes or first2originalFIframes, fixed before thisrecalculation; no favorableframe search.',
        'frames':result}
def main():
    spec=importlib.util.spec_from_file_location('PI06_offline_causal_codec',OBSERVER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    cases=[]
    for name in('PI06_CUT_CONTRA_R02.json','PI06_CUT_SHAM_R02.json'):
        path=P/'control'/name;proof=read(path)
        if proof['status']!='CLOSED'or not proof['closed']or proof['initial_tick']!=826449 or proof['final_tick']!=826650:raise ValueError('Both fullformed-source pairedexperiments must be coherentlyclosed')
        ids={};rows=[]
        for i,outcome in enumerate(proof['outcomes']):
            primary_path=Path(outcome['primary']).resolve(strict=True)
            if not primary_path.is_relative_to(P.resolve())or sha(primary_path)!=outcome['primary_sha256']:raise ValueError('Actualprimary differs')
            transport=read(primary_path)
            if transport['status']!='completed'or transport.get('error')is not None:raise ValueError('Ambiguoustransport is not accepted')
            actual=json.loads(transport['result']);rs=actual['result']['rows']
            if len(rs)!=1:raise ValueError('One scientificrow perrequest')
            row=rs[0]
            for request in row['requests']:
                rid=request['id']
                if rid in ids and ids[rid]!=request:raise ValueError('ConflictingNativealias')
                ids[rid]=request
            counts=row['Native_inputs'];expected=1 if i==0 else 176
            if counts['unique_requested']!=expected or counts['applied']!=expected or counts['rejected_or_other']!=0:raise ValueError('Exact177appliedinputs are required for the matchedcausalinterpretation')
            entry={'before_tick':row['before_tick'],'after_tick':row['after_tick'],'Native_inputs':counts,
                'primary':str(primary_path),'primary_sha256':sha(primary_path),
                'capture_inspection':frames(module,row['external_global_capture'],4 if i==0 else 2)}
            if i==0:
                r=row['requests'][0]
                if r['site']not in([52,48,51],[60,48,51])or r['direction']!=[0,0,-1]or r['tick']!=826451 or r['payload']!=0:raise ValueError('Fixedlegalcounter/sham input changed')
                entry.update({'condition':row['condition'],'actual_request':r,'before':row['observations_before'],'after':row['observations_after']})
            else:
                if row['calendar']['query_tick']!=826508:raise ValueError('Actualphase not matched')
                entry.update({'q':row['calendar']['query_tick'],'q4':row['early_physical_choice'],'q6':row['old_q6_choice'],'calendar':row['calendar']})
            rows.append(entry)
        if len(rows)!=2 or len(ids)!=177 or proof['new_ticks']!=201:raise ValueError('Exacttwo-step201ticktrial required')
        cases.append({'life_id':proof['life_id'],'proof':str(path),'proof_sha256':sha(path),'Native_ticks':201,
            'unique_requested':len(ids),'applied':sum(x['receipt']['status']=='applied'for x in ids.values()),'rows':rows})
    output=P/'control/RECALCULO_CAUSAL_INTERRUPCION_PI06_R02.json'
    value={'schema':'DEE.PI06.formed_carrier_interruption.documentary_recount.R02','cases':cases,
        'Native_executed':False,'new_Native_ticks':0,'full_buffers_reconstructed_frames':sum(r['capture_inspection']['inspected_frames']for c in cases for r in c['rows']),
        'coverage':'8interruptionframes fullyverified plus4earlyFIframes; the remainingFIframes are not declared inspected by thisscript.',
        'interpretation':'The sameagedose and fixedreader yield differentresponses after a legalcounterflow versus off-pathsham. The contactstate and its subsequentNativeevolution support a localcausalinterruption of the formedprocess. This is an externaldiagnostic, not an acquiredrepair, autonomousprotection or uniqueancestry proof.',
        'not_an_experimental_reproduction':True,'original_whole_states_preserved_by_Root':True}
    with output.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':output.name,'sha256':sha(output),'frames':value['full_buffers_reconstructed_frames'],
        'cases':[{'life':c['life_id'],'condition':c['rows'][0]['condition'],'q4':c['rows'][1]['q4'],'q6':c['rows'][1]['q6'],
            'contact_interruption':c['rows'][0]['capture_inspection']['frames'][-1]['contact'],
            'first2FIcontact':[x['contact']for x in c['rows'][1]['capture_inspection']['frames']]}for c in cases],
        'Native_executed':False}))
if __name__=='__main__':main()
