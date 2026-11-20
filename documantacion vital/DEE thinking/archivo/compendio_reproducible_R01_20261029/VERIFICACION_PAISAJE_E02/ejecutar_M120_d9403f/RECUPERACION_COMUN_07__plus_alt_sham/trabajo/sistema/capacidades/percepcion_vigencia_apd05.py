"""Prepared independent-version sensor over the SAME inherited FI128 body.

This is an explicit P0 interface candidate, not learned attention. Python never
compares the two versions to choose an action. Two separate affine encodings
enter the existing native aggregate/comparator and its lived reference decides
the sign. The geometry, bias, transduction and public sentinel are prepared.
No new Runtime, RAW/clock write, favorable reader or content transplant occurs.
"""
from capacidades import ecosistema_apd04 as env
from capacidades import percepcion_cruda_fi01 as perception
from capacidades import acciones_nativas_apd04 as tools
from capacidades import lexico_compartido_apd04 as lex
from app.native_tools import physical
from dee_thinking.persistence import encode_metadata,decode_metadata

VERSION='APD05.independent_version_native_access.P0.R01'
KEY='DEE.Cognitive.System.1.1.APD05.independent_version_access.R01'
ACTION_CODEC={-1:'USE',0:'WAIT',1:'INSPECT'}
MAX_VERSION=8
BIAS=19

def validate(a,row):
    if row.get('modo')not in('apd05-vigencia-estado','apd05-vigencia-vivir'):
        raise ValueError('Unknown APD05 version-sensor operation')
    allowed={'modo'}if row['modo']=='apd05-vigencia-estado'else{'modo','oportunidades','lexico'}
    if set(row)-allowed:raise ValueError('No expected answer, relevance, source recommendation or target field accepted')
    if row['modo'].endswith('vivir')and(type(row.get('oportunidades'))is not int or not 1<=row['oportunidades']<=4):
        raise ValueError('1..4 literal opportunities required')
    if type(row.get('lexico',True))is not bool:raise ValueError('Explicit lexical use boolean required')
    if perception.get(a).get('level')!=128:raise ValueError('The existing FI128 body is required; no implicit preparation')
    m=env.get(a)
    if m.get('in_progress'):raise ValueError('Preserve the existing uncertain environmental operation')
    for obj in m['objects']:
        if type(obj['version'])is not int or not 0<=obj['version']<=MAX_VERSION:raise ValueError('Version outside frozen0..8 domain; no saturation hidden')
        observed=obj.get('observed')
        if observed is not None and(type(observed['version'])is not int or not 0<=observed['version']<=MAX_VERSION):raise ValueError('Cached version outside0..8 domain')

def independent_codec(current_version,cached_version):
    """Fixed unit conversion per sensor, never a difference/equality test.

    Visible version v is encoded v+1; a missing cached measurement is sentinel0.
    Channel0 sees2*(current+1). Channel1 sees19-2*(cached+1), or19 for missing.
    Remaining126 sources supply declared zero material. No reduction is done in
    Python. A negative, positive, absent or ambiguous native result is preserved.
    """
    for v in(current_version,cached_version):
        if v is not None and(type(v)is not int or not 0<=v<=MAX_VERSION):raise ValueError('Version domain0..8')
    if current_version is None:raise ValueError('Actual version measurement missing; no guessed value')
    current_code=current_version+1
    cached_code=0 if cached_version is None else cached_version+1
    components=[0]*128
    components[0]=2*current_code;components[1]=BIAS-2*cached_code
    return components,{'current_version':current_version,'cached_version':cached_version,
        'current_code':current_code,'cached_code':cached_code,'channel0':components[0],'channel1':components[1],
        'remaining_zero_components':126,'missing_cache_sentinel':0,'linear_units_and_bias_are_P0':True,
        'no_comparison_or_relevance_computed_by_codec':True}

def state(a):
    m=env.get(a);entries=dict(a.world.runtime.snapshot_metadata_entries)
    own=decode_metadata(entries[KEY])if KEY in entries else{'version':VERSION,'uses':0}
    if own['version']!=VERSION:raise ValueError('Different sensor history; no silent substitution')
    return {'version':VERSION,'prepared_action_codec':ACTION_CODEC,'physical':physical(a.world),
        'source_count':len(m['objects']),'cursor_environment':m['cursor'],'own_protocol':own,
        'before_choice_native_variables':['current_version','cached_version_or_absence_sentinel'],
        'not_transduced_for_this_choice':['source_id','tag','goal_tag','object_value','cache_value'],
        'scope':'Prepared local freshness-access candidate only. No general attention, learned source addressing or P2/R2 claim.'}

