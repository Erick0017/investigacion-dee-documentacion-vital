"""Finite new equality-signal preparations using the mapped probe timing.

New recipe revision and lives; no silent reinterpretation of equalityR3.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
from instrumentos_pc01 import guard,witness,receipts,sha
import dee_thinking as d
from dee_thinking.persistence import encode_metadata
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='ES01_MAIN_04';life='PC01_IGUAL12_'+a.case;s.fork(parent,life,kind='CANDIDATE');delay=1 if a.case.startswith('delay')else 0;cue_delay=1 if a.case=='delay_cue'else 0;data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'phases':[],'criteria_before':'New equality signal protocol revisionPC12. Fixed teacher+X, fixed hub and signature[1,-1,1], phase7or8declared. No current-value comparison inside participant/decoder. All current equality uses require prior+postqualified signal and native increment7. A missing signal is indeterminate, neverNOT. Test6currentvalues before looking at outcomes, then old comparison/contact/free/time.'}
def trial(x):
    g=e.prepare(x);c=g['center'];hub=e.move(c,(0,-3,4));ports={}
    for role,target,v,lead in(('probe',c,(0,1,0),1),('cue',hub,(1,0,0),3),('query',hub,(1,0,0),3)):
        ch=d.ChannelSpec();ch.name='PC01.EQ12.'+role;ch.injection_site=d.Coordinate(*e.move(target,v,-lead));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=ch.name;p.channel=ch;x.world.declare_interface(p);ports[role]=ch.name
    entry={'schema':'PC01.equality.delayed_probe.recipe.v12','hub':hub,'ports':ports,'probe_delay':delay,'cue_delay':cue_delay,'phase':7+cue_delay,'native_signature':[1,-1,1],'not_old_equality_R3':True};data['pre']=physical(x.world,occupation=True);data['recipe']=entry
    def present(value,teacher=False):
        comp=e.tick_at_or_after(x.tick,phase=3,lead=8);first=len(x.quantity.state['requests']);x.quantity.present_object(value,round_index=(comp-70)//67);x.quantity.input('quantity.reader',7,comp-1,True);req=[]
        if a.case!='no_probe':
            r=x.world.probe(ports['probe'],0,comp+delay);req.append({'port':ports['probe'],'payload':0,'tick':comp+delay,'id':int(r.id)})
        if teacher and a.case!='delay_no_cue':
            r=x.world.submit(ports['cue'],5,comp+1+cue_delay);req.append({'port':ports['cue'],'payload':5,'tick':comp+1+cue_delay,'id':int(r.id)})
        x.run_until(comp);native=observe(x.world,c);x.run_until(comp+4+cue_delay);word=observe(x.world,hub)
        return{'actual_value':value,'teacher':teacher,'native_comparison':native,'word':word,'context':witness(x.world,hub,3),'requests':[e.receipt_at(x.world,r)for r in req],'quantity_requests':x.quantity.receipts()[first:]}
    data['teaching']=present(86,True)
    data['recalls']=[]
    for j in range(2):
        target=e.tick_at_or_after(x.tick,phase=entry['phase'],lead=3);r=x.world.probe(ports['query'],7,target-3);x.run_until(target);data['recalls'].append({'record':observe(x.world,hub),'receipt_id':int(r.id)})
    for value in(56,110,86,61,86,119):
        baseline=e.tick_at_or_after(x.tick,phase=entry['phase']);x.run_until(baseline);before=observe(x.world,hub);row=present(value,False);after=row['word'];delta=after['s_reg']-before['s_reg'];row.update(before=before,native_increment=delta,SPANISH_DECODED=['igual']if e.valid(before,(1,-1,1))and e.valid(after,(1,-1,1))and delta==7 else[]);data['phases'].append(row)
    data['less']=e.context(x,value=70,method='B');data['more']=e.context(x,value=120,method='B');data['contact']=e.contact_query(x,frame='contactoA');data['free']=e.contact_query(x,frame='freeRepair5');data['time']=e.temporal_query(x,frame='secuenciaA');data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime);x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.PC01.equality12',encode_metadata(entry))
    return{'tick':x.tick,'learned_word_signature':e.valid(data['teaching']['word'],(1,-1,1)),'recall_signatures':[e.valid(r['record'],(1,-1,1))for r in data['recalls']],'current_equal_words':[r['SPANISH_DECODED']for r in data['phases']],'less':data['less']['TRADUCCION']['SPANISH_DECODED'],'more':data['more']['TRADUCCION']['SPANISH_DECODED'],'contact':data['contact']['SPANISH_DECODED'],'free':data['free']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'PC01_PROBE_TIMING_EQUALITY_APPLICATION12',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
