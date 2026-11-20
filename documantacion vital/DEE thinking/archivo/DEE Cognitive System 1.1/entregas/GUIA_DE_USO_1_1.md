# Guía de uso1.1

Una operación compuesta que falle después de admitir alguna entrada conserva su mundo y cola parciales en un checkpoint `FAILED_*`. El error muestra su hash y tick. No se descarta ese futuro para volver a un estado anterior favorable. Un fallo de escritura interrumpido se señala como inconsistencia, sin restauración automática.

## Instalación y vida activa

Se requiere Windows x64, CPython3.13x64 y las bibliotecas de ejecución de C++ del sistema. No se distribuye el intérprete ni una toolchain. Ejecute desde la carpeta extraída:

```powershell
.\sistema\instalar_sistema.ps1 -Python313 'C:\\ruta\\python.exe'
.\sistema\iniciar_sistema.ps1 estado
.\sistema\iniciar_sistema.ps1 vidas
.\sistema\iniciar_sistema.ps1 capacidades
.\sistema\iniciar_sistema.ps1 perfiles
```

El inicio normal carga ACTIVO.json y verifica versión, hash del snapshot, RAW/clocks/tick y la identidad documental. Si falta o es incoherente, informa el error. No crea ni rebobina una vida. `activar ID` elige explícitamente otra vida sin alterar su pasado.

## Una interacción nueva con un estado aprendido

```powershell
.\sistema\iniciar_sistema.ps1 eventos .\sistema\documentacion\ejemplos\visita_1_1.eventos
.\sistema\iniciar_sistema.ps1 estado --vida VISITA_11
.\sistema\iniciar_sistema.ps1 restaurar VISITA_11
.\sistema\iniciar_sistema.ps1 interactivo
```

El recorrido crea una bifurcación exacta de E1_SOCIAL_11T3154. Consulta cuatro portadores mediante un lector material preparado; presenta un objeto nuevo82, comprueba82+5>referencia78 y vuelve al antiguo R36/O16. GuardaT3221. El originalT3154 queda intacto. La cadencia, los suministros y la elección del lector son externos y declarados, no iniciativa aprendida. VISITA_11 no debe existir antes de ejecutar el ejemplo; repetirlo con el mismoID produce error, nunca reemplazo.

## Operaciones distintas

`crear NUEVA --perfil fisica_directa --parametros '{"N":11}'` prepara un mundo vacío. `crear ... --perfil cpc9_integral_n67` prepara posibilidades, no asociaciones semánticas. `experiencia ... curriculo_integral` programa experiencias pedagógicas reales; no convierte su programación en invención del ente.

`restaurar ID` sólo carga y verifica; `continuar --vida ID --hasta T` evoluciona; `guardar --vida ID` guarda el mundo completo con colas, interfaces y metadatos. `bifurcar PADRE HIJA --modalidad EXACT_FORK` comparte el pasado hasta ese snapshot. `importar-estado ARCHIVO ID --perfil PERFIL --sha256 HASH` es continuidad importada explícita, no aprendizaje nuevo. `exportar ID --salida NUEVA` exporta un estado completo y su ficha.

`entrada --vida ID PUERTO CARGA T --sonda` introduce materia. `observar --vida ID X Y Z` y `observar-componente --vida ID quantity.center` son lecturas pasivas. Una consulta material puede enseñar, transformar o perder acceso; use copias para pruebas destructivas. Cero activo, silencio, rechazo, ocupación y fuera de dominio no se sustituyen entre sí.

## Repertorios y actualización

R65_45_VIVIDO conserva32formas adquiridasT0 y33T134. Deben consultarse en ventanas separadas: el protocolo común equivocado sólo veía33; sin reenseñar se recuperaron65 enT658/661 yT789/792. R65_REVISION_11 es otra rama: la receta privada de tres puertos revisóL01T917 y conservó64formas enT1051/1054. No amplía silenciosamente la APIoficial4.5 ni demuestra actualización arbitraria. El sham fuera de ruta afectóL06 y se conserva como control imperfecto.

R65_N67_VIVIDO es otra vida, sin el cuerpo integradoCPC9:65/65 durante diez barridos hastaT2822 y reserva con carga9 hastaT2889. U0_14_VIVIDO es el perfil oficialU0, independiente. No existe un puente implícito entre estos Runtime.

## Laboratorio, comparación y promoción

`bifurcar PADRE CANDIDATA --modalidad CANDIDATE`, `comparar PADRE CANDIDATA` y `promover CANDIDATA --decision ARCHIVO.json` están disponibles. La comparación es pasiva y no elige ganador. Promover exige el hash exacto, ganancias, pérdidas, incertidumbres, evidencia y cobertura. Registra PREPARED/COMMITTED y cambia el puntero activo sin volver atrás los individuos. Una nueva geometría oN requiere otra vida desdeT0.

`ensayar --nivel A|B|C --salida DIRECTORIO_NUEVO` ejecuta pruebas en copias. `probar-herencia --familias cpc1,cpc2,... --salida NUEVA --segundos 4200` materializa el núcleo incluido y ejecuta aparatos auxiliares; no enseña al activo. Las34familias están en capacidades/core/FAMILIAS.json. CORE06/07 usan la dependenciaNumPy incluida explícitamente sólo para esos contratos instrumentados.

## Procedencias y límites

ENTE indica campos y emisiones v27; ENTORNO, acontecimientos presentados; INSTRUMENTO, puertos, recibos y observadores; INTERPRETACIÓN, lectura del auditor. No existe chatlibre niLLM que complete respuestas. El gestor selecciona perfiles a petición explícita, nunca porque sabe quién tiene la solución.

Las restricciones de archivos del CLI son una barrera de auditoría Python, no un sandbox de seguridad del sistema operativo. El modo de física directa no añade guardas ni cognición. No hayR2demostrada, YO/TÚfuncional ni65significados. Consulte contratos y evidencia, no una puntuación global.
