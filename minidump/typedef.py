import ctypes
import ctypes.wintypes

# for CreateFile
PROCESS_ALL_ACCESS = 0x000F0000 | 0x00100000 | 0xFFF
GENERIC_READ = -0x80000000
GENERIC_WRITE = 0x40000000
CREATE_ALWAYS = 0x2
FILE_ATTRIBUTE_NORMAL = 0x80

# for MiniDumpWriteDump
MiniDumpWithFullMemory = 0x2

# for PssCaptureSnapshot
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

# for PssCaptureSnapshot
CONTEXT_ARM = 0x0200000
CONTEXT_CONTROL = (CONTEXT_ARM | 0x00000001)
CONTEXT_INTEGER = (CONTEXT_ARM | 0x00000002)
CONTEXT_FLOATING_POINT = (CONTEXT_ARM | 0x00000004)
CONTEXT_DEBUG_REGISTERS = (CONTEXT_ARM | 0x00000008)
CONTEXT_FULL = (CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_FLOATING_POINT)
CONTEXT_ALL = (CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_FLOATING_POINT | CONTEXT_DEBUG_REGISTERS)


class MINIDUMP_CALLBACK_OUTPUT(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('Status', ctypes.HRESULT)
    ]

class MINIDUMP_CALLBACK_INPUT(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('ProcessId', ctypes.wintypes.UINT),
        ('ProcessHandle', ctypes.wintypes.HANDLE),
        ('CallbackType', ctypes.wintypes.UINT)
    ]

MINIDUMP_CALLBACK_FUNC = ctypes.WINFUNCTYPE(
    ctypes.wintypes.BOOL,
    ctypes.c_void_p,
    ctypes.POINTER(MINIDUMP_CALLBACK_INPUT),
    ctypes.POINTER(MINIDUMP_CALLBACK_OUTPUT))

class MINIDUMP_CALLBACK_INFORMATION(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('CallbackRoutine', MINIDUMP_CALLBACK_FUNC),
        ('CallbackParam', ctypes.c_void_p)
    ]