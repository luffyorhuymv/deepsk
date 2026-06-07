"""
Tunnel Manager - Quản lý các dịch vụ tunnel
Hỗ trợ: Cloudflare Tunnel, ngrok, localtunnel
"""

import subprocess
import threading
import time
import re
import requests
import os
import sys
from typing import Optional, Callable


class BaseTunnel:
    """Base class cho tunnel"""
    
    def __init__(self, local_port: int = 5000):
        self.local_port = local_port
        self.public_url: Optional[str] = None
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._on_url: Optional[Callable[[str], None]] = None
        self._on_log: Optional[Callable[[str], None]] = None
    
    def on_url(self, callback: Callable[[str], None]):
        """Callback khi có URL public"""
        self._on_url = callback
        return self

    def on_log(self, callback: Callable[[str], None]):
        """Callback khi có log mới"""
        self._on_log = callback
        return self
    
    def _log(self, message: str):
        """Ghi log và gọi callback"""
        if self._on_log:
            self._on_log(message)
        print(message)
    
    def start(self) -> bool:
        """Khởi động tunnel - override ở subclass"""
        raise NotImplementedError
    
    def stop(self):
        """Dừng tunnel"""
        self.is_running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.process = None
        self.public_url = None
    
    def get_status(self) -> dict:
        """Trả về trạng thái"""
        return {
            "running": self.is_running,
            "url": self.public_url,
            "type": self.__class__.__name__
        }


class CloudflareTunnel(BaseTunnel):
    """Cloudflare Tunnel (cloudflared)"""
    
    def start(self) -> bool:
        """Khởi động Cloudflare tunnel"""
        try:
            # Kiểm tra cloudflared đã cài chưa
            result = subprocess.run(
                ['cloudflared', '--version'], 
                capture_output=True, 
                text=True
            )
            if result.returncode != 0:
                self._log("❌ cloudflared chưa được cài đặt")
                return False
        except FileNotFoundError:
            self._log("❌ cloudflared không tìm thấy. Cài đặt:")
            self._log("   Windows: winget install Cloudflare.cloudflared")
            self._log("   hoặc download từ https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
            return False
        
        def run_tunnel():
            self.is_running = True
            cmd = [
                'cloudflared', 'tunnel', '--url',
                f'http://localhost:{self.local_port}'
            ]
            
            self._log(f"🌐 Đang khởi động Cloudflare tunnel đến port {self.local_port}...")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Parse output để lấy URL - có thể xuất hiện trong stderr hoặc stdout
            # Cloudflared thường in URL dạng: https://xxxx.trycloudflare.com
            url_patterns = [
                re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com'),
                re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com/?'),
            ]
            
            # Đọc output với timeout
            start_time = time.time()
            timeout = 30  # 30 giây timeout
            
            while self.is_running and (time.time() - start_time) < timeout:
                if self.process.poll() is not None:
                    # Process đã kết thúc
                    self._log(f"❌ Cloudflared process exited with code: {self.process.returncode}")
                    break
                
                # Đọc line từ output
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    self._log(f"[cloudflared] {line}")
                    
                    # Tìm URL trong output
                    for pattern in url_patterns:
                        match = pattern.search(line)
                        if match and not self.public_url:
                            self.public_url = match.group(0)
                            self._log(f"✅ Cloudflare URL: {self.public_url}")
                            if self._on_url:
                                self._on_url(self.public_url)
                            break
                else:
                    # Không có output, đợi một chút
                    time.sleep(0.1)
            
            # Nếu đã có URL, tiếp tục đọc output để giữ process alive
            if self.public_url:
                self._log("🌐 Tunnel đang chạy, giữ kết nối...")
                while self.is_running:
                    if self.process.poll() is not None:
                        self._log("❌ Cloudflared process stopped")
                        break
                    line = self.process.stdout.readline()
                    if line:
                        self._log(f"[cloudflared] {line.strip()}")
                    else:
                        time.sleep(0.5)
            
            self.is_running = False
            if not self.public_url:
                self._log("❌ Không lấy được URL sau 30 giây")
        
        self._thread = threading.Thread(target=run_tunnel, daemon=True)
        self._thread.start()
        return True


class NgrokTunnel(BaseTunnel):
    """ngrok tunnel"""
    
    def __init__(self, local_port: int = 5000, auth_token: Optional[str] = None):
        super().__init__(local_port)
        self.auth_token = auth_token
    
    def start(self) -> bool:
        """Khởi động ngrok tunnel"""
        try:
            # Kiểm tra ngrok
            result = subprocess.run(
                ['ngrok', '--version'], 
                capture_output=True, 
                text=True
            )
            if result.returncode != 0:
                return False
        except FileNotFoundError:
            print("❌ ngrok chưa được cài đặt")
            print("   Download: https://ngrok.com/download")
            return False
        
        # Set auth token nếu có
        if self.auth_token:
            subprocess.run(['ngrok', 'config', 'add-authtoken', self.auth_token],
                         capture_output=True)
        
        def run_tunnel():
            self.is_running = True
            cmd = ['ngrok', 'http', str(self.local_port), '--log=stdout']
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # ngrok không log URL ra stdout, cần gọi API
            time.sleep(2)  # Đợi ngrok khởi động
            
            try:
                # Lấy URL từ ngrok API
                response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=10)
                data = response.json()
                if data.get('tunnels'):
                    self.public_url = data['tunnels'][0]['public_url']
                    print(f"✅ ngrok URL: {self.public_url}")
                    if self._on_url:
                        self._on_url(self.public_url)
            except Exception as e:
                print(f"⚠️ Không thể lấy ngrok URL: {e}")
            
            # Đợi process kết thúc
            self.process.wait()
            self.is_running = False
        
        self._thread = threading.Thread(target=run_tunnel, daemon=True)
        self._thread.start()
        return True


