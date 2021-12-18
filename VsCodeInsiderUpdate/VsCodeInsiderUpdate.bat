@REM
@REM This script is used to udpate vscode-insider portable:
@REM   - move new vscode zip file from A to B,
@REM   - backup original vscode folder,
@REM   - unzip new vscode to replace the original one.
@REM
#REM NOTE:
@REM   - Ensure the zip file name is updated in script %ZIPFILENAME%
@REM     E.g. VSCode-win32-x64-1.32.0-insider.zip
@REM   - The donwload vscode zip file should be placed in %ZIPFILEFOLDER%.
@REM

@echo off

@set ZIPFILENAME=VSCode-win32-x64-1.63.0-insider.zip
@set ZIPFILEFOLDER=C:\Remote\WorkSpace\
@set TASKLISTLOG=__tasklist.log
@set EXENAME="Code - Insiders.exe"

if exist %ZIPFILEFOLDER%%ZIPFILENAME% (
  echo %ZIPFILEFOLDER%%ZIPFILENAME% is present.
  move %ZIPFILEFOLDER%%ZIPFILENAME% .
) else (
  echo %ZIPFILEFOLDER%%ZIPFILENAME% is not present.
)

if not exist .\%ZIPFILENAME% (
  echo %ZIPFILENAME% is not present.
  PAUSE
  goto END
)

tasklist /NH /FO CSV > %TASKLISTLOG%
FindStr /L /C:%EXENAME% %TASKLISTLOG% > NUL
@if %errorlevel% == 0 (
  echo [101;93m VSCode is running... [0m
  PAUSE
  goto END
)

if exist .\VSCode-insider_bak (
  rmdir /S /Q .\VSCode-insider_bak
)

if exist .\VSCode-insider (
  ren VSCode-insider VSCode-insider_bak
)

"C:\Program Files\7-Zip\7z.exe" x .\%ZIPFILENAME% -o.\VSCode-insider
@if %errorlevel% == 0 (
  del /Q .\%ZIPFILENAME%
)

:END

if exist %TASKLISTLOG% (
  del /Q %TASKLISTLOG%
)
