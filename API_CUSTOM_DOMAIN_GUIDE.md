# 🌐 API Documentation - Custom Domain

**Base URL:** `https://dep.apphay.io.vn`

> Domain được kết nối qua Cloudflare Tunnel đến DeepSeek API Proxy

---

## 📡 API Endpoints

### 1. Health Check
Kiểm tra server đang chạy.

```http
GET https://dep.apphay.io.vn/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

---

### 2. Thông tin API
```http
GET https://dep.apphay.io.vn/
```

**Response:**
```json
{
  "name": "DeepSeek API Proxy",
  "version": "1.0.0",
  "endpoints": {
    "GET /": "Thông tin API",
    "GET /models": "Danh sách models",
    "POST /chat": "Gửi tin nhắn"
  }
}
```

---

### 3. Danh sách Models
```http
GET https://dep.apphay.io.vn/models
```

**Response:**
```json
{
  "models": [
    "DeepSeek-V1", "DeepSeek-V2", "DeepSeek-V2.5", "DeepSeek-V3",
    "DeepSeek-V3-0324", "DeepSeek-V3.1", "DeepSeek-V3.2",
    "DeepSeek-R1", "DeepSeek-R1-0528", "DeepSeek-R1-Distill",
    "DeepSeek-Prover-V1", "DeepSeek-Prover-V1.5", "DeepSeek-Prover-V2",
    "DeepSeek-VL", "DeepSeek-Coder", "DeepSeek-Coder-V2"
  ],
  "count": 18
}
```

---

### 4. Chat (API Chính)

```http
POST https://dep.apphay.io.vn/chat
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Nội dung câu hỏi",
  "model": "DeepSeek-V3"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | ✅ | Nội dung tin nhắn/câu hỏi |
| `model` | string | ❌ | Model AI (default: DeepSeek-V3) |

**Available Models:**
- `DeepSeek-V3` - Model mặc định, đa năng
- `DeepSeek-R1` - Reasoning, tư duy logic
- `DeepSeek-Coder` - Viết code
- `DeepSeek-VL` - Vision & Language

**Response:**
```json
{
  "success": true,
  "model": "DeepSeek-V3",
  "message": "Xin chào, bạn là ai?",
  "response": "Tôi là DeepSeek, một AI assistant..."
}
```

**Error Response:**
```json
{
  "error": "Message is required"
}
```

---

## 💻 Code Examples

### Python
```python
import requests

BASE_URL = "https://dep.apphay.io.vn"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Chat
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "message": "Viết code Python tính giai thừa",
        "model": "DeepSeek-Coder"
    },
    timeout=120
)

data = response.json()
print(data["response"])
```

---

### JavaScript (Node.js / Fetch)
```javascript
const BASE_URL = "https://dep.apphay.io.vn";

// Chat
async function chat(message, model = "DeepSeek-V3") {
    const response = await fetch(`${BASE_URL}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message, model })
    });
    
    const data = await response.json();
    return data.response;
}

// Sử dụng
chat("Xin chào, giới thiệu về bản thân").then(console.log);
```

---

### cURL
```bash
# Health check
curl https://dep.apphay.io.vn/health

# Get models
curl https://dep.apphay.io.vn/models

# Chat
curl -X POST https://dep.apphay.io.vn/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Giải thích Machine Learning đơn giản",
    "model": "DeepSeek-V3"
  }'
```

---

### PHP
```php
<?php
$base_url = "https://dep.apphay.io.vn";

// Chat
$data = [
    "message" => "Viết hàm PHP kết nối MySQL",
    "model" => "DeepSeek-Coder"
];

$ch = curl_init("$base_url/chat");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);

$response = curl_exec($ch);
curl_close($ch);

$result = json_decode($response, true);
echo $result['response'];
?>
```

---

## 🔧 Tích hợp với N8N

### HTTP Request Node

**Method:** POST  
**URL:** `https://dep.apphay.io.vn/chat`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "message": "{{$json.query}}",
  "model": "DeepSeek-V3"
}
```

### Webhook Response
Nếu muốn tạo chatbot qua webhook:
1. Tạo Webhook node (POST method)
2. Nối với HTTP Request node gọi đến `https://dep.apphay.io.vn/chat`
3. Trả về response cho ngườii dùng

---

## 🔐 Bảo Mật

### Cloudflare Protection
- ✅ SSL/TLS tự động (HTTPS)
- ✅ DDoS Protection
- ✅ Không expose IP thật

### Rate Limiting (Nếu cần)
Có thể cấu hình rate limit trong Cloudflare Dashboard để tránh abuse.

---

## ⚠️ Lưu Ý

| Vấn đề | Giải pháp |
|--------|-----------|
| Timeout | Thêm timeout >= 120s vì AI cần thởi gian xử lý |
| Server down | Kiểm tra DeepSeekProxyGUI.exe có đang chạy không |
| Model không tồn tại | Dùng `/models` để lấy danh sách chính xác |

---

## 🚀 Quick Start

### Bước 1: Kiểm tra API chạy
```bash
curl https://dep.apphay.io.vn/health
```

### Bước 2: Test chat
```bash
curl -X POST https://dep.apphay.io.vn/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào"}'
```

### Bước 3: Tích hợp vào app
Copy code examples ở trên vào project của bạn!

---

## 📞 Hỗ trợ

Nếu API không hoạt động:
1. Kiểm tra DeepSeekProxyGUI.exe đã start server chưa
2. Kiểm tra Cloudflare Tunnel đang chạy
3. Kiểm tra domain `dep.apphay.io.vn` trong Cloudflare Dashboard
