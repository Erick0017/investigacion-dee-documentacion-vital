"""Prospective bounded dose/phase contrast; importing does not import DEE."""
import hashlib,importlib.util,json
from pathlib import Path

VERSION='DEE.APD03.lexical_history_access.R04.paired_vs_desync'
MAX_TICKS=1200


def lexical_module():
    path=Path(__file__).with_name('lexico_generico_apd03_r02.py')
    spec=importlib.util.spec_from_file_location('lexical_history_r04',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def roi():
    lexical=lexical_module();g=lexical.geometry();roles={}
    def add(site,role):roles.setdefault(tuple(site),[]).append(role)
    add(lexical.K,'shared_K')
    for name,v in lexical.NEW_FORMS.items():add(lexical.pos(lexical.K,v,3),'hub_'+name)
    for row in g['new_ports']:add(row['site'],'source_'+row['form']+'_'+row['role'])
    for row in g['preparation_sites']:add(row['site'],'prepared_'+row['form'])
    for row in g['common_reader']:add(row['site'],'fixed32_'+row['form']+'_'+str(row['sign_arm']))
    return [{'site':list(p),'roles':sorted(set(role))}for p,role in sorted(roles.items())]


def plan():
    lexical=lexical_module()
    return {'schema':VERSION,'max_ticks_per_arm':MAX_TICKS,'max_seconds_all_arms':600,
        'arms':[{'A_mode':mode,'B_sign':sign,'A_sign':sign,'recording':True}
            for sign in(-1,1)for mode in('paired','desync')],
        'passivity_pair':{'repeat_arm_index':0,'recording':False,'same_one_tick_owner_schedule':True},
        'curriculum':['old4 before','A one lesson: paired or teacher+11, same sign and nominal cue5/teacher11 dose',
            'A two material queries','B one pre-teaching material query','B one paired lesson',
            'B two material queries','old4 after'],
        'old_sample':['suma','resta','compara','recuerda'],
        'criterion':'Both B postlesson outputs equal explicit B sign; do not change admission denominator',
        'comparison':'First compare actual B cue+teacher requested/applied/rejected, then outcomes. Do not infer facilitation from noncomparable admission.',
        'recording':'Passive Runtime.observe of declared ROI after each owner.run_until(t+1); all steps, no new probes, teacher or gate query',
        'equality':'Same initial encoded/decoded snapshot and physical hashes. Passivity pair requires exact complete end bytes and physical hashes, including serialized pending inputs/interfaces/owner progress.',
        'ROI':roi(),'geometry_module_sha256':hashlib.sha256(Path(lexical.__file__).read_bytes()).hexdigest(),
        'scope':'Four forks of one once-prepared prefix, not independent learners or MAIN experience; one extra instrumental replay.',
        'not_claimed':['toroidal lineage','P2 initiative','content-specific meta-learning','full14 retention','no loss outside ROI'],
        'new_ticks_authorized_by_this_file':False}


def run_arm(a,*,a_mode,b_sign,identity,on_event=None):
    lexical=lexical_module();lexical.get(a)
    if a_mode not in('paired','desync')or type(b_sign)is not int or b_sign not in(-1,1):raise ValueError('Frozen arm required')
    started=int(a.tick)
    def event(kind,value):
        if int(a.tick)-started>MAX_TICKS:raise ValueError('Declared1200tick arm bound exceeded')
        if on_event:on_event(kind,value)
        return value
    def old(label):
        return [{'form':form,'result':event('old_'+label+'_'+form,lexical.query(a,form,detailed=False))}
            for form in('suma','resta','compara','recuerda')]
    before=old('before')
    A=event('A_lesson',lexical.teach(a,'luma',b_sign,mode=a_mode))
    Auses=[event('A_use_'+str(i),lexical.query(a,'luma',detailed=False))for i in range(2)]
    Bfirst=event('B_before_teaching',lexical.query(a,'nara',detailed=False))
    B=event('B_lesson',lexical.teach(a,'nara',b_sign,mode='paired'))
    Buses=[event('B_use_'+str(i),lexical.query(a,'nara',detailed=False))for i in range(2)]
    after=old('after')
    return {'schema':VERSION,'identity':identity,'A_mode':a_mode,'A_sign':b_sign,'B_sign_auditor':b_sign,
        'start_tick':started,'end_tick':int(a.tick),'old_before':before,'A_lesson':A,'A_uses':Auses,
        'B_before_teaching':Bfirst,'B_lesson':B,'B_uses':Buses,'old_after':after,
        'all_initiative':'Operator-scheduled teaching/query apparatus; no autonomous initiative attribution'}


if __name__=='__main__':print(json.dumps(plan(),sort_keys=True,ensure_ascii=False,indent=2))
