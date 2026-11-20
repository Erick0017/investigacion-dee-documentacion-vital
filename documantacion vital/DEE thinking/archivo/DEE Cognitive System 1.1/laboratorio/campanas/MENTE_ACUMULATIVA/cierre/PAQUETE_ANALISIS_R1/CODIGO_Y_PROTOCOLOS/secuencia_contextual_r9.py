"""One continuous baseline, four visible contexts and no external expert routing."""
from pathlib import Path
import json,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def op(case,args):
    subprocess.run([sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',case,*args],check=True,cwd=ROOT)
def q(c,l,r,tool='puertas',regime='original'):return{'contexto':c,'valores':[l,r],'herramienta':tool,'regimen':regime}
def main():
    seal=HERE/'PROTOCOLO_CONTEXTO_R9.json'
    if seal.exists():raise FileExistsError('Frozen protocol already executed')
    blocks=[
      ('02_ADQUIRIR_C1',[q('c1',5,18)]*4+[q('c1',20,32)]),
      ('03_ADQUIRIR_C2',[q('c2',7,23)]*6+[q('c2',21,37)]),
      ('04_ADQUIRIR_C3',[q('c3',7,18)]*8+[q('c3',20,30)]),
      ('05_RETENCION_3',[q('c3',22,33),q('c1',24,37),q('c2',25,41)]),
      ('06_ADQUIRIR_C4',[q('c4',7,25)]*10+[q('c4',22,40)]),
      ('07_RETENCION_4',[q('c1',25,38),q('c2',26,43),q('c3',27,38)]),
      ('08_REVISAR_C1',[q('c1',6,15,regime='revisado')]*10+[q('c1',23,31,regime='revisado')]),
      ('09_OTRAS_TRAS_REVISION',[q('c4',25,43),q('c2',25,41),q('c3',25,35)]),
      ('10_USO_LOCAL_NUEVO',[q('c1',24,32,'trabajadores','revisado'),q('c1',26,35,'trabajadores','revisado')])]
    seal.write_text(json.dumps({'frozen_monotonic':time.monotonic(),'parent':'EO02_MAIN T169383','native_context_codec':'all contexts same input ports and motor reader, two equal raw cue values1..4; never a memory address or a target','external_law_contexts':{'c1':12,'c2':16,'c3':10,'c4':18,'c1_revised':8},'blocks':blocks,'criterion':'Four contexts count as accumulated only if first novel border/+1 responses after new acquisition and revision are all useful without reteaching before those first uses. Results of differing criteria preserved, no total score substitutes this.','control':'Same complete prefix and stimuli, tactile return omitted; branches are not independent individuals.','maximum_exposures_per_stage':[4,6,8,10,10],'no_extend_until_success':True},indent=2)+'\n',encoding='utf8')
    op('01_FORK_MAIN',['bifurcar','EO02_MAIN','MA_MAIN_R9','--modalidad','CANDIDATE'])
    op('01U_FORK_CONTROL',['bifurcar','EO02_MAIN','MA_R9_OMIT','--modalidad','DIAGNOSTIC_COPY'])
    for case,jobs in blocks:
        op(case,['mente-sesion','--vida','MA_MAIN_R9','--situaciones',json.dumps(jobs,separators=(',',':'))])
    # The omission control uses the initial acquisitions and first retention,
    # not a fabricated whole biography with later MAIN responses.
    for case,jobs in blocks[:4]:
        op(case+'_U',['mente-sesion','--vida','MA_R9_OMIT','--situaciones',json.dumps(jobs,separators=(',',':')),'--retorno','omit'])
if __name__=='__main__':main()
