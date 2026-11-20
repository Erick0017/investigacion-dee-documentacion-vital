"""Snapshot cut/index generation, zero physics; preserves previous resumption."""
from pathlib import Path
import hashlib,json,time
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    old=read(EV/'00_PADRES_Y_PLAZO.json');protected={}
    for life,reference in old['records'].items():
        path=ROOT/'sistema/estado/vidas'/life/'VIDA.json';r=read(path);snap=ROOT/'sistema'/r['snapshot']
        good=sha(path)==reference['record_sha256']and sha(snap)==reference['snapshot_sha256']
        protected[life]={'record_and_complete_snapshot_unchanged':good,'snapshot_sha256':sha(snap)}
        if not good:raise AssertionError('Protected parent changed: '+life)
    names=['MA_MAIN_R9','MA_R9_OMIT','MA_C2_OMIT','MA_FINAL_NO_B','MA_SOCIAL_TRACE','MA_U0_ACUMULATIVO_AUX']
    lives={}
    for life in names:
        r=read(ROOT/'sistema/estado/vidas'/life/'VIDA.json');p=ROOT/'sistema'/r['snapshot']
        if sha(p)!=r['snapshot_sha256']:raise ValueError('Current full state identity failure '+life)
        lives[life]={k:r[k]for k in('life_id','profile','branch','parent','snapshot','snapshot_sha256','physical')}
        lives[life]['snapshot_bytes']=p.stat().st_size
    active=read(ROOT/'sistema/estado/ACTIVO.json')
    if active['life_id']!='MA_MAIN_R9'or active['snapshot_sha256']!=lives['MA_MAIN_R9']['snapshot_sha256']:raise ValueError('Wrong or stale selected continuation')
    calc=read(EV/'recalculo/FINAL/RESULTADOS.json');trace=read(EV/'recalculo/FINAL/TRAZA_SOCIAL.json')
    if calc['discrepancies']or trace['discrepancies']:raise ValueError('Primary recalculation discrepancies')
    budget=read(LAB/'PRESUPUESTO.json')
    continuity=dict(campaign='MENTE_ACUMULATIVA',state='NATIVE_RESEARCH_CLOSED_DISTRIBUTION_PENDING',
      selected_development='MA_MAIN_R9',protected_reference='E1_SOCIAL_11',
      selected_state=lives['MA_MAIN_R9'],complementary_state=lives['MA_U0_ACUMULATIVO_AUX'],
      lives=lives,active=active,protected=protected,
      current_R9=dict(own=[554,548],context=[7,5],private_B=[61,19],effective_current_criterion=10,
        accessible_use='Last8/8 plus2/2 new current-domain actions, same life and another process.',
        not_preserved='Four context-specific policies; old criterion14. Private B fields still present but new social functional dependence not demonstrated.'),
      current_U0=dict(lower_associations={'L03':-1,'L04':-1,'L05':-1,'L06':1,'L07':-1},
        access='5/5 operator-addressed queries after import, plus reload/save. Initial native two-bank order/query/action chain belongs to its own earlier history and cannot yet be replayed indefinitely through the official API.'),
      results=calc['lives'],first_use_panels=calc['first_use_panels'],
      no_P2_R2_or_new_NSM65_claim=True,
      continuation_commands=['mente-estado','bifurcar MA_MAIN_R9 MI_COPIA','mente-sesion --vida MI_COPIA --situaciones JSON','guardar --vida MI_COPIA'],
      full_distribution='cognitive sistem/entregas/cognitive_sistem_colaborador.zip; final exact extraction test is recorded outside the ZIP.',
      analysis_is_not_complete_state_backup=True,
      deadline_utc=budget['deadline_utc'],deadline_monotonic=budget['deadline_monotonic'],
      budget_not_restarted=True,closed_monotonic=time.monotonic(),
      next_question='A common native access mechanism that retains contextual distinctions without the scalar overwriting or recurrent multi-bank ambiguity observed here; no automatic next campaign is started.')
    put(ROOT/'CONTINUIDAD_MENTE_ACUMULATIVA.json',continuity)
    put(LAB/'CONTINUIDAD_MENTE_ACUMULATIVA.json',continuity)
    previous=ROOT/'REANUDACION.json';backup=EV/'REANUDACION_ANTERIOR.json'
    if previous.exists()and not backup.exists():backup.write_bytes(previous.read_bytes())
    put(previous,{'campaign':'MENTE_ACUMULATIVA','state':'NATIVE_CLOSED_DELIVERY_PENDING','continuity':'CONTINUIDAD_MENTE_ACUMULATIVA.json','selected_development':'MA_MAIN_R9','protected_reference':'E1_SOCIAL_11','current_lives':list(lives.values()),'deadline_utc':budget['deadline_utc'],'budget_not_restarted':True,'do_not_repeat_finished_experiments':True})
    project=read(ROOT/'PROYECTO.json')
    project.update(latest_closed_native_cut='MENTE_ACUMULATIVA: MA_MAIN_R9 T230379 selected development continuation; auxiliary independent U0 T740. Four contextual policies not retained.',current_continuity='CONTINUIDAD_MENTE_ACUMULATIVA.json')
    put(ROOT/'PROYECTO.json',project)
    put(EV/'CORTE_OPERATIVO_FINAL.json',continuity)
    print(json.dumps({'current':active,'parents_unchanged':protected,'recalculation_discrepancies':calc['discrepancies'],'remaining_before_deadline_seconds':budget['deadline_monotonic']-time.monotonic()},ensure_ascii=False))
if __name__=='__main__':main()
