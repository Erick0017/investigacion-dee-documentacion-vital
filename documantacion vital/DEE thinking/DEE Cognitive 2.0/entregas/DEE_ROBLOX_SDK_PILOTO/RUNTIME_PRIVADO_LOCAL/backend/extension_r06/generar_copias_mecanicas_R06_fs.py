"""One-shot FS-only extraction. No Native/owner/package imports."""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent;RUNTIME=HERE.parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    actor=RUNTIME/'dependencias/sdk_bundle/rbx07_native_v3.py';text=actor.read_text('utf8')
    parsed=ast.parse(text);names=('HostSafetyStop','BoundedTime','TimedAdapter','normalized_requests')
    functions={node.name:node for node in parsed.body if isinstance(node,(ast.FunctionDef,ast.ClassDef))}
    target=HERE/'sdk_capabilities_R06.py';current=target.read_text('utf8')
    if '\nclass BoundedTime:' in current:raise FileExistsError('Mechanical extraction already present')
    extracted='\n\n'.join(ast.get_source_segment(text,functions[name]) for name in names)+'\n'
    target.write_text(current+'\n'+extracted,encoding='utf8')
    owner=RUNTIME/'backend/r06/sdk_owner.py';copied=HERE/'owner_caps_R06.py'
    if copied.exists():raise FileExistsError(copied)
    data=owner.read_text('utf8')
    data=data.replace("'backend/r06/ledger_sdk.py'","'backend/extension_r06/ledger_caps_R06.py'")
    data=data.replace("json.loads((destination / 'INSTANCE.json').read_text('utf8'))['operationalLease']['hardFinishUtcEpoch']",
                      "json.loads((destination / 'sistema/capacidades/SDK_CAPABILITIES_SCOPE_R06.json').read_text('utf8'))['native_cutoff_utc_epoch']")
    data=data.replace('app/HOST_INTEGRAL_V3.json','app/HOST_SDK_CAPABILITIES_R06.json')
    data=data.replace('app/servicio_eventos_v3.py','app/servicio_capabilities_R06.py')
    copied.write_text(data,encoding='utf8')
    source=RUNTIME/'dependencias/sistema_base/app/servicio_eventos_v3.py';host=HERE/'servicio_capabilities_R06.py'
    if host.exists():raise FileExistsError(host)
    host.write_text(source.read_text('utf8').replace('app/HOST_INTEGRAL_V3.json','app/HOST_SDK_CAPABILITIES_R06.json'),encoding='utf8')
    after=ast.parse(target.read_text('utf8'));actual={n.name:n for n in after.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    for name in names:assert ast.dump(functions[name],include_attributes=False)==ast.dump(actual[name],include_attributes=False)
    value={'schema':'DEE.Roblox.SDK.capabilities.mechanical_sources.R06','NativeOpened':False,
        'originalActor':{'path':str(actor.relative_to(RUNTIME)),'sha256':digest(actor)},
        'exactASTMembers':list(names),'sourceOwnerSha256':digest(owner),'newOwnerSha256':digest(copied),
        'sourceHostSha256':digest(source),'newHostSha256':digest(host),
        'changes':'New ledger/host/scope routing only; actual official owner, cadence, RAM and checkpoints retained.'}
    out=HERE/'ORIGENES_MECANICOS_R06.json'
    with out.open('x',encoding='utf8') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps(value))
if __name__=='__main__':main()
