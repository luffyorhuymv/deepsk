import os
import sys
import winreg

class StartupManager:
    @staticmethod
    def is_startup_enabled(app_name: str) -> bool:
        """Kiểm tra xem ứng dụng có được thiết lập khởi động cùng Windows không."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            try:
                winreg.QueryValueEx(key, app_name)
                return True
            except FileNotFoundError:
                return False
            finally:
                winreg.CloseKey(key)
        except Exception:
            return False

    @staticmethod
    def enable_startup(app_name: str, app_path: str = None) -> bool:
        """Bật tính năng khởi động cùng Windows."""
        if app_path is None:
            # Nếu chạy bằng .exe build từ PyInstaller, sys.executable là đường dẫn file .exe
            # Nếu chạy bằng python, sys.executable là python.exe và sys.argv[0] là script path
            if getattr(sys, 'frozen', False):
                app_path = sys.executable
            else:
                app_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Lỗi khi bật khởi động cùng Win: {e}")
            return False

    @staticmethod
    def disable_startup(app_name: str) -> bool:
        """Tắt tính năng khởi động cùng Windows."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Lỗi khi tắt khởi động cùng Win: {e}")
            return False
