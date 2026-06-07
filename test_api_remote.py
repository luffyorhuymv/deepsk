"""
Test DeepSeek API từ xa qua Internet
Chạy file này từ bất kỳ máy nào có kết nối internet
"""

import requests
import json
import sys

# 🔗 Nhập URL của bạn ở đây
# Nếu dùng Cloudflare Tunnel: https://abc123.trycloudflare.com
# Nếu dùng VPS/Domain: https://dep.apphay.io.vn
BASE_URL = input("Nhập API URL (vd: https://abc.trycloudflare.com): ").strip().rstrip('/')

if not BASE_URL:
    print("❌ Vui lòng nhập URL!")
    sys.exit(1)

if not BASE_URL.startswith('http'):
    BASE_URL = 'https://' + BASE_URL

print(f"\n🌐 Testing API: {BASE_URL}")
print("=" * 50)


def test_health():
    """Test health check"""
    print("\n1️⃣ Test Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Server OK: {response.json()}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_models():
    """Test lấy danh sách models"""
    print("\n2️⃣ Test Get Models...")
    try:
        response = requests.get(f"{BASE_URL}/models", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Có {data['count']} models")
            print(f"   Models: {', '.join(data['models'][:5])}...")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_chat():
    """Test chat API"""
    print("\n3️⃣ Test Chat API...")
    print("   Gửi: 'Xin chào, giới thiệu về bản thân'")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "Xin chào, giới thiệu về bản thân",
                "model": "DeepSeek-V3"
            },
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response từ {data['model']}:")
            print(f"   {data['response'][:200]}...")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_custom_message():
    """Test với câu hỏi tùy chỉnh"""
    print("\n4️⃣ Test Chat với câu hỏi tùy chỉnh...")
    message = input("   Nhập câu hỏi (hoặc Enter để bỏ qua): ").strip()
    
    if not message:
        print("   ⏭️ Bỏ qua")
        return None
    
    model = input("   Chọn model (DeepSeek-V3/DeepSeek-R1/DeepSeek-Coder): ").strip() or "DeepSeek-V3"
    
    try:
        print(f"   Đang gửi đến {model}...")
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": message, "model": model},
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Response:\n{data['response']}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def main():
    """Chạy tất cả tests"""
    print("\n🔍 Bắt đầu test API...")
    
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    
    # Test 2: Models
    results.append(("Get Models", test_models()))
    
    # Test 3: Chat
    results.append(("Chat API", test_chat()))
    
    # Test 4: Custom
    custom_result = test_custom_message()
    if custom_result is not None:
        results.append(("Custom Message", custom_result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 KẾT QUẢ TEST:")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {name}")
    
    print(f"\n📈 Tổng: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 API hoạt động tốt trên Internet!")
    else:
        print("\n⚠️ Có lỗi xảy ra, vui lòng kiểm tra lại.")


if __name__ == "__main__":
    main()
