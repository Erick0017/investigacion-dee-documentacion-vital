"""MA02 launcher transport tests: standard library, no motor and no ticks."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
SPEC=importlib.util.spec_from_file_location('ma2_launch',Path(__file__).with_name('delta_colaborador')/'arrancar.py')
L=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(L)

class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='ma02-launch-');L.ROOT=Path(self.tmp.name);self.calls=[]
        L.call=lambda argv:self.calls.append(('call',argv))or 0
        L.open_copy=lambda alias,life:self.calls.append(('import',alias,life))
        L.catalog=lambda:[{'alias':'MENTE_ACUMULATIVA_R02','source_life':'MA02_MAIN_5','profile':'fisica_directa','snapshot_sha256':'source5'},
                          {'alias':'MEMORIA_SEPARADA_MA02','source_life':'MA02_MEMORIA_SEPARADA','profile':'fisica_directa','snapshot_sha256':'source4'}]
    def tearDown(self):self.tmp.cleanup()
    def existing(self,source='MA02_MAIN_5',digest='source5'):
        folder=L.ROOT/'trabajo_personal/estado/vidas/MI_VIDA';folder.mkdir(parents=True)
        record=folder/'VIDA.json';record.write_text(json.dumps({'life_id':'MI_VIDA','profile':'fisica_directa','parent':{'encoded_sha256':digest,'source_name':source+'.T123.deetsnap.gz'}}),encoding='utf8')
        return record
    def test_literal_json_no_external_choice(self):
        raw='[{"contexto":"epsilon","modo":"usar"},{"modo":"componer","aceptar_consumo":true}]'
        L.service_mente2(['NUEVA','--situaciones',raw,'--detalle'])
        self.assertEqual(self.calls,[('import','MENTE_ACUMULATIVA_R02','NUEVA'),('call',['mente2-sesion','--vida','NUEVA','--situaciones',raw,'--detalle'])])
    def test_continue_no_import_or_record_edit(self):
        record=self.existing();before=record.read_bytes()
        L.service_mente2(['MI_VIDA','--continuar'])
        self.assertEqual(self.calls,[('call',['mente2-estado','--vida','MI_VIDA'])]);self.assertEqual(record.read_bytes(),before)
    def test_preserved_specialization_uses_its_own_state(self):
        self.existing('MA02_MEMORIA_SEPARADA','source4')
        L.service_mente2(['MI_VIDA','--continuar','--situaciones','[{"contexto":"beta"}]'])
        self.assertEqual(self.calls[0][0],'call');self.assertEqual(self.calls[0][1][0],'mente2-sesion')
    def test_controls_literal_not_inferred(self):
        self.existing();raw='[{"contexto":"gamma","modo":"trabajo"}]'
        L.service_mente2(['MI_VIDA','--continuar','--situaciones',raw,'--retorno','omit','--actuador','nulled'])
        self.assertEqual(self.calls,[('call',['mente2-sesion','--vida','MI_VIDA','--situaciones',raw,'--retorno','omit','--actuador','nulled'])])
    def test_existing_personal_state_not_silently_reimported(self):
        record=self.existing();before=record.read_bytes()
        with self.assertRaises(ValueError):L.service_mente2(['MI_VIDA'])
        self.assertEqual(record.read_bytes(),before);self.assertEqual(self.calls,[])
    def test_missing_continuation_not_recreated(self):
        with self.assertRaises(ValueError):L.service_mente2(['MISSING','--continuar'])
        self.assertEqual(self.calls,[])
    def test_default_keeps_old_R9_active_and_reports_domain(self):
        record=self.existing('MA_MAIN_R9','oldR9');before=record.read_bytes()
        active=L.ROOT/'trabajo_personal/estado/ACTIVO.json';active.write_text('{"life_id":"MI_VIDA"}',encoding='utf8');active_before=active.read_bytes()
        with self.assertRaises(ValueError):L.service_mente2([])
        self.assertEqual(self.calls,[]);self.assertEqual(record.read_bytes(),before);self.assertEqual(active.read_bytes(),active_before)
    def test_P1_is_not_admitted_to_different_mente2_contract(self):
        record=self.existing('MA02_SELECTOR_P1_H1','p1ready');before=record.read_bytes()
        existing_catalog=L.catalog
        L.catalog=lambda:[*existing_catalog(),{'alias':'SELECTOR_P1_H1_MA02','source_life':'MA02_SELECTOR_P1_H1','profile':'fisica_directa','snapshot_sha256':'p1ready'}]
        with self.assertRaises(ValueError):L.service_mente2(['MI_VIDA','--continuar'])
        self.assertEqual(self.calls,[]);self.assertEqual(record.read_bytes(),before)
    def test_default_admitted_active_is_passive(self):
        self.existing();(L.ROOT/'trabajo_personal/estado/ACTIVO.json').write_text('{"life_id":"MI_VIDA"}',encoding='utf8')
        L.service_mente2([]);self.assertEqual(self.calls,[('call',['mente2-estado','--vida','MI_VIDA'])])
    def test_empty_personal_default_explicit_complete_import(self):
        def imported(alias,life):
            self.calls.append(('import',alias,life));folder=L.ROOT/'trabajo_personal/estado/vidas'/life;folder.mkdir(parents=True)
            (folder/'VIDA.json').write_text(json.dumps({'life_id':life,'profile':'fisica_directa','parent':{'encoded_sha256':'source5'}}),encoding='utf8')
            (L.ROOT/'trabajo_personal/estado/ACTIVO.json').write_text(json.dumps({'life_id':life}),encoding='utf8')
        L.open_copy=imported;L.service_mente2([])
        self.assertEqual(self.calls[0][:2],('import','MENTE_ACUMULATIVA_R02'));self.assertTrue(self.calls[0][2].startswith('COLAB_MENTE2_'))
        self.assertEqual(self.calls[1],('call',['mente2-estado','--vida',self.calls[0][2]]))

if __name__=='__main__':unittest.main(verbosity=2)
