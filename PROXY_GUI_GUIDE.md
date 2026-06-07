# 🚀 DeepSeek API Proxy + GUI

Expose DeepSeek API qua HTTP với giao diện đồ họa, hỗ trợ tunnel để gọi từ xa.

## 📁 Các file mới

| File | Mô tả |
|------|-------|
| `proxy_server.py` | Flask server expose API qua HTTP |
| `tunnel_manager.py` | Quản lý Cloudflare/ngrok/localtunnel |
| `proxy_gui.py` | Giao diện đồ họa (tkinter) |

## ⚡ Cài đặt

```bash
# Cài thư viện Python
pip install -r requirements.txt

# (Tùy chọn) Cài đặt tunnel - chọn 1 trong các lựa chọn:

# 1. Cloudflare Tunnel (khuyến nghị) - Free, ổn định
winget install Cloudflare.cloudflared
# hoặc download: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

# 2. ngrok - Cần đăng ký, có free tier
# Download: https://ngrok.com/download

# 3. localtunnel - Node.js
npm install -g localtunnel
```

## 🚀 Sử dụng

### 1. Khởi động GUI

```bash
python proxy_gui.py
```

### 2. Các bước sử dụng

1. **Chọn Port** (mặc định 5000)
2. **Click "▶️ Start Server"** - Khởi động API server local
3. **Chọn Tunnel** (cloudflare/ngrok/localtunnel)
4. **Click "🌐 Start Tunnel"** - Tạo public URL
5. **Copy URL** - Dùng để gọi API từ xa

## 📡 API Endpoints

### Health Check
```bash
GET http://your-public-url.health
```

### Danh sách Models
```bash
GET http://your-public-url/models
```

### Chat
```bash
POST http://your-public-url/chat
Content-Type: application/json

{
    "message": "Xin chào",
    "model": "DeepSeek-V3"
}
```

## 💻 Ví dụ gọi từ xa

### Python
```python
import requests

url = "https://xxxxx.trycloudflare.com/chat"  # URL từ GUI

response = requests.post(url, json={
    "message": "Viết code Python tính giai thừa",
    "model": "DeepSeek-Coder"
})

data = response.json()
print(data['response'])
```

### JavaScript (Fetch)
```javascript
const response = await fetch('https://xxxxx.trycloudflare.com/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: 'Xin chào',
        model: 'DeepSeek-V3'
    })
});

const data = await response.json();
console.log(data.response);
```

### cURL
```bash
curl -X POST https://xxxxx.trycloudflare.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "model": "DeepSeek-V3"}'
```

## 🔧 Cấu trúc hệ thống

```
┌─────────────────┐      HTTP       ┌─────────────────┐
│   Client Remote │◄────────────────►│  Public URL     │
│   (n8n, app...) │                  │  (Cloudflare)   │
└─────────────────┘                  └────────┬────────┘
                                              │
                                              ▼
                                       ┌───────────────┐
                                       │  Proxy Server │
                                       │  (Flask)      │
                                       │  localhost    │
                                       └───────┬───────┘
                                               │
                                               ▼
                                       ┌───────────────┐
                                       │ DeepSeek API  │
                                       │ (asmodeus)    │
                                       └───────────────┘
```

## 🛠️ Tính năng GUI

- ✅ **Start/Stop Server** - Quản lý Flask server
- ✅ **Multi Tunnel Support** - Cloudflare, ngrok, localtunnel
- ✅ **Auto URL Detection** - Tự động lấy public URL
- ✅ **Built-in API Test** - Test ngay trên GUI
- ✅ **Log Viewer** - Xem logs real-time
- ✅ **Copy/Open URL** - Tiện lợi

## ⚠️ Lưu ý

- Server Flask chạy ở chế độ threaded (hỗ trợ nhiều request đồng thờii)
- Cloudflare Tunnel là lựa chọn ổn định nhất và free
- Public URL thay đổi mỗi lần restart tunnel (trừ khi dùng ngrok paid)
- Nên giới hạn rate nếu expose public

## 🔒 Bảo mật

- Tunnel encrypt traffic tự động (HTTPS)
- Có thể thêm API key nếu cần bảo vệ thêm
- Không expose server trực tiếp, luôn dùng tunnel
