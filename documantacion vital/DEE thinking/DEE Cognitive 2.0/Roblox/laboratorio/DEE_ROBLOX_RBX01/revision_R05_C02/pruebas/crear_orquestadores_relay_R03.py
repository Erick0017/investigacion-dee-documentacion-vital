"""Declared transport-only revisions. Does not import/run either orchestrator."""
from pathlib import Path
import ast,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for oldname,newname,oldline,newline in[
 ('orquestar_C02_R03.py','orquestar_C02_R04.py',
  "'--stop-file', str(relay_stop)], cwd=ROOT",
  "'--stop-file', str(relay_stop)]+(['--resume-boundary',str(output/'WORLD_RESTORED_BEFORE_NATIVE.json')]if args.world_checkpoint else []), cwd=ROOT"),
 ('orquestar_comparador_C02_R02.py','orquestar_comparador_C02_R03.py',
  "'--expected-place',args.expected_place],cwd=ROOT",
  "'--expected-place',args.expected_place]+(['--resume-boundary',str(output/'WORLD_RESTORED_BEFORE_POLICY.json')]if args.world_checkpoint else []),cwd=ROOT")]:
 a=ROOT/'control'/oldname;b=ROOT/'control'/newname
 assert not b.exists(),'New revisions only'
 t=a.read_text('utf8');oldsha=hashlib.sha256(a.read_bytes()).hexdigest()
 assert t.count(oldline)==1,(oldname,oldline)
 changed=t.replace(oldline,newline).replace('control/studio_mailbox_relay_C02_R02.py','control/studio_mailbox_relay_C02_R03.py')
 ast.parse(changed)
 assert 'WORLD_RESTORED_BEFORE_'in changed and 'if args.world_checkpoint else []'in changed
 b.write_text(changed,encoding='utf8',newline='')
 assert hashlib.sha256(a.read_bytes()).hexdigest()==oldsha
 rows.append(dict(source=str(a.relative_to(ROOT)),source_sha256=oldsha,source_unchanged=True,
                  new=str(b.relative_to(ROOT)),sha256=hashlib.sha256(b.read_bytes()).hexdigest(),
                  change='RelayR03 and explicit resume witness iff actual --world-checkpoint supplied'))
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
report=dict(schema='DEE.RBX01.C02.explicit_resume_transport_revision.R03',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            files=rows,Native_actions=0,MCP_calls=0,policy_decisions=0,model_calls=0,
            scope='Permission resumeAllowed never implies a requested restore; no policy/body/Native source changes')
out=ROOT/'pruebas'/('ORQUESTADORES_RELAY_EXPLICITO_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))
