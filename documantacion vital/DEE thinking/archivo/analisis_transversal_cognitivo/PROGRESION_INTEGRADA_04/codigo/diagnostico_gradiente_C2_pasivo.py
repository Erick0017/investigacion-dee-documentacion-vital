"""Local-gradient algebra and existing calibration only; no DEE or ticks."""
from pathlib import Path
import datetime,hashlib,json
P4=Path(__file__).resolve().parents[1];R=P4.parents[2]
KERNEL=R/'4.5/DEE_thinking_4_5_0/source/src/kernel_v27.cpp'
RUNTIME=R/'4.5/DEE_thinking_4_5_0/source/src/runtime.cpp'
SENSOR=P4/'estados/candidato_R02/sistema/capacidades/pi04_selector_contextual_C2_R01.py'
def sha(b):return hashlib.sha256(b).hexdigest()
def source(path,needles):
 b=path.read_bytes();lines=b.decode('utf-8-sig').splitlines()
 return {'path':str(path),'bytes':len(b),'sha256':sha(b),'read_scope':'Only listed mathematical/transport/geometry sections, as text. No compilation or import.',
         'anchors':[{'line':i,'text':line}for i,line in enumerate(lines,1)if any(n in line for n in needles)]}
def sign(x):return(x>0)-(x<0)
def main():
 path=P4/'control/C2CAL_R02_ANALISIS_PASIVO_R01.json';data=json.loads(path.read_text(encoding='utf-8'))
 rows=[]
 for r in data['records']:
  a=r['bank_before']['A']['s_reg'];b=r['bank_before']['B']['s_reg'];c=r['value'];directions=[o['physical']['direction']for o in r['active_outputs']]
  rows.append({'c':c,'A':a,'B':b,'delta_A_minus_B':a-b,'local_grad_x_from_A_B_datum':a-b+c,
   'predicted_x_sign':sign(a-b+c),'observed_directions':directions,'observed_s_reg':[o['physical']['s_reg']for o in r['active_outputs']],
   'matches_x_sign':len(directions)==1 and directions[0][0]==sign(a-b+c),
   'matches_query0_Z_datum_only':len(directions)==1 and directions[0][2]==sign(-c),
   'query_payload':0,'reported_choice':r['choice'],'primary':r['primary'],'primary_sha256':r['primary_sha256']})
 proof={'schema':'PI04.C2.local_gradient_diagnosis.passive.v1','at_local':datetime.datetime.now().astimezone().isoformat(),
  'source_kernel':source(KERNEL,['grad_x -=','grad_y -=','grad_z -=','int ndx =','ndx = (grad_x','ndy = (grad_y','ndz = (grad_z','if (get_dir_x(v)','if (is_alive_for_rule(nv))','if (exists(nv))']),
  'source_runtime':source(RUNTIME,['pack_record(channel.state','apply_events_at_boundary();','v27::tick(raw_a_','Intentionally preserve']),
  'source_sensor':source(SENSOR,['DATUM_OFFSET =','OUTPUT_OFFSETS =','STOP_OFFSETS =','query_payload','submit(PREFIX','query_tick + 3','query_tick + 6','o["direction"]']),
  'formula':{'exact_kernel_rule':'g_j = -sum_{26 Moore neighbours v with exists(v)} offset_j(v) * s_reg(v); existing centre is excluded.',
   'direction_quantization':'For a supported moving record (or orphan), d_j=sign(g_j). Static anchored records have direction zero; survival, transport and coalescence are additional rules.',
   'declared_offsets':{'A':[-1,-1,0],'B':[1,-1,0],'datum_c':[-1,0,1]},
   'local_contribution':'(g_x,g_y,g_z)=(A-B+c,A+B,-c)+G_other',
   'query_charge':'Own query payload is excluded from its own Moore gradient. A trailing query exactly on the Z axis contributes no direct X term. Query5 may alter neighbouring charges, survival and later contacts: independence of the complete trajectory is NOT proved.',
   'scope':'This is a conditional local model at the reading interaction, not a complete Native replay or proof that other transient contributions vanish.'},
  'existing_query0_calibration':rows,'all_six_match_local_X':all(x['matches_x_sign']for x in rows),'all_six_match_datum_Z_sign_query0':all(x['matches_query0_Z_datum_only']for x in rows),
  'MU_reported_comparison':{'delta':-20,'c0_predicted_X':sign(-20),'c32_predicted_X':sign(-20+32),'status':'Compatible with the already reported MU query5 observations; no new MU Native test executed here.'},
  'context4_6':{'initial_delta':1,'initial_gx':[5,7],'initial_X':[1,1],
   'desired_domain':'Prepared task maps X<=0 (including material zero via fixed fallback) to DIF and X>0 to SUM.',
   'needed_delta_for_contexts4_and6':'-6 < delta <= -4; integer delta -5 or -4 separates4 and6. For the full intended c<=4 / c>4 boundary, integer delta=-4.',
   'conditional_five_penalties':'Starting delta=1, five actual +1 failures decrementing delta by one each would reach delta=-4. Equal basal growth cancels in the difference. Actual per-op bank changes must be measured; datum/contact effects can alter this expectation.',
   'not_sensor_failure':'Input changes the Z signature already under query0. Constant X at delta=1 is consistent with sign quantization; query5 patch is not justified solely by this calibration.',
   'information_limit':'At a fixed unlearned cut, contexts4/6 currently collapse to the same declared output signature. Do not score that as an impossible instant classification requirement or assert global indistinguishability: acquisition may change the threshold. Keep acquisition costs/errors in the data.'},
  'minimum_before_evaluation':[
   'Continue the already sealed query0 development schedule; do not switch to query5 merely because all X signs were +1.',
   'Record deltaA-B before/after each opportunity, physical context admission, all six q+6 signatures, actual motor/capability, actual consequence and generic return. Check whether acquired threshold crosses the declared4/6 region.',
   'Before reserved scoring, use equal-phase copies at one learned cut and a no-return/equal-exposure control, with the same two contextual opportunities4/6 and frozen query0 reader. Four outcomes separate current-data sensitivity from history-induced threshold change. If this contrast is already supplied by the sealed protocol, reuse it rather than add queries.',
   'If query5 must be evaluated as an instrument variant, compare query0/query5 on copies of the SAME complete cut with c=0 and one nonzero c, equal boundaries/dose, and passive q+3 Moore-neighbour frames. Do not mix sequential different-age calibration with evidence of a query-payload effect.'
  ],'new_Native_ticks':0,'DEE_imports':0,'kernel_runtime_or_product_modified':False}
 out=P4/'control/C2_DIAGNOSTICO_GRADIENTE_LOCAL_PASIVO.json'
 if out.exists():raise FileExistsError('Existing diagnosis protected')
 out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'six_X_matches':proof['all_six_match_local_X'],'six_Z_matches':proof['all_six_match_datum_Z_sign_query0'],'Native_ticks':0},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
