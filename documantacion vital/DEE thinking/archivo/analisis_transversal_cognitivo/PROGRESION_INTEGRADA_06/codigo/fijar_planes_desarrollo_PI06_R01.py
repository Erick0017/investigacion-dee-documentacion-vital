"""Prepare fixed phase plans from the completed baseline; zero Native actions."""
from pathlib import Path
import datetime,hashlib,json

P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    before=P/'control/BASELINE_global_PI06_R01.json'
    source=json.loads(before.read_text(encoding='utf-8-sig'))
    if source['status']!='COMPLETED'or not source['owner_closed_coherently']or source['closed_card']['physical']['tick']!=825849:
        raise ValueError('Only the actual coherently closed post-baseline source')
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    case_descriptions={
        'IZQ0':'One zero-load active SEM1 +Z packet is born two geometric steps before the left aggregate. A subsequent intact query and a third intact query after six unforced ticks test transient/history/phase, without repair.',
        'INTACTO':'No extra packet. Same three FI challenges, wait6 and capture calendars as the left/sham arms; controls aging and query history.',
        'SHAM0':'One matched zero-load/state1/SEM1/+Z packet at the fixed off-path source. Same query history and age as the left arm; empirical sham, not presumed harmless.',
        'DER0':'Known right-side route comparator. Inherited PI05 guard may absorb the carrier after recirculation; such a benefit is prepared protection, not newly acquired regulation.'}
    for name,condition in [('IZQ0','izq0'),('INTACTO','intacto'),('SHAM0','sham0'),('DER0','der0')]:
        def fi(label,c):return {'label':label,'literal':{'modo':'eci01-pi06-fiplus','condicion':c,
            'izquierda':14,'derecha':3,'captura':'global'},'max_native_ticks':208,'feedback':'omit','actuator':'closed'}
        plan={'schema':'DEE.PI06.fixed_phase_plan.v1','status':'SEALED','initial_tick':825849,
            'max_native_ticks':630,'registration_utc':stamp,
            'source_proof':{'path':str(before),'sha256':sha(before),
                'source_snapshot':source['closed_card']['snapshot'],
                'source_snapshot_sha256':source['closed_card']['snapshot_sha256']},
            'description':case_descriptions[name]+' All literal steps run regardless of the valid numeric outcome. NULL/rejected input/uncertain transport stops and preserves the reached future. FI q+4/q+6 and original phase normalizer remain fixed. If each FI lasts198, the third query is402ticks after the first (6N), but actual q/age are recorded rather than forced. A fail/pass/fail pattern is compatible with a recirculating carrier and is not evidence of regulation.',
            'steps':[fi('FI1_'+name,condition),fi('FI2_INTACTO','intacto'),
                {'label':'EVOLUCION6','literal':{'modo':'eci01-pi06-evolucion','ticks':6,'captura':'normal'},
                 'max_native_ticks':6,'expected_new_ticks':6,'feedback':'omit','actuator':'closed'},
                fi('FI3_INTACTO','intacto')]}
        write(P/'control'/('PLAN_DESARROLLO_'+name+'_PI06_R01.json'),plan)
    reserve={'schema':'DEE.PI06.heldout_reserve.preregistered.R01','status':'SEALED_BEFORE_DEVELOPMENT',
        'registration_utc':stamp,'source_same_closed_prefix':source['closed_card']['snapshot_sha256'],
        'public_operands':{'izquierda':20,'derecha':7},'pre_challenge_waits':[11,13],
        'first_conditions':['izq7','intacto'],'common_followup':['intacto','legal_wait6','intacto'],
        'unchanged_readers':[4,6],'phase_rule':'Use original mu.query_timing; report any realignment instead of claiming distinct query phases.',
        'execution':'Only Root may instantiate finite runner plans and new complete clones within the unchanged campaign budget. No cases selected by their answer and no tuning of sites/readers/codec.',
        'limits':['The two wait values and new public operands are held out from development.',
            'The reserve has no equal-payload sham7 mode in the sealed apparatus: it tests a heldout dose and local function, not a perfect dose-matched off-path causal isolation.',
            'No repeated failure may trigger new support, clearing, carrier deletion or a decoder change.']}
    write(P/'control/RESERVA_FI_PI06_R01.json',reserve)
    print(json.dumps({'plans':[{'name':p.name,'sha256':sha(p)}for p in sorted((P/'control').glob('PLAN_DESARROLLO_*_PI06_R01.json'))],
                      'reserve_sha256':sha(P/'control/RESERVA_FI_PI06_R01.json'),'Native_executed':False}))

if __name__=='__main__':main()
