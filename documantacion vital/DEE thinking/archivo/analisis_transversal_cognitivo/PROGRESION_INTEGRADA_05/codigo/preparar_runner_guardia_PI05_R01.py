"""Create a separately preregistered guard/sham runner; never starts Native."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;P=H.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(t,a,b):
    if t.count(a)!=1:raise ValueError('Exact runner anchor absent: '+a[:80])
    return t.replace(a,b,1)
def main():
    source=H/'ejecutar_FI_PI05_R01.py';t=source.read_text('utf8');dest=H/'ejecutar_FI_GUARDIA_PI05_R01.py'
    if dest.exists():raise ValueError('Preserve existing guard runner')
    t=t.replace("PROTOCOL=P/'control/PROTOCOLO_FI_PI05_R01.json'","PROTOCOL=P/'control/PROTOCOLO_FI_GUARDIA_PI05_R01.json'")
    t=once(t,"def literal(left,right,capture):return {'modo':'eci01-pi05-fiplus','izquierda':left,'derecha':right,'captura':capture}",
        "def literal(left,right,capture,condition):return {'modo':'eci01-pi05-fiplus-guardia'if condition=='guardia'else'eci01-pi05-fiplus-sham','izquierda':left,'derecha':right,'captura':capture}")
    t=once(t,"need(a.izquierda==14 and a.derecha in(2,3,4),'R01 only public left14/right2,3,4; broader domain requires a new prospective protocol')",
        "need(a.izquierda==14 and a.derecha==3 and a.captura=='global','First causal guard/sham protocol only14/3 and global69; no reserved tuning')")
    a="need(p['instrument_protocol_sha256']==sha(INSTRUMENT),'Instrument protocol differs from frozen runner protocol')"
    b=a+"\n need(p['guard_protocol_sha256']==sha(S/'capacidades/PROTOCOLO_PI05_GUARDIA_R01.json'),'Frozen guard protocol differs')\n need(p['guard_module_sha256']==sha(S/'capacidades/pi05_guardia_transito_R01.py'),'Frozen guard source differs')"
    t=once(t,a,b)
    t=once(t,"request=literal(a.izquierda,a.derecha,a.captura)","request=literal(a.izquierda,a.derecha,a.captura,a.condicion)")
    t=once(t,"need(summary['Native_inputs']['unique_requested']==176,'Original Native dose differs; preserve future')",
        "need(summary['Native_inputs']['unique_requested']==177,'Old176 plus exactly1support required; preserve actual future')\n   support=actual['result']['rows'][0]['support'];sr=support['request']\n   need(sr['tick']==817878 and sr['payload']==0 and sr['declared_state']==0 and sr['declared_semantic']==4,'Support dose/phase changed')\n   need(sr['receipt']['status']=='applied','Support rejected; preserve without clearing or retry')\n   need(support['physical_before_scheduling']==support['physical_after_scheduling'] and support['no_tick_advance_to_prepare'],'Support preparation changed physical age/fields')\n   need(int(support['before']['raw'])==0 and int(support['after']['raw'])==(4<<60),'Support not legally admitted/persistent')")
    t=t.replace("'schema':'DEE.PI05.single_FI.actual.R01'","'schema':'DEE.PI05.P0_guard_sham_FI.actual.R01'")
    t=once(t,"'life_id':a.vida,'capture_condition':a.captura,","'life_id':a.vida,'intervention_condition':a.condicion,'capture_condition':a.captura,")
    t=once(t,"ap.add_argument('--tag',required=True);ap.add_argument('--dry-run'", "ap.add_argument('--tag',required=True);ap.add_argument('--condicion',choices=('guardia','sham'),required=True);ap.add_argument('--dry-run'")
    ast.parse(t);dest.write_text(t,encoding='utf8')
    patch=H/'FUENTES_GUARDIA_PI05_R01_SELLADAS/capacidades'
    protocol={'schema':'DEE.PI05.P0_guard_sham_runner.R01','status':'PREREGISTERED_BEFORE_NATIVE','runner_sha256':sha(dest),
        'original_runner':{'file':str(source),'sha256':sha(source)},
        'instrument_protocol_sha256':sha(H/'PROTOCOLO_PI05_TRANSITO_R01.json'),
        'guard_protocol_sha256':sha(patch/'PROTOCOLO_PI05_GUARDIA_R01.json'),
        'guard_module_sha256':sha(patch/'pi05_guardia_transito_R01.py'),
        'source_full_pair':{'path':str(P/'pares/REAL_PREFI_T817876'),'manifest_sha256':sha(P/'pares/REAL_PREFI_T817876/EXPORTACION_SERVICIO.json')},
        'conditions':['guardia','sham'],'public_left':14,'public_right':3,'capture':'global','before_tick':817876,'after_tick':818074,
        'old_inputs':176,'one_fixed_extra_input':1,'total_inputs':177,'same_old_readers_q4_q6':True,
        'prospective_observables':['Support RAW-empty birth/applied/persistentSEM4, noHostRAWclockwrite','Global transit and parentRupdates','Original q4/q6 answer with176oldinputs+1matchedsupport','Adverse/rejected/NULL outcomes retained'],
        'no_success_assumed':True,'classification':'PreparedP0causal support trial; no learned regulation or autonomous recovery'}
    out=P/'control/PROTOCOLO_FI_GUARDIA_PI05_R01.json'
    if out.exists():raise ValueError('Prior runner protocol protected')
    out.write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'runner':str(dest),'runner_sha256':sha(dest),'protocol':str(out),'protocol_sha256':sha(out),'Native_executed':False}))
if __name__=='__main__':main()
