"""Archive/recalculate the one authorized diagnostic panel; no new Native.

Reads only completed primary records, exact fixed RAW readers and saved full
states. Preserves negatives. The protected collaborator seed was not probed.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]if len(HERE.parents)>3 else HERE
S=ROOT/'sistema';LAB=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
EV=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
ATTEMPT=EV/'SEMILLA_PANEL24_DIAGNOSTICO_R01'
OUT=ATTEMPT/'EVIDENCIA_PORTABLE_N0_R01'
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


def fixed_lexical_reader(reader):
    candidates=[]
    for observation in reader['panel']:
        raw=int(observation['raw']);state=raw&0xffffffff;semantic=(raw>>60)&15
        vector=[((raw>>shift)&15)-(16 if((raw>>shift)&15)>=8 else 0)for shift in(48,52,56)]
        if state>0 and semantic==1 and vector in([0,0,-1],[0,0,1]):
            candidates.append({'sign':vector[2],'site':observation['site'],'raw':observation['raw'],'clock':observation['clock']})
    sign=candidates[0]['sign']if len(candidates)==1 else None
    if sign!=reader['formed_native_command']:raise ValueError('Primary RAW disagrees with the fixed lexical decoder.')
    return sign,candidates


def material_receipts(primary):
    result={}
    for item in walk(primary):
        if'id'in item and('port'in item or'channel'in item)and isinstance(item.get('receipt'),dict):
            identifier=int(item['id']);status=item['receipt']['status'];old=result.get(identifier)
            if old and status in('scheduled','queued'):continue
            normalized={'id':identifier,'channel':item.get('channel',item.get('port')),'status':status,
                'representation':'channel'if'channel'in item else'port','tick':item['tick'],'value':item.get('payload',item.get('value'))}
            if old and old['channel']!=normalized['channel']:raise ValueError('Conflicting channel for the same exact Native ID.')
            result[identifier]=normalized
    return result


def recalculate(directory):
    index=read(directory/'INDICE.json');expected={(r['family'],r['name']):r['sign']for r in read(directory/'LINEA_BASE_OLD22.json')['prior_rows']}
    expected_new=read(directory/'PROTOCOLO_PROSPECTIVO_FULL_R02.json')['baseline_new_forms']
    rows=[];receipts={};per_request=[]
    for primary_item in index['primaries']:
        path=directory/primary_item['file']
        if sha(path)!=primary_item['sha256']:raise ValueError('Exact primary bytes changed.')
        primary=read(path);part=material_receipts(primary);receipts.update(part)
        per_request.append({'id':primary['id'],'before_tick':primary['before_tick'],'after_tick':primary['after_tick'],
            'Native_receipts':len(part),'statuses':dict(Counter(r['status']for r in part.values()))})
        for block in primary['result']['rows']:
            if block.get('kind')=='APD03_explicit_material_panel':
                for family,key in(('forms','form'),('memories','context')):
                    for item in block[family]:
                        reader=item['result']['reader'];sign,candidates=fixed_lexical_reader(reader)
                        rows.append({'family':family,'name':item[key],'sign':sign,'expected_prior_sign':expected[(family,item[key])],
                            'match_prior':sign==expected[(family,item[key])],'candidates':candidates,
                            'reader_uses_target_or_token':reader.get('reader_uses_target_or_token',reader.get('reader_uses_token_target_or_expected_sign'))})
            else:
                reader=block['reader'];sign,candidates=fixed_lexical_reader(reader)
                name=next(word for word in('clasifica','equilibra')if word in primary['id'])
                rows.append({'family':'APD04_forms','name':name,'sign':sign,'expected_prior_sign':expected_new[name],
                    'match_prior':sign==expected_new[name],'candidates':candidates,
                    'reader_uses_target_or_token':reader.get('reader_uses_target_or_token',reader.get('reader_uses_token_target_or_expected_sign'))})
    delta=read(directory/'DELTA_RECIBOS_FULL.json')
    assert set(receipts)=={int(r['id'])for r in delta['new_receipts']}
    return {'schema':'APD04.seed_full_fork.panel24.RAW_recalculation.N0.v1','new_native_ticks':0,
        'host_material_requests':len(per_request),'typed_queries':len(rows),'rows':rows,
        'families':{family:{'requested':sum(r['family']==family for r in rows),
            'formed_unique':sum(r['family']==family and r['sign']is not None for r in rows),
            'matching_prior':sum(r['family']==family and r['match_prior']for r in rows)}for family in('forms','memories','APD04_forms')},
        'Native_receipts_unique':len(receipts),'Native_statuses':dict(Counter(r['status']for r in receipts.values())),
        'receipt_schema_forms':dict(Counter(r['representation']for r in receipts.values())),
        'per_request':per_request,'protected_seed_not_materially_queried':True,
        'scope':'Consecutive queries in this one exact diagnostic descendant of the seed, not extra experiences of the seed/development life, Native replay or unlimited retention.'}


def export():
    if OUT.exists():raise FileExistsError('Preserve the closed export, no overwrite.')
    final=read(ATTEMPT/'EJECUCION_NATIVE/TRAYECTORIA/RESULTADO.json')
    if final['error']or not final['owner_stop_confirmed']or final['final_protocol'].get('pending_material')or final['final_protocol'].get('uncertain_preserved'):
        raise ValueError('A pending diagnostic requires a separately labelled adverse export, not a completed panel claim.')
    card=final['final_record'];seed_proof=read(ATTEMPT/'SEMILLA_PROTEGIDA_TRAS_DIAGNOSTICO.json')
    assert seed_proof['seed_unchanged']and final['frozen_sources_unchanged']
    seal_out=ATTEMPT/'SELLO_POST_PANEL_N0'
    if not seal_out.exists():
        seal=LAB/'ejecucion/sellar_corte_poststop_apd04_n0_r01.py'
        command=[sys.executable,'-I','-B','-X','utf8',str(seal),'--root',str(ROOT),'--life',card['life_id'],
            '--tick',str(card['physical']['tick']),'--snapshot-sha256',card['snapshot_sha256'],
            '--target-name',card['life_id']+'_T'+str(card['physical']['tick'])+'_POST_PANEL24_R01',
            '--out',str(seal_out),'--scope','Stopped diagnostic descendant after24 consecutive material probes. Protected seed and developing worlds were not probed or replaced.',
            '--root-go','APD04_EXACT_CURRENT_POSTSTOP_PAIR_N0']
        subprocess.run(command,cwd=Path(sys.executable).parent,check=True)
    OUT.mkdir();primaries=[];plan=read(ATTEMPT/'PLAN_PANEL24_CERRADO_R01.json')
    for event in plan['events']:
        if event['kind']not in('material','command'):continue
        source=S/'estado/servicios_persistentes'/card['life_id']/'resultados'/(event['request_id']+'.json')
        target=OUT/'primarios'/source.name;target.parent.mkdir(exist_ok=True);shutil.copy2(source,target)
        primaries.append({'file':target.relative_to(OUT).as_posix(),'sha256':sha(source),'bytes':source.stat().st_size,'original':str(source)})
    for source,name in[(ATTEMPT/'PLAN_PANEL24_CERRADO_R01.json','PLAN_CERRADO.json'),
        (ATTEMPT/'IMPORTACION_COMPLETA_N0.json','IMPORTACION_COMPLETA_N0.json'),
        (ATTEMPT/'SEMILLA_PROTEGIDA_TRAS_DIAGNOSTICO.json','SEMILLA_PROTEGIDA_TRAS_DIAGNOSTICO.json'),
        (ATTEMPT/'EJECUCION_NATIVE/RESULTADO_SUPERVISION.json','RECURSOS_TOTALES.json'),
        (ATTEMPT/'EJECUCION_NATIVE/TRAYECTORIA/RESULTADO.json','CIERRE_NATIVE.json'),
        (seal_out/'CORTE_COMPLETO_POSTSTOP.json','SELLO_POST_PANEL_N0.json'),
        (EV/'ACTUADOR_R02_AUX_R01/CORRECCION_Y_DOSSIER_N0_R02/RECALCULO_PANEL_R02.json','LINEA_BASE_OLD22.json'),
        (LAB/'distribucion/PROTOCOLO_FULL_APD04_CERRADO_R02.json','PROTOCOLO_PROSPECTIVO_FULL_R02.json')]:shutil.copy2(source,OUT/name)
    for source in(ATTEMPT/'EJECUCION_NATIVE/TRAYECTORIA/FUENTES_ANTES_DE_NATIVE').iterdir():
        target=OUT/'fuentes'/source.name;target.parent.mkdir(exist_ok=True);shutil.copy2(source,target)
    observer=load('seed_panel24_saved_snapshot_only',S/'capacidades/observador_causal_retrospectivo_01.py')
    source_seed=Path(read(ATTEMPT/'IMPORTACION_COMPLETA_N0.json')['parent_full'])/'VIDA.deetsnap.gz'
    parent=observer.Snapshot(source_seed,verify_checksum=False);child=observer.Snapshot(S/card['snapshot'],verify_checksum=False)
    old={int(r['id']):r for r in parent.receipts};current={int(r['id']):r for r in child.receipts}
    assert all(current.get(identifier)==receipt for identifier,receipt in old.items())
    emit(OUT/'DELTA_RECIBOS_FULL.json',{'parent_snapshot_sha256':parent.encoded_sha256,'final_snapshot_sha256':child.encoded_sha256,
        'parent_receipts_exactly_preserved':True,'new_receipts':[r for i,r in current.items()if i not in old],
        'final_Native_pending':child.pending,'new_native_ticks':0})
    shutil.copy2(__file__,OUT/Path(__file__).name)
    emit(OUT/'INDICE.json',{'primaries':primaries,'final_record':card,'new_native_ticks':0,
        'omitted_full_state':{'path':str(S/card['snapshot']),'sha256':child.encoded_sha256,
            'reason':'Full operational snapshot and SQLite stay local. This analysis export is not a continuation backup.'}})
    result=recalculate(OUT);emit(OUT/'RECALCULO.json',result)
    emit(OUT/'MANIFIESTO.json',{'members':[{'file':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(OUT.rglob('*'))if p.is_file()]})
    print(json.dumps({'out':str(OUT),'manifest_sha256':sha(OUT/'MANIFIESTO.json'),'families':result['families'],
        'typed_queries':result['typed_queries'],'Native_receipts':result['Native_receipts_unique'],'statuses':result['Native_statuses'],
        'new_native_ticks':0},ensure_ascii=False),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--export-closed',action='store_true');mode.add_argument('--recalculate',type=Path)
    args=parser.parse_args()
    if args.export_closed:export()
    else:print(json.dumps(recalculate(args.recalculate.resolve(strict=True)),ensure_ascii=False))
