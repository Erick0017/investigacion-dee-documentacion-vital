"""Scoped path validation with per-scan directory identity cache.

Every leaf is lstat-checked; each ancestor is checked once per scope and freshly
again at the commit boundary. No symlink/reparse traversal is admitted. Content
hashing remains the responsibility of the unchanged checkpoint algorithms.
"""
from pathlib import Path
import os,stat
class PathGuard:
    def __init__(self,root):
        self.root=Path(root).resolve(strict=True);self.dirs={};self.leaf_checks=0;self.directory_checks=0;self.cache_hits=0;self.final_rechecks=0
        for part in reversed((self.root,*self.root.parents)):
            self._inspect(part,part.lstat(),directory=True)
    @staticmethod
    def identity(info):
        return(info.st_dev,info.st_ino,stat.S_IFMT(info.st_mode),getattr(info,'st_birthtime_ns',None))
    def _inspect(self,path,info,*,directory=False):
        if stat.S_ISLNK(info.st_mode)or getattr(info,'st_file_attributes',0)&1024:
            raise ValueError('Linked/reparse path refused: '+str(path))
        if directory:
            if not stat.S_ISDIR(info.st_mode):raise ValueError('Non-directory ancestor: '+str(path))
            previous=self.dirs.get(path)
            current=self.identity(info)
            if previous is not None and previous!=current:raise ValueError('Directory identity changed during closed scan: '+str(path))
            self.dirs[path]=current;self.directory_checks+=1
    def safe(self,path,*,exists=True,leaf_info=None):
        # abspath is lexical normalization, not filesystem resolution through
        # unchecked links. Root and every path segment are then checked below.
        value=Path(os.path.abspath(os.fspath(path)))
        if not value.is_relative_to(self.root):raise ValueError('Outside scoped C02 root')
        relative=value.relative_to(self.root);cursor=self.root
        for name in relative.parts[:-1]:
            cursor=cursor/name
            if cursor in self.dirs:self.cache_hits+=1;continue
            try:info=cursor.lstat()
            except FileNotFoundError:
                if exists:raise
                continue
            self._inspect(cursor,info,directory=True)
        try:info=leaf_info if leaf_info is not None else value.lstat()
        except FileNotFoundError:
            if exists:raise
            return value
        self.leaf_checks+=1;self._inspect(value,info,directory=stat.S_ISDIR(info.st_mode))
        return value
    def recheck(self):
        for path,identity in tuple(self.dirs.items()):
            info=path.lstat()
            if stat.S_ISLNK(info.st_mode)or getattr(info,'st_file_attributes',0)&1024 or self.identity(info)!=identity:
                raise ValueError('Fresh directory check failed before closed seal: '+str(path))
            self.final_rechecks+=1
    def stats(self):return {'leaf_lstats':self.leaf_checks,'directory_lstats':self.directory_checks,
                            'ancestor_cache_hits':self.cache_hits,'fresh_commit_directory_rechecks':self.final_rechecks,
                            'cached_directories':len(self.dirs)}
def scan_files(root,guard,hash_file,max_members,max_bytes):
    """O(files+directories) checks; never descends through an unchecked link."""
    root=guard.safe(root);stack=[root];files=[];dirs=[];total=0
    while stack:
        current=stack.pop()
        with os.scandir(current)as entries:
            batch=list(entries)
        for entry in batch:
            info=entry.stat(follow_symlinks=False)
            # DirEntry.stat can expose zero file IDs on some Windows builds.
            # Real directory lstat provides the stable identity used by recheck.
            path=guard.safe(entry.path)if stat.S_ISDIR(info.st_mode)else guard.safe(entry.path,leaf_info=info)
            relative=path.relative_to(root).as_posix()
            if stat.S_ISDIR(info.st_mode):dirs.append(relative);stack.append(path)
            elif stat.S_ISREG(info.st_mode):
                files.append({'file':relative,'bytes':info.st_size,'sha256':hash_file(path)});total+=info.st_size
                if len(files)>max_members or total>max_bytes:raise ValueError('Finite whole-source bound exceeded')
            else:raise ValueError('Nonregular checkpoint member')
    files.sort(key=lambda row:Path(row['file']));dirs.sort(key=Path)
    guard.recheck()
    return {'schema':'DEE.RBX01.C02.closed_native_component.R01','root_locator':str(root),
            'files':files,'directories':dirs,'bytes':total,'new_Native_ticks':0}
