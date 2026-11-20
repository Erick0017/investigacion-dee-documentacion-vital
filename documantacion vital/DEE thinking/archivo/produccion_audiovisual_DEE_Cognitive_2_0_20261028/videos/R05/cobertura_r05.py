"""R05 source coverage. Import SOURCE_COVERAGE; no I/O and no engine imports.

Sources, documentary families and literal catalogue mapping only.
Final rendered visual QA is deliberately not asserted.
"""

SOURCE_COVERAGE = {'schema': 'DEE.video.R05.source_coverage.v1',
 'created_utc': '2026-10-31T06:43:19.693180+00:00',
 'scope': {'new_native_ticks': 0,
           'new_experiments': 0,
           'evidence_cut': 'CompendioR01 and ECI01/ECI02R01. Operational adoption1.26 exists but is not '
                           'silently added to the prescribed examples.',
           'claims': 'Coverage of sources and existing scene adapters only. This object does not certify final '
                     'rendered visual, subtitle, perceptual or scientific QA.',
           'full_visual_QA_complete': False,
           'catalogue_rows_are_not_independent_faculties': True,
           'not_one_shared_biography': True},
 'representation_contract': {'A': 'Visualization of retained physical records; discrete integer cuts and '
                                  'original observed fields.',
                             'B': 'Reconstruction from a documented recipe, geometry and events; unknown '
                                  'intervals use cuts, not invented measured trajectories.',
                             'C': 'Functional or conceptual illustration; drawn nodes, curves, platform layers '
                                  'and external habitat do not assert DEE microgeometry.',
                             'global_editorial_elements': 'Camera, crop, layout, floor, shadows, highlights, '
                                                          'colors, glyph radii and subtitles are editorial. No '
                                                          'claim that a graphic connector is physical matter.'},
 'sources': {'fundamentos': {'path': 'datos\\evidencia_fundamentos_R05.json',
                             'sha256': '27a85e81d28d9127ea03d411dd4fcf1c1f212f33be427cb1435c892e29545014',
                             'bytes': 1672057,
                             'kind': 'local_JSON_evidence_adapter'},
             'actual': {'path': 'datos\\evidencia_actual_R05.json',
                        'sha256': '1c7f6f0bea82a62750b445d15a4f61e7ffa7894d51645ad4c450449382dd29a1',
                        'bytes': 8194130,
                        'kind': 'local_JSON_evidence_adapter'},
             'continuidad': {'path': 'datos\\continuidad_publicada_ECI02_R05.json',
                             'sha256': '8337b2382fe04416d8d44b4b53e284679c3ccd576de31279b381376d9a76df4f',
                             'bytes': 560148,
                             'kind': 'local_JSON_evidence_adapter'},
             'actuacion_alt': {'path': 'datos\\actuacion_ALT_R05.json',
                               'sha256': '0943355fef9bcba6fbaf0c1b675fb271197e3d83553543f2d6576e16d41b9f35',
                               'bytes': 2185519,
                               'kind': 'local_JSON_evidence_adapter'},
             'agregacion': {'path': 'datos\\agregacion_FI01_R05.json',
                            'sha256': '3ce763ebfe8e20bac1397d5c86d3b95cfc7021bf7ebb48d60c54276fd210aead',
                            'bytes': 4138537,
                            'kind': 'local_JSON_evidence_adapter'},
             'historical_index': {'path': 'datos\\fuentes_historicas_R05.json',
                                  'sha256': '88471a9e36c99b586054ab31287b9ddcc063ccd3480491cbe2c454223de3c1b7',
                                  'bytes': 12709,
                                  'kind': 'archival_source_index'},
             'r04_fragment': {'path': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo '
                                      'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion vital\\DEE '
                                      'thinking\\archivo\\produccion_audiovisual_DEE_Cognitive_2_0_20261028\\videos\\revision_R04_concepto_visual\\fragmento_evidencia.json',
                              'sha256': 'cd6d7c21f7a0ea7d76ff65542b27cf380defdf622339e7ec7be377915b260924',
                              'bytes': 102891,
                              'kind': 'previous_editorial_evidence_extraction'},
             'prompt': {'path': 'C:\\Users\\Erik\\.codex\\codex-remote-attachments\\01a0921e-4727-7f93-8ad0-0b605c9afe96\\C362B742-5108-465C-AEE3-EF62F1A50C55\\1-PROMPT_CODEX_DEE_VIDEO_R05_MUNDO_3D_Y_CAPACIDADES.docx',
                        'sha256': 'b634e308c5ef4cdf301c4faba48a3b1500f11e9624cfe92c55419abf98371033',
                        'bytes': 66786,
                        'kind': 'literal_user_contract_DOCX',
                        'anchors': {'families': 'word/document.xml table0 rows1..12',
                                    'timing': 'word/document.xml table1 rows1..15',
                                    'catalogue': 'word/document.xml table2 rows1..101'}},
             'primary_CORE06_REFERENCE.json': {'path': 'datos\\primarios_historicos_R05\\CORE06_REFERENCE.json',
                                               'sha256': '3867d6fa86a3b2c90b42ddf7401785827cf5ac85b4928d525d3d9698bcc5d5e4',
                                               'bytes': 77469,
                                               'kind': 'byte_exact_archival_copy',
                                               'origin': {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador '
                                                                     'de universo '
                                                                     'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                     'vital\\DEE thinking\\CPC - Experimentos '
                                                                     'y '
                                                                     'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                          'logical_member': 'cpc8/genealogia/fuentes/3867d6fa86a3b2c90b42.json',
                                                          'sha256': '3867d6fa86a3b2c90b42ddf7401785827cf5ac85b4928d525d3d9698bcc5d5e4',
                                                          'bytes': 77469,
                                                          'origin': {'directory_cut': 'CPC8_RECONSTRUCCION_20261019_002104',
                                                                     'relative': 'genealogia/fuentes/3867d6fa86a3b2c90b42.json'}}},
             'primary_CORE06_RUNNER.py': {'path': 'datos\\primarios_historicos_R05\\CORE06_RUNNER.py',
                                          'sha256': '6f3babac1f303f340b0e83c134ac65a223cd647c5da5fcf81c5bbb9a45ee7ae9',
                                          'bytes': 11732,
                                          'kind': 'byte_exact_archival_copy',
                                          'origin': {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                                'universo '
                                                                'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                'vital\\DEE thinking\\CPC - Experimentos y '
                                                                'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                     'logical_member': 'cpc8/genealogia/fuentes/6f3babac1f303f340b0e.py',
                                                     'sha256': '6f3babac1f303f340b0e83c134ac65a223cd647c5da5fcf81c5bbb9a45ee7ae9',
                                                     'bytes': 11732,
                                                     'origin': {'directory_cut': 'CPC8_RECONSTRUCCION_20261019_002104',
                                                                'relative': 'genealogia/fuentes/6f3babac1f303f340b0e.py'}}},
             'primary_M014_AB.json': {'path': 'datos\\primarios_historicos_R05\\M014_AB.json',
                                      'sha256': '1368566e1247a84566f8ab6800b8a8271bea7a043e659e90417626c9751dff41',
                                      'bytes': 319996,
                                      'kind': 'byte_exact_archival_copy',
                                      'origin': {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                            'universo '
                                                            'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                            'vital\\DEE thinking\\CPC - Experimentos y '
                                                            'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                 'logical_member': 'historico/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/ordered_discovery/ORDERED_D01_AB/MEASUREMENTS.json',
                                                 'sha256': '1368566e1247a84566f8ab6800b8a8271bea7a043e659e90417626c9751dff41',
                                                 'bytes': 319996,
                                                 'origin': {'archive': 'CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip',
                                                            'archive_sha256': 'd31972a47f12bb574a71a14d7ddca3b7a011f320eaba37dcb2ac97abe1f4ce05',
                                                            'member': 'CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/ordered_discovery/ORDERED_D01_AB/MEASUREMENTS.json',
                                                            'crc32': '0a09b7fe'}}},
             'primary_M014_BA.json': {'path': 'datos\\primarios_historicos_R05\\M014_BA.json',
                                      'sha256': '64df28beb7caebc991104821cda8df77f7a7e323a9b22ff011d2d6fd12e22ff5',
                                      'bytes': 320006,
                                      'kind': 'byte_exact_archival_copy',
                                      'origin': {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                            'universo '
                                                            'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                            'vital\\DEE thinking\\CPC - Experimentos y '
                                                            'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                 'logical_member': 'historico/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/ordered_discovery/ORDERED_D02_BA/MEASUREMENTS.json',
                                                 'sha256': '64df28beb7caebc991104821cda8df77f7a7e323a9b22ff011d2d6fd12e22ff5',
                                                 'bytes': 320006,
                                                 'origin': {'archive': 'CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip',
                                                            'archive_sha256': 'd31972a47f12bb574a71a14d7ddca3b7a011f320eaba37dcb2ac97abe1f4ce05',
                                                            'member': 'CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/ordered_discovery/ORDERED_D02_BA/MEASUREMENTS.json',
                                                            'crc32': '84aacd90'}}},
             'primary_NRD05.json': {'path': 'datos\\primarios_historicos_R05\\NRD05.json',
                                    'sha256': '04fab27d8b2714ce836ce91e83fb39d6d4c371ad8109dfe0e496ef4ee6dabaf1',
                                    'bytes': 145010,
                                    'kind': 'byte_exact_archival_copy',
                                    'origin': {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo '
                                                          'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                          'vital\\DEE thinking\\CPC - Experimentos y '
                                                          'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                               'logical_member': 'ingenierias/primarios/NRD05/NRD05_HISTORY_CONDITIONED_TRANSFORMATION.json',
                                               'sha256': '04fab27d8b2714ce836ce91e83fb39d6d4c371ad8109dfe0e496ef4ee6dabaf1',
                                               'bytes': 145010,
                                               'origin': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo '
                                                         'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                         'vital\\ingenieria\\INGENIERIA_05_DEE_V27_INTEGRADA_RESULTADOS.zip!/INGENIERIA_05/05_HISTORY_CONDITIONED_TRANSFORMATION/RESULTS/NRD05_HISTORY_CONDITIONED_TRANSFORMATION.json'}},
             'primary_NRD05_ORIGINAL.npz': {'path': 'datos\\primarios_historicos_R05\\NRD05_ORIGINAL.npz',
                                            'sha256': 'b9619a3f0209fa1f2f94b8558b676abbec194d3e6d67d4c9a624f6e24a7872bd',
                                            'bytes': 659924,
                                            'kind': 'byte_exact_archival_copy',
                                            'origin': {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                                  'universo '
                                                                  'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                  'vital\\DEE thinking\\CPC - Experimentos y '
                                                                  'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                       'logical_member': 'ingenierias/primarios/NRD05/NRD05_FACTORIAL_STATES_AND_FUTURES.npz',
                                                       'sha256': 'b9619a3f0209fa1f2f94b8558b676abbec194d3e6d67d4c9a624f6e24a7872bd',
                                                       'bytes': 659924,
                                                       'origin': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                                 'universo '
                                                                 'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                 'vital\\ingenieria\\INGENIERIA_05_DEE_V27_INTEGRADA_RESULTADOS.zip!/INGENIERIA_05/05_HISTORY_CONDITIONED_TRANSFORMATION/TELEMETRY/NRD05_FACTORIAL_STATES_AND_FUTURES.npz'}},
             'primary_CPC9_RET_D01_P.json': {'path': 'datos\\primarios_historicos_R05\\CPC9_RET_D01_P.json',
                                             'sha256': '9fa447a7a5cd1c174e5828c4bb82b15019e6de376323abc422c446a9d4ea2b41',
                                             'bytes': 888788,
                                             'kind': 'byte_exact_archival_copy',
                                             'origin': {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                                   'universo '
                                                                   'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                   'vital\\DEE thinking\\CPC - Experimentos y '
                                                                   'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                        'logical_member': 'cpc9/primarios/RET_D01_P/MEDICIONES.json',
                                                        'sha256': '9fa447a7a5cd1c174e5828c4bb82b15019e6de376323abc422c446a9d4ea2b41',
                                                        'bytes': 888788,
                                                        'origin': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                                  'universo '
                                                                  'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                  'vital\\DEE thinking\\casos '
                                                                  'practicos\\trabajo_codex\\CPC9\\runs\\RUN_20261019_165651\\resultados\\retorno\\RET_D01_P\\MEDICIONES.json'}},
             'primary_CP02_REPORT.json.gz': {'path': 'datos\\primarios_historicos_R05\\CP02_REPORT.json.gz',
                                             'sha256': '1488dcde3d6f9562b3d5a4dff7d6e40a83b5983a2739871bd8b9b019987f299c',
                                             'bytes': 5702,
                                             'kind': 'byte_exact_archival_copy',
                                             'origin': {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                                   'universo '
                                                                   'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                   'vital\\DEE thinking\\CPC - Experimentos y '
                                                                   'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                        'logical_member': 'verificacion/primarios/M002_d317401bc42c9ef6.json.gz'}},
             'primary_C02_COMMIT_340_PROTEGIDO.json.gz': {'path': 'datos\\primarios_historicos_R05\\C02_COMMIT_340_PROTEGIDO.json.gz',
                                                          'sha256': '859ce4d0078af6fd257eba3c4b731c8a80a1389a7e0005357c86ba84674082c4',
                                                          'bytes': 18549,
                                                          'kind': 'byte_exact_archival_copy',
                                                          'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                                '5.0\\simulador de universo '
                                                                                'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                                'vital\\DEE thinking\\CPC - '
                                                                                'Experimentos y '
                                                                                'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                                     'logical_member': 'mecanismos/M141/primarios/C02_COMMIT_340_PROTEGIDO.json.gz'}},
             'primary_C02_COMMIT_341_SHAM.json.gz': {'path': 'datos\\primarios_historicos_R05\\C02_COMMIT_341_SHAM.json.gz',
                                                     'sha256': '61bd29fe2b1309110037adf643f9c93ec230191a40a73d36f31ca3b8a899405f',
                                                     'bytes': 16668,
                                                     'kind': 'byte_exact_archival_copy',
                                                     'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                           '5.0\\simulador de universo '
                                                                           'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                           'vital\\DEE thinking\\CPC - '
                                                                           'Experimentos y '
                                                                           'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                                'logical_member': 'mecanismos/M141/primarios/C02_COMMIT_341_SHAM.json.gz'}},
             'primary_C02_COMMIT_342_SIN_RECORD.json.gz': {'path': 'datos\\primarios_historicos_R05\\C02_COMMIT_342_SIN_RECORD.json.gz',
                                                           'sha256': '3116637f27003f4e63fa1eced07b60e42f82293cfc47ebd33ea4479c03e021ae',
                                                           'bytes': 18238,
                                                           'kind': 'byte_exact_archival_copy',
                                                           'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                                 '5.0\\simulador de universo '
                                                                                 'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                                 'vital\\DEE thinking\\CPC - '
                                                                                 'Experimentos y '
                                                                                 'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                                      'logical_member': 'mecanismos/M141/primarios/C02_COMMIT_342_SIN_RECORD.json.gz'}},
             'primary_C02_COMMIT_343_OPUESTO.json.gz': {'path': 'datos\\primarios_historicos_R05\\C02_COMMIT_343_OPUESTO.json.gz',
                                                        'sha256': '6421191ecc36aa78a591cabb8723819b1abc3f7f1b75980525444953efa0d2e2',
                                                        'bytes': 18539,
                                                        'kind': 'byte_exact_archival_copy',
                                                        'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                              '5.0\\simulador de universo '
                                                                              'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                              'vital\\DEE thinking\\CPC - '
                                                                              'Experimentos y '
                                                                              'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                                   'logical_member': 'mecanismos/M141/primarios/C02_COMMIT_343_OPUESTO.json.gz'}},
             'primary_28T_TRANSFER.json.gz': {'path': 'datos\\primarios_historicos_R05\\28T_TRANSFER.json.gz',
                                              'sha256': '3728ad0ad279fc5ae8db3078c27d9190fa079fb54de8726d89bdd653b6c24338',
                                              'bytes': 63516,
                                              'kind': 'byte_exact_archival_copy',
                                              'origin': {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                                    'universo '
                                                                    'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                    'vital\\DEE thinking\\CPC - Experimentos y '
                                                                    'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                         'logical_member': 'referencias/ENTE_DEE_EVOLUCION_02/28T_TRANSFER.json.gz'}},
             'primary_28U_TRANSFER.json.gz': {'path': 'datos\\primarios_historicos_R05\\28U_TRANSFER.json.gz',
                                              'sha256': '954e3b3eebc35b936415f4f123090149c15a1a67f4beba23e9d4cc51d2deba85',
                                              'bytes': 62648,
                                              'kind': 'byte_exact_archival_copy',
                                              'origin': {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                                    'universo '
                                                                    'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                    'vital\\DEE thinking\\CPC - Experimentos y '
                                                                    'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                         'logical_member': 'referencias/ENTE_DEE_EVOLUCION_02/28U_TRANSFER.json.gz'}},
             'primary_PENS01_SCIENTIFIC_REPORT_CONTINUATION.md': {'path': 'datos\\primarios_historicos_R05\\PENS01_SCIENTIFIC_REPORT_CONTINUATION.md',
                                                                  'sha256': '041150772aff45d258ba0508ee22cc243cd4563dc4ae419f1654c56f7e1e7a0f',
                                                                  'bytes': 5062,
                                                                  'kind': 'byte_exact_archival_copy',
                                                                  'origin': {'archive': 'D:\\GENESIS '
                                                                                        'AI\\GENESIS '
                                                                                        '5.0\\simulador de '
                                                                                        'universo '
                                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                                        'vital\\pensamiento\\PENSAMIENTO_01_DEE_V27_RESULTADOS.zip',
                                                                             'member': 'CONTINUACIONES/HISTORIA_NATIVA_ACTUALIZACION_ACCION_20261002/SCIENTIFIC_REPORT_CONTINUATION.md'}},
             'primary_PENS01_HA_INTACT.json': {'path': 'datos\\primarios_historicos_R05\\PENS01_HA_INTACT.json',
                                               'sha256': '77aea7bf0dfca335fef0a22de771107245c6da60fb32939ac7734372c39c9836',
                                               'bytes': 43549,
                                               'kind': 'byte_exact_archival_copy',
                                               'origin': {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador '
                                                                     'de universo '
                                                                     'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                     'vital\\pensamiento\\PENSAMIENTO_01_DEE_V27_RESULTADOS.zip',
                                                          'member': 'CONTINUACIONES/HISTORIA_NATIVA_ACTUALIZACION_ACCION_20261002/CASES/HA_INTACT.json'}},
             'primary_PENS01_HA_INTACT.npz': {'path': 'datos\\primarios_historicos_R05\\PENS01_HA_INTACT.npz',
                                              'sha256': '7b5ac8a8706602ce8e29fd1b867bde5e6010d0e997b0b09df37691b60ad6c419',
                                              'bytes': 163431,
                                              'kind': 'byte_exact_archival_copy',
                                              'origin': {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                                    'universo '
                                                                    'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                    'vital\\pensamiento\\PENSAMIENTO_01_DEE_V27_RESULTADOS.zip',
                                                         'member': 'CONTINUACIONES/HISTORIA_NATIVA_ACTUALIZACION_ACCION_20261002/CASES/HA_INTACT.npz'}},
             'primary_PENS01_MEASUREMENT_SUMMARY.json': {'path': 'datos\\primarios_historicos_R05\\PENS01_MEASUREMENT_SUMMARY.json',
                                                         'sha256': 'ad94a8b193312ef2f1746ab7136fd88401ddc9e3ea04bdaadc3fd01cc58a190a',
                                                         'bytes': 8752,
                                                         'kind': 'byte_exact_archival_copy',
                                                         'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\pensamiento\\PENSAMIENTO_01_DEE_V27_RESULTADOS.zip',
                                                                    'member': 'CONTINUACIONES/HISTORIA_NATIVA_ACTUALIZACION_ACCION_20261002/MEASUREMENT_SUMMARY.json'}}},
 'source_adapters_snapshot': {'escenas_apertura_r05.py': {'path': 'escenas_apertura_r05.py',
                                                          'sha256': 'bbe71bdf03129ab16667de261dd538ee99e53f7ae68d86081581d334a61685ef',
                                                          'bytes': 6096},
                              'escenas_historicas_r05.py': {'path': 'escenas_historicas_r05.py',
                                                            'sha256': '05aae74e1fb7220ae1debbe18458c4426560cedbbe74979d74eeb1e49bc5b837',
                                                            'bytes': 24450},
                              'escenas_actuales_r05.py': {'path': 'escenas_actuales_r05.py',
                                                          'sha256': 'b1b221e244dda43970f58c6e1f967bc9a0caa649f99f7534a812edde3aefec7c',
                                                          'bytes': 21506}},
 'upstream_provenance': {'fundamentos_sources': [{'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                             'universo '
                                                             'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                             'vital\\DEE thinking\\CPC - Experimentos y '
                                                             'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                  'logical_member': 'cpc8/genealogia/fuentes/3867d6fa86a3b2c90b42.json',
                                                  'sha256': '3867d6fa86a3b2c90b42ddf7401785827cf5ac85b4928d525d3d9698bcc5d5e4',
                                                  'bytes': 77469,
                                                  'origin': {'directory_cut': 'CPC8_RECONSTRUCCION_20261019_002104',
                                                             'relative': 'genealogia/fuentes/3867d6fa86a3b2c90b42.json'}},
                                                 {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                             'universo '
                                                             'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                             'vital\\DEE thinking\\CPC - Experimentos y '
                                                             'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                  'logical_member': 'cpc8/genealogia/fuentes/6f3babac1f303f340b0e.py',
                                                  'sha256': '6f3babac1f303f340b0e83c134ac65a223cd647c5da5fcf81c5bbb9a45ee7ae9',
                                                  'bytes': 11732,
                                                  'origin': {'directory_cut': 'CPC8_RECONSTRUCCION_20261019_002104',
                                                             'relative': 'genealogia/fuentes/6f3babac1f303f340b0e.py'}},
                                                 {'archive': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de '
                                                             'universo '
                                                             'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                             'vital\\DEE thinking\\CPC - Experimentos y '
                                                             'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                  'logical_member': 'sectores/core/verificaciones/CORE06_PRIMARY_TRANSITIONS.json',
                                                  'path': 'sectores/core/verificaciones/CORE06_PRIMARY_TRANSITIONS.json',
                                                  'sha256': '786f37ed6970a9e1bfd6cb8b46ffbe8c8115b34ce5daafcad686918e1584953d',
                                                  'bytes': 154484,
                                                  'storage': 'objetos/78/786f37ed6970a9e1bfd6cb8b46ffbe8c8115b34ce5daafcad686918e1584953d.gz',
                                                  'compression': 'gzip'},
                                                 {'path': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo '
                                                          'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                          'vital\\DEE '
                                                          'thinking\\archivo\\produccion_audiovisual_DEE_Cognitive_2_0_20261028\\videos\\revision_R04_concepto_visual\\fragmento_evidencia.json',
                                                  'sha256': 'cd6d7c21f7a0ea7d76ff65542b27cf380defdf622339e7ec7be377915b260924',
                                                  'bytes': 102891},
                                                 {'path': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo '
                                                          'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                          'vital\\DEE '
                                                          'thinking\\archivo\\produccion_audiovisual_DEE_Cognitive_2_0_20261028\\videos\\produccion_cientifica\\fuentes_g07\\G07_EVIDENCIA_Y_GEOMETRIA.json',
                                                  'sha256': '940ff5ff728ed971e97a63b4ab2d822873f7c425a4ab6e415c8a7b34e6019af7',
                                                  'bytes': 77679},
                                                 {'file': 'datos\\primarios_historicos_R05\\CORE06_REFERENCE.json',
                                                  'sha256': '3867d6fa86a3b2c90b42ddf7401785827cf5ac85b4928d525d3d9698bcc5d5e4',
                                                  'bytes': 77469,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'cpc8/genealogia/fuentes/3867d6fa86a3b2c90b42.json',
                                                             'sha256': '3867d6fa86a3b2c90b42ddf7401785827cf5ac85b4928d525d3d9698bcc5d5e4',
                                                             'bytes': 77469,
                                                             'origin': {'directory_cut': 'CPC8_RECONSTRUCCION_20261019_002104',
                                                                        'relative': 'genealogia/fuentes/3867d6fa86a3b2c90b42.json'}}},
                                                 {'file': 'datos\\primarios_historicos_R05\\CORE06_RUNNER.py',
                                                  'sha256': '6f3babac1f303f340b0e83c134ac65a223cd647c5da5fcf81c5bbb9a45ee7ae9',
                                                  'bytes': 11732,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'cpc8/genealogia/fuentes/6f3babac1f303f340b0e.py',
                                                             'sha256': '6f3babac1f303f340b0e83c134ac65a223cd647c5da5fcf81c5bbb9a45ee7ae9',
                                                             'bytes': 11732,
                                                             'origin': {'directory_cut': 'CPC8_RECONSTRUCCION_20261019_002104',
                                                                        'relative': 'genealogia/fuentes/6f3babac1f303f340b0e.py'}}},
                                                 {'file': 'datos\\primarios_historicos_R05\\M014_AB.json',
                                                  'sha256': '1368566e1247a84566f8ab6800b8a8271bea7a043e659e90417626c9751dff41',
                                                  'bytes': 319996,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'historico/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/ordered_discovery/ORDERED_D01_AB/MEASUREMENTS.json',
                                                             'sha256': '1368566e1247a84566f8ab6800b8a8271bea7a043e659e90417626c9751dff41',
                                                             'bytes': 319996,
                                                             'origin': {'archive': 'CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip',
                                                                        'archive_sha256': 'd31972a47f12bb574a71a14d7ddca3b7a011f320eaba37dcb2ac97abe1f4ce05',
                                                                        'member': 'CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/ordered_discovery/ORDERED_D01_AB/MEASUREMENTS.json',
                                                                        'crc32': '0a09b7fe'}}},
                                                 {'file': 'datos\\primarios_historicos_R05\\M014_BA.json',
                                                  'sha256': '64df28beb7caebc991104821cda8df77f7a7e323a9b22ff011d2d6fd12e22ff5',
                                                  'bytes': 320006,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'historico/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/ordered_discovery/ORDERED_D02_BA/MEASUREMENTS.json',
                                                             'sha256': '64df28beb7caebc991104821cda8df77f7a7e323a9b22ff011d2d6fd12e22ff5',
                                                             'bytes': 320006,
                                                             'origin': {'archive': 'CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip',
                                                                        'archive_sha256': 'd31972a47f12bb574a71a14d7ddca3b7a011f320eaba37dcb2ac97abe1f4ce05',
                                                                        'member': 'CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/ordered_discovery/ORDERED_D02_BA/MEASUREMENTS.json',
                                                                        'crc32': '84aacd90'}}},
                                                 {'file': 'datos\\primarios_historicos_R05\\NRD05.json',
                                                  'sha256': '04fab27d8b2714ce836ce91e83fb39d6d4c371ad8109dfe0e496ef4ee6dabaf1',
                                                  'bytes': 145010,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'ingenierias/primarios/NRD05/NRD05_HISTORY_CONDITIONED_TRANSFORMATION.json',
                                                             'sha256': '04fab27d8b2714ce836ce91e83fb39d6d4c371ad8109dfe0e496ef4ee6dabaf1',
                                                             'bytes': 145010,
                                                             'origin': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador '
                                                                       'de universo '
                                                                       'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                       'vital\\ingenieria\\INGENIERIA_05_DEE_V27_INTEGRADA_RESULTADOS.zip!/INGENIERIA_05/05_HISTORY_CONDITIONED_TRANSFORMATION/RESULTS/NRD05_HISTORY_CONDITIONED_TRANSFORMATION.json'}},
                                                 {'file': 'datos\\primarios_historicos_R05\\NRD05_ORIGINAL.npz',
                                                  'sha256': 'b9619a3f0209fa1f2f94b8558b676abbec194d3e6d67d4c9a624f6e24a7872bd',
                                                  'bytes': 659924,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'ingenierias/primarios/NRD05/NRD05_FACTORIAL_STATES_AND_FUTURES.npz',
                                                             'sha256': 'b9619a3f0209fa1f2f94b8558b676abbec194d3e6d67d4c9a624f6e24a7872bd',
                                                             'bytes': 659924,
                                                             'origin': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador '
                                                                       'de universo '
                                                                       'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                       'vital\\ingenieria\\INGENIERIA_05_DEE_V27_INTEGRADA_RESULTADOS.zip!/INGENIERIA_05/05_HISTORY_CONDITIONED_TRANSFORMATION/TELEMETRY/NRD05_FACTORIAL_STATES_AND_FUTURES.npz'}},
                                                 {'file': 'datos\\primarios_historicos_R05\\CPC9_RET_D01_P.json',
                                                  'sha256': '9fa447a7a5cd1c174e5828c4bb82b15019e6de376323abc422c446a9d4ea2b41',
                                                  'bytes': 888788,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'cpc9/primarios/RET_D01_P/MEDICIONES.json',
                                                             'sha256': '9fa447a7a5cd1c174e5828c4bb82b15019e6de376323abc422c446a9d4ea2b41',
                                                             'bytes': 888788,
                                                             'origin': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador '
                                                                       'de universo '
                                                                       'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                       'vital\\DEE thinking\\casos '
                                                                       'practicos\\trabajo_codex\\CPC9\\runs\\RUN_20261019_165651\\resultados\\retorno\\RET_D01_P\\MEDICIONES.json'}},
                                                 {'file': 'datos\\primarios_historicos_R05\\CP02_REPORT.json.gz',
                                                  'sha256': '1488dcde3d6f9562b3d5a4dff7d6e40a83b5983a2739871bd8b9b019987f299c',
                                                  'bytes': 5702,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'verificacion/primarios/M002_d317401bc42c9ef6.json.gz'}},
                                                 {'file': 'datos\\primarios_historicos_R05\\C02_COMMIT_340_PROTEGIDO.json.gz',
                                                  'sha256': '859ce4d0078af6fd257eba3c4b731c8a80a1389a7e0005357c86ba84674082c4',
                                                  'bytes': 18549,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'mecanismos/M141/primarios/C02_COMMIT_340_PROTEGIDO.json.gz'}},
                                                 {'file': 'datos\\primarios_historicos_R05\\C02_COMMIT_341_SHAM.json.gz',
                                                  'sha256': '61bd29fe2b1309110037adf643f9c93ec230191a40a73d36f31ca3b8a899405f',
                                                  'bytes': 16668,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'mecanismos/M141/primarios/C02_COMMIT_341_SHAM.json.gz'}},
                                                 {'file': 'datos\\primarios_historicos_R05\\C02_COMMIT_342_SIN_RECORD.json.gz',
                                                  'sha256': '3116637f27003f4e63fa1eced07b60e42f82293cfc47ebd33ea4479c03e021ae',
                                                  'bytes': 18238,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'mecanismos/M141/primarios/C02_COMMIT_342_SIN_RECORD.json.gz'}},
                                                 {'file': 'datos\\primarios_historicos_R05\\C02_COMMIT_343_OPUESTO.json.gz',
                                                  'sha256': '6421191ecc36aa78a591cabb8723819b1abc3f7f1b75980525444953efa0d2e2',
                                                  'bytes': 18539,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'mecanismos/M141/primarios/C02_COMMIT_343_OPUESTO.json.gz'}},
                                                 {'file': 'datos\\primarios_historicos_R05\\28T_TRANSFER.json.gz',
                                                  'sha256': '3728ad0ad279fc5ae8db3078c27d9190fa079fb54de8726d89bdd653b6c24338',
                                                  'bytes': 63516,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'referencias/ENTE_DEE_EVOLUCION_02/28T_TRANSFER.json.gz'}},
                                                 {'file': 'datos\\primarios_historicos_R05\\28U_TRANSFER.json.gz',
                                                  'sha256': '954e3b3eebc35b936415f4f123090149c15a1a67f4beba23e9d4cc51d2deba85',
                                                  'bytes': 62648,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\DEE thinking\\CPC - '
                                                                        'Experimentos y '
                                                                        'mecanismos\\DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',
                                                             'logical_member': 'referencias/ENTE_DEE_EVOLUCION_02/28U_TRANSFER.json.gz'}},
                                                 {'file': 'datos\\primarios_historicos_R05\\PENS01_SCIENTIFIC_REPORT_CONTINUATION.md',
                                                  'sha256': '041150772aff45d258ba0508ee22cc243cd4563dc4ae419f1654c56f7e1e7a0f',
                                                  'bytes': 5062,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\pensamiento\\PENSAMIENTO_01_DEE_V27_RESULTADOS.zip',
                                                             'member': 'CONTINUACIONES/HISTORIA_NATIVA_ACTUALIZACION_ACCION_20261002/SCIENTIFIC_REPORT_CONTINUATION.md'}},
                                                 {'file': 'datos\\primarios_historicos_R05\\PENS01_HA_INTACT.json',
                                                  'sha256': '77aea7bf0dfca335fef0a22de771107245c6da60fb32939ac7734372c39c9836',
                                                  'bytes': 43549,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\pensamiento\\PENSAMIENTO_01_DEE_V27_RESULTADOS.zip',
                                                             'member': 'CONTINUACIONES/HISTORIA_NATIVA_ACTUALIZACION_ACCION_20261002/CASES/HA_INTACT.json'}},
                                                 {'file': 'datos\\primarios_historicos_R05\\PENS01_HA_INTACT.npz',
                                                  'sha256': '7b5ac8a8706602ce8e29fd1b867bde5e6010d0e997b0b09df37691b60ad6c419',
                                                  'bytes': 163431,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\pensamiento\\PENSAMIENTO_01_DEE_V27_RESULTADOS.zip',
                                                             'member': 'CONTINUACIONES/HISTORIA_NATIVA_ACTUALIZACION_ACCION_20261002/CASES/HA_INTACT.npz'}},
                                                 {'file': 'datos\\primarios_historicos_R05\\PENS01_MEASUREMENT_SUMMARY.json',
                                                  'sha256': 'ad94a8b193312ef2f1746ab7136fd88401ddc9e3ea04bdaadc3fd01cc58a190a',
                                                  'bytes': 8752,
                                                  'origin': {'archive': 'D:\\GENESIS AI\\GENESIS '
                                                                        '5.0\\simulador de universo '
                                                                        'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                        'vital\\pensamiento\\PENSAMIENTO_01_DEE_V27_RESULTADOS.zip',
                                                             'member': 'CONTINUACIONES/HISTORIA_NATIVA_ACTUALIZACION_ACCION_20261002/MEASUREMENT_SUMMARY.json'}}],
                         'r04_fragment_sources': [{'path': 'archivo/DEE_Cognitive_2_0_historial_presentacion_R01/videos/datos/DEMO_PARTE_A/resultados/a13_clasifica.json.gz',
                                                   'sha256': 'edef1ed28b9517ff11fa3666e591621c2064d32334c53caaae0e867e5a918a90',
                                                   'bytes': 5464,
                                                   'locator': '/job/result/request/result [JSON-string decode] '
                                                              '/result/rows/0',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE_Cognitive_2_0_historial_presentacion_R01/videos/datos/DEMO_PARTE_A/resultados/a21_revision.json.gz',
                                                   'sha256': '8108349009976c3c31d492781834e5c530aa2a95e92134b57c754b8e8221da9c',
                                                   'bytes': 5103,
                                                   'locator': '/job/result/request/result [JSON-string decode] '
                                                              '/result/rows/0',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE_Cognitive_2_0_historial_presentacion_R01/videos/datos/DEMO_PARTE_A/resultados/a22_revision_use.json.gz',
                                                   'sha256': 'b2bcf193a02e441b3d36b1e9a6c0d66ea256f82aaada747fd23d8805dc1302b4',
                                                   'bytes': 5548,
                                                   'locator': '/job/result/request/result [JSON-string decode] '
                                                              '/result/rows/0',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE_Cognitive_2_0_historial_presentacion_R01/videos/datos/DEMO_PARTE_B/resultados/b09_revision.json.gz',
                                                   'sha256': '4b44f9ddd75434472e19b730a9602d05f77e913cdc79cbab5a42795690bd5325',
                                                   'bytes': 5475,
                                                   'locator': '/job/result/request/result [JSON-string decode] '
                                                              '/result/rows/0',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE_Cognitive_2_0_historial_presentacion_R01/videos/datos/DEMO_PARTE_A_CONTINUACION_R02/resultados/a26_composition.json.gz',
                                                   'sha256': '64809c609cfe4b3963e7695b4d048aad8ae12f7cff2b173bff6c7cdbfd7378ad',
                                                   'bytes': 25624,
                                                   'locator': '/job/result/request/result [JSON-string decode] '
                                                              '/result/rows/0',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE_Cognitive_2_0_historial_presentacion_R01/videos/datos/DEMO_PARTE_A_CONTINUACION_R02/resultados/a44_save.json.gz',
                                                   'sha256': 'dde4de86de7eacceefe7872705953750afac9f19566a0c8528d11be851bf3407',
                                                   'bytes': 1169,
                                                   'locator': '/job/result',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE_Cognitive_2_0_historial_presentacion_R01/videos/datos/DEMO_PARTE_B/resultados/b02_reopen.json.gz',
                                                   'sha256': '680703fbf711b3f74d3c187ac7287c091ca53315cbd413bf2a3622d61081e4cc',
                                                   'bytes': 4262,
                                                   'locator': '/job/result/owner/observation',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos/produccion_cientifica/fuentes_g07/G07_EVIDENCIA_Y_GEOMETRIA.json',
                                                   'sha256': '940ff5ff728ed971e97a63b4ab2d822873f7c425a4ab6e415c8a7b34e6019af7',
                                                   'bytes': 77679,
                                                   'locator': '/causal_events; /paths; /limits',
                                                   'coverage': 'complete geometry JSON inspected, derived '
                                                               'versus retained status preserved'},
                                                  {'path': 'archivo/produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos/produccion_cientifica/fuentes_g07/VERIFICACION_EDITORIAL_LINUX_original.json',
                                                   'sha256': 'a958693e02a9557a465f6a2154817537d65fc1937227ecad4071720851f76ad5',
                                                   'bytes': 15385,
                                                   'locator': '/groups/07/examples/0; /groups/08',
                                                   'coverage': 'selected groups07/08 inspected'},
                                                  {'path': 'archivo/produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos/produccion_cientifica/fuentes_g07/C6H04_compositional_translation_holdout_original.json',
                                                   'sha256': '3f61ead2415dcf75a45e18c8089ecec45f8956d36aee1e16cbe53afea879fb98',
                                                   'bytes': 285813,
                                                   'locator': '/cases/0; /cases/1',
                                                   'coverage': 'first positive and omitted cases inspected; no '
                                                               'whole300case re-audit'},
                                                  {'path': 'archivo/produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos/produccion_cientifica/fuentes_g07/verificar_dee_original.py',
                                                   'sha256': '335fecb46c45612a3eece53b907850751b499204d6324f8a88d463d5b0ac5b89',
                                                   'bytes': 20637,
                                                   'locator': 'L134-157 (g07 and g08); source text only',
                                                   'coverage': 'source segment read, not executed'},
                                                  {'path': 'archivo/produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos/produccion_cientifica/R03/fuentes_extraidas/amplitud.json',
                                                   'sha256': '6b9dd533765244dd11597952eee1aaf9687e371fb269393e82f5e65002cc349a',
                                                   'bytes': 4499072,
                                                   'locator': '/aa46; /ciclo02; /aggregate128; /apd03',
                                                   'coverage': 'existing extracted selected fields, '
                                                               'cross-checked below with source primaries'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/USO_INMEDIATO_RECUPERADO_46/plus/PRIMARIOS.json.gz',
                                                   'sha256': 'f546584ac77218c22468b1964cd3d5cb026bafb14e105937c7c11cf181400059',
                                                   'bytes': 119959,
                                                   'locator': '/stages/*/answer/CONTENT_CODES; '
                                                              '/second_preparation; '
                                                              '/later_content_teacher_inputs; '
                                                              '/prepared_redundancy',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/USO_INMEDIATO_RECUPERADO_46/minus/PRIMARIOS.json.gz',
                                                   'sha256': '9ef1992e9a5e030953d78497c806072e7a2e3175f7085439af07d676bf033be7',
                                                   'bytes': 119960,
                                                   'locator': '/stages/*/answer/CONTENT_CODES; '
                                                              '/second_preparation; '
                                                              '/later_content_teacher_inputs; '
                                                              '/prepared_redundancy',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/CONTROLES_USO_INMEDIATO_47/plus_no_access_teaching/PRIMARIOS.json.gz',
                                                   'sha256': '1122c9df9861aed020c1b7003c3f62892ccdc739f518226fdca38235b5828c5d',
                                                   'bytes': 119593,
                                                   'locator': '/stages/*/answer/CONTENT_CODES; '
                                                              '/later_content_teacher_inputs',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/CONTROLES_USO_INMEDIATO_47/plus_no_backup/PRIMARIOS.json.gz',
                                                   'sha256': '13553df512b87e4bd46680db8d5b4f2474893aaa8004eba4c0cc6c4edd7630b7',
                                                   'bytes': 119860,
                                                   'locator': '/stages/*/answer/CONTENT_CODES; '
                                                              '/later_content_teacher_inputs',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/CONTROLES_USO_INMEDIATO_47/plus_cut_backup/PRIMARIOS.json.gz',
                                                   'sha256': '1da3a6b7634d76b48b64b8731d5c2ae988847f3eeb1c5872e320a2c099e26a85',
                                                   'bytes': 120043,
                                                   'locator': '/stages/*/answer/CONTENT_CODES; '
                                                              '/later_content_teacher_inputs',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/CONTROLES_USO_INMEDIATO_47/plus_sham_backup/PRIMARIOS.json.gz',
                                                   'sha256': '8239c5af4b7783c4fbca9384ce75325b44f0a61d250943ab0f3b8663b755376b',
                                                   'bytes': 120151,
                                                   'locator': '/stages/*/answer/CONTENT_CODES; '
                                                              '/later_content_teacher_inputs',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/CONTROLES_USO_INMEDIATO_47/minus_no_access_teaching/PRIMARIOS.json.gz',
                                                   'sha256': 'ed23b99d10344ae69b9f55085f3460bd9153b59319c9e183aea2df291558ff9d',
                                                   'bytes': 119603,
                                                   'locator': '/stages/*/answer/CONTENT_CODES; '
                                                              '/later_content_teacher_inputs',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/CONTROLES_USO_INMEDIATO_47/minus_no_backup/PRIMARIOS.json.gz',
                                                   'sha256': '6e90f6e334e564a39c35b37798374ee9a09056d9f20ff70f05d8a118802c8094',
                                                   'bytes': 119856,
                                                   'locator': '/stages/*/answer/CONTENT_CODES; '
                                                              '/later_content_teacher_inputs',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/CONTROLES_USO_INMEDIATO_47/minus_cut_backup/PRIMARIOS.json.gz',
                                                   'sha256': '14875d0b39751d112799d0d5b8d8fb773e40d5f8abb68416b97cf4ba3c71587b',
                                                   'bytes': 120041,
                                                   'locator': '/stages/*/answer/CONTENT_CODES; '
                                                              '/later_content_teacher_inputs',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/ACCESO_ADAPTATIVO_01/CONTROLES_USO_INMEDIATO_47/minus_sham_backup/PRIMARIOS.json.gz',
                                                   'sha256': '97c17348d0f9a5d09841b07caeaffad289f5f03452d184b73f66014ca1e0f0df',
                                                   'bytes': 120136,
                                                   'locator': '/stages/*/answer/CONTENT_CODES; '
                                                              '/later_content_teacher_inputs',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_GATE_050_RETORNO.json',
                                                   'sha256': '832f229b3a053c6021268406918500abb3b46b07e4ee6cb48585bf71570e4ed4',
                                                   'bytes': 131907,
                                                   'locator': '/data/result/rows/0..8',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_GATE_051_SIN_RETORNO.json',
                                                   'sha256': 'a939cded6e671ef7418af8f42c52cdfc15be29639a26ad4a16e74756c15f5f55',
                                                   'bytes': 107599,
                                                   'locator': '/data/result/rows/0..8',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_GATE_052_ACCION_ANULADA.json',
                                                   'sha256': '4a1e8d5ce4dec920f4f08d4886fc36423fa6a3d1ecbc7431d0242f41a3511343',
                                                   'bytes': 131972,
                                                   'locator': '/data/result/rows/0..8',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/C02_GATE_053_SHAM.json',
                                                   'sha256': 'b569c5efb14990a8c5956991b8ce50789e9591673ef6d6d87ad4c340ad84eb57',
                                                   'bytes': 131288,
                                                   'locator': '/data/result/rows/0..8',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento/B05_CONTROLS_R3_N128/ref_sham_zero.json.gz',
                                                   'sha256': 'df421c9475ea73317348c9eb5ac535a2caa8eb6cd5ed2a9367e5d82d135ac660',
                                                   'bytes': 36980,
                                                   'locator': '/result/initial; /result/raw_components; '
                                                              '/result/reader',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento/B05_CONTROLS_R3_N128/ref_sham_two.json.gz',
                                                   'sha256': '92bdae48a880ce3e9cdfd06f0b217249c48a236b92910c844b71975a2b4ab229',
                                                   'bytes': 37038,
                                                   'locator': '/result/initial; /result/raw_components; '
                                                              '/result/reader',
                                                   'coverage': 'selected primary fields inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/exportacion/CIERRE_MAIN_APD03_R01/EVIDENCIA_MAIN/EVENTOS/014_material.json.gz',
                                                   'sha256': '4c4b3caa99a199ead485cda5204d9d9d4c7be4b5a1ce95348313899d58a54cd8',
                                                   'bytes': 7024,
                                                   'locator': '/decoded_result/result/rows/0',
                                                   'coverage': 'selected row/fields inspected; no Native '
                                                               'execution'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/exportacion/CIERRE_MAIN_APD03_R01/EVIDENCIA_MAIN/EVENTOS/015_material.json.gz',
                                                   'sha256': '5e2a9f0c07f747f0b287fca59d7e6f2bf6a2b3f4ede8cb1a67b980bfebee3a61',
                                                   'bytes': 7023,
                                                   'locator': '/decoded_result/result/rows/0',
                                                   'coverage': 'selected row/fields inspected; no Native '
                                                               'execution'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/exportacion/CIERRE_MAIN_APD03_R01/EVIDENCIA_MAIN/EVENTOS/016_material.json.gz',
                                                   'sha256': 'e0b82ee51de8a451c3c547292421091fceccc71cb54f31c7e88c8cc78223db15',
                                                   'bytes': 12103,
                                                   'locator': '/decoded_result/result/rows/0',
                                                   'coverage': 'selected row/fields inspected; no Native '
                                                               'execution'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/exportacion/CIERRE_MAIN_APD03_R01/EVIDENCIA_MAIN/EVENTOS/017_material.json.gz',
                                                   'sha256': '9eb067811c2092a35408cccfa400a3f2c83975abda0fb5ed943483d1192e8408',
                                                   'bytes': 11856,
                                                   'locator': '/decoded_result/result/rows/0',
                                                   'coverage': 'selected row/fields inspected; no Native '
                                                               'execution'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/exportacion/CIERRE_MAIN_APD03_R01/EVIDENCIA_MAIN/EVENTOS/022_material.json.gz',
                                                   'sha256': '6f333426443caa3ea5f6d6499638a80a107518d91bd8d9805267131a3f1c30c4',
                                                   'bytes': 34175,
                                                   'locator': '/decoded_result/result/rows/0',
                                                   'coverage': 'selected row/fields inspected; no Native '
                                                               'execution'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/exportacion/CIERRE_MAIN_APD03_R01/EVIDENCIA_MAIN/EVENTOS/024_material.json.gz',
                                                   'sha256': '3b884d930293fde263912f7441b28e07ea9e9094bdb5795e923438ed29010d6f',
                                                   'bytes': 45053,
                                                   'locator': '/decoded_result/result/rows/0',
                                                   'coverage': 'selected row/fields inspected; no Native '
                                                               'execution'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/exportacion/CIERRE_MAIN_APD03_R01/EVIDENCIA_MAIN/EVENTOS/047_material.json.gz',
                                                   'sha256': 'eb19f9e068065ab5432d98d050e54ca81eb46e9fc9ff54e476fb4adec2edd64f',
                                                   'bytes': 34182,
                                                   'locator': '/decoded_result/result/rows/0',
                                                   'coverage': 'selected row/fields inspected; no Native '
                                                               'execution'},
                                                  {'path': 'archivo/produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos/produccion_cientifica/R03/fuentes_extraidas/comunicacion.json',
                                                   'sha256': '818e65d665bcbb13f19dc5efcbc1748ac40bdd530a381854480068fb25cdae18',
                                                   'bytes': 114325,
                                                   'locator': '/events; /same_first_opportunity; '
                                                              '/subsequent_uses; /physical_message',
                                                   'coverage': 'existing extraction, primary fields checked '
                                                               'next'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/LATE_SOCIAL_OPPOSITE_166.json',
                                                   'sha256': '3eeabc39aec8a4dc9d510675029e9a93dd6750a74462a1e5a5c2bbffd4b908f7',
                                                   'bytes': 6766619,
                                                   'locator': '/result/new_social_progress/source; '
                                                              '/result/external/rows/1',
                                                   'coverage': 'selected message and first-use fields '
                                                               'inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/LATE_SOCIAL_NO_NEW_B_166.json',
                                                   'sha256': '0638358b23d6eb7ed040e1b4ee2b47c38aa87253cc1fad0c26094a819a3b39de',
                                                   'bytes': 322682,
                                                   'locator': '/result/new_social_progress/source; '
                                                              '/result/external/rows/1',
                                                   'coverage': 'selected message and first-use fields '
                                                               'inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/LATE_SOCIAL_CUT_OPPOSITE_166.json',
                                                   'sha256': '59507bf5c058491884da68e3410ddd46815fbc1820594a0463f4acf8d40fa930',
                                                   'bytes': 326553,
                                                   'locator': '/result/new_social_progress/source; '
                                                              '/result/external/rows/1',
                                                   'coverage': 'selected message and first-use fields '
                                                               'inspected'},
                                                  {'path': 'archivo/DEE Cognitive System '
                                                           '1.1/evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/LATE_SOCIAL_SHAM_OPPOSITE_166.json',
                                                   'sha256': 'cac5f8a0d59b4cca24c4ad9c960f446eeb45a0af3431c72a351ef473fe8e6486',
                                                   'bytes': 6769415,
                                                   'locator': '/result/new_social_progress/source; '
                                                              '/result/external/rows/1',
                                                   'coverage': 'selected message and first-use fields '
                                                               'inspected'}],
                         'actual_continuity_and_action_primaries': [{'adapter_pointer': '/S04_before',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\estados\\LAB_P0\\sistema\\estado\\eci02_resultados\\ECI02_ALT_CONSOLIDADA\\E02_P01_literal_luma.json.gz',
                                                                     'sha256': '9440d772e1dd4e6fa43d608be115982e75b3b11048e143b8d2824bcb01eff7dc',
                                                                     'life': 'ECI02_ALT_CONSOLIDADA',
                                                                     'label': 'E02_P01_literal_luma',
                                                                     'before_tick': 713688,
                                                                     'after_tick': 713758,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S04_teacher',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\estados\\LAB_P0\\sistema\\estado\\eci02_resultados\\ECI02_L_MINUS\\L_MINUS_HISTORIA.json.gz',
                                                                     'sha256': '30099f9d63e16403ef51c58611d2fd613cf470d3346abd20332a40f83e5d9ffc',
                                                                     'life': 'ECI02_L_MINUS',
                                                                     'label': 'L_MINUS_HISTORIA',
                                                                     'before_tick': 719846,
                                                                     'after_tick': 719851,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S04_after',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\estados\\LAB_P0\\sistema\\estado\\eci02_resultados\\ECI02_L_MINUS\\L_MINUS_USO_COMUN.json.gz',
                                                                     'sha256': 'cd996b941a4ad32ddb41faf695b572b43cbc5430049ca59aab82de49654f4770',
                                                                     'life': 'ECI02_L_MINUS',
                                                                     'label': 'L_MINUS_USO_COMUN',
                                                                     'before_tick': 719851,
                                                                     'after_tick': 719989,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S04_ret_nara',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\estados\\LAB_P0\\sistema\\estado\\eci02_resultados\\ECI02_L_MINUS\\L_MINUS_RET_NARA.json.gz',
                                                                     'sha256': '34d640d2641efde3a8d867e64c67adf96e1200bca24d4ddd611887818d2003b4',
                                                                     'life': 'ECI02_L_MINUS',
                                                                     'label': 'L_MINUS_RET_NARA',
                                                                     'before_tick': 720190,
                                                                     'after_tick': 720257,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S04_ret_MA',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\estados\\LAB_P0\\sistema\\estado\\eci02_resultados\\ECI02_L_MINUS\\L_MINUS_RET_MA.json.gz',
                                                                     'sha256': 'e1b56e4dda3bcbcc0c1392a4662e04bc5227697c65c18f070c32578f7a5c3a96',
                                                                     'life': 'ECI02_L_MINUS',
                                                                     'label': 'L_MINUS_RET_MA',
                                                                     'before_tick': 720257,
                                                                     'after_tick': 720324,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S13_plus',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\estados\\LAB_P0\\sistema\\estado\\eci02_resultados\\ECI02_L_PLUS\\L_PLUS_USO_COMUN.json.gz',
                                                                     'sha256': 'a5d08bd6d4f753904f32018ae33c696e6875b97489b0094bd80f2473612f91dd',
                                                                     'life': 'ECI02_L_PLUS',
                                                                     'label': 'L_PLUS_USO_COMUN',
                                                                     'before_tick': 719851,
                                                                     'after_tick': 719938,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S13_minus_reserved',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\estados\\LAB_P0\\sistema\\estado\\eci02_resultados\\ECI02_L_MINUS\\L_MINUS_RESERVA.json.gz',
                                                                     'sha256': 'd110bd25e98de817287bd3dccaaa5701f9f5737cec008625dcf283c48c83cd87',
                                                                     'life': 'ECI02_L_MINUS',
                                                                     'label': 'L_MINUS_RESERVA',
                                                                     'before_tick': 720056,
                                                                     'after_tick': 720190,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S09_neutral',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\estados\\LAB_P0\\sistema\\estado\\eci02_resultados\\ECI02_ALT_CONSOLIDADA\\E02_P08_P0_neutral.json.gz',
                                                                     'sha256': '92c6f2ce6ade339c231ad5f5fef767df298f00f24cd9c5e25f3adda2f342def4',
                                                                     'life': 'ECI02_ALT_CONSOLIDADA',
                                                                     'label': 'E02_P08_P0_neutral',
                                                                     'before_tick': 714422,
                                                                     'after_tick': 714620,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S09_probe_on',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\estados\\LAB_P0\\sistema\\estado\\eci02_resultados\\ECI02_D_R04_ON\\RD_ON_TRAZA.json.gz',
                                                                     'sha256': '0d8419ad926d032d4cabed02fa7d129996ddbcd9bb09b4306d5491c38a07d253',
                                                                     'life': 'ECI02_D_R04_ON',
                                                                     'label': 'RD_ON_TRAZA',
                                                                     'before_tick': 721058,
                                                                     'after_tick': 721561,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S09_probe_off',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\estados\\LAB_P0\\sistema\\estado\\eci02_resultados\\ECI02_D_R04_OFF\\RD_OFF_TRAZA.json.gz',
                                                                     'sha256': '8e8fd99013197ca0277168120cf014cf80789f8d4c627d4ff89a9a536db0ed8b',
                                                                     'life': 'ECI02_D_R04_OFF',
                                                                     'label': 'RD_OFF_TRAZA',
                                                                     'before_tick': 721058,
                                                                     'after_tick': 721561,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S12_W11',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\estados\\LAB_P0\\sistema\\estado\\eci02_resultados\\ECI02_J_11\\J_11_FACTORIAL.json.gz',
                                                                     'sha256': '0d69e1ea45e4b2c09e443ffed08ed6a77b37bafea168c9ff696a157b560c9c8f',
                                                                     'life': 'ECI02_J_11',
                                                                     'label': 'J_11_FACTORIAL',
                                                                     'before_tick': 719846,
                                                                     'after_tick': 720057,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S12_W11_afterMA',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\estados\\LAB_P0\\sistema\\estado\\eci02_resultados\\ECI02_J_11\\J_11_POST_MA.json.gz',
                                                                     'sha256': '49d76046d92c8223044c827bf9949be16678876e5c341a419c154a852f3c8cb4',
                                                                     'life': 'ECI02_J_11',
                                                                     'label': 'J_11_POST_MA',
                                                                     'before_tick': 720057,
                                                                     'after_tick': 720123,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S12_W11_afterFI',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\estados\\LAB_P0\\sistema\\estado\\eci02_resultados\\ECI02_J_11\\J_11_POST_FI.json.gz',
                                                                     'sha256': 'f09202d32db0d2c9b322e0e70f3a8f8d6c77288dd95774bd724ca2cf4533a276',
                                                                     'life': 'ECI02_J_11',
                                                                     'label': 'J_11_POST_FI',
                                                                     'before_tick': 720123,
                                                                     'after_tick': 720321,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S14_direct',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\datos\\PRUEBA_ARITMETICA_DIRECTA_ECI02_R01.json',
                                                                     'sha256': 'ab6479a092dab52e581ec9ad7dd8ce7cb2070aaeff9b8d3f30662cc4a8e8506b',
                                                                     'life': 'ECI02_CONSOLIDADA_OPERATIVA',
                                                                     'label': None,
                                                                     'before_tick': None,
                                                                     'after_tick': None,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/S11_ALT_protocol',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\datos\\PROTOCOLO_ECI01_R01.json',
                                                                     'sha256': '1a6c7e3a550d8bcfd08528d43456a27f2f7b66b9ee8eeb4438539faf568a127d',
                                                                     'life': None,
                                                                     'label': None,
                                                                     'before_tick': None,
                                                                     'after_tick': None,
                                                                     'adapter': 'actual'},
                                                                    {'adapter_pointer': '/sources/0',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\datos\\PRUEBA_PUBLICACION_ECI02_R02.json',
                                                                     'sha256': '3c312d90b8f91cb2bcd729da77f37f717b7e3e3fd2fd7020d48b8042cddbbfaa',
                                                                     'life': 'ECI02_CONSOLIDADA_OPERATIVA',
                                                                     'label': None,
                                                                     'before_tick': None,
                                                                     'after_tick': None,
                                                                     'adapter': 'continuidad'},
                                                                    {'adapter_pointer': '/sources/1',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI02\\datos\\PRUEBA_PUBLICACION_P1_ECI02_R01.json',
                                                                     'sha256': '596f333446fbcf94b85e98ba820ae1e9cd4e0deab3b5e91885e0cfeb963391b8',
                                                                     'life': 'ECI02_ACCESO_REVISADO_MINUS',
                                                                     'label': None,
                                                                     'before_tick': None,
                                                                     'after_tick': None,
                                                                     'adapter': 'continuidad'},
                                                                    {'adapter_pointer': '/steps/0',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\A02_step_1.json.gz',
                                                                     'sha256': 'ea10b8942bfdedff99f041247256781b4a3510e5d6336598a197e2970cc0c6b6',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'A02_step_1',
                                                                     'before_tick': 697764,
                                                                     'after_tick': 697962,
                                                                     'adapter': 'actuacion_alt'},
                                                                    {'adapter_pointer': '/steps/1',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\A02_step_2.json.gz',
                                                                     'sha256': '3f8330aebef932d962aa45b1872486dce0e215eff7f6fe44da7015e8b6ec4a17',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'A02_step_2',
                                                                     'before_tick': 697962,
                                                                     'after_tick': 698160,
                                                                     'adapter': 'actuacion_alt'},
                                                                    {'adapter_pointer': '/steps/2',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\A02_step_3.json.gz',
                                                                     'sha256': 'a09bbe3984b591cb7423e071b8ef93f33df143fa1be62d611d5361b1aeaffe79',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'A02_step_3',
                                                                     'before_tick': 698160,
                                                                     'after_tick': 698358,
                                                                     'adapter': 'actuacion_alt'},
                                                                    {'adapter_pointer': '/steps/3',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\A02_step_4.json.gz',
                                                                     'sha256': 'c604a89cc00a02a119a830aadc029a323a9c923c94a5735d4983382bc91cc05c',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'A02_step_4',
                                                                     'before_tick': 698358,
                                                                     'after_tick': 698556,
                                                                     'adapter': 'actuacion_alt'},
                                                                    {'adapter_pointer': '/steps/4',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\A02_step_5.json.gz',
                                                                     'sha256': 'cce3599bcaafd92bda79785c33b9b8297c10cb94b46314413bfa2679725008ba',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'A02_step_5',
                                                                     'before_tick': 698556,
                                                                     'after_tick': 698754,
                                                                     'adapter': 'actuacion_alt'},
                                                                    {'adapter_pointer': '/steps/5',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\A02_step_6.json.gz',
                                                                     'sha256': '52f3c693f7e6e4127319e72a9a95addf05c30986395034c3356c7eb85e7fd70f',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'A02_step_6',
                                                                     'before_tick': 698754,
                                                                     'after_tick': 698952,
                                                                     'adapter': 'actuacion_alt'},
                                                                    {'adapter': 'actual',
                                                                     'adapter_pointer': '/S05_ALT/R07_ALT_integrated',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\R07_ALT_integrated.json.gz',
                                                                     'sha256': '9aff575295cab8da6c4377d0c24da0f6ec9d4977e30bf37e99aae03bbcae1f5b',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'R07_ALT_integrated',
                                                                     'before_tick': 701078,
                                                                     'after_tick': 702633},
                                                                    {'adapter': 'actual',
                                                                     'adapter_pointer': '/S05_ALT/R07_ALT_idle2680',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\R07_ALT_idle2680.json.gz',
                                                                     'sha256': 'f73ff074aec84f9bfa75f3d8c5cbb4dcd945557b4ea475a5cf9b828906bd0dbf',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'R07_ALT_idle2680',
                                                                     'before_tick': 702633,
                                                                     'after_tick': 705313},
                                                                    {'adapter': 'actual',
                                                                     'adapter_pointer': '/S05_ALT/R07_ALT_idle8040_1',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\R07_ALT_idle8040_1.json.gz',
                                                                     'sha256': 'f548a44f3e2bd361ee3a128fb868b9df3f0b8fd4ff603cb4082c759f81d2b0d4',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'R07_ALT_idle8040_1',
                                                                     'before_tick': 705313,
                                                                     'after_tick': 707993},
                                                                    {'adapter': 'actual',
                                                                     'adapter_pointer': '/S05_ALT/R07_ALT_idle8040_2',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\R07_ALT_idle8040_2.json.gz',
                                                                     'sha256': '337ca4694c2cb8ce975957afd7d22eb536e6428bf3f723f5b07d2cfa2a86e94f',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'R07_ALT_idle8040_2',
                                                                     'before_tick': 707993,
                                                                     'after_tick': 710673},
                                                                    {'adapter': 'actual',
                                                                     'adapter_pointer': '/S05_ALT/R07_ALT_idle8040_3',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\R07_ALT_idle8040_3.json.gz',
                                                                     'sha256': '5ca43ac2c5e021ae9a46dcfa031ff0b444a5dc3a3316b99dcef886760a3b035e',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'R07_ALT_idle8040_3',
                                                                     'before_tick': 710673,
                                                                     'after_tick': 713353},
                                                                    {'adapter': 'actual',
                                                                     'adapter_pointer': '/S05_ALT/R07_ALT_nara',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\R07_ALT_nara.json.gz',
                                                                     'sha256': '0fa8d0a08307c147c4c79f0e0a2008477dc2a2b260dde2354f93724838243050',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'R07_ALT_nara',
                                                                     'before_tick': 713353,
                                                                     'after_tick': 713423},
                                                                    {'adapter': 'actual',
                                                                     'adapter_pointer': '/S05_ALT/R07_ALT_alfa',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\R07_ALT_alfa.json.gz',
                                                                     'sha256': 'd9802f4daef09a902fd99f07c99bfe5888c4d2d540592aa54ea983f6bfffa91c',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'R07_ALT_alfa',
                                                                     'before_tick': 713423,
                                                                     'after_tick': 713490},
                                                                    {'adapter': 'actual',
                                                                     'adapter_pointer': '/S05_ALT/R07_ALT_balance',
                                                                     'source': 'D:\\GENESIS AI\\GENESIS '
                                                                               '5.0\\simulador de universo '
                                                                               'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                                               'vital\\DEE '
                                                                               'thinking\\archivo\\analisis_transversal_cognitivo\\ECI01\\estados\\P_COPIA_CERRADA\\sistema\\estado\\eci01_resultados\\ECI01_ACCESO_P0\\R07_ALT_balance.json.gz',
                                                                     'sha256': '02bdc07b63598bffc7fb1a0ca507821cb731b1f46fb542aed30895a6d7fe86c9',
                                                                     'life': 'ECI01_ACCESO_P0',
                                                                     'label': 'R07_ALT_balance',
                                                                     'before_tick': 713490,
                                                                     'after_tick': 713688}],
                         'agregacion_source': {'source': 'D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo '
                                                         'ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion '
                                                         'vital\\DEE '
                                                         'thinking\\archivo\\produccion_audiovisual_DEE_Cognitive_2_0_20261028\\videos\\produccion_cientifica\\R03\\fuentes_extraidas\\amplitud.json',
                                               'source_sha256': '6b9dd533765244dd11597952eee1aaf9687e371fb269393e82f5e65002cc349a',
                                               'pointer': '/aggregate128'}},
 'scenes': {'S01': {'id': 'S01',
                    'title': 'La amplitud es el mensaje',
                    'start_s': 0,
                    'end_s': 20,
                    'duration_s': 20,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 5],
                                  'representation': ['B', 'A'],
                                  'case': 'CORE06 new-query teaser',
                                  'life': 'CORE06/run_transfer/+X/trained',
                                  'cut': [12, 16],
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S03'}],
                                  'shows': 'Reuses S03 local17..22; query after historical teaching.',
                                  'limits': ['Callback provenance retained; not a current MAIN life.']},
                                 {'local_seconds': [5, 10],
                                  'representation': ['B'],
                                  'case': 'CORE06 teaching teaser',
                                  'life': 'CORE06/run_transfer/+X/trained',
                                  'cut': [0, 4],
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S03'}],
                                  'shows': 'Reuses S03 local2..7; known initial carriers and reconstructed '
                                           'meeting.',
                                  'limits': []},
                                 {'local_seconds': [10, 13],
                                  'representation': ['C', 'A'],
                                  'case': 'ECI02 revised luma teaser',
                                  'life': 'ECI02_L_MINUS',
                                  'cut': {'source_record': [719851, 719989]},
                                  'evidence': [{'source': 'actual', 'pointer': '/S04_after'}],
                                  'shows': 'Reuses S04 local18..21; conceptual relation and retained sign.',
                                  'limits': []},
                                 {'local_seconds': [13, 16],
                                  'representation': ['A'],
                                  'case': 'W11 simultaneous activity teaser',
                                  'life': 'ECI02_J_11',
                                  'cut': {'source_record': [719846, 720057]},
                                  'evidence': [{'source': 'actual', 'pointer': '/S12_W11'}],
                                  'shows': 'Reuses S12 local15..18; retained integer physical cuts.',
                                  'limits': []},
                                 {'local_seconds': [16, 20],
                                  'representation': ['B'],
                                  'case': 'CORE06 query teaser',
                                  'life': 'CORE06/run_transfer/+X/trained',
                                  'cut': [4, 12],
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S03'}],
                                  'shows': 'Reuses S03 local10..14.',
                                  'limits': []}],
                    'limits': ['The montage joins different cases and lives; it does not construct one shared '
                               'biography.']},
            'S02': {'id': 'S02',
                    'title': 'La computadora y el mecanismo son cosas distintas',
                    'start_s': 20,
                    'end_s': 44,
                    'duration_s': 24,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 11],
                                  'representation': ['C'],
                                  'case': 'Editorial neural network3-5-3',
                                  'life': None,
                                  'cut': None,
                                  'evidence': [{'source': 'prompt', 'pointer': 'table0/row1'}],
                                  'shows': 'An explicitly conceptual3-5-3 network changes three drawn '
                                           'connection weights.',
                                  'limits': ['No DEE microstate or one-to-one physical mapping.',
                                             'External conceptual reference is attribution, not DEE evidence.'],
                                  'external_concept_source': {'scene': 'S02',
                                                              'url': 'https://www.nature.com/articles/323533a0',
                                                              'DOI': '10.1038/323533a0',
                                                              'access': 'Publisher abstract read2026-10-31; '
                                                                        'connection-weight adaptation supports '
                                                                        'conceptual illustration; no private '
                                                                        'input uploaded.'}},
                                 {'local_seconds': [11, 24],
                                  'representation': ['B'],
                                  'case': 'CORE06 contrast after a cut',
                                  'life': 'CORE06/run_transfer/+X/trained',
                                  'cut': [0, 4, 12],
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S03'}],
                                  'shows': 'Reuses S03 local0..7 and8..14 after a visible editorial cut.',
                                  'limits': ['No morph or physical correspondence with the preceding '
                                             'network.']}]},
            'S03': {'id': 'S03',
                    'title': 'Aprender: una experiencia participa después',
                    'start_s': 44,
                    'end_s': 76,
                    'duration_s': 32,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 24],
                                  'representation': ['B', 'A'],
                                  'case': 'CORE06 teaching and later query',
                                  'life': 'CORE06/run_transfer/+X/trained',
                                  'cut': {'N': 41, 'events': [0, 4, 12, 16], 'A_observation': 16},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S03'},
                                               {'source': 'fundamentos', 'pointer': '/scenes/S03/events'},
                                               {'source': 'fundamentos', 'pointer': '/scenes/S03/readings'}],
                                  'shows': 'Prepared5+7 meet atT4; new query103 insertedT12; retained localT16 '
                                           'reading115.',
                                  'limits': ['No complete per-tick physical frames; use temporal cuts at '
                                             'unknown intervals.',
                                             'The omitted control has no initial teaching carriers; it is not '
                                             'the same learned life.',
                                             'Initial geometry, inputs, access time and interpretation are '
                                             'prepared; the encounter-dependent transformation is native.']},
                                 {'local_seconds': [24, 32],
                                  'representation': ['B', 'A'],
                                  'case': 'CORE06 trained versus omitted-teaching control',
                                  'life': 'CORE06/run_transfer/+X/{trained,untrained}',
                                  'cut': {'N': 41, 'query': 12, 'read': 16},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S03'}],
                                  'shows': 'Same later input103 gives115 after teaching and103 in the '
                                           'omitted-teaching world.',
                                  'limits': ['T4 support12/+Y is derived from documented recipe and rule; no '
                                             'full T4 RAW retained.',
                                             'Untrained is a separate matched world, not erasure in the '
                                             'trained life.']}]},
            'S04': {'id': 'S04',
                    'title': 'Plasticidad: revisar conservando otras relaciones',
                    'start_s': 76,
                    'end_s': 108,
                    'duration_s': 32,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 7],
                                  'representation': ['C', 'A'],
                                  'case': 'Earlier positive luma',
                                  'life': 'ECI02_ALT_CONSOLIDADA',
                                  'cut': [713688, 713758],
                                  'evidence': [{'source': 'actual', 'pointer': '/S04_before'}],
                                  'shows': 'Abstract input/relation/output followed by original retained '
                                           'reader points.',
                                  'limits': []},
                                 {'local_seconds': [7, 16],
                                  'representation': ['C', 'A'],
                                  'case': 'Review by subsequent historical input',
                                  'life': 'ECI02_L_MINUS',
                                  'cut': [719846, 719851],
                                  'evidence': [{'source': 'actual', 'pointer': '/S04_teacher'}],
                                  'shows': 'Functional luma review and retained local hub after input; not an '
                                           'invented lattice route.',
                                  'limits': []},
                                 {'local_seconds': [16, 24],
                                  'representation': ['C', 'A'],
                                  'case': 'Revised luma on common query',
                                  'life': 'ECI02_L_MINUS',
                                  'cut': [719851, 719989],
                                  'evidence': [{'source': 'actual', 'pointer': '/S04_after'}],
                                  'shows': 'Same prepared form has the revised negative response.',
                                  'limits': []},
                                 {'local_seconds': [24, 28],
                                  'representation': ['C', 'A'],
                                  'case': 'Retained nara',
                                  'life': 'ECI02_L_MINUS',
                                  'cut': [720190, 720257],
                                  'evidence': [{'source': 'actual', 'pointer': '/S04_ret_nara'}],
                                  'shows': 'Other nara relation remains usable.',
                                  'limits': []},
                                 {'local_seconds': [28, 32],
                                  'representation': ['C', 'A'],
                                  'case': 'Retained MA alfa',
                                  'life': 'ECI02_L_MINUS',
                                  'cut': [720257, 720324],
                                  'evidence': [{'source': 'actual', 'pointer': '/S04_ret_MA'}],
                                  'shows': 'Separate acquired alfa relation remains usable.',
                                  'limits': []}],
                    'limits': ['ALT and MINUS are identified historical branches; cuts do not imply one '
                               'continuous microscopic recording.',
                               'Functional curves and connectors are C; retained local RAW panels are A.']},
            'S05': {'id': 'S05',
                    'title': 'Memoria: varias formas de conservar una historia',
                    'start_s': 108,
                    'end_s': 130,
                    'duration_s': 22,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 2],
                                  'representation': ['B'],
                                  'case': 'Mobile support example',
                                  'life': 'G08',
                                  'cut': {'N': 53, 'selected': [5, 8]},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S08_G08'}],
                                  'shows': 'Known mobile support, not permanent storage at one cell.',
                                  'limits': []},
                                 {'local_seconds': [2, 4],
                                  'representation': ['A'],
                                  'case': 'Relative support example',
                                  'life': 'CP02/gate_open/paired',
                                  'cut': {'sample': 34},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S10_CP02'}],
                                  'shows': 'Relative support panel retained before the query.',
                                  'limits': []},
                                 {'local_seconds': [4, 13],
                                  'representation': ['A'],
                                  'case': 'Distributed historical conditioning',
                                  'life': 'NRD05/SEPARATED_S0',
                                  'cut': {'N': 23, 'RAW_cuts': [8, 72]},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S05_ING05'}],
                                  'shows': 'Two full retained RAW cuts; changed sites and prepared-route '
                                           'comparison.',
                                  'limits': ['Displayed difference sites are historical state differences, not '
                                             'individually established memory sites.',
                                             'The finite factorial demonstrates changed later processing. No '
                                             'word content or autonomous retrieval is identified.',
                                             'Only two retained cuts are visualized; no invented intermediate '
                                             'frames or connections.']},
                                 {'local_seconds': [13, 15],
                                  'representation': ['C'],
                                  'case': 'Archived ALT idle history',
                                  'life': 'ECI01_ACCESO_P0',
                                  'cut': {'from': 702633, 'to': 713353, 'historical_idle_ticks': 10720},
                                  'evidence': [{'source': 'actual', 'pointer': '/S05_ALT'}],
                                  'shows': 'Editorial time jump over four archived idle records.',
                                  'limits': ['No intermediate state or trajectory is fabricated.']},
                                 {'local_seconds': [15, 18],
                                  'representation': ['B', 'A'],
                                  'case': 'ALT nara before export',
                                  'life': 'ECI01_ACCESO_P0',
                                  'cut': [713353, 713423],
                                  'evidence': [{'source': 'actual', 'pointer': '/S05_ALT/R07_ALT_nara'}],
                                  'shows': 'Documented request geometry and retained observation.',
                                  'limits': ['Nara/alfa examples occurred before export; they are not '
                                             'post-reopen checks.']},
                                 {'local_seconds': [18, 20],
                                  'representation': ['C'],
                                  'case': 'Exact save and cold reopen, separate imported life',
                                  'life': 'ECI01_REAPERTURA_P0',
                                  'cut': {'save_and_open': 713886, 'reopen_ticks': 0},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S05_REOPEN'}],
                                  'shows': 'A complete saved state reopened without advancing its native '
                                           'clock.',
                                  'limits': []},
                                 {'local_seconds': [20, 22],
                                  'representation': ['A'],
                                  'case': 'Actual material use after that reopening',
                                  'life': 'ECI01_REAPERTURA_P0',
                                  'cut': {'early_zero_use': 714153},
                                  'evidence': [{'source': 'fundamentos',
                                                'pointer': '/scenes/S05_REOPEN/reopened_local_observations'},
                                               {'source': 'fundamentos', 'pointer': '/scenes/S05_REOPEN'}],
                                  'shows': 'Actual retained zero-valued early use in the reopened imported '
                                           'life.',
                                  'limits': ['A genuine zero requires a retained observation; it is not '
                                             'inferred from a missing return.']}]},
            'S06': {'id': 'S06',
                    'title': 'Composición: dos aprendizajes participan en una cadena',
                    'start_s': 130,
                    'end_s': 158,
                    'duration_s': 28,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 22],
                                  'representation': ['B'],
                                  'case': 'Two acquired translations in G07',
                                  'life': 'G07 compact historical demonstration',
                                  'cut': {'N': 67,
                                          'events': [0, 5, 10, 13, 20],
                                          'derived_middle': 23,
                                          'retained_final': 30},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S06_G07'}],
                                  'shows': 'Both supports form atT5; query20 contributes sequentially '
                                           'through+3 and+7.',
                                  'limits': ['Both learned supports form simultaneously at T5; sequential '
                                             'focus in film is editorial only.',
                                             'Intermediate23 is derived from documented recipe/rule; no '
                                             'retained G07 middle RAW.',
                                             'Final30 is retained in historical editorial execution record.',
                                             'No toroidal crossing is required in the illustrated T0..20 '
                                             'paths; do not add wraps.',
                                             'Not a recording of DEE20_DEMO_01; not the same mechanism as its '
                                             'a26 host-sequenced arithmetic.']},
                                 {'local_seconds': [22, 28],
                                  'representation': ['A'],
                                  'case': 'M014 ordered prepared encounters',
                                  'life': 'ORDERED_D01_AB / ORDERED_D02_BA',
                                  'cut': {'N': 67, 'local_observation_ticks': [11, 16, 19]},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S06_M014/AB'},
                                               {'source': 'fundamentos', 'pointer': '/scenes/S06_M014/BA'}],
                                  'shows': 'Retained observations from AB and BA arrangements.',
                                  'limits': ['AB/BA have different prepared geometries and routes; this does '
                                             'not isolate abstract order cognition.']}]},
            'S07': {'id': 'S07',
                    'title': 'Comunicación: otra experiencia puede convertirse en información',
                    'start_s': 158,
                    'end_s': 180,
                    'duration_s': 22,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 3],
                                  'representation': ['C'],
                                  'case': 'IC01 private quantity context',
                                  'life': 'IC01_LATE_SOCIAL_OPPOSITE_166',
                                  'cut': {'N': 67, 'private_value': 45},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S07_IC01'}],
                                  'shows': 'Private value45 is an editorial quantity cue, not copied as45 into '
                                           'the receiving domain.',
                                  'limits': []},
                                 {'local_seconds': [3, 13],
                                  'representation': ['A', 'C'],
                                  'case': 'IC01 transmitted sign and later local use',
                                  'life': 'IC01_LATE_SOCIAL_OPPOSITE_166',
                                  'cut': {'N': 67,
                                          'source_tick': 16562,
                                          'retained_frame_ticks': [16563,
                                                                   16564,
                                                                   16565,
                                                                   16566,
                                                                   16567,
                                                                   16568,
                                                                   16569,
                                                                   16570,
                                                                   16571,
                                                                   16572,
                                                                   16573,
                                                                   16574,
                                                                   16575,
                                                                   16576,
                                                                   16577,
                                                                   16578,
                                                                   16579,
                                                                   16580,
                                                                   16581,
                                                                   16582,
                                                                   16583,
                                                                   16584,
                                                                   16585,
                                                                   16586,
                                                                   16587,
                                                                   16588,
                                                                   16589,
                                                                   16590,
                                                                   16591,
                                                                   16592,
                                                                   16593,
                                                                   16594,
                                                                   16595,
                                                                   16596,
                                                                   16597,
                                                                   16598,
                                                                   16599,
                                                                   16600,
                                                                   16601,
                                                                   16602,
                                                                   16603,
                                                                   16604,
                                                                   16605,
                                                                   16606,
                                                                   16607,
                                                                   16608,
                                                                   16609,
                                                                   16610,
                                                                   16611,
                                                                   16612,
                                                                   16613,
                                                                   16614,
                                                                   16615,
                                                                   16616,
                                                                   16617,
                                                                   16618,
                                                                   16619],
                                          'retained_frame_count': 57,
                                          'retained_local_observation_count': 117},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S07_IC01/plan'},
                                               {'source': 'fundamentos',
                                                'pointer': '/scenes/S07_IC01/passive_local_frames'}],
                                  'shows': 'Retained local message/use observations; cuts bridge gaps.',
                                  'limits': ['Value45 is not numerically copied into E1; message encodes a '
                                             'sign through direction.',
                                             'Full and sham command0 vs no-message and cut command1 at same '
                                             'first current observation q_sin43.',
                                             'Native social signal contributes under fixed external motor '
                                             'wiring; not learned motor control, negotiation, autonomous '
                                             'interlocutor selection or decoding by host from target.']},
                                 {'local_seconds': [13, 18],
                                  'representation': ['A'],
                                  'case': 'Another case: first valid CPC9 exchange',
                                  'life': 'CPC9/RET_D01_P',
                                  'cut': {'N': 67,
                                          'retained_ticks': [143,
                                                             146,
                                                             147,
                                                             148,
                                                             149,
                                                             150,
                                                             165,
                                                             170,
                                                             204,
                                                             206,
                                                             210,
                                                             214,
                                                             215,
                                                             216,
                                                             217,
                                                             220,
                                                             221,
                                                             222,
                                                             225]},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S07_CPC9'}],
                                  'shows': 'First valid material message and its local later use.',
                                  'limits': ['Show first positive material message and its retained later use '
                                             'only.',
                                             'Later B reader inputs at213/280 were rejected; they do not '
                                             'establish successful updates.',
                                             'These are local observed sites, not a global trajectory or two '
                                             'complete minds.']},
                                 {'local_seconds': [18, 22],
                                  'representation': ['C'],
                                  'case': 'IC01 fixed functional bridge',
                                  'life': 'IC01_LATE_SOCIAL_OPPOSITE_166',
                                  'cut': None,
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S07_IC01'}],
                                  'shows': 'Sign−1 plus public native quantity+1 contributes to command0 under '
                                           'the prepared fixed bridge.',
                                  'limits': ['No invented microscopic connection, learned codec or two '
                                             'complete minds.']}]},
            'S08': {'id': 'S08',
                    'title': 'Transferencia y protección funcional',
                    'start_s': 180,
                    'end_s': 202,
                    'duration_s': 22,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 7],
                                  'representation': ['B'],
                                  'case': 'G08 zero-load relay',
                                  'life': 'G08',
                                  'cut': {'N': 53,
                                          'train': 5,
                                          'relay': 12,
                                          'query_insert': 18,
                                          'query_encounter': 23},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S08_G08'}],
                                  'shows': 'The−5 support changes route; query4 yields−1. Original support is '
                                           'consumed, not cloned.',
                                  'limits': ['Prepared zero-load routing carrier transfers usable acquired '
                                             'relation. Compact G08 is not social negotiation or a saved '
                                             'transfer into current DEE20.']},
                                 {'local_seconds': [7, 14],
                                  'representation': ['A'],
                                  'case': 'Cross-environment reuse of a prepared native function',
                                  'life': 'EO02/28T_TRANSFER',
                                  'cut': {'shown_rows': [0, 1],
                                          'start_ticks': [124809, 125591],
                                          'reader_ticks': [125496, 126278]},
                                  'evidence': [{'source': 'fundamentos',
                                                'pointer': '/scenes/S08_TRANSFER/T/rows/0'},
                                               {'source': 'fundamentos',
                                                'pointer': '/scenes/S08_TRANSFER/T/rows/1'}],
                                  'shows': 'Actual sampled domain and transaction frames.',
                                  'limits': ['The host changes the external environment; this is not '
                                             'autonomous task selection.']},
                                 {'local_seconds': [14, 16.5],
                                  'representation': ['B'],
                                  'case': 'Prepared committed counterflow inputs',
                                  'life': 'C02_COMMIT_340_PROTEGIDO',
                                  'cut': {'N': 67, 'prepared_input_ticks': [3360, 3362]},
                                  'evidence': [{'source': 'fundamentos',
                                                'pointer': '/scenes/S08_PROTECTION/prepared_inputs'}],
                                  'shows': 'Prepared zero-load counterflow input positions/directions.',
                                  'limits': []},
                                 {'local_seconds': [16.5, 22],
                                  'representation': ['A'],
                                  'case': 'Protected committed access',
                                  'life': 'C02_COMMIT_340_PROTEGIDO',
                                  'cut': {'N': 67,
                                          'sampled_ticks': [3420,
                                                            3487,
                                                            3554,
                                                            3621,
                                                            3688,
                                                            3755,
                                                            3822,
                                                            3899,
                                                            4033,
                                                            4090,
                                                            4167,
                                                            4301,
                                                            4425,
                                                            4435]},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S08_PROTECTION'}],
                                  'shows': 'Retained private-code/access samples under the existing agenda.',
                                  'limits': ['The counterflow is prepared, not acquired regulation; no '
                                             'invisible shield or deletion.']}]},
            'S09': {'id': 'S09',
                    'title': 'El acceso y el efecto de observar',
                    'start_s': 202,
                    'end_s': 230,
                    'duration_s': 28,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 9],
                                  'representation': ['C'],
                                  'case': 'AA46 alternate access to already experienced content',
                                  'life': 'AA01_USO46_plus / AA01_USO46_minus',
                                  'cut': {'first_block': [44718, 44935],
                                          'access_without_content_reteaching': [45790, 45930]},
                                  'evidence': [{'source': 'r04_fragment', 'pointer': '/aa46'}],
                                  'shows': 'Prepared redundant content, access change, later use without '
                                           'reintroducing old content.',
                                  'limits': ['An abstract functional diagram; not localization of a single '
                                             'memory particle.']},
                                 {'local_seconds': [9, 19],
                                  'representation': ['B', 'C'],
                                  'case': 'FI128 historical early point and missing later return',
                                  'life': 'ECI02_ALT_CONSOLIDADA',
                                  'cut': [714422, 714620],
                                  'evidence': [{'source': 'actual', 'pointer': '/S09_neutral'}],
                                  'shows': 'Retained early observation q+4 is distinct from the historical q+6 '
                                           'absence.',
                                  'limits': ['Missing later return is not material annihilation or an observed '
                                             'zero.']},
                                 {'local_seconds': [19, 28],
                                  'representation': ['A'],
                                  'case': 'Matched R04 observer ON/OFF retained RAW cuts',
                                  'life': 'ECI02_D_R04_ON / ECI02_D_R04_OFF',
                                  'cut': {'source_record': [721058, 721561], 'captured_frames_per_arm': 14},
                                  'evidence': [{'source': 'actual', 'pointer': '/S09_probe_on'},
                                               {'source': 'actual', 'pointer': '/S09_probe_off'}],
                                  'shows': 'Only retained RAW/clock-buffer cuts are compared.',
                                  'limits': ['Shared carrier E is not a query-specific trajectory; no complete '
                                             'causal route is invented.']}]},
            'S10': {'id': 'S10',
                    'title': 'Anticipación y secuencias temporales',
                    'start_s': 230,
                    'end_s': 250,
                    'duration_s': 20,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 8],
                                  'representation': ['A', 'C'],
                                  'case': 'CP02 past-outcome correspondence and later barrier result',
                                  'life': 'CP02/gate_open/paired',
                                  'cut': {'local_panels': [34, 37], 'emission': 37, 'external_target': 70},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S10_CP02'}],
                                  'shows': 'Retained local emitter predicts an independently occurring '
                                           'external arrival atT70.',
                                  'limits': ['Learned correspondence concerns retained past gate outcome '
                                             'class; no general forecasting claim.',
                                             'T70 is an independent external habitat outcome, not an input '
                                             'revealing the target to DEE.']},
                                 {'local_seconds': [8, 14],
                                  'representation': ['A', 'C'],
                                  'case': 'CP02 paired versus none',
                                  'life': 'CP02/gate_open/{paired,none}',
                                  'cut': {'emission': 37,
                                          'target': 70,
                                          'paired_prediction': [True],
                                          'none_prediction': [False, True]},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S10_CP02'}],
                                  'shows': 'A resolved retained prediction is contrasted with an unresolved '
                                           'set.',
                                  'limits': ['The none branch is indeterminate; it is not an erroneous '
                                             'prediction0.']},
                                 {'local_seconds': [14, 20],
                                  'representation': ['A'],
                                  'case': 'Finite prepared PENS01 sequence',
                                  'life': 'PENSAMIENTO01/HA_INTACT',
                                  'cut': {'N': 127,
                                          'RAW_cuts': [6, 12, 38, 58],
                                          'ROI': '±12 about recorded sites',
                                          'host_writes_after_T0': 0},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S10_PENS01'}],
                                  'shows': 'Four retained RAW cuts of a finite native '
                                           'consequence/program/action/query sequence.',
                                  'limits': ['Finite prepared supplies and opportunities, native dependent '
                                             'transformations. No perpetual loop.',
                                             'HA/HB do not isolate last-event identity from order; no abstract '
                                             'order cognition claim.']}]},
            'S11': {'id': 'S11',
                    'title': 'Consecuencias que modifican selecciones y acciones',
                    'start_s': 250,
                    'end_s': 274,
                    'duration_s': 24,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 15],
                                  'representation': ['C'],
                                  'case': 'Consequence-conditioned next action',
                                  'life': 'C02_GATE_050_RETORNO / C02_GATE_051_SIN_RETORNO',
                                  'cut': {'first_tick': 17376,
                                          'common_next_tick': 17510,
                                          'reference_real': [5, 11],
                                          'reference_omitted': [5, 5],
                                          'next_actions': [-1, 1]},
                                  'evidence': [{'source': 'r04_fragment', 'pointer': '/cycle02'}],
                                  'shows': 'Real/omitted consequence changes prepared reference and later '
                                           'action under common force2.',
                                  'limits': ['Functional diagram and external bridge, not a lattice trajectory '
                                             'or learned general controller.']},
                                 {'local_seconds': [15, 24],
                                  'representation': ['C'],
                                  'case': 'Actual linked ALT action cycle',
                                  'life': 'ECI01_ACCESO_P0',
                                  'cut': {'steps': 6,
                                          'external_loads': [[8, 4], [7, 5], [6, 6]],
                                          'external_total': 12},
                                  'evidence': [{'source': 'actuacion_alt', 'pointer': '/steps'},
                                               {'source': 'actual', 'pointer': '/S11_ALT_protocol'}],
                                  'shows': 'Six archived linked native commands act through the prepared '
                                           'external transducer, ending in HOLD.',
                                  'limits': ['The host encodes the public environment and applies native '
                                             'command; this is not learned motor wiring.']}]},
            'S12': {'id': 'S12',
                    'title': 'Muchas entradas y actividades en un paisaje compartido',
                    'start_s': 274,
                    'end_s': 300,
                    'duration_s': 26,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 8],
                                  'representation': ['B'],
                                  'case': 'FI01 physical source arrangement, one changed component',
                                  'life': 'FI01/ref_sham_zero / FI01/ref_sham_two',
                                  'cut': {'N': 67,
                                          'raw_sources': 128,
                                          'changed_component': 0,
                                          'change': [0, 2]},
                                  'evidence': [{'source': 'agregacion', 'pointer': '/aggregate128/pair'}],
                                  'shows': 'Frozen128-source geometry, same prepared comparison except the '
                                           'declared input component.',
                                  'limits': []},
                                 {'local_seconds': [8, 14],
                                  'representation': ['A'],
                                  'case': 'FI01 sampled propagation/readout',
                                  'life': 'FI01/ref_sham_zero / FI01/ref_sham_two',
                                  'cut': {'reader_tick': 16702, 'readouts': [-1, 1]},
                                  'evidence': [{'source': 'agregacion', 'pointer': '/aggregate128/pair'}],
                                  'shows': 'Recorded physical samples and the retained distinct readouts.',
                                  'limits': ['Views are separately labeled; translated comparison positions '
                                             'are editorial layout.']},
                                 {'local_seconds': [14, 22],
                                  'representation': ['A'],
                                  'case': 'W11 overlapping local activities',
                                  'life': 'ECI02_J_11',
                                  'cut': {'source_record': [719846, 720057],
                                          'MA_interval': [719915, 719922],
                                          'FI_interval': [719861, 719923]},
                                  'evidence': [{'source': 'actual', 'pointer': '/S12_W11'}],
                                  'shows': 'Retained full-buffer integer cuts near MA and FI, in the shared '
                                           'physical world.',
                                  'limits': ['No claim that each occupied cell is an independent memory, '
                                             'energy unit or faculty.']},
                                 {'local_seconds': [22, 24],
                                  'representation': ['A'],
                                  'case': 'W11 later MA use',
                                  'life': 'ECI02_J_11',
                                  'cut': [720057, 720123],
                                  'evidence': [{'source': 'actual', 'pointer': '/S12_W11_afterMA'}],
                                  'shows': 'Retained local MA reader use.',
                                  'limits': []},
                                 {'local_seconds': [24, 26],
                                  'representation': ['A'],
                                  'case': 'W11 later FI use',
                                  'life': 'ECI02_J_11',
                                  'cut': [720123, 720321],
                                  'evidence': [{'source': 'actual', 'pointer': '/S12_W11_afterFI'}],
                                  'shows': 'Retained FI early observation.',
                                  'limits': []}]},
            'S13': {'id': 'S13',
                    'title': 'Una señal aprendida cambia el acceso utilizado',
                    'start_s': 300,
                    'end_s': 322,
                    'duration_s': 22,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 6],
                                  'representation': ['B', 'A'],
                                  'case': 'Earlier acquired luma relation',
                                  'life': 'ECI02_ALT_CONSOLIDADA',
                                  'cut': [713688, 713758],
                                  'evidence': [{'source': 'actual', 'pointer': '/S04_before'}],
                                  'shows': 'Documented request geometry then retained local response.',
                                  'limits': []},
                                 {'local_seconds': [6, 14],
                                  'representation': ['C'],
                                  'case': 'Learned opposite signals select prepared access',
                                  'life': 'ECI02_L_PLUS / ECI02_L_MINUS',
                                  'cut': {'PLUS_record': [719851, 719938], 'MINUS_record': [719851, 719989]},
                                  'evidence': [{'source': 'actual', 'pointer': '/S13_plus'},
                                               {'source': 'actual', 'pointer': '/S04_after'}],
                                  'shows': 'Learned positive/negative signal chooses current versus MA access '
                                           'through an explicitly prepared connection.',
                                  'limits': ['Not a newly acquired routing graph, general Spanish '
                                             'comprehension or unbounded language.']},
                                 {'local_seconds': [14, 22],
                                  'representation': ['B', 'A'],
                                  'case': 'MINUS-selected memory access',
                                  'life': 'ECI02_L_MINUS',
                                  'cut': [719851, 719989],
                                  'evidence': [{'source': 'actual',
                                                'pointer': '/S04_after/recorded_result/rows/0/interaction'}],
                                  'shows': 'Known requested MA query and retained negative reader observation.',
                                  'limits': []}]},
            'S14': {'id': 'S14',
                    'title': 'Integración y continuidad de una historia',
                    'start_s': 322,
                    'end_s': 342,
                    'duration_s': 20,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 7],
                                  'representation': ['B', 'C'],
                                  'case': 'APD03 two learned forms and later first use',
                                  'life': 'APD03_MAIN',
                                  'cut': {'parent_tick': 548407, 'historical_final_tick': 604825},
                                  'evidence': [{'source': 'r04_fragment', 'pointer': '/apd03/events/0'}],
                                  'shows': 'Known acquired hubs for luma/nara followed by functional first-use '
                                           'diagrams.',
                                  'limits': ['APD03 and later ECI02 examples are distinct cases.']},
                                 {'local_seconds': [7, 14],
                                  'representation': ['C'],
                                  'case': 'Direct arithmetic and exact N0 reopening',
                                  'life': 'ECI02_CONSOLIDADA_OPERATIVA',
                                  'cut': {'initial_tick': 725081,
                                          'last_tick': 725840,
                                          'chain': ['8+3→11', '11−4→7'],
                                          'exact_reopen': True,
                                          'reopen_ticks': 0,
                                          'post_reopen_material_use_in_this_proof': False},
                                  'evidence': [{'source': 'actual', 'pointer': '/S14_direct'}],
                                  'shows': 'Actual documented arithmetic results and a saved/reopened last '
                                           'state.',
                                  'limits': ['N0 reopen itself is not a new material use or activity.',
                                             'This host-sequenced Direct chain is not the same mechanism as '
                                             'G07 native two-support composition.']},
                                 {'local_seconds': [14, 18],
                                  'representation': ['C'],
                                  'case': 'OTHER CASE: published MINUS saved/reopened',
                                  'life': 'ECI02_ACCESO_REVISADO_MINUS',
                                  'cut': {'save_and_open': 720458, 'reopen_ticks': 0},
                                  'evidence': [{'source': 'continuidad', 'pointer': '/sources/1'}],
                                  'shows': 'An explicit other-case cut to an existing MINUS publication proof.',
                                  'limits': ['The lower tick belongs to another trajectory; it does not move '
                                             'the Direct life backward.']},
                                 {'local_seconds': [18, 20],
                                  'representation': ['B', 'A'],
                                  'case': 'OTHER CASE: actual MINUS MA− use after reopen',
                                  'life': 'ECI02_ACCESO_REVISADO_MINUS',
                                  'cut': {'after_reopen_request': 720458, 'MA_read': 720589, 'end': 720592},
                                  'evidence': [{'source': 'continuidad',
                                                'pointer': '/sources/1/cycles/1/recorded_result/rows/0/interaction'}],
                                  'shows': 'Actual retained MA− reading after the MINUS reopening.',
                                  'limits': ['The literal voice is unchanged; visual evidence explicitly '
                                             'separates the cases.']}]},
            'S15': {'id': 'S15',
                    'title': 'Inteligencia funcional y propuesta de desarrollo',
                    'start_s': 342,
                    'end_s': 360,
                    'duration_s': 18,
                    'status': 'evidence_and_adapter_coverage; final_visual_QA_pending',
                    'segments': [{'local_seconds': [0, 6],
                                  'representation': ['C'],
                                  'case': 'Editorial platform layers',
                                  'life': None,
                                  'cut': None,
                                  'evidence': [{'source': 'prompt', 'pointer': 'table1/row15'}],
                                  'shows': 'Motor, tools and functional development are editorial layers.',
                                  'limits': []},
                                 {'local_seconds': [6, 8.4],
                                  'representation': ['C', 'A'],
                                  'case': 'S04 recap',
                                  'life': 'ECI02_L_MINUS',
                                  'cut': [719851, 719989],
                                  'evidence': [{'source': 'actual', 'pointer': '/S04_after'}],
                                  'shows': 'Reuses S04 post-review callback; no new trial.',
                                  'limits': []},
                                 {'local_seconds': [8.4, 10.8],
                                  'representation': ['A', 'C'],
                                  'case': 'S07 recap',
                                  'life': 'IC01_LATE_SOCIAL_OPPOSITE_166',
                                  'cut': {'N': 67, 'source_tick': 16562},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S07_IC01'}],
                                  'shows': 'Reuses a source scene callback; no new mind or episode.',
                                  'limits': []},
                                 {'local_seconds': [10.8, 13],
                                  'representation': ['A'],
                                  'case': 'S12 recap',
                                  'life': 'ECI02_J_11',
                                  'cut': [719846, 720057],
                                  'evidence': [{'source': 'actual', 'pointer': '/S12_W11'}],
                                  'shows': 'Reuses W11 recorded activity callback.',
                                  'limits': []},
                                 {'local_seconds': [13, 18],
                                  'representation': ['B', 'A', 'C'],
                                  'case': 'CORE06 finale and editorial invitation',
                                  'life': 'CORE06/run_transfer/+X/trained',
                                  'cut': {'N': 41, 'retained_read': 16},
                                  'evidence': [{'source': 'fundamentos', 'pointer': '/scenes/S03'},
                                               {'source': 'prompt', 'pointer': 'table1/row15'}],
                                  'shows': 'Retained-result recap and editorial proposal/invitation.',
                                  'limits': ['Proposal is prospective; it adds no claim of new demonstrated '
                                             'capability.']}]}},
 'families': [{'id': 1,
               'name': 'Historia y paisaje físico',
               'prompt_scenes': 'S02–S03, S09–S10',
               'prompt_target': 'Una experiencia cambia una transformación posterior.',
               'realizations': [{'scene': 'S02',
                                 'shown_realization': 'CORE06 contrast after the conceptual network'},
                                {'scene': 'S03', 'shown_realization': 'Experience-dependent103→115 versus103'},
                                {'scene': 'S09', 'shown_realization': 'AA46 access and R04 observer controls'},
                                {'scene': 'S10',
                                 'shown_realization': 'CP02/PENS01 bounded temporal organization'}],
               'scope': 'documentary family represented by identified examples; no inference of a separate '
                        'faculty for every catalogue row'},
              {'id': 2,
               'name': 'Asociaciones, revisión y retención',
               'prompt_scenes': 'S03–S05, S13',
               'prompt_target': 'Aprender, revisar una asociación y conservar otras.',
               'realizations': [{'scene': 'S03', 'shown_realization': 'CORE06 learned translation'},
                                {'scene': 'S04', 'shown_realization': 'luma review with nara/MA retention'},
                                {'scene': 'S05', 'shown_realization': 'historical conditioning and retention'},
                                {'scene': 'S13',
                                 'shown_realization': 'learned signal selecting prepared access'}],
               'scope': 'documentary family represented by identified examples; no inference of a separate '
                        'faculty for every catalogue row'},
              {'id': 3,
               'name': 'Memoria y acceso alternativo',
               'prompt_scenes': 'S05, S09',
               'prompt_target': 'Contenido anterior utilizado mediante otro acceso.',
               'realizations': [{'scene': 'S05',
                                 'shown_realization': 'mobile/relative/distributed examples plus archived idle '
                                                      'and reopened use'},
                                {'scene': 'S09',
                                 'shown_realization': 'AA46 retained content via alternate access; access '
                                                      'versus observation distinction'}],
               'scope': 'documentary family represented by identified examples; no inference of a separate '
                        'faculty for every catalogue row'},
              {'id': 4,
               'name': 'Referencias y magnitudes',
               'prompt_scenes': 'S06, S11–S12',
               'prompt_target': 'Una referencia material participa en una comparación y uso.',
               'realizations': [{'scene': 'S06',
                                 'shown_realization': 'G07 query20 with+3,+7; M014 prepared encounters'},
                                {'scene': 'S11', 'shown_realization': 'reference5→11 after consequence'},
                                {'scene': 'S12',
                                 'shown_realization': 'FI01 one-component perturbation and aggregate readout'}],
               'scope': 'documentary family represented by identified examples; no inference of a separate '
                        'faculty for every catalogue row'},
              {'id': 5,
               'name': 'Composición y reutilización',
               'prompt_scenes': 'S06, S14',
               'prompt_target': 'El producto de una transformación interviene en otra.',
               'realizations': [{'scene': 'S06',
                                 'shown_realization': 'native G07 two-support composition; distinct M014 '
                                                      'prepared routes'},
                                {'scene': 'S14',
                                 'shown_realization': 'separate host-sequenced Direct8+3→11,11−4→7'}],
               'scope': 'documentary family represented by identified examples; no inference of a separate '
                        'faculty for every catalogue row'},
              {'id': 6,
               'name': 'Comunicación e información privada',
               'prompt_scenes': 'S07–S08',
               'prompt_target': 'Mensaje recibido, utilización y protección de ruta.',
               'realizations': [{'scene': 'S07',
                                 'shown_realization': 'IC01 local private-sign transmission and first CPC9 '
                                                      'exchange'},
                                {'scene': 'S08',
                                 'shown_realization': 'prepared cross-environment transfer and committed '
                                                      'protection'}],
               'scope': 'documentary family represented by identified examples; no inference of a separate '
                        'faculty for every catalogue row'},
              {'id': 7,
               'name': 'Consecuencias, consulta y selección',
               'prompt_scenes': 'S07, S10–S11, S13',
               'prompt_target': 'La historia participa en una elección y un acceso.',
               'realizations': [{'scene': 'S07',
                                 'shown_realization': 'private sign contributes to fixed command bridge'},
                                {'scene': 'S10',
                                 'shown_realization': 'CP02 resolved/unresolved prediction and finite PENS01'},
                                {'scene': 'S11', 'shown_realization': 'consequence-conditioned next action'},
                                {'scene': 'S13', 'shown_realization': 'acquired sign selects prepared access'}],
               'scope': 'documentary family represented by identified examples; no inference of a separate '
                        'faculty for every catalogue row'},
              {'id': 8,
               'name': 'Acción, entorno y puente externo',
               'prompt_scenes': 'S11, S14',
               'prompt_target': 'La emisión tiene una consecuencia externa observable.',
               'realizations': [{'scene': 'S11',
                                 'shown_realization': 'six actual archived ALT commands alter external '
                                                      'loads8/4→6/6'},
                                {'scene': 'S14',
                                 'shown_realization': 'documented Direct first result participates as literal '
                                                      'next operand'}],
               'scope': 'documentary family represented by identified examples; no inference of a separate '
                        'faculty for every catalogue row'},
              {'id': 9,
               'name': 'Agregación, escala y cadencia',
               'prompt_scenes': 'S12',
               'prompt_target': 'Entradas que contribuyen; actividades superpuestas.',
               'realizations': [{'scene': 'S12',
                                 'shown_realization': '128 prepared sources; one changed component; W11 '
                                                      'retained overlapping activity'}],
               'scope': 'documentary family represented by identified examples; no inference of a separate '
                        'faculty for every catalogue row'},
              {'id': 10,
               'name': 'Transferencia y representación',
               'prompt_scenes': 'S08',
               'prompt_target': 'La función se traslada o una experiencia se reutiliza.',
               'realizations': [{'scene': 'S08',
                                 'shown_realization': 'G08 consumed support changes route; EO02 retained '
                                                      'environment transactions'}],
               'scope': 'documentary family represented by identified examples; no inference of a separate '
                        'faculty for every catalogue row'},
              {'id': 11,
               'name': 'Español funcional y señales',
               'prompt_scenes': 'S04, S13',
               'prompt_target': 'Señal adquirida y revisada con efecto funcional.',
               'realizations': [{'scene': 'S04',
                                 'shown_realization': 'bounded luma revision and other retained acquired '
                                                      'forms'},
                                {'scene': 'S13',
                                 'shown_realization': 'PLUS/MINUS learned signal under a prepared '
                                                      'lexical/access bridge'}],
               'scope': 'documentary family represented by identified examples; no inference of a separate '
                        'faculty for every catalogue row'},
              {'id': 12,
               'name': 'Continuidad y recuperación operativa',
               'prompt_scenes': 'S05, S14–S15',
               'prompt_target': 'Guardar, reabrir y continuar una historia completa.',
               'realizations': [{'scene': 'S05',
                                 'shown_realization': 'ECI01 imported-life save/open713886 and later actual '
                                                      'use714153'},
                                {'scene': 'S14',
                                 'shown_realization': 'Direct reopen N0 plus explicitly separate MINUS '
                                                      'post-reopen use'},
                                {'scene': 'S15',
                                 'shown_realization': 'source-backed recap and prospective platform layers'}],
               'scope': 'documentary family represented by identified examples; no inference of a separate '
                        'faculty for every catalogue row'}],
 'catalogue_mapping': [{'ID': 'M001',
                        'Mecanismo o contrato del catálogo': 'Contratos causales CP01',
                        'Escenas': 'S03, S14',
                        'Papel editorial': 'Contrato y control',
                        'scene_ids': ['S03', 'S14'],
                        'source_prompt_anchor': 'word/document.xml table2 row1',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S03', 'scenes/S14'],
                        'role_kind': 'contrato y control',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M002',
                        'Mecanismo o contrato del catálogo': 'Pronóstico por experiencia CP02',
                        'Escenas': 'S10',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S10'],
                        'source_prompt_anchor': 'word/document.xml table2 row2',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S10'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M003',
                        'Mecanismo o contrato del catálogo': 'Asociación y acción SEM01',
                        'Escenas': 'S03, S11',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S03', 'S11'],
                        'source_prompt_anchor': 'word/document.xml table2 row3',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S03', 'scenes/S11'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M004',
                        'Mecanismo o contrato del catálogo': 'Comunicación protegida ABCD',
                        'Escenas': 'S07, S08',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S07', 'S08'],
                        'source_prompt_anchor': 'word/document.xml table2 row4',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S07', 'scenes/S08'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M005',
                        'Mecanismo o contrato del catálogo': 'Composición con respaldos adquiridos',
                        'Escenas': 'S06',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S06'],
                        'source_prompt_anchor': 'word/document.xml table2 row5',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S06'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M006',
                        'Mecanismo o contrato del catálogo': 'U0 y dos formas CPC6',
                        'Escenas': 'S05, S14',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S05', 'S14'],
                        'source_prompt_anchor': 'word/document.xml table2 row6',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S05', 'scenes/S14'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M007',
                        'Mecanismo o contrato del catálogo': 'Continuidad y revisión CPC7',
                        'Escenas': 'S04, S14',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S04', 'S14'],
                        'source_prompt_anchor': 'word/document.xml table2 row7',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S04', 'scenes/S14'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M008',
                        'Mecanismo o contrato del catálogo': 'Orden contacto y magnitud MCTS',
                        'Escenas': 'S06, S12',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S06', 'S12'],
                        'source_prompt_anchor': 'word/document.xml table2 row8',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S06', 'scenes/S12'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M009',
                        'Mecanismo o contrato del catálogo': 'Repertorio opaco N131',
                        'Escenas': 'S03, S13',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S03', 'S13'],
                        'source_prompt_anchor': 'word/document.xml table2 row9',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S03', 'scenes/S13'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M010',
                        'Mecanismo o contrato del catálogo': 'Regulación contextual RCA',
                        'Escenas': 'S11',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S11'],
                        'source_prompt_anchor': 'word/document.xml table2 row10',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S11'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M011',
                        'Mecanismo o contrato del catálogo': 'Señal cuantitativa calibrada',
                        'Escenas': 'S12',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S12'],
                        'source_prompt_anchor': 'word/document.xml table2 row11',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S12'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M012',
                        'Mecanismo o contrato del catálogo': 'Contratos oficiales de thinking',
                        'Escenas': 'S15',
                        'Papel editorial': 'Plataforma',
                        'scene_ids': ['S15'],
                        'source_prompt_anchor': 'word/document.xml table2 row12',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S15'],
                        'role_kind': 'contexto de plataforma',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M013',
                        'Mecanismo o contrato del catálogo': 'Memoria basal y reescritura contextual OBP',
                        'Escenas': 'S04, S05',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S04', 'S05'],
                        'source_prompt_anchor': 'word/document.xml table2 row13',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S04', 'scenes/S05'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M014',
                        'Mecanismo o contrato del catálogo': 'Composición sensible al orden',
                        'Escenas': 'S06',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S06'],
                        'source_prompt_anchor': 'word/document.xml table2 row14',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S06'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M015',
                        'Mecanismo o contrato del catálogo': 'Flujo temporal',
                        'Escenas': 'S10',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S10'],
                        'source_prompt_anchor': 'word/document.xml table2 row15',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S10'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M016',
                        'Mecanismo o contrato del catálogo': 'Red de pregunta respuesta y uso',
                        'Escenas': 'S07',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S07'],
                        'source_prompt_anchor': 'word/document.xml table2 row16',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S07'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M017',
                        'Mecanismo o contrato del catálogo': 'Arquitecturas acopladas',
                        'Escenas': 'S12',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S12'],
                        'source_prompt_anchor': 'word/document.xml table2 row17',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S12'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M018',
                        'Mecanismo o contrato del catálogo': 'Puente de memorias relativas y móviles',
                        'Escenas': 'S05, S08',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S05', 'S08'],
                        'source_prompt_anchor': 'word/document.xml table2 row18',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S05', 'scenes/S08'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M019',
                        'Mecanismo o contrato del catálogo': 'Capacidad finita CPC5',
                        'Escenas': 'S05, S12',
                        'Papel editorial': 'Alcance y control',
                        'scene_ids': ['S05', 'S12'],
                        'source_prompt_anchor': 'word/document.xml table2 row19',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S05', 'scenes/S12'],
                        'role_kind': 'control y límite',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M020',
                        'Mecanismo o contrato del catálogo': 'Adquisición acumulativa32 y33',
                        'Escenas': 'S03, S05',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S03', 'S05'],
                        'source_prompt_anchor': 'word/document.xml table2 row20',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S03', 'scenes/S05'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M021',
                        'Mecanismo o contrato del catálogo': 'Selección revisable R14',
                        'Escenas': 'S04, S11',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S04', 'S11'],
                        'source_prompt_anchor': 'word/document.xml table2 row21',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S04', 'scenes/S11'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M022',
                        'Mecanismo o contrato del catálogo': 'Bucle nativo de vida CPC3',
                        'Escenas': 'S10',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S10'],
                        'source_prompt_anchor': 'word/document.xml table2 row22',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S10'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M023',
                        'Mecanismo o contrato del catálogo': 'Comparación central actual',
                        'Escenas': 'S12',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S12'],
                        'source_prompt_anchor': 'word/document.xml table2 row23',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S12'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M024',
                        'Mecanismo o contrato del catálogo': 'Forma móvil y acceso remoto',
                        'Escenas': 'S08, S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S08', 'S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row24',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S08', 'scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M025',
                        'Mecanismo o contrato del catálogo': 'Diagnóstico de acceso L15',
                        'Escenas': 'S09',
                        'Papel editorial': 'Diagnóstico',
                        'scene_ids': ['S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row25',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S09'],
                        'role_kind': 'diagnóstico contextual',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M026',
                        'Mecanismo o contrato del catálogo': 'Consulta por discrepancia',
                        'Escenas': 'S07, S10',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S07', 'S10'],
                        'source_prompt_anchor': 'word/document.xml table2 row26',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S07', 'scenes/S10'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M027',
                        'Mecanismo o contrato del catálogo': 'Apertura física de ausencia',
                        'Escenas': 'S07, S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S07', 'S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row27',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S07', 'scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M028',
                        'Mecanismo o contrato del catálogo': 'Retención temprana y cortes',
                        'Escenas': 'S05',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S05'],
                        'source_prompt_anchor': 'word/document.xml table2 row28',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S05'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M029',
                        'Mecanismo o contrato del catálogo': 'Retención de la forma',
                        'Escenas': 'S05',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S05'],
                        'source_prompt_anchor': 'word/document.xml table2 row29',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S05'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M030',
                        'Mecanismo o contrato del catálogo': 'Acceso tardío por historia original',
                        'Escenas': 'S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row30',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M031',
                        'Mecanismo o contrato del catálogo': 'Enseñanza social por portador',
                        'Escenas': 'S07',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S07'],
                        'source_prompt_anchor': 'word/document.xml table2 row31',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S07'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M032',
                        'Mecanismo o contrato del catálogo': 'Primer CPC8 longitudinal',
                        'Escenas': 'S14',
                        'Papel editorial': 'Continuidad histórica',
                        'scene_ids': ['S14'],
                        'source_prompt_anchor': 'word/document.xml table2 row32',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S14'],
                        'role_kind': 'contexto de continuidad',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M033',
                        'Mecanismo o contrato del catálogo': 'Extinción inversión y readquisición CORE06',
                        'Escenas': 'S03, S04',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S03', 'S04'],
                        'source_prompt_anchor': 'word/document.xml table2 row33',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S03', 'scenes/S04'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M034',
                        'Mecanismo o contrato del catálogo': 'Reprogramación funcional CORE07',
                        'Escenas': 'S04',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S04'],
                        'source_prompt_anchor': 'word/document.xml table2 row34',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S04'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M035',
                        'Mecanismo o contrato del catálogo': 'Integración física CPC9 desdeT0',
                        'Escenas': 'S14',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S14'],
                        'source_prompt_anchor': 'word/document.xml table2 row35',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S14'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M036',
                        'Mecanismo o contrato del catálogo': 'Revisión cuantitativa54 a67',
                        'Escenas': 'S11',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S11'],
                        'source_prompt_anchor': 'word/document.xml table2 row36',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S11'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M037',
                        'Mecanismo o contrato del catálogo': 'Comunicación bidireccional y uso CPC9',
                        'Escenas': 'S07',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S07'],
                        'source_prompt_anchor': 'word/document.xml table2 row37',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S07'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M038',
                        'Mecanismo o contrato del catálogo': 'Adquisición opaca65 N67 auxiliar',
                        'Escenas': 'S13',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S13'],
                        'source_prompt_anchor': 'word/document.xml table2 row38',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S13'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M039',
                        'Mecanismo o contrato del catálogo': 'Propagación y contrastes de observador CORE15',
                        'Escenas': 'S09',
                        'Papel editorial': 'Observación',
                        'scene_ids': ['S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row39',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S09'],
                        'role_kind': 'observación o instrumento',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M040',
                        'Mecanismo o contrato del catálogo': 'Operador, accesibilidad y capacidades nativas '
                                                             'CORE16',
                        'Escenas': 'S09',
                        'Papel editorial': 'Accesibilidad',
                        'scene_ids': ['S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row40',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S09'],
                        'role_kind': 'instrumento de accesibilidad',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M041',
                        'Mecanismo o contrato del catálogo': 'Reconstrucción mediante respaldo y cociente '
                                                             'causal CORE17',
                        'Escenas': 'S08, S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S08', 'S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row41',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S08', 'scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M042',
                        'Mecanismo o contrato del catálogo': 'Transformación específica de historia ING05',
                        'Escenas': 'S03',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S03'],
                        'source_prompt_anchor': 'word/document.xml table2 row42',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S03'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M043',
                        'Mecanismo o contrato del catálogo': 'Reutilización causal posterior al anfitrión '
                                                             'ING06',
                        'Escenas': 'S05, S08',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S05', 'S08'],
                        'source_prompt_anchor': 'word/document.xml table2 row43',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S05', 'scenes/S08'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M044',
                        'Mecanismo o contrato del catálogo': 'Memoria relativa y lector renovado ING02',
                        'Escenas': 'S05, S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S05', 'S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row44',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S05', 'scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M045',
                        'Mecanismo o contrato del catálogo': 'Interfaz preexistente transformada PROC02',
                        'Escenas': 'S09, S12',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S09', 'S12'],
                        'source_prompt_anchor': 'word/document.xml table2 row45',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S09', 'scenes/S12'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M046',
                        'Mecanismo o contrato del catálogo': 'Calibración de fluctuación y respuesta PROC03',
                        'Escenas': 'S09',
                        'Papel editorial': 'Calibración instrumental',
                        'scene_ids': ['S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row46',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S09'],
                        'role_kind': 'instrumento y calibración',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M047',
                        'Mecanismo o contrato del catálogo': 'Recurrencia con fuentes persistentes ING01',
                        'Escenas': 'S10',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S10'],
                        'source_prompt_anchor': 'word/document.xml table2 row47',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S10'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M101',
                        'Mecanismo o contrato del catálogo': 'Asociación léxica arbitraria y acceso por fase',
                        'Escenas': 'S13',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S13'],
                        'source_prompt_anchor': 'word/document.xml table2 row101',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S13'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M102',
                        'Mecanismo o contrato del catálogo': 'Puente léxico y uso contextual de varios accesos',
                        'Escenas': 'S09, S13',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S09', 'S13'],
                        'source_prompt_anchor': 'word/document.xml table2 row102',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S09', 'scenes/S13'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M103',
                        'Mecanismo o contrato del catálogo': 'Comunicación de una asociación y uso por el '
                                                             'receptor',
                        'Escenas': 'S07',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S07'],
                        'source_prompt_anchor': 'word/document.xml table2 row103',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S07'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M104',
                        'Mecanismo o contrato del catálogo': 'Readquisición cuantitativa protegida',
                        'Escenas': 'S04, S05',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S04', 'S05'],
                        'source_prompt_anchor': 'word/document.xml table2 row104',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S04', 'scenes/S05'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M105',
                        'Mecanismo o contrato del catálogo': 'Composición de orden y contacto con consecuencia',
                        'Escenas': 'S06',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S06'],
                        'source_prompt_anchor': 'word/document.xml table2 row105',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S06'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M110',
                        'Mecanismo o contrato del catálogo': 'Historia y retorno útil con composición y '
                                                             'receptor',
                        'Escenas': 'S06, S07',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S06', 'S07'],
                        'source_prompt_anchor': 'word/document.xml table2 row110',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S06', 'scenes/S07'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M111',
                        'Mecanismo o contrato del catálogo': 'Protección bidireccional bajo uso multifuncional',
                        'Escenas': 'S08, S12',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S08', 'S12'],
                        'source_prompt_anchor': 'word/document.xml table2 row111',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S08', 'scenes/S12'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M112',
                        'Mecanismo o contrato del catálogo': 'Acceso preparado a información transformada y '
                                                             'contexto mixto',
                        'Escenas': 'S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row112',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M120',
                        'Mecanismo o contrato del catálogo': 'Protocolo común de recuperación y uso sin '
                                                             'reenseñar',
                        'Escenas': 'S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row120',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M121',
                        'Mecanismo o contrato del catálogo': 'Selección local revisada por consecuencias y '
                                                             'nuevo contenido',
                        'Escenas': 'S11',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S11'],
                        'source_prompt_anchor': 'word/document.xml table2 row121',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S11'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M122',
                        'Mecanismo o contrato del catálogo': 'Pérdida causal contrastada y readquisición '
                                                             'explícita',
                        'Escenas': 'S04, S09',
                        'Papel editorial': 'Control y readquisición',
                        'scene_ids': ['S04', 'S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row122',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S04', 'scenes/S09'],
                        'role_kind': 'control y readquisición',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M123',
                        'Mecanismo o contrato del catálogo': 'Acceso aprendido a soporte redundante y uso '
                                                             'inmediato sin reenseñar contenido',
                        'Escenas': 'S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row123',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M130',
                        'Mecanismo o contrato del catálogo': 'Experiencias ambientales y privadas con '
                                                             'referencia adquirida y actuación posterior',
                        'Escenas': 'S11',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S11'],
                        'source_prompt_anchor': 'word/document.xml table2 row130',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S11'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M131',
                        'Mecanismo o contrato del catálogo': 'Recuperación social de ambos signos por recurso '
                                                             'genérico y acceso preparado',
                        'Escenas': 'S07',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S07'],
                        'source_prompt_anchor': 'word/document.xml table2 row131',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S07'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M132',
                        'Mecanismo o contrato del catálogo': 'Puente E1 Pendulum con acción anulada retardo y '
                                                             'continuidad',
                        'Escenas': 'S11',
                        'Papel editorial': 'Puente externo',
                        'scene_ids': ['S11'],
                        'source_prompt_anchor': 'word/document.xml table2 row132',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S11'],
                        'role_kind': 'puente externo preparado',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M140',
                        'Mecanismo o contrato del catálogo': 'Acciones útiles mediante referencia adquirida '
                                                             'por desgaste',
                        'Escenas': 'S11',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S11'],
                        'source_prompt_anchor': 'word/document.xml table2 row140',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S11'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M141',
                        'Mecanismo o contrato del catálogo': 'Protección social conservando agenda '
                                                             'comprometida y comunicación',
                        'Escenas': 'S08',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S08'],
                        'source_prompt_anchor': 'word/document.xml table2 row141',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S08'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M142',
                        'Mecanismo o contrato del catálogo': 'Separación física de soportes previos y nueva '
                                                             'contribución',
                        'Escenas': 'S08, S12',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S08', 'S12'],
                        'source_prompt_anchor': 'word/document.xml table2 row142',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S08', 'scenes/S12'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M201',
                        'Mecanismo o contrato del catálogo': 'Composición de ruta y contenido adquirido en E1 '
                                                             'tardío',
                        'Escenas': 'S06, S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S06', 'S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row201',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S06', 'scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M202',
                        'Mecanismo o contrato del catálogo': 'Solicitud material y respuesta privada MI01',
                        'Escenas': 'S07',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S07'],
                        'source_prompt_anchor': 'word/document.xml table2 row202',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S07'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M203',
                        'Mecanismo o contrato del catálogo': 'La respuesta social modifica una decisión '
                                                             'posterior',
                        'Escenas': 'S07, S11',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S07', 'S11'],
                        'source_prompt_anchor': 'word/document.xml table2 row203',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S07', 'scenes/S11'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M204',
                        'Mecanismo o contrato del catálogo': 'Un producto de fallo inicia una consulta',
                        'Escenas': 'S10, S11',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S10', 'S11'],
                        'source_prompt_anchor': 'word/document.xml table2 row204',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S10', 'scenes/S11'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M205',
                        'Mecanismo o contrato del catálogo': 'Reutilización de contenido propio sin '
                                                             'reenseñanza',
                        'Escenas': 'S05',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S05'],
                        'source_prompt_anchor': 'word/document.xml table2 row205',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S05'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M206',
                        'Mecanismo o contrato del catálogo': 'Composición adquirida de contacto y orden',
                        'Escenas': 'S06',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S06'],
                        'source_prompt_anchor': 'word/document.xml table2 row206',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S06'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M207',
                        'Mecanismo o contrato del catálogo': 'Selección local revisada por consecuencias R8',
                        'Escenas': 'S11',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S11'],
                        'source_prompt_anchor': 'word/document.xml table2 row207',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S11'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M208',
                        'Mecanismo o contrato del catálogo': 'Consulta social con lector reutilizable R9',
                        'Escenas': 'S07, S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S07', 'S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row208',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S07', 'scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M209',
                        'Mecanismo o contrato del catálogo': 'Referencia conservada con lector efímero',
                        'Escenas': 'S05, S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S05', 'S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row209',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S05', 'scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M210',
                        'Mecanismo o contrato del catálogo': 'Recuperación de acceso mediante recurso genérico '
                                                             'de fase',
                        'Escenas': 'S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row210',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M211',
                        'Mecanismo o contrato del catálogo': 'Trabajo contextual continuado CF01',
                        'Escenas': 'S14',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S14'],
                        'source_prompt_anchor': 'word/document.xml table2 row211',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S14'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M212',
                        'Mecanismo o contrato del catálogo': 'Consecuencia real posterior y uso de la '
                                                             'referencia modificada',
                        'Escenas': 'S11',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S11'],
                        'source_prompt_anchor': 'word/document.xml table2 row212',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S11'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M213',
                        'Mecanismo o contrato del catálogo': 'Transferencia de referencia entre tareas y leyes',
                        'Escenas': 'S08',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S08'],
                        'source_prompt_anchor': 'word/document.xml table2 row213',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S08'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M214',
                        'Mecanismo o contrato del catálogo': 'Sensores R10: componentes crudos y '
                                                             'transferencia2→8',
                        'Escenas': 'S08, S12',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S08', 'S12'],
                        'source_prompt_anchor': 'word/document.xml table2 row214',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S08', 'scenes/S12'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M215',
                        'Mecanismo o contrato del catálogo': 'Tres contextos acumulados y revisión con límites '
                                                             'explícitos',
                        'Escenas': 'S04, S05',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S04', 'S05'],
                        'source_prompt_anchor': 'word/document.xml table2 row215',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S04', 'scenes/S05'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M216',
                        'Mecanismo o contrato del catálogo': 'Memoria contextual restaurativa y revisión '
                                                             'selectiva',
                        'Escenas': 'S04, S05',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S04', 'S05'],
                        'source_prompt_anchor': 'word/document.xml table2 row216',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S04', 'scenes/S05'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M217',
                        'Mecanismo o contrato del catálogo': 'Composición de recorridos aprendidos y coste de '
                                                             'acceso',
                        'Escenas': 'S06, S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S06', 'S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row217',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S06', 'scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M218',
                        'Mecanismo o contrato del catálogo': 'Selección nativa de acceso condicionada por una '
                                                             'experiencia previa',
                        'Escenas': 'S09, S13',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S09', 'S13'],
                        'source_prompt_anchor': 'word/document.xml table2 row218',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S09', 'scenes/S13'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M219',
                        'Mecanismo o contrato del catálogo': 'Sexta asociación, revisión selectiva y retención '
                                                             'MU',
                        'Escenas': 'S03, S05, S13',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S03', 'S05', 'S13'],
                        'source_prompt_anchor': 'word/document.xml table2 row219',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S03', 'scenes/S05', 'scenes/S13'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M220',
                        'Mecanismo o contrato del catálogo': 'Percepción cruda de128 componentes con memoria '
                                                             'previa',
                        'Escenas': 'S12',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S12'],
                        'source_prompt_anchor': 'word/document.xml table2 row220',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S12'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M221',
                        'Mecanismo o contrato del catálogo': 'Cadena material: memoria, archivo real y nueva '
                                                             'decisión',
                        'Escenas': 'S11, S14',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S11', 'S14'],
                        'source_prompt_anchor': 'word/document.xml table2 row221',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S11', 'scenes/S14'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M222',
                        'Mecanismo o contrato del catálogo': 'Servicio persistente emparejado MU01 y '
                                                             'protección preparada de fase',
                        'Escenas': 'S14',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S14'],
                        'source_prompt_anchor': 'word/document.xml table2 row222',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S14'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M223',
                        'Mecanismo o contrato del catálogo': 'Detección material sin consumir el portador '
                                                             'original',
                        'Escenas': 'S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row223',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M224',
                        'Mecanismo o contrato del catálogo': 'Restauración genérica de soportes en U0',
                        'Escenas': 'S05, S09',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S05', 'S09'],
                        'source_prompt_anchor': 'word/document.xml table2 row224',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S05', 'scenes/S09'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M225',
                        'Mecanismo o contrato del catálogo': 'Quinta asociación y uso material repetido MA02',
                        'Escenas': 'S05',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S05'],
                        'source_prompt_anchor': 'word/document.xml table2 row225',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S05'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M226',
                        'Mecanismo o contrato del catálogo': 'Relevancia causal individual de128 componentes',
                        'Escenas': 'S12',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S12'],
                        'source_prompt_anchor': 'word/document.xml table2 row226',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S12'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M227',
                        'Mecanismo o contrato del catálogo': 'Una señal residual participa en una '
                                                             'readquisición posterior',
                        'Escenas': 'S03, S05',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S03', 'S05'],
                        'source_prompt_anchor': 'word/document.xml table2 row227',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S03', 'scenes/S05'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M301',
                        'Mecanismo o contrato del catálogo': 'Asociaciones léxicas ampliadas con contraste de '
                                                             'enseñanza',
                        'Escenas': 'S03, S13',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S03', 'S13'],
                        'source_prompt_anchor': 'word/document.xml table2 row301',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S03', 'scenes/S13'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M302',
                        'Mecanismo o contrato del catálogo': 'Traslación escalar aprendida y reutilización '
                                                             'acumulada',
                        'Escenas': 'S03, S06',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S03', 'S06'],
                        'source_prompt_anchor': 'word/document.xml table2 row302',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S03', 'scenes/S06'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M303',
                        'Mecanismo o contrato del catálogo': 'Lector recirculante y mantenimiento explícito',
                        'Escenas': 'S05, S10',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S05', 'S10'],
                        'source_prompt_anchor': 'word/document.xml table2 row303',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S05', 'scenes/S10'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M304',
                        'Mecanismo o contrato del catálogo': 'Selección bajo retorno demorado y cambios de '
                                                             'utilidad',
                        'Escenas': 'S11',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S11'],
                        'source_prompt_anchor': 'word/document.xml table2 row304',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S11'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M305',
                        'Mecanismo o contrato del catálogo': 'Sensor balanceado causal y oportunidades '
                                                             'preparadas',
                        'Escenas': 'S12',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S12'],
                        'source_prompt_anchor': 'word/document.xml table2 row305',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S12'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M306',
                        'Mecanismo o contrato del catálogo': 'Integración y continuación de un objetivo APD03',
                        'Escenas': 'S14',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S14'],
                        'source_prompt_anchor': 'word/document.xml table2 row306',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S14'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M307',
                        'Mecanismo o contrato del catálogo': 'Sensor, léxico y consecuencias compartidas APD04',
                        'Escenas': 'S07, S12',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S07', 'S12'],
                        'source_prompt_anchor': 'word/document.xml table2 row307',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S07', 'scenes/S12'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M308',
                        'Mecanismo o contrato del catálogo': 'Retención sin tareas y transducción de versiones '
                                                             'APD05',
                        'Escenas': 'S05, S14',
                        'Papel editorial': 'Familia funcional',
                        'scene_ids': ['S05', 'S14'],
                        'source_prompt_anchor': 'word/document.xml table2 row308',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S05', 'scenes/S14'],
                        'role_kind': 'familia documental con ejemplo de escena',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'},
                       {'ID': 'M309',
                        'Mecanismo o contrato del catálogo': 'Evaluación poscompromiso de artefactos y '
                                                             'consecuencias',
                        'Escenas': 'S11, S14',
                        'Papel editorial': 'Verificación de efecto',
                        'scene_ids': ['S11', 'S14'],
                        'source_prompt_anchor': 'word/document.xml table2 row309',
                        'coverage_role': 'catalogue, control or documentary context according to literal Papel '
                                         'editorial',
                        'claim_101_independent_faculties': False,
                        'claim_individual_visual_reenactment': False,
                        'scene_coverage_refs': ['scenes/S11', 'scenes/S14'],
                        'role_kind': 'verificación de efecto',
                        'evidence_link_scope': 'Editorial catalogue-to-scene mapping. The scene records name '
                                               'the actual demonstrated cases; this row is not a separate '
                                               'replay or an independently established faculty.'}],
 'critical_scope_notes': ['The same current or historical example can represent several documentary families; '
                          'neither101 catalogue rows nor12 families count independent faculties.',
                          'G07 derived middle23 and retained final30 are distinguished; compact G07 has no '
                          'matched omission control.',
                          'M014 AB/BA use different prepared routes and do not isolate abstract order.',
                          'NRD05 differing sites are historical state differences, not individually '
                          'established memory locations.',
                          'Rejected CPC9 reader requests213/280 are not successful updates.',
                          'CP02 none=[False,True] is unresolved; a missing observation is not an observed '
                          'zero.',
                          'N0 save/open proves exact continuity without advancing the native clock, not new '
                          'material use.',
                          'S14 last6s explicitly switch from Direct T725840 to another MINUS trajectory: '
                          'reopen720458, observed MA−720589.',
                          'Historical physical frames are not silently attributed to the later operational '
                          'MAIN727225.',
                          'No full visual-QA pass is claimed here.'],
 'validation': {'scene_count': 15,
                'family_count': 12,
                'catalogue_count': 101,
                'catalogue_ids_unique': True,
                'literal_catalogue_matches_prompt_and_registry': True,
                'role_counts': {'Contrato y control': 1,
                                'Familia funcional': 90,
                                'Plataforma': 1,
                                'Alcance y control': 1,
                                'Diagnóstico': 1,
                                'Continuidad histórica': 1,
                                'Observación': 1,
                                'Accesibilidad': 1,
                                'Calibración instrumental': 1,
                                'Control y readquisición': 1,
                                'Puente externo': 1,
                                'Verificación de efecto': 1},
                'source_JSON_pointers_resolved': 63,
                'byte_exact_archival_copies_SHA_checked': 18,
                'local_scene_windows_cover_all_360_seconds': True,
                'A_B_C_labels_are_per_segment': True,
                'final_visual_QA': 'pending; tracked by root in the unique production registry'}}
