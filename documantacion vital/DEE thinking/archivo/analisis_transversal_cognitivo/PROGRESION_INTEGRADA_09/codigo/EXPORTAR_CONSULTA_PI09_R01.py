"""Copy literal PI09 primaries/witnesses/products to a small new bundle.
Only closed-file reads and byte copies; no Native, DEE, Runtime or SQLite.
Default all four fixed tags; --primario accepts extra bounded P9 filenames/
globs so a failed attempt with null result is never silently discarded.
"""
from pathlib import Path
import argparse,hashlib,json,re,shutil
P=Path(__file__).resolve().parents[1]
VERSION='DEE.PI09.selective_registered_consultation.R01'
VERSIONS={VERSION,'DEE.PI09.selective_registered_consultation.R02'}
TAGS={'native_real':['PI09_NATIVE_R02','PI09_NATIVE_R03'],'always_real':['PI09_ALWAYS_R02','PI09_ALWAYS_R03'],'never':['PI09_NEVER_R02','PI09_NEVER_R03'],'always_desacoplado':['PI09_YOKE_R02','PI09_YOKE_R03']}
def require(ok,why):
    if not ok:raise ValueError(why)
def digest(file):return hashlib.sha256(Path(file).read_bytes()).hexdigest()
def rows(primary):
    value=primary.get('result');value=json.loads(value)if isinstance(value,str)else value
    return []if value is None else value.get('result',value).get('rows',[])
def prefix_role(value):
    if '='in value:
        role,tag=value.split('=',1)
    else:
        tag=value;role=next((r for token,r in [('NATIVE','native_real'),('ALWAYS','always_real'),('NEVER','never'),('YOKE','always_desacoplado')]if tag.startswith('PI09_'+token+'_')),None)
    require(role in {*TAGS,'native_desacoplado','native_reproduction'}and re.fullmatch(r'[A-Za-z0-9_]+',tag)is not None,'Bounded explicit role=TAG or known PI09 arm tag only')
    return role,tag
