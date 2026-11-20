"""Distinguish no new noise submissions from an actually drained old queue.

Finish matched18-opportunity endpoints: original12 committed stress windows
then6 clean intervals. Never cancel pending events or silently restore a state.
"""
from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from app.native_tools import atomic_json,digest_file,physical,exact_receipt
from app.process_control import protect_current
from capacidades.integracion_situada_01 import ic_external as ext,delayed_social as social
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
for name,life,source,steps in [('TRUE_WITHDRAWAL_NOMINAL_173','E1_INTEGRADO_COSTO_SOCIAL_01','STRESS_NOMINAL_MAIN_145.json',8),('TRUE_WITHDRAWAL_SEVERE_173','IC01_STRESS_SEVERE_146','STRESS_SEVERE_146.json',4)]:
    out=EV/(name+'.json')
    if out.exists():continue
    if time.monotonic()>deadline-2400:raise TimeoutError('Closing reserve')
    original=json.loads((EV/source).read_text())['result']['noise_requests'];last_noise=max(r['tick']for r in original)
    def run(a):
        before=physical(a.world,occupation=True);pending_before=[r for r in original if exact_receipt(a.world.runtime.receipt(r['id']))['status']=='scheduled']
        r=ext.run(a,steps=steps,readout='magnitude',feedback='cost',codec=2,reader='omit',stop_invalid=None,social_ports=social.get(a)['plan']['banks'])
        after_noise=[dict(q,receipt=exact_receipt(a.world.runtime.receipt(q['id'])))for q in original]
        return{'original_noise_file':source,'last_original_noise_requested_tick':last_noise,'pending_original_noise_before':pending_before,'requested_end_tick':7440,'clean_complete_intervals_end_ticks':[7105,7172,7239,7306,7373,7440],'external':r,'noise_receipts_after':after_noise,'no_noise_still_pending_after':not any(q['receipt']['status']=='scheduled'for q in after_noise),'initial':before,'final':physical(a.world,occupation=True),'scope':'Correction of interpretation: earlier WITHDRAW files meant no NEW noise, not a drained physical queue. These reached futures complete the common18-opportunity horizon. No old content or trained state is reintroduced. Current real observations and actual environmental costs continue normally.'}
    result=s.mutate(life,'IC01_TRUE_POST_QUEUE_STRESS_WITHDRAWAL',run,{'source':digest_file(__file__),'matched_no_noise_reference':'STRESS_MATCHED_144 + STRESS_MATCHED_144_WITHDRAW6 already reached T7440','do_not_count_partial_windows_as_six_clean_intervals':True});atomic_json(out,result);print(name+' '+str(result['INSTRUMENTO']['tick']),flush=True)
