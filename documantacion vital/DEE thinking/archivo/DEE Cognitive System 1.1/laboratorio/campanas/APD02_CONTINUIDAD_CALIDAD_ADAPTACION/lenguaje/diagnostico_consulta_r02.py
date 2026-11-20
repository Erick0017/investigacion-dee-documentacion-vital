"""Prospective 2x2 material query autopsy; full copies, no service cloning."""
import argparse,gc,gzip,hashlib,importlib.util,json,os,sys,time
from pathlib import Path
from datetime import datetime,timezone
os.environ['OMP_NUM_THREADS']='1'
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];S=ROOT/'sistema'
SOURCE=S/'estado/checkpoints/APD02_MAIN.T361114.97439697e3b9.deetsnap.gz'
SOURCE_SHA='c93a93c0fcddf3814cba18dd11f5a9d24fb70cb981986dbdad0783cba1efcf1d'
DEADLINE=datetime(2026,10,26,11,17,43,tzinfo=timezone.utc)
ARMS=[('A1_B1',True,True),('A0_B1',False,True),('A1_B0',True,False),('A0_B0',False,False)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    data=(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    with p.open('xb')as f:f.write(gzip.compress(data,mtime=0)if p.suffix=='.gz'else data)
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    if args.out.exists():raise FileExistsError('Preserve all previously executed evidence')
    if sha(SOURCE)!=SOURCE_SHA:raise ValueError('Immutable parent differs')
    args.out.mkdir(parents=True)
    sys.path.insert(0,str(S))
    from app.process_control import protect_current,current_resources
    protect_current(output=args.out/'RECURSOS.json',memory_limit=536870912)
    from app.lives import load_adapter
    from app.native_tools import physical
    from capacidades import mente_acumulativa_r02 as ma
    code=LAB/'lexico_apd02_01.py';spec=importlib.util.spec_from_file_location('candidate_lexical_apd02',code)
    lex=importlib.util.module_from_spec(spec);spec.loader.exec_module(lex)
    dependencies=[Path(__file__),code,S/'capacidades/mente_acumulativa_r02.py',S/'capacidades/lexico_apd_extendido_04.py',S/'capacidades/mente_unificada_01.py']
    for f in dependencies:(args.out/f.name).write_bytes(f.read_bytes())
    write(args.out/'PROTOCOLO_CONGELADO.json',{'schema':'APD02.lexical_query_autopsy.R02','status':'FROZEN_BEFORE_FIRST_TICK',
        'source':str(SOURCE),'source_sha256':SOURCE_SHA,'source_tick':361114,'profile':'fisica_directa','N':67,
        'arms':ARMS,'sources':{str(f):sha(f)for f in dependencies},'common_B_lesson':{'form':'recuerda','sign':-1,'start':361334},
        'A_window':[362410,362477],'B_window':[362477,362544],'old_panel_before':True,'old_panel_after_start':362544,
        'functional_interactions_after_word':False,'reader_sites':28,'no_MAIN_or_original_changes':True,
        'no_service_clone':'Full native diagnostic copy; service SQLite untouched; native queues/interfaces retained',
        'deadline_utc':DEADLINE.isoformat(),'max_seconds':230})
    started=time.monotonic();summaries=[]
    def neighbourhood(a):
        return {'tick':int(a.tick),'sites':[ma.view(a,tuple((lex.H[i]+off[i])%67 for i in range(3)))for off in
            ((x,y,z)for x in range(-1,7)for y in range(-1,7)for z in range(-3,4))]}
    def snapshot(a,folder,name):
        path=folder/(name+'.deetsnap.gz');a.save(path)
        return {'path':str(path),'sha256':sha(path),'physical':physical(a.world)}
    for name,do_a,do_b in ARMS:
        folder=args.out/name;folder.mkdir();a=load_adapter('fisica_directa',SOURCE);advance=a.run_until
        def guarded(t):
            if time.monotonic()-started>230 or datetime.now(timezone.utc)>=DEADLINE:raise TimeoutError('Bounded diagnostic; preserve future')
            return advance(t)
        a.run_until=guarded
        r={'arm':name,'A_material_query':do_a,'B_material_query':do_b,'initial':physical(a.world),'error':None,'queries':[]}
        try:
            r['preparation']=lex.prepare(a)
            a.run_until(361200);a.run_until(((int(a.tick)//67)+1)*67+3)
            a.run_until(361334);r['lesson_B']=lex.teach(a,'recuerda',-1)
            a.run_until(361600);r['old_before']=[lex.query(a,f,detailed=True)for f in lex.old.FORM_CODEC]
            if int(a.tick)!=362410:raise AssertionError('Common old panel phase differs')
            r['before_queries']=snapshot(a,folder,'ANTES_CONSULTAS');r['context_before_A']=neighbourhood(a)
            if do_a:r['queries'].append(lex.query(a,'compara',detailed=True))
            else:a.run_until(362477)
            if int(a.tick)!=362477:raise AssertionError('A query horizon changed')
            r['context_after_A']=neighbourhood(a);r['after_A']=snapshot(a,folder,'DESPUES_A')
            if do_b:r['queries'].append(lex.query(a,'recuerda',detailed=True))
            else:a.run_until(362544)
            if int(a.tick)!=362544:raise AssertionError('B query horizon changed')
            r['context_after_B']=neighbourhood(a);r['after_B']=snapshot(a,folder,'DESPUES_B')
            r['old_after']=[lex.query(a,f,detailed=True)for f in lex.old.FORM_CODEC]
        except BaseException as e:r['error']={'type':type(e).__name__,'message':str(e),'future_preserved':True}
        finally:
            a.run_until=advance;r['final']=snapshot(a,folder,'FINAL');r['resources']=current_resources()
        write(folder/'PRIMARIO.json.gz',r)
        rows=[x for k in ('preparation','lesson_B','old_before','queries','old_after')for x in (r.get(k,[])if isinstance(r.get(k),list)else[r.get(k,{})])]
        receipts=[q for x in rows for q in x.get('requests',[])]
        statuses={}
        for q in receipts:
            status=q.get('receipt',{}).get('status','missing');statuses[status]=statuses.get(status,0)+1
        summary={'arm':name,'old_before':[(x['form'],x['reader']['formed_native_command'])for x in r.get('old_before',[])],
            'queries':[(x['form'],x['reader']['formed_native_command'])for x in r.get('queries',[])],
            'old_after':[(x['form'],x['reader']['formed_native_command'])for x in r.get('old_after',[])],
            'requested':len(receipts),'receipts':statuses,'tick':r['final']['physical']['tick'],'error':r['error'],
            'snapshot':r['final']}
        summaries.append(summary);write(folder/'RESUMEN.json',summary)
        advance=None;guarded=None;del a;gc.collect()
    result={'cases':summaries,'host_seconds':time.monotonic()-started,'parent_unchanged':sha(SOURCE)==SOURCE_SHA,'resources':current_resources()}
    write(args.out/'RESULTADO.json',result);print(json.dumps(result,ensure_ascii=False))
    if any(x['error']for x in summaries):raise SystemExit(2)
if __name__=='__main__':main()
