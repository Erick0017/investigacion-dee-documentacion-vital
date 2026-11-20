"""New closed CTX02 vs real12..15 and the preserved CTX01 host failure."""
from pathlib import Path
import datetime,hashlib,json,runpy
P4=Path(__file__).resolve().parents[1];S2=P4/'estados/candidato_R02/sistema'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def info(p):return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def primary(p):
    d=read(p);return json.loads(d['result'])if isinstance(d.get('result'),str)else d
def main():
    out=P4/'control/C2C_CTX2_CTX1_Y_REAL_CONTRASTE_PASIVO_R01.json'
    if out.exists():raise FileExistsError('Preserve prior comparison')
    ctx_path=P4/'control/PI04_C2C_CTX_CUT4_OP2_R02.json';ctx=read(ctx_path)
    real_path=P4/'control/PI04_C2C_REAL_RES_R01.json';real=read(real_path)
    if ctx['completed']!=4 or ctx['products']!=2 or ctx['owner_closed']is not True:raise ValueError('Exact four completed CTX02 opportunities required')
    real_rows={x['ordinal']:x for x in real['rows']};rows=[]
    for r in ctx['rows']:
        x=real_rows[r['ordinal']]
        if r['ordinal']not in range(12,16)or r['context']!=x['context']or r['operands']!=x['operands']or r['before_tick']!=x['before_tick']or r['after_tick']!=x['after_tick']:raise ValueError('Matched initial schedule/age differs')
        p=Path(r['primary']);q=Path(x['primary']);cp=primary(p)['result']['rows'][0];rp=primary(q)['result']['rows'][0]
        if len(cp['requests'])!=5 or len(rp['requests'])!=6:raise ValueError('Expected one-datum omission only in outer inputs')
        rows.append({'ordinal':r['ordinal'],'context':r['context'],'operands':r['operands'],'before_tick':r['before_tick'],'after_tick':r['after_tick'],
          'real':{'first_choice':x['first_choice'],'operation':x['operation'],'actual_number':x['actual_number'],'second_choice':x['second_choice'],'route':x['actual_route'],'useful_product':x['useful_product'],'Native_inputs':x['Native_inputs'],'primary':info(q)},
          'context_omitted':{'first_choice':r['first_choice'],'operation':r['operation'],'actual_number':r['actual_number'],'second_choice':r['second_choice'],'route':r['actual_route'],'useful_product':r['useful_product'],'Native_inputs':r['Native_inputs'],'primary':info(p)}})
    first_primary=primary(Path(ctx['rows'][0]['primary']));first=first_primary['result']['rows'][0]
    home=S2/'estado/servicios_locales'/ctx['life']/'PI04_C2C_COORDINACION_R01';journal=home/'eventos.jsonl';events=[json.loads(x)for x in journal.read_bytes().splitlines()]
    action=next(e for e in events if e['kind']=='C2_SECOND_NATIVE_USE_AND_ACTION'and e['tick']==810487)
    schema=next(e for e in events if e['kind']=='C2_DEVICE_DIRECTORY_SCHEMA_PREPARED_OP2'and e['tick']==809763)
    old_path=P4/'ensayos/PI04_C2C_CTX_CUT4_R01_OP_12.json';old=read(old_path);error=json.loads(old['error']);failed_cut=error['failed_native_future_preserved']
    parser=runpy.run_path(str(P4/'codigo/contrastar_finales_E3_pasivo.py'),run_name='pure_CTX_pair_parser')['parse']
    failed=parser(S2/failed_cut['snapshot'],failed_cut['snapshot_sha256']);closed=parser(S2/first_primary['committed_snapshot']['snapshot'],first_primary['committed_snapshot']['snapshot_sha256'])
    failed_physical=failed[0]['physical'];pre_device=action['second']['after'];post_device_same_tick=action['after']['physical']
    keys=('N','tick','RAW_sha256','clocks_sha256')
    same_pre=all(failed_physical[k]==pre_device[k]for k in keys);same_post=all(failed_physical[k]==post_device_same_tick[k]for k in keys)
    if not same_pre or not same_post:raise ValueError('Schema-only comparison did not preserve the same Native pre-device physical cut')
    failed_ids={r['id']:r for r in failed[5]};closed_ids={r['id']:r for r in closed[5]}
    changed_failed_receipts=[k for k,v in failed_ids.items()if closed_ids.get(k)!=v]
    extra=[v for k,v in closed_ids.items()if k not in failed_ids]
    if changed_failed_receipts or len(extra)!=1 or extra[0]['status']!=2 or not any('.outcome.'in x for x in extra[0]['channels']):raise ValueError('CTX02 did not preserve failed-prefix receipts plus one later generic return')
    comparison={'failed_CTX01_frozen_snapshot':failed[0]['snapshot'],'CTX01_before_failed_move':failed_physical,'CTX02_second_function_after_before_Device_begin':pre_device,'CTX02_after_successful_Device_begin_same_tick':post_device_same_tick,
      'global_RAW_hashes_equal':same_pre and same_post,'global_clocks_hashes_equal':same_pre and same_post,'all_prior_Native_receipts_equal':not changed_failed_receipts,'one_later_CTX02_generic_outcome_receipt':extra[0],
      'full_same_tick_CTX02_snapshot_available':False,'not_full_causal_or_operational_world_equality':True,
      'scope':'A frozen CTX01 full buffer hash is compared with recorded CTX02 global buffer hashes before and after Device.begin at the same tick. This is cryptographic buffer identity, not a direct byte comparison against an unrecorded same-tick CTX02 snapshot. Directory/device metadata differ by design.'}
    proof={'schema':'PI04.C2C.CTX02_vs_CTX01_and_real.passive.v1','inspection_local':datetime.datetime.now().astimezone().isoformat(),'sources':{'ctx02':info(ctx_path),'real_reserve':info(real_path),'old_failed_CTX01':info(old_path),'CTX02_journal':info(journal)},
      'context_comparison':{'ordinals':[12,13,14,15],'real_products':sum(x['real']['useful_product']for x in rows),'CTX02_products':sum(x['context_omitted']['useful_product']for x in rows),'real_inputs':sum(x['real']['Native_inputs']['unique_requested']for x in rows),'CTX02_inputs':sum(x['context_omitted']['Native_inputs']['unique_requested']for x in rows),'rows':rows,'Native_ticks_each':3128,'independent_replicates':False,'shared_posttrain12_prefix':True},
      'infrastructure_schema_preparation_record':schema,'same_physics_at_the_previous_failed_move':comparison,
      'interpretation':[
        'The four real reserved opportunities12..15 produced4products; the four context-omitted counterparts produced2. They use the same public scalar/operand schedule and matched age, but the control omits one legal datum event per opportunity:744 versus740 material inputs. This is a sensor-input ablation, not an equal-dose sham or a pure observer contrast.',
        'The current context scalar influenced which prepared arithmetic capability was used in the two high-context cases. This contrast supports contextual access/use in the prepared sequence; by itself it does not identify acquisition by true own-action contingency or an autonomous choice of the multistep plan.',
        'The first repaired control reaches the same globally hashed RAW/clocks and exactly the same previous Native receipt history as the failed attempt at810487 before Device.begin. The external schema preparation added declared empty directories without changing that Native processing. Device.begin then moved the resource and the later generic return completed the control.',
        'The original failedCTX01 remains pending/uncertain and unscored, with724Native ticks. CTX02 is a new named continuation from the known full809763 prefix; it does not overwrite or retry the failed future.',
        'Matching Native buffer hashes at the action boundary does not claim equality of external directories, device state, metadata, transport identities or complete causal worlds.'
      ],'new_Native_ticks_by_this_analysis':0,'Native_or_GUI_imported':False,'product_or_S2_modified':False,'promotion_claimed':False}
    out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':info(out),'real_products':proof['context_comparison']['real_products'],'CTX02_products':proof['context_comparison']['CTX02_products'],'same_preDevice_RAW_clocks':same_pre,'same_postDevice_RAW_clocks':same_post,'prior_receipts_exact':not changed_failed_receipts,'Native_ticks_by_analysis':0},ensure_ascii=False))
if __name__=='__main__':main()
