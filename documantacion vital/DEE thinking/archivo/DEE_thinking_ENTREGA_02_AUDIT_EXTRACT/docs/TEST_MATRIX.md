# Matriz de pruebas

Esta matriz define cobertura y criterio. El estado efectivo de una ejecución se
obtiene de CTest y de los logs bajo `validation/`; una fila no se considera
aprobada por aparecer aquí.

Targets CTest configurados:

El CMake vigente declara 13 targets. El resumen bajo `validation/` todavía
corresponde a la matriz anterior de 12; la presencia en esta tabla no sustituye
la repetición de la corrida integrada.

| Target | Cobertura principal |
|---|---|
| `kernel_whl_differential` | Fixtures exactos RAW/clock del WHL |
| `runtime_contract` | Semántica temporal, eventos, aislamiento y snapshot |
| `reference_organizations` | Familias E1–E4 y sus controles |
| `execution_backends` | Equivalencia por tick denso/Lazy/paralelo 1/2/4 y repeticiones |
| `integration_persistence` | Snapshot v2, snapshot v1 real con evento pendiente, sustitución y cambio de backend |
| `composition_catalog` | Siete familias, contratos, diagnósticos y composiciones A/B |
| `composition_snapshot_restore` | Restauración autocontenida, continuidad futura y rechazo de v1/receta/manifiesto incompatibles |
| `composition_a_e2e` | Aprendizaje, actualización, consultas y respuesta reservada |
| `composition_b_e2e` | Contexto distribuido, historia y multicanal |
| `independent_consumer_e2e` | Uso externo sólo mediante API pública |
| `examples_smoke` | Ejecución de los ejemplos entregados |
| `catalog_transport_e2e` | Selección e instanciación de transporte mediante catálogo |
| `composition_c6_later_query_e2e` | Entrada nueva después de avanzar el mismo mundo |

## Núcleo y comparación diferencial

| ID | Propiedad | Comparación exigida |
|---|---|---|
| K01 | Packing/decoding | Palabra exacta y campos completos |
| K02 | Dirección con signo | `[-8,7]` en cada nibble, sin normalización externa |
| K03 | Transporte y wrapping | RAW y clock completos en varios ticks |
| K04 | `state=0` frente a `raw=0` | Trayectorias diferentes cuando el resto de RAW es causal |
| K05 | Semántica 4 | Persistencia RAW y actualización exacta de clock |
| K06 | Destino vacío/ocupado | Prioridad de rama y no escritura ingenua sobre ocupado |
| K07 | Integración simultánea | Resultado completo de una coincidencia multifuente |
| K08 | Composición por etapas | Contraste con integración simultánea; sin asumir asociatividad |
| K09 | Límite escalar | Cap del reducer sin invalidar el rango representable de `s_reg` |
| K10 | DEMUX alcanzable | Fixture primario y RAW/clock exactos |
| K11 | Clocks no uniformes | Aritmética modular y ramas dependientes de fase |
| K12 | Prioridad de ramas | Caso donde más de una condición superficial parece aplicable |
| K13 | Cuatro buffers | Copia final exacta, sin swap adicional ni alias |
| K14 | Trayectorias reservadas | Estados no vacíos generados por el WHL, no por la biblioteca bajo prueba |
| K15 | Agenda Lazy | RAW no nulo + halo, clocks completos, postpaso DEMUX y backend realmente usado |
| K16 | Paralelo | 1/2/4 hilos, trabajo no uniforme y repeticiones sin divergencia por intercalado |

Los fixtures diferenciales deben contener estado inicial y salida WHL completa.
Igualdad de ocupación, suma de cargas o dirección no sustituye igualdad byte a
byte de RAW y clock.

## Runtime

