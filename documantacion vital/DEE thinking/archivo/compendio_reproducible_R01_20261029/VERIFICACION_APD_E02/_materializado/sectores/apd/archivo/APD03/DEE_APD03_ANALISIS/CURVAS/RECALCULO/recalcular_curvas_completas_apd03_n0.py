"""Portable primary RAW/receipt recalculation for APD03 lexical AUX R01-R03.

No Native imports, restores or ticks. Serialized-state equality receipts are
identified as source proofs when their complete snapshots are omitted.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

I=(33,33,33);J=(47,47,47);H=(47,17,47);K=(47,7,47);N=67
FI={'alfa':(1,0,0),'beta':(0,1,0),'gamma':(1,1,0),'delta':(-1,1,0),
    'epsilon':(1,-1,0),'zeta':(-1,-1,0),'suma':(-1,0,0),'diferencia':(0,-1,0)}
FJ={'agrega':(-1,0,0),'resta':(0,-1,0),'total':(1,0,0),'quita':(0,1,0)}
FH={'compara':(1,0,0),'recuerda':(0,1,0)};FK={'luma':(-1,0,0),'nara':(0,-1,0)}
FORMS={**{f:(I,v)for f,v in FI.items()},**{f:(J,v)for f,v in FJ.items()},
       **{f:(H,v)for f,v in FH.items()},**{f:(K,v)for f,v in FK.items()}}


def read(path):
    data=Path(path).read_bytes();return json.loads(gzip.decompress(data)if Path(path).suffix=='.gz'else data)


def fields(raw):
    def signed(shift):
        value=(raw>>shift)&15;return value-16 if value&8 else value
    return {'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,
        'semantic':(raw>>60)&15,'direction':[signed(shift)for shift in(48,52,56)]}


def pos(origin,v,k,z):return tuple((origin[i]+k*v[i]+(z if i==2 else 0))%N for i in range(3))


def walk(value,path='$'):
    if isinstance(value,dict):
        yield path,value
        for key,item in value.items():yield from walk(item,path+'.'+str(key))
    elif isinstance(value,list):
        for index,item in enumerate(value):yield from walk(item,path+'['+str(index)+']')


def hmeta(values):return hashlib.sha256(json.dumps(values,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()


def calculate(evidence):
    evidence=Path(evidence);checks=0;raw_count=0;decoded_queries=0;issues=[]
    def check(condition,message):
        nonlocal checks
        checks+=1
        if not condition:issues.append(message)
    def validate_raw(primary,label):
        nonlocal raw_count
        for path,item in walk(primary):
            if 'raw'in item and all(k in item for k in('state','s_reg','semantic','direction')):
                raw=int(item['raw']);expected=fields(raw)
                check(0<=raw<1<<64,label+path+': uint64')
                for key,value in expected.items():check(item[key]==value,label+path+': '+key)
                if 'clock'in item:check(0<=int(item['clock'])<1<<64,label+path+': clock uint64')
                raw_count+=1
    def decode_query(query,label,*,legacy=False,memory_only=False):
        nonlocal decoded_queries
        if memory_only:codec={k:v for k,v in FORMS.items()if k in('alfa','beta','gamma','delta','epsilon','zeta')}
        else:codec={k:v for k,v in FORMS.items()if not legacy or k not in FK}
        expected={pos(origin,v,4,sign):sign for origin,v in codec.values()for sign in(-1,1)}
        panel=query['reader']['panel'];actual={tuple(o['site']):o for o in panel}
        check(len(panel)==len(expected)and set(actual)==set(expected),label+': common-reader coverage')
        candidates=[]
        for site,sign in expected.items():
            if site not in actual:continue
            f=fields(int(actual[site]['raw']))
            if f['state']>0 and f['semantic']==1 and f['direction']==[0,0,sign]:candidates.append(sign)
        formed=candidates[0]if len(candidates)==1 else None
        check(formed==query['reader']['formed_native_command'],label+': decoder from RAW')
        check((len(candidates)>1)==query['reader']['ambiguous'],label+': ambiguity')
        decoded_queries+=1;return formed
    r01=evidence/'CURVAS_LEXICO_AUX_R01'
    old01=read(r01/'OLD14_PREFIJO_COMUN.json.gz');screen01=read(r01/'PREFLIGHT_COMPLETO.json');result01=read(r01/'RESULTADOS.json')
    validate_raw(old01,'R01.old14');validate_raw(screen01,'R01.preflight')
    old_signs={row['form']:decode_query(row['result'],'R01.old14.'+row['form'],legacy=True)for row in old01['rows']}
    check(not screen01['admissible'],'R01 preflight rejected')
    conflicts=[r for r in screen01['rows']if r['requires_RAW_zero']and int(r['observation']['raw'])]
    check(conflicts==screen01['required_RAW_zero_conflicts'],'R01 exact RAW conflicts')
    check(len(result01['branches'])==0,'R01 no branch teaching')
    r02=evidence/'CURVAS_LEXICO_AUX_R02'
    screen02=read(r02/'PREFLIGHT_COMPLETO.json');preparation=read(r02/'PREPARACION_UNICA.json.gz');result02=read(r02/'RESULTADOS.json')
    validate_raw(screen02,'R02.preflight');validate_raw(preparation,'R02.preparation')
    check(screen02['admissible'],'R02 preparation admitted')
    check(all(int(r['observation']['raw'])==0 for r in screen02['rows']if r['requires_RAW_zero']),'R02 all sources/slots RAW0')
    check(len(preparation['requests'])==12 and all(r['receipt']['status']=='applied'for r in preparation['requests']),'R02 twelve legal preparation inputs')
    check(len(result02['branches'])==6 and all('failure'in r for r in result02['branches']),'R02 six documentary failures')
    r03=evidence/'CURVAS_LEXICO_AUX_R03';result03=read(r03/'RESULTADOS.json');arms=[];witnesses=[]
    module_path=Path(__file__).with_name('recalcular_curvas_lexico_apd03_r01.py')
    spec=importlib.util.spec_from_file_location('archived_curve_metric',module_path)
    metric=importlib.util.module_from_spec(spec);spec.loader.exec_module(metric)
    for branch in result03['branches']:
        if 'failure'in branch:
            issues.append('R03 branch failed: '+str(branch['index']));continue
        folder=r03/Path(branch['primary']).parent
        primary=read(folder/'PRIMARIO.json.gz');validate_raw(primary,folder.name)
        for path,item in walk(primary):
            if item.get('kind')=='APD03_common_lexical_query':decode_query(item,folder.name+path)
        computed=metric.recalculate(primary)
        check(computed==branch['result'],folder.name+': original metric reproducible')
        functional=primary['B_functional_use'];interaction=functional['interaction'];downstream=None
        if interaction is not None:
            if interaction['kind']=='query':downstream=decode_query(interaction,folder.name+': memory use',memory_only=True)
            elif interaction['kind']=='native_current_selection':
                candidates=[]
                for observation in interaction['reader']['observations']:
                    f=fields(int(observation['raw']))
                    for x in(-1,0,1):
                        for z in(0,-1):
                            site=tuple((15+offset)%N for offset in(2*x,2,2*z))
                            if tuple(observation['site'])==site and f['state']>0 and f['semantic']==1 and f['direction']==[x,1,z]:candidates.append(x)
                downstream=candidates[0]if len(candidates)==1 else None
                check(downstream==interaction['reader']['choice'],folder.name+': current-read RAW')
        rejections=[]
        for path,item in walk(primary):
            if 'receipt'in item and 'id'in item and item['receipt']['status']!='applied':
                rejections.append({'id':int(item['id']),'tick':item['tick'],'site':item.get('site'),
                    'channel':item.get('channel'),'status':item['receipt']['status'],'path':path})
        unique={r['id']:r for r in rejections};rejections=sorted(unique.values(),key=lambda r:(r['tick'],r['id']))
        witness=read(folder/'IGUALDAD_INICIAL.json');witnesses.append(witness)
        check(witness['full_encoded_byte_identical']and witness['full_decoded_byte_identical']and witness['save_preserved_physical'],folder.name+': archived complete-state source proof')
        arms.append({'index':branch['index'],'history':computed['history'],'B_sign':computed['B_sign_auditor_only'],
            'first_B_before_teaching':computed['initial_B_emission_before_B_teaching'],
            'first_criterion':computed['first_criterion'],'B_learning_curve':computed['learning_curve'],
            'old_same_valid_sign_out_of4':computed['old_same_valid_sign'],'A_before':computed['A_before_B'],'A_after':computed['A_after_B'],
            'functional_choice':computed['functional_native_choice'],'functional_downstream_emission':downstream,
            'Native_unique_requested':computed['native_requests_unique'],'Native_statuses':computed['receipt_status_counts'],
            'rejections':rejections,'first_rejection':rejections[0]if rejections else None,
            'A_lesson_hub':primary['A_lesson']['hub'],'first_B_lesson_hub':primary['B_learning_curve'][0]['lesson']['hub']})
    check(len(witnesses)==6 and all(w==witnesses[0]for w in witnesses),'R03 common loaded initial state proof')
    metadata_before=read(r03/'ARM_0_related_-1/METADATOS_RUNTIME_ANTES_SAVE.json.gz')
    metadata_after=read(r03/'ARM_0_related_-1/METADATOS_RUNTIME_DESPUES_SAVE.json.gz')
    check(metadata_before==metadata_after,'R03 saved metadata values equal')
    if witnesses:
        check(hmeta(metadata_before)==witnesses[0]['before_official_save_metadata']['all_metadata_sha256'],'R03 full metadata hash from included values')
    diagnosis=read(r03/'DIAGNOSTICO_K_Y_METADATA_N0.json')
    check(all(o['K']['raw']=='0'for o in diagnosis['observations']),'K zero at all decoded saved cuts; not persistent blockage claim')
    return {'schema':'APD03.lexical_complete_primary_recalculation.N0.R01','checks':checks,'issues':issues,
        'RAW_fields_checked':raw_count,'common_reader_queries_redecoded':decoded_queries,
        'R01':{'old14':old_signs,'rejected_preparation_conflicts':conflicts,'branches_executed':0},
        'R02':{'preparation_inputs_requested':12,'preparation_inputs_applied':12,
            'documentary_guard_failures':6,'branch_specific_experiences_executed':0},
        'R03':{'arms':arms,'independent_learners':0,'related_branches_sharing_prefix':6,
            'new_algorithms_demonstrated':0,'specific_meta_learning_demonstrated':False,
            'initial_B_valid_before_teaching':sum(r['first_B_before_teaching']in(-1,1)for r in arms)},
        'K_saved_cut_observations':diagnosis['observations'],
        'creator_guard_cache_reconstruction_source_proof':diagnosis['old_creation_hash_exactly_reconstructed_by_original_owner_chunks'],
        'new_native_ticks':0,'limits':['Raw K pre/post at individual rejected boundaries was not recorded.',
            'All omitted B cue attempts rejected; requested lessons cannot be treated as admitted equal acquisition.',
            'Full snapshots remain local; included decoded K/metadata extraction has source hashes and must not be called a complete operational backup.',
            'Similar related/opposite results do not demonstrate semantically specific learning-to-learn.']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--evidence',required=True,type=Path);parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();report=calculate(args.evidence)
    with args.out.open('x',encoding='utf8')as stream:json.dump(report,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({'checks':report['checks'],'issues':len(report['issues']),'RAW':report['RAW_fields_checked'],'queries':report['common_reader_queries_redecoded']}))
    return 0 if not report['issues']else 1


if __name__=='__main__':raise SystemExit(main())
