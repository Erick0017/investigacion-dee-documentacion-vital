"""Cierre N0 de ciencia APD04: fuentes selladas y reserva ya ejecutada; no Native/Word/ZIP."""
import argparse, hashlib, json, shutil
from pathlib import Path

def sha(data): return hashlib.sha256(data).hexdigest()
def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as f:
        json.dump(obj, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n')
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--root',type=Path,required=True)
    a=p.parse_args(); r=a.root; lab=r/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'; c=lab/'cierre'
    out=c/'FUENTES_CIERRE_SOURCE_Y_WORD_N0_R01'; assert not out.exists(); out.mkdir()
    sealpath=r/'entregas/SELLO_DISTRIBUCION_APD04_R01.json'; sb=sealpath.read_bytes()
    assert sha(sb)=='663382aef356d230bfaee5ebcad9068868391e83c763e76db080d010ad90989d'
    seal=json.loads(sb); mapping=[]; omitted=[]
    rows=list(seal['source_members'])
    rows += [{'file': seal['manual'], 'sha256': seal['manual_sha256'], 'bytes':(r/seal['manual']).stat().st_size}]
    extra=['entregas/SELLO_DISTRIBUCION_APD04_R01.json',
           'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/cierre/cerrar_corte_operativo_apd04_n0_r01.py',
           'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/manual/RESULTADOS_MANUAL_APD04_APROBADOS_R01.json',
           'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/VERIFICACION_MANUAL_EDICION_1_18_R01.json',
           'CONTINUIDAD_APD04_ECOSISTEMA_COGNITIVO.json','REANUDACION.json','LEER_PRIMERO.md']
    for name in extra:
        path=r/name
        if path.exists():
            b=path.read_bytes(); rows.append({'file':name,'sha256':sha(b),'bytes':len(b)})
    seen=set()
    for row in rows:
        name=row['file']
        if name in seen: continue
        seen.add(name)
        if name.startswith('sistema/capacidades/core/'):
            omitted.append(dict(row,reason='Inherited CPC core unchanged; full authority indexed by the exact source seal, not duplicated in APD04 analysis.')); continue
        b=(r/name).read_bytes(); assert sha(b)==row['sha256'] and len(b)==row['bytes'],name
        dest=out/'BYTES_CERRADOS'/name; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(b)
        mapping.append(dict(row,frozen_file=dest.relative_to(out).as_posix()))
    dump(out/'ORIGENES_Y_OMISIONES.json',{'source_seal_sha256':sha(sb),'members_copied_exactly':mapping,
        'members_omitted_explicitly':omitted,'scope':'Frozen final bytes; no installation/physical action performed by this capture.', 'Native_ticks':0})
    note='''# Incorporaciones efectivas y límites APD04\n\nLa autoridad del cierre operativo es `SELLO_DISTRIBUCION_APD04_R01.json`, SHA-256 663382aef356d230bfaee5ebcad9068868391e83c763e76db080d010ad90989d. Sella 279 miembros de Source, el Manual 1.18 y el par completo de la semilla APD04_SEMILLA_COLABORADOR_R01 T654959, sin ticks Native ni consultas de esa semilla. ACTIVO permanece protegido; no se promueven ni fusionan los futuros adversos.\n\nSe incorporaron al mismo gestor los cinco comandos literales de ecosistema y sus contratos, guía, continuidad, catálogo, genealogía y overlay NSM. Son transporte y aparato P0; no conversación libre, 20 fuentes simultáneas, atención aprendida general ni R2. Las dos asociaciones añadidas tienen atribución y vida; NSM conserva `nsm_upgrades=[]`. El panel de 16 formas+6 contextos+2 asociaciones se realizó en una copia diagnóstica, no en la semilla original.\n\nEl patch logístico previo quedó conservado. En su aplicación inicial, 2/5 archivos coincidieron byte a byte; los otros 3/5 sólo diferían por CRLF y coincidían normalizados y como valores JSON. Hubo después cambios descriptivos explícitos de Root: estado de prueba Full como ledger externo, enlaces del README y separación del panel NSM. Por tanto el patch propuesto no sustituye ni define los bytes finales: el sello Source y las copias exactas aquí preservadas son la autoridad final. No se afirma que los cinco finales sean idénticos al patch previo. Los tres módulos actor físicos congelados se cotejaron intactos.\n\nEl Word real conserva DCS11-MM-001 y pasa de edición 1.17 a 1.18: SHA c0c1d75011d181f4d8c81555dcc5997bcc60643e2ce09dbe20889692a1110d98,158521 bytes. Se preservaron 813 nodos y cambiaron cuatro partes OOXML. Se intentó renderizar, pero faltó soffice.exe: cero páginas verificadas visualmente. Esta limitación no se disfraza de validación visual. La edición anterior se conservó con su hash.\n\nLa prueba Full del ZIP exacto es posterior y externa a este cierre. No se certifica por el sello Source ni por este documento. El análisis no incluye motor, WHL o snapshots completos y no reemplaza el paquete operativo local.\n'''
    with (out/'INCORPORACIONES.md').open('x',encoding='utf8',newline='\n') as f:f.write(note)
    members=[{'file':x.relative_to(out).as_posix(),'bytes':x.stat().st_size,'sha256':sha(x.read_bytes())} for x in sorted(out.rglob('*')) if x.is_file()]
    dump(out/'MANIFIESTO.json',{'members':members,'Native_ticks':0,'scope':'Final immutable Source/Word capture, not a scientific global PASS.'})
    comp=lab/'controles_diseno/EVIDENCIA_RESERVA_TEMPRANA_CERRADA_N0_R08'; mb=(comp/'MANIFIESTO.json').read_bytes()
    assert sha(mb)=='13162984aab77c09a879eeb44b6bbc33149eac52288872cc4dfeaef214df5f31'
    qa=lab/'controles_diseno/VERIFICACION_RESERVA_TEMPRANA_PORTABLE_N0_R08.json'; qb=qa.read_bytes()
    rel=lambda path:path.relative_to(r).as_posix()
    spec={'base':rel(c/'CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R06'),
      'base_manifest_sha256':'f5aa118d82a6dc0f9db8dbabe6d8cad87c5e4073c54635353a9496f099bbce68',
      'components':[{'id':'EARLY_RESERVE_FINAL_R08','source':rel(comp),'manifest':'MANIFIESTO.json','manifest_sha256':sha(mb)},
        {'id':'FINAL_SOURCE_WORD_CAPTURE','source':rel(out),'manifest':'MANIFIESTO.json','manifest_sha256':sha((out/'MANIFIESTO.json').read_bytes())}],
      'files':[{'id':'EARLY_RESERVE_PORTABLE_QA','source':rel(qa),'sha256':sha(qb),'bytes':len(qb)}],
      'jobs':[{'id':'EARLY_RESERVE_FINAL_R08','base':'.','script':rel(comp/'recalcular_vistas_y_reserva_r03_n0_r08.py'),
        'args':['--recalc',{'input':rel(comp)},'--output','{output}'],'expected':rel(comp/'RECALCULO_CIENTIFICO.json'),'comparison':'bytes','timeout_seconds':900}],
      'pending_not_included':['Exact Full archive proof; final Root analysis approval. Source/Word actual closed bytes are included, with visual validation unavailable.']}
    dump(c/'EXTENSION_CAS_FINAL_CIENCIA_SPEC_N0_R08.json',spec)
    print(json.dumps({'frozen_members':len(mapping),'explicitly_omitted_core_members':len(omitted),'spec':rel(c/'EXTENSION_CAS_FINAL_CIENCIA_SPEC_N0_R08.json'),'Native_ticks':0}))
if __name__=='__main__':main()
