"""Windows 轻量隔离：受限令牌（或 AppContainer）+ 作业对象。

restricted（默认）：
  - CreateRestrictedToken(DISABLE_MAX_PRIVILEGE | LUA_TOKEN)，管理员组设为仅拒绝（deny-only），去掉除 SeChangeNotify 外的所有特权
  - 令牌完整性级别设为低（S-1-16-4096）：Windows 的强制完整性控制禁止低完整性进程写入中 / 高完整性的文件、注册表与进程
    （“不向上写”），所以只有被标为低完整性的目录可写：工作空间、私有临时目录 / HOME、声明的可写路径（icacls /setintegritylevel）
  - 读取不受限（强制完整性控制只限制写）；不限制网络
appcontainer：
  - CreateAppContainerProfile + SECURITY_CAPABILITIES：进程运行在 AppContainer 中，默认不能访问用户文件（读写都不行）、
    不能联网；按策略授予工作空间（完全控制）、只读路径（读取和执行）的 ACL，联网时授予 internetClient / privateNetworkClientServer 能力
两种方式都把进程放进作业对象：随启动器结束而结束（KILL_ON_JOB_CLOSE）、可选进程数 / 内存上限、
界面限制（不能切换桌面、改显示设置、注销关机、读剪贴板、使用作业外的窗口句柄）。

尚未在 Windows 实机上验证（见 docs/sandbox.md）。
"""

from __future__ import annotations

from foxos.i18n import tr
import os
import subprocess
import sys
import threading

IS_WIN = os.name == "nt"

# 常量
TOKEN_DUPLICATE, TOKEN_QUERY, TOKEN_ASSIGN_PRIMARY, TOKEN_ADJUST_DEFAULT = 0x2, 0x8, 0x1, 0x80
DISABLE_MAX_PRIVILEGE, LUA_TOKEN = 0x1, 0x4
SE_GROUP_USE_FOR_DENY_ONLY, SE_GROUP_INTEGRITY, SE_GROUP_ENABLED = 0x10, 0x20, 0x4
TokenIntegrityLevel = 25
CREATE_SUSPENDED, CREATE_UNICODE_ENVIRONMENT, EXTENDED_STARTUPINFO_PRESENT, CREATE_NO_WINDOW = 0x4, 0x400, 0x80000, 0x08000000
STARTF_USESTDHANDLES = 0x100
JobObjectBasicUIRestrictions, JobObjectExtendedLimitInformation = 4, 9
JOB_OBJECT_LIMIT_ACTIVE_PROCESS, JOB_OBJECT_LIMIT_JOB_MEMORY, JOB_OBJECT_LIMIT_DIE_ON_UNHANDLED_EXCEPTION, JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x8, 0x200, 0x400, 0x2000
UI_LIMITS = 0x1 | 0x2 | 0x8 | 0x10 | 0x20 | 0x40 | 0x80  # HANDLES READCLIPBOARD SYSTEMPARAMETERS DISPLAYSETTINGS GLOBALATOMS DESKTOP EXITWINDOWS
PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES = 0x00020009
WAIT_TIMEOUT, INFINITE = 0x102, 0xFFFFFFFF
SID_ADMINS, SID_LOW_IL = "S-1-5-32-544", "S-1-16-4096"
CAP_INTERNET_CLIENT, CAP_PRIVATE_NETWORK = "S-1-15-3-1", "S-1-15-3-3"
HRESULT_ALREADY_EXISTS = 0x800700B7 - (1 << 32)


def icacls_plan(policy, mode: str, sid: str | None = None) -> list[list[str]]:
    """需要执行的 icacls 命令（纯函数，便于测试与 --dry-run 展示）。"""
    pd = policy.to_dict() if hasattr(policy, "to_dict") else policy
    writes = [p for p in [pd["workspace"], pd.get("tmp"), pd.get("private_home"), *(pd.get("write") or [])] if p]
    if mode == "restricted":
        return [["icacls", p, "/setintegritylevel", "(OI)(CI)low"] for p in writes]
    out = [["icacls", p, "/grant", f"*{sid}:(OI)(CI)F"] for p in writes]
    out += [["icacls", p, "/grant", f"*{sid}:(OI)(CI)RX"] for p in (pd.get("read") or [])]
    return out


