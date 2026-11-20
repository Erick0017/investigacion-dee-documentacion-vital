"""New T0 research preparations for scale, with equal return-count horizons.

Uses the existing quantity recipe's placements/ports, not learned records.
N83 is explicitly outside the old N67 recipe contract and is re-evaluated.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent));sys.path.insert(0,str(a.system/'organizaciones/cpc9/base_validada/cpc8/src'))
import dee_thinking as d
from integracion.quantity_core import prepare as quantity_prepare
from app.native_tools import physical,observe
from app.process_control import protect_current
from dee_thinking.persistence import save_world_snapshot,encode_metadata
from instrumentos_pc01 import guard,witness,frame,receipts,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);n,mode=a.case.split('_',1);n=int(n[1:]);recipe,g=quantity_prepare(center=(30,30,30),profile='transient',guards='on_path');recipe.dimension=n;recipe.id='PC01.scale.quantity.v1.N'+str(n);recipe.domain='NewT0nativequantityscalecomparison; not inheritedN67contract';g['N']=n;g['basic_buffer_bytes']=32*n**3;recipe.options={};w=d.OrganizationalWorld.create(recipe);center=[30,30,30]
data={'case':a.case,'life':'PC01_SCALE10_'+a.case,'parent':'NEW_T0_PREPARATION_NO_TRAINED_TRANSPLANT','type':'specialized_native_reference_and_auxiliary_association','N':n,'source_sha256':sha(__file__),'geometry':g,'interventions':[],'rounds':[],'frames':[],'reference_initial_path':[],'criteria_before':'Equal actual reference86pluscue5 acquired afterT0, equal objects and per-orbit cadence N. Compare10native returns, not equal absolute ticks only. The comparator operation/supports and clock0are prepared, not learned. N83changesphaseanddomain, not E1continuity. No electrical-energy interpretation of load.','current_values':[56,119,61,110,86,60,120,70,86,100]}
def port(name,site,vector):
    ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(*vector);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=name;p.channel=ch;w.declare_interface(p)
port('PC01.scale.material_probe',[30,29,30],(0,1,0));data['requests']=[]
def send(name,load,t,probe=False):
    r=(w.probe if probe else w.submit)(name,load,t);data['requests'].append({'id':int(r.id),'channel':name,'payload':load,'tick':t,'probe':probe})
send('quantity.reference.cue',5,0);send('quantity.reference.resource',86,0)
if mode in('guard','sham'):
    for j,x in enumerate((-2,2)):data['interventions'].append(guard(w,'PC01.SCALE.GUARD'+str(j),[30+x,28,33 if mode=='guard'else 42],1))
for j,value in enumerate(data['current_values']):
    comp=n+3+n*j;send('quantity.object.cue',5,comp-5);send('quantity.object.resource',value,comp-5);send('quantity.reader',7,comp-1,True)
    if mode!='no_probe':send('PC01.scale.material_probe',0,comp+(1 if mode=='delay'else 0),True)
aux=6*n+10;send('quantity.other.cue',5,aux);send('quantity.other.event',11,aux);send('quantity.other.cue',9,aux+n,True)
w.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.PC01.scale',encode_metadata({'N':n,'mode':mode,'reference_experience_value':86,'scheduled_current_values':data['current_values'],'host_policy':'Fixed event curriculum, no output feedback into selection','progress':'Allrequestsqueuedbeforeevolution'}))
for t in range(3):w.run_until(t+1)
data['learned_reference']=observe(w,g['reference_hub']);data['checkpoint_after_experience']=save_world_snapshot(w,a.out/'T3_ADQUIRIDO_COLA_COMPLETA.deetsnap.gz',compress=True)
for j,value in enumerate(data['current_values']):
    comp=n+3+n*j
    if j==0:
        while int(w.runtime.current_tick)<comp-2:
            t=int(w.runtime.current_tick);site=[29,(31+t-3)%n,30];data['reference_initial_path'].append({'tick':t,'site':site,'record':observe(w,site)});w.run_until(t+1)
    w.run_until(comp-1);pre={'reference':observe(w,g['reference_site']),'object':observe(w,g['object_site']),'context':witness(w,center,3)};w.run_until(comp);comparison=observe(w,center);w.run_until(comp+1);after={'slot':observe(w,[30,30,31]),'context':witness(w,[30,30,31],3)};data['rounds'].append({'round':j+1,'tick':comp,'actual_object':value,'pre':pre,'comparison':comparison,'post':after});data['frames'].append(frame(w))
    if j==5:
        w.run_until(aux+3);data['new_auxiliary_acquisition']=observe(w,g['auxiliary_hub'])
    if j==6:
        w.run_until(aux+n+3);data['later_auxiliary_query']=observe(w,g['auxiliary_hub'])
data['post']=physical(w,occupation=True);data['receipts']=receipts(w.runtime);data['final_snapshot']=save_world_snapshot(w,a.out/'FINAL_COMPLETO.deetsnap.gz',compress=True)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'case':a.case,'tick':data['post']['tick'],'reference':data['learned_reference'],'comparisons':[r['comparison']['direction']for r in data['rounds']],'aux':data.get('later_auxiliary_query'),'occupied':data['post']['occupied']},ensure_ascii=False))
