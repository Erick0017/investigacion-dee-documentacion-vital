# Preintegración H3/H4

## Alcance ejecutado

Todo el trabajo quedó bajo `candidates/`. No se modificaron el kernel, headers,
source, catálogo ni CMake estables. Se recuperaron dos candidatos mediante
revisión dirigida de runners, locks y resultados primarios.

## H3 — reparación funcional CORE17

Se portó el aparato causal C17E02/C17E03 a un runner C++ aislado enlazado con la
biblioteca Release vigente. El port conserva:

- dos fuentes redundantes que reciben aprendizaje por interacción;
- daño explícito de la primera política transferida;
- lanzamiento de la segunda copia por un corredor;
- conversor de receptor y consulta fresh;
- controles de copia no entrenada, dirección reseteada, copia ausente, corte
  de ruta, corte fuera de ruta y receptor incorrecto.

Se ejecutaron dos geometrías N=31 transformadas, siete modos por geometría, 14
casos en total. En ambas geometrías:

| Modo | Función fresh observada |
|---|---:|
| tratamiento | 2/2 |
| corte fuera de ruta | 2/2 |
| copia no entrenada | 0/2 |
| dirección de copia reseteada | 0/2 |
| copia ausente | 0/2 |
| corte de ruta | 0/2 |
| receptor incorrecto | 0/2 |

La reconstrucción en el receptor coincidió exactamente con esos conteos. El
validador técnico comprobó siete invariantes y terminó con código 0.

### Distinción obligatoria sobre copia/replicación

La segunda copia estaba presente desde la preparación y **aprendió por su propia
secuencia de interacciones**, igual que la primera. Después sirvió de fuente de
reconstrucción. No apareció una operación donde la primera copia crease la
segunda; por tanto el resultado es reparación desde una copia aprendida
redundante, no replicación adquirida.

En los 14 casos las dos fuentes se consumieron. Este aparato no probó
persistencia ni reutilización de esas copias, y el contrato candidato las
declara explícitamente como recursos consumibles.

La campaña incluye inyecciones y daño del host después de t0, igual que el
aparato primario. Se clasifica `ACOPLADA_DIAGNOSTIC`, no reparación autónoma.

## H4 — accesibilidad Ingeniería 03–04.5/POST

H4 se implementó como contrato de medición y no como builder. La decisión se
debe a la evidencia primaria:

- NRD01 comparó el efecto de un challenge con el baseline de **la misma
  historia**, encontró 36 señales persistentes y verificó la canonicalización
  exacta de pares.
- NRD02 confirmó el patrón en V1/V2/V3; cada configuración conservó seis señales
  de control local.
- POST P01R corrigió identificadores de receptor entre ramas. Conservó el
  acoplamiento remoto condicionado por historia: periodo 1 en `INTACT` y periodo
  2 en `BROKEN/NO_B`.
- Ese mismo resultado registró `functional_class_reinstantiated=false` y no
  demostró el borde refractario→competente.

El verificador aislado comprobó seis invariantes, incluyendo separación entre
trayectorias nativas y challenges en clones, y terminó con código 0. No se
reejecutaron campañas históricas ni se convirtió una síntesis en nueva
telemetría.

## Estado de preintegración

| Candidato | Código/contrato | Ejecución | Estado local |
|---|---|---|---|
| H3 reparación CORE17 | runner C++, contrato, resultados y validador | 14/14 casos terminados | realización candidata ejecutada en dos geometrías; no promovida |
| H4 accesibilidad | contrato, resumen primario con hashes y validador | 6/6 checks | contrato verificado; no builder |

## Pendientes antes de cualquier promoción

H3 requeriría una API de alto nivel que declare preparación, daños diagnósticos,
timing, puertos, recursos y modalidad; tests de snapshot/backend; y una decisión
explícita sobre si un procedimiento con daño e inyecciones del host pertenece al
catálogo de organizaciones. Nada de ello autoriza llamarlo replicación.

H4 requiere un observer congelado por contrato y un aparato autocontenido si se
quiere ofrecer ejecución. La evidencia actual autoriza una consulta finita de
accesibilidad dependiente de historia, no un planificador universal ni el borde
nativo de competencia que 04.5 dejó abierto.

No se exportó ningún identificador a `OrganizationCatalog`.