class Localtunnel(BaseTunnel):
    """Localtunnel (lt) - Node.js based"""
    
    def start(self) -> bool:
        """Khởi động localtunnel"""
        try:
            result = subprocess.run(
                ['lt', '--version'], 
                capture_output=True, 
                text=True, 
                shell=True
            )
        except FileNotFoundError:
            print("❌ localtunnel chưa được cài đặt")
            print("   Cài đặt: npm install -g localtunnel")
            return False
        
        def run_tunnel():
            self.is_running = True
            cmd = ['lt', '--port', str(self.local_port)]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                shell=True
            )
            
            # Parse URL
            url_pattern = re.compile(r'https?://[a-zA-Z0-9-]+\.loca\.lt')
            
            for line in self.process.stdout:
                if not self.is_running:
                    break
                
                match = url_pattern.search(line)
                if match and not self.public_url:
                    self.public_url = match.group(0)
                    print(f"✅ Localtunnel URL: {self.public_url}")
                    if self._on_url:
                        self._on_url(self.public_url)
            
            self.is_running = False
        
        self._thread = threading.Thread(target=run_tunnel, daemon=True)
        self._thread.start()
        return True


class TunnelManager:
    """Quản lý tất cả các loại tunnel"""
    
    TUNNEL_TYPES = {
        'cloudflare': CloudflareTunnel,
        'ngrok': NgrokTunnel,
        'localtunnel': Localtunnel
    }
    
    def __init__(self, local_port: int = 5000):
        self.local_port = local_port
        self.current_tunnel: Optional[BaseTunnel] = None
        self.tunnel_type: Optional[str] = None
    
    def start(self, tunnel_type: str, **kwargs) -> bool:
        """Khởi động tunnel theo loại"""
        if tunnel_type not in self.TUNNEL_TYPES:
            print(f"❌ Loại tunnel không hỗ trợ: {tunnel_type}")
            print(f"   Hỗ trợ: {', '.join(self.TUNNEL_TYPES.keys())}")
            return False
        
        # Dừng tunnel cũ nếu có
        self.stop()
        
        # Tạo tunnel mới
        tunnel_class = self.TUNNEL_TYPES[tunnel_type]
        self.current_tunnel = tunnel_class(self.local_port, **kwargs)
        self.tunnel_type = tunnel_type
        
        return self.current_tunnel.start()
    
    def stop(self):
        """Dừng tunnel hiện tại"""
        if self.current_tunnel:
            self.current_tunnel.stop()
            self.current_tunnel = None
            self.tunnel_type = None
    
    def get_status(self) -> dict:
        """Trả về trạng thái"""
        if self.current_tunnel:
            return self.current_tunnel.get_status()
        return {"running": False, "url": None, "type": None}
    
    def on_url(self, callback: Callable[[str], None]):
        """Đăng ký callback khi có URL"""
        if self.current_tunnel:
            self.current_tunnel.on_url(callback)
        return self

    def on_log(self, callback: Callable[[str], None]):
        """Đăng ký callback khi có log mới"""
        if self.current_tunnel:
            self.current_tunnel.on_log(callback)
        return self
    
    @staticmethod
    def is_cloudflared_installed() -> bool:
        """Kiểm tra cloudflared đã cài chưa"""
        try:
            subprocess.run(['cloudflared', '--version'], 
                         capture_output=True, check=True)
            return True
        except:
            return False
    
    @staticmethod
    def install_cloudflared() -> tuple[bool, str]:
        """Cài đặt cloudflared trên Windows"""
        try:
            # Kiểm tra winget
            result = subprocess.run(['winget', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return False, "winget không khả dụng. Vui lòng cài thủ công từ: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
            
            # Cài đặt qua winget
            result = subprocess.run(
                ['winget', 'install', '--id=Cloudflare.cloudflared', '-e', '--accept-package-agreements', '--accept-source-agreements'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                return True, "✅ Đã cài đặt cloudflared thành công! Vui lòng khởi động lại terminal/ứng dụng."
            else:
                return False, f"❌ Lỗi cài đặt: {result.stderr}"
                
        except Exception as e:
            return False, f"❌ Lỗi: {str(e)}"
    
    @staticmethod
    def cloudflared_login() -> tuple[bool, str]:
        """Đăng nhập Cloudflare account"""
        try:
            # Kiểm tra cloudflared đã cài chưa
            if not TunnelManager.is_cloudflared_installed():
                return False, "cloudflared chưa được cài đặt. Vui lòng cài đặt trước."
            
            # Chạy login
            result = subprocess.run(
                ['cloudflared', 'tunnel', 'login'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                return True, "✅ Đăng nhập Cloudflare thành công!"
            else:
                return False, f"❌ Lỗi đăng nhập: {result.stderr}"
                
        except Exception as e:
            return False, f"❌ Lỗi: {str(e)}"
    
    @staticmethod
    def get_cloudflared_path() -> str:
        """Lấy đường dẫn cloudflared"""
        try:
            result = subprocess.run(['where', 'cloudflared'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        # Các đường dẫn mặc định
        default_paths = [
            r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
            r"C:\Program Files\cloudflared\cloudflared.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe"),
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                return path
        
        return "cloudflared"
    
    @classmethod
    def get_available_tunnels(cls) -> list:
        """Kiểm tra các tunnel khả dụng trên hệ thống"""
        available = []
        
        # Kiểm tra cloudflared
        try:
            subprocess.run(['cloudflared', '--version'], 
                         capture_output=True, check=True)
            available.append('cloudflare')
        except:
            pass
        
        # Kiểm tra ngrok
        try:
            subprocess.run(['ngrok', '--version'], 
                         capture_output=True, check=True)
            available.append('ngrok')
        except:
            pass
        
        # Kiểm tra localtunnel
        try:
            subprocess.run(['lt', '--version'], 
                         capture_output=True, check=True, shell=True)
            available.append('localtunnel')
        except:
            pass
        
        return available


if __name__ == '__main__':
    # Test
    print("🔍 Kiểm tra tunnel khả dụng...")
    available = TunnelManager.get_available_tunnels()
    print(f"✅ Có sẵn: {', '.join(available) if available else 'Không có'}")
