import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import recovery,ic_native_core as core,delayed_social as social
old=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
parents=[]
for label,file,source in [('PLUS','INTEGRATED_COST_SOCIAL_132.json','E1_INTEGRADO_COSTO_SOCIAL_01'),('MINUS','INTEGRATED_OPPOSITE_133.json','IC01_INTEGRATED_OPPOSITE_133'),('NO_CONTENT','INTEGRATED_NO_PARTNER_134.json','IC01_INTEGRATED_NO_PARTNER_134')]:
    r=json.loads((old/file).read_text(encoding='utf8'))['final_record'];parents.append((label,source,r))
cases=[]
for label,source,p in parents:
    for mode in(['resource','sham','none']if label!='NO_CONTENT'else['resource']):cases.append((label,source,p,mode))
atomic_json(EV/'ACCESO_RESERVA_PREVIA_PROTOCOLO_110.json',{
    'paired_original_age':5698,'parents':[{'label':label,'source':source,'snapshot':p['snapshot'],'sha256':p['snapshot_sha256']}for label,source,p in parents],
    'content_labels_auditor_only':'No label, old sign or private B value enters the access apparatus',
    'preparation':'Same two zero resources and fixed four ports before the loss; no resource for none, equal-dose19y off-route sham',
    'loss_query':'Same common Zminus0 probes, two full67tick cycles after the first resource anchor; no new B input',
    'later_use':'Four actual external actions through the declared fixed parallel ports; no post-failure recovery command',
    'classification':'Prepared opportunities P0; history-conditioned native path/use P1 if supported, not learned initiation P2',
    'source_byte_reuse':'Exact old lived checkpoints, not trained-state fusion or a new T0 reconstruction'})
for j,(label,source,parent,mode)in enumerate(cases):
    name='C02_PRE_'+str(110+j)+'_'+label+'_'+mode.upper()
    fork(source,name,checkpoint=parent['snapshot'])
    def trial(a):
        initial=physical(a.world,occupation=True)
        pre=recovery.preposition_social_access(a,name=name,enabled=mode!='none',sham=mode=='sham')
        qtick=pre['anchor_tick']+134
        query=recovery.query_social_access(a,name=name+'_QUERY',query_tick=qtick)
        frames=[];banks=pre['base_banks']
        for t in sorted(set([pre['anchor_tick']+3,pre['anchor_tick']+70,qtick-1,qtick,qtick+1,qtick+2,qtick+3])):
            ic.advance(a,until=t,record=False)
            frames.append({'tick':t,'banks':[{'sign':b['sign'],'original':observe(a.world,b['target']),
                'meeting':observe(a.world,core.move(b['target'],(b['sign'],0,-1),3)),
                'moving_old':observe(a.world,core.move(b['target'],(b['sign'],0,-1),max(0,t-qtick))),
                'context125':[observe(a.world,core.move(core.move(b['target'],(b['sign'],0,-1),3),(x,y,z)))for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)]if qtick-1<=t<=qtick+3 else[]}for b in banks]})
            if t in(qtick-1,qtick+3):a.save(EV/(name+'.T'+str(t)+'.deetsnap.gz'))
        actions=ic.act_external(a,steps=4)
        return{'initial':initial,'mode':mode,'preparation':pre,'common_query':query,'frames':frames,'external':actions,
               'requests':core.receipts(a,pre['requests']+query['requests']),'final':physical(a.world,occupation=True),
               'no_repair_or_new_content_after_loss':True,'label_only_for_auditor':label}
    run(name,name,trial,{'spec':'ACCESO_RESERVA_PREVIA_PROTOCOLO_110.json'})
