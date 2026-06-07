# 📖 Hướng dẫn gọi 18 Model DeepSeek qua lệnh CURL

Tài liệu này hướng dẫn cách sử dụng lệnh `curl` để gọi tất cả các model DeepSeek đang được hỗ trợ qua API Proxy của bạn tại địa chỉ: `https://apids.apphay.io.vn/`

---

## 📋 1. Cách lấy danh sách model trực tiếp
Bạn có thể xem danh sách 18 model mới nhất mà hệ thống hỗ trợ bằng cách chạy lệnh:
```bash
curl -X GET https://apids.apphay.io.vn/models
```

---

## 🚀 2. Cấu trúc lệnh CURL chung
Để gọi bất kỳ model nào, bạn hãy dùng cấu trúc lệnh sau:
```bash
curl -X POST https://apids.apphay.io.vn/chat \
-H "Content-Type: application/json" \
-d '{
  "message": "Nội dung câu hỏi của bạn ở đây",
  "model": "TÊN_MODEL_Ở_ĐÂY"
}'
```

---

## 🤖 3. Danh sách 18 Model & Ví dụ cụ thể

Dưới đây là ví dụ gọi các model phổ biến nhất trong hệ thống:

### 🌟 Model mặc định (DeepSeek-V3)
*Tốt nhất cho mọi tác vụ: thông minh nhất, phản hồi nhanh nhất.*
```bash
curl -X POST https://apids.apphay.io.vn/chat \
-H "Content-Type: application/json" \
-d '{"message": "DeepSeek-V3 là gì?", "model": "DeepSeek-V3"}'
```

### 🧠 Model suy luận (DeepSeek-R1)
*Chuyên sâu cho toán học, logic và giải quyết vấn đề phức tạp.*
```bash
curl -X POST https://apids.apphay.io.vn/chat \
-H "Content-Type: application/json" \
-d '{"message": "Giải bài toán 15x^2 - 10 = 5", "model": "DeepSeek-R1"}'
```

### 💻 Model lập trình (DeepSeek-Coder-V2)
*Chuyên về viết code, debug và giải thích thuật toán.*
```bash
curl -X POST https://apids.apphay.io.vn/chat \
-H "Content-Type: application/json" \
-d '{"message": "Viết code Python giải thuật toán Dijkstra", "model": "DeepSeek-Coder-V2"}'
```

---

## 📝 4. Bảng danh sách 18 Model hỗ trợ (Đầy đủ)

Bạn có thể thay thế giá trị `"model"` bằng bất kỳ tên nào trong danh sách dưới đây:

| STT | Tên Model | Ghi chú |
|:---:|:---|:---|
| 1 | `DeepSeek-V1` | Phiên bản V1 đời đầu |
| 2 | `DeepSeek-V2` | Phiên bản V2 |
| 3 | `DeepSeek-V2.5` | Phiên bản V2.5 nâng cấp |
| 4 | **`DeepSeek-V3`** | **Bản mới nhất & Thông minh nhất** |
| 5 | `DeepSeek-V3-0324` | Bản V3 cập nhật tháng 03/24 |
| 6 | `DeepSeek-V3.1` | Bản V3.1 cập nhật |
| 7 | `DeepSeek-V3.2` | Bản V3.2 cập nhật |
| 8 | **`DeepSeek-R1`** | **Bản Reasoning (Suy luận) tốt nhất** |
| 9 | `DeepSeek-R1-0528` | Bản R1 cập nhật tháng 05/28 |
| 10 | `DeepSeek-R1-Distill` | Bản R1 tối ưu (Rút gọn) |
| 11 | `DeepSeek-Prover-V1` | Chuyên chứng minh toán học |
| 12 | `DeepSeek-Prover-V1.5` | Bản nâng cấp của Prover |
| 13 | `DeepSeek-Prover-V2` | Bản Prover mới nhất |
| 14 | `DeepSeek-VL` | Vision Language (Đa phương thức) |
| 15 | `DeepSeek-Coder` | Chuyên lập trình V1 |
| 16 | **`DeepSeek-Coder-V2`** | **Bản lập trình tốt nhất (Coder V2)** |
| 17 | `DeepSeek-Coder-6.7B-base` | Bản Coder 6.7 tỷ tham số (Base) |
| 18 | `DeepSeek-Coder-6.7B-instruct` | Bản Coder 6.7 tỷ tham số (Instruct) |

---

## 💡 5. Mẹo khi sử dụng
- Nếu bạn không truyền tham số `"model"`, hệ thống sẽ mặc định dùng **`DeepSeek-V3`**.
- Đảm bảo bạn đang gọi qua giao thức **`https`** để được bảo mật tốt nhất.
- Nếu bạn nhận được lỗi **502 Bad Gateway**, vui lòng kiểm tra xem nguồn cấp dữ liệu AI có đang chặn IP của VPS bạn không.
