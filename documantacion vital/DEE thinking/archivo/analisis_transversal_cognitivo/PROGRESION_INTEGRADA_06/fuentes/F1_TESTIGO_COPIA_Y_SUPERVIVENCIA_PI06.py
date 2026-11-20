"""Find one bounded witness in closed R03 frames; no DEE import or execution."""
from pathlib import Path
from array import array
import argparse,hashlib,itertools,json,runpy,sys
P=Path(__file__).resolve().parent.parent
R=P.parents[2]
PRIMARY=P/'ensayos/PI06_AMBIENTE_NUBE_R06_AMBIENTE_NUBE.json'
CODEC=R/'archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_05/codigo/observador_global_PI05_R01.py'
OUT=P/'fuentes/F1_TESTIGO_COPIA_Y_SUPERVIVENCIA_PI06.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def fields(v):
    def nib(n):
        q=(v>>n)&15;return q-16 if q>=8 else q
    return{'RAW':str(v),'state':v&0xffffffff,'s_reg':(v>>32)&65535,
           'semantic':(v>>60)&15,'direction':[nib(48),nib(52),nib(56)]}
def uints(b):
    a=array('Q');a.frombytes(b)
    if sys.byteorder!='little':a.byteswap()
    return a
def find_witness():
    if OUT.exists():raise FileExistsError('Preserve existing witness')
    pb=PRIMARY.read_bytes();x=json.loads(pb)
    while isinstance(x,str)or isinstance(x,dict)and'result'in x:
        x=json.loads(x)if isinstance(x,str)else x['result']
    row=x['rows'][0];cap=row['external_global_capture'];directory=Path(cap['directory'])
    assert sha((directory/'INDEX.json').read_bytes())==cap['index_sha256']
    assert sha(CODEC.read_bytes())=='d60d58301fd29ae0aabf577adc2d6f82392ed42f1d691890d095873cdf80f8d6'
    module=runpy.run_path(str(CODEC),run_name='pure_closed_record_codec')
    requests=[v for v in row['requests']if v['receipt']['status']=='applied']
    before={tuple(v['site']):v['observation']for v in row['source_observations_before']}
    assert len(requests)==58 and all(v['receipt']['effective_tick']==826451 for v in requests)
    moore=[d for d in itertools.product((-1,0,1),repeat=3)if d!=(0,0,0)]
    previous=None;witness=None;frames_examined=[];checks=0
    for f in module['iter_frames'](directory):
        if f['tick']>826459:break
        n=f['config']['N'];raw=uints(f['raw_bytes']);clocks=uints(f['clocks_bytes'])
        current={'frame':f,'raw':raw,'clocks':clocks};frames_examined.append({'tick':f['tick'],'hashes':f['hashes']})
        def index(site):return(site[0]*n+site[1])*n+site[2]
        if previous and 826452<=previous['frame']['tick']and f['tick']==previous['frame']['tick']+1:
            a=previous['raw'];b=raw
            for req in requests:
                p=tuple(req['site']);v=a[index(p)];fv=fields(v)
                if not(fv['state']>0 and fv['semantic']==1 and fv['s_reg']==7 and any(fv['direction'])):continue
                dest=tuple((p[k]+fv['direction'][k])%n for k in range(3));j=index(dest);after=fields(b[j]);survivor=fields(b[index(p)])
                if a[j]!=0 or not(after['state']==1 and after['s_reg']==7 and after['semantic']==1 and after['direction']==fv['direction']and survivor['state']>0):continue
                neighbours=[];incoming=[];active={}
                for delta in moore:
                    q=tuple((dest[k]+delta[k])%n for k in range(3));ff=fields(a[index(q)]);alive=ff['state']>0 and ff['semantic']!=5;active[delta]=alive
                    nn={'site':list(q),'offset_from_destination':list(delta),'clock':str(previous['clocks'][index(q)]),**ff};neighbours.append(nn)
                    if any(ff['direction'])and all((q[k]+ff['direction'][k])%n==dest[k]for k in range(3)):incoming.append(nn)
                checks+=1;symmetric=sum(active[d]==active[tuple(-v for v in d)]for d in moore)//2
                xnor=symmetric==13 and sum(active.values())>=8
                if len(incoming)!=1 or incoming[0]['site']!=list(p)or xnor:continue
                witness={'from_tick':previous['frame']['tick'],'to_tick':f['tick'],'source_request':req,
                    'source_initial_observation':before[p], 'source_site':list(p),'destination_site':list(dest),
                    'source_before':fv,'source_after':survivor,'destination_before':fields(a[j]),'destination_after':after,
                    'source_before_clock':str(previous['clocks'][index(p)]),'source_after_clock':str(clocks[index(p)]),
                    'destination_before_clock':str(previous['clocks'][j]),'destination_after_clock':str(clocks[j]),
                    'unique_incoming_directional_sources':incoming,'Moore26_before_complete':neighbours,
                    'XNOR_before':{'symmetric_pairs':symmetric,'active_neighbours':sum(active.values()),'condition':xnor},
                    'before_hashes':previous['frame']['hashes'],'after_hashes':f['hashes']}
                break
        if witness:break
        previous=current
    result={'schema':'DEE.PI06.one_local_copy_and_survival_witness.v1','Native_ticks_executed':0,
        'primary':{'path':str(PRIMARY),'bytes':len(pb),'sha256':sha(pb)},'capture_index_sha256':cap['index_sha256'],
        'frames_examined':frames_examined,'candidate_contact_checks':checks,'witness_found':witness is not None,'witness':witness,
        'scope':'One observed local event after all58 legal inputs. Under the identified frozen source, a vacant destination with unique directional source and falseXNOR follows the directed-source branch. Source survival and destinationformation coexist; this is not a conserved-particle lineage or an explanation of all growth.',
        'limitations':['No Native replay, new query, kernel execution or change.',
        'Matching payload is not source identity; the complete pre-neighbourhood and unique incoming geometry establish only the local branch compatibility.',
        'No attribution of allSEM1/SEM7growth, autonomous regulation or learning follows from this witness.']}
    with OUT.open('x',encoding='utf-8')as out:json.dump(result,out,ensure_ascii=False,indent=2)
    print(json.dumps({'file':str(OUT),'sha256':sha(OUT.read_bytes()),'witness_found':witness is not None,'from_tick':witness['from_tick']if witness else None,'source':witness['source_site']if witness else None,'destination':witness['destination_site']if witness else None,'frames':len(frames_examined),'Native_ticks':0}))
