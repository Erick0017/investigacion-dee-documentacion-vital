"""Two bounded transport operations for the existing Cognitive owner.

No engine/world import, owner launch, selection, promotion, geometry, expected
answer or actor policy. A technical pause is queued BEHIND a processing request
before completion, so the owner handles it before another idle quantum. Timeout
preserves the same ID; no resubmission or pending-queue cleanup is performed.
"""
from pathlib import Path
import argparse,datetime,importlib.util,json,os,re,sys,time,uuid

VERSION='PI04.bounded_existing_queue_client.OP1_CANDIDATE'
COMMANDS={'pi04-coordinacion-estado':'eci01-pi04-c2c-estado',
          'pi04-coordinacion-oportunidad':'eci01-pi04-c2c-oportunidad'}
TERMINAL={'completed','failed_preserved','uncertain','rejected_invalid'}

def read(file):return json.loads(Path(file).read_text(encoding='utf-8-sig'))

def owner_process_witness(status):
    """Corroborate only the published owner PID; no machine-wide inventory."""
    if os.name!='nt':raise ValueError('This bounded local client is verified for Windows only')
    pid=status.get('pid')
    if type(pid)is not int or pid<=0:raise ValueError('Owner PID missing from its published status')
    stamp=datetime.datetime.fromisoformat(status['wall_utc'].replace('Z','+00:00'))
    if stamp.tzinfo is None:raise ValueError('Owner publication lacks zoned time')
    age=(datetime.datetime.now(datetime.timezone.utc)-stamp.astimezone(datetime.timezone.utc)).total_seconds()
    if not 0<=age<=5:raise ValueError('Owner cache is stale; no request was queued')
    import ctypes
    from ctypes import wintypes
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE
    k.CloseHandle.argtypes=[wintypes.HANDLE];k.CloseHandle.restype=wintypes.BOOL
    k.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)];k.GetExitCodeProcess.restype=wintypes.BOOL
    k.QueryFullProcessImageNameW.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)]
    k.QueryFullProcessImageNameW.restype=wintypes.BOOL
    k.GetProcessTimes.argtypes=[wintypes.HANDLE,*([ctypes.POINTER(wintypes.FILETIME)]*4)];k.GetProcessTimes.restype=wintypes.BOOL
    handle=k.OpenProcess(0x1000,False,pid)
    if not handle:raise ValueError('The published owner PID cannot be corroborated; no auto-start or queued action')
    try:
        code=wintypes.DWORD()
        if not k.GetExitCodeProcess(handle,ctypes.byref(code))or code.value!=259:raise ValueError('Published owner is no longer running')
        size=wintypes.DWORD(32768);image=ctypes.create_unicode_buffer(size.value)
        if not k.QueryFullProcessImageNameW(handle,0,image,ctypes.byref(size)):raise ValueError('Cannot identify the published owner process')
        if Path(image.value).name.lower()not in('python.exe','python3.exe','python3.13.exe'):raise ValueError('Owner PID was reused by a different executable')
        created,exited,kernel,user=(wintypes.FILETIME()for _ in range(4))
        if not k.GetProcessTimes(handle,ctypes.byref(created),ctypes.byref(exited),ctypes.byref(kernel),ctypes.byref(user)):raise ValueError('Cannot corroborate owner creation time')
        ticks=(int(created.dwHighDateTime)<<32)|int(created.dwLowDateTime)
        start=datetime.datetime.fromtimestamp((ticks-116444736000000000)/10000000,datetime.timezone.utc)
        if start>stamp.astimezone(datetime.timezone.utc):raise ValueError('Owner PID was reused after the recorded publication')
        return {'pid':pid,'executable':image.value,'process_creation_utc':start.isoformat(),
                'publication_utc':stamp.isoformat(),'cache_age_seconds':age,'currently_running':True,
                'scope':'Host-process identity only; not instantaneous Native world observation or a new writer'}
    finally:k.CloseHandle(handle)

