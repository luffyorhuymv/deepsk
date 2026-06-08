"""
DeepSeek API Proxy Server
Expose API qua HTTP để gọi từ xa
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from deepseek_api_client import DeepSeekClient
from functools import wraps
import logging
import threading
import time
import uuid
import secrets
import os
import json

# Tắt log mặc định của Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app)  # Cho phép CORS

# Global client instance
client = DeepSeekClient()
client_lock = threading.Lock()

# Đường dẫn file lưu trữ API Keys
KEYS_FILE = 'api_keys.json'

def generate_api_key():
    """Tạo một API Key ngẫu nhiên theo chuẩn sk-..."""
    return f"sk-{secrets.token_hex(24)}"

def save_api_key(api_key, note=""):
    """Lưu API key vào file"""
    keys = {}
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, 'r') as f:
                keys = json.load(f)
        except:
            keys = {}
    
    keys[api_key] = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "note": note,
        "active": True
    }
    
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=4)
    return True

def verify_api_key(api_key):
    """Kiểm tra API key có hợp lệ không"""
    if not os.path.exists(KEYS_FILE):
        return False
    try:
        with open(KEYS_FILE, 'r') as f:
            keys = json.load(f)
        return api_key in keys and keys[api_key].get('active', False)
    except:
        return False

def require_api_key(f):
    """Decorator để bắt buộc API Key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kiểm tra file keys, nếu chưa có key nào thì cho qua (bảo trì tính tương thích)
        keys = {}
        if os.path.exists(KEYS_FILE):
            try:
                with open(KEYS_FILE, 'r') as f_keys:
                    keys = json.load(f_keys)
            except:
                pass
        
        # Nếu không có bất kỳ key nào đang active, cho phép truy cập tự do
        has_active_keys = any(v.get('active', False) for v in keys.values())
        if not has_active_keys:
            return f(*args, **kwargs)
            
        # Nếu có key trong hệ thống, bắt đầu kiểm tra Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            # Nếu dùng Chatbox/NextChat mà không nhập key, header có thể trống
            return jsonify({
                "error": "Authentication required. Please provide a valid API Key in the Authorization header."
            }), 401
            
        api_key = auth_header.replace('Bearer ', '').strip()
        
        if api_key == "any" and not has_active_keys:
            return f(*args, **kwargs)
            
        if verify_api_key(api_key):
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Invalid API Key"}), 401
            
    return decorated_function


@app.route('/')
def index():
    """Trang chủ - Hiển thị thông tin API"""
    return jsonify({
        "name": "DeepSeek API Proxy",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "Thông tin API",
            "GET /models": "Danh sách models",
            "POST /chat": "Gửi tin nhắn (JSON: {message, model})",
            "GET /v1/models": "OpenAI Compatible Models",
            "POST /v1/chat/completions": "OpenAI Compatible Chat",
            "POST /v1/keys/generate": "Tạo API Key mới"
        }
    })


@app.route('/v1/keys/generate', methods=['POST'])
def generate_key_endpoint():
    """Endpoint tạo API key mới"""
    data = request.get_json() or {}
    note = data.get('note', 'Generated via API')
    
    new_key = generate_api_key()
    save_api_key(new_key, note)
    
    return jsonify({
        "status": "success",
        "api_key": new_key,
        "note": note,
        "message": "API Key đã được tạo và lưu trữ thành công."
    })


@app.route('/v1/models')
@require_api_key
def v1_models():
    """Endpoint danh sách models theo chuẩn OpenAI"""
    models = client.list_models()
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": model,
                "object": "model",
                "created": 1677610602,
                "owned_by": "deepseek"
            } for model in models
        ]
    })


@app.route('/v1/chat/completions', methods=['POST'])
@require_api_key
def v1_chat_completions():
    """Endpoint Chat Completions chuẩn OpenAI"""
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({"error": "Missing 'messages' in request"}), 400
        
        messages = data.get('messages', [])
        model = data.get('model', 'DeepSeek-V3')
        
        # Kiểm tra model hợp lệ (nếu client có danh sách hỗ trợ)
        if hasattr(client, 'MODELS') and model not in client.MODELS:
            return jsonify({"error": f"Unknown model: {model}", "available": client.MODELS}), 400
            
        # Lấy message cuối cùng làm nội dung câu hỏi
        if not messages:
            return jsonify({"error": "Messages list is empty"}), 400
            
        # Lấy nội dung của message cuối cùng từ role 'user'
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = normalize_openai_content(msg.get('content', ''))
                break
        
        if not user_message:
            user_message = normalize_openai_content(messages[-1].get('content', ''))

        if not user_message:
            return jsonify({"error": "No content found in messages"}), 400

        with client_lock:
            response_text = client.chat(message=user_message, model=model)
            
        if response_text is None:
            return jsonify({"error": "Failed to get response from API"}), 500
        
        # Format response chuẩn OpenAI
        completion_id = f"chatcmpl-{uuid.uuid4()}"
        created_time = int(time.time())
        
        # Streaming SSE response
        if data.get('stream'):
            def generate():
                chunk = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "delta": {"role": "assistant", "content": response_text},
                        "finish_reason": None
                    }]
                }
                yield "data: " + json.dumps(chunk, ensure_ascii=False) + "\n\n"
                done = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": model,
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
                }
                yield "data: " + json.dumps(done, ensure_ascii=False) + "\n\n"
                yield "data: [DONE]\n\n"
            return Response(generate(), mimetype='text/event-stream')
        
        # Non-streaming response
        return jsonify({
            "id": completion_id,
            "object": "chat.completion",
            "created": created_time,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(user_message.split()) + len(response_text.split())
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/models')
def get_models():
    """Trả về danh sách models"""
    return jsonify({
        "models": client.list_models(),
        "count": len(client.list_models())
    })


@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint chat chính
    
    Request JSON:
    {
        "message": "Xin chào",
        "model": "DeepSeek-V3"  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400
        
        message = data.get('message', '').strip()
        model = data.get('model', 'DeepSeek-V3')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Gọi API với lock để thread-safe
        with client_lock:
            response = client.chat(message=message, model=model)
        
        if response is None:
            return jsonify({"error": "Failed to get response from API"}), 500
        
        return jsonify({
            "success": True,
            "model": model,
            "message": message,
            "response": response
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Chạy server"""
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    print("🚀 Starting DeepSeek API Proxy Server...")
    print("📍 URL: http://localhost:5000")
    run_server()
