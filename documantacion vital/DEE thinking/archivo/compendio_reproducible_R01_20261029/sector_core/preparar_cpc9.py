from pathlib import Path
import json,gzip,hashlib,base64,shutil
WORK=Path(__file__).resolve().parent;STAGE=WORK/'stage'
SRC=Path(r'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking')/'casos practicos/trabajo_codex/CPC9/runs/RUN_20261019_165651'
INDEX=STAGE/'documentacion/INDICE_MIEMBROS.json';STORE=STAGE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz'
def digest(b):return hashlib.sha256(b).hexdigest()
index=json.loads(INDEX.read_text(encoding='utf8'));paths=index['paths'];added={};sources=[]
def add(name,data,origin):
    h=digest(data);row={'sha256':h,'bytes':len(data),'origin':origin}
    if name in paths:assert paths[name]['sha256']==h
    paths[name]=row;added.setdefault(h,data);return h
def file(name,path):
    data=path.read_bytes();h=add(name,data,str(path));sources.append({'original':str(path),'relative_materialized':name,'sha256':h,'bytes':len(data)});return h
def versions(d,base):
    result={}
    for name,h in d.get('source_hashes',{}).items():
        name=name.replace('\\','/');p=SRC/name
        if not p.exists() or digest(p.read_bytes())!=h:p=SRC/'genealogia/code_by_hash'/(h+'.py')
        assert p.is_file(),(name,h)
        data=p.read_bytes();assert digest(data)==h,(name,h)
        file(base+'/'+name,p);result[name]=h
    return result
EI=json.loads((SRC/'resultados/vida_integral/EI_D01/MEDICIONES.json').read_text(encoding='utf8'))
cases=[]
groups={'M035':('vida_integral',['EI_D01','EI_C01_NO_COUNT_FORM','EI_C02_QUERY_KNOWN','EI_C03_NO_ORDER_A','EI_C04_NO_TM_R','EI_C05_RCA_OFFPATH','EI_R31_REVERSED_COMBINATION','EI_R32_NEW_COMBINATION']),
        'M036':('continuacion',['E1_MAIN_884_1220','E1_CF_OFFPATH_884_1220']),
        'M037':('retorno',['RET_D01_P','RET_D02_M','RET_C01_NOFORM','RET_C02_UNPAIRED','RET_C03_NOQUERY','RET_R01_SOURCE17_OBJECT9','RET_R02_SOURCE17_OBJECT27','RET_R03_SOURCE31_OBJECT42','RET_V3_R31_SOURCE23_OBJECT16','RET_V3_R32_SOURCE23_OBJECT35']),
        'M038':('repertorio_n67',['KN_D01_K8','KN_D02_K65','KN_C03_K65_NO_EVENT','KN_C04_K65_UNPAIRED','KN_R31_K65_OPPOSITE'])}
for ident,(group,names) in groups.items():
    for case in names:
        primary=SRC/'resultados'/group/case/'MEDICIONES.json';d=json.loads(primary.read_text(encoding='utf8'))
        base='cpc9/realizaciones/'+case;ref='cpc9/primarios/'+case+'/MEDICIONES.json'
        h=file(ref,primary);source_map=versions(d,base)
        if not source_map:
            source_map=versions(EI,base)
        # Estos dos runners posteriores no estaban todavía presentes en el mapa
        # de fuentes de EI_D01. Se conservan los bytes del expediente cerrado.
        entry={'M035':'ejecutar_vida_integral.py','M036':'continuar_e1.py','M037':'ejecutar_retorno.py','M038':'ejecutar_repertorio_n67.py'}[ident]
        for n in [entry,'repertorio_n67.py','ejecutar_retorno.py'] if ident=='M038' else [entry]:
            rel='src/'+n
            if rel not in source_map:source_map[rel]=file(base+'/'+rel,SRC/rel)
        if ident=='M038':assert source_map['src/repertorio_n67.py']==d['source_sha256']
        cfg=dict(d.get('configuration',d.get('config',{})));cfg.pop('out',None);cfg.pop('parent',None)
        item={'mechanism':ident,'id':case,'group':group,'source_root':base,'entry':'src/'+entry,'reference':ref,'reference_sha256':h,'input_configuration':cfg,'source_versions':source_map}
        if ident=='M036':item['parent_snapshot']='cpc9/estados/EI_D01_T884.deetsnap.gz'
        cases.append(item)
