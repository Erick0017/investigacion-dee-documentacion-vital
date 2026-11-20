# MBP4 — paisaje plástico compartido e interacción entre organizaciones

Campaña: **continuación MBP4; no MBP5**  
Kernel: **DEE Universe v27 sin modificar**  
Producto: **DEE thinking 2.2.0**  
Padre canónico: `dfb25c87b14eeadb63a754583d3c9ced9d031a14098c8f5a5fa95f9ab8c025ee`

## Resultado ejecutivo

Se construyó y confirmó un aparato `source-supported/driven` en un único Runtime v27. El presupuesto añadido en T0 quedó fijo: un linaje móvil, dos fuentes persistentes y un portador finito de arranque. Después de T0 el host sólo avanzó, observó, guardó y creó forks diagnósticos. No se creó una fibra por experiencia ni se programaron llegadas sucesivas con `place_arrival`.

El mismo linaje completó seis ciclos nativos de acción y retorno. Su estado retenido y la respuesta de una consulta común recorrieron cuatro clases funcionales antes de coalescer por saturación:

| Exposiciones completadas | Estado retenido `s_reg` | Respuesta a consulta común |
|---:|---:|---:|
| 0 | 7 | 4007 |
| 1 | 7007 | 11007 |
| 2 | 14007 | 18007 |
| 3 | 19664 | 19664 |
| 4–6 | 19664 | 19664 |

La salida no se interpretó por el escalar aislado: la consulta física común produjo un portador downstream en otra posición y con dirección `[0,0,1]`; el valor retenido cambió esa consecuencia posterior. DenseSequential y Lazy produjeron RAW y clocks completos idénticos hasta el tercer ciclo (tick absoluto 128).

El mejor gate demostrado es **MBP4-SP9**. `SP10` fue ensayado y resultó negativo: el futuro diagonal conjunto apareció sólo durante el contacto B1–B2, pero es reducible al reductor vectorial/de carga del kernel; no es un futuro conjunto no aditivo.

## Aparato físico congelado

- Mundo: `N=47`, toroidal, restaurado de `OBP_FRESH_VALIDATED_T32.deetsnap`.
- Política móvil inicial: dirección `[1,0,0]`, carga 7.
- Fuente persistente sensora: dirección `[-1,0,1]`, carga 4000.
- Fuente persistente normalizadora: dirección `[1,0,-1]`, carga 3000.
- Periodo observado de oportunidades: 47 ticks, producido por recorrido toroidal y fuentes persistentes.
- Acción: `[0,0,1]`; el normalizador devuelve el linaje a `[1,0,0]`.
- Límite físico dominante: saturación en `P_KERNEL-1 = 19664`.

Las cargas y coordenadas son parámetros de este aparato finito, no categorías humanas ni límites universales de v27.

## Adquisición multiexposición e historia

La adquisición resolvió estados subumbral distinguibles antes de saturar: 4007, 11007 y 18007. El tercer ciclo llevó la consulta común a 19664; exposiciones posteriores coalescieron. Esto permite medir velocidad y capacidad sin reservar infraestructura nueva.

Para una variante ambiental congelada (`sensor=2000`, `normalizer=3000`), el linaje naïve necesitó cuatro ciclos para alcanzar 19664 y el linaje con dos experiencias previas necesitó dos. La historia ahorró dos ciclos causales en este umbral. Se clasifica como **adquisición dependiente de historia dentro del mismo mecanismo de carga compartida**, no como “aprender a aprender” general.

Los controles `NO_COUPLING`, `SHAM` y `ROUTE_CUT` no reprodujeron la secuencia FULL 7007→14007. El corte de retorno dejó la acción sin reinstanciar la política recurrente.

## Práctica, no-uso, interferencia y reaprendizaje

Las ramas matched partieron del mismo checkpoint después de dos exposiciones:

- `PRACTICE`: una exposición adicional saturó la respuesta en 19664; dos y tres adicionales no añadieron clases.
- `IDLE`: la consulta siguió dando 18007 después de 47, 94 y 188 ticks sin el acoplamiento.
- `NO_USE_ACTIVE`: con actividad ambiental remota, la misma respuesta 18007 persistió en los tres horizontes.
- `INTERFERENCE`: un portador contrarruta actuó sobre el mismo linaje; la acción pasó a `[-1,1,1]` con carga 18218 y la firma A dejó de ser accesible durante el horizonte congelado.

