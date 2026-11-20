# Reserva R07: corrección espacial y contraste causal

La revisión independiente no avanzó DEE ni editó primarios. Fuente: las cuatro
vidas `MA02_R07_RES_*.R07.json.gz`, originadas en el mismo snapshot completo
MA02_MAIN T2486. Recálculo: `recalculo/recalcular_reserva_r07.py`; referencia en
`evidencia/campanas/MENTE_ACUMULATIVA_R02/cierre/RECALCULO_RESERVA_R07.json`.

## Corrección del instrumento, no de la física

El exportador ejecutado asignó a los registros globales la coordenada
`[k%N,(k//N)%N,k//N²]`. El índice nativo es `(x*N+y)*N+z`: esos registros requieren
intercambiar X y Z. El recálculo conserva sus bytes originales y aplica esa
transposición únicamente a `frames_global_sparse[*].nonzero_raw[*].site`.
No afecta los sitios obtenidos mediante `observe`, paneles o corte diagnóstico.

Desde cada lista corregida se reconstruyó el vector RAW completo, incluidos
los ceros implícitos. Sus316 hashes coinciden exactamente con los316 hashes
originales del array completo:79 ticks por rama,2613–2691 sin huecos. También
coinciden los RAW de los gates con su observación local independiente. Los
clocks de sitios RAW0 no se publicaron individualmente: no se reconstruyen;
se conservan sus hashes globales y los snapshots completos locales.

## Retorno observado y uso causal

La contribución ya formada enT2622, sitio(33,33,27), dirección(−1,0,−1) y
carga270, aparece en cada tick hastaT2688 en la siguiente posición predicha
por su dirección. Su RAW sólo aparece una vez en el registro global de cada
uno de esos ticks. Se observan dos cruces periódicos distintos:

| Tick | De | A | Frontera |
|---:|---|---|---|
|2650|(6,33,0)|(5,33,66)|Z|
|2656|(0,33,61)|(66,33,60)|X|

EnT2688 llegan al mismo sitio de encuentro tres contribuciones observadas:

| Posición previa | Dirección | Carga |
|---|---|---:|
|(34,33,28)|(−1,0,−1)|270|
|(33,34,28)|(0,−1,−1)|439|
|(32,32,27)|(1,1,0)|7|

EnT2689,67 ticks después de la primera formación, el sitio(33,33,27) contiene
un nuevo producto de carga716 y dirección Z− pura. Se conservan los tres
antecedentes: no se inventa una identidad única del producto combinado.

El corte externo de la primera contribución enT2622 modifica sólo ese RAW y
conserva el hash global de clocks en ese momento. Antes del corte, sus hashes
RAW/clocks coinciden con CONCORDANT. El sham conserva el registro y coincide
con CONCORDANT en ambos hashes durante los79 ticks. El gate reservado emite−
en CONCORDANT y SHAM; no emite una respuesta válida en CUT. Esto respalda la
relevancia causal del retorno particular, no que toda recurrencia sea memoria.

## Corrección de los denominadores de enseñanza

Las cuatro ramas solicitaron tres entradas de revisión beta enT2546. La dosis
realizada **no está emparejada**: CONCORDANT/CUT/SHAM admitieron2/3 y rechazaron
la contribución axial que coincidía con el portador anterior; MIXED admitió3/3.
Las cargas posteriores fueron420 y431, respectivamente. Por tanto, MIXED
contrasta historias físicas diferentes pero no aísla únicamente el signo con
la misma dosis admitida. No invalida el contraste CUT/SHAM, que comparte la
misma historia de adquisición y difiere en el corte posterior selectivo.

## Ganancia y coste funcional

Las cuatro ramas conservaron uso posterior de gamma+ y delta−. Alfa no produjo
una respuesta válida aunque su petición entró; beta no la produjo con una
petición rechazada por ocupación. No se atribuyen ambos fallos a la misma causa
ni se declara destrucción global de esas memorias.

La combinación es preparada, acotada y parcialmente destructiva. El circuito,
sus consultas, recursos y calendario pertenecen al investigador; los contenidos,
su transporte y el producto pertenecen a la evolución física documentada. No
demuestra conjunción semántica aprendida, selección P2/R2, iniciativa autónoma
ni que el E1 histórico haya adquirido esta nueva preparación N67.

El recálculo portable desde otra ubicación reprodujo exactamente la referencia,
SHA-256 `4b79a85e981520ed466032d99d94d1f2f060ac9c501d7811b3bff38db5a5c3fd`.
Esta comprobación es de los registros archivados, no una segunda ejecución
nativa ni una réplica independiente de aprendizaje.
