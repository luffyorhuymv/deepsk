"""
DeepSeek API Proxy GUI
Giao diện đồ họa để quản lý proxy server và tunnel
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import webbrowser
import requests
import json
from proxy_server import run_server, app
from tunnel_manager import TunnelManager
from deepseek_api_client import DeepSeekClient
from startup_manager import StartupManager


class ProxyGUI:
    APP_NAME = "DeepSeekProxy"
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 DeepSeek API Proxy")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        
        # Biến trạng thái
        self.server_running = False
        self.tunnel_running = False
        self.local_port = tk.IntVar(value=5000)
        self.selected_tunnel = tk.StringVar(value="cloudflare")
        self.public_url = ""
        self.is_startup = tk.BooleanVar(value=StartupManager.is_startup_enabled(self.APP_NAME))
        
        # Components
        self.server_thread = None
        self.tunnel_manager = TunnelManager(local_port=self.local_port.get())
        
        # Tạo UI
        self._create_styles()
        self._create_widgets()
        self._check_available_tunnels()
        
        # Auto-scroll log
        self.log_autoscroll = True
        
    def _create_styles(self):
        """Tạo styles cho ttk"""
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        self.style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        self.style.configure('Status.TLabel', font=('Segoe UI', 10))
        self.style.configure('URL.TLabel', font=('Segoe UI', 11, 'underline'), foreground='blue')
        
    def _create_widgets(self):
        """Tạo các widget"""
        # Main container với padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Log area expands
        
        # ========== HEADER ==========
        header = ttk.Label(main_frame, text="🚀 DeepSeek API Proxy", style='Title.TLabel')
        header.grid(row=0, column=0, pady=(0, 10), sticky="w")
        
        desc = ttk.Label(main_frame, text="Expose DeepSeek API qua HTTP để gọi từ xa", 
                        foreground='gray')
        desc.grid(row=1, column=0, pady=(0, 20), sticky="w")
        
        # ========== CONTROL PANEL ==========
        control_frame = ttk.LabelFrame(main_frame, text="⚙️ Điều khiển", padding="15")
        control_frame.grid(row=2, column=0, pady=(0, 15), sticky="ew")
        control_frame.columnconfigure(1, weight=1)
        
        # Local Port
        ttk.Label(control_frame, text="Local Port:").grid(row=0, column=0, sticky="w")
        port_spin = ttk.Spinbox(control_frame, from_=1024, to=65535, 
                               textvariable=self.local_port, width=10)
        port_spin.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # Server buttons
        self.btn_start_server = ttk.Button(
            control_frame, text="▶️ Start Server", 
            command=self.toggle_server, width=15
        )
        self.btn_start_server.grid(row=0, column=2, padx=(20, 5))
        
        self.lbl_server_status = ttk.Label(
            control_frame, text="⭕ Stopped", foreground='red'
        )
        self.lbl_server_status.grid(row=0, column=3, padx=(5, 0))
        
        # Tunnel selection
        ttk.Label(control_frame, text="Tunnel:").grid(row=1, column=0, sticky="w", pady=(15, 0))
        self.tunnel_combo = ttk.Combobox(
            control_frame, textvariable=self.selected_tunnel,
            values=["cloudflare", "ngrok", "localtunnel"],
            state="readonly", width=15
        )
        self.tunnel_combo.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(15, 0))
        
        self.btn_start_tunnel = ttk.Button(
            control_frame, text="🌐 Start Tunnel", 
            command=self.toggle_tunnel, width=15
        )
        self.btn_start_tunnel.grid(row=1, column=2, padx=(20, 5), pady=(15, 0))
        
        self.lbl_tunnel_status = ttk.Label(
            control_frame, text="⭕ Stopped", foreground='red'
        )
        self.lbl_tunnel_status.grid(row=1, column=3, padx=(5, 0), pady=(15, 0))
        
        # Cloudflare Setup buttons
        cf_frame = ttk.Frame(control_frame)
        cf_frame.grid(row=2, column=0, columnspan=4, pady=(15, 0), sticky="w")
        
        ttk.Label(cf_frame, text="Cloudflare:").grid(row=0, column=0, sticky="w")
        
        self.btn_install_cloudflare = ttk.Button(
            cf_frame, text="⬇️ Cài Cloudflared", 
            command=self.install_cloudflare, width=18
        )
        self.btn_install_cloudflare.grid(row=0, column=1, padx=(10, 5))
        
        self.btn_login_cloudflare = ttk.Button(
            cf_frame, text="🔐 Login Cloudflare", 
            command=self.login_cloudflare, width=18
        )
        self.btn_login_cloudflare.grid(row=0, column=2, padx=(5, 0))
        
        # System options
        ttk.Checkbutton(
            cf_frame, text="Khởi động cùng Windows", 
            variable=self.is_startup, command=self.toggle_startup
        ).grid(row=1, column=0, columnspan=3, pady=(10, 0), sticky="w")
        
        # ========== PUBLIC URL ==========
        url_frame = ttk.LabelFrame(main_frame, text="🌎 Public URL", padding="15")
        url_frame.grid(row=3, column=0, pady=(0, 15), sticky="ew")
        url_frame.columnconfigure(0, weight=1)
        
        self.lbl_url = ttk.Label(url_frame, text="(Chưa có URL)", style='Status.TLabel')
        self.lbl_url.grid(row=0, column=0, sticky="w")
        
        self.btn_copy_url = ttk.Button(
            url_frame, text="📋 Copy", command=self.copy_url, state="disabled"
        )
        self.btn_copy_url.grid(row=0, column=1, padx=(10, 5))
        
        self.btn_open_url = ttk.Button(
            url_frame, text="🔗 Mở", command=self.open_url, state="disabled"
        )
        self.btn_open_url.grid(row=0, column=2)
        
        # ========== TEST API ==========
        test_frame = ttk.LabelFrame(main_frame, text="🧪 Test API", padding="15")
        test_frame.grid(row=4, column=0, pady=(0, 15), sticky="ew")
        test_frame.columnconfigure(0, weight=1)
        
        # Model selection
        ttk.Label(test_frame, text="Model:").grid(row=0, column=0, sticky="w")
        self.test_model = ttk.Combobox(
            test_frame, 
            values=DeepSeekClient.MODELS,
            width=20, state="readonly"
        )
        self.test_model.set("DeepSeek-V3")
        self.test_model.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # Message input
        ttk.Label(test_frame, text="Message:").grid(row=1, column=0, sticky="nw", pady=(10, 0))
        self.test_message = tk.Text(test_frame, height=3, width=50)
        self.test_message.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(10, 0))
        self.test_message.insert("1.0", "Xin chào, bạn là ai?")
        
        self.btn_test = ttk.Button(
            test_frame, text="📤 Gửi", command=self.test_api
        )
        self.btn_test.grid(row=1, column=2, padx=(10, 0), pady=(10, 0))
        
        # Response
        ttk.Label(test_frame, text="Response:").grid(row=2, column=0, sticky="nw", pady=(10, 0))
        self.test_response = scrolledtext.ScrolledText(
            test_frame, height=4, width=50, wrap=tk.WORD
        )
        self.test_response.grid(row=2, column=1, columnspan=2, sticky="ew", 
                               padx=(10, 0), pady=(10, 0))
        
        # ========== LOGS ==========
        log_frame = ttk.LabelFrame(main_frame, text="📝 Logs", padding="10")
        log_frame.grid(row=5, column=0, sticky="nsew", pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=10, wrap=tk.WORD, state="disabled"
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        # Log buttons
        log_btn_frame = ttk.Frame(log_frame)
        log_btn_frame.grid(row=1, column=0, pady=(5, 0), sticky="e")
        
        ttk.Button(log_btn_frame, text="🗑️ Clear", 
                  command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 5))
        
        self.autoscroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(log_btn_frame, text="Auto-scroll", 
                       variable=self.autoscroll_var).pack(side=tk.LEFT)
        
        # ========== API DOCS ==========
        docs_frame = ttk.LabelFrame(main_frame, text="📚 API Documentation", padding="10")
        docs_frame.grid(row=6, column=0, sticky="ew")
        docs_frame.columnconfigure(0, weight=1)
        
        docs_text = """POST /chat - Gửi tin nhắn
  Body: {"message": "...", "model": "DeepSeek-V3"}
  
