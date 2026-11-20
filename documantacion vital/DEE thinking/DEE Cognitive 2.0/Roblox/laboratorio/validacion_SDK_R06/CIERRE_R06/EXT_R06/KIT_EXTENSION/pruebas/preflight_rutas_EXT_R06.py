"""Read-only explicit-path check; no Native import, DLLload, Store, HTTP or process launch."""
from pathlib import Path
import argparse,json

def inspect(root,relative,label):
 p=Path(relative)
 if p.is_absolute()or'..'in p.parts:raise ValueError('Containedrelativepathrequired')
 target=root/p;resolved=target.resolve(strict=True)
 if not resolved.is_relative_to(root):raise ValueError('Escapedruntime')
 cursor=root
 for part in p.parts:
  cursor=cursor/part
  if cursor.is_symlink()or getattr(cursor.lstat(),'st_file_attributes',0)&1024:raise ValueError('Linkedpathnotaccepted')
 units=len(str(resolved).encode('utf-16-le'))//2
 return{'label':label,'path':str(resolved),'exists':True,'isFile':resolved.is_file(),'utf16PathUnits':units,'warningLongPath':units>240,'interpretation':'Lengthheuristiconly; no loader test performed'}

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--runtime-root',type=Path,required=True);a.add_argument('--native-pyd',required=True);a.add_argument('--python');a.add_argument('--launcher');v=a.parse_args()
 root=v.runtime_root.resolve(strict=True)
 if root.is_symlink():raise ValueError('Linkedruntime')
 if not Path(v.native_pyd).name.startswith('_native')or not v.native_pyd.lower().endswith('.pyd'):raise ValueError('Explicit_nativePYDrequired')
 rows=[inspect(root,v.native_pyd,'NativePYD')]
 if v.python:rows.append(inspect(root,v.python,'PrivatePython'))
 if v.launcher:rows.append(inspect(root,v.launcher,'FrozenEXTlauncher'))
 print(json.dumps({'schema':'DEE.SDK.EXT.ShortPathPreflight.R06','NativeImported':False,'DLLLoaded':False,'StoreCreated':False,'HttpRequested':False,'ProcessLaunched':False,'paths':rows,'loaderVerified':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