El tiempo/no-uso y la interferencia no produjeron el mismo resultado. No se demostró borrado microscópico: el resultado se clasifica como **inaccesibilidad por desplazamiento de ruta**. Tampoco se demostró recuperación espontánea ni `RELEARNING_SAVINGS`: `L_acquire` quedó resuelto, pero `L_reacquire` no fue finito dentro del horizonte preregistrado. Por ello `SP5` queda **PARTIAL**, no PASS.

## Capacidad e interferencia

`C_shared(k)` contiene cuatro clases de respuesta distinguibles, incluida la basal, y una profundidad de exposición funcional observada `K*=3` antes de la coalescencia. No son tres recuerdos independientes ni bits. La frontera se debe a la saturación de carga del linaje compartido; añadir más exposiciones ya no cambia la consulta congelada.

La práctica consolida únicamente hasta esa frontera. La interferencia de ruta puede volver inaccesible la función aunque el tiempo o la actividad remota no lo hagan. No se construyó una matriz de memorias independientes porque eso habría reintroducido el diseño por fibras que esta campaña debía evitar.

## Observación móvil y atlas causal 2.0

El observador relacional predijo posición toroidal, dirección y carga en cada acción/retorno. Las seis vueltas coincidieron exactamente. Las coordenadas iniciales quedaron vacías mientras el linaje siguió funcional; un lector fijo habría producido falsos negativos.

El atlas congelado cubrió exhaustivamente su dominio declarado:

- estados tras 0, 1, 2, 3 y 6 exposiciones;
- sensores con cargas 1000, 2000 y 4000;
- un sham ortogonal;
- horizontes 1 y 8.

X1 y X2 añadieron clases downstream específicas y sustituyeron las basales. En X3 y X6 las variantes de carga coalescieron en 19664, aunque la dirección ortogonal siguió distinguiendo ruta. El grafo causal confirmado es:

`fuente sensora → onda sensora → política móvil → ACTION0 → onda normalizadora → política actualizada → nueva oportunidad`.

El full-state pertenece al observador científico. Nada de ese estado se copió como entrada nativa.

## Continuidad histórica de la sección 18

El checkpoint histórico se verificó en tick 78 con SHA-256 `cba13f5fa58b2fef02a1cf4c170ab1555efde4467341ba4a99dc6f2046cd7cee`. Sus cuatro linajes entregados `s_reg=812`, dirección B, persistieron mientras el nuevo aparato completó tres ciclos. Sin embargo, el nuevo linaje recorrió exactamente 7007→14007→19664, igual que en fresh. No apareció una ruta causal desde las cuatro fibras históricas hacia el landscape compartido.

Clasificación: **HISTORY_PRESERVED_BUT_NOT_COUPLED_TO_SHARED_LANDSCAPE**.

## B1 + B2

B2 fue validada separadamente en un marco B real: dos retornos conservaron dirección `[0,1,0]`. En el mundo conjunto, B1 y B2 mantuvieron identidades separables hasta el tick relativo 19. En el tick 20 ambas rutas alcanzaron el mismo sitio por dinámica v27:

- B1 sola: `[1,0,0]`, carga 7007.
- B2 desplazada un plano (`SPATIAL_SHAM`): B1 permanece `[1,0,0]`, 7007.
- B1+B2 en contacto: descendiente `[1,1,0]`, 14014.
- B1 sin la carga histórica previa + B2: descendiente `[1,1,0]`, 7014.

El contacto físico cambia los futuros de ambas organizaciones y la historia previa de B1 cambia la carga del descendiente y de la consulta posterior. Esto sostiene `SP9` dentro del dominio de un contacto nativo. Después del contacto las identidades separadas se fusionan; no se demostró un lazo recíproco repetido, comunicación, enseñanza ni que B1 cambie la velocidad de adquisición de B2.

Existe una trayectoria diagonal ausente en los mundos aislados, pero su dirección y carga son la reducción simétrica aditiva de v27. Por el criterio preregistrado, **no** se promueve `SP10`.

