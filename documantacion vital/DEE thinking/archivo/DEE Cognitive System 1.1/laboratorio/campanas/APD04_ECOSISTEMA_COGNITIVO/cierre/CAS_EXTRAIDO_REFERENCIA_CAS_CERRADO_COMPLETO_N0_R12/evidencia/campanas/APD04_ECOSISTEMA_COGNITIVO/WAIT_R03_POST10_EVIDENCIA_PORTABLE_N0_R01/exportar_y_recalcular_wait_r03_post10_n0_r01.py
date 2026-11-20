"""N0 compact export and independent record arithmetic for two closed ACT_R03 originals.

Never queries a live participant, imports Native, advances ticks or changes a
criterion. RAW actuator formation is recalculated from the fixed three gates.
Old work gain remains separate from the new postaction WAIT-quality contract.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
S=ROOT/'sistema'
EV=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
OUT=EV/'WAIT_R03_POST10_EVIDENCIA_PORTABLE_N0_R01'
BUNDLE=HERE/'EJECUTOR_WAIT_R03_SAFE_R03'
PARENT=S/'estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01'


def read(path):return json.loads(Path(path).read_bytes())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def emit(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m


def walk(value):
    if isinstance(value,dict):
        yield value
        for item in value.values():yield from walk(item)
    elif isinstance(value,list):
        for item in value:yield from walk(item)


def fields(raw):
    raw=int(raw)
    def signed(shift):
        v=(raw>>shift)&15
        return v-16 if v&8 else v
    return {'state':raw&0xffffffff,'semantic':(raw>>60)&15,
        'direction':[signed(s)for s in(48,52,56)],'s_reg':(raw>>32)&65535}


def native_selection(row):
    observations=row['selection']['reader']['observations']
    if len(observations)!=3:raise ValueError('Historical fixed three-gate reader required.')
    candidates=[]
    for sign,observation in zip((-1,0,1),observations):
        f=fields(observation['raw'])
        for key in('state','semantic','direction','s_reg'):
            if f[key]!=observation[key]:raise ValueError('RAW disagrees with exported field: '+key)
        if f['state']>0 and f['semantic']==1 and f['direction']==[sign,1,0]:candidates.append(sign)
    formed=len(candidates)==1
    actual=candidates[0]if formed else None
    if actual!=row['selection']['physical_choice']:raise ValueError('RAW fixed reader disagrees with emitted Native choice.')
    return actual,formed,observations


def receipts(primary):
    items={}
    for item in walk(primary):
        if 'id'in item and('port'in item or'channel'in item)and isinstance(item.get('receipt'),dict):
            identifier=int(item['id']);status=item['receipt']['status'];old=items.get(identifier)
            if old and status in('scheduled','queued'):continue
            current={'id':identifier,'channel':item.get('channel',item.get('port')),
                'representation':'channel'if'channel'in item else'port','status':status,
                'value':item.get('payload',item.get('value')),'tick':item['tick']}
            if old and old['channel']!=current['channel']:raise ValueError('One Native ID names different channels.')
            items[identifier]=current
    return items


def recalculate(directory):
    index=read(directory/'INDICE.json');summaries=[];all_rows={}
    for branch,info in index['branches'].items():
        rows=[];inputs={};groups={'ten_work':{},'other_preparation':{}}
        for item in info['primaries']:
            path=directory/item['file']
            if sha(path)!=item['sha256']:raise ValueError('Primary original bytes changed.')
            primary=read(path);part=receipts(primary)
            group='ten_work'if'opportunity_'in primary['id']else'other_preparation'
            groups[group].update(part);inputs.update(part)
            for block in primary['result'].get('rows',[]):
                if not block.get('kind','').startswith('APD04.shared_workshop'):continue
                for row in block.get('rows',[]):
                    sign,formed,observations=native_selection(row)
                    action={-1:'INSPECT',0:'WAIT',1:'USE'}.get(sign)
                    assert action==row['physical_action']
                    q=row['posteffect_quality'];effect=row['committed_effect'];before=q['task_env_before'];after=q['task_env_after']
                    source=row['public_before']['source_id'];obj_before=next(o for o in before['objects']if o['id']==source);obj_after=next(o for o in after['objects']if o['id']==source)
                    relevant=obj_before['tag']==row['public_before']['goal_tag']
                    if action=='INSPECT':
                        old_gain=(obj_before['observed']!=obj_after['observed'])and relevant
                        assert obj_after['observed']=={'value':obj_before['value'],'version':obj_before['version']}
                    elif action=='USE':
                        if row['native_operation']is None:old_gain=False
                        elif 'loads_before'in effect:
                            old_gap=abs(before['loads'][0]-before['loads'][1]);new_gap=abs(after['loads'][0]-after['loads'][1])
                            direction=row['native_operation']['physical_choice']
                            old_gain=(new_gap<old_gap or(direction==0 and old_gap==0))and relevant
                        else:
                            direction=row['native_operation']['physical_choice'];value=obj_before['value'];criterion=row['auditor_only_after_effect']['criterion']
                            expected=(value>criterion)-(value<criterion)
                            fresh=obj_before['observed']is not None and obj_before['observed']['version']==obj_before['version']
                            old_gain=direction in(-1,0,1)and direction==expected and fresh and relevant and obj_before['bin']!=obj_after['bin']
                    else:old_gain=False
                    quality=formed and ((sign==0 and not relevant and before==after)if action=='WAIT'else bool(old_gain))
                    if bool(old_gain)!=effect['old_work_gain']or bool(old_gain)!=effect['useful']or bool(quality)!=effect['new_quality']or bool(quality)!=q['new_quality']:
                        raise ValueError('Postaction record arithmetic mismatch.')
                    if row['feedback']['category']!=('SUCCESS'if quality else'FAILURE'):raise ValueError('Feedback category mismatch.')
                    rows.append({'request_id':primary['id'],'episode':row['episode'],'query_tick':row['selection']['query_tick'],
                        'raw_components':row['raw_sensor_components'],'source':source,'public_before':row['public_before'],
                        'Native_choice':sign,'formed_unique_from_RAW':formed,'action':action,'old_work_gain':bool(old_gain),
                        'new_quality':bool(quality),'feedback':row['feedback'],'primary':item['file'],
                        'RAW_fixed_gate_witness':observations,'environment_unchanged':before==after})
        native_delta=read(directory/info['full_receipts_delta'])
        assert set(inputs)=={int(r['id'])for r in native_delta['new_receipts']}
        assert native_delta['parent_receipts_exactly_preserved']
        all_rows[branch]=rows
        summaries.append({'branch':branch,'work_requests_completed':len(rows),
            'Native_formed':sum(r['formed_unique_from_RAW']for r in rows),'NULL_or_ambiguous':sum(not r['formed_unique_from_RAW']for r in rows),
            'actions':dict(Counter(r['action']for r in rows)),'old_work_gain':sum(r['old_work_gain']for r in rows),
            'new_quality':sum(r['new_quality']for r in rows),'Native_receipts':len(inputs),
            'receipt_statuses':dict(Counter(r['status']for r in inputs.values())),
            'receipt_schema_forms':dict(Counter(r['representation']for r in inputs.values())),
            'groups':{key:{'unique':len(value),'statuses':dict(Counter(r['status']for r in value.values()))}for key,value in groups.items()},'rows':rows})
    first_difference=None
    for number,(real,omit)in enumerate(zip(all_rows['REAL'],all_rows['OMIT']),1):
        if real['Native_choice']!=omit['Native_choice']:
            first_difference={'opportunity':number,'same_query_tick':real['query_tick']==omit['query_tick'],
                'same_raw_components':real['raw_components']==omit['raw_components'],
                'same_public_before':real['public_before']==omit['public_before'],'REAL':real,'OMIT':omit};break
    return {'schema':'APD04.ACT_R03.post10.primary_recalculation.N0.v1','new_native_ticks':0,
        'Native_imported':False,'fixed_reader_from_exact_RAW_not_NULL_as_zero':True,
        'old_gain_and_new_quality_separate':True,'branches':summaries,'first_Native_difference':first_difference,
        'scope':'Arithmetic from original primary records and exact RAW witnesses, not Native replay, policy generality or recovery of unobserved states.'}


def export():
    if OUT.exists():raise FileExistsError('Preserve the existing export; no overwrite.')
    finals={}
    for branch in('REAL','OMIT'):
        attempt=EV/f'WAIT_R03_{branch}_ORIGINAL_R03';final=read(attempt/'TRAYECTORIA/RESULTADO.json')
        if final['error']or not final['owner_stop_confirmed']or final['final_protocol'].get('pending_material')or final['final_protocol'].get('uncertain_preserved'):
            raise ValueError('A partial/adverse future needs a separately labelled export, not this closed post10 export.')
        finals[branch]=final
        assert(attempt/'SELLO_POST10_N0/CORTE_COMPLETO_POSTSTOP.json').is_file()
    OUT.mkdir()
    observer=load('wait_r03_export_pure_saved_observer',S/'capacidades/observador_causal_retrospectivo_01.py')
    parent=observer.Snapshot(PARENT/'VIDA.deetsnap.gz',verify_checksum=False)
    branches={};sources={};omitted=[]
    for branch,final in finals.items():
        attempt=EV/f'WAIT_R03_{branch}_ORIGINAL_R03';life=final['life'];folder=OUT/branch;folder.mkdir()
        emit(folder/'CORTE_ORIGINAL.json',{'record':final['final_record'],'protocol':final['final_protocol'],
            'source_result_sha256':sha(attempt/'TRAYECTORIA/RESULTADO.json'),'not_current_live_VIDA':True})
        primaries=[];plan=read(BUNDLE/f'PLAN_WAIT_R03_{branch}_ORIGINAL_CERRADO_R03.json')
        for event in plan['events']:
            if event['kind']not in('command','material'):continue
            source=S/'estado/servicios_persistentes'/life/'resultados'/(event['request_id']+'.json')
            target=folder/'primarios'/source.name;target.parent.mkdir(exist_ok=True);shutil.copy2(source,target)
            primaries.append({'file':target.relative_to(OUT).as_posix(),'sha256':sha(source),'bytes':source.stat().st_size,
                'original':source.relative_to(ROOT).as_posix()})
        for relative in('RESULTADO_SUPERVISION.json','ANTES_DEL_PROCESO.json','TRAYECTORIA/RESULTADO.json','TRAYECTORIA/ANTES_DE_NATIVE.json','SELLO_POST10_N0/CORTE_COMPLETO_POSTSTOP.json'):
            source=attempt/relative;target=folder/'continuidad'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        for source in(attempt/'TRAYECTORIA/FUENTES_ANTES_DE_NATIVE').iterdir():
            h=sha(source)
            if h not in sources:
                target=OUT/'fuentes'/(h+'_'+source.name);target.parent.mkdir(exist_ok=True);shutil.copy2(source,target)
                sources[h]={'file':target.relative_to(OUT).as_posix(),'sha256':h,'bytes':source.stat().st_size,'original':str(source)}
        seal=read(attempt/'SELLO_POST10_N0/CORTE_COMPLETO_POSTSTOP.json');pair=Path(seal['pair']['directory'])
        complete=observer.Snapshot(pair/'VIDA.deetsnap.gz',verify_checksum=False)
        parent_ids={int(r['id']):r for r in parent.receipts};final_ids={int(r['id']):r for r in complete.receipts}
        assert all(final_ids.get(identifier)==receipt for identifier,receipt in parent_ids.items())
        delta=[r for identifier,r in final_ids.items()if identifier not in parent_ids]
        delta_path=folder/'RECIBOS_NUEVOS_DESDE_FULL.json'
        emit(delta_path,{'parent_snapshot_sha256':parent.encoded_sha256,'final_snapshot_sha256':complete.encoded_sha256,
            'final_tick':complete.tick,'parent_receipts_exactly_preserved':True,'new_receipts':delta,
            'Native_pending_count':len(complete.pending),'new_native_ticks_executed_by_observer':0})
        branches[branch]={'life':life,'primaries':primaries,'full_receipts_delta':delta_path.relative_to(OUT).as_posix()}
        omitted.append({'path':str(pair/'VIDA.deetsnap.gz'),'sha256':complete.encoded_sha256,
            'bytes':(pair/'VIDA.deetsnap.gz').stat().st_size,'reason':'Complete operational snapshot stays local; analysis package is not a continuation backup.'})
    shutil.copy2(__file__,OUT/Path(__file__).name)
    emit(OUT/'INDICE.json',{'branches':branches,'unique_source_members':list(sources.values()),'omitted':omitted,
        'parent_full_snapshot':str(PARENT/'VIDA.deetsnap.gz'),'parent_full_sha256':parent.encoded_sha256,
        'new_native_ticks':0,'originals_modified':False})
    result=recalculate(OUT);emit(OUT/'RECALCULO.json',result)
    emit(OUT/'MANIFIESTO.json',{'members':[{'file':p.relative_to(OUT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
        for p in sorted(OUT.rglob('*'))if p.is_file()]})
    print(json.dumps({'out':str(OUT),'manifest_sha256':sha(OUT/'MANIFIESTO.json'),
        'branches':[{k:r[k]for k in('branch','work_requests_completed','actions','old_work_gain','new_quality','Native_receipts','receipt_statuses')}for r in result['branches']],
        'new_native_ticks':0},ensure_ascii=False),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--export-closed',action='store_true');mode.add_argument('--recalculate',type=Path)
    args=parser.parse_args()
    if args.export_closed:export()
    else:print(json.dumps(recalculate(args.recalculate.resolve(strict=True)),ensure_ascii=False))
