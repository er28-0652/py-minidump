import ctypes as ct
import ctypes.wintypes as wt
import contextlib
import typing as t
from pathlib import Path

from minidump import create_file, open_process

# macros
MiniDumpWithFullMemory = 0x2

PSS_CAPTURE_VA_CLONE                            = 0x00000001
PSS_CAPTURE_HANDLES                             = 0x00000004
PSS_CAPTURE_HANDLE_NAME_INFORMATION             = 0x00000008
PSS_CAPTURE_HANDLE_BASIC_INFORMATION            = 0x00000010
PSS_CAPTURE_HANDLE_TYPE_SPECIFIC_INFORMATION    = 0x00000020
PSS_CAPTURE_HANDLE_TRACE                        = 0x00000040
PSS_CAPTURE_THREADS                             = 0x00000080
PSS_CAPTURE_THREAD_CONTEXT                      = 0x00000100
PSS_CAPTURE_THREAD_CONTEXT_EXTENDED             = 0x00000200
PSS_CREATE_BREAKAWAY_OPTIONAL                   = 0x04000000
PSS_CREATE_BREAKAWAY                            = 0x08000000
PSS_CREATE_USE_VM_ALLOCATIONS                   = 0x20000000
PSS_CREATE_RELEASE_SECTION                      = 0x80000000

CONTEXT_ARM = 0x0200000
CONTEXT_CONTROL = (CONTEXT_ARM | 0x00000001)
CONTEXT_INTEGER = (CONTEXT_ARM | 0x00000002)
CONTEXT_FLOATING_POINT = (CONTEXT_ARM | 0x00000004)
CONTEXT_DEBUG_REGISTERS = (CONTEXT_ARM | 0x00000008)
CONTEXT_FULL = (CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_FLOATING_POINT)
CONTEXT_ALL = (CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_FLOATING_POINT | CONTEXT_DEBUG_REGISTERS)

# win api
PssCaptureSnapshot = ct.windll.kernel32.PssCaptureSnapshot
PssFreeSnapshot = ct.windll.kernel32.PssFreeSnapshot
GetCurrentProcess = ct.windll.kernel32.GetCurrentProcess
MiniDumpWriteDump = ct.windll.dbghelp.MiniDumpWriteDump
GetLastError = ct.GetLastError
    

class MINIDUMP_CALLBACK_OUTPUT(ct.Structure):
    _pack_ = 1
    _fields_ = [
        ('Status', ct.HRESULT)
    ]

class MINIDUMP_CALLBACK_INPUT(ct.Structure):
    _pack_ = 1
    _fields_ = [
        ('ProcessId', wt.UINT),
        ('ProcessHandle', wt.HANDLE),
        ('CallbackType', wt.UINT)
    ]

MINIDUMP_CALLBACK_FUNC = ct.WINFUNCTYPE(
    wt.BOOL,
    ct.c_void_p,
    ct.POINTER(MINIDUMP_CALLBACK_INPUT),
    ct.POINTER(MINIDUMP_CALLBACK_OUTPUT))
    
class MINIDUMP_CALLBACK_INFORMATION(ct.Structure):
    _pack_ = 1
    _fields_ = [
        ('CallbackRoutine', MINIDUMP_CALLBACK_FUNC),
        ('CallbackParam', ct.c_void_p)
    ]

@MINIDUMP_CALLBACK_FUNC
def MinidumpCallbackFunc(CallbackParam: ct.c_void_p, CallbackInput: MINIDUMP_CALLBACK_INPUT, CallbackOutput: MINIDUMP_CALLBACK_OUTPUT) -> bool:
    if CallbackInput.contents.CallbackType == 16:
        CallbackOutput.contents.Status = 0x00000001
    return True

PssCaptureSnapshot.argtypes = [
    wt.HANDLE,
    wt.DWORD,
    wt.DWORD,
    ct.POINTER(wt.HANDLE)
]
PssCaptureSnapshot.restype = wt.DWORD

MiniDumpWriteDump.argtypes = [
    wt.HANDLE,
    wt.DWORD,
    wt.DWORD,
    ct.c_ulong,
    ct.c_void_p,
    ct.c_void_p, 
    ct.POINTER(MINIDUMP_CALLBACK_INFORMATION)]
MiniDumpWriteDump.restype = wt.BOOL

callback = MINIDUMP_CALLBACK_INFORMATION(
    CallbackRoutine=MinidumpCallbackFunc,
    CallbackParam=None
)

@contextlib.contextmanager
def capture_snapshot(
    h_process: wt.HANDLE
) -> t.Iterable[wt.HANDLE]:
    try:
        capture_flags = PSS_CAPTURE_VA_CLONE\
            | PSS_CAPTURE_HANDLES\
            | PSS_CAPTURE_HANDLE_NAME_INFORMATION\
            | PSS_CAPTURE_HANDLE_BASIC_INFORMATION\
            | PSS_CAPTURE_HANDLE_TYPE_SPECIFIC_INFORMATION\
            | PSS_CAPTURE_HANDLE_TRACE\
            | PSS_CAPTURE_THREADS\
            | PSS_CAPTURE_THREAD_CONTEXT\
            | PSS_CAPTURE_THREAD_CONTEXT_EXTENDED\
            | PSS_CREATE_BREAKAWAY\
            | PSS_CREATE_BREAKAWAY_OPTIONAL\
            | PSS_CREATE_USE_VM_ALLOCATIONS\
            | PSS_CREATE_RELEASE_SECTION

        h_snapshot = wt.HANDLE()
        ret = PssCaptureSnapshot(
            h_process, capture_flags, CONTEXT_ALL, ct.byref(h_snapshot))
        if ret != 0:
            raise RuntimeError(f'PssCaptureSnapshot failed, err={ret}')
        yield h_snapshot
    finally:
        PssFreeSnapshot(GetCurrentProcess(), h_snapshot)      

def create_minidump_from_snapshot(pid: int, dest: str, filename: str = None) -> Path:
    with open_process(pid) as h_process:
        with capture_snapshot(h_process) as h_snapshot:
            dumped_path = Path(dest, filename or f'{pid}.dmp')
            with create_file(str(dumped_path)) as h_file:
                ret = MiniDumpWriteDump(
                    h_snapshot, pid, h_file, 
                    MiniDumpWithFullMemory, None, None, ct.byref(callback))
                if not ret:
                    raise RuntimeError(
                        f'MiniDumpWriteDump failed, err={GetLastError()}')    
                return dumped_path
