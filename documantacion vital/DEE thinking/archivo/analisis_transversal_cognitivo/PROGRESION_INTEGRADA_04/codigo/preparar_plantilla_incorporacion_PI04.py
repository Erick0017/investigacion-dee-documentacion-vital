"""Create an UNEXECUTED gated PI04 adapter from the preserved PI03 contract."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1]

def once(s,a,b):
    if s.count(a)!=1:raise ValueError('Nonunique adaptation locator: '+a[:80])
    return s.replace(a,b,1)

if __name__=='__main__':
    source=P.parent/'PROGRESION_INTEGRADA_03/codigo/incorporar_PI03.py'
    old=source.read_bytes();s=old.decode('utf-8-sig').replace('\r\n','\n')
    # Metadata/report identifiers are new, while the actual inherited life ID
    # remains literally inside its already accepted PI03 transport namespace.
    s=s.replace('PI03','PI04').replace('pi03','pi04')
    s=once(s,"CS=P/'estados/candidato/sistema'","CS=P/'estados/candidato_R02/sistema'")
    s=once(s,"LIFE='ECI02_PI04_MAIN';PARENT='ECI02_PI02_MAIN';PARENT_T=753346",
           "LIFE='ECI02_PI03_REPRO_PI04_MAIN_02';PARENT='ECI02_PI03_MAIN';PARENT_T=775355")
    s=once(s,"PARENT_SHA='17da00843456f1a76faafcbc42cd72b6395753d439e62edd02883d0f7e8d5c88'",
           "PARENT_SHA='5581d3785bf7d7194b5bdb545827aab55f0659d8b3f2c00301425d89616cf07b'")
    s=once(s,"protocol_jsons={'capacidades/PROTOCOLO_PI04_R01.json','capacidades/PROTOCOLO_PI04_TAREA_R02.json'}",
           "protocol_jsons={'capacidades/PROTOCOLO_PI03_R01.json','capacidades/PROTOCOLO_PI03_TAREA_R02.json','capacidades/PROTOCOLO_PI04_C2_R01.json','capacidades/PROTOCOLO_PI04_C2B_R01.json','capacidades/PROTOCOLO_E3_R01.json'}")
    s=once(s,"def load_decision(path):\n    d=read(path)",
           "def load_decision(path):\n    d=read(path)\n    if d.get('adapter_reviewed_for_PI04')is not True or d.get('campaign')!='PROGRESION_INTEGRADA_04':\n        raise ValueError('UNEXECUTED PI04 template: root must review actual adapter and supply actual final decision; no inferred approval')")
    s=s.replace('The actual PI04 MAIN life','The actual PI04 candidate life')
    s=s.replace('default principal remains PI02','default principal remains PI03')
    s=s.replace('physical_parent identifies the PI02 physical-history predecessor.',
                'physical_parent identifies the PI03 actual physical-history predecessor; source identity retains its original PI03_REPRO_PI04 namespace.')
    s=s.replace('the preserved PI02 life','the preserved PI03 life')
    header='''# UNEXECUTED PI04 ADAPTER TEMPLATE — NOT A DECISION OR AN ADOPTION.
# Native phases require DECISION_FINAL_PI04.json with actual evidence/gates,
# adapter_reviewed_for_PI04:true, exact source/pair/protected-parent hashes,
# fresh process proof, then a separate actual product0tick reopening witness.
# No file here claims those conditions have occurred. Root must inspect the
# provenance/allowed-code list/current principal again before any invocation.
'''
    s=header+s
    target=P/'codigo/incorporar_PI04_BORRADOR.py'
    if target.exists():raise ValueError('Preserve prior adapter draft')
    compile(s,str(target),'exec');target.write_text(s,encoding='utf8',newline='')
    if source.read_bytes()!=old:raise AssertionError('PI03 adapter modified')
    proof={'schema':'DEE.PI04.incorporation_adapter.UNEXECUTED_DRAFT.v1','source':str(source),
        'source_sha256':hashlib.sha256(old).hexdigest(),'source_unchanged':True,'draft':str(target),
        'draft_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'LIFE':'ECI02_PI03_REPRO_PI04_MAIN_02','CS':'estados/candidato_R02/sistema',
        'protected_parent':'ECI02_PI03_MAIN','protected_parent_tick':775355,
        'protected_parent_snapshot_sha256':'5581d3785bf7d7194b5bdb545827aab55f0659d8b3f2c00301425d89616cf07b',
        'decision_created':False,'adoption_approved':False,'Native_ticks':0,'product_modified':False,
        'pending_before_any_use':['Actual functional/reserve/control evidence','Old12panel and no material regressions','Reached full final pair and current source CAS','Fresh scoped closed-process proof','Explicit PI04 provenance on actual source card','Approved source-code delta hashes/current product baseline','Root adapter review and actual final decision','Product import and separate0tick reopen/close before Store.promote']}
    out=P/'control/PLANTILLA_INCORPORACION_PI04_NO_EJECUTADA.json'
    if out.exists():raise ValueError('Preserve prior template proof')
    out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(proof,ensure_ascii=False,indent=2))
