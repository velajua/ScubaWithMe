@echo off
setlocal EnableExtensions

rem Batch-upscale chaiNNer print-test exports with Real-ESRGAN.
rem Usage:
rem   run-esrgan-print-tests.cmd
rem   run-esrgan-print-tests.cmd 3
rem Optional environment overrides:
rem   set ESRGAN_MODEL=realesrnet-x4plus
rem   set ESRGAN_OVERWRITE=1

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

set "PYTHON_CMD=python"
if not "%ESRGAN_PYTHON%"=="" set "PYTHON_CMD=%ESRGAN_PYTHON%"

"%PYTHON_CMD%" "%PROJECT_ROOT%esrgan-print-test-helper.py" %*
