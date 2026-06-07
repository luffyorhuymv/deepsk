"""
DeepSeek API Client
Gọi API DeepSeek thông qua asmodeus.free.nf
"""

import requests
import re
import time
from Crypto.Cipher import AES
from typing import Optional


class DeepSeekClient:
    """Client để gọi DeepSeek API"""
    
    BASE_URL = "https://asmodeus.free.nf"
    
    MODELS = [
        "DeepSeek-V1", "DeepSeek-V2", "DeepSeek-V2.5", "DeepSeek-V3", "DeepSeek-V3-0324",
        "DeepSeek-V3.1", "DeepSeek-V3.2", "DeepSeek-R1", "DeepSeek-R1-0528", "DeepSeek-R1-Distill",
        "DeepSeek-Prover-V1", "DeepSeek-Prover-V1.5", "DeepSeek-Prover-V2", "DeepSeek-VL",
        "DeepSeek-Coder", "DeepSeek-Coder-V2", "DeepSeek-Coder-6.7B-base", "DeepSeek-Coder-6.7B-instruct"
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Android)'
        })
        self._initialized = False
    
    def _solve_challenge(self) -> bool:
        """
        Giải challenge AES để lấy cookie __test
        """
        try:
            # Bước 1: Lấy challenge từ trang chủ
            response = self.session.get(f'{self.BASE_URL}/')
            response.raise_for_status()
            
            # Trích xuất các giá trị hex từ JavaScript
            nums = re.findall(r'toNumbers\("([a-f0-9]+)"\)', response.text)
            
            if len(nums) < 3:
                print("❌ Không tìm thấy challenge data")
                return False
            
            # Chuyển hex sang bytes
            key = bytes.fromhex(nums[0])
            iv = bytes.fromhex(nums[1])
            data = bytes.fromhex(nums[2])
            
            # Giải mã AES-CBC
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(data)
            cookie_value = decrypted.hex()
            
            # Set cookie
            self.session.cookies.set('__test', cookie_value, domain='asmodeus.free.nf')
            
            # Bước 2: Gọi index.php để activate session
            self.session.get(f'{self.BASE_URL}/index.php?i=1')
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"❌ Lỗi giải challenge: {e}")
            return False
    
    def chat(self, message: str, model: str = "DeepSeek-V3", retry: int = 2) -> Optional[str]:
        """
        Gửi tin nhắn và nhận phản hồi
        
        Args:
            message: Câu hỏi/tin nhắn cần gửi
            model: Tên model (mặc định: DeepSeek-V3)
            retry: Số lần thử lại nếu gặp lỗi
        
        Returns:
            Phản hồi từ AI hoặc None nếu lỗi
        """
        # Kiểm tra model hợp lệ
        if model not in self.MODELS:
            print(f"❌ Model không hợp lệ. Các model hỗ trợ: {', '.join(self.MODELS)}")
            return None
        
        for attempt in range(retry + 1):
            try:
                # Khởi tạo session nếu chưa có
                if not self._initialized:
                    print("🔐 Đang khởi tạo session...")
                    if not self._solve_challenge():
                        print("❌ Không thể giải challenge")
                        return None
                
                # Gửi request
                response = self.session.post(
                    f'{self.BASE_URL}/deepseek.php',
                    params={'i': '1'},
                    data={'model': model, 'question': message},
                    timeout=120
                )
                response.raise_for_status()
                
                # Kiểm tra nếu response là HTML challenge (cần retry)
                if '<script' in response.text and 'aes.js' in response.text:
                    print(f"⚠️ Nhận được HTML challenge (lần {attempt + 1}), đang retry...")
                    self._initialized = False  # Reset để giải challenge lại
                    time.sleep(1)
                    continue
                
                # Parse response
                match = re.search(
                    r'<div class="response-content">(.*?)</div>', 
                    response.text, 
                    re.DOTALL
                )
                
                if match:
                    return match.group(1).strip()
                else:
                    # Thử tìm pattern khác
                    match2 = re.search(r'<div[^>]*response[^>]*>(.*?)</div>', response.text, re.DOTALL | re.IGNORECASE)
                    if match2:
                        return match2.group(1).strip()
                    print("⚠️ Không tìm thấy nội dung phản hồi")
                    return response.text
                    
            except requests.exceptions.Timeout:
                print("❌ Timeout - Request quá lâu")
                return None
            except Exception as e:
                print(f"❌ Lỗi gọi API (lần {attempt + 1}): {e}")
                if attempt < retry:
                    time.sleep(2)
                    continue
                return None
        
        return None
    
    def list_models(self) -> list:
        """Trả về danh sách các model có sẵn"""
        return self.MODELS


# ============ VÍ DỤ SỬ DỤNG ============

if __name__ == "__main__":
    # Khởi tạo client
    client = DeepSeekClient()
    
    print("🤖 DeepSeek API Client")
    print("=" * 40)
    
    # Hiển thị danh sách model
    print("\n📋 Danh sách model:")
    for i, m in enumerate(client.list_models(), 1):
        print(f"  {i}. {m}")
    
    # Ví dụ 1: Chat đơn giản
    print("\n" + "=" * 40)
    print("💬 Ví dụ 1: Chat với DeepSeek-V3")
    print("=" * 40)
    
    response = client.chat(
        message="Xin chào, bạn là ai?",
        model="DeepSeek-V3"
    )
    
    if response:
        print(f"🤖 Phản hồi:\n{response}")
    
    # Ví dụ 2: Chat với model khác
    print("\n" + "=" * 40)
    print("💬 Ví dụ 2: Chat với DeepSeek-R1")
    print("=" * 40)
    
    response = client.chat(
        message="Giải thích về Machine Learning",
        model="DeepSeek-R1"
    )
    
    if response:
        print(f"🤖 Phản hồi:\n{response}")