def portable(evidence,output):
    if output.exists():raise FileExistsError('New output required')
    data=evidence.read_bytes();d=json.loads(data);w=d['witness'];assert d['witness_found']
    n=67;dest=w['destination_site'];source=w['source_site'];rows=w['Moore26_before_complete']
    assert len(rows)==26 and len({tuple(r['offset_from_destination'])for r in rows})==26
    expected=set(itertools.product((-1,0,1),repeat=3))-{(0,0,0)}
    assert {tuple(r['offset_from_destination'])for r in rows}==expected
    incoming=[];active={}
    for r in rows:
        q=r['site'];v=int(r['RAW']);f=fields(v);assert all(f[k]==r[k]for k in('state','s_reg','semantic','direction'))
        delta=tuple(r['offset_from_destination']);assert q==[(dest[k]+delta[k])%n for k in range(3)]
        active[delta]=f['state']>0 and f['semantic']!=5
        if any(f['direction'])and all((q[k]+f['direction'][k])%n==dest[k]for k in range(3)):incoming.append(r)
    symmetric=sum(active[a]==active[tuple(-x for x in a)]for a in active)//2;xnor=symmetric==13 and sum(active.values())>=8
    assert len(incoming)==1 and incoming[0]['site']==source and not xnor
    assert w['destination_before']['RAW']=='0'and w['source_before']['s_reg']==7 and w['source_before']['semantic']==1
    assert w['source_after']['state']>0 and w['destination_after']['state']==1 and w['destination_after']['s_reg']==7 and w['destination_after']['direction']==w['source_before']['direction']
    result={'schema':'DEE.PI06.local_witness.portable_recalculation.v1','evidence_sha256':sha(data),
        'Native_ticks':0,'reads_original_capture':False,'Moore26_complete':True,'unique_incoming_source':source,
        'XNOR_condition':xnor,'symmetric_pairs':symmetric,'active_neighbours':sum(active.values()),
        'vacant_destination_forms_expected_source_signature':True,'source_remains_active':True,
        'scope':'Local field/geometry recalculation only; original full-buffer hashes are verified separately by the global portable bundle. Not Native reproduction or particle lineage.'}
    with output.open('x',encoding='utf-8')as out:json.dump(result,out,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--recalcular-portable',action='store_true');ap.add_argument('--evidence',type=Path);ap.add_argument('--out',type=Path);a=ap.parse_args()
    if a.recalcular_portable:
        if a.evidence is None or a.out is None:ap.error('--evidence and --out required')
        portable(a.evidence,a.out)
    else:find_witness()
