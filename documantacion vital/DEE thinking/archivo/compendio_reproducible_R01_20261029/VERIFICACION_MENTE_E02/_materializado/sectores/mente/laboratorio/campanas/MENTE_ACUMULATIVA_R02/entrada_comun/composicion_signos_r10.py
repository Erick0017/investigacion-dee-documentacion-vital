"""Reserva simétrica y reproducción desde snapshot/hash explícitos.

No consulta VIDA.json mutable, no avanza MAIN. Usa literalmente mecanismos
R08/R06 ya congelados; sólo varía historias docentes, no lector ni criterios.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,time
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('r08_frozen',HERE/'composicion_reserva_r08.py')
r8=importlib.util.module_from_spec(sp);sp.loader.exec_module(r8)
b=r8.b;r=r8.r;native=r8.p.d
load=r8.p.p.p.p.load
inward=r8.p.p.inward_query

def run(source,digest,label,a,beta,cut=False,sham=False):
    if hashlib.sha256(source.read_bytes()).hexdigest()!=digest:raise ValueError('Parent SHA differs; no mutable-life fallback')
    s,initial=load(source,label)
    if s.tick!=2486:raise ValueError('Requires exact selected parent T2486')
    r8.revise_four(s,0,a,2546)
    r8.revise_four(s,1,beta,2613)
    history=s.save('history_T'+str(s.tick));q=2680;st=q+67
    inward(s,0,q,True);inward(s,1,st,True)
    for sg in(-1,1):
        dest=(b.I[0],b.I[1],(b.I[2]+6*sg)%67);dv=(1,1,0)
        s.send('joint.r06.resource.'+str(sg),b.add(dest,dv,-2),dv,7,st+7)
    frames=[];intervention=None;panel=[]
    for tick in range(q,st+12):
        s.world.run_until(tick)
        if tick==q+9 and(cut or sham):
            # Select already formed first stream by predeclared teaching arm,
            # diagnostic only; the unchanged two-site reader gets no history.
            site=(b.I[0],b.I[1],(b.I[2]+6*a)%67)
            before=s.observe(site);cp=s.save('formed_before_cut')
            edit=native.ResearchStateEdit();edit.coordinate=native.Coordinate(*site)
            edit.raw=int(before['raw'])if sham else 0;edit.clock=int(before['clock'])
            edit.label='R10 exact sham'if sham else'R10 formed-stream diagnostic cut'
            s.world=s.world.diagnostic_fork([edit],True)
            intervention={'tick':tick,'site':list(site),'pre':before,'post':s.observe(site),
                'parent_snapshot':cp,'external_diagnostic_only':True,'sham':sham}
        frames.append(r8.global_frame(s))
        if tick==st+9:panel=[s.observe((b.I[0],b.I[1],(b.I[2]+6*sg)%67))for sg in(-1,1)]
    cs=[{'site':o['site'],'sign':o['direction'][2]}for o in panel
        if o['state']>0 and o['semantic']==1 and o['direction']in([0,0,-1],[0,0,1])]
    row={'kind':'joint','input_tick':q,'second_tick':st,'read_tick':st+9,
         'end_tick':s.tick,'fixed_panel':panel,'candidates':cs,
         'decoded_sign':cs[0]['sign']if len(cs)==1 else None,
         'intervention':intervention,'frames_global_sparse':frames,'history_snapshot':history,
         'history_signs':[a,beta],'reader_has_no_history_argument':True,
         'phase_shift_vs_R08':67,'scope':'New reserved cases from same complete parent, not independent T0 learners'}
    s.rows.append(row);post=s.save('joint_T'+str(s.tick))
    for j,i in enumerate([2,3,0,1],42):r.query(s,i,j*67,trace=True)
    result=s.export(initial,s.save('T'+str(s.tick)));result['post_joint_snapshot']=post
    result['explicit_parent_sha256']=digest
    b.put(b.OUT/(label+'.R10.json.gz'),result)
    print(json.dumps({'label':label,'joint':row['decoded_sign'],
        'hubs':[x['hub']for x in s.rows if x['kind']=='revision'],
        'postqueries':[x['decoded_sign']for x in s.rows if x['kind']=='query'],'end':s.tick}),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--sha256',required=True)
    p.add_argument('--prefix',default='MA02_R10');args=p.parse_args()
    source=args.snapshot.resolve(strict=True)
    if not args.prefix.replace('_','').isalnum():raise ValueError('Explicit safe prefix required')
    protocol=b.OUT/('PROTOCOLO_'+args.prefix+'.json')
    if protocol.exists():raise FileExistsError('No overwrite of frozen reservation')
    b.put(protocol,{'fixed_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
      'parent_path':str(source),'parent_sha256':args.sha256,'parent_tick':2486,
      'no_mutable_VIDA_lookup':True,'history_inputs':'Each of two contents receives four legal requests dose38; actual receipts must be checked',
      'histories':{'PLUS':[1,1],'MINUS':[-1,-1],'MIXED_PM':[1,-1],'MIXED_MP':[-1,1]},
      'times':{'alpha_teach':2546,'beta_teach':2613,'query':2680,'second':2747,'read':2756},
      'fixed_read':'Unique active SEM1 pureZ at either of the same two central gates; no sign supplied to reader',
      'cut_sham':'First formed plus stream inPLUS at2689, preserveclock, rest future unchanged',
      'future_after_composition':'First-use gamma,delta,alpha,beta at2814,2881,2948,3015',
      'no_policy_or_general_semantic_claim':True})
    cases=[('PLUS',1,1,False,False),('MINUS',-1,-1,False,False),
           ('MIXED_PM',1,-1,False,False),('MIXED_MP',-1,1,False,False),
           ('CUT_PLUS',1,1,True,False),('SHAM_PLUS',1,1,False,True)]
    for name,a,beta,cut,sham in cases:run(source,args.sha256,args.prefix+'_'+name,a,beta,cut,sham)
if __name__=='__main__':main()
