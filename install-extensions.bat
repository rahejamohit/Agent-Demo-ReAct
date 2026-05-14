@echo off
REM VS Code Python Development Extensions Installer (Windows)

echo.
echo 🚀 Installing VS Code Python Extensions
echo ==========================================
echo.

REM Check if code command is available
where code >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ VS Code 'code' command not found
    echo.
    echo    Please ensure VS Code is installed and in your PATH
    echo.
    echo    To add VS Code to PATH:
    echo    1. Open VS Code
    echo    2. Press Ctrl+Shift+P
    echo    3. Type 'Shell Command: Install code command in PATH'
    echo.
    pause
    exit /b 1
)

echo ✅ VS Code found
echo.
echo 📦 Installing ESSENTIAL extensions...
echo.

REM Install extensions
call :install_extension "ms-python.python"
call :install_extension "ms-python.vscode-pylance"
call :install_extension "ms-python.debugpy"
call :install_extension "ms-python.pylint"
call :install_extension "ms-python.black-formatter"
call :install_extension "humao.rest-client"
call :install_extension "usernamehw.errorlens"
call :install_extension "aaron-bond.better-comments"
call :install_extension "shardulm94.trailing-spaces"
call :install_extension "ms-json.json-language-features"
call :install_extension "DRMWNM.fastapi-snippets"

echo.
echo ==========================================
echo ✅ Extension installation complete!
echo.
echo 🔄 Next steps:
echo    1. Reload VS Code (Ctrl+R)
echo    2. Select your Python interpreter:
echo       - Press Ctrl+Shift+P
echo       - Type 'Python: Select Interpreter'
echo       - Choose the venv in your project folder
echo.
echo 📚 Verify setup:
echo    - Create a test Python file
echo    - You should see syntax highlighting
echo.
pause
exit /b 0

:install_extension
echo ⏳ Installing: %~1
code --install-extension %~1 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    ✅ Installed
) else (
    echo    ⚠️  Check connection
)
goto :eof
