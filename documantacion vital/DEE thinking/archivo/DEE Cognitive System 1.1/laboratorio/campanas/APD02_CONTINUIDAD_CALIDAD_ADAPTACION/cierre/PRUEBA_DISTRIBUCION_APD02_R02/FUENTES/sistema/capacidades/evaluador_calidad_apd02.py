"""Post-commit quality evaluation, never an action/route policy.

This evaluator privately knows the original requested operation. Its reference
arithmetic is external evaluation, not DEE computation. Only feedback.category
may be transduced to the participant; no number, operator or route correction
is in that object. This is constrained file validation, not an OS sandbox.
"""
from pathlib import Path,PurePosixPath
import hashlib,json,math,os,re,stat,time

ARTIFACT_SCHEMA='DEE.APD02.calculation_artifact.v1'
REPORT_SCHEMA='DEE.APD02.post_commit_quality.v1'
CATEGORIES=('SUCCESS','SAFETY_ERROR','FILESYSTEM_ERROR','ARTIFACT_ERROR','SEMANTIC_ERROR','NUMERIC_ERROR','RESOURCE_LIMIT','ABSTENTION','NO_RESPONSE','EXECUTION_ERROR')
CATEGORY_CODES={name:i for i,name in enumerate(CATEGORIES)}
TERMINAL_STATES={'committed','failed','abstained','no_output'}
OPERATIONS={'add','sub'}
PROCEDURES={'native','external'}
_PRIVATE_LITERAL_REFERENCE={'suma':'add','diferencia':'sub','agrega':'add','resta':'sub','total':'add','quita':'sub'}
TOKEN=re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_.-]{0,95}$')

class UncommittedActionError(ValueError):pass
class UnsafeArtifactError(ValueError):pass

def _integer(value,low,high):return type(value)is int and low<=value<=high
def _finite_nonnegative(value):return type(value)in(int,float)and math.isfinite(value)and value>=0
def _duplicates_rejected(pairs):
    out={}
    for key,value in pairs:
        if key in out:raise ValueError('Duplicate JSON field')
        out[key]=value
    return out
def _constant_rejected(value):raise ValueError('Nonfinite JSON number')
def _reference(operation,operands):
    left,right=operands
    return left+right if operation=='add'else left-right

def validate_request(request,policy):
    if not isinstance(request,dict)or set(request)!={'task_id','text','operands','required_operation'}:raise ValueError('Exact private original-request fields required')
    if not isinstance(request['task_id'],str)or not TOKEN.fullmatch(request['task_id']):raise ValueError('Bounded task identity required')
    if not isinstance(request['text'],str)or not 1<=len(request['text'])<=96:raise ValueError('Bounded original literal required')
    if request['required_operation']not in OPERATIONS:raise ValueError('Evaluator domain is add/sub, not a free semantic parser')
    if not isinstance(request['operands'],list)or len(request['operands'])!=2 or any(not _integer(v,0,policy['max_operand'])for v in request['operands']):raise ValueError('Two original integer operands in the declared domain required')
    return True

def validate_policy(policy):
    required={'max_operand','max_artifact_bytes','max_price','max_delay_ticks','resource_limits_required_for_success'}
    if not isinstance(policy,dict)or set(policy)!=required:raise ValueError('Exact predeclared quality-policy fields required')
    if not _integer(policy['max_operand'],0,4096)or not _integer(policy['max_artifact_bytes'],1,1048576):raise ValueError('Bounded operand/file policy required')
    for key in('max_price','max_delay_ticks'):
        if policy[key]is not None and not _finite_nonnegative(policy[key]):raise ValueError('Nonnegative resource limits or None required')
    if type(policy['resource_limits_required_for_success'])is not bool:raise ValueError('Explicit resource-limit interpretation required')
    return True

def _safe_path(root,relative):
    if not isinstance(relative,str)or not relative or '\\'in relative or ':'in relative:raise UnsafeArtifactError('Artifact needs a relative forward-slash path without ADS or drive prefix')
    path=PurePosixPath(relative)
    if path.is_absolute()or any(p in('','.', '..')for p in path.parts)or path.as_posix()!=relative:raise UnsafeArtifactError('Normalized relative artifact path required')
    reserved={'CON','PRN','AUX','NUL',*(f'COM{i}'for i in range(1,10)),*(f'LPT{i}'for i in range(1,10))}
    for part in path.parts:
        if len(part)>128 or part.endswith((' ','.'))or part.split('.')[0].upper()in reserved or not re.fullmatch(r'[A-Za-z0-9_.-]+',part):raise UnsafeArtifactError('Unsafe or nonportable artifact component')
    current=root
    for part in path.parts:
        current=current/part
        try:s=current.lstat()
        except FileNotFoundError:continue
        if stat.S_ISLNK(s.st_mode)or getattr(s,'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',1024):raise UnsafeArtifactError('Symlink/reparse artifacts are outside the admitted executor contract')
    if not current.resolve(strict=False).is_relative_to(root):raise UnsafeArtifactError('Artifact escaped the permitted root')
    return current

