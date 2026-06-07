"""
Ví dụ đơn giản - Gọi API DeepSeek
"""

from deepseek_api_client import DeepSeekClient

# 1. Khởi tạo client
client = DeepSeekClient()

# 2. Gửi câu hỏi
response = client.chat(
    message="Viết code Python tính tổng 2 số",
    model="DeepSeek-V3"
)

# 3. In kết quả
print(response)
