# Hướng dẫn sử dụng Cloudflare API Proxy UI

Giao diện đồ họa (GUI) này giúp bạn dễ dàng thiết lập một API Proxy cho DeepSeek thông qua Cloudflare Tunnel mà không cần cấu hình dòng lệnh phức tạp.

## 🚀 Cách khởi động

1. Chạy file `cloudflare_proxy_gui.py`:
   ```bash
   python cloudflare_proxy_gui.py
   ```
2. Trên giao diện hiện ra:
   - **Local Port**: Cổng mặc định là 5000 (bạn có thể thay đổi nếu cần).
   - **Start Server**: Nhấn nút này để khởi động Proxy Server (Flask).
   - **Start Tunnel**: Nhấn nút này để tạo URL công khai thông qua Cloudflare.

## 🛠️ Yêu cầu cài đặt (Cloudflare)

Nếu bạn chưa có `cloudflared` trên máy tính:
1. Nhấn nút **"Install cloudflared"** trên giao diện (sử dụng winget trên Windows).
2. Sau khi cài đặt, bạn có thể cần nhấn nút **"Login Cloudflare"** để xác thực tài khoản (không bắt buộc đối với Quick Tunnels nhưng khuyến khích).

## 📝 Các tính năng chính

- **Public URL**: Sau khi bật Tunnel, URL công khai sẽ hiện ra. Bạn có thể nhấn **Copy** hoặc **Open** để sử dụng.
- **Logs**: Theo dõi chi tiết tiến trình khởi chạy của Server và Tunnel.
- **Test API**: Nhập tin nhắn và nhấn **Send Test** để kiểm tra xem Proxy có đang hoạt động tốt hay không.

## ⚠️ Lưu ý

- Đảm bảo bạn đã cài đặt các thư viện cần thiết:
  ```bash
  pip install flask flask-cors requests
  ```
- Nếu Server báo lỗi không khởi động được, hãy kiểm tra xem Port đó có đang bị ứng dụng khác chiếm dụng không.
