@echo off
echo ======================================
echo   Instalador de dependencias Python
echo ======================================
echo.

python -m pip --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python o pip no están instalados.
    echo Instala Python desde https://www.python.org/
    pause
    exit /b
)

echo Instalando librerías necesarias...
echo.

pip install pdfplumber
pip install python-docx
pip install langdetect

echo.
echo ======================================
echo   Instalación completada correctamente
echo ======================================
pause