GET /models - Danh sách models
GET /health - Health check"""
        
        docs_label = tk.Label(docs_frame, text=docs_text, 
                             font=('Consolas', 10), justify=tk.LEFT,
                             bg='#f5f5f5', fg='#333')
        docs_label.grid(row=0, column=0, sticky="w")
        
        self.log("🚀 DeepSeek API Proxy GUI đã khởi động")
        self.log("📖 Sẵn sàng để start server...")
    
    def _check_available_tunnels(self):
        """Kiểm tra tunnel khả dụng"""
        # Kiểm tra cloudflared
        if TunnelManager.is_cloudflared_installed():
            self.log("✅ Cloudflared đã được cài đặt")
            self.btn_install_cloudflare.configure(state="disabled")
            self.btn_login_cloudflare.configure(state="normal")
        else:
            self.log("⚠️ Cloudflared chưa được cài đặt")
            self.log("   Click 'Cài Cloudflared' để cài đặt tự động")
            self.btn_install_cloudflare.configure(state="normal")
            self.btn_login_cloudflare.configure(state="disabled")
        
        # Kiểm tra các tunnel khác
        available = TunnelManager.get_available_tunnels()
        if available:
            self.log(f"✅ Tunnel khả dụng: {', '.join(available)}")
    
    def log(self, message: str):
        """Thêm log"""
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"[{self._get_time()}] {message}\n")
        if self.autoscroll_var.get():
            self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
    
    def _get_time(self):
        """Lấy thời gian hiện tại"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def clear_logs(self):
        """Xóa logs"""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")
    
    def toggle_server(self):
        """Bật/tắt server"""
        if not self.server_running:
            self.start_server()
        else:
            self.stop_server()
    
    def start_server(self):
        """Khởi động server"""
        try:
            port = self.local_port.get()
            self.server_thread = threading.Thread(
                target=run_server,
                args=('0.0.0.0', port, False),
                daemon=True
            )
            self.server_thread.start()
            
            self.server_running = True
            self.btn_start_server.configure(text="⏹️ Stop Server")
            self.lbl_server_status.configure(text=f"🟢 Running (:{port})", foreground='green')
            self.log(f"✅ Server đã khởi động tại http://localhost:{port}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể khởi động server:\n{e}")
            self.log(f"❌ Lỗi khởi động server: {e}")
    
    def stop_server(self):
        """Dừng server"""
        # Flask không có cách dừng clean, cần restart app
        self.log("⚠️ Vui lòng đóng cửa sổ để dừng server hoàn toàn")
        self.server_running = False
        self.btn_start_server.configure(text="▶️ Start Server")
        self.lbl_server_status.configure(text="⭕ Stopped", foreground='red')
    
    def toggle_tunnel(self):
        """Bật/tắt tunnel"""
        if not self.tunnel_running:
            self.start_tunnel()
        else:
            self.stop_tunnel()
    
    def start_tunnel(self):
        """Khởi động tunnel"""
        if not self.server_running:
            messagebox.showwarning("Cảnh báo", "Vui lòng start server trước!")
            return
        
        tunnel_type = self.selected_tunnel.get()
        self.tunnel_manager = TunnelManager(local_port=self.local_port.get())
        
        # Callback khi có URL
        def on_url(url):
            self.public_url = url
            self.root.after(0, self._update_url_ui, url)
        
        self.tunnel_manager.on_url(on_url)
        
        success = self.tunnel_manager.start(tunnel_type)
        
        if success:
            self.tunnel_running = True
            self.btn_start_tunnel.configure(text="⏹️ Stop Tunnel")
            self.lbl_tunnel_status.configure(
                text=f"🟢 {tunnel_type.title()}", foreground='green'
            )
            self.log(f"🌐 Đang khởi động {tunnel_type} tunnel...")
        else:
            messagebox.showerror(
                "Lỗi", 
                f"Không thể khởi động {tunnel_type}.\n"
                f"Vui lòng kiểm tra đã cài đặt chưa."
            )
    
    def _update_url_ui(self, url: str):
        """Cập nhật UI khi có URL"""
        self.lbl_url.configure(text=url, style='URL.TLabel', cursor="hand2")
        self.lbl_url.bind("<Button-1>", lambda e: webbrowser.open(url))
        self.btn_copy_url.configure(state="normal")
        self.btn_open_url.configure(state="normal")
        self.log(f"🌎 Public URL: {url}")
    
    def stop_tunnel(self):
        """Dừng tunnel"""
        self.tunnel_manager.stop()
        self.tunnel_running = False
        self.btn_start_tunnel.configure(text="🌐 Start Tunnel")
        self.lbl_tunnel_status.configure(text="⭕ Stopped", foreground='red')
        self.lbl_url.configure(text="(Chưa có URL)", style='Status.TLabel', cursor="")
        self.btn_copy_url.configure(state="disabled")
        self.btn_open_url.configure(state="disabled")
        self.public_url = ""
        self.log("🌐 Tunnel đã dừng")
    
    def copy_url(self):
        """Copy URL vào clipboard"""
        if self.public_url:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.public_url)
            self.log("📋 Đã copy URL vào clipboard")
    
    def open_url(self):
        """Mở URL trong browser"""
        if self.public_url:
            webbrowser.open(self.public_url)
    
    def install_cloudflare(self):
        """Cài đặt cloudflared"""
        self.log("⬇️ Đang cài đặt cloudflared...")
        self.btn_install_cloudflare.configure(state="disabled")
        
        def do_install():
            success, message = TunnelManager.install_cloudflared()
            self.root.after(0, self._handle_install_result, success, message)
        
        threading.Thread(target=do_install, daemon=True).start()
    
    def _handle_install_result(self, success: bool, message: str):
        """Xử lý kết quả cài đặt"""
        self.log(message)
        if success:
            self.btn_install_cloudflare.configure(state="disabled")
            self.btn_login_cloudflare.configure(state="normal")
            messagebox.showinfo("Thành công", message)
        else:
            self.btn_install_cloudflare.configure(state="normal")
            messagebox.showerror("Lỗi", message)
    
    def login_cloudflare(self):
        """Đăng nhập Cloudflare"""
        self.log("🔐 Đang đăng nhập Cloudflare...")
        self.log("   Mở browser để xác thực...")
        
        def do_login():
            success, message = TunnelManager.cloudflared_login()
            self.root.after(0, self._handle_login_result, success, message)
        
        threading.Thread(target=do_login, daemon=True).start()
    
    def _handle_login_result(self, success: bool, message: str):
        """Xử lý kết quả đăng nhập"""
        self.log(message)
        if success:
            messagebox.showinfo("Thành công", message)
        else:
            messagebox.showerror("Lỗi", message)
    
    def toggle_startup(self):
        """Bật/tắt khởi động cùng Windows"""
        if self.is_startup.get():
            if StartupManager.enable_startup(self.APP_NAME):
                self.log("✅ Đã bật khởi động cùng Windows")
            else:
                self.log("❌ Lỗi khi bật khởi động cùng Windows")
                self.is_startup.set(False)
        else:
            if StartupManager.disable_startup(self.APP_NAME):
                self.log("ℹ️ Đã tắt khởi động cùng Windows")
            else:
                self.log("❌ Lỗi khi tắt khởi động cùng Windows")
                self.is_startup.set(True)
    
    def test_api(self):
        """Test API"""
        if not self.server_running:
            messagebox.showwarning("Cảnh báo", "Server chưa chạy!")
            return
        
        message = self.test_message.get("1.0", tk.END).strip()
        model = self.test_model.get()
        
        if not message:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập message!")
            return
        
        self.test_response.delete("1.0", tk.END)
        self.test_response.insert(tk.END, "⏳ Đang gửi...")
        self.btn_test.configure(state="disabled")
        
        def do_test():
            try:
                url = f"http://localhost:{self.local_port.get()}/chat"
                response = requests.post(
                    url,
                    json={"message": message, "model": model},
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get('response', 'Không có phản hồi')
                else:
                    result = f"Lỗi {response.status_code}: {response.text}"
                
                self.root.after(0, self._update_test_response, result)
                
            except Exception as e:
                self.root.after(0, self._update_test_response, f"Lỗi: {e}")
        
        threading.Thread(target=do_test, daemon=True).start()
    
    def _update_test_response(self, text: str):
        """Cập nhật kết quả test"""
        self.test_response.delete("1.0", tk.END)
        self.test_response.insert(tk.END, text)
        self.btn_test.configure(state="normal")
        self.log("✅ Test API hoàn thành")


def main():
    root = tk.Tk()
    app = ProxyGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
