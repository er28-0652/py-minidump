# py-minidump

Interface for `MiniDumpWriteDump` and `PssCaptureSnapshot` written in Python.

## Requirement

 * python >= 3.6
 * Administrators privilege in Windows

## Install

```bash
> git clone https://github.com/er28-0652/py-minidump.git
> cd py-minidump
> python setup.py install
```

## Usage

Open PowerShell as administrator.

#### Use `MiniDumpWriteDump` to create minidump

```bash
PS > python -m minidump -p <PID>
```

#### Use `PssCaptureSnapshot` to create minidump

```bash
PS > python -m minidump -p <PID> --snapshot
```