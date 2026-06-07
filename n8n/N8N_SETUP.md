# 🔗 Hướng dẫn tích hợp DeepSeek API với n8n

## Cách 1: Sử dụng Webhook Service (Khuyến nghị) ⭐

### Bước 1: Chạy service

```bash
cd n8n
pip install -r requirements.txt
python deepseek_n8n.py
```

Service chạy tại: `http://localhost:5000`

### Bước 2: Cấu hình n8n Workflow

```
[Trigger] → [HTTP Request] → [Output]
```

**HTTP Request node config:**
- **Method:** POST
- **URL:** `http://localhost:5000/chat`
- **Body:** JSON
```json
{
  "message": "{{$json.message}}",
  "model": "{{$json.model || 'DeepSeek-V3'}}"
}
```

---

## Cách 2: Sử dụng Code Node (JavaScript)

Nếu bạn muốn chạy trực tiếp trong n8n mà không cần external service:

### Workflow n8n:

```
[HTTP Request: GET Challenge] 
    ↓
[Code Node: Giải AES]
    ↓
[HTTP Request: POST Chat]
```

### Code Node (JavaScript):

```javascript
// Node 1: Parse challenge từ HTTP response
const html = $input.first().json.data;

// Trích xuất hex values
const regex = /toNumbers\("([a-f0-9]+)"\)/g;
const matches = [...html.matchAll(regex)];

return {
  key: matches[0][1],
  iv: matches[1][1],
  data: matches[2][1]
};
```

> ⚠️ **Lưu ý:** n8n Code Node không hỗ trợ thư viện crypto để giải AES dễ dàng.

---

## Cách 3: Sử dụng Docker (Production)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "deepseek_n8n.py"]
```

### Chạy:

```bash
docker build -t deepseek-n8n .
docker run -p 5000:5000 deepseek-n8n
```

---

## Cách 4: Sử dụng n8n + ngrok (Public Webhook)

Nếu n8n cloud cần gọi đến local service:

```bash
# Cài ngrok
npm install -g ngrok

# Expose service
gngrok http 5000
```

Copy URL ngrok (vd: `https://abc123.ngrok.io`) vào n8n HTTP Request node.

---

## 📋 Ví dụ Workflow n8n hoàn chỉnh

### Scenario: Chatbot Telegram + DeepSeek

```
[Telegram Trigger: Nhận tin nhắn]
    ↓
[HTTP Request: POST http://localhost:5000/chat]
    - Body: {"message": "{{$json.message.text}}"}
    ↓
[Telegram: Gửi phản hồi]
    - Text: "{{$json.response}}"
```

### Scenario: Webhook nhận câu hỏi

```
[Webhook Trigger]
    ↓
[HTTP Request: POST /chat]
    ↓
[Respond to Webhook]
```

---

## 🔧 API Endpoints

| Endpoint | Method | Body | Mô tả |
|----------|--------|------|-------|
| `/chat` | POST | `{"message": "...", "model": "..."}` | Gửi tin nhắn |
| `/models` | GET | - | Lấy danh sách model |
| `/health` | GET | - | Kiểm tra status |

---

## ⚠️ Lưu ý

1. **Rate Limiting:** Nên thêm Delay node trong n8n nếu gọi nhiều request
2. **Error Handling:** Thêm IF node để kiểm tra `success: true`
3. **Timeout:** Đặt HTTP Request timeout ≥ 120s vì AI cần thởi gian tạo phản hồi
