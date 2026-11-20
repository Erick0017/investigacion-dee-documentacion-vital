"""Inventory exact execution-source hashes; never invent an unavailable cut."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[4]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    expected={};current={};files=list((ROOT/'laboratorio/campanas/CONSOLIDACION_1_1').rglob('*.py'))+list((ROOT/'sistema/capacidades').glob('*.py'))
    for p in files:
        if'node_modules'in p.parts:continue
        current[sha(p.read_bytes())]=p
    for p in(ROOT/'evidencia').rglob('MEDICIONES.json'):
        d=json.loads(p.read_bytes())
        for key in('runner_sha256','bridge_source_sha256'):
            value=d.get(key)
            if value:expected.setdefault(value,[]).append({'record':p.relative_to(ROOT).as_posix(),'field':key})
    out=ROOT/'evidencia/genealogia/CODIGO_VERSIONADO';out.mkdir(parents=True,exist_ok=True);rows=[];unmatched=set(expected)-set(current)
    recovered={}
    for p in files:
        if not unmatched:break
        if'node_modules'in p.parts:continue
        h=hashlib.sha256();prefix=b''
        for line in p.read_bytes().splitlines(keepends=True):
            h.update(line);prefix+=line;value=h.hexdigest()
            if value in unmatched:
                target=out/(value+'.py');target.write_bytes(prefix);recovered[value]=target;unmatched.remove(value)
    # Reverse only declared additive interface changes. A candidate is accepted
    # solely when its complete bytes match an execution-time recorded SHA256.
    candidates=[]
    bridge=ROOT/'sistema/capacidades/puente_adquirible.py';content=bridge.read_bytes();prefix=content.split(b'\ndef read_transformed(',1)[0].replace(b'from dee_thinking.consolidated import exact_observation\n',b'')
    candidates += [prefix.rstrip(b'\n')+ending for ending in(b'',b'\n',b'\n\n')]
    runner=ROOT/'laboratorio/campanas/CONSOLIDACION_1_1/continuidad_funcional.py';content=runner.read_text(encoding='utf8');prior=content.replace("case.get('actual_new_form_events',plan['actual_new_form_events'])","plan['actual_new_form_events']").replace(",cue=case.get('cue',plan.get('new_cue_load',5)),teacher=case.get('teacher',plan.get('new_teacher_load',11))",'');candidates.append(prior.encode('utf8'))
    for candidate in candidates:
        value=sha(candidate)
        if value in unmatched:
            target=out/(value+'.py');target.write_bytes(candidate);recovered[value]=target;unmatched.remove(value)
    for value,refs in expected.items():
        source=current.get(value)or recovered.get(value)
        if source is not None:
            target=out/(value+'.py')
            if not target.exists():target.write_bytes(source.read_bytes())
        rows.append({'sha256_recorded_before_execution':value,'records':refs,'exact_source_available':source is not None,'source':(out/(value+'.py')).relative_to(ROOT).as_posix()if source is not None else None,'recovery_method':'CURRENT_FILE_EXACT_BYTES'if value in current else'COMPLETE_BYTES_MATCH_EXECUTION_HASH_AFTER_REVERSING_KNOWN_ADDITIVE_CHANGE_OR_PREFIX'if value in recovered else'EARLIER_BYTE_CUT_NOT_FOUND_CURRENT_ADAPTED_RUNNER_RETAINED','effect_if_missing':'Original native measurements and plans remain primary. The current executable runner can reproduce its stated protocol but is not falsely identified as the absent original byte cut.'if source is None else None})
    report={'schema':'DCS1.1.experimental_source_versions.v1','execution_source_hashes':len(rows),'exact_available':sum(x['exact_source_available']for x in rows),'missing_earlier_cuts':sum(not x['exact_source_available']for x in rows),'rows':rows,'scope':'New campaign runner versions only. Does not replace the separately hash-preserved CPC1–9 historical source registry or current installed-system manifest.'}
    (ROOT/'evidencia/genealogia/VERSIONES_RUNNERS_1_1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'hashes':len(rows),'exact_available':report['exact_available'],'earlier_cuts_missing':report['missing_earlier_cuts']}))
if __name__=='__main__':main()
