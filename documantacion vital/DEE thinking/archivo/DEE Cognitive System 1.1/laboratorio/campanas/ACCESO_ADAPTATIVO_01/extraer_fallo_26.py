"""Read existing interrupted evidence; no evolution, new inputs or simulations.

Exact complete JSONL records retain uncompressed byte offsets and line hashes.
A missing gzip trailer/partial tail is recorded, not silently repaired.
"""
from pathlib import Path
import argparse,sys,json,gzip,lzma,re,hashlib,time
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01')]
from app.process_control import protect_current
from app.lives import load_adapter
from app.native_tools import physical
from instrumentos_pc01 import sha,receipts,native_digest
from agenda_binaria_pc01 import queue_state
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);original=a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01/ACCESO_CONECTADO_CONTROLES_11/initialup_feedback_sham_c11';source=original/'CAMPOS_ACCESO_CONECTADO.jsonl.gz';data={'case':a.case,'life':'AA01_CONECTADO10_initialup_feedback_sham_c11','source_sha256':sha(__file__),'original':str(source),'original_sha256':sha(source),'original_bytes':source.stat().st_size,'no_new_native_evolution':True,'lines':[],'selected':[],'incomplete_tail':None,'complete_checkpoint_views':[]};offset=0;growth_selected=False;started=time.perf_counter()
with gzip.open(source,'rb')as f:
    while True:
        try:line=f.readline()
        except(EOFError,OSError)as error:data['incomplete_tail']={'type':type(error).__name__,'detail':str(error),'after_complete_uncompressed_bytes':offset};break
        if not line:break
        if not line.endswith(b'\n'):data['incomplete_tail']={'type':'PARTIAL_JSONL_LINE','bytes':len(line),'sha256':hashlib.sha256(line).hexdigest(),'offset':offset};break
        head=line[:1024];number=len(data['lines'])+1;tick=int(re.search(rb'"tick"\s*:\s*(\d+)',head).group(1));occupied=int(re.search(rb'"occupied"\s*:\s*(\d+)',head).group(1));row={'line':number,'offset_uncompressed':offset,'bytes':len(line),'sha256_exact_line':hashlib.sha256(line).hexdigest(),'tick':tick,'occupied':occupied};data['lines'].append(row)
        if tick in(39842,40076,40147)or(occupied>5000 and not growth_selected):
            value=json.loads(line);dest=a.out/('CAMPO_ORIGINAL_T'+str(tick)+'.json.xz')
            with lzma.open(dest,'xb',preset=6)as out:out.write(line)
            data['selected'].append({**row,'file':dest.name,'compressed_sha256':sha(dest),'compressed_bytes':dest.stat().st_size,'JSON_validated':True});growth_selected=growth_selected or occupied>5000
        offset+=len(line)
        if time.perf_counter()-started>150:data['incomplete_tail']={'type':'FINITE_EXTRACTION_WINDOW','remaining_original_preserved':True};break
for path in sorted(original.glob('*.deetsnap.gz')):
    x=load_adapter('cpc9_integral_n67',path);before=native_digest(x.world.runtime);row={'file':str(path),'file_sha256':sha(path),'physical':physical(x.world,occupation=True),'all_receipts':receipts(x.world.runtime),'native_queue':queue_state(x.world.runtime),'native_exact':before,'loaded_passively_without_advancing':True};row['passive_bytes_equal']=before==native_digest(x.world.runtime);data['complete_checkpoint_views'].append(row)
data['interpretation']='An invalid selectivity sham produced broad growth and exceeded the owned wall window. Last complete checkpoints and recorded prefix are not the unrecorded final state. No cognitive error/forgetting is inferred from a killed process. Normal continuation of its stale pointer is blocked.'
with gzip.open(a.out/'PRIMARIOS.json.gz','wt',encoding='utf8',compresslevel=9)as f:json.dump(data,f,ensure_ascii=False,separators=(',',':'))
print(json.dumps({'complete_lines':len(data['lines']),'last_recorded_tick':data['lines'][-1]['tick']if data['lines']else None,'selected':[(r['tick'],r['compressed_bytes'])for r in data['selected']],'tail':data['incomplete_tail'],'checkpoints':[r['physical']['tick']for r in data['complete_checkpoint_views']]}))
