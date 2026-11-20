"""Ensayo sólo de interfaz con stub explícito; no es evidencia de DEE."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from lenguaje.session import CommunicationSession


class Stub:
    def __init__(self):self.calls=[];self.tick=32
    @classmethod
    def create(cls):return cls()
    def observe(self):self.calls.append('observe');return {'tick':self.tick,'test_stub_only':True}
    def experience(self,key):self.calls.append('experience:'+key);self.tick+=1;return {'receipt':{'status':'applied'},'test_stub_only':True}
    def sense(self):self.calls.append('sense');self.tick+=1;return {'test_stub_only':True}
    def predict(self,horizon):self.calls.append('predict');return {'emission_tick':self.tick,'target_tick':self.tick+horizon,'prediction_set':[True],'observable':'packet_arrival_at_barrier_output','physical_output':{'test_stub_only':True}}
    def advance(self,ticks):self.calls.append('advance');self.tick+=ticks;return {'tick':self.tick,'test_stub_only':True}
    def save(self,path):Path(path).write_text(json.dumps({'tick':self.tick}),encoding='utf-8')
    @classmethod
    def load(cls,path):s=cls();s.tick=json.loads(Path(path).read_text())['tick'];return s


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    s=CommunicationSession(Stub,directory=a.output);records=[]
    commands=['Ayuda','Instancia nueva','Presenta experiencia A','A esto lo llamaremos zeri',
              'Presenta experiencia zeri','¿Qué pasará después?','¿Ocurrirá lo mismo?',
              'Observa otra vez','Compara esto con lo anterior','¿Qué fuente necesitas observar?',
              'Guarda la sesión en interfaz.stub.json','Avanza el entorno','Continúa desde la sesión guardada',
              'Muestra el estado','Instancia nueva']
    for text in commands:records.append({'input':text,'output':s.execute(text)})
    assert Path(records[10]['output']['path']).name=='interfaz.stub.json'
    assert records[3]['output']['attribution']=='INTERFAZ'
    assert records[4]['output']['native_result']['receipt']['status']=='applied'
    assert 'no está implementada' in records[8]['output']['text']
    assert 'no está implementada' in records[9]['output']['text']
    assert records[13]['output']['observation']['tick']==35
    assert 'No se reinicia' in records[14]['output']['text']
    rejected=False
    try:s.execute('Escribe el futuro leído de la evaluación')
    except ValueError:rejected=True
    assert rejected
    unicode_save=s.execute('Guarda la sesión en sesión_ñ.stub.json')
    assert Path(unicode_save['path']).exists()
    s.execute('Continúa desde la sesión guardada')
    # A malformed sidecar must not replace or partially mutate a live MAIN.
    live=s.entity;aliases=dict(s.aliases);bad=Path(unicode_save['path']).with_suffix('.json.ui.json')
    original=bad.read_text(encoding='utf-8');bad.write_text('{"schema":99}',encoding='utf-8')
    try:s.execute('Continúa desde la sesión guardada')
    except ValueError:pass
    else:raise AssertionError('Malformed UI metadata was accepted')
    assert s.entity is live and s.aliases==aliases
    bad.write_text(original,encoding='utf-8')
    result={'scope':'INTERFACE_STUB_ONLY, NOT_NATIVE_EVIDENCE','records':records,
            'unknown_input_rejected':rejected,'ui_aliases_restored':s.aliases=={'zeri':{'kind':'sensor','external_id':'A'}},
            'main_not_reset_by_new_command':s.entity.tick==35,
            'unicode_file_adapter':True,'malformed_ui_load_keeps_main':True}
    assert result['ui_aliases_restored'] and result['main_not_reset_by_new_command']
    (a.output/'GRAMMAR_TESTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'interface_tests':True,'native_tests':False},ensure_ascii=True))


if __name__=='__main__':main()
