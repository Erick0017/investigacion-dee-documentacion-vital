"""Bounded exact localizers, not an inventory or a claim of complete state backup."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0'
def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def record(p,role):
    p=p.resolve(strict=True)
    if not p.is_relative_to(R.resolve()): raise ValueError('Outside DEE scope')
    for n in (p,*p.parents):
        if n.is_symlink() or getattr(n.lstat(),'st_file_attributes',0)&1024: raise ValueError('Linked source refused')
    return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'role':role}
def main(a):
    ledger=read(a.ledger);rows=[]
    for r in ledger['Native_ledger']['life_rows']:
        cards=[]
        for path in r['cards']:
            q=Path(path);j=read(q);system=q.parents[3]
            snapshot=(system/j['snapshot']).resolve(strict=True)
            if sha(snapshot)!=j['snapshot_sha256']: raise ValueError('Current saved cut mismatch')
            pair={'system_root':str(system),'card':record(q,'Current saved identity/genealogy; not a full world'),
                  'snapshot':record(snapshot,'Current full Native snapshot; requires paired transport/store/environment'),
                  'VIDA_paths_are_not_a_complete_backup':True,
                  'required_state_components':'Interfaces, agenda, organizational state, queue/SQLite+receipts/outbox, environmental resources and progress according to the existing service contract; never restore RAW alone.'}
            cards.append(pair)
        rows.append({'life_id':r['life_id'],'parent_tick':r['parent_tick'],'current_tick':r['current_tick'],
                     'current_stores':cards,'reason_not_in_analysis_ZIP':'Large complete operational sets remain local. The analysis packet is not an executable backup; partial snapshots do not replace their paired service.'})
    exact=[record(P/'ENSAYOS.jsonl','Deep supervisor/resource telemetry retained locally; summary included'),
           record(R/'4.5/DEE_thinking_4_5_0_Maestro_Arquitectura_Reconstruccion.docx','Official Thinking architecture manual unchanged; prior directed readings reused'),
           record(R/'4.5/DEE_thinking_4_5_0_Libro_Blanco_y_Manual_Tecnico.docx','Distinct official Thinking technical manual unchanged; not included due size/shared dependencies')]
    for item in ledger['engine_and_kernel_source_pins']:
        exact.append(record(Path(item['path']),'Frozen shared engine/source dependency, hash checked without execution'))
    manifests=[]
    for p in [C/'reproducibilidad/materiales/PI08_A_CONSOLIDADA_T861426/EXPORTACION_SERVICIO.json',
              P/'pares/PI08_B_REAL_POST18_T875451/EXPORTACION_SERVICIO.json',
              P/'pares/PI08_B_NONE_POST18_T875451/EXPORTACION_SERVICIO.json']:
        if not p.is_file():
            # The exporter can use its existing MANIFIESTO name. Never invent a manifest.
            candidates=[q for q in p.parent.iterdir() if q.is_file() and q.suffix=='.json' and ('MANIFEST' in q.name.upper() or 'EXPORT' in q.name.upper())] if p.parent.exists() else []
            manifests.extend(record(q,'Existing complete pair preservation manifest; exact name retained') for q in candidates)
        else: manifests.append(record(p,'Existing complete pair preservation manifest; its member list covers the large local set'))
    out={'schema':'DEE.PI08.located_omissions.v1','at_utc':datetime.now(timezone.utc).isoformat(),
         'ledger_source':record(a.ledger,'Bounded saved-card accounting'),
         'states_retained_locally':rows,'large_shared_sources':exact,'complete_pair_manifests':manifests,
         'F1_exception':'Two exact q8 parent/identity snapshots travel in the analysis; no cut state exists. Other F1 failed/partial operational state remains local, not adopted.',
         'preservation_scope':'Exact local file availability and hashes here; no new Native opening, no online SQLite copy, no proof of unlimited future use.',
         'next_material_needed':'For Native replay use the existing RP recipe and full referenced prefix/capsule/official runtime, not this ZIP alone. For a specific omitted state bring its paired service, not just its snapshot.',
         'new_Native_ticks':0,'DEE_imports':0}
    with a.salida.open('x',encoding='utf-8') as f: json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(a.salida),'sha256':sha(a.salida),'states':len(rows),'large_files':len(exact)}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ledger',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);main(p.parse_args())
