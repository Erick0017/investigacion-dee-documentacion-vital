"""Read-only installed Python symbol/method inventory; not a C++ ABI promise."""
from pathlib import Path
import argparse,inspect,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from neutral_differential import native,put,sha


def signature(value):
    try:return str(inspect.signature(value))
    except (TypeError,ValueError):
        text=getattr(value,'__doc__',None)
        if text:return re.sub(r'0x[0-9A-Fa-f]+','0xADDRESS',text[:4096])
        return None


def inventory(args):
    _,engine=native(args.expected_version)
    import dee_thinking as package
    names=sorted(name for name in dir(package) if not name.startswith('_'));symbols={};classes={}
    for name in names:
        value=getattr(package,name)
        kind='class' if inspect.isclass(value) else 'callable' if callable(value) else 'module' if inspect.ismodule(value) else 'value'
        symbols[name]={'kind':kind,'defined_in':getattr(value,'__module__',None)}
        if kind=='callable':symbols[name]['signature_or_binding_doc']=signature(value)
        if kind=='class':
            attrs={}
            for attribute in sorted(x for x in dir(value) if not x.startswith('_')):
                member=getattr(value,attribute)
                attrs[attribute]={'kind':'callable' if callable(member) else 'property' if isinstance(member,property) else 'attribute',
                    'signature_or_binding_doc':signature(member) if callable(member) else None}
            classes[name]={'qualname':getattr(value,'__qualname__',None),'attributes':attrs,'constructor_doc':signature(value.__init__)}
    put(args.out,{'schema':'DEE45.installed_python_API.v1','engine':engine,'symbols':symbols,'classes':classes,
        'all_declared':getattr(package,'__all__',None),'scope':'Public installed module names and class attribute/method names; signatures/binding docs retained for review. No objects/worlds created. Not binary C++ ABI compatibility or exhaustive semantic equivalence.'})
    print(json.dumps({'library':args.expected_version,'public_symbols':len(symbols),'public_classes':len(classes)}))


def compare(args):
    a=json.loads(args.before.read_text(encoding='utf-8'));b=json.loads(args.after.read_text(encoding='utf-8'))
    before=set(a['symbols']);after=set(b['symbols']);class_changes=[]
    for name in sorted(set(a['classes'])&set(b['classes'])):
        old=set(a['classes'][name]['attributes']);new=set(b['classes'][name]['attributes'])
        changed=[x for x in sorted(old&new) if a['classes'][name]['attributes'][x]!=b['classes'][name]['attributes'][x]]
        if old!=new or changed:class_changes.append({'class':name,'removed':sorted(old-new),'added':sorted(new-old),'signature_or_documentation_changed':changed})
    removed=sorted(before-after);removed_methods=[{'class':x['class'],'removed':x['removed']} for x in class_changes if x['removed']]
    report={'schema':'DEE45.installed_python_API.diff.v1','before':a['engine']['library'],'after':b['engine']['library'],
        'before_inventory_sha256':sha(args.before),'after_inventory_sha256':sha(args.after),
        'removed_public_symbols':removed,'added_public_symbols':sorted(after-before),'class_changes':class_changes,
        'removed_public_class_attributes':removed_methods,
        'common_symbol_kind_changes':[{'name':x,'before':a['symbols'][x]['kind'],'after':b['symbols'][x]['kind']} for x in sorted(before&after) if a['symbols'][x]['kind']!=b['symbols'][x]['kind']],
        'name_surface_preserved':not removed and not removed_methods,
        'scope':'Surface compatibility only. Pointer addresses in binding docs normalized; changed docs/overloads require review, and no C++ binary ABI promise is made.'}
    put(args.out,report);print(json.dumps({'removed_symbols':len(removed),'removed_class_attributes':len(removed_methods),'added':len(after-before)}))
    if removed or removed_methods:raise SystemExit(1)


def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True)
    s=sub.add_parser('inventory');s.add_argument('--expected-version',required=True);s.add_argument('--out',type=Path,required=True)
    s=sub.add_parser('compare');s.add_argument('--before',type=Path,required=True);s.add_argument('--after',type=Path,required=True);s.add_argument('--out',type=Path,required=True)
    args=p.parse_args();{'inventory':inventory,'compare':compare}[args.mode](args)

if __name__=='__main__':main()
