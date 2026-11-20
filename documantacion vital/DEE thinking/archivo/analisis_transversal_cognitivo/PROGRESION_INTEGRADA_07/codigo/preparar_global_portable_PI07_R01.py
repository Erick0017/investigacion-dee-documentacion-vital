"""Explicit closed-capture export. Default read-only plan; no Native execution."""
from pathlib import Path
import argparse, hashlib, json, runpy


def sha(b):return hashlib.sha256(b).hexdigest()


def rows(value):
    if isinstance(value,dict):
        for k,v in value.items():
            if k in('external_global_capture','external_observation')and isinstance(v,dict)and all(name in v for name in('directory','index_sha256','captured_frames')):yield v
            else:yield from rows(v)
    elif isinstance(value,list):
        for v in value:yield from rows(v)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--primarios',type=Path,nargs='+',required=True)
    parser.add_argument('--destino',type=Path,required=True);parser.add_argument('--crear',action='store_true')
    args=parser.parse_args();p7=Path(__file__).resolve().parents[1];r=p7.parents[2]
    selected={};references=[]
    for path in args.primarios:
        p=path.resolve(strict=True)
        if not p.is_relative_to(r):raise ValueError('Primary outside DEE root')
        b=p.read_bytes();j=json.loads(b)
        if str(j.get('status','')).lower()not in('completed','failed','rejected','cancelled'):
            raise ValueError('Only terminal explicit primaries: '+str(p))
        if isinstance(j.get('result'),str):j['result']=json.loads(j['result'])
        ref={'path':str(p),'bytes':len(b),'sha256':sha(b)};references.append(ref)
        for cap in rows(j):
            directory=Path(cap['directory']).resolve(strict=True)
            if not directory.is_relative_to(r):raise ValueError('Capture outside DEE root')
            data=(directory/'INDEX.json').read_bytes()
            if sha(data)!=cap['index_sha256']:raise ValueError('Closed capture index differs')
            key=str(directory)
            if key not in selected:selected[key]={'source':directory,'capture':cap,'index':json.loads(data),'source_references':[]}
            selected[key]['source_references'].append(ref)
    if not args.crear:
        print(json.dumps({'mode':'READ_ONLY_PLAN','primaries':len(references),'captures':len(selected),
          'recorded_frames':sum(x['capture']['captured_frames']for x in selected.values()),
          'compressed_payload_bytes':sum(x['capture']['compressed_payload_bytes']for x in selected.values()),
          'destination':str(args.destino),'Native_ticks':0,'files_written':0},ensure_ascii=False));return
    dest=args.destino.resolve()
    if not dest.is_relative_to(p7)or dest.exists():raise ValueError('Fresh PI07-only destination required')
    dest.mkdir(parents=True);files=[];captures=[]
    def copy(source,name):
        source=Path(source);resolved=source.resolve(strict=True)
        if not resolved.is_relative_to(r):raise ValueError('Source outside DEE root')
        for ancestor in(source,*source.parents):
            if ancestor.is_symlink()or getattr(ancestor.lstat(),'st_file_attributes',0)&1024:
                raise ValueError('Linked/reparse source is not allowed')
            if ancestor.resolve()==r.resolve():break
        data=source.read_bytes();target=dest/name
        if target.exists():raise FileExistsError(target)
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        if source.read_bytes()!=data:raise ValueError('Source changed during copy')
        files.append({'file':name,'bytes':len(data),'sha256':sha(data),'source':str(resolved)})
    for ordinal,item in enumerate(selected.values()):
        caseid=f'C{ordinal:04d}_{item["source_references"][0]["sha256"][:10]}'
        directory='capturas/'+caseid
        for name in('CAPTURA.json','INDEX.json','FRAMES.jsonl'):
            copy(item['source']/name,directory+'/'+name)
        for frame in item['index']['frames']:
            name=frame['file']
            if Path(name).name!=name:raise ValueError('Only safe capture leaf filenames')
            copy(item['source']/name,directory+'/'+name)
        captures.append({'id':caseid,'directory':directory,'source_references':item['source_references'],
          'captured_frames':item['capture']['captured_frames'],
          'missing_planned_ticks':item['capture'].get('missing_planned_ticks',[])})
    copy(p7.parent/'PROGRESION_INTEGRADA_05/codigo/observador_global_PI05_R01.py','codec.py')
    copy(p7/'codigo/recalcular_global_portable_PI07_R01.py','recalcular.py')
    manifest={'schema':'DEE.PI07.lossless_global_portable_manifest.v1','files':files,'captures':captures,
      'Native_ticks':0,'source_paths_are_provenance_only':True,'no_interpolated_frames':True}
    (dest/'CASOS.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    module=runpy.run_path(str(dest/'recalcular.py'),run_name='pure_portable_lossless_check')
    result=module['verify'](dest)
    proof=p7/'control'/('EXPORTACION_GLOBAL_PORTABLE_'+dest.name+'.json')
    if proof.exists():raise FileExistsError(proof)
    proof.write_text(json.dumps({'schema':'DEE.PI07.literal_closed_global_export.v1','bundle':str(dest),
      'manifest_sha256':sha((dest/'CASOS.json').read_bytes()),'captures':result['captures'],
      'frames':result['total_frames'],'all_complete_buffer_hashes_match':result['all_complete_buffer_hashes_match'],
      'files':len(files),'copied_bytes':sum(x['bytes']for x in files),'Native_ticks':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(proof.read_text(encoding='utf-8'))


if __name__=='__main__':main()
