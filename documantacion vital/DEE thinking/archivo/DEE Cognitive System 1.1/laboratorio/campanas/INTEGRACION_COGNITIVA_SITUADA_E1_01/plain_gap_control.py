from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema')]
from app.lives import Store
from app.native_tools import physical,atomic_json,observe,exact_receipt,digest_file
s=Store();prefix=json.loads((EV/'COST_NATIVE_73.json').read_text())['prefix_record']
for name,reader in [('PLAIN_GAP_105',False),('PLAIN_GAP_RENEW_106',True)]:
    if time.monotonic()>json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']:raise TimeoutError('Deadline')
    s.fork('IC01_COST_NATIVE_73','IC01_'+name,kind='DIAGNOSTIC_COPY',checkpoint=prefix['snapshot'])
    def run(a):
        start=physical(a.world,occupation=True);t=3621;k=(t-70)//67;a.quantity.present_object(73,round_index=k);rr=[dict(r)for r in a.quantity.state['requests'][-2:]]
        if reader:rr.append(a.input('quantity.reader',7,t-1,'probe','FIXED_GENERIC_RENEWAL_NOT_REFERENCE'))
        frames=[]
        for at in(3553,3554,3619,3620,3621):a.run_until(at);frames.append({'tick':at,'Q':observe(a.world,a.quantity.geometry['center']),'reference_hub':observe(a.world,a.quantity.geometry['reference_hub'])})
        return{'initial':start,'reader':reader,'actual_object':73,'frames':frames,'requests':[dict(r,receipt=exact_receipt(a.world.runtime.receipt(r['id'])))for r in rr],'final':physical(a.world,occupation=True)}
    r=s.mutate('IC01_'+name,'IC01_NO_MESSAGE_NO_ROUTING_COMPARATOR_GAP',run,{'source':digest_file(__file__),'fixed_current_object_and_generic_reader':True});atomic_json(EV/(name+'.json'),r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
