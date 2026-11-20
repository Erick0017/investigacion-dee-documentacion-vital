# Composición física ordenada adquirida

Dos relaciones móviles adquiridas conservan una diferencia de dirección que una
lectura escalar pierde. En el par de igual inventario, AB y BA producen ambos
`s_reg=39` después del segundo encuentro, pero sus direcciones son `(0,1,0)` y
`(1,1,0)`. Esa diferencia produce contactos distintos con dos paquetes ambientales
iguales: AB forma46 en el bancoV; BA forma46 en el bancoD.

El código publicado prepara rutas y tiempos. No infiere desde fuera qué ocurrió
antes. Ambas relaciones se forman por experiencias efectivamente admitidas:
cue `(0,-1,0)` y acontecimiento `(±1,1,0)` generan el portador `(±1,0,0)`.
La consulta común es `(1,1,0)`. No hay RAW entrenado inicialmente.

## Mecanismo y controles

Cada encuentro simultáneo usa el mismo reductor conmutativo v27. Normalizar cada
componente por signo entre encuentros hace no conmutativa su composición:

`sign(sign(v+A)+B) != sign(sign(v+B)+A)` para este conjunto de vectores.

Esto describe una operación física ordenada y preparada; no acredita una relación
abstracta ANTES/DESPUÉS, pronombres ni gramática general.

- Omitir/desacoplar/invertir A en AB conserva a veces la dirección vertical, pero
  cambia la carga final de39 a27 y la consecuencia de46 a34. Dirección sola no
  acredita que ambas contribuciones estuvieran presentes.
- Omitir A en BA deja27 vertical y ninguno de los bancos alcanza46. Así se localiza
  la función del segundo giro en esa preparación.
- Cortar sólo el producto ya formado, en t12, deja14 o12 en el segundo encuentro y
  bancos7/7. El sham conserva39 y46. Los respaldos adquiridos siguen consultables;
  el corte no destruye toda capacidad perceptiva o de respuesta.
- Reservas con nuevas cargas y traslación conservan la transformación ordenada:
  AB produce55 y contacto62; BA45 y contacto52.
- Dos respaldos aprendidos mediante exposiciones propias responden21/23 en t70.
  Tras cargar el estado t73 en otro proceso, esperar y consultar con una carga
  nueva11, responden32/34 en t137 sin reenseñanza.

Los recursos son cuatro componentes, ocho entradas de adquisición, una consulta
común, dos contactos ambientales y dos consultas a respaldos. La redundancia no
es una copia gratuita. La continuación introduce otras dos consultas y mantiene
sus recibos, clocks, interfaces y estado anterior.

## Evidencia y reconstrucción

[ORDERED_COMPOSITION.json](ORDERED_COMPOSITION.json) enlaza los13registros primarios:
dos discovery, ocho controles congelados, dos reservas y un contraste exploratorio
identificado después de examinar el contraejemplo de AB sin A. La continuación es
otro registro de trayectoria, no otra preparación independiente.

[ORDERED_TRANSITION_RECONSTRUCTION.json](ORDERED_TRANSITION_RECONSTRUCTION.json)
reconstruye26transiciones desde Moore27 completos. El auditor excluye las guardas
previas de cristalización y XNOR, enumera fuentes direccionales entrantes y compara
estado, semantic, carga, dirección y clock con el postestado observado. Todas las
comparaciones de campo coinciden. Estas fórmulas se ejecutan después y nunca
alimentan al participante. El inspector pasivo original conserva su declaración
`VOID_PRECEDENCE_UNRESOLVED`; la reconstrucción adicional no se presenta como una
capacidad oculta de ese inspector.

Los datos están en `../resultados/ordered_discovery/`, `ordered_confirmation/`,
`ordered_localization/` y `ordered_continuation/`. Preestados, postestados,
vecindarios, entradas, recibos, intervenciones y snapshots permanecen disponibles.

## Incidencias conservadas

El primer AB completó la física pero su assert de metadata comparaba tuplas de
Python con listas restauradas de JSON. RAW/clocks y canales/recibos coincidían.
Se conserva el resultado original y el código v1; `TECHNICAL_REANALYSIS.json`
verifica el namespace serializado real sin repetir la trayectoria ni alterar
expectativas. Una etiqueta manual de hora del JSON de confirmación también se
conserva con errata: la identidad y el orden se verifican por hash y registros del
supervisor, no por ese reloj editorial.
