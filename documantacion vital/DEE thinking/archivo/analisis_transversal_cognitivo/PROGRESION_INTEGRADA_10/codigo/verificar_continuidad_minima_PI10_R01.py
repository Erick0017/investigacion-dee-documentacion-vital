"""PI10 initial read-only proof; no DEE import, process start or state write.

Only writes its fresh campaign evidence file. If WAL/process/queue evidence is
uncertain, preserves everything and stops rather than opening another writer.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json

P=Path(__file__).resolve().parents[1]
P9=P.with_name('PROGRESION_INTEGRADA_09')
C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad'
EXPECTED='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
SOURCE_PROC=P9/'codigo/comprobar_procesos_adopcion_D_PI09_R01.py'
PROC_SHA='9222b2fb422bb3c19d9ed4c5bf1785d2f987dd0d5533ddf9242600a563e22107'
PARSER_SHA='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873'

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):p=Path(p);return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def load(name,p,pin):
    need(sha(p)==pin,'Reviewed passive stdlib helper changed')
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main(a):
    if not a.verificar:
        print(json.dumps({'mode':'PLAN_ONLY_NO_STATE_READ','Native':0,'target':str(S),'output_scope':str(P/'control')}));return
    output=(P/'control/CONTINUIDAD_MINIMA_PI10_R01.json')
    need(not output.exists(),'Existing inspection proof preserved')
    need(not(P9/'PI09_ROOT_NATIVE_WRITER.lock').exists()and not(P/'PI10_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Scoped writer declared; do not inspect/open a writer')
    activefile=S/'estado/ACTIVO.json';active=read(activefile);life=active['life_id']
    need(life==EXPECTED,'A different selected principal needs deliberate genealogy reconciliation, not maximum tick')
    process=load('PI10_reviewed_stdlib_closed_scope',SOURCE_PROC,PROC_SHA)
    closed=process.inspect('PI10_current_main',S,life)
    need(closed['no_live_affected_writer']is True,'Current main process/queue/lock evidence uncertain: preserve and report')
    cardfile=S/'estado/vidas'/life/'VIDA.json';card=read(cardfile);snapshot=S/card['snapshot']
    need(active['tick']==card['physical']['tick']and active['snapshot_sha256']==card['snapshot_sha256']==sha(snapshot),'ACTIVO/card/snapshot pairing mismatch')
    need(card['physical']['N']==67 and card['physical']['tick']>=922371,'Wrong geometry or older returned principal')
    parser=load('PI10_reviewed_passive_snapshot',RP/'observador_pasivo.py',PARSER_SHA)
    view=parser.snapshot_view(snapshot)
    need(all(view['physical'][k]==card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),'Passive raw/clocks binding mismatch')
    keys={'D':('DEE.Cognitive.PI09.persistent_environment.D.R02',12),
      'FI8':('DEE.Cognitive.PI09.explicit_FI_eight_offer_lot.R01',8),
      'C2C':('DEE.Cognitive.PI04.C2C.coordination.R01',32),
      'R02_historical':('DEE.Cognitive.PI09.selective_registered_consultation.R02',18)}
    stocks={}
    for label,(key,total)in keys.items():
        v=json.loads(view['metadata'][key]);n=v['ordinal'];need(type(n)is int and 0<=n<=total,'Invalid finite stock')
        stocks[label]={'ordinal':n,'total':total,'remaining':total-n,'access':'historical_readonly'if label.endswith('historical')else'current_declared_finite'}
    profile=S/'contratos/PI09_D_USO_OPERATIVO_R02.json';p=read(profile)
    need(p['status']=='COMMITTED'and p['life_id']==life and p['historical_R02_material_disabled']is True,'Exact current D profile/readonly ancestry missing')
    project=read(C/'PROYECTO.json');publication=read(P9/'documentos/PUBLICACION_EDICION_1_38_PI09.json')
    manual=C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
    pub=next(r for r in publication['rows']if Path(r['source']).resolve()==manual.resolve())
    need(publication['internal_edition']=='1.38'and sha(manual)==pub['published_sha256'],'Current Manual differs from verifiedPI09 publication; inspect newer cut')
    before={str(p):sha(p)for p in(activefile,cardfile,snapshot,profile,manual)}
    result={'schema':'DEE.PI10.initial_readonly_continuity.R01','at_utc':datetime.now(timezone.utc).isoformat(),
      'Native_imported':False,'Native_ticks_added':0,'owners_started':False,'originals_modified':False,
      'selected_life':life,'world_id':card['world_id'],'profile':card['profile'],'physical':view['physical'],'parent':card['parent'],
      'ACTIVO':ref(activefile),'VIDA':ref(cardfile),'snapshot':ref(snapshot),'profile_contract':ref(profile),'manual':{**ref(manual),'internal_edition':'1.38'},
      'current_stock':stocks,'closed_writer_and_queue_scope':closed,'causal_prefix_sha256':view['causal_prefix_sha256'],
      'interfaces':view['interfaces'],'pending_native':view['pending_native'],'native_receipts':view['native_receipts'],'phase':view['phase'],
      'complete_state_roots':[str(S/'estado'/name/life)for name in('vidas','servicios_locales','servicios_persistentes')],
      'transport_complete_requirement':'The snapshot is paired with the closed full services. Root must export via the existing full-state contract before clone import.',
      'initial_protected_inputs':before,'CIM_process_inventory':'An initial scoped Get-CimInstance was denied by Windows. The existing scoped Win32 PID identity proof succeeded or this tool would stop.',
      'publication_scope':'Literal current Manual matching PI09 publication; not a new full reading/visual QA.',
      'no_response_targets_or_auditor_data_fed_to_participant':True}
    need(all(sha(Path(p))==digest for p,digest in before.items()),'A protected source changed during passive inspection')
    with output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(output),'sha256':sha(output),'selected_life':life,'N':view['physical']['N'],'T':view['physical']['tick'],'stock':stocks,'closed':True,'Native':0}))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--verificar',action='store_true');main(ap.parse_args())
