# Open WebUI + DeepSeek Proxy (Docker)

Chạy Open WebUI kết nối tới DeepSeek API Proxy qua Docker Compose — 1 lệnh duy nhất.

## Kiến trúc

```
Browser  ──►  Open WebUI  ──►  DeepSeek Proxy  ──►  asmodeus.free.nf
              :8080            :5000
              (container)      (container)
                  │                 │
                  └──── deepseek-net ┘
```

## Yêu cầu

- Docker Desktop / Docker Engine
- Docker Compose v2 (`docker compose`)

## Chạy nhanh

```bash
# Build + start tất cả services
docker compose up -d --build

# Xem logs
docker compose logs -f

# Truy cập Open WebUI
# http://localhost:8080
```

Tài khoản đầu tiên tạo trong Open WebUI sẽ thành **admin**.

## Cấu hình

Tạo file `.env` (tùy chọn) để override defaults:

```env
# API key gửi tới proxy. Nếu proxy chưa có key nào, giá trị này bị bỏ qua.
OPENAI_API_KEY=sk-your-key-here

# Bật/tắt đăng nhập Open WebUI
WEBUI_AUTH=true

# Secret key cho session (để trống = random mỗi restart, sẽ mất session)
WEBUI_SECRET_KEY=change-me-to-random-string
```

## Models

Sau khi vào Open WebUI:

1. Click avatar góc trên phải → **Settings**
2. Tab **Connections** → **OpenAI API** đã tự động trỏ tới `http://deepseek-proxy:5000/v1`
3. Tab **Models** — danh sách models sẽ tự load từ proxy
4. Tick ✓ các model muốn dùng (vd: `DeepSeek-V3`, `DeepSeek-R1`, `DeepSeek-Coder`)

## API Key (tùy chọn, nếu muốn bảo vệ proxy)

```bash
# Tạo key mới
curl -X POST http://localhost:5000/v1/keys/generate \
  -H "Content-Type: application/json" \
  -d '{"note":"open-webui"}'

# Copy key, paste vào OPENAI_API_KEY trong .env
# Restart: docker compose restart open-webui
```

Nếu proxy **chưa có key nào**, endpoint `/v1/chat/completions` cho qua tự do (backward compat) — không cần set key.

## Các service

| Service | Port | Mô tả |
|---------|------|-------|
| `deepseek-proxy` | 5000 | Flask proxy gọi asmodeus |
| `open-webui` | 8080 | Giao diện chat |
| `cloudflare-tunnel` | - | Expose public URL (optional) |

## Lệnh hữu ích

```bash
# Stop
docker compose down

# Stop + xóa data Open WebUI
docker compose down -v

# Xem logs từng service
docker compose logs -f deepseek-proxy
docker compose logs -f open-webui

# Restart 1 service
docker compose restart open-webui

# Rebuild sau khi sửa code proxy
docker compose up -d --build deepseek-proxy
```

## Truy cập từ xa (không cần tunnel container)

Nếu đã có Cloudflare Tunnel / ngrok chạy ngoài Docker:

```bash
cloudflared tunnel --url http://localhost:8080
# → dùng URL https://xxx.trycloudflare.com truy cập Open WebUI
```

## Troubleshooting

**Open WebUI không thấy model:**
```bash
docker compose exec open-webui wget -qO- http://deepseek-proxy:5000/v1/models
# Phải trả về JSON danh sách models
```

**Lỗi 401 Unauthorized:**
- Proxy đã có key active. Tạo key qua endpoint `/v1/keys/generate`, paste vào `OPENAI_API_KEY`, restart.

**Port 8080 bị chiếm:**
- Đổi `"8080:8080"` → `"8888:8080"` trong `docker-compose.yml`.

**Lỗi "Connection refused" khi start Open WebUI:**
- Đợi proxy healthy (healthcheck 30s interval). `depends_on: condition: service_healthy` đã xử lý.
