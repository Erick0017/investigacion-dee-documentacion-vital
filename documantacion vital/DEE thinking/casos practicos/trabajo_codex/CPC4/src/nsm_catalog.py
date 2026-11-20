"""Versioned documentary NSM inventory, not a native cognition implementation.

Spanish exponents are factual catalogue labels from the scholarly resources
cited below. Registering a form does not establish its DEE realization, acquired
association, retention, reserved use, emission or composition.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONSULTED = "2026-10-17"
DIMENSIONS = (
    "interfaz_registrada", "fisica_realizable", "asociacion_entrenada",
    "retencion", "reservada", "emision", "composicion",
)
SOURCES = {
    "NSM_ES_DIAGRAM_2021": {
        "url": "https://nsm-approach.net/wp-content/uploads/2021/10/Primes_Diagram_Spanish_2021.png",
        "title": "Semantic primes Spanish diagram",
        "attribution": "Spanish after Catherine Travis2002; diagram Lauren Sadow2019, original design Havain Oy",
        "version_locator": "2021/10 publication path; diagram footer2019; downloaded and visually inspected",
        "consulted_utc_date": CONSULTED,
        "license": "CC-BY-SA4.0, explicit diagram footer and resource-page notice",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "local_artifact": "fuentes/NSM/Primes_Diagram_Spanish_2021.png",
        "role": "Spanish forms and documented allolexes, not evidence of any DEE capability",
    },
    "NSM_ES_TABLE_2021": {
        "url": "https://nsm-approach.net/wp-content/uploads/2021/10/Spanish_Table_Primes.docx",
        "title": "Spanish Semantic Primes with English equivalents after Travis2002",
        "version_locator": "2021/10 resource path; XML table inspected read-only",
        "consulted_utc_date": CONSULTED,
        "local_staging_only": "staging/nsm/Spanish_Table_Primes.docx",
        "distribution": "The complete DOCX is not a campaign deliverable; only factual catalogue forms and bibliographic provenance are retained",
        "role": "Cross-check Spanish exponent grouping and English glosses",
    },
    "NSM_RESOURCES": {
        "url": "https://nsm-approach.net/resources",
        "title": "NSM resources maintained by Lauren Sadow; site developed by Bert Peeters",
        "consulted_utc_date": CONSULTED,
        "role": "Primary research-community resource index and diagram licence notice",
    },
    "TRAVIS_2002": {
        "url": "https://doi.org/10.1075/slcs.60.11tra",
        "index_url": "https://nsm-approach.net/archives/983",
        "title": "La Metalengua Semántica Natural The Natural Semantic Metalanguage of Spanish",
        "author": "Catherine Travis",
        "year": 2002,
        "bibliography": "In C.Goddard and A.Wierzbicka editors, Meaning and universal grammar, vol1, pp173-242, John Benjamins",
        "consulted_utc_date": CONSULTED,
        "access_scope": "Bibliographic record verified; chapter not reproduced and not claimed read in full",
    },
    "WIERZBICKA_2021": {
        "url": "https://journals.rudn.ru/linguistics/article/view/26795/en_US",
        "doi": "10.22363/2687-0088-2021-25-2-317-342",
        "title": "Semantic Primitives fifty years later",
        "author": "Anna Wierzbicka",
        "year": 2021,
        "consulted_utc_date": CONSULTED,
        "own_summary": "The author describes the inventory stabilizing at65 in2014 and presents universality as the NSM research programme's empirical claim. It is not a finding about DEE.",
        "reproduction": "Bibliographic fields and short original summary only; no full article copy",
    },
    "GODDARD_WIERZBICKA_CHART_2022": {
        "url": "https://nsm-approach.net/wp-content/uploads/2022/05/Chart-of-NSM-Semantic-Primes_English_v20_May-2022.pdf",
        "title": "Chart of NSM Semantic Primes English",
        "version_locator": "v20,10May2022, one-page chart",
        "consulted_utc_date": CONSULTED,
        "own_summary": "The chart distinguishes semantic primes from their language-specific forms and illustrates constrained combinations. A list of labels alone is not mastery of that syntax.",
        "reproduction": "Bibliographic fields and short original summary only; chart not copied into the deliverable",
    },
}

# Order follows the Spanish table, not a DEE ranking. IDs are fixed to the
# English gloss slug; changing display spelling never changes identity.
GROUPS = [
    ("substantivos", [
        ("I", "yo", [], "yo"), ("YOU", "tú", [], "tu"),
        ("SOMEONE", "alguien", ["persona"], "alguien~persona"),
        ("SOMETHING", "algo", ["cosa"], "algo~cosa"),
        ("PEOPLE", "gente", [], "gente"), ("BODY", "cuerpo", [], "cuerpo")]),
    ("substantivos_relacionales", [
        ("KINDS", "tipos", [], "tipos"), ("PARTS", "partes", [], "partes")]),
    ("determinantes", [
        ("THIS", "esto", [], "esto"), ("THE_SAME", "lo mismo", [], "lo mismo"),
        ("OTHER", "otro", [], "otro")]),
    ("cuantificadores", [
        ("ONE", "uno", [], "uno"), ("TWO", "dos", [], "dos"),
        ("SOME", "algunos", [], "algunos"), ("ALL", "todo", [], "todo"),
        ("MUCH_MANY", "mucho", [], "mucho"), ("LITTLE_FEW", "poco", [], "poco")]),
    ("evaluadores", [("GOOD", "bueno", [], "bueno"), ("BAD", "malo", [], "malo")]),
    ("descriptores", [("BIG", "grande", [], "grande"), ("SMALL", "pequeño", [], "pequeño")]),
    ("predicados_mentales", [
        ("KNOW", "saber", [], "saber"), ("THINK", "pensar", [], "pensar"),
        ("WANT", "querer", [], "querer"), ("DONT_WANT", "no querer", [], "no querer"),
        ("FEEL", "sentir", [], "sentir"), ("SEE", "ver", [], "ver"),
        ("HEAR", "oír", [], "oír")]),
    ("habla", [("SAY", "decir", [], "decir"), ("WORDS", "palabras", [], "palabras"),
               ("TRUE", "verdad", [], "verdad")]),
    ("acciones_acontecimientos_movimiento", [
        ("DO", "hacer", [], "hacer"), ("HAPPEN", "pasar", [], "pasar"),
        ("MOVE", "moverse", [], "moverse")]),
    ("localizacion_existencia_especificacion", [
        ("BE_SOMEWHERE", "estar en algún lugar", [], "estar (en algún lugar)"),
        ("THERE_IS", "hay", [], "hay"),
        ("BE_SOMEONE_SOMETHING", "ser alguien o algo", [], "ser (alguien/algo)")]),
    ("posesion", [("IS_MINE", "es mío", [], "(es) mío")]),
    ("vida_muerte", [("LIVE", "vivir", [], "vivir"), ("DIE", "morir", [], "morir")]),
    ("tiempo", [
        ("WHEN_TIME", "cuándo", ["tiempo"], "cuándo~tiempo"),
        ("NOW", "ahora", [], "ahora"), ("BEFORE", "antes", [], "antes"),
        ("AFTER", "después", [], "después"),
        ("LONG_TIME", "mucho tiempo", [], "mucho tiempo"),
        ("SHORT_TIME", "poco tiempo", [], "poco tiempo"),
        ("FOR_SOME_TIME", "por un tiempo", [], "por un tiempo"),
        ("MOMENT", "momento", [], "momento")]),
    ("lugar", [
        ("WHERE_PLACE", "dónde", ["lugar"], "dónde~lugar"),
        ("HERE", "aquí", [], "aquí"), ("ABOVE", "arriba", [], "arriba"),
        ("BELOW", "debajo", [], "debajo"), ("NEAR", "cerca", [], "cerca"),
        ("FAR", "lejos", [], "lejos"), ("SIDE", "lado", [], "lado"),
        ("INSIDE", "dentro", [], "dentro"), ("TOUCH", "tocar", [], "tocar")]),
    ("conceptos_logicos", [
        ("NOT", "no", [], "no"), ("MAYBE", "tal vez", [], "tal vez"),
        ("CAN", "poder", [], "poder"), ("BECAUSE", "porque", [], "porque"),
        ("IF", "si", [], "si")]),
    ("intensificador_aumentador", [("VERY", "muy", [], "muy"), ("MORE", "más", [], "más")]),
    ("similitud", [("LIKE_AS", "como", [], "como")]),
]


def initial_statuses():
    result = {key: {"estado": "NO_COMPROBADO_EN_DEE", "evidencia": [], "alcance": None} for key in DIMENSIONS}
    result["interfaz_registrada"] = {"estado": "SOLO_FORMA_TEXTUAL_CATALOGADA", "evidencia": ["NSM_ES_DIAGRAM_2021", "NSM_ES_TABLE_2021"],
                                     "alcance": "Una etiqueta documental; no entrada física instalada ni semántica adquirida"}
    return result


def catalogue():
    entries = []
    for group, items in GROUPS:
        for english, form, variants, original in items:
            entry = {"id": "NSM65." + english, "orden_tabla": len(entries) + 1,
                     "glosa_inglesa_id": english, "grupo_documental": group,
                     "forma_es": form, "variantes_documentadas": variants, "forma_fuente": original,
                     "fuentes": ["NSM_ES_DIAGRAM_2021", "NSM_ES_TABLE_2021"],
                     "normalizacion_editorial": "Tilde española normalizada; fuente imprime tu" if english == "YOU" else None,
                     "dimensiones_independientes": initial_statuses(),
                     "advertencia": "La forma o una aproximación instrumental no prueban el significado humano completo propuesto por NSM"}
            entries.append(entry)
    assert len(entries) == 65 and len({x["id"] for x in entries}) == 65
    sources = deepcopy(SOURCES)
    for value in sources.values():
        local = value.get("local_artifact") or value.get("local_staging_only")
        if local and (ROOT / local).exists():
            value["sha256"] = hashlib.sha256((ROOT / local).read_bytes()).hexdigest()
    return {"schema": "CPC4.NSM65.documentary.v1", "catalogue_version": "2026-10-17.1",
            "generated_utc": datetime.now(timezone.utc).isoformat(), "count": len(entries),
            "source_scope": "Inventario lingüístico humano de referencia, no ontología impuesta al kernel ni65capacidades de DEE",
            "status_dimensions_independent": list(DIMENSIONS),
            "status_rule": "Cada dimensión necesita su propio contraste y evidencia; ninguna se deriva automáticamente de otra",
            "entries": entries, "sources": sources}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "NSM65_CATALOGO.json")
    args = parser.parse_args()
    if not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("CPC4 output must remain inside its own workspace")
    if args.output.exists():
        raise FileExistsError("Preserve a prior catalogue before regenerating")
    value = catalogue()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"entries": value["count"], "learned_native_claims": 0, "output": str(args.output.resolve())}))


if __name__ == "__main__":
    main()
