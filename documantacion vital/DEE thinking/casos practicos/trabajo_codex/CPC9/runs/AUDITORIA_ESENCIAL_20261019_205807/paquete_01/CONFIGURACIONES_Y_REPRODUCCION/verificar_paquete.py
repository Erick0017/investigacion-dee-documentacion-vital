"""Validate the essential package and repeat metrics without a DEE Runtime."""
from pathlib import Path
from collections import Counter
import argparse,ast,csv,hashlib,json,os,subprocess,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from codec import Reader,sha,canonical
from campos_guardados import array_bytes,stats
sys.stdout.reconfigure(encoding='utf8')
def read(p):return json.loads(p.read_text(encoding='utf8'))
def run(argv,folder,name,timeout=420):
    before=time.monotonic();c=subprocess.run(argv,cwd=folder,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    folder.joinpath(name+'.stdout.log').write_bytes(c.stdout);folder.joinpath(name+'.stderr.log').write_bytes(c.stderr)
    if c.returncode:raise RuntimeError(name+' failed: '+c.stderr.decode('utf8',errors='replace')[-2000:])
    return{'name':name,'argv':list(map(str,argv)),'exit_code':c.returncode,'elapsed_seconds':time.monotonic()-before}
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=a.root.resolve(strict=True);out=a.out.resolve();started=time.monotonic()
    if out.exists():raise FileExistsError('Use a fresh verification directory')
    out.mkdir(parents=True);m=read(root/'MANIFIESTO_HASHES.json');actual={f.relative_to(root).as_posix():f for f in root.rglob('*')if f.is_file()and f.name!='MANIFIESTO_HASHES.json'};listed={r['path']:r for r in m['files']}
    if set(actual)!=set(listed):raise ValueError('Manifest coverage mismatch')
    replacements=[];old_invalid_sources=[]
    forbidden={'.whl','.pyd','.dll','.exe','.cpp','.hpp','.h','.so','.a','.lib','.o','.obj','.zip','.gz','.deetsnap'}
    for name,f in actual.items():
        b=f.read_bytes()
        if len(b)!=listed[name]['bytes']or sha(b)!=listed[name]['sha256']:raise ValueError('Manifest checksum mismatch: '+name)
        if f.suffix.lower()in forbidden:raise ValueError('An engine/binary/state file leaked into reduced export')
        text=b.decode('utf-8-sig')
        if '\ufffd'in text:replacements.append({'file':name,'replacement_characters':text.count('\ufffd'),'note':'Existing recorded text retained without silently repairing its provenance.'})
        if f.suffix=='.json':json.loads(text)
        if f.suffix=='.py':
            try:ast.parse(text)
            except SyntaxError as e:
                if '/FUENTES_EXPERIMENTALES/'not in name and '/CODIGOS_POR_HASH/'not in name and '/TESTIGOS_HISTORICOS/'not in name:raise
                old_invalid_sources.append({'file':name,'line':e.lineno,'message':e.msg,'scope':'Archived prior source, not an executed audit entry point'})
            if '/FUENTES_EXPERIMENTALES/'in name or'/CODIGOS_POR_HASH/'in name:
                if 'def one_step('in text or'PYBIND11_MODULE('in text or'__global__'in text:raise ValueError('Transition implementation exported unexpectedly')
    reader=Reader(root/'EVIDENCIA_PRIMARIA_ESENCIAL')
    for i,row in enumerate(reader.index['documents']):
        reader.get(row['id'])
        if i%200==0:print('Decoded documents',i,flush=True)
    fields=[]
    for f in sorted((root/'EVIDENCIA_PRIMARIA_ESENCIAL/CAMPOS_COMPACTOS').glob('S*.json')):
        d=read(f);raw=array_bytes(d,'RAW',f.parent);clocks=array_bytes(d,'CLOCKS',f.parent)
        if sha(raw)!=d['physical']['RAW_sha256']or sha(clocks)!=d['physical']['clocks_sha256']or stats(raw)!=d['independently_recounted']:raise ValueError('Exact saved fields differ')
        fields.append({'file':f.relative_to(root).as_posix(),'tick':d['physical']['tick'],'N':d['N'],'exact':True})
    guards=root/'CONFIGURACIONES_Y_REPRODUCCION/guardia_recalculo.py';commands=[];python=sys.executable
    def guarded(script,arguments,name):
        rec=out/(name+'.guard.json');argv=[python,'-I','-B',str(guards),'--root',str(root),'--work',str(out),'--script',script,'--receipt',str(rec),'--',*map(str,arguments)]
        commands.append(run(argv,out,name));d=read(rec)
        if d['status']!='PASS'or d['engine_imported']or d['denied_operations']:raise ValueError('Audit isolation check failed')
    guarded('recalcular_esencial.py',['--root',root,'--out',out/'recalculo'],'01_recalculo')
    guarded('preparar_tablas.py',['--package',root,'--recalculation',out/'recalculo','--out',out/'tablas.json'],'02_tablas')
    guarded('contrastar_historicos.py',['--root',root,'--out',out/'contraste_historico.json'],'03_historico')
    cal=read(out/'recalculo/CALCULOS_RECALCULADOS.json');baseline=read(root/'EVIDENCIA_PRIMARIA_ESENCIAL/CALCULOS_RECALCULADOS.json');cal.pop('elapsed_seconds',None);baseline.pop('elapsed_seconds',None)
    if cal!=baseline:raise ValueError('Primary recalculation differs from sealed metrics')
    if read(out/'contraste_historico.json')!=read(root/'CONTROLES_CAUSALES/CONTRASTE_HISTORICO_RECALCULADO.json'):raise ValueError('Historical fingerprint recalc differs')
    expected=read(out/'tablas.json');csvs=[]
    for name,t in expected['tables'].items():
        with(root/name).open(encoding='utf-8-sig',newline='')as f:rows=list(csv.reader(f))
        if rows!=[t['headers'],*t['rows']]:raise ValueError('CSV literal table mismatch: '+name)
        csvs.append({'file':name,'rows':len(t['rows']),'columns':len(t['headers']),'all_values_recalculated_or_source_checked':True})
    queries=read(root/'RESULTADOS_NEGATIVOS/CONSULTAS_65_Y_CONTROLES.json')['rows'];qcheck=0
    for q in queries:
        v=int(q['physical']['raw']);direction=[((v>>s)&15)-16 if((v>>s)&15)>=8 else((v>>s)&15)for s in(48,52,56)]
        qualified=(v&0xffffffff)>0 and(v>>60)&15==1 and direction==q['expected_auditor_direction']
        if qualified!=q['qualified']:raise ValueError('Raw-derived qualification differs from frozen recorded qualifier')
        qcheck+=1
    claims=read(root/'AFIRMACIONES_Y_EVIDENCIAS.json')['claims']
    if len(claims)!=15 or any(not c['evidence']for c in claims):raise ValueError('An important claim lacks original evidence')
    for c in claims:
        for e in c['evidence']:
            row=reader.lookup[e['id']]
            if not any(o['sha256']==e['original_sha256']for o in row['origins']):raise ValueError('Claim source hash is not included')
    if len(fields)!=13 or cal['primary_coverage']['containers']!=281 or cal['continuity']['unique_receipts']!=1573:raise ValueError('Essential coverage incomplete')
    report={'schema':'CPC9.essential.clean_package_validation.v1','status':'PASS','python':sys.version,'executable':sys.executable,'manifest_files_verified':len(actual),'documents_losslessly_decoded':len(reader.index['documents']),
       'physical_field_states':fields,'CSV_tables':csvs,'raw_derived_query_checks':qcheck,'claims_with_original_hashes_checked':len(claims),'commands':commands,
       'engine_imported':False,'new_native_campaign_runs':0,'all_guarded_audits_no_undeclared_access':True,'original_replacement_characters':replacements,'archived_syntax_invalid_sources':old_invalid_sources,
       'scope':'Integrity/data recalculation only; not a new scientific replica or a verdict of65meanings. Python guards are not an OS security sandbox.','elapsed_seconds':time.monotonic()-started}
    with(out/'VERIFICACION_PAQUETE.json').open('x',encoding='utf8')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'status':'PASS','files':len(actual),'documents':len(reader.index['documents']),'queries_checked_from_RAW':qcheck,'elapsed_seconds':report['elapsed_seconds']}))
if __name__=='__main__':main()