| ID | Propiedad | Criterio |
|---|---|---|
| R01 | `advance(n)` | Igual a `n` llamadas `advance(1)` |
| R02 | Ejecución por bloques | Igual a ejecución continua con la misma agenda |
| R03 | `advance(0)` | No aplica eventos ni cambia ningún estado observable |
| R04 | `run_until(T)` | Termina antes de aplicar eventos de frontera `T` |
| R05 | Pausa/reanudación | Pausa bloquea avance positivo; reanudar no modifica estado |
| R06 | Admisión diferida | Ocupación se comprueba en la frontera efectiva |
| R07 | Clock en entrada | Se conserva el clock completo del sitio |
| R08 | Eventos simultáneos | Conflicto explícito; nunca última escritura gana |
| R09 | Lote atómico | Un lote inválido/conflictivo no deja aplicación parcial |
| R10 | Tardíos/inválidos | Recibos con motivo y sin modificación del mundo |
| R11 | Observación repetida | RAW, clock, tick, cola y recibos permanecen idénticos |
| R12 | Probe | Recibo `Probe`, intervención declarada y canal autorizado |
| R13 | Fork | Continuaciones no comparten memoria mutable |
| R14 | Dos mundos | Ausencia de contaminación global |
| R15 | Snapshot pendiente | Cola, orden, canales, fase y estado sobreviven |
| R16 | Futuro restaurado | RAW/clock futuros iguales a continuación no interrumpida |
| R17 | Restauración fallida | Corrupción/truncamiento no altera la instancia receptora |
| R18 | Límites | Dimensión, cola, strings, conteos y tamaño inválidos se rechazan |
| R19 | Sin Python | Consumidor funciona sin importar ni lanzar Python |
| R20 | Backend en frontera | Cambio explícito entre ticks; misma continuación RAW/clock |
| R21 | Snapshot v1 real | Archivo escrito por Entrega 01, evento t5 pendiente y futuro exacto |
| R22 | Snapshot v2 | Metadatos/composición/configuración sobreviven sin ejecutar código |
| R23 | Publicación fallida | Destino anterior sigue siendo un snapshot legible |
| R24 | Restore compuesto v2 | Receta reconstruye organizaciones, conexiones, `purpose`, landmarks y futuro sin planner del consumidor |
| R25 | Separación legacy | v1 sigue cargando como `Runtime`, pero `ComposedWorld::load_snapshot` lo rechaza por carecer de receta |

## Organizaciones y extremo a extremo

| ID | Familia | Contraste mínimo |
|---|---|---|
| E101 | Transporte | Carga no cero, carga cero, ausencia y destino ocupado |
| E201 | Reprogramación | Escritura presente frente a teacher/enlace omitido |
| E301 | Historia | HA/HB/H0 a edad común y consulta común |
| E302 | Fondo temporal | Efecto de consulta frente al mismo fondo sin consulta |
| E401 | Multicanal | AB/ABC y control de inventario cuando corresponda |
| E402 | Recurrencia | Enlace intacto frente a corte/sham con suministro conservado |
| E2E1 | Consumidor | Crear, experimentar, avanzar, observar, segunda entrada, guardar, restaurar y continuar |
| E2E2 | Control no favorable | El consumidor no imprime siempre la misma respuesta |
| C201 | Catálogo | Parámetros/rangos, footprint/relación/read/context/horizonte, presupuesto y capacidad pendiente son públicos y coherentes |
| C202 | Conexión | Tipo, geometría y ruta incompatibles impiden construir |
| C203 | Composición A | Intacto, marcador omitido, no-update, no-learning, corte y valor reservado sobre el mismo aparato C7 |
| C204 | Composición B | HA/HB, B ausente/carga cero, corte, sham de trayectoria paralela y lectura común |
| C205 | C6 separado | Consulta C6H01 solicitada en t6 después de avanzar; no se usa como sustituto de A |
| C206 | Contexto | Scaffold distribuido permanece en el mundo compuesto y afecta el testigo |

## Benchmark técnico

El ejecutable de benchmark mantiene 63 filas comparables del kernel (tres
estados × siete configuraciones × tres repeticiones) y registra por separado:
agenda del evento, pared de la frontera de aplicación, tiempo interno del
kernel, estimación etiquetada del coste de aplicación/wrapper, observaciones,
save, restore y total end-to-end. `validation/backend_benchmark.json` debe
regenerarse antes de atribuir valores a los campos añadidos recientemente.

## Errores históricos convertidos en contrato

| ID | Regresión o restricción |
|---|---|
| H01 | Entradas posteriores no escriben clock |
| H02 | No se añade swap al copy-back histórico |
| H03 | Métricas separan soporte RAW, ocupación y carga |
| H04 | Carga cero y ausencia son casos distintos |
| H05 | Una llegada a ocupado no se trata como escritura garantizada |
| H06 | Reducciones por etapas no se suponen asociativas |
| H07 | Un sham se analiza por trayectoria, no sólo posición inicial |
| H08 | La identidad operacional de la señal no cambia entre entrenamiento y consulta |
| H09 | No se instancia un controlador nuevo por muestra y se llama reutilización |
| H10 | Se controla evolución libre a la misma edad |
| H11 | Alcanzar el cap no se rotula regeneración/aprendizaje |
| H12 | Se distingue proyección igual de estado causal igual |
| H13 | Receptor/lector queda fijado antes del tratamiento |
| H14 | Pilotos, copias y checkpoints no cuentan como réplicas independientes |
| H15 | Consultas transformativas no se documentan como observación pasiva |

## Criterio técnico

Sólo el conjunto de logs de compilación, enlace, CTest, consumidor limpio,
comparación WHL y extracción/reconstrucción de paquete permite decidir el estado
técnico. Una prueba omitida o deshabilitada queda pendiente. Una discrepancia
exacta no se convierte en tolerancia para obtener un resultado verde.
