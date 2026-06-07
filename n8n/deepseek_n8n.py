"""
DeepSeek API Service for n8n
Chạy như một webhook service để n8n có thể gọi
"""

from flask import Flask, request, jsonify
import sys
import os

# Add parent directory to path to import deepseek_api_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from deepseek_api_client import DeepSeekClient

app = Flask(__name__)
client = DeepSeekClient()

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint: POST /chat
    Body: {"message": "xin chào", "model": "DeepSeek-V3"}
    """
    data = request.get_json()
    
    message = data.get('message', '')
    model = data.get('model', 'DeepSeek-V3')
    
    if not message:
        return jsonify({"error": "Thiếu message"}), 400
    
    response = client.chat(message, model)
    
    return jsonify({
        "response": response,
        "model": model,
        "success": response is not None
    })

@app.route('/models', methods=['GET'])
def models():
    """Lấy danh sách model"""
    return jsonify({"models": client.list_models()})

@app.route('/health', methods=['GET'])
def health():
    """Kiểm tra service"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("🚀 DeepSeek API Service for n8n")
    print("📍 http://localhost:5000")
    print("\nEndpoints:")
    print("  POST /chat    - Gửi tin nhắn")
    print("  GET  /models  - Danh sách model")
    print("  GET  /health  - Kiểm tra status")
    app.run(host='0.0.0.0', port=5000, debug=False)
