"""Export every published C attempt and immediate witness, including failures.

One fixed diagnostic life/home, six fixed episode IDs. No favourable subset,
Native import, state intervention or claim that an unfinished attempt completed.
"""
from pathlib import Path
import argparse,hashlib,json,shutil

P=Path(__file__).resolve().parents[1];LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01'
HOME=P/'estados/C_R03/sistema/estado/servicios_locales'/LIFE/'PI08_CONSULTA_CONDICIONAL_C_R02'
def require(ok,message):
    if not ok:raise ValueError(message)
def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def unwrap(primary):
    value=primary.get('result');value=json.loads(value)if isinstance(value,str)else value
    return value['result']['rows'][0]if value is not None else None
def main(args):
    dest=Path(args.destino).absolute();require(dest.is_relative_to(P.resolve()),'Compact C export must stay in PI08')
    require(not dest.exists()or(dest.is_dir()and not any(dest.iterdir())),'New empty output only')
    dest.mkdir(parents=True,exist_ok=True)
    def member(source,relative):
        source=Path(source);target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():require(sha(target)==sha(source),'Conflicting compact member')
        else:shutil.copyfile(source,target)
        require(sha(target)==sha(source),'Copied bytes differ')
        return{'file':relative,'bytes':target.stat().st_size,'sha256':sha(target),'source_reference_for_packager_only':str(source)}
    index={'schema':'DEE.PI08.C.portable_primary_index.R03','Native_executed':False,'life_id':LIFE,
       'protocol':member(P/'codigo/PROTOCOLO_PI08_C_R02.json','PROTOCOLO_PI08_C_R02.json'),
       'seal':member(P/'codigo/SELLO_PI08_C_R03.json','SELLO_PI08_C_R03.json'),
       'episode_primaries':[],'immediate_witnesses':[],'products':[],'owner_or_all_six_completion_not_assumed':True}
    prep=P/'ensayos/PI08_C_PREPARAR_R04_preparar.json'
    require(prep.is_file(),'The actual preparation attempt must be preserved')
    index['preparation_primary']=member(prep,'PRIMARIOS/'+prep.name)
    products=set();seen_missing=False;attempts=[]
    for i in range(6):
        file=P/'ensayos'/('PI08_C_EVALUAR_R04_EP%02d.json'%i)
        if not file.exists():seen_missing=True;continue
        require(not seen_missing,'Missing intermediate C attempt; never choose favourable episodes')
        primary=read(file);require(primary['status']in('completed','failed_preserved','uncertain','rejected_invalid'),'C attempt not terminal/preserved')
        index['episode_primaries'].append(member(file,'PRIMARIOS/'+file.name));attempts.append({'ordinal':i,'status':primary['status'],'error':primary.get('error')})
        row=unwrap(primary)
        if row and'second_stage'in row:
            require(row['ordinal']==i and row['life_id']==LIFE,'Actual C life/ordinal differs')
            artifact=row['second_stage']['message']['artifact']
            if artifact:
                source=HOME/artifact['file'];require(source.is_file()and source.stat().st_size==64 and sha(source)==artifact['sha256'],'Actual secondstage artifact absent/different')
                if artifact['sha256']not in products:index['products'].append(member(source,'PRODUCTOS/'+artifact['file']));products.add(artifact['sha256'])
    if HOME.exists():
        for file in sorted(HOME.glob('primera_C_??_q*.json')):
            witness=read(file);require(witness['schema']=='DEE.PI08.C.immediate_first_stage_witness.R03'and 0<=witness['ordinal']<6,'Only the bounded actual immediate witnesses')
            require(file.name=='primera_C_%02d_q%d.json'%(witness['ordinal'],witness['query_tick']),'Witness name/ordinal/query mismatch')
            index['immediate_witnesses'].append(member(file,'TESTIGOS/'+file.name))
    for phase in('PREPARAR','EVALUAR'):
        proof=P/'control'/('PI08_C_'+phase+'_R04.json')
        if proof.exists():index[phase.lower()+'_summary']=member(proof,'CONTROLES/'+proof.name)
    startup=P/'control/PI08_C_PREPARAR_R03.json'
    if startup.exists():index['preserved_zero_Native_startup_failure']=member(startup,'CONTROLES/'+startup.name)
    index['attempts']=attempts
    file=dest/'INDICE_C_PI08_R03.json'
    with file.open('x',encoding='utf8')as out:json.dump(index,out,ensure_ascii=False,indent=2);out.write('\n')
    member(P/'codigo/RECALCULAR_C_PI08_R03.py','RECALCULAR_C_PI08_R03.py')
    member(P/'codigo/heredado/RECALCULAR_PRIMARIOS_PI07_LITERAL.py','RECALCULAR_PRIMARIOS_PI07_LITERAL.py')
    print(json.dumps({'index':str(file),'sha256':sha(file),'episode_attempts':len(attempts),'immediate_witnesses':len(index['immediate_witnesses']),'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--destino',required=True);main(parser.parse_args())
