# Componentes nativos CPC9: contacto y orden

Estos componentes son recetas científicas externas sobre el WHL oficial4.5.0; no modifican el motor. Sus laboratorios son auxiliares y no se suman a la vida principal de E1. La integración real debe comprobarla el ejecutor principal.

## Montaje desde T0

Todos los componentes devuelven interfaces sin materia inicial. Se añaden a una receta antes de `OrganizationalWorld.create`, nunca a un mundo ya entrenado. N=67 es fijo durante cada vida. Los métodos `schedule` sólo programan acontecimientos, oportunidades y recursos iguales para los bancos; no leen observaciones ni eligen la respuesta correcta.

- Contacto G: `contact_access_g.prepare_remote_contact(remote_phase=3,remote_regulation='onpath',...)` prepara las interfaces declaradas; `schedule_remote(session)` añade el currículo remoto sin repetir el currículo base. La geometría queda en `geometry['remote_contact']`. Devuelve una recetaMCTS completa: al integrar con otra receta sólo se seleccionan sus24 interfaces `remote_contact.*`, sin duplicar el cuerpoMCTS. Se conserva la primera lectura410 y uso416; no se anuncia acceso renovado ilimitado477/483. El valor por defecto `remote_regulation='omitted'` es el controlD, no la reparaciónG.
- Orden F2: `counterprop_order.component(origin=(12,50,50),first_tick=469,interval=5,separation=11)` devuelve `(ports,geometry)`. Instalar como `geometry['counterprop_order']`. `schedule` admite ordenAB/BA, omisión de acontecimientos, dosis y señal. Las oportunidades fijas477,481,548,554 tienen un dominio temporal estrecho; intervalo3 sin retimar falló y se conserva.
- Orden F3v2: `tiled_order_parallel.component(origin=(12,45,45))` devuelve `(ports,geometry)`. Instalar como `geometry['tiled_order']`. `schedule(session,tile_order='AB',interval=5,...)` es la implementación de `tiled_order.py`; ambos archivos son necesarios. Los seis lectores+Z y recursos−Y permanecen iguales en todas las condiciones. Los intervalos1/3/5 cambian los acontecimientos, no los puertos ni las ventanas.
- Receptor de orden: `order_social.component(origin=...)` devuelve `(source_ports,source_geometry,receiver_ports,receiver_geometry)`. Instalar como `geometry['tiled_order']` y `geometry['order_social']`. `schedule_receiver(session)` programa sólo las entradas del receptor. No vuelve a programar el currículo fuente. El portador producido por E viaja por v27, no mediante lectura/reinyección Python.

Los constructores de laboratorio `RemoteContactSession`, `TiledOrderParallelSession` y `OrderSocialSession` incluyen el aparatoMCTS heredado y su instrumentación. Son ejemplos ejecutables y no deben importarse para reclamar automáticamente todas las capacidades históricas.

## Contratos observables

Contacto G: a partir del acontecimiento tardío340, un acceso nuevo343 conserva la firmaadquirida; lector410 y recurso416 producen cargas y dirección dependientes de contacto/libre. Un contraflujo fijo neutraliza una corriente antigua que ocupaba el destino350. Su modalidad es regulación preparada, no política adquirida.

F3v2: dos tipos físicos de acontecimiento actuales producen un encuentro cuya localización diferencia su precedencia. A es un portador; B es una forma de seis portadores reales, no una clonación gratuita. Todos los bancos reciben la misma señalposterior482, lector549 y recurso555.

Con cargas actuales `a,b`, las firmas calificadas del banco correspondiente son:

-482: dirección(0,1,0), carga`5+a+b`.
-549: dirección(0,1,1), carga`12+a+b`.
-555: dirección(0,0,1), carga`23+a+b`.

El referente de banco depende de la relación geométrica entre estos acontecimientos, no de una etiquetaANTES enviada por el host. El auditor conoce el orden presentado para comparar después, pero esa comparación no alimenta al participante.

Receptor: el portador555 viaja ocho pasos+Z hasta563. Las firmas candidatas son:

-563: dirección(0,1,0), carga`28+a+b`.
-630: dirección(0,1,-1), carga`35+a+b`.
-636: dirección(0,0,-1), carga`46+a+b`.

Los fondos12/23 pueden tener direcciones parecidas y no representan silencio. Por ello la evaluación exige firma completa, no una respuesta simplemente no nula.

## Recursos y atribución

F2 añade10 interfaces, cero materiaT0 y diez entradas de contenido/oportunidad/señal/consulta/uso en el caso normal; dosis total52.

F3 añade31 interfaces, cero materiaT0, siete entradas de acontecimientos y18 de señal/lectura/uso:25 solicitudes, dosis159 con `a=b=3`. Seis interfaces de control fuera de ruta están preparadas pero no se usan en el positivo. El diseño comparte mecanismo, no seis conocimientos adquiridos simultáneos.

El receptor añade18 interfaces y18 solicitudes, dosis138. Se paga la transmisión del mismo portador fuente sin callback ni copia del estado entrenado.

Las geometrías, formatos de señal y ventanas son recursos preparados. El contenido que depende de los acontecimientos y sus encuentros es adquirido. La fuente temporal no inventa autónomamente su aparato; tampoco contiene enT0 la respuestaAB/BA. La circulación posterior y las cargas exactas se miden en datos primarios.

## Alcance de la generalización

Los nuevos ensayos de intervalos y dosis mantienen la preparaciónF3v2 fija, lo que comprueba robustez de la operación física y del acceso. Cada laboratorio adquirió su propia señal en482. Eso no basta para afirmar que una palabra aprendida con intervalo5 se aplicó a intervalo3 sin nueva asociación, ni ANTES humano universal, ni selección de memoria aprendida.

Para trasladar a E1 se requiere montar las interfaces desde suT0 y comprobar causalmente allí adquisición, retención, uso y controles. Los snapshots de laboratorios no se trasplantan a E1.
