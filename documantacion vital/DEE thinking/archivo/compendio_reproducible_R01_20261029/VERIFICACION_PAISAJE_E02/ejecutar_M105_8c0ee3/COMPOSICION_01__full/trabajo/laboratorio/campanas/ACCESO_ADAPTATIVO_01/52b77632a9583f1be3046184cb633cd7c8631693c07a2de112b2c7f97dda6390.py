"""Two learned supports; later access teaching supplies no original content.

Prepared redundancy is counted: both samples are real initial experiences,
not transplanted trained fields. The same later protocol is used for opposite
codes. It teaches an access strategy using generic fixed+Z calibration samples,
never the old code at either content support. Native cuts/omissions test whether
the untouched learned support is needed. This is not autonomous failure sensing.
"""
from pathlib import Path
import argparse,sys,json,gzip
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'),str(Path(__file__).parent)]
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import acceso_adaptativo_01 as aa,espanol_funcional_01 as e,paisaje_causal_01 as pc
from instrumentos_pc01 import frame,witness,guard,receipts,sha
from avance_acotado import install
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);reference=a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01/MAIN_CONFIRMATORIO_36/main/PRIMARIOS.json.gz';ref=json.loads(gzip.decompress(reference.read_bytes()));start_record=ref['initial_record'];parent=ref['life'];life='AA01_USO46_'+a.case;s.fork(parent,life,kind='CANDIDATE',checkpoint=start_record['snapshot']);z=1 if a.case.startswith('plus')else-1;data={'case':a.case,'life':life,'parent_current':s.record(parent),'historical_full_parent':start_record,'source_sha256':sha(__file__),'design_before':'Same fixed utility curriculum[+1,-1], two initial real content experiences, long old-function interval, fixed historical Mplus query, then same new utility[+1,+1]. Both opposite old codes receive an identical later future and no newMcontent. NativeY chooses the other Mroute. Initial redundancy is prepared, not invented by the entity. Strategy teaching is not autonomous failure diagnosis.','initial_external_content':z,'prepared_redundancy':'Two initially experienced supports, except explicit omitted-backup controls','requests':[],'stages':[],'panels':[]}
def trial(x):
    install(x,a.out,seconds=220);data['pre']=physical(x.world,occupation=True);initial_contents=[None if'no_backup'in a.case else z,z];data['first_preparation']=aa.prepare_local_episode(x,episode='R40_INITIAL',availability=[1,-1],contents=initial_contents);data['frames']=[]
    def capture(label):data['frames'].append({'label':label,'frame':frame(x.world)})
    for stage in('first','learned','content','access','transformed','received','social','use'):
        answer=aa.advance_episode(x,stage=stage,max_seconds=90);data['stages'].append({'block':'initial','stage':stage,'answer':answer})
        if stage in('content','access','use'):capture('initial_'+stage)
    first_end=x.tick;data['first_use_complete']=x.save(a.out/'PRIMER_USO_ESTADO_COMPLETO.deetsnap.gz')
    for name,callback in(('less',lambda:e.context(x,value=64,method='B')),('more',lambda:e.context(x,value=117,method='B')),('near',lambda:pc.current_dose(x,parameter=3,load=4)),('far',lambda:pc.current_dose(x,parameter=-3,load=6)),('contact',lambda:e.contact_query(x,frame='contactoA')),('free',lambda:e.contact_query(x,frame='freeRepair5'))):data['panels'].append({'block':'after_first_use','name':name,'answer':callback()})
    data['before_old_reader_complete']=x.save(a.out/'ANTES_LECTOR_ANTERIOR_ESTADO_COMPLETO.deetsnap.gz');capture('after_new_experiences')
    # Historical source Mplus is fixed by the first declared task, never by code.
    Mplus=[19,19,50];old_query=e.tick_at_or_after(x.tick,phase=(data['first_preparation']['INSTRUMENTO']['epoch']+161)%67,lead=5);data['requests'].append(guard(x.world,'AA01.R40.HISTORICAL_MPLUS',e.move(Mplus,(1,1,0),-3),old_query-3,direction=(1,1,0),semantic=1,payload=5));x.run_until(old_query);data['historical_source_read']=observe(x.world,Mplus);data['old_code_reintroduced_after_first_block']=False
    backup=[19,11,50]
    if'cut_backup'in a.case or'sham_backup'in a.case:
        for sign in(-1,1):
            site=e.move(backup,(0,0,sign),4)
            if'sham_backup'in a.case:site=e.move(site,(1,0,0),13)
            data['requests'].append(guard(x.world,'AA01.R40.BACKUP_CUT.'+str(sign),site,x.tick+3,semantic=4,payload=0))
    delay=(6-x.tick%67)%67;data['second_preparation']=aa.prepare_local_episode(x,episode='R40_ACCESS_ONLY',availability=[1,1],contents=None,recipient_mode='immediate_yz',feedback='omit_all'if'no_access_teaching'in a.case else'paired',delay=delay);data['later_content_teacher_inputs']=[q for q in data['second_preparation']['INSTRUMENTO']['requests']if'.NEW.'in q['port']]
    if data['later_content_teacher_inputs']:raise AssertionError('This recovery arm must not reteach either original content')
    data['before_access_teaching_complete']=x.save(a.out/'ANTES_APRENDER_ACCESO_ESTADO_COMPLETO.deetsnap.gz')
    for stage in('first','learned','access','received','use'):
        answer=aa.advance_episode(x,stage=stage,max_seconds=90);data['stages'].append({'block':'access_without_content_reteaching','stage':stage,'answer':answer})
        if stage in('learned','access','use'):capture('recovery_'+stage)
    data['second_use_complete']=x.save(a.out/'SEGUNDO_USO_ESTADO_COMPLETO.deetsnap.gz')
    for name,callback in(('less',lambda:e.context(x,value=73,method='B')),('more',lambda:e.context(x,value=121,method='B')),('near',lambda:pc.current_dose(x,parameter=5,load=3)),('far',lambda:pc.current_dose(x,parameter=-5,load=3)),('contact',lambda:e.contact_query(x,frame='contactoA')),('free',lambda:e.contact_query(x,frame='freeRepair5'))):data['panels'].append({'block':'final','name':name,'answer':callback()})
    capture('final');data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime);return{'life':life,'tick':x.tick,'old_reader_direction':data['historical_source_read']['direction'],'old_reader_content_code':[z for z in(-1,1)if e.valid(data['historical_source_read'],(1,1,z))],'second_block_content_inputs':len(data['later_content_teacher_inputs']),'recovery':[{'stage':r['stage'],'codes':r['answer']['CONTENT_CODES']}for r in data['stages']if r['block']=='access_without_content_reteaching'],'final_panel':{r['name']:r['answer'].get('SPANISH_DECODED',r['answer'].get('TRADUCCION',{}).get('SPANISH_DECODED'))for r in data['panels']if r['block']=='final'}}
try:data['commit']=s.mutate(life,'AA01_RECOVERED_OLD_CONTENT_IMMEDIATE_NATIVE_PARTICIPANT_USE_46',trial)
except Exception as error:
    data['failure']={'type':type(error).__name__,'detail':str(error)};data['reached_record']=s.record(life);raise
finally:
    with gzip.open(a.out/'PRIMARIOS.json.gz','wt',encoding='utf8',compresslevel=9)as f:json.dump(data,f,ensure_ascii=False,separators=(',',':'))
print(json.dumps(data.get('commit',{}).get('result',{}),ensure_ascii=False))
