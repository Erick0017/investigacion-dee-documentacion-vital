"""R2 phase-aligned paired/past-outcome Spanish cues on an exact E1 branch.

The geometric sign split and comparator are prepared. Native current objects
produce the sign, not a Python comparison. Word cues are explicit pedagogy.
Every evaluation probes both word banks; no target is sent during testing.
"""
from pathlib import Path
import argparse,json,sys,hashlib,time
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',choices=['paired','after1','after2','omitted','opposite','offpath','noevent'],required=True);a=p.parse_args()
sys.path.insert(0,str(a.system));from app.lives import Store
from app.native_tools import observe,physical,moore27
from app.process_control import protect_current
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);life='ES01_R2_'+a.case;s.fork('ES01_MAIN_R0',life,kind='CANDIDATE')
data={'case_id':'ES01_R2_'+a.case,'life':life,'parent':s.record('ES01_MAIN_R0'),'mode':a.case,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'frames':[],'requested':[],'pedagogy':'Externally labelled experiences; equality is a new-object contrast, not a trained Spanish word','plan_fixed_before_run':True,'evaluation_target_in_participant':False,'repair':'First read3489 matches learned material return; R1read3490 is retained as access failure.'}
def move(p,v,k=1):return[(p[i]+v[i]*k)%67 for i in range(3)]
def execute(x):
    w=x.world;c=x.quantity.geometry['center'];geometry={}
    def port(name,target,v):
        ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*move(target,v,-3));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
        q=d.InterfaceSpec();q.name=name;q.channel=ch;w.declare_interface(q)
    for word,sign in [('menos',1),('mas',-1)]:
        hub=move(c,(sign,0,0),2);geometry[word]={'hub':hub,'prepared_sign_side':sign}
        for role,v in [('cue',(0,1,0)),('query_plus',(0,0,1)),('query_minus',(0,0,-1))]:port('EF01.R1.'+word+'.'+role,hub,v)
        port('EF01.R1.'+word+'.sham',move(hub,(0,0,1),8),(0,1,0))
    data['geometry']=geometry;data['before_register']=data.get('before_register',physical(w,occupation=True))
    def send(name,load,t,probe=False):
        r=(w.probe if probe else w.submit)(name,load,t);data['requested'].append({'port':name,'payload':load,'tick':t,'probe':probe,'id':int(r.id)})
    def frame(label):
        data['frames'].append({'label':label,'tick':x.tick,'physical':physical(w,occupation=True),'center':observe(w,c),'words':{word:{'record':observe(w,g['hub']),'neighborhood':moore27(w,g['hub'])}for word,g in geometry.items()}})
    frame('initial')
    for index,(value,word)in enumerate([(50,'menos'),(82,'mas'),(73,None)]):
        k=48+index;center=70+67*k;event=center+2
        if a.case!='noevent' and index<2 or index==2:x.quantity.present_object(value,round_index=k)
        x.quantity.input('quantity.reader',7,center-1,True)
        if word and a.case!='omitted':
            chosen=('mas'if word=='menos'else'menos')if a.case=='opposite'else word
            delay={'after1':1,'after2':2}.get(a.case,0)
            send('EF01.R1.'+chosen+('.sham'if a.case=='offpath'else'.cue'),5,event-3+delay)
        x.run_until(center-1);frame('pre_comparison_'+str(index))
        for t in [center,center+1,center+2,center+3,center+4]:
            x.run_until(t);frame('experience_'+str(index))
    # Word-only after both relation experiences. No correct class or object.
    for j in range(8):
        t=3489+67*j;role='query_plus'if j%2==0 else'query_minus'
        for word in geometry:send('EF01.R1.'+word+'.'+role,7,t-3,True)
        x.run_until(t-1);frame('pre_word_only_'+str(j))
        x.run_until(t);frame('word_only_'+str(j))
        if j in(0,3,7):x.save(a.out/('T'+str(x.tick)+'.deetsnap.gz'))
    w.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.EF01.R1',encode_metadata({'geometry':geometry,'case':a.case,'prepared_sign_split':True,'word_teaching_external':True,'not_general_language':True}))
    data['post']=physical(w,occupation=True);data['receipts']=[{**r,'receipt':__import__('dee_thinking').consolidated.exact_receipt(w.runtime.receipt(r['id']))}for r in data['requested']]
    return{'case':a.case,'tick':x.tick,'modality':'NEW_NATIVE_RELATION_SIGN_TEACHING_WITH_PREPARED_GEOMETRY'}
data['commit']=s.mutate(life,'EF01_WORD_RELATION_R1',execute)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'case':a.case,'tick':data['post']['tick'],'occupied':data['post']['occupied'],'responses':[{'tick':f['tick'],'words':{k:v['record']for k,v in f['words'].items()}}for f in data['frames']if f['label'].startswith('word_only')][:3]},ensure_ascii=False))

