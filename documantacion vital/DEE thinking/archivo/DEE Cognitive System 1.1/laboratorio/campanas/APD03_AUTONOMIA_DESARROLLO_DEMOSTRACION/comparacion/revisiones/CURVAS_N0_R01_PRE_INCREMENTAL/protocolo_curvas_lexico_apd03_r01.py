"""Bounded prospective APD03 curve; an existing owner's actor is required.

This module neither creates/restores lives nor executes on import. Every arm
must start as a separately identified exact copy of the once-prepared prefix.
Expected signs are used only AFTER a common-reader query for audit metrics.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

KEY='DEE.APD03.generic_lexicon_curve.prospective.R01'
HISTORIES=('related','opposite','omitted')
CRITERION_CONSECUTIVE_CORRECT=2
MAX_B_LESSONS=3


def lexical_module():
    path=Path(__file__).with_name('lexico_generico_apd03_r01.py')
    spec=importlib.util.spec_from_file_location('apd03_generic_lexicon',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def plan():
    lexical=lexical_module()
    return {'schema':KEY,'module_sha256':hashlib.sha256(Path(lexical.__file__).read_bytes()).hexdigest(),
        'prefix':'A complete APD02 parent copy after one common old14 panel, then exactly one preparation of both empty generic slots; no taught A/B content.',
        'arms':[{'history':history,'B_sign_auditor':sign,
                 'A_sign_explicit_teacher':sign if history!='opposite' else -sign,
                 'A_teacher_mode':'omitted' if history=='omitted' else 'paired'}
                for sign in(-1,1)for history in HISTORIES],
        'curriculum':[
            'one old14 material panel in the common parent only;4representative forms before/after in each branch',
            'A one paired/opposite/omitted explicit lesson, followed by2common-reader queries',
            'B first common-reader query before B teaching (initial transfer, not meta-learning)',
            'B three signed paired lessons, each followed by2common-reader queries; do not stop early or add lessons',
            'B functional use with datum23/contextgamma via the same fixed sign transduction',
            'A post-course common-reader query and final old14 material panel'],
        'criterion':{'consecutive_correct_material_queries':CRITERION_CONSECUTIVE_CORRECT,
            'max_B_lessons':MAX_B_LESSONS,'criterion_not_changed_after_results':True},
        'scope':'Six branches share a prefix, not six independent learners. A related/opposite sign can produce transfer or interference; an initial advantage alone does not demonstrate learning-to-learn.',
        'dose_limit':'Omitted A teacher has fewer material inputs; cue count/age/query count are matched and actual admission/rejection must be reported. No claim of perfectly equal material dose.',
        'no_anatomy_changes_after_prefix':True,'new_ticks_authorized_by_this_file':False,
        'old_sample':['suma','resta','compara','recuerda'],
        'sampling_limit':'Per-branch4forms cover two arithmetic signs and two prepared functional requests, not full14retention. Only the prefix has an old14panel; MAIN final requires its own full panel.',
        'geometry':lexical.geometry()}


def old_panel(a,lexical,*,label,detailed=False):
    rows=[]
    for form in('suma','resta','compara','recuerda'):
        result=lexical.query(a,form,detailed=detailed)
        rows.append({'form':form,'result':result})
    return {'kind':'common32_reader_old4_representative_material_panel','label':label,
            'rows':rows,'not_passive_observation':True}


def run_arm(a,*,history,b_sign,life_identity,detailed=False):
    lexical=lexical_module();lexical.get(a)
    if history not in HISTORIES or type(b_sign)is not int or b_sign not in(-1,1):
        raise ValueError('A preregistered history and exact signed B lesson are required')
    start_tick=int(a.tick);rows=[]
    before=old_panel(a,lexical,label='before_new_teaching',detailed=detailed)
    a_sign=-b_sign if history=='opposite' else b_sign
    mode='omitted' if history=='omitted' else 'paired'
    lesson_a=lexical.teach(a,'luma',a_sign,mode=mode)
    a_uses=[lexical.query(a,'luma',detailed=detailed) for _ in range(2)]
    first_b=lexical.query(a,'nara',detailed=detailed)
    consecutive=0;first_criterion=None
    for lesson_number in range(1,MAX_B_LESSONS+1):
        lesson=lexical.teach(a,'nara',b_sign,mode='paired')
        uses=[]
        for use_number in range(1,3):
            result=lexical.query(a,'nara',detailed=detailed)
            emitted=result['reader']['formed_native_command']
            # This comparison is an external audit after the physical use.
            correct=emitted==b_sign
            consecutive=consecutive+1 if correct else 0
            if consecutive>=CRITERION_CONSECUTIVE_CORRECT and first_criterion is None:
                first_criterion={'B_lessons':lesson_number,'B_postlesson_queries':(lesson_number-1)*2+use_number,
                    'tick':int(a.tick)}
            uses.append({'result':result,'audit_correct_after_emission':correct})
        rows.append({'B_lesson_number':lesson_number,'lesson':lesson,'uses':uses})
    functional=lexical.use_relation(a,'nara',23,'gamma',detailed=detailed)
    a_after=lexical.query(a,'luma',detailed=detailed)
    after=old_panel(a,lexical,label='after_course_and_functional_use',detailed=detailed)
    return {'schema':KEY,'life_identity':life_identity,'history':history,
        'B_sign_auditor_only':b_sign,'A_sign_explicit_teacher':a_sign,'A_teacher_mode':mode,
        'start_tick':start_tick,'end_tick':int(a.tick),'old_panel_before':before,
        'A_lesson':lesson_a,'A_uses':a_uses,'B_before_teaching':first_b,
        'B_initial_transfer_audit':first_b['reader']['formed_native_command']==b_sign,
        'B_learning_curve':rows,'criterion':plan()['criterion'],
        'first_criterion':first_criterion,'B_functional_use':functional,
        'A_after_B_course':a_after,'old_panel_after':after,
        'scope':'All learned contents belong to this branch only. Results may demonstrate acquisition, transfer, facilitation or interference. Meta-learning is not presumed.'}


if __name__=='__main__':
    print(json.dumps(plan(),ensure_ascii=False,indent=2))
