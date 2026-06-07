"""
Cloudflare API Proxy GUI
Giao diện đơn giản để chạy API Proxy qua Cloudflare Tunnel
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import webbrowser
import time
import os
import requests
from proxy_server import run_server
from tunnel_manager import TunnelManager
from deepseek_api_client import DeepSeekClient
from startup_manager import StartupManager

class CloudflareProxyGUI:
    APP_NAME = "DeepSeekCloudflareProxy"
    
    def __init__(self, root):
        self.root = root
        self.root.title("☁️ Cloudflare API Proxy")
        self.root.geometry("800x700")
        
        # Biến trạng thái
        self.server_running = False
        self.tunnel_running = False
        self.local_port = tk.IntVar(value=5000)
        self.public_url = ""
        self.is_startup = tk.BooleanVar(value=StartupManager.is_startup_enabled(self.APP_NAME))
        
        # Components
        self.server_thread = None
        self.tunnel_manager = TunnelManager(local_port=self.local_port.get())
        
        self._setup_ui()
        self.log("🚀 Sẵn sàng khởi động Proxy và Tunnel...")

    def _setup_ui(self):
        """Thiết lập giao diện"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Tiêu đề
        title_label = ttk.Label(main_frame, text="☁️ Cloudflare API Proxy", font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # --- Cấu hình & Cài đặt ---
        config_frame = ttk.LabelFrame(main_frame, text=" Cấu hình & Cài đặt ", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 15))

        # Dòng 1: Port & Khởi động
        row1 = ttk.Frame(config_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Local Port:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(row1, textvariable=self.local_port, width=10).pack(side=tk.LEFT, padx=5)
        
        self.btn_server = ttk.Button(row1, text="▶️ Start Server", command=self.toggle_server, width=15)
        self.btn_server.pack(side=tk.LEFT, padx=10)
        
        self.btn_tunnel = ttk.Button(row1, text="🌐 Start Tunnel", command=self.toggle_tunnel, width=15)
        self.btn_tunnel.pack(side=tk.LEFT, padx=5)

        # Dòng 2: Cloudflare Tools
        row2 = ttk.Frame(config_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text="Cloudflare:").pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="⬇️ Install cloudflared", command=self.install_cloudflare).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="🔐 Login Cloudflare", command=self.login_cloudflare).pack(side=tk.LEFT, padx=5)

        # Dòng 3: Tùy chọn hệ thống
        row3 = ttk.Frame(config_frame)
        row3.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(row3, text="Khởi động cùng Windows", variable=self.is_startup, command=self.toggle_startup).pack(side=tk.LEFT, padx=5)

        # --- Trạng thái ---
        status_frame = ttk.LabelFrame(main_frame, text=" Trạng thái ", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 15))

        self.lbl_server_status = ttk.Label(status_frame, text="Server: ⭕ Stopped", foreground="red", font=("Segoe UI", 10))
        self.lbl_server_status.pack(anchor=tk.W)

        self.lbl_tunnel_status = ttk.Label(status_frame, text="Tunnel: ⭕ Stopped", foreground="red", font=("Segoe UI", 10))
        self.lbl_tunnel_status.pack(anchor=tk.W)

        url_container = ttk.Frame(status_frame)
        url_container.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(url_container, text="Public URL: ").pack(side=tk.LEFT)
        self.ent_url = ttk.Entry(url_container, state="readonly", font=("Consolas", 10))
        self.ent_url.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(url_container, text="📋 Copy", command=self.copy_url, width=8).pack(side=tk.LEFT)
        ttk.Button(url_container, text="🌍 Open", command=self.open_url, width=8).pack(side=tk.LEFT, padx=5)

        # --- Test API ---
        test_frame = ttk.LabelFrame(main_frame, text=" Test API (Gửi tin nhắn thử nghiệm) ", padding="10")
        test_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Dòng chọn Model
        test_model_row = ttk.Frame(test_frame)
        test_model_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(test_model_row, text="Model:").pack(side=tk.LEFT, padx=5)
        self.cmb_model = ttk.Combobox(test_model_row, values=DeepSeekClient.MODELS, state="readonly", width=30)
        self.cmb_model.set("DeepSeek-V3")
        self.cmb_model.pack(side=tk.LEFT, padx=5)

        # Dòng nhập tin nhắn
        test_input_row = ttk.Frame(test_frame)
        test_input_row.pack(fill=tk.X)
        
        self.ent_test_msg = ttk.Entry(test_input_row)
        self.ent_test_msg.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.ent_test_msg.insert(0, "Xin chào!")
        
        self.btn_test = ttk.Button(test_input_row, text="🚀 Send Test", command=self.test_api)
        self.btn_test.pack(side=tk.RIGHT)

        # --- Logs ---
        ttk.Label(main_frame, text="Logs:").pack(anchor=tk.W)
        self.log_area = scrolledtext.ScrolledText(main_frame, height=15, font=("Consolas", 9), state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        """Thêm message vào log area"""
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"{timestamp} {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def toggle_server(self):
        if not self.server_running:
            self.start_server()
        else:
            self.stop_server()

    def start_server(self):
        port = self.local_port.get()
        self.log(f"Đang khởi động Server trên port {port}...")
        
        def run():
            try:
                self.server_running = True
                self.root.after(0, lambda: self.btn_server.config(text="⏹️ Stop Server"))
                self.root.after(0, lambda: self.lbl_server_status.config(text=f"Server: ✅ Running on port {port}", foreground="green"))
                run_server(port=port)
            except Exception as e:
                self.log(f"❌ Lỗi Server: {str(e)}")
                self.root.after(0, self.stop_server)

        self.server_thread = threading.Thread(target=run, daemon=True)
        self.server_thread.start()

    def stop_server(self):
        self.server_running = False
        self.btn_server.config(text="▶️ Start Server")
        self.lbl_server_status.config(text="Server: ⭕ Stopped", foreground="red")
        self.log("⚠️ Server đã dừng (Lưu ý: Tiến trình Flask có thể vẫn chạy ngầm)")

    def toggle_tunnel(self):
        if not self.tunnel_running:
            self.start_tunnel()
        else:
            self.stop_tunnel()

    def start_tunnel(self):
        self.log("Đang khởi động Cloudflare Tunnel...")
        self.tunnel_manager.local_port = self.local_port.get()
        
        def on_url(url):
            self.public_url = url
            self.root.after(0, self._update_url_ui, url)

        def on_log(msg):
            self.root.after(0, self.log, msg)

        success = self.tunnel_manager.start("cloudflare")
        if success:
            self.tunnel_running = True
            self.btn_tunnel.config(text="⏹️ Stop Tunnel")
            self.lbl_tunnel_status.config(text="Tunnel: ⏳ Đang khởi tạo...", foreground="orange")
            self.tunnel_manager.on_url(on_url)
            self.tunnel_manager.on_log(on_log)
        else:
            self.log("❌ Không thể khởi động Tunnel.")
            messagebox.showerror("Lỗi", "Không tìm thấy cloudflared. Hãy nhấn 'Install cloudflared' bên trên.")

    def _update_url_ui(self, url):
        self.ent_url.config(state="normal")
        self.ent_url.delete(0, tk.END)
        self.ent_url.insert(0, url)
        self.ent_url.config(state="readonly")
        self.lbl_tunnel_status.config(text="Tunnel: ✅ Active", foreground="green")
        self.log(f"✅ Tunnel thành công: {url}")

    def stop_tunnel(self):
        self.tunnel_manager.stop()
        self.tunnel_running = False
        self.btn_tunnel.config(text="🌐 Start Tunnel")
        self.lbl_tunnel_status.config(text="Tunnel: ⭕ Stopped", foreground="red")
        self.ent_url.config(state="normal")
        self.ent_url.delete(0, tk.END)
        self.ent_url.config(state="readonly")
        self.log("Tunnel đã dừng.")

    def install_cloudflare(self):
        self.log("⬇️ Bắt đầu cài đặt cloudflared...")
        def do_install():
            success, msg = TunnelManager.install_cloudflared()
            self.root.after(0, lambda: messagebox.showinfo("Kết quả", msg) if success else messagebox.showerror("Lỗi", msg))
            self.root.after(0, self.log, msg)
        threading.Thread(target=do_install, daemon=True).start()

    def login_cloudflare(self):
        self.log("🔐 Đang mở trang đăng nhập Cloudflare...")
        def do_login():
            success, msg = TunnelManager.cloudflared_login()
            self.root.after(0, lambda: messagebox.showinfo("Kết quả", msg) if success else messagebox.showerror("Lỗi", msg))
            self.root.after(0, self.log, msg)
        threading.Thread(target=do_login, daemon=True).start()

    def toggle_startup(self):
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

    def copy_url(self):
        url = self.ent_url.get()
        if url:
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            messagebox.showinfo("Thông báo", "Đã copy URL!")

    def open_url(self):
        url = self.ent_url.get()
        if url:
            webbrowser.open(url)

    def test_api(self):
        msg = self.ent_test_msg.get()
        model = self.cmb_model.get()
        if not self.server_running:
            messagebox.showwarning("Lỗi", "Hãy bật Server trước!")
            return
        
        self.log(f"🧪 Đang test API với model {model} và tin nhắn: '{msg}'")
        def do_test():
            try:
                # Test qua localhost để nhanh
                resp = requests.post(f"http://localhost:{self.local_port.get()}/chat", 
                                  json={"message": msg, "model": model}, timeout=30)
                if resp.status_code == 200:
                    result = resp.json().get('response', 'No response')
                    self.root.after(0, self.log, f"🤖 Phản hồi: {result[:100]}...")
                else:
                    self.root.after(0, self.log, f"❌ Lỗi API: {resp.status_code}")
            except Exception as e:
                self.root.after(0, self.log, f"❌ Lỗi kết nối: {str(e)}")
        threading.Thread(target=do_test, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app_gui = CloudflareProxyGUI(root)
    root.mainloop()
