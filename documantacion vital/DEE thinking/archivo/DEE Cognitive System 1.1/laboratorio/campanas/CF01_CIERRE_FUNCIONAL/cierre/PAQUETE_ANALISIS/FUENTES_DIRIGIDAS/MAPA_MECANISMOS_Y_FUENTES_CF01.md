# Mecanismos utilizados en CF01

Este mapa orienta la construcción sobre fuentes existentes. No representa una nueva auditoría, una reejecución de CORE/CPC ni conocimiento que el participante pueda consultar. El texto extraído está en `textos/`; `INDICE_FUENTES_EXTRAIDAS.json` conserva archivo fuente, hash y alcance de extracción. Los identificadores P corresponden a párrafos del XML, no a páginas verificadas visualmente.

| Mecanismo o distinción | Fuente y localizador efectivamente leído | Implementación existente | Función en el cierre |
|---|---|---|---|
| Estado completo y persistencia | Física4.0.1 §§3–4; Manual1.8 caps2,9,11; informe técnico4.5 persistencia | `app/lives.py`, `dee_thinking.persistence`, Runtime/OrganizationalWorld oficiales | Bifurcar un pasado real y conservar mundo, agendas, interfaces y progreso; no reconstruir desde arrays incompletos. |
| Comparación y retorno por consecuencias | Manual1.8 cap25/P00712–713; PN caps14–15 y OBP cierre29–34 | `arquitectura_distribuida_mi02_r8.py`; `integracion_distribuida_mi02_r6.py` heredado por R9 | Conservar contenido adquirido y demostrar cambios de actuación; no atribuir toda reescritura a un retorno exterior sin corte causal tardío. |
| Historia contextual y factoriales | PN cap18/P00450–487, Ingeniería05 NRD05/06 consolidada; Física4.0.1 §§9.3,10.2,11 | Ramas exactas del Store; protocolo común de evaluación; recálculo del auditor | Comparar efecto de una misma oportunidad después de historias distintas; igual delta inmediato no implica igual propagación. |
| Memoria relativa y expresión | OBP2.1 cierre29/P00472–484 y32/P00555–590 | Comparador soportado y lector nativo en preparaciones existentes | Separar conservación de relación, disponibilidad del lector y utilidad de la actuación; incrementos comunes pueden conservar la diferencia. |
| Lector liberable y consulta privada | Manual1.8 cap25/P00715–718; `integracion_distribuida_mi02_r9.py` y geometríaR9 leídos | R9 N26, participante A/B en mismo Runtime, canales y suministro preparados | Reutilizar el acceso social sin limpieza externa; el protocoloR9 hereda el lector métrico deR6 y conserva anatomía propia. |
| Reutilización y soporte distribuido | PN cap19/P00491–505 (Ingeniería06) y cap17/P00409–446 | Soportes, referencias y rutas presentes en snapshot; observación pasiva | No reducir memoria a puerto ni firmas a bits independientes; exigir uso específico, no sólo diferencia detectable por auditor. |
| Propagación y retorno | Física4.0.1 §§4.2,5.3–5.4; PN cap20/P00510–547 (Procesos01–02) | Runtime y observador exacto; geometría externa de auditoría | Dependencia RAW hasta radio3 por tick, clocks hasta radio1; distinguir trayectoria material, influencia efectiva, latencia y retorno toroidal. |
| Observación y lectura | PN cap7/P00169–181; OBP cierre33/P00592–601; Entrelazamiento§0.5/0.8 | Observador pasivo existente y sondas materiales declaradas | Un lector parcial puede ocultar diferencias; una sonda puede enseñar/interferir. Estado conjunto no acredita por sí solo entrelazamiento cuántico. |
| Pérdida causal y reducción | Física4.0.1§4.3/P00196–200; PN cap21/P00556–575 | Comparación exacta de RAW, clocks y operativo en ramas de control | Estado causal idéntico + protocolo idéntico exige futuro idéntico. No inventar recuperación si las historias convergieron; no concluir borrado global a partir de un puerto. |

## Restricciones de ingeniería extraídas

El tick calcula la salida base desde el estado de entrada y aplica DEMUX después. No hay cascada ilimitada intratick. Los snapshots se toman en fronteras operativas completas del propietario, no saltando agendas mediante otro acceso al Runtime.

La protección preparada, la selección condicionada por contenido adquirido y una estrategia modificada por consecuencias son atribuciones diferentes. R9 es una preparación nueva de MI02 y su descendiente CF01 no se renombra como biografía E1. El predeterminado E1_SOCIAL_11 permanece protegido.

El cierre posterior de OBP corrige una atribución importante: retirar desdeT0 la consulta cambia el contexto antes de que exista el supuesto retorno exterior. Los cortes tardíos de la acción o del producto42 conservaron la reescritura local investigada. Por ello, para sostener necesidad del retorno deben intervenirse productos ya formados y compararse shams, no aceptarse el nombre de un brazo como explicación.

## Cobertura de fuentes y ausencias

Se extrajeron completos cuerpo, tablas, notas y encabezados/pies accesibles de los DOCX, sin OCR de sus imágenes ni ejecución de cápsulas. Los tokens matemáticos OMML se conservan en orden textual, pero no sustituyen la estructura de fracciones/subíndices del documento fuente. La lectura de Física y PN para ingeniería fue dirigida a los capítulos citados; una extracción completa no se denomina lectura lineal completa del tratado.

El Manual1.8 se leyó transversalmente en su texto completo. Conserva afirmaciones de acceso documental de ediciones anteriores que no equivalen a nuestro acceso actual. Los dos DOCX técnicos4.5 citados no se recuperaron en las ubicaciones ya comprobadas; sí se leyeron completos `documentos/thinking_4_5/INFORME_TECNICO.md` y `LEEME.md` de la distribución, junto con contratos/código instalado pertinente. No se sustituyen por manuales4.0 rotulados como4.5.

UNI v3 está incorporado materialmente en Física4.0.1, parteIV, sección que comienza en P01008 y preserva bloques matemáticos desde el DOCX fuente según el propio tratado. Se distingue esa lectura integrada de la recuperación de un archivo UNI v3 independiente, no localizado por nombre en los índices y documentos principales consultados.

La documentación es del investigador. No alimenta al participante durante evaluación y no transfiere conocimientos entre vidas.
