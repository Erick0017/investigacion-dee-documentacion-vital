"""Before teaching a word, map why the +1 event failed on the actual late life.

All arms share the exact complete T36403 parent and event calendar. The
sensor does not calculate a word and no Spanish teacher cue is provided.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
from instrumentos_pc01 import Trace,witness,receipts,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='ES01_LATE_ACCESS29_passive';life='PC01_EVENT26_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY');k=3 if a.case=='full3'else 1
data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'criteria_before':'MapactualcurrenteventwithoutSpanishlabel. Samehistory/calendar; +1versus+3 and omissionofAorB. AllsixBopportunitiesarephysicallyprepared; no targetwordorpreviousresultselectstheanswer. TraceglobalRAW!=0includingstate0andexactclockexceptions.','requests':[],'critical':[]}
def trial(x):
    data['pre']=physical(x.world,occupation=True);entry=e.prepare(x)['relational_words_v2']['lexical05'];start=e.tick_at_or_after(x.tick,phase=8,lead=5);meet_delay=(11-k)//2;meet=e.move(entry['origin'],(1,1,1),k+meet_delay);data['event']={'k':k,'load_each':3,'start':start,'nominal_AB_meet':meet,'nominal_AB_meet_tick':start+meet_delay,'all_six_B':True,'teacher_signal':False};tr=Trace(x,a.out/'CAMPO_EVENTO_SIN_PALABRA.jsonl.gz',start=start-2,end=start+81).install()
    def submit(port):
        r=x.world.submit(port,3,start);data['requests'].append({'id':int(r.id),'port':port,'tick':start,'payload':3})
    if a.case!='no_A1':submit(entry['ports']['A_positions'][str(k)])
    if a.case!='no_B1':
        for row in entry['ports']['B']:submit(row['on'])
    for t in sorted(set([start-1,start,start+1,start+meet_delay-1,start+meet_delay,start+meet_delay+1,start+12,start+13,start+14,start+67+13,start+81])):
        x.run_until(t);data['critical'].append({'tick':x.tick,'meet':witness(x.world,meet,3),'banks':{b['id']:observe(x.world,b['hub'])for b in entry['banks']}})
    data['trace']=tr.close();data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'event':data['event'],'at_first_bank':[r['banks']for r in data['critical']if r['tick']==start+13],'at_return':[r['banks']for r in data['critical']if r['tick']==start+80]}
data['commit']=s.mutate(life,'PC01_CURRENT_EVENT_CAUSAL_MAP_WITHOUT_TEACHER26',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'tick':data['post']['tick'],'case':a.case,'frames':data['trace']['frames']},ensure_ascii=False))
