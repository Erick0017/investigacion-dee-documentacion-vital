"""Artificial prefix-identity/file export tests; no Native trajectory is simulated."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
H=Path(__file__).resolve().parent
def load(name,file):
    s=importlib.util.spec_from_file_location(name,H/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def dump(path,v):path.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--directorio',type=Path,required=True);args=parser.parse_args()
    root=args.directorio.absolute();assert not root.exists();root.mkdir()
    old=H.parent/'fuentes/PRUEBA_EXPORTADOR_PURO_R01/EXPORTACION_SINTETICA';parent_index=old/'INDEX.json';parent=json.loads(parent_index.read_text('utf8'))
    prefix=(old/parent['episodes'][0]['witness']['file']).read_bytes()
    ex=load('export','exportar_primarios_cerrados_PI10_R02.py');fx=load('fixture','probar_lector_primario_puro_PI10_R02.py');env=load('env','pi10_entorno_dos_puertas_R01.py');audit=load('audit','recalcular_primarios_PI10_R02.py')
    source=root/'RAMA_SINTETICA'/ex.FOLDER;source.mkdir(parents=True);(source/'episodio_0000.json').write_bytes(prefix)
    v,p=fx.fixture();v.update(ordinal=1,life_id='SYNTHETIC_BRANCH_NO_NATIVE');p['schema']='DEE.PI10.adaptive_query.protocol.R01';p['schedule'].append(dict(p['schedule'][0]))
    sample=v['first_stage']['sample_register']['actual_preview_observation'];q=v['first_stage']['query_tick'];motor=v['second_stage']
    offer=env.prepare_offer(source,1,sample,'need',actual_tick=q-1,query_tick=q)
    consequence=env.act_on_observed_motor(source,1,1,native_choice=1,reader_observation=motor['reader']['observation'],command_valid=True,q1_valid=True,fi_choice=1,fi_required=True,actual_tick=q+220,command_receipt=motor['copy_receipt'])
    v.update(offer=offer,resource=consequence);dump(source/'episodio_0001.json',v)
    protocol=root/'PROTOCOLO_SINTETICO.json';dump(protocol,p);closure=root/'CIERRE_SINTETICO.json';dump(closure,{'synthetic':True,'Native_executed':False,'closed':True})
    conf={'schema':'DEE.PI10.closed_export_configuration.R01','closed_confirmed_by_root':True,'protocol':{'file':str(protocol),'sha256':hashlib.sha256(protocol.read_bytes()).hexdigest()},
      'sources':[{'tag':'branch','source_actor_home':str(source),'closed_proof_file':str(closure),'first_exported_ordinal':1,
        'shared_prefix_bundle':{'index':str(parent_index),'sha256':hashlib.sha256(parent_index.read_bytes()).hexdigest(),'parent_life_id':'SYNTHETIC_NO_NATIVE'}}]}
    exported=ex.export(conf,root/'EXPORTACION_RAMA');recalc=audit.bundle(root/'EXPORTACION_RAMA/INDEX.json')
    assert len(recalc['rows'])==1 and recalc['rows'][0]['ordinal']==1 and recalc['rows'][0]['life_id']=='SYNTHETIC_BRANCH_NO_NATIVE'
    index=json.loads((root/'EXPORTACION_RAMA/INDEX.json').read_text('utf8'));binding=index['sources'][0]['shared_prefix_omitted_from_duplicate_copy']
    assert len(binding)==1 and binding[0]['historical_life_id']=='SYNTHETIC_NO_NATIVE'and binding[0]['sha256']==hashlib.sha256(prefix).hexdigest()
    # Only synthetic test fixture bytes are deliberately changed for rejection.
    wrong=json.loads(prefix);wrong['life_id']='FALSIFIED_PARENT';dump(source/'episodio_0000.json',wrong)
    try:ex.export(conf,root/'EXPORTACION_DEBE_RECHAZARSE')
    except ValueError:wrong_prefix_rejected=True
    else:raise AssertionError('A rewritten copied history was accepted')
    proof={'schema':'DEE.PI10.synthetic_shared_prefix_export_contract.R02','synthetic':True,'Native_executed':False,'DEE_imported':False,
      'export':exported,'new_rows_only':True,'historical_life_identity_and_bytes_not_rewritten':True,'falsified_prefix_rejected':wrong_prefix_rejected,
      'scope':'Artificial integer/file records only. This checks transport genealogy accounting, not acquisition, physical continuity or an actual Native branch.'}
    dump(root/'PRUEBA_EXPORTADOR_PREFIJO_PURO.json',proof);print(json.dumps(proof,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
