import ctypes
import typing as t
from pathlib import Path

from minidump import typedef, winapi


def create_minidump(pid: int, dest: str = '.', filename: str = None) -> t.Optional[Path]:
    with winapi.open_process(pid) as h_process:
        dumped_path = Path(dest, filename or f'{pid}.dmp')
        with winapi.create_file(str(dumped_path)) as h_file:
            if winapi.minidump_write_dump(h_process, pid, h_file):
                return dumped_path


@typedef.MINIDUMP_CALLBACK_FUNC
def MinidumpCallbackFunc(
    CallbackParam: ctypes.c_void_p, 
    CallbackInput: typedef.MINIDUMP_CALLBACK_INPUT, 
    CallbackOutput: typedef.MINIDUMP_CALLBACK_OUTPUT
) -> bool:
    if CallbackInput.contents.CallbackType == 16:
        CallbackOutput.contents.Status = 0x00000001
    return True

CALLBACK_FUNC = typedef.MINIDUMP_CALLBACK_INFORMATION(
    CallbackRoutine=MinidumpCallbackFunc,
    CallbackParam=None
)

def create_minidump_from_snapshot(pid: int, dest: str, filename: str = None) -> t.Optional[Path]:
    with winapi.open_process(pid) as h_process:
        with winapi.capture_snapshot(h_process) as h_snapshot:
            dumped_path = Path(dest, filename or f'{pid}.dmp')
            with winapi.create_file(str(dumped_path)) as h_file:
                if winapi.minidump_write_dump(h_snapshot, pid, h_file, CALLBACK_FUNC):
                    return dumped_path