def main(args):
    dest=Path(args.destino).absolute();require(dest.is_relative_to(P.resolve())and not dest.exists(),'New compact destination inside PI09 only');dest.mkdir(parents=True)
    systems={}
    for value in args.sistema:
        role,path=value.split('=',1);require(role not in systems and role in {*TAGS,'native_desacoplado','native_reproduction'},'Exact one system per arm');systems[role]=Path(path).resolve(strict=True)
    def member(source,name,**extra):
        source=Path(source);require(not source.is_symlink()and source.is_file(),'Literal regular source file only');target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():require(digest(target)==digest(source),'Conflicting compact member')
        else:shutil.copyfile(source,target)
        require(digest(target)==digest(source),'Copied literal differs')
        return {'file':name,'bytes':target.stat().st_size,'sha256':digest(target),'source_reference_for_packager_only':str(source),**extra}
    index={'schema':'DEE.PI09.consultation.portable_primary_index.R01','Native_executed':False,'protocol':member(P/'codigo/PROTOCOLO_PI09_CONSULTA_R01.json','PROTOCOLO_PI09_CONSULTA_R01.json'),'primaries':[],'witnesses':[],'products':[],'all_errors_retained':True,'controls':[]}
    selected={}
    require(not args.solo_prefijos or args.prefijo,'Explicit prefix required for isolated sub-bundle')
    prefixes=[]if args.solo_prefijos else[(role,tag)for role,tags in TAGS.items()for tag in tags]
    prefixes.extend(prefix_role(value)for value in args.prefijo)
    for role,tag in prefixes:
        for file in sorted((P/'ensayos').glob(tag+'*.json')):
            require(file not in selected or selected[file]==role,'Same primary cannot be assigned to different arms');selected[file]=role
    for pattern in args.primario:
        require('..'not in Path(pattern).parts and not Path(pattern).is_absolute()and'/'not in pattern and'\\'not in pattern,'Extra primary glob must be bounded to P9/ensayos')
        for file in sorted((P/'ensayos').glob(pattern)):
            require(file.suffix=='.json','Literal primary JSON only')
            if file not in selected:
                data=json.loads(file.read_bytes());rr=rows(data);role=next((r.get('arm')for r in rr if r.get('arm')),None)
                require(role in systems,'Extra primary without role requires a declared system and arm in result');selected[file]=role
    witness_keys=set();product_keys=set()
    for file,role in sorted(selected.items()):
        data=json.loads(file.read_bytes());rr=rows(data);index['primaries'].append(member(file,'PRIMARIOS/'+file.name,arm=role))
        for row in rr:
            if row.get('version')not in VERSIONS or'first_stage'not in row:continue
            require(role in systems,'Provide --sistema '+role+'=<actual closed system> for witnesses/products')
            life=row['life_id'];folder='PI09_CONSULTA_SELECTIVA_R02'if row['version'].endswith('.R02')else'PI09_CONSULTA_SELECTIVA_R01';home=systems[role]/'estado/servicios_locales'/life/folder
            pointer=row['external_immediate_first_stage_witness'];require(Path(pointer['file']).name==pointer['file'],'Fixed witness basename only');source=home/pointer['file']
            require(source.stat().st_size==pointer['bytes']and digest(source)==pointer['sha256'],'Actual immediate witness differs')
            key=(role,pointer['file'])
            if key not in witness_keys:index['witnesses'].append(member(source,'TESTIGOS/'+role+'/'+pointer['file'],arm=role));witness_keys.add(key)
            artifact=row['second_stage']['message']['artifact']
            if artifact:
                require(artifact['file']=='mensaje_%04d.bin'%row['ordinal'],'Actual product basename/ordinal differs');source=home/artifact['file'];require(source.stat().st_size==64 and digest(source)==artifact['sha256'],'Actual Native64B product differs')
                key=(role,artifact['file'])
                if key not in product_keys:index['products'].append(member(source,'PRODUCTOS/'+role+'/'+artifact['file'],arm=role));product_keys.add(key)
    # Also preserve witnesses preceding a failed outer result. No invented stage2.
    for role,system in systems.items():
        roots=system/'estado/servicios_locales'
        if not roots.exists():continue
        for home in sorted([*roots.glob('*/PI09_CONSULTA_SELECTIVA_R01'),*roots.glob('*/PI09_CONSULTA_SELECTIVA_R02')]):
            for source in sorted(home.glob('primera_C_??_q*.json')):
                key=(role,source.name)
                if key not in witness_keys:index['witnesses'].append(member(source,'TESTIGOS/'+role+'/'+source.name,arm=role));witness_keys.add(key)
    for value in args.control:
        source=Path(value).resolve(strict=True);require(source.is_relative_to(P.resolve()),'Control source must remain in PI09');index['controls'].append(member(source,'CONTROLES/'+source.name))
    for name in('SELLO_PI09_CONSULTA_R01.json','SELLO_PI09_CONSULTA_R02.json'):
        source=P/'codigo'/name
        if source.exists():index['controls'].append(member(source,'CONTROLES/'+name))
    for name in('RECALCULAR_CONSULTA_PI09_R01.py','RECALCULAR_C_PI08_LITERAL.py','RECALCULAR_PRIMARIOS_PI07_LITERAL.py'):
        member(P/'codigo'/name,name)
    file=dest/'INDICE_PI09_CONSULTA_R01.json'
    with file.open('x',encoding='utf8')as f:json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'index':str(file),'sha256':digest(file),'primaries':len(index['primaries']),'witnesses':len(index['witnesses']),'products':len(index['products']),'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--destino',required=True);ap.add_argument('--sistema',action='append',default=[]);ap.add_argument('--prefijo',action='append',default=[],help='Additional bounded TAG or arm=TAG; defaults retain both R02 and R03 attempts');ap.add_argument('--solo-prefijos',action='store_true',help='Isolated RP sub-bundle from explicit prefixes only; main expedition export keeps all default adverse attempts');ap.add_argument('--primario',action='append',default=[]);ap.add_argument('--control',action='append',default=[]);main(ap.parse_args())
