# 🖥️ Hướng Dẫn Cài Đặt DeepSeek API Proxy lên VPS

Tài liệu này hướng dẫn các cách khác nhau để triển khai API Proxy lên máy chủ VPS của bạn.

---

## 📋 Yêu cầu

- VPS Ubuntu 20.04/22.04 hoặc CentOS 7/8
- RAM tối thiểu 512MB (khuyến nghị 1GB)
- Port 5000 hoặc 80/443 mở
- Domain (tùy chọn)

---

## 🚀 Cách 1: Cài Đặt Tự Động (One-Click - Khuyến nghị)

Đây là cách nhanh nhất và dễ nhất. Script sẽ tự động cài đặt mọi thứ (Python, Docker, Service).

### Bước 1: SSH vào VPS
```bash
ssh root@your-vps-ip
```

### Bước 2: Chạy script cài đặt
Nếu bạn đã tải mã nguồn lên VPS, hãy chạy:
```bash
chmod +x setup.sh
./setup.sh
```

Hoặc nếu bạn muốn tải và chạy trực tiếp từ GitHub (thay thế `USER` và `REPO` bằng thông tin của bạn):
```bash
curl -sSL https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main/setup.sh | bash
```

---

## 🐳 Cách 2: Cài Đặt Qua Docker (Nhanh & Sạch)

Nếu VPS của bạn đã cài Docker & Docker Compose, đây là cách nhanh nhất để deploy.

### Bước 1: SSH và Tải Code
```bash
# Upload code lên thư mục /opt/deepseek-api trên VPS
cd /opt/deepseek-api
```

### Bước 2: Khởi Chạy Bằng Docker Compose
```bash
docker-compose up -d --build
```

### Bước 3: Kiểm tra Logs
```bash
docker logs -f deepseek-proxy
```

*Lưu ý: Server sẽ tự động chạy trên port 5000 và tự khởi động lại khi VPS reboot.*

---

## ⚡ Cách 3: Cài Đặt Thủ Công (Basic)

Nếu bạn muốn kiểm soát hoàn toàn quá trình cài đặt:

### Bước 1: SSH vào VPS
```bash
ssh root@your-vps-ip
```

### Bước 2: Cài Python & pip
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# CentOS/RHEL
sudo yum update
sudo yum install -y python3 python3-pip git
```

### Bước 3: Thiết lập thư mục
```bash
cd /opt
mkdir deepseek-api && cd deepseek-api
```

### Bước 4: Cài đặt Production (Systemd)

### Bước 1: Tạo virtual environment
```bash
cd /opt/deepseek-api
python3 -m venv venv
source venv/bin/activate

# Cài thư viện
pip install -r requirements.txt
```

### Bước 2: Tạo Systemd Service

Tạo file service:
```bash
sudo nano /etc/systemd/system/deepseek-api.service
```

Thêm nội dung:
```ini
[Unit]
Description=DeepSeek API Proxy Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/deepseek-api
Environment="PATH=/opt/deepseek-api/venv/bin"
ExecStart=/opt/deepseek-api/venv/bin/python proxy_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Bước 3: Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable deepseek-api
sudo systemctl start deepseek-api

# Kiểm tra status
sudo systemctl status deepseek-api

# Xem logs
sudo journalctl -u deepseek-api -f
```

---

## 🔒 Cách 4: Dùng Nginx + SSL (Tên Miền Riêng)

### Bước 1: Cài Nginx
```bash
# Ubuntu/Debian
sudo apt install -y nginx

