' System Monitor Universal Launcher
' Automatically detects compiled executable OR Python installation.
' Double-click to launch with admin rights. No console window.

Dim shell, fso, py, script, dir, exePath

Set shell = CreateObject("WScript.Shell")
Set fso   = CreateObject("Scripting.FileSystemObject")

' ── Resolve the folder this VBS lives in ──────────────────────────────────────
dir = fso.GetParentFolderName(WScript.ScriptFullName)

' ── 0. Check for Standalone Executable (System Monitor.exe) ──────────────────
exePath = ""
If fso.FileExists(dir & "\System Monitor.exe") Then
    exePath = dir & "\System Monitor.exe"
ElseIf fso.FileExists(dir & "\dist\System Monitor\System Monitor.exe") Then
    exePath = dir & "\dist\System Monitor\System Monitor.exe"
ElseIf fso.FileExists(dir & "\dist\System Monitor.exe") Then
    exePath = dir & "\dist\System Monitor.exe"
End If

If exePath <> "" Then
    CreateObject("Shell.Application").ShellExecute Chr(34) & exePath & Chr(34), "", dir, "runas", 1
    WScript.Quit 0
End If

' ── 1. Fallback to Python Script Launch ───────────────────────────────────────
script = Chr(34) & dir & "\status_monitor.py" & Chr(34)
py = ""

' Strategy A: Check py.exe (Python Launcher)
On Error Resume Next
Dim execObj
Set execObj = shell.Exec("where.exe py.exe")
If Err.Number = 0 Then
    Dim whereOut
    whereOut = Trim(execObj.StdOut.ReadLine())
    If fso.FileExists(whereOut) Then py = "py.exe"
End If
On Error GoTo 0

' Strategy B: Check pythonw.exe on PATH
If py = "" Then
    On Error Resume Next
    Set execObj = shell.Exec("where.exe pythonw.exe")
    If Err.Number = 0 Then
        Dim whereOut2
        whereOut2 = Trim(execObj.StdOut.ReadLine())
        If fso.FileExists(whereOut2) Then py = whereOut2
    End If
    On Error GoTo 0
End If

' Strategy C: Check python.exe on PATH
If py = "" Then
    On Error Resume Next
    Set execObj = shell.Exec("where.exe python.exe")
    If Err.Number = 0 Then
        Do While Not execObj.StdOut.AtEndOfStream
            Dim candidate
            candidate = Trim(execObj.StdOut.ReadLine())
            If fso.FileExists(candidate) And InStr(LCase(candidate), "windowsapps") = 0 Then
                py = candidate
                Exit Do
            End If
        Loop
    End If
    On Error GoTo 0
End If

' Strategy D: Check codex-runtimes & standard install locations
If py = "" Then
    Dim userProfile, paths, i
    userProfile = shell.ExpandEnvironmentStrings("%USERPROFILE%")
    paths = Array( _
        userProfile & "\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe", _
        userProfile & "\AppData\Local\Programs\Python\Python314\pythonw.exe", _
        userProfile & "\AppData\Local\Programs\Python\Python312\pythonw.exe", _
        userProfile & "\AppData\Local\Programs\Python\Python313\pythonw.exe", _
        userProfile & "\AppData\Local\Programs\Python\Python311\pythonw.exe", _
        "C:\Python314\pythonw.exe", _
        "C:\Python312\pythonw.exe", _
        "C:\Python313\pythonw.exe", _
        "C:\Program Files\Python314\pythonw.exe", _
        "C:\Program Files\Python312\pythonw.exe" _
    )
    For i = 0 To UBound(paths)
        If fso.FileExists(paths(i)) Then
            py = paths(i)
            Exit For
        End If
    Next
End If

If py = "" Then
    MsgBox "Could not find Python or System Monitor executable!" & vbCrLf & vbCrLf & _
           "Please install Python from python.org or build the executable via setup.bat.", _
           vbCritical, "System Monitor"
    WScript.Quit 1
End If

CreateObject("Shell.Application").ShellExecute py, script, dir, "runas", 1
