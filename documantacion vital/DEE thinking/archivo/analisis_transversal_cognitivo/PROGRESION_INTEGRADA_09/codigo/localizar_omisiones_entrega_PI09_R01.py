"""Read-only scoped locations and logical bytes; never imports DEE."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os

P=Path(__file__).resolve().parents[1]
R=P.parents[2]
C=R/'DEE Cognitive 2.0'
S=C/'sistema'
RP=C/'reproducibilidad'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def ref(p):
    return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def tree(p):
    count=total=0; excluded=[]
    for base, dirs, files in os.walk(p,followlinks=False):
        root=Path(base)
        for name in list(dirs):
            q=root/name
            if q.is_symlink() or getattr(q.lstat(),'st_file_attributes',0)&1024:
                dirs.remove(name);excluded.append(str(q))
        for name in files:
            q=root/name
            if q.is_symlink():excluded.append(str(q));continue
            count+=1;total+=q.stat().st_size
    return {'path':str(p),'files':count,'logical_bytes':total,'excluded_links':excluded}

output=P/'control/OMISIONES_Y_ALMACENAMIENTO_PI09_R01.json'
assert not output.exists()
closure=json.loads((P/'control/CIERRE_PRESUPUESTO_Y_ESTADO_PI09_R01.json').read_text('utf-8-sig'))
assert closure['all_scoped_Native_writers_closed'] is True
life=closure['current_main']['life_id']
card=json.loads((S/'estado/vidas'/life/'VIDA.json').read_text('utf-8-sig'))
assert card['physical']['tick']==922371
omitted=[]
for label,p in [('Full current snapshot',S/card['snapshot']),
 ('Official architecture manual',R/'4.5/DEE_thinking_4_5_0_Maestro_Arquitectura_Reconstruccion.docx'),
 ('Official technical manual',R/'4.5/DEE_thinking_4_5_0_Libro_Blanco_y_Manual_Tecnico.docx')]:
    omitted.append({'kind':label,**ref(p),'reason':'Kept intact locally; large states and official Thinking manuals are excluded from the 15,000,000-byte analysis ZIP.'})
for name in ('MAPA_TRASLADO_PRODUCTO_PI09.json','MAPA_TRASLADO_D_PRODUCTO_PI09.json'):
    omitted.append({'kind':'Complete state member map',**ref(P/'control'/name),'reason':'Map is delivered as evidence; full member bytes stay at mapped current product paths.'})
scopes=[P]
for parent in ('materiales','codigo_preservado','evidencia','verificaciones'):
    if (RP/parent).is_dir():scopes += [p for p in (RP/parent).iterdir() if p.is_dir() and 'PI09' in p.name.upper()]
for ident in (life,'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'):
    for part in ('vidas','servicios_locales','servicios_persistentes'):
        p=S/'estado'/part/ident
        if p.exists():scopes.append(p)
totals=[tree(p) for p in scopes]
checkpoint_files=[p for p in (S/'estado/checkpoints').iterdir() if p.is_file() and ('PI09_DISCOVERY_01' in p.name or 'PI09_NATIVE_01' in p.name)]
logical=sum(v['logical_bytes'] for v in totals)+sum(p.stat().st_size for p in checkpoint_files)
value={'schema':'DEE.PI09.local_omissions_and_scoped_logical_size.R01','at_utc':datetime.now(timezone.utc).isoformat(),
 'Native_executed':False,'omitted':omitted,'complete_current_state_directories':[str(S/'estado'/x/life) for x in ('vidas','servicios_locales','servicios_persistentes')],
 'current_full_state_contract':'Snapshot plus interfaces, agenda, SQLite/receipts/outbox/artifacts and environmental progress in the full member map. The small ZIP is not a runnable backup.',
 'stable_RP_resources':ref(RP/'RECURSOS.json'),'scoped_logical_measurements':totals,'additional_product_checkpoint_files':len(checkpoint_files),'scoped_logical_bytes':logical,
 'size_scope':'Campaign tree, new PI09 shared RP directories, both relocated PI09 product worlds and their checkpoints. Logical file sizes count hardlinks by path. No free-space recovery claim.',
 'storage_limit_bytes':16000000000,'closure_reserve_bytes':1000000000,'scoped_plus_reserve_fits':logical+1000000000<=16000000000,
 'coverage_limit':'Small root metadata/code/document deltas outside these scopes are bounded separately by the explicit package/code manifests; this is not a census of the computer or proof of every original byte.',
 'deep_data_local':[str(P/'ensayos'),str(P/'estados'),str(P/'pares'),str(P/'codigo'),str(RP/'materiales'),str(RP/'codigo_preservado')],
 'exclusions':['Historical engines/WHL/checkpoint collections are not duplicated in the ZIP.','No credentials, unrelated business, email, videos, Drive or Mac work was collected.'],
 'temporary_verification':'Fresh p9v* extraction is regenerable from the verified ZIP, but is not deleted automatically. Campaign states/evidence and stable RP stores are not temporary.'}
output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'output':str(output),'sha256':sha(output),'scoped_logical_bytes':logical,'plus_reserve_fits':value['scoped_plus_reserve_fits']}))
