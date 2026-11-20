"""Documentary NSM65 plan from the frozen inherited catalogue; no evolution.

This script deliberately cannot set trained/retained/used states. Scientific
evidence is attached later by the auditor from new primary measurements.
"""
from pathlib import Path
import argparse
import hashlib
import json

EXT = Path(__file__).resolve().parents[1]
BASE = EXT.parents[1]

GROUPS = {
 'substantivos': ('Participante o soporte conservado bajo cambios de contexto',
     ['referente', 'emisor', 'destinatario', 'contexto'],
     'Contrastar un referente accesible con otro y cambiar emisor/destinatario sin cambiar el código de consulta'),
 'substantivos_relacionales': ('Pertenencia funcional a una clase o dependencia de una parte del conjunto',
     ['componente', 'conjunto', 'función', 'contexto'],
     'Cambiar soporte manteniendo función y retirar una parte con sham que preserve inventario pertinente'),
 'determinantes': ('Referencia conservada, identidad funcional y cambio de referente',
     ['referente_1', 'referente_2', 'historia', 'interfaz'],
     'Comparar mismo referente transformado con distinto referente de señal semejante; no identidad por coordenada'),
 'cuantificadores': ('Multiplicidad accesible mediante contribuciones físicamente diferenciadas',
     ['contribuciones', 'destinos', 'ventana', 'saturación'],
     'Variar número preservando carga total y variar carga preservando número; no equiparar suma escalar a cantidad universal'),
 'evaluadores': ('Consecuencia relativa a una función declarada y contexto',
     ['acontecimiento', 'acción', 'función', 'contexto'],
     'La misma contribución tiene diferente consecuencia medida al cambiar contexto; igual información disponible'),
 'descriptores': ('Comparación de una extensión o respuesta física definida',
     ['objeto_1', 'objeto_2', 'coordenada_medida', 'contexto'],
     'Variar soporte, escala y carga por separado; comprobar qué observable realmente ordena las respuestas'),
 'predicados_mentales': ('Disponibilidad o uso operacional de información, sin atribución fenomenológica',
     ['participante', 'información', 'canal', 'consecuencia'],
     'Contrastar historia pertinente, omisión y acceso; una etiqueta del auditor no es un estado subjetivo acreditado'),
 'habla': ('Emisión física, recepción y uso dependiente de experiencia',
     ['emisor', 'destinatario', 'mensaje', 'convención', 'contexto'],
     'Invertir historias con codificador fijo; cortar canal; probar nueva consulta y situación que produzca emisión'),
 'acciones_acontecimientos_movimiento': ('Contribución propia frente a acontecimiento y transporte observado',
     ['actor', 'acción', 'objeto', 'resultado', 'instante'],
     'Igualar acontecimiento sensorial con/sin contribución nativa; variar dirección y ruta conservando inventario'),
 'localizacion_existencia_especificacion': ('Presencia, acceso e identificación de soporte en un dominio explícito',
     ['referente', 'región', 'acceso', 'ventana'],
     'Variar referente y contexto; separar ausencia física, puerto ocupado, silencio y lectura fuera de fase'),
 'posesion': ('Disponibilidad relacional de un recurso para un participante',
     ['participante', 'recurso', 'ruta_de_acceso', 'otro_participante'],
     'Cambiar acceso sin cambiar la etiqueta del recurso; probar quién puede utilizarlo en el estado actual'),
 'vida_muerte': ('Continuidad o pérdida de una función operacional finita',
     ['organización', 'soporte', 'función', 'horizonte'],
     'Conservar función tras perturbación y contrastar pérdida localizada; no equivalencia biológica por nombre'),
 'tiempo': ('Orden o intervalo de acontecimientos accesibles y utilización posterior',
     ['acontecimiento_1', 'acontecimiento_2', 'orden', 'intervalo', 'contexto'],
     'Mismo inventario y orden invertido; nuevos referentes e intervalos; no enviar el bit de orden desde el host'),
 'lugar': ('Relación espacial en un marco declarado conservando papeles',
     ['referente', 'marco', 'origen', 'destino', 'ruta'],
     'Trasladar el conjunto y variar referente; separar cambio de lectura de cambio de relación; respetar toro'),
 'conceptos_logicos': ('Ausencia, posibilidad, dependencia o condición en un dominio de operaciones físicas',
     ['contenido', 'operación', 'alternativa', 'contexto', 'consecuencia'],
     'Probar más de un contenido y controles de acceso; timeout del host no es negación o incertidumbre nativa'),
 'intensificador_aumentador': ('Cambio relativo de una magnitud funcional conservando la dimensión medida',
     ['referencia', 'magnitud', 'comparador', 'contexto'],
     'Separar carga, número de contribuciones y consecuencia; no una escala semántica universal por s_reg'),
 'similitud': ('Equivalencia o diferencia funcional bajo un panel y contexto determinados',
     ['estado_1', 'estado_2', 'panel', 'contexto'],
     'Estados de soporte distinto con firma común y estados de soporte igual con función distinta en reservas')
}

