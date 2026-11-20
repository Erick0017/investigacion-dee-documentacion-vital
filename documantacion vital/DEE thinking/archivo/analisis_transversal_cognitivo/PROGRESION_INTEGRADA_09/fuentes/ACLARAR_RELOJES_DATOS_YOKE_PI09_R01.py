"""Pure provenance/age clarification for the CLOSED Yoke data control.
Independent worlds' Native counters are not a common physical-age axis.
"""
from pathlib import Path
from datetime import datetime
import hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf8')
def read_primary(tag,i):
    file=P/'ensayos'/('%s_%03d.json'%(tag,i+2));data=file.read_bytes();primary=json.loads(data);assert primary['status']=='completed';v=json.loads(primary['result'])if isinstance(primary['result'],str)else primary['result'];row=v.get('result',v)['rows'][0];assert row['ordinal']==i;return primary,row,sha(data)
def run():
    result=[]
    for i in range(12):
        primary,row,p_hash=read_primary('PI09_YOKE_R03',i);reg=row['first_stage']['sample_register'];src=reg['release_source'];j=(i+5)%12
        source,source_row,s_hash=read_primary('PI09_ALWAYS_R03',j);observation=src['observation'];assert src['source_ordinal']==src['ordinal']==j and src['primary_sha256']==s_hash and observation==source_row['first_stage']['sample_register']['actual_preview_observation']and sha(canon(observation))==src['observation_sha256']
        finished=datetime.fromisoformat(source['finished_utc']);started=datetime.fromisoformat(primary['started_utc']);assert finished<=started
        q1=row['first_stage']['query_tick'];q2=row['second_stage']['calendar']['query_tick'];release=reg['release_tick'];capture=reg['sample_tick']
        result.append({'ordinal':i,'recipient_primary_sha256':p_hash,'source_ordinal':j,'source_primary_sha256':s_hash,'released_source_observation_sha256':src['observation_sha256'],'recipient_own_preview_tick':capture,'recipient_release_tick':release,'recipient_second_datum_tick':q2+3,'recipient_own_preview_age_at_release':release-capture,'recipient_own_preview_age_at_second_boundary':q2+3-capture,'released_external_source_Native_tick':observation['tick'],'source_counter_difference_at_recipient_release_NOT_SAME_WORLD_AGE':release-observation['tick'],'source_counter_difference_at_second_boundary_NOT_SAME_WORLD_AGE':q2+3-observation['tick'],'source_primary_finished_utc':source['finished_utc'],'recipient_primary_started_utc':primary['started_utc'],'source_was_already_observed_before_recipient_operation_wallclock':True,'released_sample_wallclock_age_not_measured':True,'scope':'A frozen actual sample from another completed arm. Native counter subtraction across worlds is not a physical data age, current measurement, Native memory, or information from the future.'})
    value={'schema':'DEE.PI09.yoked_data.clock_provenance_clarification.R01','Native_executed':False,'DEE_imported':False,'all12_sources_matched_actual_Always_primaries':True,'all_sources_completed_before_recipient_wallclock':True,'rows':result,'meaning':'The earlier evaluator technical_register age fields refer to each recipient own preview sample. For Yoke that is not the released foreign sample; this explicit companion preserves and disambiguates both. Native real uses its own sample, with age9 atrelease andq2-q1+4 atsecondinput. No actor/decoder/permutation is changed.'}
    out=P/'fuentes/ACLARACION_RELOJES_DATOS_YOKE_PI09_R01.json'
    with out.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'rows':12,'sources_already_recorded':True,'sha256':sha(out.read_bytes()),'negative_cross_world_differences':sum(r['source_counter_difference_at_second_boundary_NOT_SAME_WORLD_AGE']<0 for r in result)}))
if __name__=='__main__':run()
