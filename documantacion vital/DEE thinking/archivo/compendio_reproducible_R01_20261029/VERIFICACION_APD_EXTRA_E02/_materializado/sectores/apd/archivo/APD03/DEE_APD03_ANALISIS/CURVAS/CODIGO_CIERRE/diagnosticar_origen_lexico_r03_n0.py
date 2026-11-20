"""Exact stdlib snapshot parser diagnosis of K blockage and metadata guard."""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path


def load(path):
    spec=importlib.util.spec_from_file_location('exact_snapshot_observer',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def hmeta(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--evidence-root',required=True,type=Path)
    parser.add_argument('--original-parent',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();reader=load(Path(__file__).with_name('recalculo')/'observador_causal_retrospectivo_01.py')
    r02=args.evidence_root/'CURVAS_LEXICO_AUX_R02';r03=args.evidence_root/'CURVAS_LEXICO_AUX_R03'
    files=[('original_parent',args.original_parent),('prepared_prefix',r02/'PREFIJO_COMPLETO.deetsnap.gz'),
        ('omitted_minus_final',r03/'ARM_2_omitted_-1/FINAL_COMPLETO.deetsnap.gz'),
        ('omitted_plus_final',r03/'ARM_5_omitted_1/FINAL_COMPLETO.deetsnap.gz'),
        ('related_minus_final',r03/'ARM_0_related_-1/FINAL_COMPLETO.deetsnap.gz')]
    observations=[];parent_meta=None;prefix_meta=None
    for label,path in files:
        snapshot=reader.Snapshot(path,verify_checksum=True)
        observations.append({'label':label,'source_path':str(path),'encoded_bytes':snapshot.encoded_bytes,
            'encoded_sha256':snapshot.encoded_sha256,'decoded_sha256':snapshot.decoded_sha256,
            'checksum_valid':snapshot.checksum_valid,'N':snapshot.N,'tick':snapshot.tick,
            'K':snapshot.observation([47,7,47]),'legacy_H':snapshot.observation([47,17,47]),
            'metadata_sha256':hmeta(snapshot.metadata)})
        if label=='original_parent':parent_meta=snapshot.metadata
        if label=='prepared_prefix':prefix_meta=snapshot.metadata
        del snapshot
    loaded=json.loads(gzip.decompress((r03/'ARM_0_related_-1/METADATOS_RUNTIME_ANTES_SAVE.json.gz').read_bytes()))
    witness=json.loads((r02/'PREFIJO_TESTIGO.json').read_bytes())
    encoded_prefix='dee_thinking.organizational.v1.'
    combined={k:v for k,v in prefix_meta.items()if not k.startswith(encoded_prefix)}
    combined.update({k:v for k,v in parent_meta.items()if k.startswith(encoded_prefix)})
    changed=[{'key':key,'serialized_prefix_sha256':None if key not in prefix_meta else hashlib.sha256(prefix_meta[key].encode('utf8')).hexdigest(),
        'loaded_runtime_sha256':None if key not in loaded else hashlib.sha256(loaded[key].encode('utf8')).hexdigest()}
        for key in sorted(set(prefix_meta)|set(loaded))if prefix_meta.get(key)!=loaded.get(key)]
    report={'schema':'APD03.lexical_origin_snapshot_diagnosis.N0.R01','new_native_ticks':0,
        'parser_path':str(Path(reader.__file__)),'parser_sha256':hashlib.sha256(Path(reader.__file__).read_bytes()).hexdigest(),
        'observations':observations,'source_rejections':[],
        'serialized_prefix_vs_loaded_runtime_metadata_different_keys':changed,
        'prefix_runtime_metadata_hash_recorded_at_creation':witness['all_snapshot_metadata_sha256'],
        'serialized_prefix_metadata_hash':hmeta(prefix_meta),'loaded_runtime_metadata_hash':hmeta(loaded),
        'reconstructed_using_current_nonowner_metadata_and_original_parent_owner_chunks_hash':hmeta(combined),
        'old_creation_hash_exactly_reconstructed_by_original_owner_chunks':hmeta(combined)==witness['all_snapshot_metadata_sha256'],
        'scope':'Complete snapshot decoding with checksum; K is measured at saved prefix/final only, not at each rejected application. Metadata reconstruction is an exact hash check of a specified candidate cache composition, not a claim of time inversion or historical information recovery.'}
    for arm in('ARM_2_omitted_-1','ARM_5_omitted_1'):
        primary=json.loads(gzip.decompress((r03/arm/'PRIMARIO.json.gz').read_bytes()));found={}
        def visit(x,path='$'):
            if isinstance(x,dict):
                if 'receipt'in x and 'id'in x and x['receipt']['status']!='applied':
                    found[int(x['id'])]={'path':path,'id':x['id'],'channel':x.get('channel'),'site':x.get('site'),'tick':x.get('tick'),'receipt':x['receipt']}
                for k,v in x.items():visit(v,path+'.'+str(k))
            elif isinstance(x,list):
                for i,v in enumerate(x):visit(v,path+'['+str(i)+']')
        visit(primary)
        rows=sorted(found.values(),key=lambda row:(row['tick'],int(row['id'])))
        report['source_rejections'].append({'arm':arm,'first_rejection':rows[0]if rows else None,
            'rejections':rows,'all_rejections_at_K':all(row['site']==[47,7,47]for row in rows),
            'missing_pre_post_RAW_at_each_rejection':True})
    data=(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    with args.output.open('xb')as stream:stream.write(data)
    print(json.dumps({'output':str(args.output),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
        'K_raw_by_state':[(r['label'],r['K']['raw'])for r in observations],
        'old_creation_hash_exactly_reconstructed_by_original_owner_chunks':report['old_creation_hash_exactly_reconstructed_by_original_owner_chunks'],
        'metadata_different_keys_count':len(changed)}))


if __name__=='__main__':main()
