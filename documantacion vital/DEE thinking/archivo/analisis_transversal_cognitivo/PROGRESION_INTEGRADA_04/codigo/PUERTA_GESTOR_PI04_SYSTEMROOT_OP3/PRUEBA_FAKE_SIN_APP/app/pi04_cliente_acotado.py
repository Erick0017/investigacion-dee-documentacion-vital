import json
def cli(arguments,*,system_root):
 print(json.dumps({'FAKE_TRANSPORT_ONLY':True,'arguments':arguments,'system_root':str(system_root),'Native_ticks':0})); return 0
