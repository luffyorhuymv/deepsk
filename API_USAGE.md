# 📖 Hướng dẫn sử dụng DeepSeek API Client

## ⚡ Cài đặt thư viện cần thiết

```bash
pip install requests pycryptodome
```

## 📁 Cấu trúc file

| File | Mô tả |
|------|-------|
| `deepseek_api_client.py` | Class chính để gọi API |
| `example_simple.py` | Ví dụ đơn giản |
| `DeepSeek 18 model.py` | File gốc (CLI đầy đủ) |

## 🚀 Cách sử dụng

### 1. Cách đơn giản nhất

```python
from deepseek_api_client import DeepSeekClient

client = DeepSeekClient()
response = client.chat("Xin chào", model="DeepSeek-V3")
print(response)
```

### 2. Vòng lặp chat tương tác

```python
from deepseek_api_client import DeepSeekClient

client = DeepSeekClient()

while True:
    msg = input("\n📝 Bạn: ")
    if msg.lower() in ['exit', 'quit', 'thoát']:
        break
    
    response = client.chat(msg, model="DeepSeek-R1")
    if response:
        print(f"\n🤖 AI: {response}")
```

### 3. Chọn model khác

```python
# Lấy danh sách model
models = client.list_models()
print(models)

# Gọi model cụ thể
response = client.chat("Viết code Python", model="DeepSeek-Coder")
```

## 🔐 Quản lý API Key (Mới)

Server hiện hỗ trợ cơ chế bảo mật bằng API Key.

### 1. Cách tạo API Key mới
Bạn có thể tạo API Key bằng cách gửi request POST đến endpoint `/v1/keys/generate`:

```bash
curl -X POST http://localhost:5000/v1/keys/generate \
-H "Content-Type: application/json" \
-d '{"note": "Key cho n8n"}'
```

Kết quả trả về sẽ là một chuỗi dạng `sk-...`. Hãy lưu lại chuỗi này.

### 2. Cách sử dụng API Key
Khi hệ thống đã có ít nhất 1 API Key được tạo, các endpoint `/v1/models` và `/v1/chat/completions` sẽ yêu cầu Header Authorization:

```bash
curl -X POST http://localhost:5000/v1/chat/completions \
-H "Authorization: Bearer sk-YOUR_KEY_HERE" \
-H "Content-Type: application/json" \
-d '{
  "model": "DeepSeek-V3",
  "messages": [{"role": "user", "content": "Hello"}]
}'
```

*Lưu ý: Nếu chưa có bất kỳ key nào được tạo trong hệ thống, chế độ bảo mật sẽ tự động tắt để duy trì tính tương thích.*

## 📋 Danh sách Model

| # | Model | Mục đích |
|---|-------|----------|
| 1-5 | DeepSeek-V1 đến V3.2 | General purpose |
| 6-9 | DeepSeek-R1, R1-0528, R1-Distill | Reasoning |
| 10-12 | DeepSeek-Prover | Math/Proof |
| 13 | DeepSeek-VL | Vision-Language |
| 14-18 | DeepSeek-Coder | Code generation |

## ⚠️ Lưu ý

- API này **không phải chính thức** từ DeepSeek
- Có thể bị giới hạn rate limit
- Dữ liệu đi qua server trung gian
