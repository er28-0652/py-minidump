import ctypes
import ctypes.wintypes
import contextlib
import typing as t

from minidump import typedef


# win api
CreateFileW = ctypes.windll.kernel32.CreateFileW
CloseHandle = ctypes.windll.kernel32.CloseHandle
OpenProcess = ctypes.windll.kernel32.OpenProcess
MiniDumpWriteDump = ctypes.windll.dbghelp.MiniDumpWriteDump
GetLastError = ctypes.GetLastError
PssCaptureSnapshot = ctypes.windll.kernel32.PssCaptureSnapshot
PssFreeSnapshot = ctypes.windll.kernel32.PssFreeSnapshot
GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess

# proto
PssCaptureSnapshot.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
    ctypes.POINTER(ctypes.wintypes.HANDLE)
]
PssCaptureSnapshot.restype = ctypes.wintypes.DWORD

# proto
MiniDumpWriteDump.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
    ctypes.c_ulong,
    ctypes.c_void_p,
    ctypes.c_void_p, 
    ctypes.POINTER(typedef.MINIDUMP_CALLBACK_INFORMATION)]
MiniDumpWriteDump.restype = ctypes.wintypes.BOOL


@contextlib.contextmanager
def create_file(filepath: str) -> t.Iterator[int]:
    try:
        h_file = CreateFileW(
            filepath,
            typedef.GENERIC_READ | typedef.GENERIC_WRITE,
            0,
            None,
            typedef.CREATE_ALWAYS,
            typedef.FILE_ATTRIBUTE_NORMAL,
            None)
        yield h_file
    finally:
        CloseHandle(h_file)

@contextlib.contextmanager
def open_process(pid: int) -> t.Iterator[int]:
    try:
        h_process = OpenProcess(typedef.PROCESS_ALL_ACCESS, False, pid)
        yield h_process
    finally:
        CloseHandle(h_process)

def minidump_write_dump(h_process, pid, h_file, callback=None):
    if MiniDumpWriteDump(
        h_process, pid, h_file,
        typedef.MiniDumpWithFullMemory, None, None, callback) == 1:
        return True
    raise RuntimeError(
        f'MiniDumpWriteDump failed, err_code={GetLastError()}')

@contextlib.contextmanager
def capture_snapshot(
    h_process: ctypes.wintypes.HANDLE
) -> t.Iterable[ctypes.wintypes.HANDLE]:
    try:
        capture_flags = typedef.PSS_CAPTURE_VA_CLONE\
            | typedef.PSS_CAPTURE_HANDLES\
            | typedef.PSS_CAPTURE_HANDLE_NAME_INFORMATION\
            | typedef.PSS_CAPTURE_HANDLE_BASIC_INFORMATION\
            | typedef.PSS_CAPTURE_HANDLE_TYPE_SPECIFIC_INFORMATION\
            | typedef.PSS_CAPTURE_HANDLE_TRACE\
            | typedef.PSS_CAPTURE_THREADS\
            | typedef.PSS_CAPTURE_THREAD_CONTEXT\
            | typedef.PSS_CAPTURE_THREAD_CONTEXT_EXTENDED\
            | typedef.PSS_CREATE_BREAKAWAY\
            | typedef.PSS_CREATE_BREAKAWAY_OPTIONAL\
            | typedef.PSS_CREATE_USE_VM_ALLOCATIONS\
            | typedef.PSS_CREATE_RELEASE_SECTION

        h_snapshot = ctypes.wintypes.HANDLE()
        ret = PssCaptureSnapshot(
            h_process, capture_flags, typedef.CONTEXT_ALL, ctypes.byref(h_snapshot))
        if ret != 0:
            raise RuntimeError(f'PssCaptureSnapshot failed, err={ret}')
        yield h_snapshot
    finally:
        PssFreeSnapshot(GetCurrentProcess(), h_snapshot)  