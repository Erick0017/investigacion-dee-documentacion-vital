"""Reproduction comparison: exact bytes are distinct from physical equivalence."""
from pathlib import Path
import argparse,difflib,gzip,hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[4]
def digest(p,expanded=False):
    h=hashlib.sha256();size=0
    with(gzip.open(p,'rb')if expanded else Path(p).open('rb'))as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b);size+=len(b)
    return h.hexdigest(),size
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def save_change(r,zpath):
    identity=digest(zpath)[0]
    if identity!='935f7f78f799e2ff5e1cabfe568960ed61d708aeb6efaf7b075a2be6d601860a':raise ValueError('Diff requires immutable candidate01, never an ambiguous canonical alias')
    dest=r/'evidencia/diagnosticos/GESTION_FALLOS_PARCIALES/CAMBIO_R1_R2.json'
    if dest.exists():
        before=json.loads(dest.read_bytes())
        if before.get('source_archive_sha256')!=identity:
            invalid=dest.with_name('INTENTO_INVALIDO_POR_ALIAS.json')
            if invalid.exists():raise FileExistsError('Prior invalid attempt already preserved')
            put(invalid,{'status':'INSTRUMENTALLY_INVALID','cause':'The canonical ZIP name was moved from candidate01 to candidate02 while the byte-comparison utility was running. Its initial diff therefore compared candidate02 against itself. Native-state regeneration counts were unaffected; the mislabeled zero diff is not accepted as evidence.','original_unaccepted_result':before,'native_experiments_repeated':0})
    changes=[]
    with zipfile.ZipFile(zpath)as z:
        for rel in('sistema/app/lives.py','sistema/gestionar.py','sistema/pruebas_minimas/probar_sistema.py'):
            before=z.read('DEE_COGNITIVE_SYSTEM_1_1/'+rel);after=(r/rel).read_bytes();changes.append({'file':rel,'candidate01_sha256':hashlib.sha256(before).hexdigest(),'candidate02_sha256':hashlib.sha256(after).hexdigest(),'diff':''.join(difflib.unified_diff(before.decode('utf8').splitlines(True),after.decode('utf8').splitlines(True),fromfile='CANDIDATO01/'+rel,tofile='CANDIDATO02/'+rel))})
    put(dest,{'schema':'DCS1.1.partial_failure.correction.v1','source_archive':str(zpath),'source_archive_sha256':identity,'reason':'Persist partial failed operations instead of losing admitted inputs. No kernel, decoder or inherited recoveryworker change.','changes':changes,'affected_tests':'Common-interface profile release including admitted-input-then-invalid-form, pendingqueue, reload and later native response.','unaffected':'Core source store, engine, inherited workers and their physics; exact payload equality and targeted fresh references.'})
    return changes
def main():
    p=argparse.ArgumentParser();p.add_argument('--fresh',type=Path);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--source-candidate',type=Path);p.add_argument('--diff-only',action='store_true');a=p.parse_args();r=a.root;zpath=a.source_candidate or r/'entregas/candidatos/CANDIDATO_01/DEE_COGNITIVE_SYSTEM_1_1_SISTEMA.zip'
    if a.diff_only:print(json.dumps({'changed_files':len(save_change(r,zpath)),'native_experiments_repeated':0}));return
    if a.fresh is None:raise ValueError('--fresh is required for state comparison')
    old=r/'evidencia/verificaciones/HERENCIA_01';new=a.fresh/'HERENCIA_FINAL';rows=[]
    for f in sorted(old.rglob('*')):
        if not f.is_file()or f.suffix not in('.deetsnap','.gz'):continue
        rel=f.relative_to(old);n=new/rel;oh,size=digest(f);row={'path':rel.as_posix(),'original_sha256':oh,'original_bytes':size,'recovered_exists':n.exists()}
        if n.exists():
            nh,ns=digest(n);row.update(recovered_sha256=nh,recovered_bytes=ns,exact_bytes_equal=nh==oh)
            if f.suffix=='.gz':
                try:
                    oe,oes=digest(f,True);ne,nes=digest(n,True);row.update(exact_gzip_expanded_bytes_equal=oe==ne,original_expanded_sha256=oe,recovered_expanded_sha256=ne,expanded_bytes=oes)
                except (OSError,EOFError):row['gzip_expansion_comparison']='NOT_GZIP_OR_INVALID; no equivalence inferred'
        rows.append(row)
    report={'schema':'DCS1.1.regeneration.comparison.v1','original_root':str(old),'fresh_root':str(new),'compared_native_states':len(rows),'exact_byte_equal':sum(x.get('exact_bytes_equal',False)for x in rows),'not_byte_equal_or_missing':sum(not x.get('exact_bytes_equal',False)for x in rows),'rows':rows,'meaning':'Exactbytes and expanded-gzipbytes are measured separately. Metadata differences are not silently called identity. A result below does not invent unavailable historical full-state hashes.'}
    report['direct_array_ports']=[]
    for family in('core06','core07'):
        op=old/('native_'+family)/'PRIMARY_TRANSITIONS.json';np=new/('native_'+family)/'PRIMARY_TRANSITIONS.json'
        if op.exists()and np.exists():
            od=json.loads(op.read_bytes());nd=json.loads(np.read_bytes());keys=('family','worlds','transitions','physical_imports');report['direct_array_ports'].append({'family':family,'keys_compared':keys,'exact_decoded_fields_equal':{k:od[k]==nd[k]for k in keys},'original_sha256':digest(op)[0],'recovered_sha256':digest(np)[0],'scope':'New official4.5 port initial states, exact external array writes and terminal RAW/clocks; not a fabricated historical fullstate comparison.'})
    put(r/'evidencia/verificaciones/REGENERACION_ESTADOS_HEREDADOS.json',report)
    # Preserve the exact source delta that motivated the narrow second cut.
    save_change(r,zpath)
    print(json.dumps({'states':len(rows),'exact_equal':report['exact_byte_equal'],'not_equal_or_missing':report['not_byte_equal_or_missing'],'direct_ports':report['direct_array_ports']}))
if __name__=='__main__':main()
