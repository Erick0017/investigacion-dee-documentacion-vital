"""External closure only: verify transport and record final elapsed budget.

Never edits sealed ZIPs, scientific sources or an original archive.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--budget',type=Path,required=True);a=p.parse_args();out=a.out.resolve(strict=True)
    record=out/'VERIFICACION_FINAL.json';r=read(record);parts=read(out/'PARTES.json')
    if r['status']!='TWO_EXACT_ZIPS_VERIFIED_TRANSPORT_PENDING':raise ValueError('Unexpected or already closed publication record')
    entries={x['name']:x for x in parts['archives']}
    if len(entries)!=2 or parts['maximum_part_bytes']!=16000000:raise ValueError('Wrong transport scope/limit')
    for item in r['artifacts']:
        e=entries[item['name']];canonical=out/item['name']
        if not(e['sha256']==item['sha256']==sha(canonical) and e['bytes']==item['compressed_bytes'] and e['reconstruction_verified'] and e['byte_comparison_verified']):raise ValueError('Transport identity or reconstruction failed')
        if [v['index']for v in e['parts']]!=list(range(1,len(e['parts'])+1)):raise ValueError('Incorrect part order')
        for piece in e['parts']:
            f=out/piece['name']
            if f.parent!=out or f.stat().st_size!=piece['bytes']or piece['bytes']>16000000 or sha(f)!=piece['sha256']:raise ValueError('Bad segment')
    b=read(a.budget);q=ctypes.c_longlong();ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(q));elapsed=(q.value-b['monotonic_start'])/b['monotonic_frequency']
    if elapsed>b['budget_seconds']:raise RuntimeError('Original campaign deadline exceeded; cannot issue within-budget closure')
    r.update(status='VERIFIED_EXACT_ARTIFACTS_AND_BYTE_RECONSTRUCTION',closed_utc=datetime.now(timezone.utc).isoformat(),elapsed_monotonic_seconds_at_final_close=elapsed,
      remaining_original_budget_seconds=b['budget_seconds']-elapsed,all_final_owned_verification_workers_waited_and_jobs_closed=True,
      transport={'manifest':'PARTES.json','sha256':sha(out/'PARTES.json'),'maximum_part_bytes':16000000,'archives':parts['archives'],
      'actual_reconstruction_not_hash_only':True,'canonical_archives_unchanged_after_split':True},
      scientific_scope='Bounded historical contracts and new E1 functions. Not65human meanings, all56broad domains operationally reconstructed, R2, general curiosity, consciousness or universal language.')
    # The public final receipt remains PENDING until ALL other closure files
    # and the prospective final hash index have been written successfully.
    previous=sha(record)
    index=['# Entrega CPC9 y DEE Cognitive Core','',
      'Dos ZIP privados verificados. Las partes son segmentos binarios; no se abren por separado. Cada archivo de transferencia mide como máximo16.000.000bytes.','',
      '## Leer primero','',
      '[Lectura inicial](LEER_PRIMERO.md) · [Conclusiones](CPC9_CONCLUSIONES_Y_PENDIENTES.md) · [20 respuestas científicas](CPC9_INFORME_TRANSVERSAL_FINAL.md) · [Verificación final](VERIFICACION_FINAL.json)','',
      '## Partes para descargar','']
    for item in r['artifacts']:
        e=entries[item['name']];index+=['### '+item['name'],'',f"Comprimido: {item['compressed_bytes']:,} bytes. Expandido: {item['expanded_bytes']:,} bytes.",f"SHA-256: `{item['sha256']}`.",'']
        for piece in e['parts']:index.append(f"- [Parte{piece['index']:03d}]({piece['name']}) — {piece['bytes']:,} bytes.")
        index+=['',f"[ZIP canónico completo]({item['name']}) (opcional; supera el límite de transferencia).",'']
    index+=['## Reunir y comprobar','',
      'Descargue todas las partes del paquete elegido junto con [PARTES.json](PARTES.json) y [REUNIR_ENTREGA.py](REUNIR_ENTREGA.py). Ejecute `python REUNIR_ENTREGA.py`; el script verifica tamaño y SHA de cada parte y del ZIP. No sobrescribe un archivo diferente.','',
      'La unión/publicación atómica usa enlaces físicos: el destino debe admitirlos (NTFS probado). Si su unidad no los admite, elija otra carpeta mediante `--out`. Las instrucciones están en [INSTRUCCIONES_PARTES.txt](INSTRUCCIONES_PARTES.txt).','',
      '[Manual de recuperación](DEE_COGNITIVE_CORE_MANUAL_RECONSTRUCCION.md) · [Matriz68filas](CPC01_A_CPC09_MATRIZ_CAPACIDADES.csv) · [Compresión y pérdidas](INFORME_COMPRESION_Y_PERDIDA_DE_INFORMACION.md) · [NSM65](NSM65_EVIDENCIAS.json)','',
      'Tiempo total y límite original: véase VERIFICACION_FINAL.json, escrito como última señal de cierre; pruebas finitas, sin simulaciones propias pendientes.','',
      'La lectura en teléfono no requiere reconstruir losZIP. Para ejecutar el motor se necesita Windowsx64/CPython3.13x64; el Core declara NumPy2.2.6 sólo para CORE06/07.']
    target=out/'ENTREGA_CPC9.md'
    index_bytes=('\n'.join(index)+'\n').encode('utf8')
    if target.exists():
        if target.read_bytes()!=index_bytes:raise FileExistsError('Existing delivery index differs; preserved')
    else:
        with target.open('xb')as f:f.write(index_bytes)
    # This evidence is later than the seal, hence deliberately external.
    note='\n## Comprobación posterior al sello\n\nEl ZIP maestro exacto superó34 familias; el ZIP CPC9 exacto superó instalación offline, parser, demo/control, referencia/restauración entre procesos, cadena nueva completa de siete fases T0–2493 y recálculo. Los recibos externos conservan comandos, identidades, comparaciones y límites. Los ZIP no cambiaron al generar/verificar las partes.\n'
    for name in('CPC9_INFORME_TRANSVERSAL_FINAL.md','CPC9_CONCLUSIONES_Y_PENDIENTES.md'):
        report=out/name
        if not report.read_text(encoding='utf8').endswith(note):
            with report.open('a',encoding='utf8')as f:f.write(note)
    ordinary=[x for x in out.iterdir()if x.is_file()and x.suffix!='.zip' and x.name!='HASHES_ENTREGA.sha256']
    if any(x.stat().st_size>16000000 for x in ordinary):raise ValueError('A noncanonical delivery file exceeds transfer limit')
    # Read all larger payloads before the final clock measurement. Publication
    # time includes reports, joins and this complete delivery-byte inventory.
    digest_rows={x.name:sha(x)for x in sorted(out.iterdir())if x.is_file()and x.name not in('HASHES_ENTREGA.sha256','VERIFICACION_FINAL.json')}
    ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(q));elapsed=(q.value-b['monotonic_start'])/b['monotonic_frequency']
    if elapsed>b['budget_seconds']:raise RuntimeError('Deadline exceeded during closure; receipt stays pending')
    r.update(closed_utc=datetime.now(timezone.utc).isoformat(),elapsed_monotonic_seconds_at_final_close=elapsed,remaining_original_budget_seconds=b['budget_seconds']-elapsed,
      closure_clock_scope='After reports and all payload hashing, immediately before two small metadata commits')
    final_bytes=(json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    digest_rows['VERIFICACION_FINAL.json']=hashlib.sha256(final_bytes).hexdigest()
    hashes='# CPC9 owned final delivery index; excludes this index itself\n'+''.join(digest+'  '+name+'\n'for name,digest in sorted(digest_rows.items()))
    with (out/'HASHES_ENTREGA.sha256').open('x',encoding='utf8')as f:f.write(hashes)
    temp=record.with_name(record.name+'.closing.'+str(os.getpid()))
    with temp.open('xb')as f:f.write(final_bytes)
    if sha(record)!=previous:raise RuntimeError('External receipt concurrently changed; preserved')
    os.replace(temp,record)  # LAST commit: consumers may now rely on final status
    print(json.dumps({'status':r['status'],'elapsed_seconds':elapsed,'artifacts':r['artifacts'],'parts':sum(len(x['parts'])for x in entries.values()),'delivery':str(out)},ensure_ascii=False))
if __name__=='__main__':main()
