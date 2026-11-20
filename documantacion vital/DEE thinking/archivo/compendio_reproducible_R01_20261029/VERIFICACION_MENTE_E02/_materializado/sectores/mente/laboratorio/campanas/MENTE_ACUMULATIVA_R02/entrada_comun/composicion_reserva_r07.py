"""R07: reserva posterior a R06, historias emparejadas, corte y cobertura global.
Origen completo MA02_MAIN T2486 después de servicios y retención. No avanza MAIN.
"""
import hashlib,importlib.util,json,time
from array import array
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('r06_exact',HERE/'composicion_r06.py');p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
b=p.b;r=p.r;d=b.d
SYSTEM=HERE.parents[3]/'sistema'
def global_frame(s):
    raw=s.world.runtime.raw_copy();cl=s.world.runtime.clock_copy();out=[]
    for k,x in enumerate(raw):
        if x:
            site=[k%67,(k//67)%67,k//(67*67)]
            out.append({'site':site,'raw':str(x),'clock':str(cl[k])})
    return {'tick':s.tick,'nonzero_raw':out,'RAW_sha256':hashlib.sha256(array('Q',raw).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',cl).tobytes()).hexdigest(),'coverage':'Every nonzero RAW globally, including state0; zeroRAW clocks committed by complete-array hash, full snapshot local.'}
def run(label,desired=-1,cut=False,sham=False):
    life=json.loads((SYSTEM/'estado/vidas/MA02_MAIN/VIDA.json').read_text(encoding='utf8'))
    src=SYSTEM/life['snapshot']
    if life['physical']['tick']!=2486:raise ValueError('This prospectively frozen reservation requires exact MAIN2486, no silently newer cut')
    s,initial=p.p.p.load(src,label)
    p.p.p.revise(s,1,desired,2546,'double')
    history=s.save('history_T'+str(s.tick));q=2613;st=2680
    p.inward_query(s,0,q,True);p.inward_query(s,1,st,True)
    for sg in(-1,1):
        dest=(b.I[0],b.I[1],(b.I[2]+6*sg)%67);dv=(1,1,0)
        s.send('joint.r06.resource.'+str(sg),b.add(dest,dv,-2),dv,7,st+7)
    frames=[];intervention=None;panel=[]
    for tick in range(q,st+12):
        s.world.run_until(tick)
        if tick==q+9 and(cut or sham):
            site=(b.I[0],b.I[1],b.I[2]-6);before=s.observe(site);cp=s.save('formed_first_before_cut')
            edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=int(before['raw'])if sham else 0;edit.clock=int(before['clock']);edit.label='MA02 R07 formed-stream exact sham'if sham else'MA02 R07 selective formed first-stream cut'
            s.world=s.world.diagnostic_fork([edit],True)
            intervention={'tick':tick,'site':list(site),'pre':before,'post':s.observe(site),'parent_snapshot':cp,'modality':'external diagnostic copy; not autonomous intervention or MAIN repair','actual_edits':[str(x)for x in s.world.diagnostic_edits]}
        frames.append(global_frame(s))
        if tick==st+9:panel=[s.observe((b.I[0],b.I[1],(b.I[2]+6*sg)%67))for sg in(-1,1)]
    cs=[{'site':o['site'],'sign':o['direction'][2]}for o in panel if o['state']>0 and o['semantic']==1 and o['direction']in([0,0,-1],[0,0,1])]
    row={'kind':'joint','input_tick':q,'second_tick':st,'read_tick':st+9,'end_tick':s.tick,'fixed_panel':panel,'candidates':cs,'decoded_sign':cs[0]['sign']if len(cs)==1 else None,'intervention':intervention,'frames_global_sparse':frames,'history_snapshot':history,'history_acquired_signal':desired,'observer_never_uses_history_signal':True,'evidence_mode':'new prospective reserved native execution; forked common past, not independent T0 learner'}
    s.rows.append(row)
    postjoint=s.save('joint_T'+str(s.tick))
    for j,i in enumerate([2,3,0,1],41):r.query(s,i,j*67,trace=True)
    result=s.export(initial,s.save('T'+str(s.tick)));result['post_joint_snapshot']=postjoint
    b.put(b.OUT/(label+'.R07.json.gz'),result)
    print(json.dumps({'label':label,'joint':row['decoded_sign'],'postqueries':[{'token':x['request_token'],'sign':x['decoded_sign']}for x in s.rows if x['kind']=='query'],'end':s.tick},ensure_ascii=False),flush=True)
if __name__=='__main__':
    b.put(b.OUT/'PROTOCOLO_RESERVA_R07.json',{'fixed_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'prefix':'MA02_MAIN T2486 after four actual jobs and four-content next-process use','matched_histories':'Same prefix and three beta revision inputs at2546, differing only physical teaching signal±; same load/count and later agenda','query_sequence':[2613,2680],'gate_read':2689,'hypothesis':'Concordant learned contents generate native pureZ central product; mixed histories or cutting first formed stream prevent it','cut':'At2622 global(33,33,27), erase only already formed record, preserveclock and all future inputs; exact sham keepsRAW','coverage':'Every tick2613..2691 full global nonzero RAW including inactive; no gap at toroidal crossing; full snapshots before history/cut/afterjoint/end','retention_after_composition':'First-use gamma,delta,alpha,beta at2747,2814,2881,2948; do not assume individual contents survive a merge'})
    run('MA02_R07_RES_CONCORDANT',-1);run('MA02_R07_RES_MIXED',1);run('MA02_R07_RES_CUT',-1,True,False);run('MA02_R07_RES_SHAM',-1,False,True)