def run_queue(q,life,command,identifier,wait,*,clock=time.monotonic,sleep=time.sleep):
    """Only existing transport API. Tests may supply a visibly fake queue."""
    if command not in COMMANDS:raise ValueError('Only state or one next opportunity')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,70}',identifier):raise ValueError('Fresh bounded ASCII ID required')
    if not 1<=wait<=600:raise ValueError('Finite wait1..600seconds only')
    names={name:identifier+suffix for name,suffix in(('action',''),('resume','_resume'),('pause','_pause'),('save','_save'))}
    if any(q.get(name)is not None for name in names.values()):raise ValueError('ID/control suffix already used; inspect existing result, do not repeat')
    status=q.get_meta('owner')or{}
    if status.get('running')is not True or status.get('paused')is not True or status.get('uncertain_external_result'):
        raise ValueError('Open the existing owner explicitly and leave it paused; no auto-start/resume of uncertain state')
    counters=q.counters()
    if any(counters.get(k,0)for k in('queued','processing','uncertain')):
        raise ValueError('An earlier transport operation is unresolved; use its existing ID')
    payload={'operacion':'sesion','situaciones':[{'modo':COMMANDS[command]}],'actuador':'closed','retorno':'omit'}
    def put(name,value):
        if q.get(name)is not None:raise ValueError('Concurrent/reused ID preserved')
        result=q.put(name,value)
        if str(result.get('admission','')).startswith('rejected'):raise ValueError('Transport admission rejected; no retry: '+str(result))
        return result
    admission=put(names['action'],payload)
    put(names['resume'],{'operacion':'reanudar'})
    deadline=clock()+wait;pause_queued=False;action=None;pause=None
    while clock()<deadline:
        action=q.get(names['action']);resume=q.get(names['resume'])
        if resume and resume['status']in TERMINAL and resume['status']!='completed':
            return {'version':VERSION,'life_id':life,'id':identifier,'status':'RESUME_FAILED_REQUEST_PRESERVED',
                    'resume':resume,'request':action,'automatic_retry':False,'owner_started':False,'selection_modified':False}
        if action and action['status']in({'processing'}|TERMINAL)and not pause_queued:
            put(names['pause'],{'operacion':'pausar'});pause_queued=True
        pause=q.get(names['pause'])if pause_queued else None
        if action and action['status']in TERMINAL and pause and pause['status']in TERMINAL:break
        sleep(.02)
    closed_transport=bool(action and action['status']in TERMINAL and pause and pause['status']=='completed')
    if not closed_transport:
        if not pause_queued:put(names['pause'],{'operacion':'pausar'})
        return {'version':VERSION,'life_id':life,'id':identifier,'status':'WAITING_OR_UNCERTAIN_PRESERVED',
                'request':q.get(names['action']),'pause':q.get(names['pause']),'automatic_retry':False,
                'pending_cleared':False,'owner_started':False,'selection_modified':False,
                'inspect_same_id':'mente-unificada-resultado --vida '+life+' --id '+identifier}
    saved=None
    if action['status']=='completed':
        put(names['save'],{'operacion':'guardar'})
        # Technical checkpoint only; it does not send another stimulus/action.
        end=clock()+min(30,wait)
        while clock()<end:
            saved=q.get(names['save'])
            if saved and saved['status']in TERMINAL:break
            sleep(.02)
    decoded=json.loads(action['result'])if action.get('result')else None
    return {'version':VERSION,'life_id':life,'id':identifier,'status':action['status'],
            'admission':admission,'request':action,'native_result':decoded,'pause':pause,'save':saved,
            'saved_and_paused':bool(saved and saved['status']=='completed'and pause['status']=='completed'),
            'owner_started':False,'selection_modified':False,'automatic_retry':False,
            'scope':'Operator-triggered fixed protocol use through the existing queue; not learned initiative or an external decision policy.'}

def cli(arguments,*,system_root):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=tuple(COMMANDS));p.add_argument('--vida',required=True)
    p.add_argument('--id');p.add_argument('--esperar',type=float,default=600)
    p.add_argument('--material',action='store_true',help='Required to consume one native opportunity; state sends no Native inputs')
    p.add_argument('--diagnostico',action='store_true',help='Explicit isolated clone, never an unselected life in the product')
    a=p.parse_args(arguments);system=Path(system_root).resolve(strict=True)
    if not re.fullmatch(r'ECI02_PI03_REPRO_PI04_[A-Za-z0-9_]{1,48}',a.vida):raise ValueError('Explicit existing PI04 life only')
    if a.command.endswith('oportunidad')and not a.material:raise ValueError('Use --material for this explicit consumable opportunity')
    for node in(system,system/'app'):
        if node.is_symlink()or(getattr(node.lstat(),'st_file_attributes',0)&0x400):raise ValueError('No linked/reparse system')
    cardfile=system/'estado/vidas'/a.vida/'VIDA.json'
    card=read(cardfile)
    if card.get('life_id')!=a.vida:raise ValueError('Actual life-card identity differs')
    activefile=system/'estado/ACTIVO.json';active=read(activefile)if activefile.is_file()else{}
    if a.diagnostico:
        if(system.parent/'PROYECTO.json').exists()or active.get('life_id')==a.vida:
            raise ValueError('Diagnostic flag only outside the product and never on ACTIVO')
    elif a.command.endswith('oportunidad'):
        if active.get('life_id')!=a.vida or read(system.parent/'PROYECTO.json').get('selected_life')!=a.vida:
            raise ValueError('Use the actually adopted principal; this command never selects or promotes')
    world=card['world_id']
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}',world):raise ValueError('Bounded existing world identity required')
    db=system/'estado/servicios_persistentes'/world/'cola.sqlite3'
    if not db.is_file():raise ValueError('Existing owner not initialized; no implicit world/service creation')
    # Existing queue client, not Store/Native. Literal validation for these two
    # modes is stdlib-only; the separately opened owner performs Native calls.
    sys.path.insert(0,str(system))
    source=system/'app/cola_local.py'
    spec=importlib.util.spec_from_file_location('PI04_existing_queue',source)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    identifier=a.id or('pi04_cli_'+uuid.uuid4().hex)
    queue=m.QueueDB(db)
    witness=owner_process_witness(queue.get_meta('owner')or{})
    result=run_queue(queue,a.vida,a.command,identifier,a.esperar)
    result['owner_process_witness']=witness
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
    return 0 if result.get('status')=='completed'and result.get('saved_and_paused')else 2
