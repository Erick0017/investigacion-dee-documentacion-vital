# Auditoría de interferencias y pérdida de acceso K65

## Qué se contó

Fuente central: `resultados/continuacion/E1_MAIN_K65_1907_2353/MEDICIONES.json`
del ZIP CPC9, SHA-256
`eddf877a8db828cd1b20e3627753dcb727aa579f50c4867d69aa9fed4cc5180f`.
El índice enlaza ese archivo con el documento reducido D00030.

Una lectura se califica con el decoder congelado:
`active AND semantic==1 AND direction==expected_auditor_direction`.
No se cambia ese criterio para convertir fallos en aciertos. `semantic` es
un campo del kernel, no una medida de significado lingüístico.

Las 60/65 primeras respuestas se agregan entre los aprendizajes por bloques.
No son un repertorio de 60 relaciones semánticas simultáneas. Después de adquirir
todos los bloques, cada barrido completo reúne una lectura de cada forma en
cuatro ticks distintos:

| Ventana | Bancos, numeradores/denominadores | Total |
|---|---|---:|
| T2180–2219 | 6/8 + 6/8 + 15/16 + 30/33 | 57/65 |
| T2247–2286 | 7/8 + 5/8 + 14/16 + 27/33 | 53/65 |
| T2314–2353 | 4/8 + 0/8 + 0/16 + 0/33 | 4/65 |

El recálculo verifica 65 formas distintas por ventana. No presenta esos totales
como lecturas simultáneas ni suma individuos independientes. Se incluyen las
753 consultas de MAIN y sus dos controles, con RAW/clocks, dirección, ticks,
expectativa del auditor y localizador de origen.

## Controles de adquisición y ocupación

Sin evento y con exposición desacoplada: 0/65 primeras respuestas y 0/186
posteriores bajo el mismo decoder. No son controles sin materia: sus entradas
y recibos están conservados para examinar la diferencia.

En estados guardados T2353, el recuento independiente de arrays completos da:

- MAIN: 298024/300763 sitios con `state>0`.
- Sin evento: 348/300763.
- Desacoplado: 297334/300763.

La expansión también aparece sin asociación funcional correcta. Por ello no
se atribuye específicamente a «aprender 65 conceptos». La carga máxima de MAIN
sigue por debajo del tope del reducer; ocupación geométrica no equivale a
saturación numérica de ese campo ni a consumo eléctrico.

## Qué causas pueden examinarse

El perfil T2220–2353 y la vecindad del primer nacimiento local de `semantic7`
registrado en T2292 están íntegros. La rama identificada es EMPTY_XNOR. El
corte selectivo evita ese nacimiento local, pero la expansión global continúa;
la ocupación ya estaba creciendo antes. No hay causa única aislada de toda la
onda ni demostración de que ese nacimiento produzca todos los fallos.

Los diagnósticos de lectores conservan preestado/postestado, vecinos y destinos.
Una célula ocupada puede evolucionar y destruir una llegada esperada antes de
la rama DEMUX. Otros casos son problemas de fase: observación temprana fallida
y acceso posterior no equivalen a pérdida definitiva de memoria.

En la fase final se rechazan 177/178 peticiones nuevas, incluidos los intentos
de revisión. Se conserva el control sin esos intentos y su igualdad física.
No se limpió RAW, no se reiniciaron clocks y no se restauró una memoria favorable
en MAIN para ocultar el deterioro.

## Qué no puede concluirse

No se ha probado borrado de las 65 relaciones, un máximo universal de palabras,
estabilidad indefinida ni imposibilidad fundamental de v27. Tampoco basta
encontrar un portador antiguo para afirmar acceso funcional. La evidencia
favorece un conflicto concreto entre rutas/retornos, ocupación y protocolo;
la explicación completa y el acceso sostenido permanecen abiertos.

Datos directos: `RESULTADOS_NEGATIVOS/CONSULTAS_65_Y_CONTROLES.json`,
`EVIDENCIA_PRIMARIA_ESENCIAL/CAMPOS_COMPACTOS/`,
`CONTROLES_CAUSALES/INDICE_CONTROLES.json` y C02/C10–C12 del mapa de afirmaciones.
