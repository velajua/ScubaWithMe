@echo off
setlocal

set "ROOT=%~dp0"
if not defined CHAINNER_EXE set "CHAINNER_EXE=%LOCALAPPDATA%\chaiNNer\chaiNNer.exe"
set "LOGDIR=%ROOT%notes"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"
if not exist "%CHAINNER_EXE%" (
  echo Could not find chaiNNer. Set CHAINNER_EXE to the full chaiNNer executable path.
  exit /b 1
)

start /wait "" "%CHAINNER_EXE%" run "%ROOT%workflows\scubawithme-template-01-natural-print-prep.chn" > "%LOGDIR%\scubawithme-template-01-natural-print-prep.log" 2>&1
ping -n 21 127.0.0.1 > nul
start /wait "" "%CHAINNER_EXE%" run "%ROOT%workflows\scubawithme-template-02-clean-product-prep.chn" > "%LOGDIR%\scubawithme-template-02-clean-product-prep.log" 2>&1
ping -n 21 127.0.0.1 > nul
start /wait "" "%CHAINNER_EXE%" run "%ROOT%workflows\scubawithme-template-03-vivid-reef-grade.chn" > "%LOGDIR%\scubawithme-template-03-vivid-reef-grade.log" 2>&1
ping -n 21 127.0.0.1 > nul

echo Done. Review outputs in "%ROOT%exports\print-tests\chainner_output".