# CentOS/RHEL
sudo yum install -y nginx
```

### Bước 2: Cấu hình Nginx Reverse Proxy

Tạo config:
```bash
sudo nano /etc/nginx/sites-available/deepseek-api
```

Thêm:
```nginx
server {
    listen 80;
    server_name dep.apphay.io.vn;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/deepseek-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Bước 3: Cài SSL (Let's Encrypt)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d dep.apphay.io.vn
```

---

## 🔥 Mở Firewall

### UFW (Ubuntu)
```bash
sudo ufw allow 5000/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### FirewallD (CentOS)
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

---

## 🧪 Kiểm tra sau khi cài

### Trên VPS
```bash
curl http://localhost:5000/health
```

### Từ máy khác
```bash
curl http://your-vps-ip:5000/health
```

Hoặc nếu có domain:
```bash
curl https://dep.apphay.io.vn/health
```

---

## 📡 Gọi API từ xa

```python
import requests

# Dùng IP VPS
BASE_URL = "http://your-vps-ip:5000"

# Hoặc domain
BASE_URL = "https://dep.apphay.io.vn"

response = requests.post(f"{BASE_URL}/chat", json={
    "message": "Xin chào",
    "model": "DeepSeek-V3"
})

print(response.json()["response"])
```

---

## ⚠️ Bảo mật (QUAN TRỌNG)

### 1. Thay đổi port mặc định (nếu cần)
Sửa `proxy_server.py`:
```python
def run_server(host='0.0.0.0', port=8080):  # Đổi port
```

### 1. Tạo API Key bảo mật
Hệ thống hiện đã hỗ trợ tạo API Key tự động. Bạn không cần sửa code.

**Cách tạo key:**
Sau khi server chạy, hãy gửi một request POST để lấy key mới:
```bash
curl -X POST http://localhost:5000/v1/keys/generate \
-H "Content-Type: application/json" \
-d '{"note": "Key cho n8n hoặc Chatbox"}'
```
Hệ thống sẽ trả về một mã `sk-...`. Hãy lưu lại mã này.

**Cách sử dụng:**
Khi đã có key, mọi yêu cầu sau này phải kèm theo header Authorization:
```bash
curl -X POST http://localhost:5000/v1/chat/completions \
-H "Authorization: Bearer sk-YOUR_KEY_HERE" \
-H "Content-Type: application/json" \
-d '{"model": "DeepSeek-V3", "messages": [{"role": "user", "content": "Hello"}]}'
```

*Lưu ý: Nếu bạn chưa bao giờ gọi lệnh tạo key, hệ thống sẽ mặc định cho phép truy cập tự do.*

### 3. Giới hạn IP (Firewall)
```bash
# Chỉ cho phép IP cụ thể
sudo ufw allow from 1.2.3.4 to any port 5000
```

---

## 🔧 Troubleshooting

### Lỗi port đã được sử dụng
```bash
# Kill process đang dùng port 5000
sudo fuser -k 5000/tcp

# Hoặc đổi port
python3 proxy_server.py --port 8080
```

### Server tự tắt khi thoát SSH
Dùng screen hoặc tmux:
```bash
# Cài screen
sudo apt install screen

# Chạy
screen -S deepseek
python3 proxy_server.py

# Thoát: Ctrl+A, D
# Vào lại: screen -r deepseek
```

### Lỗi permission
```bash
chmod -R 755 /opt/deepseek-api
```

---

## 🔧 Các Lệnh Quản Lý Nhanh

### Với Docker
```bash
# Xem logs
docker logs -f deepseek-proxy

# Dừng container
docker stop deepseek-proxy

# Chạy lại
docker start deepseek-proxy
```

### Với Systemd
```bash
# Xem logs
sudo journalctl -u deepseek-api -f

# Restart service
sudo systemctl restart deepseek-api
```

---

## 📝 Tóm tắt lệnh nhanh

```bash
# 1. VPS Setup
ssh root@your-vps-ip
apt update && apt install -y python3-pip git

# 2. Upload code (từ local)
scp -r c:\AI\api root@your-vps-ip:/opt/deepseek-api

# 3. Trên VPS
cd /opt/deepseek-api
pip3 install -r requirements.txt
python3 proxy_server.py

# 4. Hoặc chạy background
nohup python3 proxy_server.py &

# 5. Kiểm tra
curl http://your-vps-ip:5000/health
```

---

## ✅ Checklist hoàn thành

- [ ] Code đã upload lên VPS
- [ ] Python & thư viện đã cài
- [ ] Server đang chạy
- [ ] Firewall đã mở port
- [ ] Test API từ máy khác thành công
- [ ] (Tùy chọn) Domain đã trỏ đến VPS
- [ ] (Tùy chọn) SSL đã cài