def capabilities() -> dict:
    if not IS_WIN:
        return {"platform": "windows", "available": False, "reason": tr("sandbox.windows.not_windows")}
    import ctypes
    k32 = ctypes.WinDLL("kernel32")
    has_ac = bool(getattr(ctypes.WinDLL("userenv"), "CreateAppContainerProfile", None))
    has_job = bool(getattr(k32, "CreateJobObjectW", None))
    return {"platform": "windows", "mechanism": "restricted-token+job" , "available": has_job, "modes": ["restricted"] + (["appcontainer"] if has_ac else []),
            "filesystem": "write" , "filesystem_appcontainer": "read+write" if has_ac else None, "network": "appcontainer" if has_ac else False,
            "signal_scope": True, "verified_on_hardware": False, "reason": None}


if IS_WIN:
    import ctypes
    import msvcrt
    from ctypes import wintypes as W

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    adv = ctypes.WinDLL("advapi32", use_last_error=True)
    uenv = ctypes.WinDLL("userenv", use_last_error=True)

    class SID_AND_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("Sid", ctypes.c_void_p), ("Attributes", W.DWORD)]

    class STARTUPINFOW(ctypes.Structure):
        _fields_ = [("cb", W.DWORD), ("lpReserved", W.LPWSTR), ("lpDesktop", W.LPWSTR), ("lpTitle", W.LPWSTR), ("dwX", W.DWORD), ("dwY", W.DWORD),
                    ("dwXSize", W.DWORD), ("dwYSize", W.DWORD), ("dwXCountChars", W.DWORD), ("dwYCountChars", W.DWORD), ("dwFillAttribute", W.DWORD),
                    ("dwFlags", W.DWORD), ("wShowWindow", W.WORD), ("cbReserved2", W.WORD), ("lpReserved2", ctypes.c_void_p),
                    ("hStdInput", W.HANDLE), ("hStdOutput", W.HANDLE), ("hStdError", W.HANDLE)]

    class STARTUPINFOEXW(ctypes.Structure):
        _fields_ = [("StartupInfo", STARTUPINFOW), ("lpAttributeList", ctypes.c_void_p)]

    class PROCESS_INFORMATION(ctypes.Structure):
        _fields_ = [("hProcess", W.HANDLE), ("hThread", W.HANDLE), ("dwProcessId", W.DWORD), ("dwThreadId", W.DWORD)]

    class SECURITY_CAPABILITIES(ctypes.Structure):
        _fields_ = [("AppContainerSid", ctypes.c_void_p), ("Capabilities", ctypes.c_void_p), ("CapabilityCount", W.DWORD), ("Reserved", W.DWORD)]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [(n, ctypes.c_ulonglong) for n in ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount", "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong), ("LimitFlags", W.DWORD),
                    ("MinimumWorkingSetSize", ctypes.c_size_t), ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", W.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", W.DWORD), ("SchedulingClass", W.DWORD)]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION), ("IoInfo", IO_COUNTERS), ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

    H, P, D, B = W.HANDLE, ctypes.c_void_p, W.DWORD, W.BOOL
    _SIG = {
        (k32, "GetCurrentProcess"): ([], H), (k32, "CloseHandle"): ([H], B), (k32, "LocalFree"): ([P], P),
        (k32, "CreateJobObjectW"): ([P, W.LPCWSTR], H), (k32, "SetInformationJobObject"): ([H, ctypes.c_int, P, D], B),
        (k32, "AssignProcessToJobObject"): ([H, H], B), (k32, "TerminateJobObject"): ([H, ctypes.c_uint], B),
        (k32, "TerminateProcess"): ([H, ctypes.c_uint], B), (k32, "ResumeThread"): ([H], D),
        (k32, "WaitForSingleObject"): ([H, D], D), (k32, "GetExitCodeProcess"): ([H, ctypes.POINTER(D)], B),
        (k32, "InitializeProcThreadAttributeList"): ([P, D, D, ctypes.POINTER(ctypes.c_size_t)], B),
        (k32, "UpdateProcThreadAttribute"): ([P, D, ctypes.c_size_t, P, ctypes.c_size_t, P, P], B),
        (k32, "CreateProcessW"): ([W.LPCWSTR, W.LPWSTR, P, P, B, D, P, W.LPCWSTR, P, P], B),
        (adv, "OpenProcessToken"): ([H, D, ctypes.POINTER(H)], B),
        (adv, "CreateRestrictedToken"): ([H, D, D, P, D, P, D, P, ctypes.POINTER(H)], B),
        (adv, "SetTokenInformation"): ([H, ctypes.c_int, P, D], B), (adv, "GetLengthSid"): ([P], D),
        (adv, "ConvertStringSidToSidW"): ([W.LPCWSTR, ctypes.POINTER(P)], B), (adv, "ConvertSidToStringSidW"): ([P, ctypes.POINTER(W.LPWSTR)], B),
        (adv, "CreateProcessAsUserW"): ([H, W.LPCWSTR, W.LPWSTR, P, P, B, D, P, W.LPCWSTR, P, P], B),
        (uenv, "CreateAppContainerProfile"): ([W.LPCWSTR, W.LPCWSTR, W.LPCWSTR, P, D, ctypes.POINTER(P)], ctypes.c_long),
        (uenv, "DeriveAppContainerSidFromAppContainerName"): ([W.LPCWSTR, ctypes.POINTER(P)], ctypes.c_long),
    }
    for (_dll, _name), (_args, _res) in _SIG.items():
        try:
            _f = getattr(_dll, _name)
        except AttributeError:
            continue
        _f.argtypes, _f.restype = _args, _res

    def _ok(r, what):
        if not r:
            e = ctypes.get_last_error()
            raise OSError(e, f"{what}: {ctypes.FormatError(e).strip()}")
        return r

    def _sid(s: str):
        p = ctypes.c_void_p()
        _ok(adv.ConvertStringSidToSidW(W.LPCWSTR(s), ctypes.byref(p)), f"ConvertStringSidToSid {s}")
        return p

    def _sid_str(p) -> str:
        s = W.LPWSTR()
        _ok(adv.ConvertSidToStringSidW(p, ctypes.byref(s)), "ConvertSidToStringSid")
        v = s.value
        k32.LocalFree(s)
        return v

    def restricted_token():
        cur = W.HANDLE()
        _ok(adv.OpenProcessToken(k32.GetCurrentProcess(), TOKEN_DUPLICATE | TOKEN_QUERY | TOKEN_ASSIGN_PRIMARY | TOKEN_ADJUST_DEFAULT, ctypes.byref(cur)), "OpenProcessToken")
        deny = (SID_AND_ATTRIBUTES * 1)(SID_AND_ATTRIBUTES(_sid(SID_ADMINS).value, 0))
        tok = W.HANDLE()
        _ok(adv.CreateRestrictedToken(cur, DISABLE_MAX_PRIVILEGE | LUA_TOKEN, 1, deny, 0, None, 0, None, ctypes.byref(tok)), "CreateRestrictedToken")
        k32.CloseHandle(cur)
        low = _sid(SID_LOW_IL)
        tml = SID_AND_ATTRIBUTES(low.value, SE_GROUP_INTEGRITY)
        size = ctypes.sizeof(tml) + adv.GetLengthSid(low)
        _ok(adv.SetTokenInformation(tok, TokenIntegrityLevel, ctypes.byref(tml), size), "SetTokenInformation(IntegrityLevel)")
        return tok

    def appcontainer_sid(profile: str):
        name = f"foxos.sandbox.{profile}"[:64]
        sid = ctypes.c_void_p()
        hr = uenv.CreateAppContainerProfile(W.LPCWSTR(name), W.LPCWSTR(f"FoxOS sandbox {profile}"), W.LPCWSTR("FoxOS light sandbox"), None, 0, ctypes.byref(sid))
        if hr == HRESULT_ALREADY_EXISTS:
            hr = uenv.DeriveAppContainerSidFromAppContainerName(W.LPCWSTR(name), ctypes.byref(sid))
        if hr < 0:
            raise OSError(hr & 0xFFFFFFFF, tr("sandbox.windows.createappcontainerprofile_failed_0x", hr & 0xFFFFFFFF))
        return sid

    def job_object(policy):
        job = _ok(k32.CreateJobObjectW(None, None), "CreateJobObject")
        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        flags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_DIE_ON_UNHANDLED_EXCEPTION
        if policy.max_processes:
            flags |= JOB_OBJECT_LIMIT_ACTIVE_PROCESS
            info.BasicLimitInformation.ActiveProcessLimit = int(policy.max_processes)
        if policy.memory_mb:
            flags |= JOB_OBJECT_LIMIT_JOB_MEMORY
            info.JobMemoryLimit = int(policy.memory_mb) * 1024 * 1024
        info.BasicLimitInformation.LimitFlags = flags
        _ok(k32.SetInformationJobObject(W.HANDLE(job), JobObjectExtendedLimitInformation, ctypes.byref(info), ctypes.sizeof(info)), "SetInformationJobObject(limits)")
        ui = W.DWORD(UI_LIMITS)
        _ok(k32.SetInformationJobObject(W.HANDLE(job), JobObjectBasicUIRestrictions, ctypes.byref(ui), ctypes.sizeof(ui)), "SetInformationJobObject(ui)")
        return job

    def _env_block(env: dict) -> ctypes.Array:
        s = "".join(f"{k}={v}\0" for k, v in sorted(env.items(), key=lambda kv: kv[0].upper())) + "\0"
        return ctypes.create_unicode_buffer(s, len(s))

    def _spawn(policy, argv, cwd, stdio, profile):
        mode = policy.windows_mode or "restricted"
        env = {**os.environ, **(policy.env or {}), "FOXOS_SANDBOX": "light"}
        sid_s = None
        si = STARTUPINFOEXW()
        si.StartupInfo.cb = ctypes.sizeof(si) if mode == "appcontainer" else ctypes.sizeof(STARTUPINFOW)
        si.StartupInfo.dwFlags = STARTF_USESTDHANDLES
        si.StartupInfo.hStdInput, si.StartupInfo.hStdOutput, si.StartupInfo.hStdError = stdio
        cmdline = ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
        pi = PROCESS_INFORMATION()
        flags = CREATE_SUSPENDED | CREATE_UNICODE_ENVIRONMENT
        keep = []
        if mode == "appcontainer":
            sid = appcontainer_sid(profile)
            sid_s = _sid_str(sid)
            caps = (SID_AND_ATTRIBUTES * 2)(SID_AND_ATTRIBUTES(_sid(CAP_INTERNET_CLIENT).value, SE_GROUP_ENABLED), SID_AND_ATTRIBUTES(_sid(CAP_PRIVATE_NETWORK).value, SE_GROUP_ENABLED))
            sc = SECURITY_CAPABILITIES(sid.value, ctypes.cast(caps, ctypes.c_void_p).value if policy.network else None, 2 if policy.network else 0, 0)
            size = ctypes.c_size_t()
            k32.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(size))
            al = ctypes.create_string_buffer(size.value)
            _ok(k32.InitializeProcThreadAttributeList(al, 1, 0, ctypes.byref(size)), "InitializeProcThreadAttributeList")
            _ok(k32.UpdateProcThreadAttribute(al, 0, PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES, ctypes.byref(sc), ctypes.sizeof(sc), None, None), "UpdateProcThreadAttribute")
            si.lpAttributeList = ctypes.cast(al, ctypes.c_void_p).value
            keep += [caps, sc, al]
            grants = icacls_plan(policy, "appcontainer", sid_s)
        else:
            grants = icacls_plan(policy, "restricted")
        for g in grants:
            subprocess.run(g, capture_output=True, creationflags=CREATE_NO_WINDOW)
        job = job_object(policy)
        block = _env_block(env)
        if mode == "appcontainer":
            _ok(k32.CreateProcessW(None, cmdline, None, None, True, flags | EXTENDED_STARTUPINFO_PRESENT, block, W.LPCWSTR(cwd), ctypes.byref(si), ctypes.byref(pi)), "CreateProcess(AppContainer)")
        else:
            tok = restricted_token()
            _ok(adv.CreateProcessAsUserW(tok, None, cmdline, None, None, True, flags, block, W.LPCWSTR(cwd), ctypes.byref(si.StartupInfo), ctypes.byref(pi)), "CreateProcessAsUser")
            k32.CloseHandle(tok)
        try:
            _ok(k32.AssignProcessToJobObject(W.HANDLE(job), pi.hProcess), "AssignProcessToJobObject")
        except OSError:
            k32.TerminateProcess(pi.hProcess, 1)
            raise
        k32.ResumeThread(pi.hThread)
        k32.CloseHandle(pi.hThread)
        return pi.hProcess, job, {"mode": mode, "appcontainer_sid": sid_s, "grants": grants}

    def run(policy, argv, cwd=None, timeout=None, capture=True, profile="default"):
        cwd = cwd or policy.workspace
        pipes = []
        if capture:
            r_out, w_out = os.pipe()
            r_err, w_err = os.pipe()
            hin = msvcrt.get_osfhandle(os.open("NUL", os.O_RDONLY))
            for fd in (w_out, w_err):
                os.set_inheritable(fd, True)
            os.set_handle_inheritable(hin, True)
            stdio = (hin, msvcrt.get_osfhandle(w_out), msvcrt.get_osfhandle(w_err))
            pipes = [(r_out, w_out), (r_err, w_err)]
        else:
            stdio = tuple(msvcrt.get_osfhandle(f.fileno()) for f in (sys.stdin, sys.stdout, sys.stderr))
            for h in stdio:
                try:
                    os.set_handle_inheritable(h, True)
                except OSError:
                    pass
        hproc, job, _info = _spawn(policy, argv, cwd, stdio, profile)
        bufs = [b"", b""]
        threads = []
        for i, (r, w) in enumerate(pipes):
            os.close(w)

            def pump(i=i, r=r):
                with os.fdopen(r, "rb") as f:
                    bufs[i] = f.read()
            t = threading.Thread(target=pump, daemon=True)
            t.start()
            threads.append(t)
        ms = INFINITE if timeout is None else int(timeout * 1000)
        if k32.WaitForSingleObject(W.HANDLE(hproc), ms) == WAIT_TIMEOUT:
            k32.TerminateJobObject(W.HANDLE(job), 1)
            raise subprocess.TimeoutExpired(argv, timeout)
        code = W.DWORD()
        k32.GetExitCodeProcess(W.HANDLE(hproc), ctypes.byref(code))
        for t in threads:
            t.join(5)
        k32.CloseHandle(W.HANDLE(hproc))
        k32.CloseHandle(W.HANDLE(job))
        return subprocess.CompletedProcess(argv, code.value, bufs[0] if capture else None, bufs[1] if capture else None)
else:
    def run(policy, argv, cwd=None, timeout=None, capture=True, profile="default"):
        raise OSError(95, tr("sandbox.windows.the_windows_light_sandbox_only_runs"))
