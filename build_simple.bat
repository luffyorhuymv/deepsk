@echo off
chcp 65001 >nul
echo 🚀 Build DeepSeek Proxy GUI - Single File .exe
echo ================================================
echo.

:: Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python chưa được cài đặt hoặc không có trong PATH
    pause
    exit /b 1
)

:: Cài PyInstaller nếu chưa có
echo 📦 Kiểm tra PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 📦 Đang cài PyInstaller...
    pip install pyinstaller
)

:: Dọn dẹp
echo 🧹 Dọn dẹp build cũ...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Build
echo 🔨 Đang build .exe...
python -m PyInstaller ^
    --name="DeepSeek-Proxy" ^
    --onefile ^
    --noconsole ^
    --clean ^
    --hidden-import=requests ^
    --hidden-import=Crypto ^
    --hidden-import=Crypto.Cipher ^
    --hidden-import=Crypto.Cipher.AES ^
    --hidden-import=flask ^
    --hidden-import=flask_cors ^
    --hidden-import=werkzeug ^
    --hidden-import=jinja2 ^
    --hidden-import=markupsafe ^
    --hidden-import=itsdangerous ^
    --hidden-import=click ^
    proxy_gui.py

if errorlevel 1 (
    echo.
    echo ❌ Build thất bại!
    pause
    exit /b 1
)

echo.
echo ================================================
echo ✅ BUILD THÀNH CÔNG!
echo ================================================
echo.
echo 📁 File .exe: dist\DeepSeek-Proxy.exe
echo.
echo 💡 Lưu ý:
echo    - File .exe có thể chạy độc lập
echo    - Cloudflared vẫn cần cài riêng nếu muốn dùng tunnel
echo.
pause
