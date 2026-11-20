"""Finite physical diagnostics of two new functional cues on complete forks.
Service transport is not cloned here; these are explicitly physical AUX worlds.
"""
import argparse,gc,gzip,hashlib,importlib.util,json,os,shutil,sys,time
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--sistema',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();s=a.sistema.resolve();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(s));os.environ['OMP_NUM_THREADS']='1'
    from app import process_control as pc
    pc.protect_current(memory_limit=536870912)
    from app.lives import load_adapter
    from app.native_tools import physical
    rec=json.loads((s/'estado/vidas/APD02_MAIN/VIDA.json').read_bytes());snap=s/rec['snapshot']
    if rec['physical']['tick']!=361114 or sha(snap)!='c93a93c0fcddf3814cba18dd11f5a9d24fb70cb981986dbdad0783cba1efcf1d':raise ValueError('Exact unchanged initial APD02_MAIN cut required for this diagnostic')
    code=Path(__file__).with_name('lexico_apd02_01.py');spec=importlib.util.spec_from_file_location('candidate_lexical_apd02',code);lex=importlib.util.module_from_spec(spec);spec.loader.exec_module(lex)
    for f in(Path(__file__),code):shutil.copyfile(f,out/f.name)
    arms=[('paired',1,-1,'paired'),('opposite',-1,1,'paired'),('omitted',1,-1,'omitted'),('A_only',1,None,'paired'),('B_only',None,-1,'paired'),('B_then_A',1,-1,'paired')]
    proto={'schema':'APD02.lexical_function_diagnostic.R01','parent_record':str(s/'estado/vidas/APD02_MAIN/VIDA.json'),'parent_snapshot':str(snap),'snapshot_sha256':sha(snap),'source_sha256':sha(code),'arms':arms,'fixed_reader_sites':28,'common_probe':[{'form':'compara','datum':7,'context':'gamma'},{'form':'recuerda','datum':53,'context':'beta'}],'all_arms_equal_time_before_probe':True,'no_service_clone_or_MAIN_adoption':True}
    write(out/'PROTOCOLO.json',proto);all_rows=[];started=time.monotonic()
    for name,sa,sb,mode in arms:
        folder=out/name;folder.mkdir();w=load_adapter(rec['profile'],snap);row={'arm':name,'initial':physical(w.world),'preparation':lex.prepare(w),'lessons':[]}
        w.save(folder/'ANTES_DOCENCIA.deetsnap.gz')
        order=['recuerda','compara']if name=='B_then_A'else['compara','recuerda']
        for index,form in enumerate(order):
            w.run_until(361200+index*134)
            sign=sa if form=='compara'else sb
            if sign is not None:row['lessons'].append(lex.teach(w,form,sign,mode=mode))
            else:w.run_until(((int(w.tick)//67)+1)*67+3)
        w.run_until(361600);row['before_probe']=physical(w.world)
        row['old_before']=[lex.query(w,f)for f in lex.old.FORM_CODEC]
        row['uses']=[lex.use_relation(w,f,datum,ctx,detailed=True)for f,datum,ctx in(('compara',7,'gamma'),('recuerda',53,'beta'))]
        row['old_after']=[lex.query(w,f)for f in lex.old.FORM_CODEC]
        row['final']=physical(w.world);w.save(folder/'FINAL.deetsnap.gz');all_rows.append(row)
        with gzip.GzipFile(filename=str(folder/'PRIMARIO.json.gz'),mode='wb',mtime=0)as z:z.write((json.dumps(row,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8'))
        write(out/'PROGRESO.json',{'completed':[r['arm']for r in all_rows],'host_seconds':time.monotonic()-started})
        del w;gc.collect()
    summary={'protocol':proto,'rows':all_rows,'host_seconds':time.monotonic()-started,'resources':pc.current_resources()}
    with gzip.GzipFile(filename=str(out/'PRIMARIOS_COMPLETOS.json.gz'),mode='wb',mtime=0)as z:z.write((json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'out':str(out),'arms':len(all_rows),'seconds':summary['host_seconds'],'uses':[(r['arm'],[(x['literal_form'],x['native_function_choice'],x['interaction']is not None)for x in r['uses']])for r in all_rows]},ensure_ascii=False))
if __name__=='__main__':main()