SPECIFIC = {
 'I': 'El referente de la misma forma debe cambiar con quien emite y con destinatario actual; incluir tercer interlocutor.',
 'YOU': 'El referente de la misma forma debe seguir al destinatario actual, no al ID fijo B ni a cualquier otro.',
 'BEFORE': 'Presentar acontecimientos sin etiqueta de orden; variar identidades e intervalos; reservar R(A,B) frente a R(B,A).',
 'AFTER': 'Usar el mismo inventario e invertir orden accesible; comprobar consulta posterior sin reenseñar el resultado.',
 'THE_SAME': 'Conservar identidad funcional bajo cambio de soporte y distinguir igualdad de señal de identidad de participante.',
 'OTHER': 'Cambiar referente conservando rasgos; probar que no se reduce a coordenada ni al signo contrario.',
 'THERE_IS': 'Probar varios referentes y condiciones de acceso; dominio y ventana explícitos, sin convertir silencio instrumental en ausencia.',
 'NOT': 'Aplicar el contraste a más de un contenido y separar una ausencia concreta de una operación de negación general.',
 'GOOD': 'Una consecuencia conserva una función en un contexto y no en otro; registrar la función y el cambio de contexto.',
 'BAD': 'Valorar por consecuencia medida y contexto, no fijar universalmente una carga como perjudicial.',
 'DO': 'Comparar consecuencia de una acción nativa con acontecimiento igual sin contribución del actor.',
 'HAPPEN': 'Comparar acontecimiento observado con acción propia manteniendo iguales consecuencias sensoriales cuando sea viable.',
 'KNOW': 'Ensayo operacional de información conservada y utilizable ante consulta nueva; sin equivalencia fenomenológica.',
 'THINK': 'Ensayo de transformación interna con consecuencia posterior y control de estímulos; no mera etiqueta de actividad.',
 'FEEL': 'No se acredita experiencia subjetiva por score; sólo se registra eventual respuesta operacional con su dominio.'
}


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=EXT / 'revision/NSM65_PLAN.json')
    args = p.parse_args()
    source = BASE / 'referencias/NSM65_CATALOGO_CPC4.json'
    catalogue = json.loads(source.read_text(encoding='utf-8'))
    entries = []
    for row in catalogue['entries']:
        title, participants, test = GROUPS[row['grupo_documental']]
        gloss = row['glosa_inglesa_id']
        entries.append({
            'id': row['id'], 'forma_es': row['forma_es'],
            'variantes_documentadas': row['variantes_documentadas'],
            'grupo_documental': row['grupo_documental'],
            'significado_propuesto_en_inventario': {'english_prime_identifier': gloss,
                'spanish_exponent': row['forma_fuente'],
                'definition_scope': 'Referencia lingüística heredada; no se reemplaza la definición NSM por el ensayo DEE'},
            'fuentes': row['fuentes'],
            'estado_anterior_literal': row['dimensiones_independientes'],
            'version_operacional_propuesta': title,
            'participantes_y_relaciones_a_conservar': participants,
            'experiencias_propuestas': SPECIFIC.get(gloss, test),
            'senal_fisica': {'estado': 'POR_SELECCIONAR_SEGUN_MECANISMO',
                'fixed_encoder_required': True, 'signal_is_not_semantic_solution': True},
            'preparacion': 'Declara geometría, interfaces, recursos, lectores y oportunidades; no incluye la respuesta reservada',
            'debe_adquirirse': 'Correspondencia funcional dependiente de interacciones reales; comparar historias con interfaces idénticas',
            'retencion': {'estado': 'PLANIFICADO', 'prueba': 'Consulta anterior tras experiencia nueva y espera sin reenseñanza'},
            'generalizacion_reservada': {'estado': 'PLANIFICADO', 'prueba': test},
            'uso_comunicativo': {'estado': 'PLANIFICADO', 'prueba': 'El emisor responde desde su estado; portador llega y altera uso del receptor en el mismo Runtime'},
            'composicion': {'estado': 'PLANIFICADO', 'prueba': 'Relaciones adquiridas separadamente; combinación y papeles no enseñados completos'},
            'emision_situacion_a_forma': {'estado': 'PLANIFICADO', 'prueba': 'Situación sin señal de consulta provoca emisión físicamente identificable'},
            'evidencia_nueva': [], 'estado_ejecucion_ampliacion': 'PLANIFICADO',
            'scientific_claim_rule': 'Ningún campo de este plan acredita entrenamiento, retención, uso o significado completo'} )
    assert len(entries) == 65 and len({r['id'] for r in entries}) == 65
    result = {'schema': 'CPC5.extension.NSM65-plan.v1', 'registered_entries': 65,
        'source': 'CPC5/referencias/NSM65_CATALOGO_CPC4.json', 'source_sha256': sha(source),
        'source_catalogue_version': catalogue['catalogue_version'], 'sources_inherited': catalogue['sources'],
        'plan_only': True, 'new_semantics_claimed_by_plan': 0,
        'statement': 'Plan documental completo. Los estados de evidencia se calculan aparte de las mediciones primarias.',
        'entries': entries}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'entries': len(entries), 'output': str(args.output), 'sha256': sha(args.output)}))


if __name__ == '__main__': main()
