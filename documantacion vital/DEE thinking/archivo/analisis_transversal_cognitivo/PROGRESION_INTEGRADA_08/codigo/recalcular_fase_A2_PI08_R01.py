"""Freeze and recalculate explicit CLOSED A2 phase primaries/products. No DEE."""
from pathlib import Path
import argparse
import datetime
import json
import runpy
import sys

HERE=Path(__file__).resolve().parent;P8=HERE.parent
sys.path.insert(0,str(HERE))
from auditoria_documental_PI08 import body, digest, interval_union


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fase',type=Path,required=True)
    ap.add_argument('--system-root',type=Path,required=True)
    ap.add_argument('--destino',type=Path,required=True)
    a=ap.parse_args();phase_path=a.fase.resolve(strict=True);system=a.system_root.resolve(strict=True);dest=a.destino.resolve()
    if not phase_path.is_relative_to(P8)or not system.is_relative_to(P8/'estados'):
        raise ValueError('Explicit actual PI08 phase and diagnostic system required')
    if dest.exists()or not any(dest.is_relative_to(P8/k)for k in('codigo','fuentes')):
        raise ValueError('Fresh P8 codigo/fuentes documentary destination required')
    phase_bytes=phase_path.read_bytes();phase=json.loads(phase_bytes)
    if not phase.get('closed')or phase.get('status')!='CLOSED_PHASE':
        raise ValueError('No live/unfinished phase can be copied')
    tool=runpy.run_path(str(HERE/'RECALCULAR_PRIMARIOS_PI08.py'),run_name='pure_A2_phase_decoder')
    index={'schema':'DEE.PI08.portable_primary_index.v1','primaries':[],'products':[],
           'scope':'Actual closed PI08 phase documentary evidence; not a Native replay or executable backup.'}
    files={};excluded=[];hashes={};phase_tick_rows=[]
    for phase_row in phase['rows']:
        if phase_row.get('kind')is None:
            excluded.append({'label':phase_row['label'],'scope':'Nonmaterial state view, not an extra functional opportunity'})
            continue
        source=Path(phase_row['primary']).resolve(strict=True)
        if not source.is_relative_to(P8):raise ValueError('Outside PI08 phase primary')
        data=source.read_bytes()
        if digest(data)!=phase_row['primary_sha256']:raise ValueError('Closed primary hash changed')
        rel='04_EVIDENCIAS/PRIMARIOS/'+source.name
        files[rel]=data
        index['primaries'].append({'file':rel,'bytes':len(data),'sha256':digest(data),
            'modality':'PI08_RECORDED_MATERIAL_USE_IN_SAME_CONTINUATION',
            'source_reference_for_packager_only':str(source)})
        envelope,rows=body(json.loads(data))
        for row in rows:
            product=row.get('actual_effect',{}).get('product')
            artifact=row.get('message',{}).get('artifact')
            candidates=[]
            if product is not None:
                value=Path(product['path'])
                base=system/'estado/servicios_locales'/phase['life_id']/'PI04_C2C_COORDINACION_R01/dispositivo'
                candidates.append((value if value.is_absolute()else base/value,product))
            if artifact is not None:
                candidates.append((system/'estado/servicios_locales'/phase['life_id']/'PI07_REGULACION_ENV_R03'/artifact['file'],artifact))
            for path,metadata in candidates:
                path=path.resolve(strict=True)
                if not path.is_relative_to(system):raise ValueError('Product escaped its explicit diagnostic system')
                content=path.read_bytes()
                if len(content)!=metadata['bytes']or digest(content)!=metadata['sha256']:
                    raise ValueError('Actual product bytes differ')
                name='04_EVIDENCIAS/PRIMARIOS/product_'+digest(content)[:20]+'.bin'
                if name not in files:
                    files[name]=content
                    index['products'].append({'file':name,'bytes':len(content),'sha256':digest(content),
                                              'source_reference_for_packager_only':str(path)})
                if path.read_bytes()!=content:raise ValueError('Closed product changed while copying')
        hashes[str(source)]=digest(data)
        phase_tick_rows.append((phase_row['before_tick'],phase_row['after_tick']))
    if phase_path.read_bytes()!=phase_bytes:raise ValueError('Phase proof changed')
    dest.mkdir(parents=True)
    for relative,data in files.items():
        target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    ip=dest/'04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI08.json'
    ip.parent.mkdir(parents=True,exist_ok=True);ip.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    result=tool['recalculate'](dest)
    if not result['all_checks_passed']:raise ValueError(json.dumps(result['documentary_mismatches']))
    ledger=result['current_direct_receipt_ledger']
    if ledger['unique_current_Native_requests']!=phase['Native_inputs']['unique_requested']:
        raise ValueError('Recalculated phase Native denominator differs')
    if ledger['status_counts']!=phase['Native_inputs']['status_counts']:
        raise ValueError('Recalculated phase Native statuses differ')
    windows=interval_union(phase_tick_rows)
    if windows['unique_recorded_tick_advancements']!=phase['new_Native_ticks']:
        raise ValueError('Material primary windows do not cover closed phase ticks')
    rp=dest/'RESULTADO.json';rp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    proof={'schema':'DEE.PI08.A2.closed_phase_documentary_recalculation.v1',
           'at':datetime.datetime.now().astimezone().isoformat(),'phase':str(phase_path),
           'phase_sha256':digest(phase_bytes),'life_id':phase['life_id'],
           'recorded_phase_before_tick':phase['initial_tick'],'recorded_phase_after_tick':phase['final_tick'],
           'recorded_phase_Native_ticks':phase['new_Native_ticks'],'material_tick_windows':windows,
           'indexed_material_primaries':len(index['primaries']),'products':index['products'],
           'nonmaterial_state_views_not_counted':excluded,
           'all_documentary_checks_passed':True,'documentary_checks':len(result['checks']),
           'episodes':result['episodes'],'inherited_witnesses':result['inherited_function_witnesses_recalculated_separately'],
           'C2C_chain_witnesses':result['C2C_chain_witnesses_recalculated_separately'],
           'current_direct_receipt_ledger':ledger,'result_sha256':digest(rp.read_bytes()),
           'new_Native_ticks_in_this_recalculation':0,'DEE_imports':0,
           'scope':'Passive independent decoding/counting of actual closed material primaries and actual products. '
                   'Not six new experiences, acquisition replay, adoption or a repeat of the Native phase.'}
    pp=dest/'PRUEBA_FASE.json';pp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':str(pp),'sha256':digest(pp.read_bytes()),'material_primaries':len(index['primaries']),
                      'checks':len(result['checks']),'current_Native_requests':ledger['unique_current_Native_requests'],
                      'recorded_Native_ticks':phase['new_Native_ticks'],'new_Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
