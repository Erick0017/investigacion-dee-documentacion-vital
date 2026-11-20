"""Copy only explicitly CLOSED D phase primaries/full witnesses/products.

Missing or unclosed closure => WAIT before any system/home read or output write.
Use repeat --cierre role=proof and --sistema role=closed-system. No glob guessing,
world/card/SQLite/DEE/Native access; all adverse recorded attempts are retained.
"""
from pathlib import Path
import argparse,hashlib,json,re,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';VERSION='DEE.PI09.persistent_environment.D.R02';FOLDER='PI09_ENTORNO_PERSISTENTE_D_R02';ROLES={'real','none','yoked','real_reproduction'}
def require(ok,why):
    if not ok:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rr(v):
    x=v.get('result');x=json.loads(x)if isinstance(x,str)else x
    return []if x is None else x.get('result',x).get('rows',[])
def assignments(values):
    out=[]
    for value in values:
        role,path=value.split('=',1);require(role in ROLES,'Fixed D role only');out.append((role,Path(path).absolute()))
    return out
def export(a):
    sources=assignments(a.cierre);require(sources,'At least one explicit closed D phase required');missing=[{'arm':role,'path':str(path)}for role,path in sources if not path.is_file()]
    if missing:return {'status':'WAIT','missing_closed_inputs':missing,'output_written':False,'Native_executed':False}
    closures=[]
    for role,path in sources:
        require(path.resolve().is_relative_to((P/'control').resolve()),'Closure must be actual PI09/control file');value=read(path)
        if value.get('closed')is not True:return {'status':'WAIT','reason':'Explicit D owner closure is absent; no source/system read','arm':role,'closure':str(path),'output_written':False,'Native_executed':False}
        require(value.get('schema')in('DEE.PI09.D.actual.finite_owner_phase.R02','DEE.PI09.D.actual.finite_owner_phase.R03'),'Recognized closed finite D driver witness only')
        require(value.get('arm')==('real'if role=='real_reproduction'else role),'Closed proof role mismatch');closures.append((role,path,value))
    systems=dict(assignments(a.sistema));require(len(systems)==len(a.sistema),'One system per explicit role')
    dest=Path(a.destino).absolute();require(dest.is_relative_to(P.resolve())and not dest.exists(),'New compact PI09 destination only')
    # All closure decisions precede the first system/home access and mkdir.
    for role,system in systems.items():require(system.resolve(strict=True).name=='sistema'and system.resolve().is_relative_to((P/'estados').resolve()),'Explicit closed isolated system only')
    dest.mkdir(parents=True);copied={}
    def member(source,name,**extra):
        source=Path(source).resolve(strict=True);require(source.is_file()and not source.is_symlink(),'Literal regular evidence');data=source.read_bytes();target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
        require(name not in copied or copied[name]==sha(source),'Conflicting member aliases')
        if not target.exists():
            with target.open('xb')as f:f.write(data)
        require(target.read_bytes()==data,'Copied literal bytes changed');copied[name]=sha(source)
        return {'file':name,'bytes':len(data),'sha256':copied[name],'source_reference_for_packager_only':str(source),**extra}
    index={'schema':'DEE.PI09.D.portable_primary_index.R02','Native_executed':False,'protocol':member(H/'PROTOCOLO_PI09_D_R02.json','PROTOCOLO_PI09_D_R02.json'),'closures':[],'plans':[],'primaries':[],'witnesses':[],'products':[],'all_recorded_adverse_attempts_retained':True,'future6_separated_from_evaluation6':True}
    primary_seen=set();witness_seen=set();product_seen=set();homes={}
    for role,path,closure in closures:
        index['closures'].append(member(path,'CIERRES/'+role+'/'+path.name,arm=role));plan=Path(closure['plan']).resolve(strict=True)
        require(sha(plan)==closure['plan_sha256']and plan.is_relative_to(H.resolve()),'Actual pinned prospective plan changed')
        index['plans'].append(member(plan,'PLANES/'+role+'/'+plan.name,arm=role))
        for record in closure['records']:
            source=Path(record['primary']).resolve(strict=True);require(source.is_relative_to((P/'ensayos').resolve())and sha(source)==record['sha256'],'Actual closed record primary changed/outside ensayos')
            if(role,str(source))in primary_seen:continue
            primary_seen.add((role,str(source)));index['primaries'].append(member(source,'PRIMARIOS/'+role+'/'+source.name,arm=role));primary=read(source)
            for row in rr(primary):
                if row.get('version')!=VERSION or'first_stage'not in row:continue
                require(role in systems,'Explicit closed system required for full immediate witness/product')
                home=systems[role]/'estado/servicios_locales'/row['life_id']/FOLDER;homes[role,row['life_id']]=home
                ptr=row['external_immediate_first_stage_witness'];require(Path(ptr['file']).name==ptr['file'],'Witness basename');w=home/ptr['file'];require(w.stat().st_size==ptr['bytes']and sha(w)==ptr['sha256'],'Immediate witness changed')
                key=(role,w.name)
                if key not in witness_seen:index['witnesses'].append(member(w,'TESTIGOS/'+role+'/'+w.name,arm=role));witness_seen.add(key)
                artifact=row['second_stage']['message']['artifact']
                if artifact:
                    require(artifact['file']=='mensaje_%04d.bin'%row['ordinal'],'Fixed product ordinal');product=home/artifact['file'];require(product.stat().st_size==64 and sha(product)==artifact['sha256'],'Actual material64B product changed')
                    key=(role,product.name)
                    if key not in product_seen:index['products'].append(member(product,'PRODUCTOS/'+role+'/'+product.name,arm=role));product_seen.add(key)
        # Preserve immediate witnesses preceding any failed outer result as well.
        if role in systems:
            home=systems[role]/'estado/servicios_locales'/closure['life_id']/FOLDER
            if home.exists():
                for w in sorted(home.glob('primera_C_??_q*.json')):
                    key=(role,w.name)
                    if key not in witness_seen:index['witnesses'].append(member(w,'TESTIGOS/'+role+'/'+w.name,arm=role));witness_seen.add(key)
    for name in('RECALCULAR_D_PI09_R02.py','RECALCULAR_CONSULTA_PI09_R01.py','RECALCULAR_C_PI08_LITERAL.py','RECALCULAR_PRIMARIOS_PI07_LITERAL.py'):member(H/name,name)
    out=dest/'INDICE_D_PI09_R02.json'
    with out.open('x',encoding='utf8')as f:json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
    return {'status':'EXPORTED_CLOSED_LITERALS','index':str(out),'sha256':sha(out),'primaries':len(index['primaries']),'witnesses':len(index['witnesses']),'products':len(index['products']),'Native_executed':False}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--destino',required=True);ap.add_argument('--cierre',action='append',default=[]);ap.add_argument('--sistema',action='append',default=[]);a=ap.parse_args();print(json.dumps(export(a),ensure_ascii=False))
