// Small Windows launch/exit boundary for reader-run.ps1. No privilege changes.
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Security.Principal;
using System.Text;

public static class ReaderNative {
    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)] struct STARTUPINFO {
        public uint cb; public string reserved, desktop, title;
        public uint x,y,xSize,ySize,xChars,yChars,fill,flags;
        public ushort show, reserved2; public IntPtr reservedPtr, stdin, stdout, stderr;
    }
    [StructLayout(LayoutKind.Sequential)] public struct Child {
        public IntPtr process, thread; public uint pid, tid;
    }
    [StructLayout(LayoutKind.Sequential)] struct BasicLimits {
        public long processTime, jobTime; public uint flags;
        public UIntPtr minWorking, maxWorking; public uint activeLimit;
        public UIntPtr affinity; public uint priority, scheduling;
    }
    [StructLayout(LayoutKind.Sequential)] struct IOCount { public ulong a,b,c,d,e,f; }
    [StructLayout(LayoutKind.Sequential)] struct ExtendedLimits {
        public BasicLimits basic; public IOCount io;
        public UIntPtr processMemory,jobMemory,peakProcessMemory,peakJobMemory;
    }
    [StructLayout(LayoutKind.Sequential)] public struct Accounting {
        public long userTime,kernelTime,periodUser,periodKernel;
        public uint pageFaults,totalProcesses,activeProcesses,terminatedProcesses;
    }
    [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern bool CreateProcessW(string app,StringBuilder command,IntPtr pa,IntPtr ta,bool inherit,uint flags,IntPtr env,string cwd,ref STARTUPINFO startup,out Child child);
    [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern bool QueryFullProcessImageNameW(IntPtr p,uint flags,StringBuilder text,ref uint length);
    [DllImport("kernel32.dll",SetLastError=true)] static extern bool GetProcessTimes(IntPtr p,out long creation,out long exit,out long kernel,out long user);
    [DllImport("kernel32.dll",SetLastError=true)] public static extern IntPtr OpenProcess(uint access,bool inherit,uint pid);
    [DllImport("kernel32.dll",SetLastError=true)] static extern uint WaitForSingleObject(IntPtr h,uint ms);
    [DllImport("kernel32.dll",SetLastError=true)] static extern bool GetExitCodeProcess(IntPtr p,out uint code);
    [DllImport("kernel32.dll",SetLastError=true)] static extern uint ResumeThread(IntPtr t);
    [DllImport("kernel32.dll",SetLastError=true)] static extern bool TerminateProcess(IntPtr p,uint code);
    [DllImport("kernel32.dll",SetLastError=true)] public static extern bool CloseHandle(IntPtr h);
    [DllImport("kernel32.dll")] static extern IntPtr GetCurrentProcess();
    [DllImport("kernel32.dll")] static extern IntPtr GetCurrentThread();
    [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr CreateJobObjectW(IntPtr attr,string name);
    [DllImport("kernel32.dll",SetLastError=true)] static extern bool SetInformationJobObject(IntPtr job,int kind,ref ExtendedLimits info,uint size);
    [DllImport("kernel32.dll",SetLastError=true)] static extern bool AssignProcessToJobObject(IntPtr job,IntPtr process);
    [DllImport("kernel32.dll",SetLastError=true)] static extern bool IsProcessInJob(IntPtr p,IntPtr job,out bool member);
    [DllImport("kernel32.dll",SetLastError=true)] static extern bool QueryInformationJobObject(IntPtr job,int kind,out Accounting info,uint size,IntPtr length);
    [DllImport("kernel32.dll",SetLastError=true,EntryPoint="QueryInformationJobObject")] static extern bool QueryJobBuffer(IntPtr job,int kind,IntPtr info,uint size,IntPtr length);
    [DllImport("ntdll.dll")] static extern int NtQueryInformationProcess(IntPtr p,int kind,IntPtr data,int size,out int returned);
    [DllImport("kernel32.dll",SetLastError=true)] static extern bool TerminateJobObject(IntPtr job,uint code);
    [DllImport("advapi32.dll",SetLastError=true)] static extern bool OpenProcessToken(IntPtr p,uint access,out IntPtr token);
    [DllImport("advapi32.dll",SetLastError=true)] static extern bool OpenThreadToken(IntPtr t,uint access,bool asSelf,out IntPtr token);
    [DllImport("advapi32.dll",SetLastError=true)] static extern bool GetTokenInformation(IntPtr token,int kind,IntPtr data,uint size,out uint returned);

    static Exception Error(string api) { return new Win32Exception(Marshal.GetLastWin32Error(),api); }
    static int Dword(IntPtr token,int kind) {
        IntPtr data=Marshal.AllocHGlobal(4);
        try { uint returned; if(!GetTokenInformation(token,kind,data,4,out returned)) throw Error("GetTokenInformation("+kind+")");
            if(returned!=4) throw new InvalidOperationException("Unexpected DWORD token size"); return Marshal.ReadInt32(data);
        } finally { Marshal.FreeHGlobal(data); }
    }
    static IntPtr TokenBuffer(IntPtr token,int kind) {
        uint length; bool ok=GetTokenInformation(token,kind,IntPtr.Zero,0,out length); int err=Marshal.GetLastWin32Error();
        if(ok || err!=122 || length==0 || length>65536) throw new Win32Exception(err,"GetTokenInformation length");
        IntPtr data=Marshal.AllocHGlobal((int)length);
        if(!GetTokenInformation(token,kind,data,length,out length)) { int e=Marshal.GetLastWin32Error(); Marshal.FreeHGlobal(data); throw new Win32Exception(e,"GetTokenInformation value"); }
        return data;
    }
    public static Dictionary<string,object> Boundary(IntPtr process,bool currentThread) {
        IntPtr token; if(!OpenProcessToken(process,8,out token)) throw Error("OpenProcessToken");
        var result=new Dictionary<string,object>();
        try {
            result["elevated"]=Dword(token,20)!=0; result["appcontainer"]=Dword(token,29)!=0;
            IntPtr user=TokenBuffer(token,1);
            try { result["user_sid"]=new SecurityIdentifier(Marshal.ReadIntPtr(user)).Value; } finally { Marshal.FreeHGlobal(user); }
            IntPtr groups=TokenBuffer(token,2); bool admin=false;
            try {
                int count=Marshal.ReadInt32(groups), offset=IntPtr.Size==8?8:4, stride=IntPtr.Size==8?16:8;
                for(int i=0;i<count;i++) {
                    IntPtr row=IntPtr.Add(groups,offset+i*stride);
                    string sid=new SecurityIdentifier(Marshal.ReadIntPtr(row)).Value;
                    int attr=Marshal.ReadInt32(row,IntPtr.Size);
                    if(sid=="S-1-5-32-544" && (attr&4)!=0 && (attr&16)==0) admin=true;
                }
            } finally { Marshal.FreeHGlobal(groups); }
            result["effective_administrator"]=admin;
        } finally { if(!CloseHandle(token)) throw Error("CloseHandle token"); }
        if(currentThread) {
            IntPtr threadToken; bool opened=OpenThreadToken(GetCurrentThread(),8,true,out threadToken); int err=Marshal.GetLastWin32Error();
            if(opened) { CloseHandle(threadToken); throw new InvalidOperationException("Impersonated launching thread is outside this boundary"); }
            if(err!=1008) throw new Win32Exception(err,"OpenThreadToken"); result["thread_token_absent"]=true;
        }
        result["permitted"]=!(bool)result["elevated"] && !(bool)result["appcontainer"] && !(bool)result["effective_administrator"];
        return result;
    }
    public static Dictionary<string,object> CurrentBoundary() { return Boundary(GetCurrentProcess(),true); }
    public static IntPtr Job() {
        IntPtr job=CreateJobObjectW(IntPtr.Zero,null); if(job==IntPtr.Zero) throw Error("CreateJobObject");
        var limits=new ExtendedLimits(); limits.basic.flags=0x2000; // KILL_ON_JOB_CLOSE; no breakaway.
        if(!SetInformationJobObject(job,9,ref limits,(uint)Marshal.SizeOf(limits))) {
            int err=Marshal.GetLastWin32Error(); CloseHandle(job); throw new Win32Exception(err,"SetInformationJobObject");
        }
        return job;
    }
    public static Child Create(string exe,string command,string cwd,string environment) {
        var startup=new STARTUPINFO(); startup.cb=(uint)Marshal.SizeOf(startup);
        IntPtr env=Marshal.StringToHGlobalUni(environment);
        try {
            Child child;
            if(!CreateProcessW(exe,new StringBuilder(command),IntPtr.Zero,IntPtr.Zero,false,0x08000404,env,cwd,ref startup,out child)) {
                Exception failure=Error("CreateProcessW"); failure.Data["creation_outcome"]="confirmed_not_created"; throw failure;
            }
            return child; // suspended; caller owns both handles even if later verification fails.
        } finally { Marshal.FreeHGlobal(env); }
    }
    public static void Assign(IntPtr job,IntPtr process) { if(!AssignProcessToJobObject(job,process)) throw Error("AssignProcessToJobObject"); }
    public static bool Member(IntPtr job,IntPtr process) { bool member; if(!IsProcessInJob(process,job,out member)) throw Error("IsProcessInJob"); return member; }
    public static Dictionary<string,object> Identity(IntPtr process) {
        uint size=32768; var path=new StringBuilder((int)size);
        if(!QueryFullProcessImageNameW(process,0,path,ref size)) throw Error("QueryFullProcessImageNameW");
        long created,exit,kernel,user; if(!GetProcessTimes(process,out created,out exit,out kernel,out user)) throw Error("GetProcessTimes");
        return new Dictionary<string,object>{{"actual_image",path.ToString()},{"creation_ticks",created},{"exit_ticks",exit},{"kernel_ticks",kernel},{"user_ticks",user}};
    }
    public static Dictionary<string,object> FinalTimes(IntPtr process) {
        long created,exit,kernel,user; if(!GetProcessTimes(process,out created,out exit,out kernel,out user)) throw Error("GetProcessTimes final");
        return new Dictionary<string,object>{{"creation_ticks",created},{"exit_ticks",exit},{"kernel_ticks",kernel},{"user_ticks",user}};
    }
    public static void Resume(IntPtr thread) {
        uint before=ResumeThread(thread); if(before==0xffffffff) throw Error("ResumeThread");
        if(before!=1) throw new InvalidOperationException("Unexpected primary-thread suspension count");
    }
    public static bool Exited(IntPtr process) { uint r=WaitForSingleObject(process,0); if(r==0)return true; if(r==258)return false; throw Error("WaitForSingleObject"); }
    public static uint ExitCode(IntPtr process) { uint code; if(!GetExitCodeProcess(process,out code))throw Error("GetExitCodeProcess"); return code; }
    public static Accounting Account(IntPtr job) { Accounting info; if(!QueryInformationJobObject(job,1,out info,(uint)Marshal.SizeOf(typeof(Accounting)),IntPtr.Zero))throw Error("QueryInformationJobObject"); return info; }
    public static uint[] ProcessIds(IntPtr job) {
        int size=8+8*IntPtr.Size; IntPtr data=Marshal.AllocHGlobal(size);
        try {
            if(!QueryJobBuffer(job,3,data,(uint)size,IntPtr.Zero))throw Error("QueryInformationJobObject process list");
            int assigned=Marshal.ReadInt32(data), count=Marshal.ReadInt32(data,4);
            if(count<1 || count>8 || assigned!=count)throw new InvalidOperationException("Incomplete/beyond-limit job PID list");
            var ids=new uint[count]; for(int i=0;i<count;i++)ids[i]=(uint)Marshal.ReadIntPtr(data,8+i*IntPtr.Size).ToInt64();
            return ids;
        } finally { Marshal.FreeHGlobal(data); }
    }
    public static string CommandLine(IntPtr process) {
        int needed; int status=NtQueryInformationProcess(process,60,IntPtr.Zero,0,out needed);
        if(needed<8 || needed>65536)throw new InvalidOperationException("Command-line size query failed, NTSTATUS="+status.ToString("X8"));
        IntPtr data=Marshal.AllocHGlobal(needed);
        try {
            status=NtQueryInformationProcess(process,60,data,needed,out needed);
            if(status!=0)throw new InvalidOperationException("Command-line query failed, NTSTATUS="+status.ToString("X8"));
            int length=(ushort)Marshal.ReadInt16(data); IntPtr text=Marshal.ReadIntPtr(data,IntPtr.Size==8?8:4);
            return Marshal.PtrToStringUni(text,length/2);
        } finally { Marshal.FreeHGlobal(data); }
    }
    public static int StopJob(IntPtr job,uint code) { if(TerminateJobObject(job,code))return 0; return Marshal.GetLastWin32Error(); }
    public static int StopProcess(IntPtr process,uint code) { if(TerminateProcess(process,code))return 0; return Marshal.GetLastWin32Error(); }
}
