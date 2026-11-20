"""Root-only C seal and isolated code/context preparation; never Native.

Default is read-only. --sellar binds one complete A/REAL-B source; --preparar
copies the already frozen B code capsule, adding C mode hooks in copies only.
The official import_pair process is a separate Root-only phase.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse, ast, hashlib, importlib.util, json, os, shutil

P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01';KEY_B='DEE.Cognitive.PI08.successive_contextual_regulation.B.R01'
STAGE=H/'FUENTES_C_PI08_R03_PREPARADAS';DEST=P/'estados/C_R03';OUT=P/'control/SISTEMA_C_PI08_R03_PREPARADO.json'
def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)
def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8')as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write('\n')
def once(text,before,after):
    require(text.count(before)==1,'Exact isolated B hook anchor changed: '+before[:90]);return text.replace(before,after)
def safe(path,roots):
    path=Path(path).resolve(strict=True);require(any(path.is_relative_to(root.resolve())for root in roots),'Outside explicit PI08/stable material roots')
    for node in(path,*path.parents):require(not node.is_symlink()and not(getattr(node.lstat(),'st_file_attributes',0)&1024),'No linked/reparse path')
    return path

def main(args):
    protocolfile=H/'PROTOCOLO_PI08_C_R02.json';sealfile=H/'SELLO_PI08_C_R03.json'
    Bproof=read(P/'control/SISTEMAS_B_PI08_R02_PREPARADOS.json');Bmanifestfile=Path(Bproof['source_manifest']);Bmanifest=read(Bmanifestfile);Bhome=Bmanifestfile.parent
    require(sha(Bmanifestfile)==Bproof['source_manifest_sha256'],'Frozen isolated B capsule changed')
    seal=read(sealfile)if sealfile.exists()else None
    if not seal:
        require(args.prefijo,'An actual complete A or REAL-B prefix is required')
        pair=safe(args.prefijo,[P,RP/'materiales']);manifestfile=pair/'EXPORTACION_SERVICIO.json';manifest=read(manifestfile)
        require(manifest['schema']=='DEE.persistent_service.paired_export.v1','Complete paired export required')
        require(sha(pair/manifest['native_snapshot'])==manifest['snapshot_sha256'],'Source snapshot hash differs')
        spec=importlib.util.spec_from_file_location('PI08_C_passive_source_only',RP/'observador_pasivo.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
        view=parser.snapshot_view(pair/manifest['native_snapshot']);require(view['physical']=={k:manifest['physical'][k]for k in view['physical']},'Source physical manifest differs')
        r3=json.loads(view['metadata']['DEE.Cognitive.PI07.regulation.environment.R03'])
        require(r3['ready']and not r3['pending']and not r3['uncertain'],'Actual closed inherited R03 required')
        inheritedB=KEY_B in view['metadata'];Bseal=read(H/'SELLO_PI08_B_R01.json')
        if inheritedB:
            bm=json.loads(view['metadata'][KEY_B]);require(bm['control']['arm']=='real'and bm['ordinal']>=30 and not bm['pending']and not bm['uncertain'],'No source from another control or incomplete B future')
            require(manifest['life_id']==Bseal['research_life_ids']['real']and Bseal['additional_readonly_life_ids']==[LIFE],'Exact real-B genealogy/readpermission required')
        else:require(manifest['life_id']=='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01','Only actual A or REAL-B source')
        p=read(protocolfile);require(p['status']=='DRAFT_PREPARED_NO_MATERIAL_AUTHORIZATION','Preserve existing C seal')
        p['status']='SEALED_BEFORE_C_NATIVE';p['actual_source_parent']={'life_id':manifest['life_id'],'N':67,'T':view['physical']['tick'],'manifest_sha256':sha(manifestfile),'snapshot_sha256':manifest['snapshot_sha256'],'inherits_B_metadata':inheritedB}
        data=(json.dumps(p,ensure_ascii=False,indent=2)+'\n').encode('utf8')
        names=['pi08_consulta_condicional_C_R03.py','pi08_consulta_condicional_C_segunda_R02.py']
        files={name:sha(H/name)for name in names}
        files['pi07_regulacion_R03.py']='40648fd81c5b1f278ee9c18d0d464c5a4b5e9fd808054afe6ff072a10fda0ac5'
        files.update(p['dependencies_sha256'])
        seal={'schema':'DEE.PI08.C.prospective_source.seal.R02','sealed_utc':datetime.now(timezone.utc).isoformat(),'life_id':LIFE,'protocol_sha256':hashlib.sha256(data).hexdigest(),
              'source_prefix':{'life_id':manifest['life_id'],'path':str(pair),'alias':pair.name,'N':67,'T':view['physical']['tick'],'physical':view['physical'],'manifest_sha256':sha(manifestfile),'snapshot_sha256':manifest['snapshot_sha256'],'causal_prefix_sha256':view['causal_prefix_sha256'],'inherits_B_metadata':inheritedB},
              'files_sha256':files,'source_code_manifest_sha256':sha(Bmanifestfile),'Native_executed':False,'C_adoption_authorized':False,'limited_single_world_information_flow_only':True}
        if args.sellar:
            backup=P/'control/PROTOCOLO_C_R03_BORRADOR_LITERAL.json';require(not backup.exists(),'Preserve literal C draft')
            with backup.open('xb')as out:out.write(protocolfile.read_bytes())
            temporary=protocolfile.with_name(protocolfile.name+'.C_SEALING')
            with temporary.open('xb')as out:out.write(data);out.flush();os.fsync(out.fileno())
            os.replace(temporary,protocolfile);put(sealfile,seal)
        elif args.preparar:raise ValueError('C preparation requires an actual saved seal; use explicit --sellar before or together')
    if not args.preparar:
        print(json.dumps({'mode':'SEALED_NO_NATIVE'if args.sellar else'READ_ONLY_PLAN_NO_NATIVE','seal':seal,'next':'Root --preparar then one complete-pair import then Cpreparar3+evaluar6'},ensure_ascii=False,indent=2));return
    require(sealfile.exists()and sha(protocolfile)==seal['protocol_sha256'],'Actual prospective C seal required')
    require(not STAGE.exists()and not DEST.exists()and not OUT.exists(),'Fresh C stage/destination, never reset/retry')
    require(not(P/'PI08_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Root writer remains active')
    STAGE.mkdir();rows=[]
    for row in Bmanifest['files']:
        rel=PurePosixPath(row['file']);require(not rel.is_absolute()and all(v not in('.','..')for v in rel.parts)and not row['file'].startswith(('estado/','runtime/')),'Code-only source')
        src=safe(Bhome.joinpath(*rel.parts),[Bhome]);require(sha(src)==row['sha256'],'Frozen B code member changed')
        target=STAGE.joinpath(*rel.parts);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
    for name in ['pi08_consulta_condicional_C_R03.py','pi08_consulta_condicional_C_segunda_R02.py','PROTOCOLO_PI08_C_R02.json','SELLO_PI08_C_R03.json']:
        shutil.copyfile(H/name,STAGE/'capacidades'/name)
    wf=STAGE/'app/mundo_genesis_apd05.py';world=wf.read_text('utf-8-sig')
    world=once(world,'        pi08b.operational_dependencies(self.a,self.work_directory)\n',"        pi08b.operational_dependencies(self.a,self.work_directory)\n        from capacidades import pi08_consulta_condicional_C_R03 as pi08c\n        pi08c.operational_dependencies(self.a,self.work_directory)\n        for path in pi08c.code_files():\n            self.code_sha256['PI08C/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n")
    anchor="        if row is not None and str(row.get('modo','')).startswith('eci01-pi08-b-'):";require(world.count(anchor)==2,'Two frozen B routers required')
    index=world.index(anchor);world=world[:index]+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi08-c-'):\n            from capacidades import pi08_consulta_condicional_C_R03 as pi08c\n            pi08c.validate(self.a,row)\n            return\n"+world[index:]
    index=world.index(anchor,world.index('    def execute(self,payload):'));world=world[:index]+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi08-c-'):\n            from capacidades import pi08_consulta_condicional_C_R03 as pi08c\n            pi08c.validate(self.a,row)\n            self.before_mutation('PI08_C_CONDITIONAL_REGISTER_ACCESS_NATIVE_FLOW')\n            value=pi08c.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':pi08c.VERSION,'rows':[value]}\n"+world[index:]
    world=once(world,"        result['PI08_B']=pi08b.operational_dependencies(self.a,self.work_directory)\n","        result['PI08_B']=pi08b.operational_dependencies(self.a,self.work_directory)\n        from capacidades import pi08_consulta_condicional_C_R03 as pi08c\n        result['PI08_C']=pi08c.operational_dependencies(self.a,self.work_directory)\n")
    world=once(world,'    def external_uncertainty(self):\n','    def external_uncertainty(self):\n        from capacidades import pi08_consulta_condicional_C_R03 as pi08c\n        if pi08c.uncertain(self.a):return True\n');ast.parse(world);wf.write_text(world,encoding='utf8',newline='\n')
    qf=STAGE/'app/cola_local.py';q=qf.read_text('utf-8-sig');anchor="            if str(row.get('modo','')).startswith('eci01-pi08-b-'):";q=once(q,anchor,"            if str(row.get('modo','')).startswith('eci01-pi08-c-'):\n                from capacidades.pi08_consulta_condicional_C_R03 import validate_literal\n                validate_literal(row)\n                continue\n"+anchor);ast.parse(q);qf.write_text(q,encoding='utf8',newline='\n')
    files=[row['file']for row in Bmanifest['files']]+['capacidades/'+name for name in ['pi08_consulta_condicional_C_R03.py','pi08_consulta_condicional_C_segunda_R02.py','PROTOCOLO_PI08_C_R02.json','SELLO_PI08_C_R03.json']]
    for relative in files:
        file=STAGE/relative
        if file.suffix=='.py':ast.parse(file.read_text('utf-8-sig'))
        rows.append({'file':relative,'bytes':file.stat().st_size,'sha256':sha(file)})
    put(STAGE/'SISTEMA_CODIGO.json',{'schema':'DEE.PI08.C.isolated_source_capsule.R02','files':rows,'B_capsule_sha256':sha(Bmanifestfile),'Native_executed':False})
    system=DEST/'sistema';system.mkdir(parents=True)
    for row in rows:
        target=system/row['file'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(STAGE/row['file'],target);require(sha(target)==row['sha256'],'Copied C member differs')
    (system/'estado/checkpoints').mkdir(parents=True);(system/'runtime').mkdir();wheel='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl';os.link(C/'sistema/runtime'/wheel,system/'runtime'/wheel)
    context={'schema':'DEE.PI08.C.explicit_complete_import.R02','life':LIFE,'system':str(system),'prefix':seal['source_prefix']['path'],'prefix_manifest_sha256':seal['source_prefix']['manifest_sha256'],'source_code_manifest_sha256':sha(STAGE/'SISTEMA_CODIGO.json'),
             'tool_sources':[{'file':name,'sha256':sha(RP/name)}for name in('importar_diagnostico.py','observador_pasivo.py')],'never_select_or_promote':True,'Native_executed_by_preparation':False}
    put(DEST/'CONTEXTO_EJECUCION.json',context)
    put(OUT,{'schema':'DEE.PI08.C.isolated_system.prepared.R02','status':'PREPARED_NO_NATIVE','source_manifest':str(STAGE/'SISTEMA_CODIGO.json'),'source_manifest_sha256':sha(STAGE/'SISTEMA_CODIGO.json'),'context':str(DEST/'CONTEXTO_EJECUCION.json'),'context_sha256':sha(DEST/'CONTEXTO_EJECUCION.json'),'system':str(system),'directory':str(DEST),'life':LIFE,'Native_executed':False})
    print(json.dumps({'proof':str(OUT),'sha256':sha(OUT),'code_files':len(rows),'Native_executed':False},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prefijo');parser.add_argument('--sellar',action='store_true');parser.add_argument('--preparar',action='store_true');main(parser.parse_args())
