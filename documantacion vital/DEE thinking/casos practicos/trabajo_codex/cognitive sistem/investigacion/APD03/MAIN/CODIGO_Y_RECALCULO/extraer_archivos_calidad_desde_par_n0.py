"""Copy actual APD02 files exclusively from an already closed paired cut.

No live state, engine, actor, queue database or original file is opened.
The script is prepared while Main runs, and is not run until Root confirms
the exact postSTOP final pair. It never reconstructs expected artifact bytes.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path,PureWindowsPath
import shutil


def read(path):
    value=Path(path).read_bytes()
    return json.loads(gzip.decompress(value) if str(path).endswith('.gz') else value)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def walk(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from walk(child)
    elif isinstance(value,list):
        for child in value:yield from walk(child)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--paired',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError('A new immutable extraction directory is required')
    manifest_path=args.paired/'EXPORTACION_SERVICIO.json';manifest=read(manifest_path)
    final=read(args.evidence/'REGISTROS_VENTANA.json.gz')
    if manifest['life_id']!='APD03_MAIN' or not final.get('final_stopped_cut'):
        raise ValueError('Only the confirmed actual Main postSTOP final pair is accepted')
    if sha(manifest_path)!=final['final_stopped_cut']['manifest_sha256']:
        raise ValueError('The paired cut differs from the actual recorded final one')
    files=[];args.out.mkdir(parents=True)
    for event_path in sorted((args.evidence/'EVENTOS').glob('*.json.gz')):
        event=read(event_path)
        if event.get('kind')!='material':continue
        decoded=event.get('decoded_result') or {}
        for row in walk((decoded.get('result') or {}).get('rows',[])):
            if row.get('kind')!='APD02_quality_request':continue
            artifact=row['committed_effect'].get('artifact')
            if not artifact:continue
            container=PureWindowsPath(row['effect_directory']).name
            suffix='/'+container+'/'+artifact['relative_path'].replace('\\','/')
            matches=[item for item in manifest['members'] if item['file'].endswith(suffix) and
                item['sha256']==artifact['sha256'] and item['bytes']==artifact['bytes']]
            if len(matches)!=1:raise ValueError('Actual APD02 file not unique in the closed pair: '+suffix)
            member=matches[0];source=(args.paired/member['file']).resolve()
            if not source.is_relative_to(args.paired.resolve()):raise ValueError('Paired artifact escapes the closed evidence directory')
            if sha(source)!=artifact['sha256'] or source.stat().st_size!=artifact['bytes']:
                raise ValueError('Actual paired artifact no longer matches its committed receipt')
            relative='FILES/'+container+'/'+artifact['relative_path'].replace('\\','/')
            destination=args.out/relative;destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,destination)
            if sha(destination)!=artifact['sha256']:raise ValueError('Copied actual bytes differ')
            files.append({'tag':event['tag'],'file':relative,'relative_path':artifact['relative_path'],
                'bytes':artifact['bytes'],'sha256':artifact['sha256'],'source_pair_member':member['file'],
                'source_system_relative_provenance_only':member.get('source_system_relative'),
                'source_event':'EVENTOS/'+event_path.name,'source_event_sha256':sha(event_path),
                'scope':'Original bytes copied from the final postSTOP pair; not reconstructed from a quality verdict or expected number.'})
    result={'schema':'APD03.closed_pair_actual_APD02_files.R01','life':'APD03_MAIN',
        'source_pair_manifest_sha256':sha(manifest_path),'source_pair_physical':manifest['physical'],
        'new_native_ticks':0,'files':files,'no_live_system_reads':True}
    with (args.out/'APD02_FILES.json').open('x',encoding='utf8') as stream:
        json.dump(result,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({'actual_files':len(files),'manifest_sha256':sha(args.out/'APD02_FILES.json'),'new_native_ticks':0}))


if __name__=='__main__':main()