def live(a,count,directory,*,use_lexicon=True,detailed=False):
    from pathlib import Path
    import json
    m=env.get(a);start=physical(a.world);rows=[]
    for _ in range(count):
        obj=m['objects'][m['cursor']];cached=obj.get('observed')
        public={'source_id':obj['id'],'current_version':obj['version'],
            'cached_version':None if cached is None else cached['version'],
            'cached_value':None if cached is None else cached['value'],'word':m['word'],'loads':list(m['loads'])}
        components,codec=independent_codec(public['current_version'],public['cached_version'])
        m['episode']+=1;ep=m['episode'];m['in_progress']={'episode':ep,'tick':int(a.tick),'prepared_profile':VERSION};env.save(a,m)
        trial=perception.frame(a,components,detailed=detailed)
        reader=trial['reader'];sign=reader.get('choice');candidates=reader.get('candidates',[])
        formed=type(sign)is int and sign in(-1,0,1)and len(candidates)==1
        action=ACTION_CODEC.get(sign)if formed else None
        effect={'action':action,'valid_native':formed,'useful':False,'prepared_action_codec':VERSION,'new_fact':False}
        word=None;operation=None;artifact=None;expected=None
        if action is None:
            m['counters']['invalid']+=1;effect['reason']='no_unique_native_version_access_emission'
        elif action=='WAIT':
            m['counters'].setdefault('wait',0);m['counters']['wait']+=1;effect['reason']='formed_zero_no_task_change'
        elif action=='INSPECT':
            old=obj.get('observed');obj['observed']={'value':obj['value'],'version':obj['version']}
            effect['new_fact']=old!=obj['observed'];effect['useful']=effect['new_fact']and obj['tag']==m['goal_tag'];m['counters']['inspect']+=1
            effect['reason']='native_emission_refreshes_environmental_cache_not_native_number_memory'
        elif action=='USE':
            m['counters']['use']+=1;tool=m['word']
            if use_lexicon:
                word=lex.query(a,m['word'],detailed=detailed);tool=env.TOOL_CODEC.get(word['reader']['formed_native_command'])
            effect['tool_emitted']=tool
            if tool=='clasifica'and public['cached_value']is not None:
                operation=tools.classify(a,public['cached_value'],detail=detailed);direction=operation['physical_choice']
                if type(direction)is int and direction in(-1,0,1):
                    previous=obj['bin'];obj['bin']=direction
                    # Evaluator runs only AFTER the native command and effect.
                    expected=(obj['value']>m['criterion_auditor_only'])-(obj['value']<m['criterion_auditor_only'])
                    correct=direction==expected and obj['observed']['version']==obj['version']
                    effect.update(correct=correct,actual_bin=direction,previous_bin=previous)
                    effect['useful']=correct and obj['tag']==m['goal_tag']and previous!=direction
                    if correct:m['counters']['correct_classifications']+=1
                else:effect['reason']='no_unique_native_classification'
            elif tool=='equilibra':
                before=list(m['loads']);operation=tools.balance(a,*before,detail=detailed);direction=operation['physical_choice']
                if direction==1 and m['loads'][0]>0 and m['loads'][1]<20:m['loads'][0]-=1;m['loads'][1]+=1;m['counters']['moves']+=1
                elif direction==-1 and m['loads'][1]>0 and m['loads'][0]<20:m['loads'][1]-=1;m['loads'][0]+=1;m['counters']['moves']+=1
                if direction is not None:
                    old_gap=abs(before[0]-before[1]);new_gap=abs(m['loads'][0]-m['loads'][1])
                    effect.update(loads_before=before,loads_after=list(m['loads']),gap_before=old_gap,gap_after=new_gap,physical_move_direction=direction)
                    effect['useful']=(new_gap<old_gap or(direction==0 and old_gap==0))and obj['tag']==m['goal_tag']
            else:effect['reason']='unavailable_cached_fact_or_unformed_word'
            folder=Path(directory)/'synthetic_workshop_apd05';folder.mkdir(parents=True,exist_ok=True)
            artifact=folder/('world'+str(m['world_serial'])+'_episode'+str(ep)+'.json')
            with artifact.open('x',encoding='utf8')as f:json.dump({'schema':VERSION,'episode':ep,'native_tick':int(a.tick),'effect':effect},f,ensure_ascii=False,sort_keys=True);f.write('\n')
        if effect['useful']:m['counters']['useful']+=1
        # This P0 environment does not pretend to have a learned feedback link.
        # No R04 consequence is emitted without a corresponding delayed window.
        cursor_before=m['cursor'];m['cursor']=(m['cursor']+1)%len(m['objects']);m['in_progress']=None;env.save(a,m)
        entries=dict(a.world.runtime.snapshot_metadata_entries)
        own=decode_metadata(entries[KEY])if KEY in entries else{'version':VERSION,'uses':0}
        own['uses']+=1;a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(own))
        rows.append({'episode':ep,'public_environment_before':public,'codec':codec,'selection_native_trial':trial,
            'physical_choice':sign,'formed_unique':formed,'physical_action':action,'word':word,'native_operation':operation,
            'committed_effect':effect,'cursor_before':cursor_before,'cursor_after':m['cursor'],'artifact':None if artifact is None else str(artifact),
            'auditor_only_after_effect':{'actual_value':obj['value'],'tag':obj['tag'],'goal':m['goal_tag'],'criterion':m['criterion_auditor_only'],'expected_class':expected},
            'feedback':{'native_consequence_delivered':False,'scope':'Environment changes can become later version observations; no acquired feedback strategy is claimed.'}})
    return {'kind':VERSION,'before':start,'rows':rows,'after':physical(a.world),'state':state(a),
        'assistance':'Prepared two-version affine sensor, native FI128 aggregate/reference, fixed sign-to-access codec, circular source view and inherited lexical/tools. No Python version comparison chooses access.'}

def dispatch(a,row,directory,*,feedback='real',actuator='closed',detailed=False):
    validate(a,row)
    if actuator!='closed':raise ValueError('Version-sensor R01 only admits the declared closed actuator; no silent substitute')
    if row['modo']=='apd05-vigencia-estado':return state(a)
    return live(a,row['oportunidades'],directory,use_lexicon=row.get('lexico',True),detailed=detailed)
