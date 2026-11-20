"""Passive closed-calibration checker and external authorization, no Native."""
from pathlib import Path
import hashlib, importlib.util, json
P = Path(__file__).resolve().parents[1]
PROTO_SHA = 'f69e8558799558a1ccceb70e0684a061a971b9521ad8985205d1662aea55d269'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    output = P/'control/RECALCULO_CALIBRACION_R03_PI07_R02.json'
    authpath = P/'control/AUTORIZACION_EVALUACION_R03_PI07_R02.json'
    if output.exists() or authpath.exists(): raise FileExistsError('Never overwrite a gate or authorization')
    if sha(P/'codigo/PROTOCOLO_PI07_R03.json') != PROTO_SHA: raise ValueError('Protocol changed')
    spec = importlib.util.spec_from_file_location('PI07_frozen_record_decoder', P/'codigo/RECALCULAR_PRIMARIOS_PI07.py')
    dec = importlib.util.module_from_spec(spec); spec.loader.exec_module(dec)
    checks = []; arms = {}; evidence = []
    for arm, forced in [('PULSE','pulso'), ('NONE','nada')]:
        proofpath = P/'control'/('PI07_CAL_'+arm+'_R03.json'); proof = read(proofpath)
        if not (proof['closed'] and proof['status']=='CLOSED' and proof['full_plan_completed'] and proof['error'] is None):
            raise ValueError('Both actual calibration worlds must have closed completely')
        found = {}
        for item in proof['outcomes']:
            primary = P/'ensayos'/Path(item['primary']).name
            if sha(primary) != item['primary_sha256']: raise ValueError('Actual primary changed')
            _, rows = dec.decoded_result(read(primary))
            for r in rows:
                if 'FI' not in r: continue
                if r['ordinal'] in found: raise ValueError('Duplicate calibration opportunity')
                found[r['ordinal']] = (r, primary)
        if set(found) != {0,1}: raise ValueError('Exact threat-first/message-second calibration required')
        data = []
        for ordinal in (0,1):
            r, primary = found[ordinal]; fi = r['FI']; cal = r['calendar']; q = cal['query_tick']
            old = dec.late_FI_choice(fi['legacy_result']['original_result']['native_trial']['reader'])
            early = dec.early_choice(fi['legacy_result']['early_observation'])
            sensor = dec.observation(r['sensor']['observation'])
            req, aliases = dec.receipts(r['requests']); statuses = {}
            for rc in req.values(): statuses[rc['status']] = statuses.get(rc['status'],0)+1
            fi_req,_ = dec.receipts(fi['requests'])
            msg = r['message']; obs = dec.observation(msg['observation'])
            ms = dec.request_status(msg['request']); ps = dec.request_status(r['actuator_request'])
            delivered = (ms=='applied' and obs['state']>0 and obs['semantic']==1 and obs['direction']==[1,0,0] and obs['s_reg']==5)
            expected_FI = -1 if ordinal==0 and arm=='NONE' else 1
            expected_failed = (ordinal==0 and arm=='NONE') or (ordinal==1 and arm=='PULSE')
            cue = 'threat' if ordinal==0 else 'falsecue'
            local = {
                'actual_sensor_identity_codec': sensor['state']==r['sensor']['actual_state_datum'],
                'required_threat_information_state1': ordinal!=0 or sensor['state']==1,
                'fixed_environment_order': r['environment_spec']['cue']==cue and r['environment_spec']['message_payload']==(None if ordinal==0 else 5),
                'explicit_forced_not_acquired': r['operator_forced_action']==forced and r['actual_motor']==(1 if arm=='PULSE' else -1),
                'FI_RAW_at_both_fixed_readers': old==early==fi['old_q6_choice']==fi['early_physical_choice']==expected_FI,
                'all176_FI_inputs': len(fi_req)==176 and all(z['status']=='applied' for z in fi_req.values()),
                'generic_actual_outcome': r['actual_failed'] is expected_failed and r['returned_failed'] is expected_failed,
                'unchanged_six_lap_timing': cal['seed_tick']==q+7 and cal['outcome_injection_tick']==q+408 and cal['contact_tick']==q+410 and r['after_tick']==q+412,
                'no_unknown_receipts': all(s=='applied' or s.startswith('rejected') for s in statuses),
            }
            if ordinal==0:
                local['tool_admission'] = ps==('applied' if arm=='PULSE' else None)
            elif arm=='PULSE':
                local['actual_Native_conflict_cost'] = ps==ms=='rejected_conflict' and not r['pulse_applied'] and not msg['delivered_exact'] and statuses.get('rejected_conflict')==2
            else:
                artifact = msg['artifact']; path = P/'estados/candidato/sistema/estado/servicios_locales'/r['life_id']/'PI07_REGULACION_ENV_R03'/artifact['file']
                content = path.read_bytes()
                local['actual_message_and64bytes'] = ps is None and delivered and msg['delivered_exact'] and len(content)==artifact['bytes']==64 and sha(path)==artifact['sha256'] and content==int(obs['s_reg']).to_bytes(8,'little')*8
            before = r['reference_before']; after = r['return_frames'][-1]
            db = before[0]['s_reg']-before[1]['s_reg']; da = after['A']['s_reg']-after['B']['s_reg']
            local['credit_direction'] = da-db == (0 if not expected_failed else -1 if arm=='PULSE' else 1)
            for key,value in local.items(): checks.append({'arm':arm,'ordinal':ordinal,'check':key,'passed':bool(value)})
            data.append({'ordinal':ordinal,'primary':primary.name,'sha256':sha(primary),'before_tick':r['before_tick'],'after_tick':r['after_tick'],'calendar':cal,'sensor_state':sensor['state'],'Native_choice':r['reader']['choice'],'forced_motor':r['actual_motor'],'FI_q4':early,'FI_q6':old,'message_delivered':msg['delivered_exact'],'pulse_status':ps,'message_status':ms,'reference_delta_before':db,'reference_delta_after':da,'unique_requested':len(req),'status_counts':statuses})
        arms[arm] = data
        evidence.append({'forced_action':forced,'path':str(proofpath.resolve()),'sha256':sha(proofpath),'closed':True,'viability_passed':True})
    checks.append({'arm':'PAIRED','check':'same_first_age_and_calendar','passed':arms['PULSE'][0]['before_tick']==arms['NONE'][0]['before_tick']==846520 and arms['PULSE'][0]['calendar']==arms['NONE'][0]['calendar']})
    f1path = P/'control/F1_DESVIO_LATERAL_CAL00_PI07_R03_R01.json'; f1 = read(f1path)
    frame = next(z for z in f1['selected_frames'] if z['relative_q']==8)
    contact = next(z for z in frame['fixed_sites'] if z['site']==[52,48,56])
    literal = {**contact,'raw':contact['RAW']}; decoded = dec.observation(literal)
    follow = next(z for z in f1['selected_frames'] if z['relative_q']==9)
    away = next(z for z in follow['fixed_sites'] if z['site']==[51,48,57])
    out = dec.observation({**away,'raw':away['RAW']})
    checks.append({'arm':'PULSE','check':'F1_actual_diagonal_product_and_departure','passed':decoded['state']>0 and decoded['semantic']==1 and decoded['s_reg']==0 and decoded['direction']==[-1,0,1] and out==decoded and f1['primary']['sha256']==arms['PULSE'][0]['sha256']})
    passed = all(item['passed'] for item in checks)
    for item in evidence: item['viability_passed'] = passed
    gate = {'schema':'DEE.PI07.R03.closed_calibration.passive_gate.v1','evaluation_authorized':passed,'new_Native_ticks':0,'protocol_sha256':PROTO_SHA,'checks':checks,'arms':arms,'F1_product_proof':{'path':str(f1path.resolve()),'sha256':sha(f1path)},'calibration_proofs':evidence,'scope':'Forced mechanical paired controls. First opportunity shares complete source; second message trial follows divergent prior forced histories. No new learned selection, general regulation, universal phase result or promotion claimed.'}
    output.write_text(json.dumps(gate,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    auth = {'schema':'DEE.PI07.R03.closed_calibration.authorization.v1','protocol_sha256':PROTO_SHA,'evaluation_authorized':passed,'calibration_proofs':evidence}
    authpath.write_text(json.dumps(auth,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({'passed':passed,'checks':len(checks),'gate':str(output),'gate_sha256':sha(output),'authorization':str(authpath),'authorization_sha256':sha(authpath),'new_Native_ticks':0},ensure_ascii=False))
    return 0 if passed else 2

if __name__=='__main__': raise SystemExit(main())
