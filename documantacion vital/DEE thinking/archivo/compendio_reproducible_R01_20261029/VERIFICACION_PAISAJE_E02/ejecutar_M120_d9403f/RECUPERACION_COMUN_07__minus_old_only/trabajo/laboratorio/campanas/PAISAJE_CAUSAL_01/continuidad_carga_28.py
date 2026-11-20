"""Finite multi-function continuity beyond the mapped original failure windows.

The two exact forks receive the same new worlds/quantities and block calendar.
One receives intermediate free/contact material assays; the other only the
same final assay. This does not prohibit learning or functional questions.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import paisaje_causal_01 as pc,espanol_funcional_01 as e
from instrumentos_pc01 import frame,receipts,sha,guard,witness
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_INTEGRACION25_paired_guard';life='PC01_CONTINUIDAD28_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'blocks':[],'criteria_before':'Twelve536tickblocks=96N67returnswithactualquantity+spatialusesineveryblock. Frozenpairsbelow. Sharedcompleteparent; allfuturephysicalinputsidenticalexceptintermediatecontact/freeassaysinblocks3/6/9. Fixedcalendarend536perblockmatched. Bothkeepallfunctionalcurrentquestions; finalcommonpanelafterblock12. No infinitestabilityorindependentnclaim.','curriculum':[[61,5,2],[119,-3,4],[70,3,6],[120,-5,6],[64,5,4],[117,-3,2],[62,3,4],[118,-5,2],[65,5,6],[116,-5,4],[63,3,2],[115,-3,6]]}
def trial(x):
    data['pre']=physical(x.world,occupation=True);base=x.tick
    if a.case.startswith('far_guard'):
        data['new_mapped_intervention']=guard(x.world,'PC01.SECOND33.GUARD',[61,10 if a.case.endswith('sham')else 1,20],32584)
    elif a.case.startswith('far_divert'):
        data['new_mapped_intervention']=guard(x.world,'PC01.SECOND33.DIVERT',[60,9 if a.case.endswith('sham')else 0,19],32594,direction=(1,1,1),semantic=1,payload=0)
    if a.case.startswith('far_'):
        data['new_question']='Theoldone-offdiversiondidnotprovideindefiniteaccess. At32598anotheroccupieddestination59,1,20withnegativeX247blocksfree126. Testoneadditionalnativeoppositesideinterceptionversusredirectionwithmatchedshamsunderall12blocks, notanunboundedlistofrepairs.';data['witnesses']=[];oldrun=x.run_until
        def watched(target):
            for t in(32584,32593,32594,32595,32596,32597,32598,32599):
                if x.tick<t<=target:oldrun(t);data['witnesses'].append({'tick':t,'corridor':witness(x.world,[59,1,20],3),'physical':physical(x.world,occupation=True)})
            oldrun(target)
        x.run_until=watched
    for j,(value,k,L)in enumerate(data['curriculum']):
        x.run_until(base+j*536);row={'episode':j+1,'start_tick':x.tick,'magnitude_value':value,'spatial_parameter':k,'dose':L,'magnitude':e.context(x,value=value,method='B'),'spatial':pc.current_dose(x,parameter=k,load=L)}
        if j in(2,5,8):
            if a.case!='final_assay_only':row['contact']=e.contact_query(x,frame='contactoA');row['free']=e.contact_query(x,frame='freeRepair5')
            else:
                # Same boundaries, but no material probe at either interface.
                x.run_until(e.tick_at_or_after(x.tick,phase=e.prepare(x)['contact_frames']['contactoA']['acquired_at']%67,lead=3))
                x.run_until(e.tick_at_or_after(x.tick,phase=e.prepare(x)['contact_frames']['freeRepair5']['acquired_at']%67,lead=3))
                row['assay_omission']='Nativeexperienceandcurrentsunchanged; thisarmdoesnotinjectthetwointermediateprobeopportunities'
        end=base+(j+1)*536
        if x.tick>end:raise AssertionError('Fixedblockcalendaroverrun; do not silently change matched horizons')
        x.run_until(end);row['physical']=physical(x.world,occupation=True);row['global_sample']=frame(x.world);data['blocks'].append(row)
        if j==5:x.save(a.out/'MITAD_CONTINUIDAD_COMPLETA.deetsnap.gz')
    data['final']={'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5'),'less':e.context(x,value=66,method='B'),'more':e.context(x,value=121,method='B'),'near':pc.current_dose(x,parameter=5,load=4),'far':pc.current_dose(x,parameter=-3,load=6)}
    if a.case.startswith('far_'):x.run_until=oldrun
    data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'magnitude':[r['magnitude']['TRADUCCION']['SPANISH_DECODED']for r in data['blocks']],'spatial':[r['spatial']['SPANISH_DECODED']for r in data['blocks']],'intermediate_free':[r['free']['SPANISH_DECODED']for r in data['blocks']if'free'in r],'final':{k:v.get('SPANISH_DECODED',v.get('TRADUCCION',{}).get('SPANISH_DECODED'))for k,v in data['final'].items()}}
data['commit']=s.mutate(life,'PC01_FINITE_MULTIFUNCTION_CONTINUITY_AND_ASSAY_DOSE28',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
