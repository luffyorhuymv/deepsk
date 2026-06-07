# 🚀 DeepSeek API Proxy

Proxy server expose API DeepSeek (từ `asmodeus.free.nf`) qua HTTP, tương thích chuẩn **OpenAI**. Hỗ trợ **GUI desktop**, **Docker + Open WebUI**, **n8n**, **tunnel public**, và **build EXE** chạy độc lập.

> Dùng khi muốn gọi DeepSeek từ app/web bất kỳ mà không cần code trực tiếp client crypto AES.

---

## ✨ Tính năng

- 🔌 **OpenAI-compatible API** — `/v1/models`, `/v1/chat/completions`
- 🖥️ **GUI desktop** (tkinter) — Start/Stop server, chọn tunnel, test API, xem log
- 🐳 **Docker Compose** — 1 lệnh chạy cả proxy + Open WebUI
- 🌐 **Tunnel tự động** — Cloudflare / ngrok / localtunnel
- 🔐 **API Key auth** — Optional, tạo key qua HTTP endpoint
- 📦 **18 models** — V1-V3.2, R1 (reasoning), Coder, Prover, VL
- 🔗 **Tích hợp sẵn** — n8n workflow, Cloudflare custom domain
- 💻 **Build EXE** — Chạy độc lập trên Windows, không cần Python

---

## ⚡ Quick Start (Docker — Khuyến nghị)

```bash
git clone https://github.com/luffyorhuymv/deepsk.git
cd deepsk
cp .env.example .env
# Sửa .env: điền CLOUDFLARE_TUNNEL_TOKEN nếu cần public URL

docker compose up -d --build
```

Truy cập:
- **Open WebUI** → http://localhost:8080 (chat giao diện đẹp, acc đầu tiên = admin)
- **Proxy API** → http://localhost:5000

Test nhanh:
```bash
curl http://localhost:5000/health
# {"status":"healthy"}
```

Xem chi tiết: [OPEN_WEBUI_DOCKER.md](OPEN_WEBUI_DOCKER.md)

---

## 🐍 Cài đặt thủ công (Python)

### Yêu cầu
- Python 3.8+
- pip

### Cài đặt
```bash
git clone https://github.com/luffyorhuymv/deepsk.git
cd deepsk
pip install -r requirements.txt
```

### Chạy server
```bash
python proxy_server.py
# Server: http://localhost:5000
```

### Chạy GUI
```bash
python proxy_gui.py
```

GUI cho phép:
- Chọn port (mặc định 5000)
- Start/Stop server
- Chọn tunnel (Cloudflare/ngrok/localtunnel)
- Test API ngay trong app
- Xem log real-time

Xem chi tiết: [PROXY_GUI_GUIDE.md](PROXY_GUI_GUIDE.md)

---

## 💻 Build EXE Windows

```bash
pip install pyinstaller
pyinstaller DeepSeek-Proxy-v1.spec
# Hoặc dùng script:
python build_exe.py
```

Output: `dist/DeepSeek-Proxy-v1.exe` — chạy độc lập, không cần Python.

Xem chi tiết: [BUILD_EXE.md](BUILD_EXE.md)

---

## 🖥️ Deploy lên VPS

```bash
# SSH vào VPS
ssh root@your-vps-ip

# Upload code (hoặc git clone), rồi:
chmod +x setup.sh
sudo ./setup.sh
```

Script tự động: cài Python/Docker, tạo service, mở firewall.

Xem chi tiết: [VPS_DEPLOY_GUIDE.md](VPS_DEPLOY_GUIDE.md)

---

## 🔗 Tích hợp

### Open WebUI (chat UI đẹp)
Đã có sẵn trong `docker-compose.yml`. Sau khi start:
1. Mở http://localhost:8080
2. Tạo acc admin
3. Settings → Connections → OpenAI API (tự động trỏ tới proxy)
4. Settings → Models → tick models muốn dùng

Chi tiết: [OPEN_WEBUI_DOCKER.md](OPEN_WEBUI_DOCKER.md)

### n8n (workflow automation)
```bash
cd n8n
pip install -r requirements.txt
python deepseek_n8n.py
```

Trong n8n workflow: HTTP Request node → `POST http://localhost:5000/v1/chat/completions`.

Có sẵn workflow mẫu: `n8n/n8n_direct_workflow.json`.

Chi tiết: [n8n/N8N_SETUP.md](n8n/N8N_SETUP.md)

### Cloudflare Tunnel (public URL)
Đã cấu hình trong `docker-compose.yml` (service `cloudflare-tunnel`).
Public URL sẽ tự động có sau khi start container.

Hoặc chạy tunnel ngoài Docker:
```bash
cloudflared tunnel --url http://localhost:5000
# → https://xxx.trycloudflare.com
```

Chi tiết: [CLOUDFLARE_GUIDE.md](CLOUDFLARE_GUIDE.md) · [API_CUSTOM_DOMAIN_GUIDE.md](API_CUSTOM_DOMAIN_GUIDE.md)

---

## 📡 API Reference

Base URL: `http://localhost:5000` (hoặc public URL từ tunnel)

### `GET /`
Thông tin API + danh sách endpoints.

### `GET /health`
```bash
curl http://localhost:5000/health
# {"status":"healthy"}
```

### `GET /v1/models`
OpenAI-compatible models list.
```bash
curl http://localhost:5000/v1/models
```

### `POST /v1/chat/completions`
OpenAI-compatible chat.
```bash
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DeepSeek-V3",
    "messages": [{"role": "user", "content": "Xin chào"}]
  }'
```

