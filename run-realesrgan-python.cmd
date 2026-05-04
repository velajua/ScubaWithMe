@echo off
setlocal EnableExtensions

rem Run the PyTorch Real-ESRGAN implementation from the local venv.
rem Usage:
rem   run-realesrgan-python.cmd
rem   run-realesrgan-python.cmd working\current-png\squid1.png
rem Optional environment overrides:
rem   set PY_ESRGAN_MODEL=RealESRNet_x4plus
rem   set PY_ESRGAN_SCALE=2
rem   set PY_ESRGAN_TILE=128
rem   set PY_ESRGAN_SUFFIX=pytorch-x4plus-2x

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

set "PYTHON_EXE=%PROJECT_ROOT%.realesrgan-runtime\venv\Scripts\python.exe"
if not "%PY_ESRGAN_PYTHON_EXE%"=="" set "PYTHON_EXE=%PY_ESRGAN_PYTHON_EXE%"

set "INFERENCE=%PROJECT_ROOT%Real-ESRGAN\inference_realesrgan.py"
if not "%PY_ESRGAN_INFERENCE%"=="" set "INFERENCE=%PY_ESRGAN_INFERENCE%"

set "MODEL_NAME=RealESRGAN_x4plus"
if not "%PY_ESRGAN_MODEL%"=="" set "MODEL_NAME=%PY_ESRGAN_MODEL%"

set "MODEL_PATH=%PROJECT_ROOT%Real-ESRGAN\weights\%MODEL_NAME%.pth"
if not "%PY_ESRGAN_MODEL_PATH%"=="" set "MODEL_PATH=%PY_ESRGAN_MODEL_PATH%"

set "INPUT=working\current-png"
if not "%~1"=="" set "INPUT=%~1"

set "OUTPUT=exports\print-tests\ESRGAN-pytorch"
if not "%PY_ESRGAN_OUTPUT%"=="" set "OUTPUT=%PY_ESRGAN_OUTPUT%"

set "SCALE=2"
if not "%PY_ESRGAN_SCALE%"=="" set "SCALE=%PY_ESRGAN_SCALE%"

set "TILE=128"
if not "%PY_ESRGAN_TILE%"=="" set "TILE=%PY_ESRGAN_TILE%"

set "SUFFIX=pytorch-%MODEL_NAME%-%SCALE%x"
if not "%PY_ESRGAN_SUFFIX%"=="" set "SUFFIX=%PY_ESRGAN_SUFFIX%"

for %%I in ("%INPUT%") do set "INPUT_STEM=%%~nI"
if "%INPUT_STEM%"=="" set "INPUT_STEM=batch"
set "INPUT_STEM=%INPUT_STEM: =-%"

set "LOG_DIR=%PROJECT_ROOT%.realesrgan-runtime\logs"
if not "%PY_ESRGAN_LOG_DIR%"=="" set "LOG_DIR=%PY_ESRGAN_LOG_DIR%"

set "LOG_PATH=%LOG_DIR%\%INPUT_STEM%.log"
if not "%PY_ESRGAN_LOG_PATH%"=="" set "LOG_PATH=%PY_ESRGAN_LOG_PATH%"

if not exist "%PYTHON_EXE%" (
  echo Missing Python Real-ESRGAN venv: "%PYTHON_EXE%"
  echo Create it with the setup steps in notes\esrgan-print-test-workflow.md.
  exit /b 1
)

if not exist "%INFERENCE%" (
  echo Missing inference script: "%INFERENCE%"
  exit /b 1
)

if not exist "%MODEL_PATH%" (
  echo Missing model weights: "%MODEL_PATH%"
  echo Download the matching .pth into Real-ESRGAN\weights or set PY_ESRGAN_MODEL_PATH.
  exit /b 1
)

if not exist "%OUTPUT%" mkdir "%OUTPUT%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo Running Python Real-ESRGAN for "%INPUT%"
echo Writing log to "%LOG_PATH%"

cmd /c ""%PYTHON_EXE%" "%INFERENCE%" -n "%MODEL_NAME%" -i "%INPUT%" -o "%OUTPUT%" --model_path "%MODEL_PATH%" --outscale "%SCALE%" --suffix "%SUFFIX%" --tile "%TILE%" --fp32 > "%LOG_PATH%" 2>&1"

set "CODE=%ERRORLEVEL%"
if not "%CODE%"=="0" (
  echo Python Real-ESRGAN failed. See "%LOG_PATH%"
  exit /b %CODE%
)

echo Python Real-ESRGAN complete. Outputs: "%OUTPUT%"
echo Log: "%LOG_PATH%"
exit /b 0