def _read_artifact(root,receipt,max_bytes):
    if not isinstance(receipt,dict)or set(receipt)!={'relative_path','bytes','sha256'}:raise ValueError('Exact committed artifact receipt required')
    path=_safe_path(root,receipt['relative_path'])
    before=path.stat()
    if not stat.S_ISREG(before.st_mode):raise UnsafeArtifactError('Only regular synthetic files are admitted')
    if before.st_size>max_bytes:raise ValueError('Artifact exceeds its declared size limit')
    with path.open('rb')as stream:
        opened=os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode)or (before.st_ino,before.st_dev)!=(opened.st_ino,opened.st_dev):raise UnsafeArtifactError('Artifact identity changed before its read')
        data=stream.read(max_bytes+1)
        after=os.fstat(stream.fileno())
    if len(data)>max_bytes or (opened.st_size,opened.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise UnsafeArtifactError('Artifact changed during its bounded read')
    final=path.lstat()
    if (final.st_ino,final.st_dev)!=(opened.st_ino,opened.st_dev):raise UnsafeArtifactError('Artifact was replaced before read-back completed')
    if not path.resolve(strict=True).is_relative_to(root):raise UnsafeArtifactError('Artifact path changed outside the admitted root')
    digest=hashlib.sha256(data).hexdigest()
    receipt_matches=type(receipt['bytes'])is int and receipt['bytes']==len(data)and receipt['sha256']==digest
    body=json.loads(data.decode('utf8'),object_pairs_hook=_duplicates_rejected,parse_constant=_constant_rejected)
    if not isinstance(body,dict)or set(body)!={'schema','task_id','operation','operands','value','procedure'}:raise ValueError('Exact calculation-artifact JSON fields required')
    if body['schema']!=ARTIFACT_SCHEMA or body['operation']not in OPERATIONS or body['procedure']not in PROCEDURES or type(body['value'])is not int:raise ValueError('Calculation artifact schema/domain invalid')
    if not isinstance(body['operands'],list)or len(body['operands'])!=2 or any(type(v)is not int for v in body['operands']):raise ValueError('Artifact operands must be exact integers, not bool')
    return body,{'relative_path':receipt['relative_path'],'bytes_read':len(data),'sha256':digest,'receipt_matches_actual_bytes':receipt_matches}

def actor_feedback(report,*,binary=False):
    """The sole permitted return projection. No private reference is copied."""
    category=report['feedback']['category']
    if category not in CATEGORIES:raise ValueError('Unknown consequence class')
    return {'category':('SUCCESS'if category=='SUCCESS'else'FAILURE')if binary else category}

def evaluate_literal_committed(public_request,committed,*,sandbox_root,policy):
    """Conventional six-form reference resolved only AFTER a terminal effect.

    This private evaluator lookup never participates in the lexical codec,
    native selector or action execution. The explicit-request API remains for
    opposite-teaching and other auditor controls.
    """
    if not isinstance(committed,dict)or committed.get('state')not in TERMINAL_STATES:raise UncommittedActionError('Terminal effect required before resolving an evaluator-private literal reference')
    if not isinstance(public_request,dict)or set(public_request)!={'task_id','text','operands'}:raise ValueError('The transport/public request must not carry an evaluator operation or answer')
    operation=_PRIVATE_LITERAL_REFERENCE.get(public_request['text'])
    if operation is None:raise ValueError('Literal outside the fixed conventional evaluator domain; no inferred meaning or corrective answer')
    report=evaluate_committed({**public_request,'required_operation':operation},committed,sandbox_root=sandbox_root,policy=policy)
    report['private_audit']['reference_origin']='Conventional six-form evaluator table, resolved only after the action terminal record; never sent to an actor or used to choose its operation.'
    return report

def evaluate_committed(request,committed,*,sandbox_root,policy):
    """Evaluate one already committed effect without choosing or retrying it.

    Private request: task_id,text,operands,required_operation. Committed receipt:
    task_id,state,selected_operation,selected_procedure,artifact,price,delay_ticks;
    optional reported_value/failure_class are diagnostic only. A missing file
    or wrong operator never earns success merely because a cheap route ran.
    """
    started=time.perf_counter();cpu=time.process_time();validate_policy(policy);validate_request(request,policy)
    if not isinstance(committed,dict)or committed.get('state')not in TERMINAL_STATES:raise UncommittedActionError('Do not evaluate pending/processing/uncertain actions or manufacture a retry')
    root=Path(sandbox_root).resolve(strict=True)
    if not root.is_dir():raise ValueError('An existing explicit synthetic-output root is required')
    expected=_reference(request['required_operation'],request['operands'])
    selected_operation=committed.get('selected_operation');selected_procedure=committed.get('selected_procedure');state=committed['state']
    axes={'terminal_action':True,'same_task_identity':committed.get('task_id')==request['task_id'],'operation_corresponds_to_original_request':selected_operation==request['required_operation'],'selected_procedure_admitted':selected_procedure in PROCEDURES,'artifact_present':False,'artifact_valid':False,'filesystem_effect_completed':state=='committed','safety':True,'receipt_matches_actual_bytes':False,'operands_match_original':None,'artifact_matches_committed_action':None,'numeric_correct_for_original_request':None,'price_within_limit':None,'delay_within_limit':None,'resource_fields_valid':False}
    artifact=None;observed=None;error=None
    if state not in('abstained','no_output')and committed.get('artifact')is not None:
        try:
            if isinstance(committed['artifact'],dict)and isinstance(committed['artifact'].get('relative_path'),str):axes['artifact_present']=_safe_path(root,committed['artifact']['relative_path']).is_file()
            observed,artifact=_read_artifact(root,committed['artifact'],policy['max_artifact_bytes']);axes['artifact_present']=True;axes['artifact_valid']=True;axes['receipt_matches_actual_bytes']=artifact['receipt_matches_actual_bytes'];axes['operands_match_original']=observed['operands']==request['operands'];axes['artifact_matches_committed_action']=observed['task_id']==request['task_id']and observed['operation']==selected_operation and observed['procedure']==selected_procedure;axes['numeric_correct_for_original_request']=observed['value']==expected
        except UnsafeArtifactError as exc:axes['safety']=False;error={'class':'unsafe_artifact','detail':str(exc)}
        except (FileNotFoundError,PermissionError,OSError)as exc:error={'class':'filesystem','detail':type(exc).__name__}
        except (ValueError,UnicodeError,TypeError)as exc:error={'class':'invalid_artifact','detail':str(exc)}
    elif state not in('abstained','no_output'):error={'class':'filesystem','detail':'No committed artifact receipt'}
    price=committed.get('price');delay=committed.get('delay_ticks');axes['resource_fields_valid']=_finite_nonnegative(price)and type(delay)is int and delay>=0
    if axes['resource_fields_valid']:
        axes['price_within_limit']=policy['max_price']is None or price<=policy['max_price'];axes['delay_within_limit']=policy['max_delay_ticks']is None or delay<=policy['max_delay_ticks']
    valid=all(axes[k]is True for k in('same_task_identity','operation_corresponds_to_original_request','selected_procedure_admitted','artifact_present','artifact_valid','filesystem_effect_completed','safety','receipt_matches_actual_bytes','operands_match_original','artifact_matches_committed_action','numeric_correct_for_original_request'))
    resources=axes['resource_fields_valid']and axes['price_within_limit']and axes['delay_within_limit'];success=bool(valid and(resources or not policy['resource_limits_required_for_success']))
    if not axes['safety']:category='SAFETY_ERROR'
    elif state=='abstained':category='ABSTENTION'
    elif state=='no_output'or selected_operation not in OPERATIONS or selected_procedure not in PROCEDURES:category='NO_RESPONSE'
    elif state=='failed'and committed.get('failure_class')not in(None,'PermissionError','OSError','FileNotFoundError','filesystem'):category='EXECUTION_ERROR'
    elif not axes['filesystem_effect_completed']or(error and error['class']=='filesystem'):category='FILESYSTEM_ERROR'
    elif not all(axes[k]is True for k in('artifact_valid','receipt_matches_actual_bytes','same_task_identity','artifact_matches_committed_action','operands_match_original')):category='ARTIFACT_ERROR'
    elif not axes['operation_corresponds_to_original_request']:category='SEMANTIC_ERROR'
    elif not axes['numeric_correct_for_original_request']:category='NUMERIC_ERROR'
    elif not resources and policy['resource_limits_required_for_success']:category='RESOURCE_LIMIT'
    else:category='SUCCESS'
    reported=committed.get('reported_value');reported_correct=(reported==expected)if type(reported)is int else None
    return {'schema':REPORT_SCHEMA,'feedback':{'category':category},'axes':axes,'valid_solution_before_resource_ranking':valid,'resource_acceptable':bool(resources),'task_success':success,'completed_task':bool(valid),'completed_under_declared_limits':success,'private_audit':{'request':{**request,'operands':list(request['operands'])},'selected_operation':selected_operation,'selected_procedure':selected_procedure,'reference_value':expected,'observed_artifact':observed,'artifact_read':artifact,'reported_value':reported,'reported_value_correct_is_not_a_file_effect':reported_correct,'price':price,'delay_ticks':delay,'error':error,'original_terminal_state':state,'failure_class':committed.get('failure_class')},'evaluation_resources':{'external_reference_operations':1,'bytes_read':artifact['bytes_read']if artifact else 0,'host_wall_seconds':time.perf_counter()-started,'host_cpu_seconds':time.process_time()-cpu,'not_DEE_computation':True},'scope':'Post-action external evaluator. Only feedback.category may enter the participant. It does not choose a route, call another procedure, correct a number, learn for DEE or provide an OS sandbox. Deliberate abstention and no response are not completed tasks. Completed valid work and compliance with resource limits remain separate.'}
