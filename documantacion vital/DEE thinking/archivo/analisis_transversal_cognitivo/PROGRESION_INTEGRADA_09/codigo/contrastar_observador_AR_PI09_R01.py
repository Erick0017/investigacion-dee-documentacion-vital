"""Passive full-snapshot contrast from two closed four-operation proofs.

Only stdlib and the SHA-pinned passive byte parser are imported. No Native,
owner, database, world restore or current mutable card is accessed.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json

P=Path(__file__).resolve().parents[1]
PARSER=P.parents[2]/'DEE Cognitive 2.0/reproducibilidad/observador_pasivo.py'
PARSER_SHA='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):return json.loads(Path(path).read_text('utf-8-sig'))


def require(value,message):
    if not value:raise ValueError(message)


def snapshot_record(proof_path,ordinal):
    proof=read(proof_path)
    require(proof['closed']is True and proof['error']is None and len(proof['records'])==4,'Closed complete four-operation phase required')
    plan=read(proof['plan']);record=proof['records'][ordinal];primary=Path(record['primary'])
    require(sha(primary)==record['sha256'],'Closed immutable primary changed')
    envelope=read(primary)['result']
    if isinstance(envelope,str):envelope=json.loads(envelope)
    snap=envelope['committed_snapshot'];system=Path(plan['system']).resolve(strict=True)
    path=(system/snap['snapshot']).resolve(strict=True)
    require(path.is_relative_to(system)and not path.is_symlink(),'Snapshot locator escaped isolated system')
    require(sha(path)==snap['snapshot_sha256'],'Snapshot/primary mismatch')
    return {'path':path,'sha256':snap['snapshot_sha256'],'physical':snap['physical'],
            'life_id':snap['life_id'],'system':str(system),'primary':str(primary),'primary_sha256':record['sha256']}


def canonical(text,record):
    # Exact administrative identity/home substitutions only; never drop a key,
    # number, protocol, return, expected value, sensor or actor field.
    def value(obj):
        if isinstance(obj,str):return obj.replace(record['system'].replace('\\','/'),'<SYSTEM>').replace(record['system'],'<SYSTEM>').replace(record['life_id'],'<DIAGNOSTIC_LIFE>')
        if isinstance(obj,list):return[value(x)for x in obj]
        if isinstance(obj,dict):return{value(k):value(v)for k,v in obj.items()}
        return obj
    try:parsed=json.loads(text)
    except (ValueError,TypeError):return value(text)
    return json.dumps(value(parsed),ensure_ascii=False,sort_keys=True,separators=(',',':'))


def main(args):
    require(sha(PARSER)==PARSER_SHA,'Pinned passive parser changed')
    spec=importlib.util.spec_from_file_location('AR_passive_snapshot_parser',PARSER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    rows=[]
    for ordinal in range(4):
        a=snapshot_record(args.a,ordinal);b=snapshot_record(args.b,ordinal)
        av=module.snapshot_view(a['path']);bv=module.snapshot_view(b['path'])
        require(sha(a['path'])==a['sha256']and sha(b['path'])==b['sha256'],'Snapshot changed during passive read')
        require(all(a['physical'][k]==v for k,v in av['physical'].items())and all(b['physical'][k]==v for k,v in bv['physical'].items()),'Decoded physical fields disagree with closed primary')
        # Cached transport owner/service values deliberately remain listed.
        admin_keys={module.SYSTEM_KEY,module.SERVICE_KEY}
        keys=sorted(set(av['metadata'])|set(bv['metadata']));metadata=[]
        for key in keys:
            left=av['metadata'].get(key);right=bv['metadata'].get(key)
            if left==right:continue
            normalized=(left is not None and right is not None and canonical(left,a)==canonical(right,b))
            metadata.append({'key':key,'literal_equal':False,'exact_home_and_identity_normalized_equal':normalized,
                             'administrative_key':key in admin_keys or key.startswith(module.SERVICE_KEY+'.queue.'),
                             'a_sha256':hashlib.sha256((left or '').encode('utf8')).hexdigest(),
                             'b_sha256':hashlib.sha256((right or '').encode('utf8')).hexdigest()})
        unresolved=[m['key']for m in metadata if not(m['exact_home_and_identity_normalized_equal']or m['administrative_key'])]
        rows.append({'ordinal':ordinal,'a':{k:str(v)if isinstance(v,Path)else v for k,v in a.items()},
                     'b':{k:str(v)if isinstance(v,Path)else v for k,v in b.items()},
                     'physical_equal':av['physical']==bv['physical'],
                     'causal_prefix_equal':av['causal_prefix_sha256']==bv['causal_prefix_sha256'],
                     'phase_equal':av['phase']==bv['phase'],
                     'counts_equal':all(av[k]==bv[k]for k in ('interfaces','pending_native','native_receipts')),
                     'a_counts':{k:av[k]for k in ('interfaces','pending_native','native_receipts')},
                     'b_counts':{k:bv[k]for k in ('interfaces','pending_native','native_receipts')},
                     'changed_metadata':metadata,'unresolved_metadata_changes':unresolved,
                     'scope':'Causal prefix covers Native header, RAW, clocks, interfaces, pending agenda, receipts and organizational record bytes; metadata examined separately.'})
    output={'schema':'DEE.PI09.F1.actual_snapshot_observer_contrast.R01','rows':rows,
            'all_four_physical_and_causal_prefixes_equal':all(r['physical_equal']and r['causal_prefix_equal']for r in rows),
            'all_nonadministrative_metadata_equal_after_exact_transport_aliases':all(not r['unresolved_metadata_changes']for r in rows),
            'native_ticks_added':0,'DEE_imports':0,'databases_read':0,
            'parser':{'path':str(PARSER),'sha256':PARSER_SHA,'gzip_CRC_checked':True,'internal_FNV_recalculated':False},
            'claim_scope':'Matched four-operation observer comparison only. This does not validate every future reader, phase or instrumentation condition.'}
    with args.salida.open('x',encoding='utf8')as stream:json.dump(output,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'output':str(args.salida),'sha256':sha(args.salida),
                      'all_four_physical_and_causal_prefixes_equal':output['all_four_physical_and_causal_prefixes_equal'],
                      'unresolved_metadata':{str(r['ordinal']):r['unresolved_metadata_changes']for r in rows},'Native':0},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--a',type=Path,required=True);parser.add_argument('--b',type=Path,required=True);parser.add_argument('--salida',type=Path,required=True);main(parser.parse_args())
