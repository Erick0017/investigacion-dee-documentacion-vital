"""Make a precise unified diff only; NEVER edit or import the actual system."""
import difflib,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SYSTEM=ROOT/'sistema'
def main():
    rows=[];diff=[]
    changes={
        'app/access_guard.py':[("Pythonopen/subprocess/network audit hooks; an optional exact declared environment-worker argv does not authorize other processes or networks. Not an operating-system sandbox",
            'Python open/subprocess/network audit hooks. Reads inside sistema, including operational life records, journals and cached results in estado, remain permitted except explicit exclusions; declared exact external inputs are permitted. Undeclared sibling laboratorio/evidencia and other external reads are blocked. An optional exact environment-worker argv does not authorize other processes or networks. This does not detect all response-history lookups and is not an operating-system sandbox.')],
        'app/servicio_persistente.py':[("'no_lab_evidence_or_history_reads_allowed':True,'scope':self.guard['scope']}",
            "'no_lab_evidence_or_history_reads_allowed':False,'legacy_combined_flag_deprecated_no_universal_history_guarantee':True,'no_undeclared_external_lab_or_evidence_reads_allowed':True,'operational_history_reads_universally_blocked':False,'scope':self.guard['scope']}")],
        'gestionar.py':[("'no_lab_evidence_or_history_reads_allowed':True,'scope':guard['scope']}",
            "'no_lab_evidence_or_history_reads_allowed':False,'legacy_combined_flag_deprecated_no_universal_history_guarantee':True,'no_undeclared_external_lab_or_evidence_reads_allowed':True,'operational_history_reads_universally_blocked':False,'scope':guard['scope']}")]}
    for relative,replacements in changes.items():
        p=SYSTEM/relative;old=p.read_text(encoding='utf-8-sig');new=old
        for before,after in replacements:
            if new.count(before)!=1:raise ValueError('Exact reviewed descriptor changed: '+relative)
            new=new.replace(before,after)
        diff.extend(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='a/sistema/'+relative,tofile='b/sistema/'+relative))
        rows.append({'relative_SYSTEM':relative,'original_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
            'permission_logic_modified':False,'physical_fields_or_tick_modified':False})
    patch=''.join(diff).encode('utf8')
    with(HERE/'PROPUESTA_METADATA_PERIMETRO_NO_APLICADA.patch').open('xb')as f:f.write(patch)
    value={'status':'PROPOSAL_NOT_APPLIED','native_ticks':0,'files':rows,'patch_sha256':hashlib.sha256(patch).hexdigest(),
        'warning':'Historical primaries retain original tags. Consumers of the deprecated combined claim need a metadata-only test update after the live source freeze ends.'}
    with(HERE/'IDENTIDAD_PROPUESTA_PERIMETRO.json').open('xb')as f:f.write((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(value))
if __name__=='__main__':main()
