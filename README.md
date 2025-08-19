# Markdown to Excel API

API FastAPI để chuyển đổi file markdown thành file Excel sử dụng Google Gemini AI.

## Cài đặt

1. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

2. Tạo file `.env` từ `.env.example` và cấu hình:
```bash
cp .env.example .env
```

3. Thêm GEMINI_API_KEY vào file `.env`:
```
GEMINI_API_KEY=your_actual_api_key_here
```

## Chạy ứng dụng

```bash
python main.py
```

Hoặc:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API sẽ chạy tại: http://localhost:8000

## Endpoints

### 1. `POST /convert-markdown-to-excel`
Chuyển đổi file markdown thành file Excel

**Parameters:**
- `file`: File markdown (.md) để upload
- `output_filename` (optional): Tên file Excel đầu ra

**Response:** File Excel download

**Ví dụ sử dụng với curl:**
```bash
curl -X POST "http://localhost:8000/convert-markdown-to-excel" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_file.md" \
     -F "output_filename=result.xlsx" \
     --output result.xlsx
```

### 2. `POST /convert-markdown-content-to-excel`
Chuyển đổi nội dung markdown (text) thành file Excel

**Request Body:**
```json
{
  "text": "# Markdown content here\n\nYour markdown content..."
}
```

**Response:** File Excel download

**Ví dụ sử dụng với curl:**
```bash
curl -X POST "http://localhost:8000/convert-markdown-content-to-excel" \
     -H "Content-Type: application/json" \
     -d '{"text": "# Markdown content\n\nYour content here"}' \
     --output result.xlsx
```

### 3. `POST /convert-from-api-to-excel`
Gọi API khác để lấy file markdown, sau đó chuyển đổi thành file Excel

**Request Body:**
```json
{
  "url": "http://example.com/api/endpoint",
  "method": "GET",
  "headers": {
    "Authorization": "Bearer token",
    "Content-Type": "application/json"
  },
  "params": {
    "param1": "value1"
  },
  "data": {
    "key": "value"
  }
}
```

**Các trường:**
- `url` (bắt buộc): URL của API cần gọi
- `method` (tùy chọn): GET hoặc POST, mặc định là GET
- `headers` (tùy chọn): Headers cho request
- `params` (tùy chọn): Query parameters cho GET request
- `data` (tùy chọn): Body data cho POST request

**Response:** File Excel download

**Ví dụ sử dụng với curl:**
```bash
curl -X POST "http://localhost:8000/convert-from-api-to-excel" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "http://your-api.com/markdown",
       "method": "GET",
       "headers": {"Authorization": "Bearer your-token"}
     }' \
     --output result.xlsx
```

### 4. `GET /process-demo`
Xử lý file markdown demo (dựa trên đoạn code mẫu)

**Response:** JSON thông tin kết quả

### 5. `GET /health`
Kiểm tra tình trạng hoạt động của API

### 6. `GET /`
Endpoint gốc để kiểm tra API

## Cấu trúc thư mục

```
.
├── main.py              # File chính FastAPI
├── google_ai.py         # Module xử lý Gemini AI
├── excel_process.py     # Module chuyển đổi sang Excel
├── base_prompt.py       # Module chứa prompt templates
├── requirements.txt     # Danh sách thư viện
├── .env.example        # File cấu hình mẫu
├── output/             # Thư mục chứa file Excel đầu ra
└── README.md           # File hướng dẫn này
```

## Cách hoạt động

1. **Upload file markdown** hoặc gửi nội dung markdown
2. **Xử lý với Gemini AI**: Nội dung markdown được gửi đến Google Gemini API để trích xuất và cấu trúc hóa thông tin
3. **Chuyển đổi sang Excel**: Dữ liệu JSON từ Gemini được chuyển đổi thành file Excel theo định dạng đã cấu hình
4. **Download file Excel**: API trả về file Excel đã được tạo

## Lưu ý

- Đảm bảo có kết nối internet để gọi Gemini API
- File Excel đầu ra sẽ được lưu trong thư mục `output/`
- API hỗ trợ CORS cho tất cả origin (trong production nên hạn chế)
- Cần GEMINI_API_KEY hợp lệ để sử dụng

## Swagger UI

Truy cập http://localhost:8000/docs để xem giao diện Swagger UI và test API trực tiếp.
