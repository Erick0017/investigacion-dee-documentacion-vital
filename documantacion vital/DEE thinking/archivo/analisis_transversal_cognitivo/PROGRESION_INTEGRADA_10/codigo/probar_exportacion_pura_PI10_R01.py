"""Synthetic compact-export/readback test, not a Native replay."""
from pathlib import Path
import argparse,importlib.util,json,hashlib
H=Path(__file__).resolve().parent
def load(name,file):
    s=importlib.util.spec_from_file_location(name,H/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def dump(path,v):path.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--directorio',type=Path,required=True);args=parser.parse_args()
    root=args.directorio.absolute();assert not root.exists();root.mkdir()
    fx=load('fixture','probar_lector_primario_puro_PI10_R02.py');env=load('env','pi10_entorno_dos_puertas_R01.py');ex=load('export','exportar_primarios_cerrados_PI10_R01.py');audit=load('audit','recalcular_primarios_PI10_R02.py')
    source=root/'SINTETICO'/ex.FOLDER;source.mkdir(parents=True);v,p=fx.fixture();p['schema']='DEE.PI10.adaptive_query.protocol.R01'
    sample=v['first_stage']['sample_register']['actual_preview_observation'];q=v['first_stage']['query_tick'];motor=v['second_stage']
    offer=env.prepare_offer(source,0,sample,'need',actual_tick=q-1,query_tick=q)
    consequence=env.act_on_observed_motor(source,0,1,native_choice=1,reader_observation=motor['reader']['observation'],command_valid=True,q1_valid=True,fi_choice=1,fi_required=True,actual_tick=q+220,command_receipt=motor['copy_receipt'])
    v.update(offer=offer,resource=consequence);dump(source/'episodio_0000.json',v)
    protocol=root/'PROTOCOLO_SINTETICO.json';dump(protocol,p);closure=root/'CIERRE_SINTETICO.json';dump(closure,{'synthetic':True,'Native_executed':False,'closed':True})
    config={'schema':'DEE.PI10.closed_export_configuration.R01','closed_confirmed_by_root':True,'protocol':{'file':str(protocol),'sha256':hashlib.sha256(protocol.read_bytes()).hexdigest()},
      'sources':[{'tag':'fixture','source_actor_home':str(source),'closed_proof_file':str(closure)}]}
    result=ex.export(config,root/'EXPORTACION_SINTETICA');check=audit.bundle(root/'EXPORTACION_SINTETICA'/'INDEX.json')
    assert len(check['rows'])==1 and check['rows'][0]['physical_delivered']and check['rows'][0]['attributed_useful']
    assert not check['complete_three_paired_arms']and check['reserved_gain_vs_nonfailure']is None
    try:ex.export(config,root/'EXPORTACION_SINTETICA')
    except ValueError:overwrite_rejected=True
    else:raise AssertionError('Existing destination was overwritten')
    proof={'schema':'DEE.PI10.synthetic_export_contract_test.R01','synthetic':True,'Native_executed':False,'DEE_imported':False,
      'export':result,'recalculation':{'rows':len(check['rows']),'physical_resource_actual64B':True,'partial_record_not_claimed_full_reserve':True},
      'existing_destination_rejected':overwrite_rejected,'scope':'One artificial integer record and real synthetic64B file movement; not Native calibration or learning.'}
    dump(root/'PRUEBA_EXPORTADOR_PURO.json',proof);print(json.dumps(proof,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
