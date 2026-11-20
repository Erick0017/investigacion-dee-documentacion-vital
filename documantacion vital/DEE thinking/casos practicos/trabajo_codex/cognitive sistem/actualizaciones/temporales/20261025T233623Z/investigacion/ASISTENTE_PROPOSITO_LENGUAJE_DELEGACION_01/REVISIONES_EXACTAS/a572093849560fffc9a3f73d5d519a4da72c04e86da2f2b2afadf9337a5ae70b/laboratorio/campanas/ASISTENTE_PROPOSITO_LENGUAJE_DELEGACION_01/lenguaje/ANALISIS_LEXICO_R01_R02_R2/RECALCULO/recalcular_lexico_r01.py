"""Independent0tick RAW decoder and denominators for exported R01 primaries."""
import argparse,gzip,hashlib,json
from pathlib import Path

def decode(v):
    v=int(v)
    def signed(k):
        x=(v>>k)&15
        return x-16 if x&8 else x
    return {'state':v&0xffffffff,'s_reg':(v>>32)&65535,
            'direction':[signed(k) for k in (48,52,56)],'semantic':(v>>60)&15}

def read(path):
    b=path.read_bytes()
    return json.loads(gzip.decompress(b) if path.suffix=='.gz' else b)

def run(folder):
    protocol=read(folder/'PROTOCOLO_CONGELADO.json');rows=[];errors=[];nobs=0
    for case in protocol['cases']:
        path=folder/(case+'_01_PRIMARY.json.gz');p=read(path);r=p['result']
        summary={'case':case,'primary_file':path.name,'primary_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                 'life_id':p['INSTRUMENTO']['life_id'],'tick':p['physical']['tick'],
                 'snapshot_sha256':p['INSTRUMENTO']['snapshot_sha256'],'groups':{}}
        for group in ('first_queries','old_panel','post_old_queries'):
            qs=[]
            for qi,q in enumerate(r[group]):
                found=[]
                for o in q['reader']['panel']:
                    d=decode(o['raw']);nobs+=1
                    for key in d:
                        if d[key]!=o[key]:errors.append([case,group,qi,o['site'],'RAW_FIELD_DISAGREEMENT',key])
                    if d['state']>0 and d['semantic']==1 and d['direction']in ([0,0,-1],[0,0,1]):
                        found.append({'site':o['site'],'sign':d['direction'][2],'s_reg':d['s_reg']})
                output=found[0]['sign'] if len(found)==1 else None
                if found!=q['reader']['candidates'] or output!=q['reader']['formed_native_command']:
                    errors.append([case,group,qi,'FIXED_READER_DISAGREEMENT'])
                if len(q['reader']['panel'])!=(12 if group=='old_panel' else 16):
                    errors.append([case,group,qi,'GATE_COVERAGE_DISAGREEMENT'])
                for frame in q.get('frames',[]):
                    for o in frame['sites']:
                        d=decode(o['raw']);nobs+=1
                        if any(d[key]!=o[key] for key in d):errors.append([case,group,qi,'TRACE_RAW_DISAGREEMENT',o['site']])
                req=q['requests'];statuses=[x['receipt']['status'] for x in req]
                qs.append({'form':q.get('form',q.get('context_signal')),'output':output,
                           'ambiguous':len(found)>1,'input_tick':q['input_tick'],'read_tick':q['read_tick'],
                           'requested':len(req),'applied':statuses.count('applied'),
                           'rejected_or_other':len(statuses)-statuses.count('applied')})
                if group!='old_panel' and any(x['value'] not in (5,7) for x in req):
                    errors.append([case,group,qi,'UNEXPECTED_QUERY_CONTENT'])
            summary['groups'][group]=qs
        requests=[x for x in r['preparation']['requests']]
        summary['preparation']={'requested':len(requests),'applied':sum(x['receipt']['status']=='applied' for x in requests)}
        t_requests=[x for q in r['teaching'] for x in q['requests']]
        summary['teaching']={'requested':len(t_requests),'applied':sum(x['receipt']['status']=='applied' for x in t_requests),
                             'teacher_modes':[q['teacher_mode'] for q in r['teaching']]}
        if case in ('paired','reversed'):
            expected={'suma':1,'diferencia':-1}
            if case=='reversed':expected={k:-v for k,v in expected.items()}
            queries=[*summary['groups']['first_queries'],*summary['groups']['post_old_queries']]
            summary['correspondence']={'numerator':sum(q['output']==expected[q['form']] for q in queries),'denominator':len(queries),
                                       'scope':'Match to explicitly taught arbitrary physical sign, not general Spanish or task competence'}
        else:
            queries=[*summary['groups']['first_queries'],*summary['groups']['post_old_queries']]
            summary['control_outputs']={'valid':sum(q['output']in(-1,1) for q in queries),'none':sum(q['output']is None for q in queries),'denominator':len(queries)}
        old=summary['groups']['old_panel'];targets=protocol['old_last_observed_signs']
        summary['old_match_to_R17']={'numerator':sum(q['output']==sg for q,sg in zip(old,targets)),'denominator':len(old),
                                    'scope':protocol['old_target_scope']}
        rows.append(summary)
    return {'schema':'APD01.lexical_recalculation.R01','cases':rows,'raw_observations_decoded':nobs,
            'discrepancies':errors,'native_ticks_executed':0,
            'limits':'Recalculation of archived data, not native reproduction or a new independent biography. No native order/syntax claim.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--primarios',type=Path,required=True);p.add_argument('--salida',type=Path)
    a=p.parse_args();z=run(a.primarios);b=(json.dumps(z,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    if a.salida:
        with a.salida.open('xb')as f:f.write(b)
    print(json.dumps(z,ensure_ascii=False));raise SystemExit(bool(z['discrepancies']))
