# 🔨 Build File .exe cho DeepSeek Proxy GUI

## 📋 Yêu cầu

- Python 3.8+ đã cài đặt
- Windows 10/11

## ⚡ Cách 1: Cloudflare Proxy GUI (Mới nhất)

```bash
# Chạy build script chuyên biệt cho Cloudflare
python build_cloudflare.py
```

Khi chạy, script sẽ hỏi bạn nhập phiên bản (ví dụ: `v1.0.0`).

File kết quả: `dist/Cloudflare-Proxy-v1.0.0.exe` (tên file phụ thuộc vào phiên bản bạn nhập)

## ⚡ Cách 2: DeepSeek Proxy GUI (Bản cũ)

```bash
# Chạy build script cũ
python build_exe.py
```

Khi chạy, script sẽ hỏi bạn chọn kiểu build (onefile/onedir) và nhập phiên bản.

File kết quả: `dist/DeepSeek-Proxy-v1.0.0.exe` (tên file phụ thuộc vào phiên bản bạn nhập)

## ⚡ Cách 3: Build thủ công

```bash
# 1. Cài PyInstaller
pip install pyinstaller

# 2. Build (one file, no console)
python -m PyInstaller \
    --name="DeepSeek-Proxy" \
    --onefile \
    --noconsole \
    --hidden-import=requests \
    --hidden-import=Crypto \
    --hidden-import=Crypto.Cipher \
    --hidden-import=Crypto.Cipher.AES \
    --hidden-import=flask \
    --hidden-import=flask_cors \
    --hidden-import=werkzeug \
    --hidden-import=jinja2 \
    proxy_gui.py
```

## 📁 Kết quả

Sau khi build thành công:
```
dist/
└── DeepSeek-Proxy-v1.0.0.exe    ← File này có thể chạy độc lập
```

## 🚀 Sử dụng file .exe

1. **Copy file** `DeepSeek-Proxy-vX.X.X.exe` sang máy khác (không cần cài Python)
2. **Double-click** để chạy
3. **Sử dụng GUI** như bình thường

## 💡 Lưu ý quan trọng

| Vấn đề | Giải pháp |
|--------|-----------|
| File bị detect virus | Đây là false positive, add exception hoặc build tự build |
| Cloudflare tunnel không chạy | Cần cài `cloudflared` riêng trên máy đích |
| File .exe to (~15-20MB) | Bình thường vì bundle cả Python runtime |
| Chạy bị lỗi thiếu DLL | Cài [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) |

## 🔧 Tùy chọn build nâng cao

### Build nhiều file (nhẹ hơn, load nhanh hơn)
```bash
python -m PyInstaller --onedir --noconsole proxy_gui.py
```

### Thêm icon
```bash
python -m PyInstaller --onefile --noconsole --icon=icon.ico proxy_gui.py
```

### Build với console (debug)
```bash
python -m PyInstaller --onefile proxy_gui.py
```

## 📦 Phân phối

Để ngườii khác dùng, chỉ cần gửi file:
```
DeepSeek-Proxy-v1.0.0.exe
```

Hoặc nén thành ZIP:
```bash
# Windows PowerShell
Compress-Archive -Path dist\DeepSeek-Proxy-v1.0.0.exe -DestinationPath DeepSeek-Proxy-v1.0.0.zip
```

## 🛠️ Troubleshooting

### Lỗi "Failed to execute script"
Chạy lại với `--console` để xem lỗi chi tiết:
```bash
python -m PyInstaller --onefile proxy_gui.py
# Chạy dist\DeepSeek-Proxy.exe trong CMD để xem lỗi
```

### Lỗi thiếu module
Thêm `--hidden-import=module_name` vào lệnh build

### File bị Windows Defender chặn
- Add file vào exception
- Hoặc build trên máy đích
- Hoặc dùng code signing (trả phí)
