"""Portable archived calculation: no DEE import, native ticks or host targets.
Reconstructs decoded emissions and tool-byte consequences from primary records.
"""
import argparse,base64,collections,gzip,hashlib,json,zlib
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def raw_fields(raw):
    n=int(raw);dirs=[]
    if not 0<=n<1<<64:raise ValueError('RAW outside uint64')
    for bit in(48,52,56):
        v=(n>>bit)&15;dirs.append(v-16 if v&8 else v)
    return {'state':n&0xffffffff,'s_reg':(n>>32)&0xffff,'semantic':(n>>60)&15,'direction':dirs}
def walk(x,path='$'):
    yield path,x
    if isinstance(x,dict):
        for k,v in x.items():
            if k not in('stdout','stderr'):yield from walk(v,path+'.'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from walk(v,path+'['+str(i)+']')
def recalc(folder):
    out={'schema':'MUFI01.archived_main_A.v1','native_ticks_executed':0,'files':[],'cases':[],'errors':[],
         'raw_observations_checked':0,'readers_reconstructed':0,'worker_byte_checks':0,'scope':'Archived arithmetic/decoding only; no native reproduction or new acquisition.'}
    for p in sorted(folder.glob('A*.json.gz')):
        b=p.read_bytes();j=json.loads(gzip.decompress(b));out['files'].append({'name':p.name,'bytes':len(b),'sha256':sha(b)})
        r=j.get('result')
        if not isinstance(r,dict):
            out['cases'].append({'case':j.get('case',p.name),'returncode':j.get('returncode'),'result':'instrumental_error_or_nonresult','stderr':j.get('stderr')});continue
        root=r.get('result',{});rows=root.get('rows',[])if isinstance(root,dict)else[]
        case={'case':j.get('case',p.name),'returncode':j.get('returncode'),'rows':[],'requested':0,'receipts':collections.Counter()}
        for loc,x in walk(root):
            if not isinstance(x,dict):continue
            if all(k in x for k in('raw','state','s_reg','semantic','direction')):
                d=raw_fields(x['raw']);out['raw_observations_checked']+=1
                for k,v in d.items():
                    if x[k]!=v:out['errors'].append({'file':p.name,'location':loc,'field':k,'expected':v,'recorded':x[k]})
            if 'receipt'in x and isinstance(x['receipt'],dict)and('id'in x or 'channel'in x or 'port'in x):
                case['requested']+=1;case['receipts'][x['receipt']['status']]+=1
            if 'panel'in x and 'formed_native_command'in x:
                cs=[]
                for o in x['panel']:
                    z=raw_fields(o['raw'])
                    if z['state']>0 and z['semantic']==1 and z['direction']in[[0,0,-1],[0,0,1]]:cs.append(z['direction'][2])
                expected=cs[0]if len(cs)==1 else None;out['readers_reconstructed']+=1
                if expected!=x['formed_native_command']:out['errors'].append({'file':p.name,'location':loc,'reader':'pureZ','expected':expected,'recorded':x['formed_native_command']})
            if 'observations'in x and 'choice'in x and len(x['observations'])==3:
                cs=[]
                for sign,o in zip((-1,0,1),x['observations']):
                    z=raw_fields(o['raw'])
                    if z['state']>0 and z['semantic']==1 and z['direction']==[sign,1,0]:cs.append(sign)
                expected=cs[0]if len(cs)==1 else None;out['readers_reconstructed']+=1
                if expected!=x['choice']:out['errors'].append({'file':p.name,'location':loc,'reader':'selectorXY','expected':expected,'recorded':x['choice']})
            if x.get('schema')=='EO02.local_worker.receipt.v2':
                vs=x['raw_observations'];payload=bytes(vs)*max(1,32+sum(vs[::2]))
                if x['operation']=='verify_commit':
                    # This receipt need not repeat the earlier input. Check the
                    # exact pending artifact separately when its bytes exist.
                    continue
                data=zlib.compress(payload,9)if x['worker']==1 else hashlib.sha256(payload).digest()
                checks={'input_bytes':len(payload),'input_sha256':sha(payload),'output_bytes':len(data),'output_sha256':sha(data),
                        'accepted':x['worker']==(1 if sum(vs[::2])+x['modelled_capacity_credit_not_actor_input']>=sum(vs[1::2])else-1)}
                out['worker_byte_checks']+=1
                for k,v in checks.items():
                    if x[k]!=v:out['errors'].append({'file':p.name,'location':loc,'worker_field':k,'expected':v,'recorded':x[k]})
        for x in rows:
            reader=x.get('reader',{});ext=x.get('external',{})
            case['rows'].append({'kind':x.get('kind'),'context':x.get('context_signal'),'choice':reader.get('choice',reader.get('formed_native_command')),
              'worker':ext.get('executed_worker',ext.get('executed_action')),'completed':ext.get('opportunity_completed'),
              'feedback_tick':(ext.get('return')or{}).get('arrival_tick'),'worker_accepted':(ext.get('worker_receipt')or{}).get('accepted')})
        case['receipts']=dict(case['receipts']);out['cases'].append(case)
    by={c['case']:c for c in out['cases']}
    def choices(n):return[c['choice']for c in by.get(n,{}).get('rows',[])]
    out['decisive_contrasts']={
      'first_five':choices('A03_PRIMER_USO_CINCO'),
      'six_after_addition':choices('A13_MAIN_PRIMER_PANEL'),
      'six_after_selective_revision':choices('A15_MAIN_RETENCION_TRAS_REVISION'),
      'six_after_actual_prepare_commit':choices('A24_MAIN_REUSO_TRAS_COMMIT'),
      'no_experience_zeta_first_then_old':choices('A11_U_PRIMER_PANEL'),
      'same_untrained_history_old_first':choices('A22_U_ANTERIORES_PRIMERO_CORREGIDO'),
      'resources_without_cue_vs_none':[choices('A26_PANEL_MU_GENERIC_BOTH'),choices('A26_PANEL_MU_GENERIC_NONE')],
      'main_own_consequence_choices':choices('A42_MAIN_DOS_CONSECUENCIAS')+choices('A45_MAIN_RESERVAS_UTILES'),
      'main_reserved_actual_useful':sum(c['completed']is True for c in by.get('A45_MAIN_RESERVAS_UTILES',{}).get('rows',[])),
      'omitted_reserved_actual_useful':sum(c['completed']is True for c in by.get('A46_U_RESERVAS_UTILES',{}).get('rows',[])),
      'common_reserved_opportunities_per_arm':len(by.get('A45_MAIN_RESERVAS_UTILES',{}).get('rows',[])),
      'old_six_after_consequence_learning':choices('A47_MAIN_RETENCION_SEIS')}
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidencia',type=Path,default=Path(__file__).resolve().parent.parent/'EVIDENCIA_A');ap.add_argument('--salida',type=Path);args=ap.parse_args()
    result=recalc(args.evidencia)
    text=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
    if args.salida:args.salida.write_text(text,encoding='utf8')
    else:print(text)
    if result['errors']:raise SystemExit(2)
if __name__=='__main__':main()
