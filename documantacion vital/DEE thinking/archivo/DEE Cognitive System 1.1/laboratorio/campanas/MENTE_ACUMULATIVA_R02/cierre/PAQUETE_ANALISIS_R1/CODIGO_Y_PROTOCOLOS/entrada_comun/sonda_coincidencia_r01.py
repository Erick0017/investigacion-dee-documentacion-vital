"""MA02 R01. Cribado físico acotado, sin targets en el lector común.
Nueva preparación T0 N67; no estados entrenados heredados.
"""
import gzip, hashlib, importlib.util, json, time
from pathlib import Path

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]
OLD=ROOT/'laboratorio/campanas/MENTE_ACUMULATIVA/mecanismo/enrutador_comun_sin_giros.py'
spec=importlib.util.spec_from_file_location('base_common',OLD)
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.N=67;b.I=(33,33,33);b.V=[(1,0,0),(0,1,0),(1,1,0),(-1,1,0)]
b.OUT=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02/entrada_comun'
b.OUT.mkdir(parents=True,exist_ok=True)

def keypoints():
    out=set()
    for v in b.V:
        h=b.add(b.I,v,3)
        for k in range(-2,5):
            for z in range(-4,5):out.add((b.add(h,v,k)[0],b.add(h,v,k)[1],(h[2]+z)%b.N))
    return sorted(out)

def run(label,sign=1,marker=True,request=True,delay=0):
    s=b.Common(label); initial=s.save('T0')
    s.teach(0,sign,0)
    t=67;v=b.V[0];h=b.add(b.I,v,3)
    s.world.run_until(t)
    before=s.save('antes')
    if request:s.send('common.token.0',b.I,v,5,t)
    # Dos recursos iguales no específicos del signo; convergen con las dos
    # posibilidades de respuesta en posiciones preparadas, NO el target.
    if marker:
        for z in (-1,1):
            p=b.add(h,v,1);gate=(p[0],p[1],(p[2]+z)%b.N)
            direction=(-v[0],-v[1],0)
            s.send('generic.marker.'+str(z),b.add(gate,direction,-2),direction,7,t+2+delay)
    frames=[]; points=keypoints()
    for tick in range(t,t+10):
        s.world.run_until(tick)
        frames.append({'tick':tick,'sites':[s.observe(p) for p in points]})
    final=s.save('final')
    out=s.export(initial,final);out['frames']=frames;out['pre_query']=before
    out['factors']={'sign':sign,'marker':marker,'request':request,'marker_delay':delay}
    b.put(b.OUT/(label+'.traza.json.gz'),out)
    print(json.dumps({'label':label,'tick':s.tick,'interesting':[{ 'tick':f['tick'],'points':[{'site':x['site'],'s':x['s_reg'],'dir':x['direction'],'state':x['state']} for x in f['sites']if x['state']>0 and x['direction'][2]!=0]}for f in frames]},ensure_ascii=False),flush=True)

if __name__=='__main__':
    b.put(b.OUT/'PROTOCOLO_COINCIDENCIA_R01.json',{'fixed_before_first_tick_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'new_T0':True,'N':67,'question':'Can a generic matched resource convert a current signed response into a distinguishable physical direction without knowing its sign?','reader':'Exploration only. Exact all-route frames; no action decoder selected from this screen.','factors':{'sign':[1,-1],'marker':[True,False],'request':[True,False]},'resources':'Two equal generic loads7 for both signed branches; direction inverse to request XY, arrives downstream. No correct content or target supplied.'})
    for label,sign,marker,request,delay in [('MA02_COINC_R01_PLUS',1,True,True,0),('MA02_COINC_R01_MINUS',-1,True,True,0),('MA02_COINC_R01_NOMARK',1,False,True,0),('MA02_COINC_R01_NOQUERY',1,True,False,0),('MA02_COINC_R01_LATE',1,True,True,1)]:run(label,sign,marker,request,delay)
