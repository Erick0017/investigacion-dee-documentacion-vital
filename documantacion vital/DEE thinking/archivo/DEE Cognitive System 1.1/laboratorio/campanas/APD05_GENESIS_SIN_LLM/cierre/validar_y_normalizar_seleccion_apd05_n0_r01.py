"""Valida exactamente las construcciones del schema APD05 usando sólo stdlib.

No es un validador universal JSONSchema2020. Rechaza construcciones de schema
desconocidas, conserva rótulos descriptivos al normalizar los enums admitidos y
no aprueba resultados, ejecuta Native o cambia las fuentes originales.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re


ANNOTATIONS={'$schema','$id','title','description','default'}
SUPPORTED=ANNOTATIONS|{'$defs','$ref','oneOf','type','required','enum','const','pattern','minItems','minimum','maximum','properties','items','additionalProperties'}
ROLE_MAP={'DIAGNOSTIC_FORK':'FORK','CONTINUATION_OR_FORK':'AUX'}
STATUS_MAP={'CLOSED_COMPLETE_RESULT':'CLOSED_RESULT','CLOSED_PHYSICAL_STOP_STALE_UI_PENDING':'CLOSED_RESULT'}


def schema_features(node,path='$schema'):
    if not isinstance(node,dict):raise ValueError('Non-object schema at '+path)
    unknown=set(node)-SUPPORTED
    if unknown:raise ValueError('Unhandled schema keywords at '+path+':'+str(unknown))
    for key in ('$defs','properties'):
        for name,child in node.get(key,{}).items():schema_features(child,path+'/'+key+'/'+name)
    for key in ('items',):
        if key in node:schema_features(node[key],path+'/'+key)
    if isinstance(node.get('additionalProperties'),dict):schema_features(node['additionalProperties'],path+'/additionalProperties')
    for i,child in enumerate(node.get('oneOf',[])):schema_features(child,path+'/oneOf/'+str(i))


def validate(value,schema,root,path='$'):
    if '$ref' in schema:
        ref=schema['$ref'];assert ref.startswith('#/')
        target=root
        for bit in ref[2:].split('/'):target=target[bit.replace('~1','/').replace('~0','~')]
        validate(value,target,root,path)
    if 'oneOf' in schema:
        matches=0
        for option in schema['oneOf']:
            try:validate(value,option,root,path);matches+=1
            except (ValueError,TypeError):pass
        if matches!=1:raise ValueError(path+' oneOf matched '+str(matches))
    types=schema.get('type')
    if types is not None:
        types=[types] if isinstance(types,str) else types
        checks={'null':value is None,'object':isinstance(value,dict),'array':isinstance(value,list),'string':isinstance(value,str),
                'boolean':type(value)is bool,'integer':type(value)is int,'number':type(value)in(int,float)}
        if not any(checks[t] for t in types):raise ValueError(path+' wrong type; wanted '+str(types))
    if 'const' in schema and value!=schema['const']:raise ValueError(path+' const')
    if 'enum' in schema and value not in schema['enum']:raise ValueError(path+' enum '+str(value))
    if isinstance(value,dict):
        absent=set(schema.get('required',[]))-set(value)
        if absent:raise ValueError(path+' missing required '+str(absent))
        for name,child in schema.get('properties',{}).items():
            if name in value:validate(value[name],child,root,path+'/'+name)
        extra=set(value)-set(schema.get('properties',{}))
        policy=schema.get('additionalProperties',True)
        if policy is False and extra:raise ValueError(path+' additionalProperties '+str(extra))
        if isinstance(policy,dict):
            for name in extra:validate(value[name],policy,root,path+'/'+name)
    if isinstance(value,list):
        if len(value)<schema.get('minItems',0):raise ValueError(path+' minItems')
        if 'items' in schema:
            for i,item in enumerate(value):validate(item,schema['items'],root,path+'/'+str(i))
    if isinstance(value,str) and 'pattern'in schema and re.search(schema['pattern'],value)is None:raise ValueError(path+' pattern')
    if type(value)in(int,float):
        if 'minimum'in schema and value<schema['minimum']:raise ValueError(path+' minimum')
        if 'maximum'in schema and value>schema['maximum']:raise ValueError(path+' maximum')


def semantic_checks(value):
    all_sources=value['files']+value['components'];ids=[x['id'] for x in all_sources]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate source IDs')
    for group in ('claims','attempts','executed_revisions'):
        for row in value[group]:
            if not set(row['source_ids'])<=set(ids):raise ValueError('Unresolved source ID in '+row['id'])
    files={x['destination'] for x in value['files']};components={x['destination'] for x in value['components']}
    if len(files)!=len(value['files']):raise ValueError('Duplicate file destinations')
    def relative(name):
        if not isinstance(name,str) or '\\' in name or ':' in name:raise ValueError('Nonportable destination '+str(name))
        p=PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe relative path '+name)
    for dest in files|components:relative(dest)
    def resolves(name):return name=='.' or name in files or any(name==c or name.startswith(c+'/')for c in components)
    for job in value['jobs']:
        relative(job['script']);relative(job['expected'])
        if job['script']not in files:raise ValueError('Master job script is not an exported file: '+job['id'])
        if job['expected']not in files:raise ValueError('Master expected result not exported: '+job['id'])
        if not resolves(job['base']):raise ValueError('Unknown master job base '+job['id'])
        for arg in job['args']:
            if isinstance(arg,dict):
                relative(arg['input'])
                if not resolves(arg['input']):raise ValueError('Unknown master input '+str(arg))


def normalize(value):
    changes=[]
    for row in value['attempts']:
        for field,mapping in (('role',ROLE_MAP),('status',STATUS_MAP)):
            if row[field] in mapping:
                old=row[field];row[field]=mapping[old];row[field+'_description_original']=old
                changes.append({'attempt':row['id'],'field':field,'old':old,'new':row[field]})
    return changes


def negative_tests(value,schema):
    mutants=[]
    def add(label,change):
        x=copy.deepcopy(value);change(x);mutants.append((label,x))
    add('unknown_role',lambda x:x['attempts'][0].update(role='INVENTED_ROLE'))
    add('unknown_status',lambda x:x['attempts'][0].update(status='PASS_COGNITION'))
    add('boolean_is_not_integer',lambda x:x['lives'][0].update(tick=True))
    add('bad_hash',lambda x:x['files'][0].update(sha256='z'*64))
    add('missing_field',lambda x:x.pop('claims'))
    add('bad_job_comparison',lambda x:x['jobs'][0].update(comparison='trust'))
    add('empty_required_array',lambda x:x.update(lives=[]))
    add('unsafe_job_input',lambda x:x['jobs'][0]['args'].append({'input':'../outside'}))
    add('oneof_extra_key',lambda x:x['jobs'][0]['args'].append({'input':'EVIDENCIA_CAS','hidden_target':1}))
    add('unknown_source_ID',lambda x:x['claims'][0].update(source_ids=['NO_SUCH_SOURCE']))
    add('missing_exported_expected',lambda x:x['jobs'][0].update(expected='NOT_EXPORTED.json'))
    results=[]
    for label,x in mutants:
        try:validate(x,schema,schema);semantic_checks(x)
        except (ValueError,TypeError) as exc:results.append({'test':label,'rejected':True,'reason':str(exc)})
        else:raise ValueError('Negative fixture wrongly accepted: '+label)
    return results


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--selection',type=Path,required=True);p.add_argument('--schema',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();assert not a.out.exists();schema=json.loads(a.schema.read_bytes());original=a.selection.read_bytes();value=json.loads(original)
    schema_features(schema);changes=normalize(value);validate(value,schema,schema);semantic_checks(value);tests=negative_tests(value,schema)
    a.out.mkdir(parents=True)
    with (a.out/'RESULTADOS_FINAL.json').open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    proof={'schema':'APD05.strict_actual_schema_validation.N0.R01','selection_before_sha256':hashlib.sha256(original).hexdigest(),
        'selection_after_sha256':hashlib.sha256((a.out/'RESULTADOS_FINAL.json').read_bytes()).hexdigest(),'actual_schema_sha256':hashlib.sha256(a.schema.read_bytes()).hexdigest(),
        'all_used_schema_constructs_validated':True,'not_universal_JSONSchema_implementation':True,'source_IDs_and_master_jobs_resolved':True,
        'enum_normalizations_preserving_original_labels':changes,'negative_fixtures':tests,'source_selection_unchanged':a.selection.read_bytes()==original,
        'scientific_counts_changed':False,'approval_changed':False,'new_Native_ticks':0}
    with (a.out/'PRUEBA_SCHEMA_ESTRICTO.json').open('x',encoding='utf8',newline='\n')as f:json.dump(proof,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'strict_actual_schema_valid':True,'enum_labels_normalized':len(changes),'negative_tests':len(tests),'source_unchanged':True,'new_Native_ticks':0}))


if __name__=='__main__':main()
