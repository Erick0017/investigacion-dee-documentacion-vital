"""Index/copy only completed B primaries and actual64B products. Native0.

Explicit role=tag arguments prevent recursive scans or selecting favourable
episodes. --parcial permits an unfinished arm's *closed* published episodes,
without representing its owner/arm as closed. Original absolute references
travel only as provenance and are never opened by the portable comparator.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil

P=Path(__file__).resolve().parents[1];VERSION='DEE.PI08.successive_contextual_regulation.B.R01'
def require(ok,message):
    if not ok:raise ValueError(message)
def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def one(path):
    raw=read(path);require(raw['status']=='completed'and not raw.get('error'),'Only completed actual primary')
    value=raw['result'];value=json.loads(value)if isinstance(value,str)else value
    row=value['result']['rows'][0];require(row['version']==VERSION,'Only Bversion actual episodes')
    return row
def main(args):
    dest=Path(args.destino).absolute();require(dest.is_relative_to(P.resolve()),'Compact export stays in PI08')
    require(not dest.exists()or(dest.is_dir()and not any(dest.iterdir())),'New empty export destination only')
    mapping={}
    for value in args.brazo:
        role,tag=value.split('=',1);require(role in('real','none','yoked','reference')and role not in mapping,'Explicit unique arm')
        require(re.fullmatch(r'PI08_B_[A-Za-z0-9_]{1,40}',tag),'Fixed bounded exact primary tag')
        mapping[role]=tag
    dest.mkdir(parents=True,exist_ok=True)
    def member(source,relative):
        source=Path(source);target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():require(sha(target)==sha(source),'Different existing compact member')
        else:shutil.copyfile(source,target)
        require(sha(target)==sha(source),'Copied member differs')
        return{'file':relative,'bytes':target.stat().st_size,'sha256':sha(target),'source_reference_for_packager_only':str(source)}
    index={'schema':'DEE.PI08.B.portable_primary_index.R01','Native_executed':False,'arms':{},
           'protocol':member(P/'codigo/PROTOCOLO_PI08_B_R01.json','PROTOCOLO_PI08_B_R01.json'),
           'seal':member(P/'codigo/SELLO_PI08_B_R01.json','SELLO_PI08_B_R01.json')}
    for role,tag in mapping.items():
        summarypath=P/'control'/(tag+'.json');summary=read(summarypath)if summarypath.exists()else None
        closed=bool(summary and summary.get('closed')and summary.get('status')=='CLOSED_18_OPPORTUNITIES'and summary.get('error')is None)
        require(closed or args.parcial,'Wait for actual closed18 or explicitly request partial published episodes')
        arm={'status':'CLOSED18'if closed else'PARTIAL_PUBLISHED_EPISODES_OWNER_NOT_ASSERTED_CLOSED','primaries':[],'products':[]}
        if summary:arm['summary']=member(summarypath,'CONTROLES/'+summarypath.name)
        products=set();life=None
        for i in range(18):
            primary=P/'ensayos'/(tag+'_EP%02d.json'%i)
            if not primary.exists():break
            row=one(primary);require(row['feedback_arm']==role and row['B_ordinal']==i,'Role/index mismatch')
            require(life in(None,row['life_id']),'Mixed source lives');life=row['life_id']
            arm['primaries'].append(member(primary,'PRIMARIOS/'+primary.name))
            artifact=row['message']['artifact']
            if artifact:
                homes=list((P/'estados').glob('*/sistema/estado/servicios_locales/'+life+'/PI08_REGULACION_FLEXIBLE_B_R01'))
                require(len(homes)==1,'One complete diagnostic owner home, no branch substitution')
                source=homes[0]/artifact['file'];require(source.stat().st_size==64 and sha(source)==artifact['sha256'],'Actual Native artifact differs')
                if artifact['sha256']not in products:
                    arm['products'].append(member(source,'PRODUCTOS/'+role+'/'+artifact['file']));products.add(artifact['sha256'])
        require(len(arm['primaries'])==18 if closed else len(arm['primaries'])>0,'No missing closed material episode')
        if role=='yoked':arm['yoked_plan']=member(P/'control/PLAN_YOKE18_B_PI08_R01.json','PLAN_YOKE18_B_PI08_R01.json')
        index['arms'][role]=arm
    file=dest/'INDICE_B_PI08_R01.json'
    with file.open('x',encoding='utf8')as out:json.dump(index,out,ensure_ascii=False,indent=2);out.write('\n')
    # Recalculation requires no source files outside the exported directory.
    member(P/'codigo/RECALCULAR_B_PI08_R01.py','RECALCULAR_B_PI08_R01.py')
    member(P/'codigo/heredado/RECALCULAR_PRIMARIOS_PI07_LITERAL.py','RECALCULAR_PRIMARIOS_PI07_LITERAL.py')
    print(json.dumps({'index':str(file),'sha256':sha(file),'arms':{role:len(arm['primaries'])for role,arm in index['arms'].items()},'Native_executed':False},ensure_ascii=False,indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--destino',required=True);parser.add_argument('--brazo',action='append',required=True,help='role=exactactualprimarytag');parser.add_argument('--parcial',action='store_true');main(parser.parse_args())
