"""Prepare a separately sealed P0 guard source tree only, no S5 application."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;P=H.parent;S=P/'estados/candidato/sistema';OUT=H/'FUENTES_GUARDIA_PI05_R01_SELLADAS'
def sha(b):return hashlib.sha256(b).hexdigest()
def replace1(t,a,b):
    if t.count(a)!=1:raise ValueError('Expected exact source anchor absent: '+a[:80])
    return t.replace(a,b,1)
def main():
    if OUT.exists():raise ValueError('New guard patch tree only')
    source_packet=P/'control/PI05_REAL_FI_GLOBAL_R01.json';packet=json.loads(source_packet.read_text('utf8'))
    source=packet['actual']['result']['rows'][0]['legacy_result']['original_result']['native_trial']['before']
    if source['N']!=67 or source['tick']!=817876:raise ValueError('Exact measured causal parent')
    dependencies=['pi05_transito_causal_R01.py','PROTOCOLO_PI05_TRANSITO_R01.json','observador_global_PI05_R01.py',
                  'acceso_eci01.py','acciones_nativas_apd04.py','percepcion_cruda_fi01.py','mente_unificada_01.py']
    protocol={'schema':'DEE.PI05.P0_guard_sham.protocol.R01','status':'SEALED','source':source,
        'source_full_pair_manifest':{'path':str(P/'pares/REAL_PREFI_T817876/EXPORTACION_SERVICIO.json'),
            'sha256':sha((P/'pares/REAL_PREFI_T817876/EXPORTACION_SERVICIO.json').read_bytes())},
        'sites':{'guard':[19,53,20],'sham':[21,53,20]},
        'birth':{'state':0,'semantic':4,'s_reg':0,'direction':[0,0,0],'delay_ticks':2},
        'public_independent_operand_domain':[0,20],'prospective_first_comparison':[14,3],
        'fixed_decoder':'Original q+4 and q+6; neither changes or selects a favourable port/window',
        'old_material_inputs':176,'extra_material_inputs':1,'old_age_ticks':198,
        'dependencies_sha256':{n:sha((S/'capacidades'/n).read_bytes())for n in dependencies},
        'source_evidence':[{'file':str(p),'sha256':sha(p.read_bytes())}for p in
            (source_packet,P/'control/PROPUESTA_GUARDIA_PREFLIGHT_PASIVO_R01.json',P/'fuentes/PROPUESTA_INTERVENCION_LEGAL_Y_SHAM_PI05_R01.json')],
        'prepared_support_scope':'One fixed legal RAW-empty SEM4 birth, operator-designed P0. Not a taught answer, direct field/clock edit, learned recovery or self-regulation.',
        'separate_installation_mode':'Schedules one fixed birth at current+2 with0advance; current RAW-empty/diagnostic identity mandatory. It is pending until later legal admission; never reinsert during continuation.',
        'predetermined_checks':['All177receipts and extra support admission','SEM4 expectedRAW4<<60 persists at site','Intervened zero downstream,critical parent update and C/S/E','Fixed old q4/q6 output','Same inputs/dose/phase guard versus sham; matched original normal/global baseline','Representative earlier functions and continuation if useful'],
        'risks':['Persistent local support could block later legitimate traffic; evaluate conserved functions','Sham RAW-empty at69recorded boundaries is not a universal harmlessness guarantee','Input birth atcurrent+2 may reject if occupied at actual boundary; preserve rejection, neverclear/retry','Removing one zero does not predetermine the four-parent nonlinear outcome']}
    content={'capacidades/pi05_guardia_transito_R01.py':(H/'pi05_guardia_transito_R01.py').read_bytes(),
             'capacidades/PROTOCOLO_PI05_GUARDIA_R01.json':(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n').encode('utf8')}
    original={n:(S/n).read_bytes()for n in('app/cola_local.py','app/mundo_genesis_apd05.py')}
    if sha(original['app/cola_local.py'])!='d6b9be95e0f59c16a50bf2617e3e19f1483c76778782b5e045dc60d5208e199c'or sha(original['app/mundo_genesis_apd05.py'])!='dc0d185640b000cee25b405f6048b19f0351bfb9066a5b3044a40448b181907f':
        raise ValueError('Exact applied PI05 R01 source required; no overwrite of another revision')
    q=original['app/cola_local.py'].decode('utf8').replace('\r\n','\n')
    a="        for row in rows:\n"
    q=replace1(q,a,a+"            if row.get('modo')in('eci01-pi05-fiplus-guardia','eci01-pi05-fiplus-sham','eci01-pi05-guardia-preparar','eci01-pi05-sham-preparar'):\n                from capacidades.pi05_guardia_transito_R01 import validate_literal\n                validate_literal(row)\n                continue\n")
    o=original['app/mundo_genesis_apd05.py'].decode('utf8').replace('\r\n','\n')
    a="        return result\n\n    def validate(self,payload):"
    o=replace1(o,a,"        from capacidades import pi05_guardia_transito_R01 as support\n        for path in support.code_files():\n            self.code_sha256['PI05/support/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n"+a)
    cond="row.get('modo')in('eci01-pi05-fiplus-guardia','eci01-pi05-fiplus-sham','eci01-pi05-guardia-preparar','eci01-pi05-sham-preparar')"
    a="    def validate(self,payload):\n        row=self._eci01_row(payload)\n"
    o=replace1(o,a,a+"        if row is not None and "+cond+":\n            from capacidades import pi05_guardia_transito_R01 as support\n            support.validate(self.a,row)\n            return\n")
    a="    def execute(self,payload):\n        row=self._eci01_row(payload)\n"
    o=replace1(o,a,a+"        if row is not None and "+cond+":\n            from capacidades import pi05_guardia_transito_R01 as support\n            support.validate(self.a,row)\n            self.before_mutation('PI05_ONE_TIME_LEGAL_RAW_EMPTY_GUARD_OR_SHAM')\n            value=support.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':support.VERSION,'rows':[value]}\n")
    content['app/cola_local.py']=q.encode();content['app/mundo_genesis_apd05.py']=o.encode()
    for n in original:
        if b'\r\n'in original[n]:content[n]=content[n].replace(b'\n',b'\r\n')
    for name,data in content.items():
        if name.endswith('.py'):ast.parse(data.decode('utf8'),filename=name)
        else:json.loads(data)
    OUT.mkdir()
    rows=[]
    for name,data in content.items():
        p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        rows.append({'file':name,'bytes':len(data),'sha256':sha(data),'source_before_sha256':sha(original[name])if name in original else None})
    for name,data in original.items():
        p=OUT/'originales'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    proof={'schema':'DEE.PI05.P0_guard_source_patch.R01','source_system':str(S),'patch_tree':str(OUT),'files':rows,
           'applied':False,'Native_executed':False,'old_scientific_modules_changed':False,
           'scope':'Only four explicit guarded/P0 preparation modes ahead of old PI05 dispatcher; old handlers/capture/reader kernels remain literal.'}
    (OUT/'MANIFIESTO_CAMBIOS_PI05.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
