"""One LAB-only ACT_R03 proposal; R01/R02 scoring is not retroactively changed.

No Native imports/ticks. Quality is a posteffect environmental contract, not an
actor policy. The current REAL reserve keeps its installed R02 sources intact.
"""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import importlib.util
import json
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
LAB=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
BASE=LAB/'revisiones/ACTUADOR_R02_AUX_R01_EJECUTADO/sistema'
OUT=HERE/'PROPUESTA_ACTUADOR_R03_R01'
QUALITY='APD04.posteffect_quality.relevant_gain_or_irrelevant_formed_wait.R03.v1'


def write(path,value):
    with path.open('x',encoding='utf8')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def digest(path):return{'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def main():
    if OUT.exists():raise FileExistsError('Proposal frozen; no silent overwrite')
    OUT.mkdir();members=[];patches=[]
    def propose(relative,replacements):
        source=BASE/relative;base=OUT/'FUENTES_BASE'/relative;base.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,base)
        before=source.read_text(encoding='utf8');after=before
        for old,new in replacements:
            if after.count(old)!=1:raise ValueError('Exact ACT_R02 source base differs: '+relative+' / '+old[:70])
            after=after.replace(old,new)
        ast.parse(after);target=OUT/'sistema'/relative;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('x',encoding='utf8',newline='\n')as stream:stream.write(after)
        members.append({'file':'sistema/'+relative,'base':digest(base),'proposed':digest(target)})
        patches.append(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='sistema/'+relative,tofile='sistema/'+relative)))
    propose('app/protocolo_apd04.py',[
        ("row['version']not in('R01','R02')", "row['version']not in('R01','R02','R03')"),
        ("Codec P0 fijo R01/R02; no decision por caso", "Codec P0 fijo R01/R02/R03; no decision por caso"),
    ])
    helpers='''def task_env_signature(m):
    """Exact environmental objects/loads audit copy, never an actor input."""
    return json.loads(json.dumps({'objects':m['objects'],'loads':m['loads']},sort_keys=True,separators=(',',':')))


def formed_native_choice(sign,reader):
    candidates=reader.get('candidates',[])
    return type(sign)is int and sign in(-1,0,1) and reader.get('choice')==sign and len(candidates)==1 and candidates[0].get('choice')==sign


def posteffect_quality_r03(sign,action,reader,old_gain,tag,goal,before,after,actuator):
    """Postemission environment score. No strategy/content is returned to Native."""
    formed=formed_native_choice(sign,reader)
    if actuator!='closed':
        return {'contract':QUALITY_R03,'status':'out_of_domain','old_work_gain':bool(old_gain),'new_quality':None,
            'actuator':actuator,'no_feedback_category_is_defined':True}
    quality=False
    if formed:
        if action=='WAIT':quality=sign==0 and tag!=goal and before==after
        elif action in('INSPECT','USE'):quality=bool(old_gain)
    return {'contract':QUALITY_R03,'status':'in_domain','old_work_gain':bool(old_gain),'new_quality':quality,
        'formed_unique':formed,'formed_native_sign':sign,'transduced_action':action,'actuator':actuator,
        'tag_auditor_after_effect':tag,'goal_auditor_after_effect':goal,
        'task_env_before':before,'task_env_after':after,'task_env_unchanged':before==after,
        'not_an_actor_input':True,'SUCCESS_adds_no_new_positive_reinforcement_port':True}


'''
    old_config='''    m=get(a);before=m.get('action_codec','R01');version=row['version']
    if version not in ACTION_CODECS:raise ValueError('Codec fijo R01/R02')
    m['action_codec']=version;save(a,m)
    return {'kind':'explicit_prepared_actuator_codec','before':before,'after':version,
       'fixed_signed_map':dict(ACTION_CODECS[version]),'new_native_ticks_in_operation':0,
       'scope':'External transduction preparation only. No RAW, clock, source cache, world reset, target or learned-policy edit.'}
'''
    new_config='''    m=get(a);before=m.get('action_codec','R01');version=row['version']
    if version not in ACTION_CODECS:raise ValueError('Codec fijo R01/R02/R03')
    m['action_codec']=version
    if version=='R03':
        m['quality_contract']=QUALITY_R03;m['counters'].setdefault('wait',0);m['counters'].setdefault('quality_success',0)
    else:m.pop('quality_contract',None)
    save(a,m)
    result={'kind':'explicit_prepared_actuator_codec','before':before,'after':version,
       'fixed_signed_map':dict(ACTION_CODECS[version]),'new_native_ticks_in_operation':0,
       'scope':'External transduction preparation only. No RAW, clock, source cache, world reset, target or learned-policy edit.'}
    if version=='R03':result.update(quality_contract=QUALITY_R03,quality_domain_actuator='closed',old_work_gain_still_separate=True)
    return result
'''
    propose('capacidades/ecosistema_apd04.py',[
        ("'R02':{-1:'INSPECT',0:'INSPECT',1:'USE'}}", "'R02':{-1:'INSPECT',0:'INSPECT',1:'USE'},\n               'R03':{-1:'INSPECT',0:'WAIT',1:'USE'}}"),
        ("TOOL_CODEC={1:'clasifica',-1:'equilibra'}", "TOOL_CODEC={1:'clasifica',-1:'equilibra'}\nQUALITY_R03='"+QUALITY+"'"),
        ("    return m\n\ndef validate", "    if m.get('action_codec','R01')=='R03'and m.get('quality_contract')!=QUALITY_R03:raise ValueError('Contrato posteffect R03 ausente o distinto; no reparar')\n    return m\n\ndef validate"),
        ("    m=get(a);return {'version':VERSION", "    m=get(a);result={'version':VERSION"),
        ("       'memory_scope':'Cache and cursor belong to simulated environment. Not Native retained numbers or autonomous source-address learning.'}\n\ndef configure_actuator", "       'memory_scope':'Cache and cursor belong to simulated environment. Not Native retained numbers or autonomous source-address learning.'}\n    if m.get('action_codec','R01')=='R03':result.update(quality_contract=QUALITY_R03,quality_domain_actuator='closed')\n    return result\n\ndef configure_actuator"),
        (old_config,new_config),
        ("def change(a,row):",helpers+"def change(a,row):"),
        ("    m=get(a);codec_version=m.get('action_codec','R01');action_codec=ACTION_CODECS[codec_version]\n    before=physical", "    m=get(a);codec_version=m.get('action_codec','R01');action_codec=ACTION_CODECS[codec_version]\n    if codec_version=='R03'and actuator!='closed':return {'kind':'APD04_R03_quality_out_of_domain','out_of_domain':True,'rows':[],'new_native_ticks_in_operation':0,'actuator':actuator,'no_feedback_or_native_answer_substituted':True}\n    before=physical"),
        ("        m['episode']+=1;ep=m['episode'];obj=m['objects'][m['cursor']]", "        m['episode']+=1;ep=m['episode'];obj=m['objects'][m['cursor']]\n        task_before=task_env_signature(m)if codec_version=='R03'else None;quality_witness=None"),
        (";sign=selected['physical_choice'];action=action_codec.get(sign)", ";sign=selected['physical_choice'];actuator_sign=sign if codec_version!='R03'or formed_native_choice(sign,selected['reader'])else None;action=action_codec.get(actuator_sign)"),
        ("'useful':False,'valid_native':sign is not None}", "'useful':False,'valid_native':actuator_sign is not None}"),
        ("        elif action=='INSPECT':", "        elif action=='WAIT':\n            m['counters']['wait']+=1;effect['reason']='formed_zero_WAIT_no_task_environment_change'\n        elif action=='INSPECT':"),
        ("        category='SUCCESS'if effect['useful']else'FAILURE'", "        feedback_success=effect['useful']\n        if codec_version=='R03':\n            quality_witness=posteffect_quality_r03(sign,action,selected['reader'],effect['useful'],obj['tag'],m['goal_tag'],task_before,task_env_signature(m),actuator)\n            effect.update(old_work_gain=effect['useful'],new_quality=quality_witness['new_quality'],quality_contract=QUALITY_R03)\n            feedback_success=quality_witness['new_quality']\n            if feedback_success:m['counters']['quality_success']+=1\n        category='SUCCESS'if feedback_success else'FAILURE'"),
        ("        rows.append({'episode':ep", "        result_row={'episode':ep"),
        ("'cursor_rule':'Prepared circular view after any opportunity; Native decides INSPECT/USE, not an arbitrary numeric source address'})", "'cursor_rule':'Prepared circular view after any opportunity; Native decides INSPECT/USE, not an arbitrary numeric source address'}\n        if quality_witness is not None:result_row['posteffect_quality']=quality_witness\n        rows.append(result_row)"),
    ])
    propose('app/usar_dee.py',[
        ('eco_actuator.add_argument("version", choices=("R01", "R02"))','eco_actuator.add_argument("version", choices=("R01", "R02", "R03"))'),
    ])
    with(OUT/'PARCHE_PROPUESTO.diff').open('x',encoding='utf8',newline='\n')as stream:stream.write(''.join(patches))
    # Execute only isolated pure host-quality helpers, never a DEE Runtime.
    tree=ast.parse((OUT/'sistema/capacidades/ecosistema_apd04.py').read_text(encoding='utf8'))
    selected=[node for node in tree.body if isinstance(node,ast.FunctionDef)and node.name in('task_env_signature','formed_native_choice','posteffect_quality_r03')]
    namespace={'json':json,'QUALITY_R03':QUALITY};exec(compile(ast.Module(body=selected,type_ignores=[]),'<pure-environment-quality-only>','exec'),namespace)
    evaluate=namespace['posteffect_quality_r03'];signature=namespace['task_env_signature']
    before=signature({'objects':[{'id':0,'tag':0,'value':16,'version':2,'observed':{'value':18,'version':1},'bin':1}], 'loads':[7,3]})
    def reader(sign):return{'choice':sign,'candidates':[{'choice':sign}]}
    test_rows=[]
    cases=[
        ('formed_zero_irrelevant_WAIT',0,'WAIT',reader(0),False,1,0,before,before,'closed',True),
        ('formed_zero_relevant_WAIT',0,'WAIT',reader(0),False,0,0,before,before,'closed',False),
        ('NULL_not_WAIT',None,None,{'choice':None,'candidates':[]},False,1,0,before,before,'closed',False),
        ('mismatched_NULL_called_WAIT',None,'WAIT',{'choice':None,'candidates':[]},False,1,0,before,before,'closed',False),
        ('ambiguous_zero_not_WAIT',0,'WAIT',{'choice':None,'candidates':[{'choice':0},{'choice':1}]},False,1,0,before,before,'closed',False),
        ('useful_USE',1,'USE',reader(1),True,0,0,before,before,'closed',True),
        ('correct_but_repeated_USE',1,'USE',reader(1),False,0,0,before,before,'closed',False),
        ('useful_INSPECT',-1,'INSPECT',reader(-1),True,0,0,before,before,'closed',True),
        ('nulled_WAIT_out_of_domain',0,'WAIT',reader(0),False,1,0,before,before,'nulled',None),
    ]
    for field in('observed','bin','loads'):
        after=copy.deepcopy(before)
        if field=='observed':after['objects'][0]['observed']={'value':99,'version':1}
        elif field=='bin':after['objects'][0]['bin']=-1
        else:after['loads']=[6,4]
        cases.append(('WAIT_changed_'+field,0,'WAIT',reader(0),False,1,0,before,after,'closed',False))
    for name,sign,action,r,old,tag,goal,pre,post,actuator,expected in cases:
        result=evaluate(sign,action,r,old,tag,goal,pre,post,actuator)
        assert result['new_quality']is expected,name
        test_rows.append({'name':name,'result':result,'expected_new_quality':expected})
    assert namespace['formed_native_choice'](None,{'choice':None,'candidates':[]})is False
    assert namespace['formed_native_choice'](0,reader(0))is True
    assert namespace['formed_native_choice'](False,reader(0))is False
    metadata=copy.deepcopy(before);metadata.update(cursor=4,episode=99,counters={'wait':3},diary='audit')
    assert signature(metadata)==before
    old_cli=load('R02_fixed_cli_only',BASE/'app/usar_dee.py');new_cli=load('R03_fixed_cli_only',OUT/'sistema/app/usar_dee.py')
    protocol=load('R03_literal_validator_only',OUT/'sistema/app/protocolo_apd04.py')
    legacy=read_legacy=[]
    old_tests=json.loads((HERE/'PROPUESTA_ACTUADOR_R02_R01/PRUEBAS_N0.json').read_bytes())
    for sample in old_tests['legacy17']:
        argv=sample['argv'];aa=old_cli.command_parser().parse_args(argv);bb=new_cli.command_parser().parse_args(argv)
        assert vars(aa)==vars(bb)and old_cli.literal_rows(aa)==new_cli.literal_rows(bb)
        legacy.append(argv)
    for version in('R01','R02','R03'):
        parsed=new_cli.command_parser().parse_args(['configurar-actuador-ecosistema',version])
        row=new_cli.literal_rows(parsed)[0];protocol.validate_literal(row)
        assert row=={'modo':'apd04-actuador','version':version}
    negatives=[{'modo':'apd04-actuador','version':'R04'},
        {'modo':'apd04-actuador','version':'R03','goal':0},
        {'modo':'apd04-actuador','version':'R03','target':1},
        {'modo':'apd04-actuador','version':'R03','quality_contract':'favorable'},
        {'modo':'apd04-vivir','oportunidades':1,'action_codec':'R03'}]
    for row in negatives:
        try:protocol.validate_literal(row)
        except ValueError:continue
        raise AssertionError('Forbidden free policy/target configuration accepted')
    # The old maps and the NULL transduction stay exactly unchanged.
    maps=next(node for node in tree.body if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ACTION_CODECS'for t in node.targets))
    codecs=ast.literal_eval(maps.value)
    assert codecs['R01']=={-1:'USE',0:'INSPECT',1:'INSPECT'}and codecs['R02']=={-1:'INSPECT',0:'INSPECT',1:'USE'}
    assert codecs['R03']=={-1:'INSPECT',0:'WAIT',1:'USE'}and all(m.get(None)is None for m in codecs.values())
    write(OUT/'PRUEBAS_P0_N0.json',{'schema':'APD04.ACT_R03.proposal.software_only.N0.v1',
        'quality_contract':QUALITY,'pure_quality_tests':test_rows,'legacy17_unchanged':legacy,
        'fixed_codecs':codecs,'forbidden_literals_rejected':negatives,
        'state_semantic_uint64_layout':'state low32; semantic high4; actual signed direction nibbles48/52/56',
        'new_native_ticks':0,'Runtime_created':False,'physical_noninterference_not_tested':True,
        'scope':'Host transduction/quality logic only. Not a Native learning result, new policy or incorporation.'})
    write(OUT/'MANIFIESTO_PROPUESTA_N0.json',{'schema':'APD04.ACT_R03.single_proposal.N0.r01','members':members,
        'quality_contract':QUALITY,'Native_ticks':0,'Runtime_created':False,'shared_sistema_modified':False,
        'old_versions':'R01/R02 maps and old gain/feedback branches preserved; new quality activates only with explicit R03 metadata.'})
    print(json.dumps({'folder':str(OUT),'members':members,'pure_tests':len(test_rows),'legacy17':len(legacy),'Native_ticks':0},indent=2))


if __name__=='__main__':main()
