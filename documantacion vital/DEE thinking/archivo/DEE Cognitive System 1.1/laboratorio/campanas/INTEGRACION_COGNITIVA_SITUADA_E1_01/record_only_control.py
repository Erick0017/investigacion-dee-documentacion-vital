from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_body as body
protect_current();s=Store();expected=json.loads((EV/'MAIN_COMMITTED_BODY_38.json').read_text())['INSTRUMENTO']['snapshot_sha256'];parent=next(p for p in(s.root/'estado/checkpoints').glob('E1_INTEGRADO_MAIN.T3312.*')if digest_file(p)==expected)
for name,sham in [('RECORD_ONLY_NO_B_94',False),('RECORD_ONLY_SHAM_95',True)]:
    if time.monotonic()>json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']:raise TimeoutError('Deadline')
    out=EV/(name+'.json');life='IC01_'+name
    if out.exists():continue
    s.fork('E1_INTEGRADO_MAIN',life,kind='DIAGNOSTIC_COPY',checkpoint=str(parent.relative_to(s.root)))
    def run(a):
        rr=[];initial=physical(a.world,occupation=True)
        for b in a.geometry['cpc9_return']['banks']:
            if sham:
                site=body.ic.move(body.ic.move(b['hub'],(0,1,0),-3),(0,0,1),9);r=body.ic.submit(a,'IC01.'+name+'.'+b['id'],site,(0,1,0),3362,5)
            else:
                rec=a.world.submit('back.'+b['id']+'.record',5,3362);r={'id':int(rec.id),'port':'back.'+b['id']+'.record','payload':5,'tick':3362}
            rr.append(r)
        h=body.attach(a);frames=[];samples=[]
        try:
            for t in(3312,3363,3364,3365,3366,3441,3500,3600,3639,3691,3710,3743,3899):
                a.run_until(t);samples.append(physical(a.world,occupation=True));frames.append({'tick':t,'banks':[{'id':b['id'],'hub_context':[body.ic.obs(a,body.ic.move(b['hub'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for b in a.geometry['cpc9_return']['banks']]})
        finally:h['detach']()
        return{'initial':initial,'sham':sham,'B_current_inputs':0,'new_record_cues':2,'later_back_queries_or_use':0,'samples':samples,'frames':frames,'requests':body.ic.receipts(a,rr),'final':physical(a.world,occupation=True)}
    r=s.mutate(life,'IC01_ISOLATED_RECORD_CUE_CAUSAL_CONTROL',run,{'source':digest_file(__file__),'same_dose_direction_and_time':True});atomic_json(out,r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
