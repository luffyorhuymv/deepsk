# 🌐 Hướng Dẫn Gọi API Từ Xa Qua Tunnel

## 🎯 Cách Hoạt Động

```
[Client Remote] --HTTPS--> [Cloudflare Tunnel] --HTTP--> [Flask Server :5000] --> [DeepSeek API]

VD: https://abc123.trycloudflare.com/chat  -->  localhost:5000/chat
```

## 📡 Các API Endpoints

### 1. Health Check
```bash
GET https://your-tunnel-url.trycloudflare.com/health
```

**Response:**
```json
{"status": "healthy"}
```

---

### 2. Lấy Danh Sách Models
```bash
GET https://your-tunnel-url.trycloudflare.com/models
```

**Response:**
```json
{
  "models": ["DeepSeek-V3", "DeepSeek-R1", "DeepSeek-Coder", ...],
  "count": 18
}
```

---

### 3. Chat (API Chính)
```bash
POST https://your-tunnel-url.trycloudflare.com/chat
Content-Type: application/json
```

**Body:**
```json
{
  "message": "Xin chào, bạn là ai?",
  "model": "DeepSeek-V3"
}
```

**Response:**
```json
{
  "success": true,
  "model": "DeepSeek-V3",
  "message": "Xin chào, bạn là ai?",
  "response": "Tôi là DeepSeek, một AI assistant..."
}
```

---

## 💻 Ví Dụ Code

### Python
```python
import requests

# URL từ GUI (Cloudflare tunnel)
BASE_URL = "https://abc123.trycloudflare.com"

# 1. Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())  # {"status": "healthy"}

# 2. Chat
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "message": "Viết code Python tính giai thừa",
        "model": "DeepSeek-Coder"
    }
)
data = response.json()
print(data["response"])
```

---

### JavaScript (Fetch)
```javascript
const BASE_URL = "https://abc123.trycloudflare.com";

// Chat
const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: 'Giải thích về Machine Learning',
        model: 'DeepSeek-R1'
    })
});

const data = await response.json();
console.log(data.response);
```

---

### cURL
```bash
# Health check
curl https://abc123.trycloudflare.com/health

# Chat
curl -X POST https://abc123.trycloudflare.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "model": "DeepSeek-V3"}'
```

---

### Postman
1. Method: `POST`
2. URL: `https://your-tunnel-url.trycloudflare.com/chat`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "message": "Xin chào",
  "model": "DeepSeek-V3"
}
```

---

## 🔧 Tích Hợp với N8N

### HTTP Request Node
```
Method: POST
URL: https://your-tunnel-url.trycloudflare.com/chat
Body (JSON): {"message": "{{$json.query}}", "model": "DeepSeek-V3"}
```

### Webhook Trigger
Nếu muốn nhận request từ n8n:
1. Start server + tunnel
2. Copy public URL
3. Dùng URL đó trong HTTP node của n8n

---

## ⚠️ Lưu Ý

| Vấn đề | Giải pháp |
|--------|-----------|
| URL thay đổi mỗi lần restart | Dùng ngrok paid hoặc Cloudflare Tunnel cố định |
| Tunnel bị ngắt | Restart tunnel trong GUI |
| Timeout | Thêm timeout dài (120s) khi gọi API |

## 🔒 Bảo mật

- URL Cloudflare là **ngẫu nhiên** và **bí mật**
- Traffic được **mã hóa HTTPS**
- Không ai biết URL của bạn trừ khi bạn chia sẻ

## 🚀 Luồng Hoạt Động Tổng Thể

```
1. Mở DeepSeekProxyGUI.exe
2. Click "▶️ Start Server" (chạy ở port 5000)
3. Click "⬇️ Cài Cloudflared" (nếu chưa cài)
4. Click "🔐 Login Cloudflare" (nếu muốn dùng account)
5. Click "🌐 Start Tunnel" → Lấy URL (vd: https://abc.trycloudflare.com)
6. Dùng URL đó để gọi API từ xa!
```
