# Sử dụng Python slim image để giảm dung lượng
FROM python:3.10-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file requirements trước để tận dụng Docker cache
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Expose port mà ứng dụng đang sử dụng (5000 trong proxy_server.py)
EXPOSE 5000

# Chạy server
CMD ["python", "proxy_server.py"]
