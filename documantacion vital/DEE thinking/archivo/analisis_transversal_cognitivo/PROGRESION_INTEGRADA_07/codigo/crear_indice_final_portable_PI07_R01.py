"""Passive final selection/export/index. Literal primaries and actual products."""
from pathlib import Path
import hashlib, importlib.util, json, sys

P=Path(__file__).resolve().parents[1]
DEST=P/'control/PORTABLE_FINAL_PI07_R01'
COLD=P/'control/PORTABLE_COLD_FINAL_PI07_R01'
INDEX=P/'control/INDICE_PRIMARIOS_PI07.json'

def load(name,file):
    s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def recognized(row):
    if isinstance(row.get('original_result'),dict) and 'FI'in row['original_result']:
        return recognized(row['original_result'])
    if all(k in row for k in('FI','sensor','return_frames')):return True
    if all(k in row for k in('first_reader','native_arithmetic','second_native_use','actual_effect')):return True
    if 'numeric_result'in row and 'native_operation'in row:return True
    if isinstance(row.get('reader'),dict)and 'formed_native_command'in row['reader']:return True
    if 'early_observation'in row and 'original_result'in row:return True
    nested=row.get('result',{})
    return isinstance(nested,dict)and any(recognized(r)for r in nested.get('rows',[]))

def main():
    if INDEX.exists()or DEST.exists()or COLD.exists():raise FileExistsError('No overwritten final index or export')
    dec=load('PI07_documentary_decoder',P/'codigo/RECALCULAR_PRIMARIOS_PI07.py')
    exporter=load('PI07_literal_exporter',P/'codigo/EXPORTAR_PRIMARIOS_PORTABLE_PI07.py')
    sources={};omitted=[]
    for label,folder in [('campaign',P/'ensayos'),('cold',P/'estados/RP_EP04_R01/ensayos')]:
        selected=[]
        for path in sorted(folder.glob('*.json')):
            _,rows=dec.decoded_result(read(path))
            if any(recognized(row)for row in rows):selected.append(path)
            else:omitted.append({'file':str(path),'sha256':sha(path),'reason':'Administrative/no recognized fixed material reader row; still preserved in campaign/all-primaries package selection.'})
        sources[label]=selected
    total=sum(f.stat().st_size for fs in sources.values()for f in fs)
    if total>80000000:raise ValueError('Unexpected material copy size; inspect before exporting')
    exports=[]
    for label,destination,system in [('campaign',DEST,P/'estados/candidato/sistema'),('cold',COLD,P/'estados/RP_EP04_R01/sistema')]:
        sys.argv=['literal_export','--destino',str(destination),'--sistema',str(system),'--primarios',*[str(f)for f in sources[label]]]
        if exporter.main()!=0:raise RuntimeError('Literal export failed; preserve partial work')
        exports.append(destination)
    combined={'schema':'DEE.PI07.portable_primary_index.v1','primaries':[],'products':[],
              'new_Native_ticks':0,'scope':'Literal current material primaries, negative cases, selected cold replay rows and actual64B products. Original paths are provenance only and are ignored by the portable verifier.'}
    home=DEST/'04_EVIDENCIAS/PRIMARIOS';products={};names=set()
    for export in exports:
        index=read(export/'04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI07.json')
        for entry in index['primaries']:
            name=entry['original_basename']
            if Path(name).name!=name or name in names:raise ValueError('Ambiguous material primary basename')
            names.add(name);source=export/entry['file'];target=home/name
            if source!=target:
                if target.exists():raise FileExistsError(target)
                # Move only the new export copy, never a Native/original file.
                if not source.resolve().is_relative_to(P.resolve())or not target.parent.resolve().is_relative_to(P.resolve()):raise ValueError('Export copy escaped PI07')
                source.rename(target)
            if sha(target)!=entry['sha256']:raise ValueError('Literal material copy changed')
            entry=dict(entry,file=target.relative_to(DEST).as_posix());combined['primaries'].append(entry)
        for entry in index['products']:
            if entry['sha256']in products:continue
            source=export/entry['file'];target=home/Path(entry['file']).name
            if source!=target and not target.exists():source.rename(target)
            if sha(target)!=entry['sha256']:raise ValueError('Actual product copy changed')
            products[entry['sha256']]=dict(entry,file=target.relative_to(DEST).as_posix())
    combined['products']=list(products.values())
    data=(json.dumps(combined,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    # The campaign index is the canonical source selected by the final packager.
    INDEX.write_bytes(data);(home/'INDICE_PRIMARIOS_PI07.json').write_bytes(data)
    result=DEST/'RESULTADO_PRIMARIOS_PI07.json'
    sys.argv=['documentary_recalculation','--raiz',str(DEST),'--salida',str(result)]
    status=dec.main()
    proof={'schema':'DEE.PI07.final_literal_portable_index.actual.v1','new_Native_ticks':0,
           'primary_count':len(combined['primaries']),'product_files':len(combined['products']),
           'literal_primary_copy_bytes':total,'index':str(INDEX),'index_sha256':sha(INDEX),
           'portable_export_root':str(DEST),'recalculation':str(result),'recalculation_sha256':sha(result),
           'returncode':status,'omitted_administrative_from_fixed_recalculation':omitted,
           'no_Native_original_modified':True}
    out=P/'control/INDICE_PORTABLE_FINAL_VERIFICADO_PI07_R01.json';out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'index':str(INDEX),'index_sha256':sha(INDEX),'primaries':len(combined['primaries']),
                      'products':len(combined['products']),'copy_bytes':total,'recalculation_returncode':status,
                      'result_sha256':sha(result),'verification_sha256':sha(out)},ensure_ascii=False))
    return status

if __name__=='__main__':raise SystemExit(main())