### `POST /v1/keys/generate`
Tạo API key mới (chỉ cần khi muốn bật auth).
```bash
curl -X POST http://localhost:5000/v1/keys/generate \
  -H "Content-Type: application/json" \
  -d '{"note": "key cho open-webui"}'
# → {"api_key": "sk-abc123...", ...}
```

Sau khi có ≥1 key, mọi request tới `/v1/*` phải có header:
```
Authorization: Bearer sk-your-key-here
```

### Endpoint custom (không cần key)
- `POST /chat` — `{message, model}` (format đơn giản)
- `GET /models` — danh sách models (format custom)

---

## 🤖 Danh sách Models

| # | Model | Dùng cho |
|---|-------|----------|
| 1-5 | DeepSeek-V1, V2, V2.5, V3, V3-0324, V3.1, V3.2 | General purpose |
| 6-9 | DeepSeek-R1, R1-0528, R1-Distill | Reasoning |
| 10-12 | DeepSeek-Prover-V1, V1.5, V2 | Toán/Chứng minh |
| 13 | DeepSeek-VL | Vision-Language |
| 14-18 | DeepSeek-Coder, Coder-V2, Coder-6.7B | Code generation |

---

## ⚙️ Cấu hình

### File `.env` (cho Docker)
```env
CLOUDFLARE_TUNNEL_TOKEN=your-token
OPENAI_API_KEY=sk-no-auth-needed
WEBUI_AUTH=true
WEBUI_SECRET_KEY=random-string-32-chars
```

### File `api_keys.json` (tự sinh khi tạo key)
Lưu trữ API keys. **KHÔNG commit** (đã có trong `.gitignore`).

---

## 🛠️ Troubleshooting

| Lỗi | Nguyên nhân | Cách xử lý |
|------|-------------|------------|
| `Connection refused` khi start Open WebUI | Proxy chưa healthy | Đợi healthcheck (30s) — `depends_on` đã xử lý |
| `401 Invalid API Key` | Proxy có key active, client chưa gửi | Tạo key qua `/v1/keys/generate`, paste vào `OPENAI_API_KEY` |
| `Port 8080 already in use` | Open WebUI trùng port | Đổi `"8080:8080"` → `"8888:8080"` trong `docker-compose.yml` |
| `docker: command not found` | Chưa cài Docker | Cài [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| Open WebUI không thấy models | Proxy chưa start hoặc network lỗi | `docker compose logs deepseek-proxy` |
| Tunnel token invalid | Token sai/hết hạn | Rotate trên Cloudflare Zero Trust, cập nhật `.env` |

Debug nhanh:
```bash
docker compose ps                  # trạng thái services
docker compose logs -f             # log tất cả
docker compose exec deepseek-proxy python -c "import requests; print(requests.get('http://localhost:5000/health').json())"
```

---

## 📁 Cấu trúc dự án

```
deepsk/
├── proxy_server.py            # Flask proxy (chính)
├── proxy_gui.py               # GUI tkinter
├── deepseek_api_client.py     # Client gọi asmodeus (AES decrypt)
├── tunnel_manager.py          # Quản lý Cloudflare/ngrok/localtunnel
├── startup_manager.py         # Auto-start với Windows
├── cloudflare_proxy_gui.py    # GUI riêng cho Cloudflare
│
├── Dockerfile                 # Build image proxy
├── docker-compose.yml         # proxy + open-webui + cloudflared
├── requirements.txt           # Python deps
├── setup.sh                   # VPS one-click install
│
├── n8n/                       # Tích hợp n8n
│   ├── deepseek_n8n.py
│   ├── n8n_direct_workflow.json
│   └── N8N_SETUP.md
│
├── build_exe.py               # Build EXE Windows
├── build_cloudflare.py
├── *.spec                     # PyInstaller configs
│
├── .env.example               # Template env vars
├── .gitignore
└── *.md                       # Docs (hướng dẫn chi tiết)
```

---

## 📚 Tài liệu chi tiết

- [OPEN_WEBUI_DOCKER.md](OPEN_WEBUI_DOCKER.md) — Docker + Open WebUI
- [PROXY_GUI_GUIDE.md](PROXY_GUI_GUIDE.md) — GUI desktop
- [API_USAGE.md](API_USAGE.md) — API reference
- [API_MODELS_USAGE.md](API_MODELS_USAGE.md) — Models guide
- [API_REMOTE_GUIDE.md](API_REMOTE_GUIDE.md) — Gọi API từ xa
- [API_CUSTOM_DOMAIN_GUIDE.md](API_CUSTOM_DOMAIN_GUIDE.md) — Custom domain
- [CLOUDFLARE_GUIDE.md](CLOUDFLARE_GUIDE.md) — Cloudflare Tunnel
- [VPS_DEPLOY_GUIDE.md](VPS_DEPLOY_GUIDE.md) — Deploy lên VPS
- [BUILD_EXE.md](BUILD_EXE.md) — Build EXE
- [n8n/N8N_SETUP.md](n8n/N8N_SETUP.md) — n8n workflow

---

## ⚠️ Lưu ý

- API DeepSeek **không phải chính thức**, đi qua server trung gian `asmodeus.free.nf` — có thể giới hạn rate hoặc gián đoạn
- Nên bật API key auth nếu expose public
- Public tunnel URL đổi mỗi lần restart (trừ khi dùng Cloudflare named tunnel)

---

## 📄 License

MIT
