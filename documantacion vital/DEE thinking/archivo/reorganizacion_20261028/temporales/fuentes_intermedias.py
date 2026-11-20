# -*- coding: utf-8 -*-
"""Material editorial dirigido para el compendio acumulativo.
Fuentes y primarios existentes; ningún tick nuevo ni modificación de vidas.
Las rutas originales se expresan respecto de DEE thinking; tras el archivo,
DEE Cognitive System 1.1/ puede localizarse bajo archivo/.
No es un catálogo de capacidades simultáneas de una sola vida.
"""

FUENTES = [{'id': 'PC-REPORT',
  'ruta_original': 'DEE Cognitive System 1.1/laboratorio/campanas/PAISAJE_CAUSAL_01/INFORME_RESULTADOS.md',
  'sha256': '6f15515d913d2a2879f05df70acf92ba3c42230b21e3607a6dbe05ae932f05d7',
  'bytes': 20378,
  'tipo': 'informe',
  'localizador': 'Secciones sobre consultas, protección bidireccional, lector transformado, continuidad y escala',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'PC-CALC',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/PAISAJE_CAUSAL_01/RECALCULO_DESDE_DATOS_EMPAQUETADOS_52.json',
  'sha256': '191f48e7f41be7e51406cf75f29a59194d6419154c88e864b1de191c163717f2',
  'bytes': 555200,
  'tipo': 'recalculo archivado',
  'localizador': '$.cases[REFERENCIA_CAUSAL_05/*, LECTOR_POST_TRANSFORMACION_41/*, CONTEXTO_UTIL_MIXTO_44/*, '
                 'PROTECCION_BIDIRECCIONAL_33/*]',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'PC-OMIT',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/PAISAJE_CAUSAL_01/REFERENCIA_CAUSAL_05/omit_probe/PRIMARIOS.json',
  'sha256': 'ed775690bfe69c5a0e6f62df782333871396a43118a7d6fa8a1f26976706f4ba',
  'bytes': 3680110,
  'tipo': 'primario',
  'localizador': '$.phases; $.witnesses; $.interventions; $.before_new_use; $.receipts',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'PC-TRANS',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/PAISAJE_CAUSAL_01/LECTOR_POST_TRANSFORMACION_41/full/PRIMARIOS.json',
  'sha256': '0bcdf2603f731975572efb3f7fed102e75f8b409512b1efe8d9ff1f5b58b7cc8',
  'bytes': 1589847,
  'tipo': 'primario',
  'localizador': '$.transformed; $.reader; $.SPANISH_DECODED; $.action; $.old_after',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'AA-REPORT',
  'ruta_original': 'DEE Cognitive System 1.1/entregas/DEE_COGNITIVE_1_1_ACCESO_ADAPTATIVO_01_ANALISIS.zip',
  'sha256': '8776bb41f12d6c2cda83fa1b4dacbc0170d38160bb946e99ffa2e1af1673f275',
  'bytes': 13912710,
  'tipo': 'informe',
  'localizador': 'Secciones sobre redundancia, acceso nuevo, selección local y MAIN',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks',
  'miembro': 'INFORME_RESULTADOS.md',
  'sha256_miembro': '2bd080991a86d6389957662110e304e8d29ece75d7d24d90e92810e63a0522a8',
  'bytes_miembro': 16829},
 {'id': 'AA-CALC',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/RECALCULO_FINAL_CLASIFICADO.json',
  'sha256': '70504067ab5e0d25076c87930c5e5d8cb7c7e28f1be1a740c4edf96788ac4511',
  'bytes': 1044355,
  'tipo': 'recalculo archivado',
  'localizador': '$.cases: ACCESO_LOCAL_SEPARADO_33, CONTROLES_Y_RESERVAS_33, USO_INMEDIATO_RECUPERADO_46, '
                 'CONTINUIDAD_OPERATIVA_49; $.errors',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'AA-PLUS46',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/USO_INMEDIATO_RECUPERADO_46/plus/PRIMARIOS.json.gz',
  'sha256': 'f546584ac77218c22468b1964cd3d5cb026bafb14e105937c7c11cf181400059',
  'bytes': 119959,
  'tipo': 'primario',
  'localizador': '$.initial_external_content; $.prepared_redundancy; $.later_content_teacher_inputs; $.stages; '
                 '$.frames; $.receipts',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks',
  'sha256_descomprimido': '7ad6fcae3cc3a5ba0b76482026ed6e90c264fd75629051947915d290bcc0553d',
  'bytes_descomprimido': 1421348},
 {'id': 'AA-MINUS46',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/USO_INMEDIATO_RECUPERADO_46/minus/PRIMARIOS.json.gz',
  'sha256': '9ef1992e9a5e030953d78497c806072e7a2e3175f7085439af07d676bf033be7',
  'bytes': 119960,
  'tipo': 'primario',
  'localizador': '$.stages; $.frames; $.later_content_teacher_inputs; $.receipts',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks',
  'sha256_descomprimido': '1580b8827357b7ccaf9321035034eabb5a2bb5c39be38b0412b083ba1efe9454',
  'bytes_descomprimido': 1421205},
 {'id': 'AA-POLICY',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/ACCESO_LOCAL_SEPARADO_33/up/PRIMARIOS.json.gz',
  'sha256': '3bbc78f95fd23b7841ae3f34f10e649605785cdf7ef4dc0404f9427d53e02f77',
  'bytes': 60627,
  'tipo': 'primario',
  'localizador': '$.prepared_policy_site; $.policy_first; $.policy_second; $.B_use; $.assistance',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks',
  'sha256_descomprimido': '6245a1234c5ab6c1af9a166fda9f868eed9774c9d6e492f7295a08a5c21b9063',
  'bytes_descomprimido': 995522},
 {'id': 'AA-OMIT',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/CONTROLES_Y_RESERVAS_33/up_omit_feedback/PRIMARIOS.json.gz',
  'sha256': '482675fa0008b0ab08e2317080c4181108e1f909d20e87701b25ecadff87d2dc',
  'bytes': 60403,
  'tipo': 'primario',
  'localizador': '$.policy_first; $.policy_second; $.B_use; $.receipts',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks',
  'sha256_descomprimido': '07bdffad860b953c90b5f8621ed947a6a46c8966b60dfe753b9e0058085eb5d2',
  'bytes_descomprimido': 992049},
 {'id': 'RET-REPORT',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/AUDITORIA_RETROSPECTIVA_01/PAQUETE_CANDIDATO_01/INFORME_CIENTIFICO.md',
  'sha256': 'c762693aec0965a5fa398bfb6ae6fc9b7ba53eebe2b102e82af6a751a4520eef',
  'bytes': 20483,
  'tipo': 'informe',
  'localizador': 'Apartados AA13, AA42, conservación y acceso, CPC9, límites',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'RET-CALC',
  'ruta_original': 'DEE Cognitive System 1.1/evidencia/campanas/AUDITORIA_RETROSPECTIVA_01/CALCULOS_R5.json',
  'sha256': '6849e7359e1981b2ef3032757827a0a5cdf6bc08573ffda814a46c6f412e9768',
  'bytes': 6315542,
  'tipo': 'recalculo retrospectivo cero ticks',
  'localizador': '$.AA13; $.AA42; $.CONTENT_CONTRASTS; $.POLICY_HISTORY_CONTRASTS; $.EXISTING_TOROIDAL_ROUTES; '
                 '$.CPC9',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'HAB-REPORT',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/entregas/DEE_COGNITIVE_1_1_HABITAT_CAUSAL_Y_ESTRES_E1_01_ANALISIS.zip',
  'sha256': '45e3ab84f178d24e171ad73c8f27671b843964e30304f166d718e7594bd0267b',
  'bytes': 2117598,
  'tipo': 'informe',
  'localizador': 'Informe completo: estrés, puente y límites',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks',
  'miembro': 'INFORME_RESULTADOS.md',
  'sha256_miembro': '5734a43be9aeb43c7267e6958a5056b7733aef637545a2eb0804f92c949fee61',
  'bytes_miembro': 7691},
 {'id': 'HAB-CALC',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01/RECALCULO_EXTERNO_CONSOLIDADO.json',
  'sha256': '85a77e5b576703c6f758031b2e902f2a155b681ad8d2cea00668a5c683421e40',
  'bytes': 18059,
  'tipo': 'recalculo de primarios externos',
  'localizador': '$.trials; $.matched_environment_comparisons; $.totals',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'IC-REPORT',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/entregas/DEE_COGNITIVE_1_1_INTEGRACION_COGNITIVA_SITUADA_E1_01_ANALISIS.zip',
  'sha256': 'edcbacb7244edc8b4ad0fa8dec43c3170e23bc672f95c0c26d9465841cdd7bb5',
  'bytes': 9130853,
  'tipo': 'informe',
  'localizador': 'Informe completo y genealogía de las ramas continuables',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks',
  'miembro': 'INFORME_RESULTADOS.md',
  'sha256_miembro': '7016596c9fe57a3b948186e4fbb3ead4d0d9cc2663da774482e691f44e76ba1c',
  'bytes_miembro': 14633},
 {'id': 'IC-CALC',
  'ruta_original': 'DEE Cognitive System 1.1/evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/CALCULOS.json',
  'sha256': '63987551d94bf55c8e181fa082f508012628438b63774a35c907ad4d835aae83',
  'bytes': 481897,
  'tipo': 'recalculo archivado',
  'localizador': '$.trial_metrics; $.common_history_opportunities; $.selected_physical_results',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'IC-ACTION',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/COMMON_ACTION_INTEGRATED_COST_SOCIAL_132_D0_160.json',
  'sha256': '4a97cf5c8ae93650f6214ff18553b406497f0c4c8e0730b75023cbf289b1541b',
  'bytes': 377096,
  'tipo': 'primario',
  'localizador': '$.result.spec; $.result.frames; $.result.quantity; $.result.reference_hub; $.physical',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'IC-NULL',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/COMMON_ACTION_INTEGRATED_NULL_138_D0_160.json',
  'sha256': 'd06cec8e09f1e8721d4a8baece42ab6ee30e926079285f9eda6f82da52c8c538',
  'bytes': 377091,
  'tipo': 'primario',
  'localizador': '$.result.spec; $.result.frames; $.result.quantity; $.result.reference_hub; $.physical',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'IC-OMIT',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/COMMON_ACTION_INTEGRATED_RETURN_OMIT_137_D0_160.json',
  'sha256': 'b3a1c365df1808c2ad267155516ee25ea4384fb44bd7242dff52eeb0065cac9d',
  'bytes': 377045,
  'tipo': 'primario',
  'localizador': '$.result.spec; $.result.frames; $.result.quantity; $.result.reference_hub; $.physical',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'IC-RECP',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/GENERIC_RECOVERY_R2_PLUS_RECOVER_167.json',
  'sha256': '8472f5a12409f13998af2c2d02f392e84f48952f07432f536c91a2c2a1c7ed65',
  'bytes': 76739,
  'tipo': 'primario',
  'localizador': '$.result.spec; $.result.generic_requests; $.result.local_frames; $.result.external.rows; '
                 '$.result.no_reteaching_content; $.result.scope',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'IC-RECM',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/GENERIC_RECOVERY_R2_MINUS_RECOVER_167.json',
  'sha256': '513eb04409dd5dcba8f48df061c8fef63d785005f916354a88612c9ffbd73bad',
  'bytes': 76733,
  'tipo': 'primario',
  'localizador': '$.result.spec; $.result.generic_requests; $.result.local_frames; $.result.external.rows; '
                 '$.result.no_reteaching_content; $.result.scope',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'IC-SHAM',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/GENERIC_RECOVERY_R2_PLUS_SHAM_167.json',
  'sha256': '0c8eb17d7b7fe4b52554fffaf942f7873e66395bb4c47fc3db7faecdcf6a2729',
  'bytes': 76568,
  'tipo': 'primario',
  'localizador': '$.result.spec; $.result.generic_requests; $.result.local_frames; $.result.external.rows; '
                 '$.result.no_reteaching_content; $.result.scope',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'C2-REPORT',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/entregas/DEE_COGNITIVE_1_1_CONSOLIDACION_EVOLUCION_E1_CICLO_02_ANALISIS.zip',
  'sha256': 'a2684be6d4b699e12ba3804a17eaf84991ddf3b08984448c92bd56063959bfb3',
  'bytes': 5832737,
  'tipo': 'informe',
  'localizador': 'Informe científico completo, capacidades incorporadas y pérdidas',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks',
  'miembro': 'INFORME_CIENTIFICO.md',
  'sha256_miembro': 'ee96e923b249bc15e007902f79e003f9adaadda876a67befdc2082466d67f409',
  'bytes_miembro': 12199},
 {'id': 'C2-CALC',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/CALCULOS_REPETIBLES.json',
  'sha256': '120ff00e16949ddf956fe52dcd18ea21a525fd163a00f41e6699507e5d45c0da',
  'bytes': 684464,
  'tipo': 'recalculo archivado',
  'localizador': '$.gate_cases; $.main_gate; $.social_cases; $.separation_cases; $.case_inventory; '
                 '$.recovery_cases',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'C2-GATE',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_GATE_050_RETORNO.json',
  'sha256': '832f229b3a053c6021268406918500abb3b46b07e4ee6cb48585bf71570e4ed4',
  'bytes': 131907,
  'tipo': 'primario',
  'localizador': '$.data.result.rows[*].native_pre; .native_response; .environment; .utility_auditor_only; '
                 '.useful_auditor_only; $.before; $.after',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'C2-GATE-OMIT',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_GATE_051_SIN_RETORNO.json',
  'sha256': 'a939cded6e671ef7418af8f42c52cdfc15be29639a26ad4a16e74756c15f5f55',
  'bytes': 107599,
  'tipo': 'primario',
  'localizador': '$.data.result.rows[*].native_pre; .native_response; .environment; .utility_auditor_only; '
                 '.useful_auditor_only; $.before; $.after',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'C2-GATE-SHAM',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_GATE_053_SHAM.json',
  'sha256': 'b569c5efb14990a8c5956991b8ce50789e9591673ef6d6d87ad4c340ad84eb57',
  'bytes': 131288,
  'tipo': 'primario',
  'localizador': '$.data.result.rows[*].native_pre; .native_response; .environment; .utility_auditor_only; '
                 '.useful_auditor_only; $.before; $.after',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'C2-HIST6',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_HIST_140_DESGASTE6.json',
  'sha256': '903713545f2f16a2681b827efe21283847a9255bf392acaf0c37f0ceb20cc366',
  'bytes': 56567,
  'tipo': 'primario',
  'localizador': '$.data.result.rows[*].native_pre; .native_response; .environment; .utility_auditor_only; '
                 '.useful_auditor_only; $.before; $.after',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'C2-HIST13',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_HIST_141_DESGASTE13.json',
  'sha256': '24df0e035e6d12e806aed0ad108bc62e091348348970e710156eff2779a5111f',
  'bytes': 56602,
  'tipo': 'primario',
  'localizador': '$.data.result.rows[*].native_pre; .native_response; .environment; .utility_auditor_only; '
                 '.useful_auditor_only; $.before; $.after',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'C2-PROTECT',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_COMMIT_340_PROTEGIDO.json',
  'sha256': '5f345afdf703adff092de3819f775967b4763bf094afc1ae011e4bc7437f506c',
  'bytes': 145946,
  'tipo': 'primario',
  'localizador': '$.before; $.after; $.data.result; consultar social_cases del recálculo para fase válida y '
                 'agenda de191 eventos',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'C2-PROTECT-SHAM',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_COMMIT_341_SHAM.json',
  'sha256': 'e2978ec6f2f4a64badf08bab7537b10e1e2cae931d9144f78c9fa1be567deacd',
  'bytes': 113931,
  'tipo': 'primario',
  'localizador': '$.before; $.after; $.data.result; consultar social_cases del recálculo para fase válida y '
                 'agenda de191 eventos',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'C2-PROTECT-OPPOSITE',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_COMMIT_343_OPUESTO.json',
  'sha256': 'a536e0fe7fadf2ff47e77d3fd815a66b94489ee35e09b4191da49ec183b35c7f',
  'bytes': 145850,
  'tipo': 'primario',
  'localizador': '$.before; $.after; $.data.result; consultar social_cases del recálculo para fase válida y '
                 'agenda de191 eventos',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'C2-TRIPLE',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_SEPARA_330_DOS_PULSOS.json',
  'sha256': 'e40ca329bb33a9ba350849c40ea5b50820f8fcc26dac1dedd0dc2baac1796f85',
  'bytes': 646119,
  'tipo': 'primario',
  'localizador': '$.before; $.after; $.data.result; separación de roles y sucesivos usos en $.separation_cases '
                 'del recálculo',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'C2-TRIPLE-SHAM',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_SEPARA_331_SHAM.json',
  'sha256': '40f9526d4684a809f7507731b5558d375516c14237eadb958a926c72b1ada4a4',
  'bytes': 645343,
  'tipo': 'primario',
  'localizador': '$.before; $.after; $.data.result; separación de roles y sucesivos usos en $.separation_cases '
                 'del recálculo',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'},
 {'id': 'C2-ONEPULSE',
  'ruta_original': 'DEE Cognitive System '
                   '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_SEPARA_332_SOLO_ELEVAR.json',
  'sha256': '07b159e94cf04d8d2a991c9c45e430fd62e7efb2f5dd9df1fd755e7f7227be92',
  'bytes': 943274,
  'tipo': 'primario',
  'localizador': '$.before; $.after; $.data.result; separación de roles y sucesivos usos en $.separation_cases '
                 'del recálculo',
  'alcance_lectura': 'Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks'}]

FICHAS = [{'id': 'INTERMEDIA-01',
  'titulo': 'Consultar transforma el paisaje; proteger un acceso puede alterar otro',
  'funcion': 'Conservar y utilizar relaciones adquiridas mediante protección selectiva y lectores cuyo dominio se '
             'declara.',
  'mecanismo': 'PC01 separó el registro externo pasivo de una consulta material. La consulta de carga cero no era '
               'ausencia de interacción: cambiaba el número de vecinos activos y la regla aplicable. En el caso '
               'temprano, una contribución7 se desvió y encontró la referencia91 en T9986; produjo98 con otra '
               'dirección. Más adelante, la señal adquirida +XYZ11 se transformó por encuentro con -XYZ120 en '
               '+YZ131. Un lector preparado que añadía X pudo utilizar ese producto; cortar el contexto120 '
               'conservaba el acceso antiguo pero quitaba la función del lector nuevo. La historia podía ser útil '
               'y perjudicial según la tarea, sin que ello acreditara regulación aprendida.',
  'datos': ['Cuatro magnitudes nuevas: acceso original0/4; omitir la sonda, aplicar el mismo aporte fuera de ruta '
            'o retrasar1tick:4/4 en cada contraste.',
            'En R41 se registró +YZ131 en [57,10,35],T39836, RAW1229483260912861185; la consecuencia material se '
            'observó en T39848, RAW1224979691350261761.',
            'Protección bidireccional y desvío sostuvieron12 rondas y un panel durante96 retornos de calendario '
            'N67. PC01_NORMALIZADO45 llegó aT41318 con lector transformado y funciones intercaladas.'],
  'controles_y_negativos': 'Omisión, desplazamiento, desfase, cortes y shams separan el efecto de consulta del de '
                           'otros lectores. No todos los cortes resolvían el fallo. La protección de nuevas '
                           'adquisiciones perdió contacto o accesos espaciales anteriores; una consulta posterior '
                           'también podía dejar el lector ocupado. N83 demoró el fallo aT252 frenteT204 en N67, '
                           'pero ambos fallaron en la tercera ronda.',
  'vida_y_dominio': 'Ramas PC01 de E1,N67; PC01_NORMALIZADO45 y vidas de protección son trayectorias '
                    'alternativas, no una memoria fusionada. El ensayo deN83 es otra preparación.',
  'asistencia': 'El investigador fija suministros, lector, ruta y protección P0. El observador calcula '
                'diferencias sin alimentar respuestas al ente.',
  'limites': 'Un lector que aporta X favorece un código y no reconstruye contenidos opuestos en general. La '
             'Retrospectiva corrige el seguimiento proyectado: sólo se acredita el sufijo causal '
             'T10928–22318,11390 pasos y170 cruces por eje, no toda la proyección inicial. Ni recurrencia ni '
             'ocupación baja equivalen por sí solas a memoria funcional.',
  'estado': 'Procedimientos experimentales y comandos paisaje-* conservados; protección preparada utilizable '
            'dentro de sus dominios. No promoción general ni adquisición autónoma de rutas.',
  'fuentes': ['PC-REPORT', 'PC-CALC', 'PC-OMIT', 'PC-TRANS', 'RET-CALC']},
 {'id': 'INTERMEDIA-02',
  'titulo': 'Acceso alternativo a contenido anterior y revisión local de un selector',
  'funcion': 'Recuperar un código adquirido en otro soporte y modificar una selección local mediante '
             'consecuencias.',
  'mecanismo': 'AA01 preparó dos soportes que adquirieron inicialmente el mismo contenido por experiencia. Cuando '
               'dejó de servir la primera ruta, otra experiencia enseñó acceso sin nuevas entradas de contenido '
               '.NEW. Una consulta X común encontró un selector Y modificado por la historia y dirigió la '
               'interacción hacia otro soporte. En AA33 el selector preparado se revisó entre Y- eY+ por '
               'consecuencias opuestas; no fue Python quien eligió la ruta al observar el resultado. Son dos '
               'grados distintos: uso de información histórica y modificación local de selección.',
  'datos': ['En AA46 las dos historias plus/minus recuperaron Z±, lo recibieron y lo usaron nativamente en '
            'T45928/45929/45930; las vidas READY AA01_ACCESO_LISTO_plus/minus se conservaron enT45857 con9 '
            'entradas pendientes comunes.',
            'En AA33/up el selector pasó de [0,-1,0],s_reg70,T44718 a [0,1,0],s_reg140,T44785. Al omitir la '
            'segunda consecuencia conservó [0,-1,0],s_reg70 en ambos momentos.',
            'AA14/21: cuatro brazos consultados9/9 cada uno y dos sin consultas intermedias1/1 final cada uno:38 '
            'lecturas en seis ramas, no38 individuos.'],
  'controles_y_negativos': 'Cortar u omitir el segundo soporte o la enseñanza del nuevo acceso elimina la '
                           'función; sham la conserva. Consecuencia omitida o desacoplada mantiene la selección '
                           'anterior. Las historias opuestas, sin contenido y los cortes del selector impiden '
                           'atribuirla a una polaridad fija del lector.',
  'vida_y_dominio': 'E1_ACCESO_ADAPTATIVO_01 y ramas AA33/40/46/47/49,N67. MAIN terminaT47146; las READY son '
                    'alternativas con su propio pasado y no reparaciones retroactivas de MAIN.',
  'asistencia': 'Dos rutas, calendario, contextos, recursos, ley de consecuencias y anatomía están preparados. La '
                'iniciativa de pedir y de enseñar sigue siendo del anfitrión; el contenido y el cambio local del '
                'selector dependen de historia material.',
  'limites': 'P2 local de revisión por consecuencias dentro de oportunidades preparadas no es iniciativa de '
             'detectar el propio fallo, recuperación universal ni regulación R2 general. Seis funciones antiguas '
             'se intercalaron, pero el receptor no obtuvo retención prolongada general. El bloqueo posterior de '
             'MAIN no desaparece por conservar READY.',
  'estado': 'Operaciones acceso-* incorporadas con vida explícita y soporte de guardado/continuación. Capacidad '
            'local admitida; no se atribuye todo el repertorio al activo ni a un perfil posterior por compartir '
            'biblioteca.',
  'fuentes': ['AA-REPORT', 'AA-CALC', 'AA-PLUS46', 'AA-MINUS46', 'AA-POLICY', 'AA-OMIT', 'RET-CALC']},
 {'id': 'INTERMEDIA-03',
  'titulo': 'Distinguir información perdida, diferencia física y acceso funcional',
  'funcion': 'Establecer el límite físico de recuperación y auditar snapshots sin convertir el diario del '
             'anfitrión en memoria del ente.',
  'mecanismo': 'La auditoría retrospectiva trabajó con cero nuevos ticks. En AA13, dos historias de carga11 y17 '
               'convergían enT6 al mismo RAW,clocks, canales, recibos, entradas pendientes y protocolo futuro '
               'común dentro del sistema causal declarado. Los archivos guardados completos diferían en '
               'identificadores documentales y diario del propietario: ese diario conserva las antiguas cargas, '
               'pero el protocolo nativo no las consulta. En AA42, retirar la contribución entrante Z-192 antes '
               'del encuentro producía exactamente el mismo campo físico posterior que dejarla; retirar la '
               'ocupación de destino permitía su tránsito. El fallo no era simplemente un lector ciego a esa '
               'contribución, aunque otras diferencias históricas del mundo pudieran permanecer.',
  'datos': ['AA13:0 sitios RAW y0 clocks diferentes; tick6 en ambas historias; mismos canales, recibos y '
            'pendientes. Consulta futura común devuelve Y5 fuera del decodificador A/B.',
            'AA42,T45029,N67: retirar entrante da0 diferencias RAW y0clock; vaciar destino da2 diferenciasRAW; '
            'anular sólo state de destino da1; sham da0 y no recupera Z.',
            'AA46: antes del acceso READY hay9 sitios RAW diferentes y0 clocks; tras cortar soporte alternativo '
            'todavía quedan5 diferencias físicas, pero se pierde acceso y uso. Distinguibilidad externa no basta '
            'para memoria utilizable.'],
  'controles_y_negativos': 'Sin muro y sham conservan la distinción AA13; la nueva enseñanza permite '
                           'readquisición, no recuperación del pasado convergente. AA42 compara campo completo '
                           'de300763 sitios, colas vacías y recibos iguales; la intervención es diagnóstica '
                           'externa en copias, no acción de MAIN.',
  'vida_y_dominio': 'AA13 es aparato auxiliarN17; AA42 y contrastes de acceso pertenecen a ramasN67 de AA01. No '
                    'se extrapola la pérdida de una contribución a toda la biografía de E1.',
  'asistencia': 'El investigador delimita el sistema causal y compara estados completos; inspeccionar-snapshot es '
                'un instrumento externo. Recuperar desde un diario11/17 y escribir el resultado sería ayuda del '
                'anfitrión y no recuerdo DEE.',
  'limites': 'La no inyectividad admite pérdida en un dominio concreto. La existencia de diferencias RAW en otras '
             'condiciones tampoco acredita que E1 pueda utilizarlas. No se infiere un pasado único de un snapshot '
             'final. El rastreo de X+5 es continuo sólo en las ventanas disponibles, no linaje único sin huecos '
             'hastaT45028.',
  'estado': 'Instrumento de inspección incorporado; corrección científica incorporada a las conclusiones. Sin '
            'promoción de ramas ni nueva capacidad cognitiva general por esta auditoría.',
  'fuentes': ['RET-REPORT', 'RET-CALC', 'AA-CALC']},
 {'id': 'INTERMEDIA-04',
  'titulo': 'Un puente externo ejecutable y sus límites bajo estrés',
  'funcion': 'Hacer que salidas físicas de una bifurcación real de E1 actúen sobre Pendulum-v1 y recibir '
             'consecuencias, preservando continuidad.',
  'mecanismo': 'Hábitat01 bifurcó E1_SOCIAL_11T3154 y enlazó el runtime compatible con un proceso Gymnasium. Una '
               'regla fija convirtió sin(theta) en una carga mediante redondeo de73+40sin(theta), acotada1..145; '
               'descartó cos(theta) y velocidad angular. Direcciones nativas±X se transdujeron en±2Nm, con67ticks '
               'DEE por0.05s externos. Silencio/conflicto produjo0 por el puente y no se contabilizó como '
               'decisión inteligente. El mundo externo evolucionó por su modelo, recibió torques y devolvió '
               'observaciones; no fue un generador aleatorio rebautizado.',
  'datos': ['Gymnasium1.4.0, Pendulum-v1, proceso externo CPython3.12 y motor congelado CPython3.13. Dos semillas '
            'ambientales y controles de acción anulada y retardo1paso.',
            '73 pasos;57 torques no nulos ejecutados;16 salidas producidas pero anuladas en el control;219 '
            'solicitudes,146 aplicadas y73 rechazadas por ocupación.',
            'En el hábitat nativo: apertura20/20, ruido nominal10/12; choque temprano5/8 y recuperación12/12 '
            'después de retirar el estrés conforme al criterio declarado.'],
  'controles_y_negativos': 'Acción anulada y retardo delimitan el efecto de la salida; reconstrucción del entorno '
                           'desde acciones archivadas es recálculo externo separado de reproducción nativa. La '
                           'condición exigente y su control sin ruido nuevo dieron0/16 en una vida ya alterada; '
                           'escasez0/12 tampoco demuestra una causa nueva por sí sola.',
  'vida_y_dominio': 'E1_ECO_MAIN,T3154–7509 conserva futuro adverso; ECO_EXT_01T6167 tiene continuidad de puente. '
                    'No se reúnen las experiencias de ramas para fabricar una línea exitosa.',
  'asistencia': 'Sensor, codec, actuador, calendario, entorno y reinicios externos son instrumentación diseñada. '
                'No hay PID, planificador ni política externa actuando por E1. El resultado se limita además por '
                'rechazo del lector: parte de la salida procede del contexto heredado.',
  'limites': 'No demostró aprender una política competente de control ni cerró un hábitat endógeno autónomo v27. '
             'Retirar ruido desde el anfitrión y recuperar función no acredita homeostasis aprendida. Sin '
             'metabolismo nativo ni NSM65nuevo.',
  'estado': 'Puente y operaciones habitat-* incorporados como instrumentos y perfiles continuables, con estado '
            'ambiental/RNG/colas y reglas de silencio explícitos.',
  'fuentes': ['HAB-REPORT', 'HAB-CALC']},
 {'id': 'INTERMEDIA-05',
  'titulo': 'La consecuencia ambiental cambia una referencia y una decisión posterior',
  'funcion': 'Adquirir una referencia escalar contextual a partir del retorno real de acciones y utilizarla ante '
             'una oportunidad común.',
  'mecanismo': 'IC01 conservó un prefijo físico común y comparó actuación con retorno intacto, acción anulada y '
               'retorno omitido. La consecuencia llegó por un canal fijo y fue transformada por encuentros '
               'nativos; no se escribió desde Python la nueva referencia. En una oportunidad posterior con el '
               'mismo objeto230, la respuesta direccional dependía de la historia. Así se separó la simple '
               'actividad de un cambio adquirido que tiene uso posterior, sin atribuir competencia de control a '
               'cualquier cambio de referencia.',
  'datos': ['Tras tres pasos la referencia era81 con retorno real frente78 con retorno omitido.',
            'Ante objeto común230 y demora0, IC01_INTEGRATED_COST_SOCIAL_132 emitió+X,carga7,T5765; acción '
            'anulada y retorno omitido emitieron-X,carga7 en el mismo tick. Los contrastes persistieron con '
            'demoras67 y134.',
            'El primario enT5765 muestra referencias en el hub248/230/166 para intacto/anulado/omitido. No se '
            'debe convertir sin análisis el valor del hub post-tick en el único comparando accesible durante todo '
            'el tick.'],
  'controles_y_negativos': 'Historias de retorno omitido y acción anulada, demoras de periodo completo y consulta '
                           'común fijada antes del seguimiento. La nueva magnitud230 queda fuera del codec '
                           'externo1..145; el caso prueba uso nativo de historia, no transferencia de control '
                           'competente al péndulo.',
  'vida_y_dominio': 'Ramas IC01 desde E1_SOCIAL_11, y continuidad '
                    'E1_INTEGRADO_COSTO_SOCIAL_01→E1_INTEGRADO_CONTINUABLE_01T16485→E1_INTEGRADO_RECUPERACION_01T17155. '
                    'MAINadversoT3899 permanece separado.',
  'asistencia': 'Comparador, interfaces y retorno ambiental preparados; experiencia modifica material de la vida. '
                'El anfitrión ofrece oportunidades, no calcula la acción conveniente.',
  'limites': 'En193 pasos externos, retorno DEE -1232.1764 frente neutral -921.4793, fijo+2 -916.9369 y '
             'referencia aleatoria del auditor -1038.1701; las referencias nunca controlaron E1. Acumular una '
             'referencia que hace constante la acción en el rango sensorial no es política competente ni '
             'R2general.',
  'estado': 'Adquisición y utilización contextual incorporadas a capacidades/integracion_situada_01 y operaciones '
            'integrado-* con vidas identificadas; no promoción global.',
  'fuentes': ['IC-REPORT', 'IC-CALC', 'IC-ACTION', 'IC-NULL', 'IC-OMIT']},
 {'id': 'INTERMEDIA-06',
  'titulo': 'Información privada, actualización social y recuperación asistida de ambos signos',
  'funcion': 'Transmitir una relación de B, conservar un producto adquirido y volver a utilizarlo por una ruta '
             'alternativa preparada.',
  'mecanismo': 'En IC01 la información privada18/45 de B produjo señales opuestas que llegaron mediante '
               'portadores y encuentros del mismo mundo. E1 pudo usarlas después y un mensaje nuevo cambió '
               'actuaciones posteriores. Una consulta podía transformar el soporte anterior en X±Z-. Antes de las '
               'reservas se fijaron recursos genéricos de carga cero para ambas posibilidades, accesos paralelos '
               'y un decodificador común. El contenido de la recuperación dependía de la historia física; el '
               'investigador no aportó el signo, referencia ni palabra correcta.',
  'datos': ['Recuperación167:4/4 usos para cada signo; sham y ausencia de intervención0/4. Reserva tardía4/4 '
            'frente0/4; control sin contenido antiguo0/4.',
            'Los primarios explicitan fixed query boundary, oportunidades Z+ de carga cero dirigidas3ticks '
            'después a ambas continuaciones, cuatro cuadros locales y ninguna nueva enseñanza de contenido.',
            'La línea continuable acumuló193 pasos Pendulum y168 usos sociales; la reserva externa '
            'posterior202pasos incluye199 del episodio1 y3 tras reset explícito del entorno, sin reset DEE.'],
  'controles_y_negativos': 'SinB, corte de mensaje ya formado, desacoplamiento y sham distinguen transmisión de '
                           'causa común; lectores vacíos simultáneos separan contenido adquirido de una polaridad '
                           'aportada. Algunos cortes sociales no pudieron realizarse por ocupación y se conservan '
                           'como fuera de dominio, no ablaciones exitosas.',
  'vida_y_dominio': 'E1_INTEGRADO_RECUPERACION_01T17155 y ramas de signosopuestos; no segunda mente completa por '
                    'cada región receptora. Uso social y referencia adquirida coexistieron en vidas concretas, no '
                    'por suma de todas las ramas.',
  'asistencia': 'Canales, lectores y recursos paralelos son P0/R0. El operador inicia la recuperación y el '
                'calendario; el signo proviene del antiguo soporte adquirido. El nombre histórico '
                'GENERIC_RECOVERY_R2 de un fichero no demuestra R2.',
  'limites': 'No se demostró diagnóstico propio del fallo, iniciativa autónoma, lenguaje general, negociación o '
             'composición productiva. Los cuatro lectores sociales antiguos se perdieron al final aunque '
             'sobrevivieron comparaciones revisadas. La asistencia no repara información que convergió a un '
             'estado causal común.',
  'estado': 'integrado-recuperar-social y operaciones estado/experiencia/continuar/panel/externo incorporadas; '
            'recuperación asistida oficial dentro de ese dominio, preservando el activo protegido y futuro '
            'adverso.',
  'fuentes': ['IC-REPORT', 'IC-CALC', 'IC-RECP', 'IC-RECM', 'IC-SHAM']},
 {'id': 'INTERMEDIA-07',
  'titulo': 'Aprendizaje escalar que mejora decisiones útiles dentro de una tarea definida',
  'funcion': 'Modificar una actuación posterior a partir del desgaste causado por la acción propia, con utilidad '
             'contrastada.',
  'mecanismo': 'Ciclo02 ofreció una puerta ambiental con fuerza observable y resistencia que cambiaba al intentar '
               'actuar. La transducción devolvía sólo desgaste realmente ocurrido, no resistencia oculta, acción '
               'correcta ni utilidad del auditor. La consecuencia se sumó físicamente a una referencia nativa. '
               'Con la misma arquitectura, la experiencia cambió el intento posterior o la retirada. Es un avance '
               'respecto de IC01: además de cambiar referencias y respuestas, la decisión fue útil según una '
               'regla ambiental fijada antes.',
  'datos': ['Recuento directo de9 filas primarias de C02_GATE_050_RETORNO:9 respuestas válidas,9 '
            'útiles,utilidad4; secuencia de referencia5,11,11,11,17,17,28,28,39.',
            'C02_GATE_051_SIN_RETORNO y053_SHAM:9 respuestas válidas cada una pero2/9útiles,utilidad-5; '
            'referencia5constante. La validez del código por sí sola no alcanza utilidad.',
            'Reservas140/141: después de desgaste6o13 se formaron referencias11o18; objeto común9 provocó '
            'acciones opuestas y útiles en sus respectivos mundos. MAIN reunió21/21acciones válidas '
            'útiles,utilidad10, en una trayectoria; no21réplicas.'],
  'controles_y_negativos': 'Acción anulada mantiene salidas nativas sin efectos útiles efectivos; omisión de '
                           'retorno y aporte equivalente fuera de ruta mantienen elección equivocada en el mundo '
                           'desgastado. Igualdad física produce dirección0carga7fuera del codec de acción: no se '
                           'rebautiza como NO.',
  'vida_y_dominio': 'E1_CICLO02_MAIN y descendientes reales de E1_INTEGRADO_RECUPERACION_01T17155,N67; la '
                    'principal terminaT21711 con pérdidas sociales. Reservas de historias alternativas son '
                    'bifurcaciones identificadas.',
  'asistencia': 'Comparador, actuador, recursos, fases y ley de desgaste preparados. Python modela ambiente y '
                'calcula utilidad sólo para el auditor; la referencia adquirida y la respuesta física salen de '
                'v27.',
  'limites': 'No aprende la ley universal del entorno ni una política general de control, no garantiza adaptación '
             'a inversiones arbitrarias y no convierte el puente Pendulum en competente. La utilidad depende de '
             'la tarea y la información disponible; costos y recursos deben compararse junto a aciertos.',
  'estado': 'Capacidad ejecutable de acción útil por consecuencias incorporada al mismo gestor, con perfil y vida '
            'explícitos. No reemplazo automático del activo ni atribución de todas las funciones históricas.',
  'fuentes': ['C2-REPORT', 'C2-CALC', 'C2-GATE', 'C2-GATE-OMIT', 'C2-GATE-SHAM', 'C2-HIST6', 'C2-HIST13']},
 {'id': 'INTERMEDIA-08',
  'titulo': 'Protección social que conserva el mensaje sin suprimir el canal vulnerable',
  'funcion': 'Reducir una expansión perjudicial asociada a back.minus.record/back.plus.record y conservar uso de '
             'información privada.',
  'mecanismo': 'El problema no se resolvió suprimiendo toda comunicación. Guardas estacionarias bloquearon la '
               'entrada y la función social, por lo que se descartaron como reparación. Dos contraflujos '
               'transitorios de carga cero, fijados antes del resultado, desviaron actividad en la ruta '
               'vulnerable mientras las entradas record y los mensajes privados seguían siendo aplicados. La '
               'comparación se repitió desde el pasado con agenda real, porque igualRAW/clocks con0eventos '
               'pendientes no era el mismo sistema que con191.',
  'datos': ['C02_COMMIT_340_PROTEGIDO y343_OPUESTO:9/9 muestras en fase correcta coinciden con el signo privado; '
            'ocupación final341/340 enT4435.',
            'Sham341 llega a297664sitios ocupados enT3899 y sólo5/7muestras válidas antes del deterioro; el '
            'control sinrecord termina340sitios enT4435.',
            '340/343 registran11 solicitudes locales cada una:10aplicadas,1rechazada por ocupación,0pendientes. '
            'No se ocultan rechazos al declarar comunicación preservada.'],
  'controles_y_negativos': 'Entradas record y protectores aplicados se contrastan con sham, ausencia de record y '
                           'signos privados opuestos. Cortar comunicación desde el inicio o instalar una guarda '
                           'que impide todo mensaje no prueba protección funcional. Los paneles130–133 '
                           'son8actualizacionesporvida,no32individuos.',
  'vida_y_dominio': 'Ramas C02 del prefijo E1T3312 y canal preparado; fase3esel dominio de lectura puntuado. Las '
                    'trayectorias protegidas y adversas se conservan separadas.',
  'asistencia': 'Protección P0 diseñada y temporizada por el investigador. B aporta contenido privado y E1 lo '
                'utiliza nativamente; no se atribuye al ente selección aprendida de protección.',
  'limites': 'El selector corporal sigue agotándose también bajo protección y en el control sinrecord. Evitar '
             'esta expansión no corrige todos los mecanismos ni acredita estabilidad ilimitada, R2 o memoria '
             'general.',
  'estado': 'Variante operativa conservada con comunicación y dominio de agenda/fase explícitos; no invalida el '
            'mecanismo anterior ni borra MAINadverso.',
  'fuentes': ['C2-REPORT', 'C2-CALC', 'C2-PROTECT', 'C2-PROTECT-SHAM', 'C2-PROTECT-OPPOSITE']},
 {'id': 'INTERMEDIA-09',
  'titulo': 'Separación triple: reutilizar soportes transformados sin fusionar vidas',
  'funcion': 'Conservar acceso a tres contribuciones adquiridas y una referencia nueva dentro de una sola '
             'continuación real.',
  'mecanismo': 'La cancelación de contribuciones opuestas y la coalescencia contextual causaban pérdidas de '
               'acceso, sin demostrar borrado de toda la historia. En C02_SEPARA_330 dos pulsos nativos de carga '
               'cero redirigieron una contribución negativa ya transformada a un lector existente y evitaron su '
               'cancelación con la positiva. La preparación no aporta el signo ni copia recuerdos. El mecanismo '
               'se incorporó como separar-soportes y se programó antes de la nueva respuesta deB. La vida '
               'operativa proviene de un padre realT20927, no de importar un estado favorable desde el '
               'control330.',
  'datos': ['En330 los primeros tres usos posteriores conservan negativo previo en z26, positivo previo en z23 y '
            'nuevo lateral. Sham331conserva sólo lateral; un pulso332conserva positivo pero no negativo.',
            'Con nueva información privada52,330pierde el lateral aunque conserva ambos previos durante nueva '
            'adquisición escalar: la reserva negativa se conserva y limita el alcance.',
            'E1_CICLO02_SEPARACION_TRIPLE_01T21711adquiere desgaste1, utiliza ambos comparadores antiguos, '
            'continúa externamente y, tras restaurar el mismo estado completo en otro proceso, utiliza cuatro '
            'veces los tres códigos. Antes de restaurar, un primer uso alcanzó sólo dos: no se elimina esa '
            'diferencia.'],
  'controles_y_negativos': 'Dos pulsos frente sham y un pulso, controles de cancelación antes de consulta tardía '
                           'y comparaciones con agendas/interfaces/recibos completos. Más tarde un lateral '
                           'ocupado y las variantes remotas no arreglan toda interferencia. Reaprender o '
                           'abrirotra rama no se presenta como retención intacta.',
  'vida_y_dominio': 'Vida E1_CICLO02_SEPARACION_TRIPLE_01T21711 y ramas diagnósticas330/331/332 separadas. '
                    'Retención01T21510,Comunicación01T22783 y capas210son especializaciones complementarias, no '
                    'una biografía compuesta artificialmente.',
  'asistencia': 'Reconexion y protección preparadasP0; signos adquiridos y uso condicionados por historiaP1. El '
                'anfitrión decide cuándo aplicar la operación; no hay recuperación iniciada autónomamente.',
  'limites': 'Tres códigos no son tres palabras ni NSM65. No hay evidencia de P2general de recuperación, ni '
             'garantía ante nueva actualización social. La reconstrucción de contenido tras pérdida causal '
             'completa no se intenta ni se reclama.',
  'estado': 'Separación triple incorporada como vida seleccionable ejecutable y contrato limitado. No promoción '
            'global: se conserva E1_SOCIAL_11 protegido, MAINadverso y perfiles complementarios.',
  'fuentes': ['C2-REPORT', 'C2-CALC', 'C2-TRIPLE', 'C2-TRIPLE-SHAM', 'C2-ONEPULSE']}]
