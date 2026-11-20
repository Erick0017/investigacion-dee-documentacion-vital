"""Auditor-only analytical policy references. No DEE import, ticks or controller."""
import argparse,gzip,hashlib,itertools,json
from pathlib import Path

BUDGET=2
POLICIES=('always_native','always_external','stay_until_last_cost_exceeds_budget_then_alternate')

def load(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def choose(policy,previous_action,previous_observed_cost,initial_action):
    """Policy has NO law/prices, task operands, expected answer or future argument."""
    if policy=='always_native':return'native'
    if policy=='always_external':return'external'
    if policy!='stay_until_last_cost_exceeds_budget_then_alternate':raise ValueError('Unknown auditor reference')
    if previous_action is None:return initial_action
    if previous_observed_cost is None:raise ValueError('Only an observed post-action cost can change a later choice')
    if previous_observed_cost>BUDGET:return'external'if previous_action=='native'else'native'
    return previous_action

def run(policy,law,initial_action,completion_pattern):
    """Auditor environment applies published law AFTER each policy action."""
    previous=None;cost=None;rows=[]
    for index,completed in enumerate(completion_pattern):
        action=choose(policy,previous,cost,initial_action)
        price=law['native_price']if action=='native'else law['external_price']
        if law['missing_artifact_rule']=='fixed_deadline5':actualcost=price if completed else 5
        elif law['missing_artifact_rule']=='price_plus4':actualcost=price+(0 if completed else 4)
        else:raise ValueError('Undeclared environmental noncompletion rule')
        rows.append({'opportunity':index,'action':action,
                     'policy_information_before_action':{'previous_action':previous,'previous_own_observed_cost':cost,'budget':BUDGET},
                     'assumed_completed':completed,'published_price':price,'environment_cost_after_action':actualcost,
                     'counterfactual_numeric_correctness':'INDETERMINATE_NOT_EXECUTED',
                     'counterfactual_DEE_internal_effects':'NOT_MODELLED'})
        previous=action;cost=actualcost
    return {'rows':rows,'total_modelled_cost':sum(r['environment_cost_after_action']for r in rows)}

def unit_tests():
    tests=[]
    def test(name,got,expected):
        tests.append({'name':name,'obtained':got,'expected':expected,'equal':got==expected})
    adaptive=POLICIES[2]
    for current in('native','external'):
        for cost in(0,1,2,3,5,32):
            expected=current if cost<=2 else('external'if current=='native'else'native')
            test('one_past_cost_'+current+'_'+str(cost),choose(adaptive,current,cost,'native'),expected)
    test('no_observation_does_not_guess_law',choose(adaptive,None,None,'external'),'external')
    test('source_law',[(r['action'],r['environment_cost_after_action'])for r in run(adaptive,{'native_price':1,'external_price':5,'missing_artifact_rule':'fixed_deadline5'},'external',[True]*3)['rows']],
         [('external',5),('native',1),('native',1)])
    test('reversed_law',[(r['action'],r['environment_cost_after_action'])for r in run(adaptive,{'native_price':5,'external_price':1,'missing_artifact_rule':'price_plus4'},'native',[True]*2)['rows']],
         [('native',5),('external',1)])
    return tests

def calculate(root):
    sources=[];issues=[]
    def read(name):
        p=root/name;sources.append({'file':name,'sha256':sha(p),'bytes':p.stat().st_size});return load(p)
    first=read('PROTOCOLO_RUTA_O2_R3.json');rev=read('PROTOCOLO_REVERSION_O2_R3.json')
    actual_o2={name:read('O2_'+name+'.json.gz')['result']for name in('real','omit','sham')}
    actual_rev={name:read('REV_'+name+'.json.gz')['result']for name in('SAME_LAW','REVERSE')}
    cases=[]
    environments=[{'id':'O2_INITIAL','opportunities':first['task_opportunities'],
                   'initial_action':'external','law':{'native_price':first['environment']['native_price'],'external_price':first['environment']['external_and_help_price'],'missing_artifact_rule':'fixed_deadline5'},
                   'actual':actual_o2,'source_kind':'three matched complete-prefix DEE controls'},
                  *[{'id':condition['label'],'opportunities':rev['opportunities'],
                     'initial_action':'native','law':{'native_price':condition['prices'][0],'external_price':condition['prices'][1],'missing_artifact_rule':'price_plus4'},
                     'actual':{condition['label']:actual_rev[condition['label']]},
                     'source_kind':'continuation from the actual final acquired negative O2 state; no reseed'}for condition in rev['worlds']]]
    for env in environments:
        observations=[]
        for arm,data in env['actual'].items():
            rows=[]
            for row in data['rows']:
                action='native'if row['native_route']==-1 else'external'if row['native_route']in(0,1)else'absent'
                if env['id']=='O2_INITIAL':cost=row['modelled_price']
                else:cost=row['actual_modelled_cost']
                price=env['law']['native_price']if action=='native'else env['law']['external_price']
                calculated=(price if row['completed']else 5)if env['law']['missing_artifact_rule']=='fixed_deadline5'else price+(0 if row['completed']else 4)
                if calculated!=cost:issues.append(env['id']+':actual_cost_law')
                # OFFLINE scoring. These operands/expected values never enter choose().
                correct=row['numeric_result']==row['operands'][0]+row['operands'][1]
                rows.append({'opportunity':row['opportunity'],'actual_native_emission':row['native_route'],'actual_action':action,
                             'actual_numeric':row['numeric_result'],'offline_numeric_correct':correct,
                             'actual_artifact_produced':row['completed'],'actual_modelled_cost':cost})
            observations.append({'arm':arm,'rows':rows,'total_actual_modelled_cost':sum(x['actual_modelled_cost']for x in rows)})
        refs=[];count=len(env['opportunities'])
        for policy in POLICIES:
            conditional=run(policy,env['law'],env['initial_action'],[True]*count)
            alternatives=[run(policy,env['law'],env['initial_action'],list(pattern))for pattern in itertools.product((False,True),repeat=count)]
            refs.append({'policy':policy,'classification':'ANALYTICAL_COUNTERFACTUAL_NOT_EXECUTED_NO_DEE_CONTROLLER',
                         'all_actions_complete_conditional_trace':conditional,
                         'all_completion_patterns_count':len(alternatives),
                         'modelled_cost_bounds_over_binary_completion_assumptions':{'min':min(x['total_modelled_cost']for x in alternatives),'max':max(x['total_modelled_cost']for x in alternatives)},
                         'all_completion_patterns':alternatives,
                         'numeric_correctness':'INDETERMINATE: corresponding counterfactual DEE histories were not executed',
                         'utility_comparison_scope':'Conditional published task price only; no CPU, energy, real elapsed time, phase/retention, tool availability or cognitive superiority inferred.'})
        cases.append({'id':env['id'],'public_opportunities':env['opportunities'],'published_environmental_law':env['law'],
                      'initial_reference_action':env['initial_action'],
                      'initialization_scope':'Reference initial action matches the first observed route of this existing prefix, not selected using which route is cheaper; policy carries no hidden law or answer.',
                      'actual_observations':observations,'analytical_references':refs})
    tests=unit_tests()
    if any(not t['equal']for t in tests):issues.append('Policy unit test')
    return {'schema':'APD01.auditor_only_causal_policy_references.v1','native_ticks':0,'new_DEE_runs':0,
            'controller_used_on_MAIN':False,'policy_inputs':['policy_id','previous_action','previous_own_observed_cost','initial_action'],'policy_fixed_budget':BUDGET,
            'effective_information_used':'Only previous own action and whether its post-action cost exceeded2. The native apparatus conveyed excess by material presence at S2 and absence below threshold; the external reference receives that bit directly as an idealized auditor algorithm. Physical decoding, calendars and memory costs are NOT matched.',
            'cases':cases,'unit_tests':tests,'sources':sources,'issues':issues,
            'interpretation':'An ordinary external cost-responsive rule is an analytical reference, never a DEE capacity. Its next action is computed only after its preceding hypothetical action receives an environmental cost. Fixed price laws belong to the auditor environment, not policy information. Full binary completion branches bound assumptions, not actual DEE-reachable states or confidence intervals. Counterfactual numerical correctness and internal dynamics remain unmeasured.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--evidencia',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
    if a.salida.exists():raise FileExistsError('Preserve earlier policy calculation')
    r=calculate(a.evidencia);a.salida.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'native_ticks':0,'issues':r['issues'],'tests':len(r['unit_tests']),
                      'cases':[{'id':c['id'],'actual':[x['total_actual_modelled_cost']for x in c['actual_observations']],
                                'conditional_reference_costs':{x['policy']:x['all_actions_complete_conditional_trace']['total_modelled_cost']for x in c['analytical_references']}}for c in r['cases']]}))
    raise SystemExit(bool(r['issues']))