file('cpc9/estados/EI_D01_T884.deetsnap.gz',SRC/'resultados/vida_integral/EI_D01/T884.deetsnap.gz')
for ident,case,source_group,source_case,entry,snapshot in [
    ('M037','RET_CAUSAL','retorno','RET_D01_P','causal_retorno.py','T148.deetsnap.gz'),
    ('M037','RET_CAUSAL_MINUS','retorno','RET_D02_M','causal_retorno.py','T148.deetsnap.gz'),
    ('M038','KN_CAUSAL_F00','repertorio_n67','KN_D02_K65','causal_repertorio_n67.py','T310.deetsnap.gz')]:
    parent=next(x for x in cases if x['id']==source_case);base='cpc9/realizaciones/'+case
    d=json.loads((SRC/'resultados'/source_group/source_case/'MEDICIONES.json').read_text(encoding='utf8'));source_map=versions(d if d.get('source_hashes') else EI,base)
    for n in [entry,'ejecutar_retorno.py']+(['repertorio_n67.py'] if ident=='M038' else []):
        rel='src/'+n
        if rel not in source_map:source_map[rel]=file(base+'/'+rel,SRC/rel)
    for n in ['MEDICIONES.json',snapshot]:file(base+'/resultados/'+source_group+'/'+source_case+'/'+n,SRC/'resultados'/source_group/source_case/n)
    ref='cpc9/primarios/'+case+'/MEDICIONES.json';h=file(ref,SRC/'resultados'/source_group/case/'MEDICIONES.json')
    cases.append({'mechanism':ident,'id':case,'group':'causal_'+source_group,'source_root':base,'entry':'src/'+entry,'reference':ref,'reference_sha256':h,'input_configuration':{'case' if ident=='M037' else 'source':source_case},'source_versions':source_map})
# Preservar la evidencia adversa de la continuidad tardía sin venderla como un
# nuevo mecanismo positivo: recálculo/consulta archivada, no nueva vida ni éxitos.
for rel in ['resultados/continuacion/E1_MAIN_K65_1907_2353/MEDICIONES.json','resultados/continuacion/E1_CF_K65_NO_EVENT/MEDICIONES.json','resultados/continuacion/E1_CF_K65_UNPAIRED/MEDICIONES.json','resultados/continuacion/E1_MAIN_TAIL_2353_2493/MEDICIONES.json','resultados/continuacion/E1_TAIL_NO_NEW/MEDICIONES.json']:
    file('cpc9/limites/'+Path(rel).parent.name+'/MEDICIONES.json',SRC/rel)
temp=STORE.with_suffix('.nuevo.gz');seen={r['sha256'] for r in json.loads(INDEX.read_text(encoding='utf8'))['paths'].values()}
with gzip.open(STORE,'rb') as src,temp.open('wb') as raw:
    with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,compresslevel=9) as dst:
        shutil.copyfileobj(src,dst)
        for h,data in added.items():
            if h in seen:continue
            row={'sha256':h,'bytes':len(data),'base64':base64.b64encode(data).decode('ascii')};dst.write((json.dumps(row,separators=(',',':'))+'\n').encode('ascii'))
temp.replace(STORE);index['paths']=paths;index['content_store_sha256']=digest(STORE.read_bytes());INDEX.write_text(json.dumps(index,ensure_ascii=False,separators=(',',':')),encoding='utf8')
(STAGE/'configuraciones/CPC9_RECUPERACION.json').write_text(json.dumps({'cases':cases,'compare':'Exact geometry, all native frames, local windows, requests and final physical state; host output paths/timestamps and container metadata treated separately.'},ensure_ascii=False,indent=2),encoding='utf8')
(WORK/'cpc9_sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'cases':len(cases),'paths':len(paths),'store_bytes':STORE.stat().st_size,'added_unique_bytes':sum(len(x) for x in added.values())},ensure_ascii=False))
