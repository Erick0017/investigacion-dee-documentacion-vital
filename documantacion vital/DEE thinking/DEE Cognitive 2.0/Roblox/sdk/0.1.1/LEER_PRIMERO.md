# DEE Roblox SDK 0.1.1 · candidato público

Dos componentes separados: KIT_DESARROLLADOR (CoreMax3) y KIT_EXTENSION (capacidades asistidas). No incluye el cerebro/runtime privado, credenciales ni estados Native.

El paquete se entrega como candidato. El registro final aportado por Root está en ESTADO_VERIFICACION.json; el ensamblador no deduce éxito material desde hashes o fixtures. Aprobación pública declarada por Root: sí.

| Criterio | Estado declarado | Alcance |
|---|---|---|
| K1 | VERIFIED | Instalación local desde copia en otra ruta; despliegue corto Windows y conexión privada declarados. No es evaluación externa. |
| K2 | VERIFIED | Dos ciclos con Native oficial, misma vida diagnóstica y cuatro respuestas con sus ACK. Sin usar el principal. |
| K3 | VERIFIED | Cuerpo preparado ejecutó EXIT_1 y cambió dispositivo -1 a +1; retorno Native ordinario. No demuestra navegación aprendida ni aprendizaje nuevo de una política. |
| K4 | VERIFIED | Reapertura entre procesos; ocho campos restaurados con cero diferencias según contrato, recibos y cursor coincidentes antes de observar; uso posterior y nuevo cierre T994315. |
| K5 | NOT_RUN | Cero evaluadores externos. Modalidad inicial local acompañada con backend autorizado. |
| EXT | PARTIAL | Diez solicitudes Native: memoria luma, comparación +1/-1/0, suma4+5=9, composición asistida9-2=7 y revisiónluma+/-/+. Invocación y orden del operador. Cierre Native correcto; recibo HTTP R03 requirió recuperación GET del mismo ID. R04 corrige gracia HTTP con pruebas sintéticas. Comunicación entre participantes Native no expuesta; SOLVE usado dentro de COMPOSE, no ensayo directo separado. |

Los criterios originales previos se conservan en KIT_DESARROLLADOR/guias/CRITERIOS_PILOTO.md (su encabezado histórico no es el estado actual). La ficha externa sigue pendiente. Lea GUIAS/INICIO_Y_REQUISITOS.md. Modalidad inicial: piloto local acompañado en este PC, con backend privado autorizado por su propietario. No hay runtime entregado ni endpoint remoto ofrecido. La evaluación externa sigue PENDIENTE; nadie fue contactado por este ensamblador.

Verificación portable sin Native:

    python herramientas/ensamblar_publico_R06.py verify --root .

Este comando comprueba integridad, fuentes y defaults; no reproduce Native, Roblox, aprendizaje ni K1–K5. No ejecute experiencias antiguas para verificar el ZIP.
