"""
Build script - Đóng gói DeepSeek Proxy GUI thành file .exe
"""

import subprocess
import sys
import os
import shutil


def check_pyinstaller():
    """Kiểm tra PyInstaller đã cài chưa"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Cài PyInstaller"""
    print("📦 Đang cài PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✅ Đã cài PyInstaller")


def clean_build():
    """Xóa build cũ"""
    dirs_to_remove = ['build'] # Không xóa dist để giữ các build khác
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"🗑️ Đang xóa {dir_name}/...")
            try:
                shutil.rmtree(dir_name)
            except Exception as e:
                print(f"⚠️ Không thể xóa {dir_name}: {e}")
    
    # Xóa file .spec cũ
    for f in os.listdir('.'):
        if f.endswith('.spec') and f != 'deepseek-proxy.spec':
            os.remove(f)
            print(f"🗑️ Đã xóa {f}")


def build_exe(one_file=True, windowed=True, version="v1.0.0"):
    """Build file .exe"""
    
    app_name = f"DeepSeek-Proxy-{version}"
    cmd = [
        sys.executable, "-m", "PyInstaller",
        f"--name={app_name}",
        "--clean",
    ]
    
    if one_file:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")
    
    if windowed:
        cmd.append("--noconsole")  # Không hiện console khi chạy GUI
    
    # Hidden imports (các module cần include)
    hidden_imports = [
        "requests",
        "Crypto",
        "Crypto.Cipher",
        "Crypto.Cipher.AES",
        "flask",
        "flask_cors",
        "werkzeug",
        "jinja2",
        "markupsafe",
        "itsdangerous",
        "click",
    ]
    
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    
    # Thêm data files nếu có
    # cmd.extend(["--add-data", "templates;templates"])
    
    # File chính
    cmd.append("proxy_gui.py")
    
    print("🔨 Đang build .exe...")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        subprocess.check_call(cmd)
        print()
        print("=" * 50)
        print("✅ BUILD THÀNH CÔNG!")
        print("=" * 50)
        print()
        print(f"📁 File .exe nằm tại: dist/{app_name}.exe")
        print()
        print("💡 Lưu ý:")
        print("   - File .exe có thể chạy độc lập (không cần cài Python)")
        print("   - Copy file .exe sang máy khác là chạy được")
        print("   - Cloudflared vẫn cần cài riêng nếu muốn dùng tunnel")
        print()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build thất bại: {e}")
        return False
    
    return True


def main():
    print("🚀 DeepSeek Proxy GUI - Build Script")
    print("=" * 50)
    print()
    
    # Kiểm tra PyInstaller
    if not check_pyinstaller():
        install_pyinstaller()
    else:
        print("✅ PyInstaller đã được cài đặt")
    
    print()
    
    # Hỏi ngườii dùng
    print("Chọn kiểu build:")
    print("  1. One file (1 file .exe duy nhất) - Khuyến nghị")
    print("  2. One folder (nhiều file trong thư mục)")
    
    choice = input("\nLựa chọn (1/2): ").strip() or "1"
    
    one_file = (choice == "1")
    
    # Hỏi phiên bản
    version = input("\nNhập phiên bản (mặc định v1.0.0): ").strip() or "v1.0.0"
    if not version.startswith('v'):
        version = 'v' + version
    
    print()
    print("🧹 Đang dọn dẹp build cũ...")
    clean_build()
    
    print()
    build_exe(one_file=one_file, windowed=True, version=version)


if __name__ == "__main__":
    main()
