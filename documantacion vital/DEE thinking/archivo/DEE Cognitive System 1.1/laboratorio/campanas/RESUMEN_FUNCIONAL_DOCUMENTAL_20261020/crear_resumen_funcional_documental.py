"""Package existing 1.1 documents. Does not import or execute DEE or validation code."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import zipfile

NAME="DEE_COGNITIVE_SYSTEM_1_1_RESUMEN_FUNCIONAL"
SOURCES=[
("sistema/documentacion/MATRIZ_HERENCIA_CPC01_CPC09.csv","Inventario completo; disponibilidad, integración, dominios y comandos ya documentados"),
("sistema/documentacion/NSM65_ESTADO_POR_VIDA.csv","Tabla NSM original, sin edición ni recálculo"),
("sistema/documentacion/ARQUITECTURA_Y_SEPARACION.md","Arquitectura, fronteras, estado operativo y errores"),
("sistema/documentacion/ESTADO_ACTUAL_DE_VIDAS.json","Nueve estados seleccionados y conocimiento atribuido por vida"),
("sistema/documentacion/RAMAS_Y_GENEALOGIA.json","Identidades, parentescos y ramas"),
("sistema/documentacion/DECISIONES_DE_PROMOCION.md","Mejoras, pérdidas, alternativas no promovidas"),
("sistema/documentacion/COBERTURA_REGRESION.json","Cobertura anterior; no ejecución nueva"),
("sistema/documentacion/DESCUBRIMIENTOS_NATIVOS.json","Observaciones nativas separadas del catálogo NSM"),
("sistema/documentacion/GUIA_DE_USO_1_1.md","Procedimientos aplicables al SISTEMA completo"),
("sistema/documentacion/USO_PRIVADO.md","Alcance privado"),
("sistema/contratos/PERFILES.json","Cinco perfiles y límites de atribución"),
("sistema/contratos/PROMOCION_SOCIAL_R1.json","Decisión preferente, ganancias, pérdidas e incertidumbres"),
("sistema/estado/ACTIVO.json","Puntero activo registrado; no se carga el mundo"),
("sistema/capacidades/core/FAMILIAS.json","Identidad de las familias de recuperación; sin código o datos del motor"),
("evidencia/informes/CATALOGO_CAPACIDADES_1_1.json","Catálogo completo con procedencia, dominios, controles y estados"),
("evidencia/informes/COBERTURA_Y_DECISION.json","Decisión y cobertura existente por alcance"),
("evidencia/informes/CALCULOS_DESDE_PRIMARIOS.json","Resultados de cálculos anteriores copiados literalmente, sin recalcular"),
("evidencia/informes/INFORME_CIENTIFICO_1_1.md","Informe existente de resultados y límites"),
("evidencia/informes/RESUMEN_CIENTIFICO_1_1.md","Síntesis final existente"),
("evidencia/informes/PENDIENTES_Y_CAUSAS.json","16 filas documentales y otros problemas abiertos"),
("evidencia/informes/NSM65_COBERTURA.json","Cobertura semántica previamente registrada"),
("evidencia/informes/NSM65_DIMENSIONES_POR_VIDA.json","Dimensiones y localizadores NSM por vida"),
("evidencia/informes/INFORME_TAMANOS_Y_COMPACTACION.md","Decisiones previas de tamaño y exclusión"),
("evidencia/informes/RECURSOS_Y_TAMANOS.json","Recursos registrados, no mediciones nuevas"),
("evidencia/verificaciones/RECUPERACION_FINAL_DESDE_ZIP/REGRESION_HEREDADA_LIMPIA.json","Resultado existente de recuperación limpia de34familias"),
("evidencia/verificaciones/RECUPERACION_FINAL_DESDE_ZIP/PERFILES_CANDIDATO02/RESULTADOS.json","25comprobaciones existentes, reutilizadas por identidad de payload en el cierre"),
("evidencia/verificaciones/NUEVE_ESTADOS_ORIGINALES_VALIDOS.json","Resultado archivado de carga de nueve estados"),
("evidencia/verificaciones/TABLAS_CSV_RELECTURA.json","Registro anterior de conservación de las tablas"),
("evidencia/verificaciones/ORIGINALES_SIN_MODIFICAR.json","Constancia anterior de identidad de fuentes; no nueva auditoría"),
("evidencia/INDICE_EVIDENCIA.json","Índice anterior de primarios y localizadores; no incluye los datos a los que remite"),
("PROVENANCE.json","Procedencia acumulativa existente"),
("entregas/VERIFICACION_FINAL_EXTERNA.json","Comprobante final anterior, no repetido"),
("entregas/REANUDACION.json","Cierre de campaña existente"),
("entregas/DEE_COGNITIVE_SYSTEM_1_1_SISTEMA.SELLADO.json","Identidad registrada del ZIP operativo; el ZIP no se anida"),
("entregas/DEE_COGNITIVE_SYSTEM_1_1_AUDITORIA_ESENCIAL.SELLADO.json","Identidad registrada de la auditoría; el ZIP no se anida")
]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def js(data):
    return (json.dumps(data,ensure_ascii=False,indent=2)+"\n").encode("utf-8")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--content",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    root=a.root.resolve()
    output=a.output.resolve()
    if output.exists():
        raise FileExistsError("Se conserva el ZIP existente; no se sobrescribe")
    payload={}
    members=[]
    for relative,purpose in SOURCES:
        source=root/relative
        data=source.read_bytes()
        dest="originales/"+relative
        payload[dest]=data
        members.append({"file":dest,"bytes":len(data),"sha256":sha(data),
            "role":"COPIA_LITERAL_DE_DOCUMENTO_EXISTENTE",
            "source_relative_to_DCS11":relative,"source_absolute":str(source),
            "source_sha256":sha(data),"purpose":purpose,"original_modified":False})
    for name in ("LEER_PRIMERO.md","RESUMEN_FUNCIONAL.md","MEJORAS_COEXISTENCIAS_Y_LIMITES.md","FUENTES_Y_ALCANCE.md"):
        data=(a.content/name).read_bytes()
        payload[name]=data
        members.append({"file":name,"bytes":len(data),"sha256":sha(data),
            "role":"ORGANIZACION_DOCUMENTAL_NUEVA_SIN_RESULTADOS_NUEVOS",
            "basis":"Documentos originales incluidos y localizadores citados"})
    def original(relative):
        return "originales/"+relative
    index={"schema":"DCS1.1.functional.document.index.v1",
        "scope":"Lectura y empaquetado documental de registros existentes",
        "questions":[
            {"number":1,"topic":"Capacidades CPC1–CPC9 recuperadas",
             "documents":[original("sistema/documentacion/MATRIZ_HERENCIA_CPC01_CPC09.csv"),original("evidencia/informes/CATALOGO_CAPACIDADES_1_1.json"),original("evidencia/verificaciones/RECUPERACION_FINAL_DESDE_ZIP/REGRESION_HEREDADA_LIMPIA.json")],
             "locators":["Filas identificadas por id y origin; availability/integration no son conocimiento por individuo","entries[].source_identities, audit_row, revalidation; legacy_family_contracts"]},
            {"number":2,"topic":"Mejoras, sustituciones locales y mecanismos complementarios",
             "documents":["MEJORAS_COEXISTENCIAS_Y_LIMITES.md",original("sistema/documentacion/DECISIONES_DE_PROMOCION.md"),original("sistema/contratos/PROMOCION_SOCIAL_R1.json")],
             "locators":["gains/losses/uncertainties/not_promoted","No existe declaración nueva de superioridad universal"]},
            {"number":3,"topic":"Integración real, otros perfiles y pendientes",
             "documents":[original("sistema/contratos/PERFILES.json"),original("evidencia/informes/PENDIENTES_Y_CAUSAS.json"),original("evidencia/informes/CATALOGO_CAPACIDADES_1_1.json")],
             "locators":["profiles[].current_learned_lives e integration_caveat","documentary_rows, still_open","entries[].integration/availability/knowledge"]},
            {"number":4,"topic":"Qué conserva cada vida y participante",
             "documents":["RESUMEN_FUNCIONAL.md",original("sistema/documentacion/ESTADO_ACTUAL_DE_VIDAS.json"),original("sistema/documentacion/NSM65_ESTADO_POR_VIDA.csv")],
             "locators":["lives[].life_id/tick/scope_current_knowledge/parent","A/B/C: participantes del mismo mundo, no vidas completas independientes"]},
            {"number":5,"topic":"Uso conjunto e incompatibilidades",
             "documents":["MEJORAS_COEXISTENCIAS_Y_LIMITES.md",original("evidencia/informes/INFORME_CIENTIFICO_1_1.md"),original("evidencia/informes/CALCULOS_DESDE_PRIMARIOS.json")],
             "locators":["Deterioro; Aprendizaje/comunicación; Repertorios; functional/mobile/K65/late_access/social_causal ya calculados","Nada fue recalculado para este ZIP"]},
            {"number":6,"topic":"Arquitectura, estados y continuidad",
             "documents":[original("sistema/documentacion/ARQUITECTURA_Y_SEPARACION.md"),original("sistema/documentacion/RAMAS_Y_GENEALOGIA.json"),original("sistema/documentacion/GUIA_DE_USO_1_1.md"),original("entregas/VERIFICACION_FINAL_EXTERNA.json")],
             "locators":["Los comandos se aplican al SISTEMA anterior, no al resumen","checks/profile_release/heritage_release y sealed_archives_and_transport: registros de verificaciones anteriores"]},
            {"number":7,"topic":"Resultados, tablas y referencias de respaldo",
             "documents":["MANIFIESTO.json",original("evidencia/INDICE_EVIDENCIA.json"),original("PROVENANCE.json")],
             "locators":["El manifiesto enumera los documentos incluidos","El índice anterior remite a evidencia profunda no necesariamente incluida"]}
        ],
        "not_included":["Motor, WHL/PYD y fuentes","Código del sistema ejecutable","Snapshots completos","Telemetría y arraysRAW/clocks","ZIP históricos y paquetes completos"],
        "not_executed":["Simulaciones","Auditorías científicas nuevas","Pruebas/regresiones","Recálculos de métricas","Continuación/carga de individuos","Generación de telemetría"],
        "references_to_prior_exact_archives":[
            json.loads(payload[original("entregas/DEE_COGNITIVE_SYSTEM_1_1_SISTEMA.SELLADO.json")]),
            json.loads(payload[original("entregas/DEE_COGNITIVE_SYSTEM_1_1_AUDITORIA_ESENCIAL.SELLADO.json")])
        ]}
    payload["INDICE_DOCUMENTAL.json"]=js(index)
    members.append({"file":"INDICE_DOCUMENTAL.json","bytes":len(payload["INDICE_DOCUMENTAL.json"]),
        "sha256":sha(payload["INDICE_DOCUMENTAL.json"]),"role":"INDICE_DOCUMENTAL_NUEVO_SIN_EJECUCION"})
    manifest={"schema":"DCS1.1.functional.summary.manifest.v1",
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "project_root":str(root),"author_of_source_project":"Ivan Erick Tlaltecatl Morales",
        "package_type":"RESUMEN_DOCUMENTAL_NO_EJECUTABLE",
        "source_cut":"DEE Cognitive System1.1 cerrado; identidades exactas en comprobantes anteriores incluidos",
        "source_documents_copied":len(SOURCES),
        "no_original_files_modified":True,
        "no_engine_or_experiment_execution":True,
        "no_new_scientific_audit_or_metric_recalculation":True,
        "hashes_are_for_packaging_provenance_not_new_scientific_verification":True,
        "csv_policy":"Copias literales; ningún archivoCSV es reescrito",
        "member_hashes_exclude_self_and_HASHES_file":True,
        "files":members}
    payload["MANIFIESTO.json"]=js(manifest)
    payload["HASHES.sha256"]=("".join(sha(b)+"  "+n+"\n" for n,b in sorted(payload.items()))).encode("utf-8")
    total=sum(map(len,payload.values()))
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,"x",compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as z:
        for name,data in sorted(payload.items()):
            z.writestr(NAME+"/"+name,data)
    print(json.dumps({"file":str(output),"bytes":output.stat().st_size,
        "expanded_bytes":total,"members":len(payload),"sha256":sha(output.read_bytes()),
        "source_documents":len(SOURCES),"experimental_runs":0,"new_scientific_tests":0,
        "scientific_metrics_recalculated":False},ensure_ascii=False))

if __name__=="__main__":
    main()

