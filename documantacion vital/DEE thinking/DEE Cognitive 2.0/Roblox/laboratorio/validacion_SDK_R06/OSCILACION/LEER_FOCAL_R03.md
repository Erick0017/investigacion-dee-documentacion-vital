# Entrada focalR03: sólo guarda del enlace

Use DEE_FOCAL_CONSUME_RECHARGE_R03.rbxlx y DEE_FOCAL_NONCONSUMING_CONTROL_R03.rbxlx. R02 permanece íntegro como antecedente. El único cambio es FocalHttpLoop antes del HttpLoop original y el Script de arranque que lo llama. No cambia mapa, ley del cupón,encoder,actor,motor ni criterios.

La guarda consulta GET handshake y exige profile=FOCAL. CONSUME_RECHARGE requiere focalCondition=OSCILANTE; NONCONSUMING_CONTROL requiere CONTROL. Son metadatos del servicio privado focal, no sensores/inputsNative. El runtime conserva protocolVersion=DEE.RBX.Connector.R01 y runtimeVersion=0.1.0. Si falta el perfil/condición, se detiene antes de enviar un POST; no usar el servicioDEMO3 ni omitir la guarda para continuar.

Siguen vigentes los preflightRO R02/R03 y LEER_FOCAL_R02.md. Root debe comprobarlos enPreview, preparar lasdosinstancias completas, terminar elservicio anterior y cargaruna sola vida cada vez. El SDKy la demo no se modifican. Primeraadmisiónmáxima04:03UTC/cierre05:03:43UTC18nov2026 ypresupuesto compartido40000ticks.

La revisión estática del runtime focal verifica role6,lease6,cursorhasta12,fuentesNativeKEYseparadas yledgercomún. El soporte técnico no acredita exposicionesNative o salida delbucle. c02 conserva los resultados completos privados y sus fuentes congeladas; los IDs del brazo se deben registrar junto a su escena.