## Respuestas directas

1. **¿Las experiencias modifican un landscape compartido?** Sí, un único linaje y las mismas fuentes cambian la respuesta posterior hasta saturación.
2. **¿La historia cambia una experiencia posterior?** Sí; la variante nueva alcanza el umbral en 2 ciclos desde historia previa frente a 4 desde naïve.
3. **¿La adquisición requiere múltiples encuentros?** Sí, las clases subumbral preceden a la clase saturada.
4. **¿Práctica difiere de no-uso?** Sí; práctica satura, no-uso conserva 18007.
5. **¿Tiempo e interferencia son iguales?** No; idle/no-uso retienen, la contrarruta vuelve inaccesible la función A.
6. **¿Hubo pérdida parcial?** Hubo pérdida de accesibilidad funcional por ruta; no se demostró destrucción del estado histórico.
7. **¿Hubo recuperación sin reaprender?** No en la rama interferida; las ramas de no-uso nunca perdieron acceso.
8. **¿Hubo savings?** No demostrado; `L_reacquire` quedó fuera del horizonte finito.
9. **¿Capacidad observada?** Cuatro clases de consulta, `K*=3` de profundidad de exposición antes de coalescer.
10. **¿Causa de saturación?** El límite `P_KERNEL-1` del registro transportado en este aparato.
11. **¿Qué interfiere?** La contrarruta causal; actividad remota matched no interfiere.
12. **¿Qué se integra?** Exposiciones repetidas se integran acumulativamente en el mismo linaje hasta coalescer; no se obtuvieron memorias independientes.
13. **¿Cómo cambia el landscape?** Aparecen nuevas clases downstream y luego se pierden distinciones por saturación.
14. **¿Los observadores móviles evitan falsos negativos?** Sí, siguieron exactamente seis vueltas donde la coordenada fija ya no contenía el linaje.
15. **¿Puede moverse sin perder seguimiento?** Sí, dentro del dominio toroidal congelado.
16. **¿Influye la sección 18?** No; se preserva, pero no se acopla funcionalmente.
17. **¿B1 modifica B2 y viceversa?** El contacto modifica el futuro de ambos; no se probó influencia repetida mediada por ambiente.
18. **¿Una cambia la velocidad de aprendizaje de la otra?** No ensayado con adjudicación suficiente.
19. **¿Hay un futuro conjunto ausente en aislados?** Hay una ruta diagonal nueva, pero es aditiva; `NON_ADDITIVE_JOINT_FUTURE` no demostrado.
20. **Gate más alto:** `MBP4-SP9 PASS`; `SP10 FAIL`.

## Checkpoints y reproducibilidad

Se conservaron `FRESH_SHARED_T0`, `FRESH_SHARED_VALIDATED`, `POST_ACQUISITION`, `POST_INTERFERENCE`, `POST_RELEARNING`, `B1_B2_PRE_CONTACT`, `B1_B2_POST_CONTACT` y `MAIN_FINAL`. El MAIN científico es fresh compartido; la rama histórica queda como comparación negativa de acoplamiento. `MAIN_FINAL.deetsnap` termina en tick 269 y conserva la genealogía de seis exposiciones.

Los runners exactos, locks, telemetría, atlas, controles, hashes y verificación del paquete están en esta sección. Las secciones 00–18 permanecen byte-idénticas por contenido respecto del ZIP padre.

## Clasificación epistemológica

- **Hecho computacional:** resultados, snapshots, igualdad Dense/Lazy, hashes y trazas.
- **Mecanismo DEE:** propagación, reducción direccional, transporte de carga, acción y retorno bajo v27.
- **Inferencia funcional:** la historia cambia una consecuencia física posterior y una latencia de umbral.
- **Hipótesis:** otros landscapes compartidos podrían soportar memorias no escalares o recuperación; no se demostró aquí.
- **Analogía:** práctica, olvido y reaprendizaje son nombres operacionales de ramas, no equivalencias psicológicas.
- **Posible isomorfismo futuro:** curvas de retención, saturación e interferencia; queda fuera de esta campaña.
