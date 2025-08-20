from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import requests
import json
from google_ai import call_gemini_api
from typing import Optional

app = FastAPI(title="Markdown to Excel API", description="API chuyển đổi file markdown thành file Excel")

# Thêm CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.get("/")
async def root():
    """Endpoint gốc để kiểm tra API hoạt động"""
    return {"message": "Markdown to Excel API đang hoạt động"}

    
@app.post("/convert-pdf-to-json")
async def convert_pdf_to_json(
    file: UploadFile = File(...),
    output_filename: Optional[str] = None
):
    """
    Nhận file PDF, tự động gọi API parse PDF sang markdown, rồi chuyển markdown sang Excel.
    """
    # 1. Lưu file PDF tạm thời
    temp_pdf_path = f"temp_{uuid.uuid4().hex}.pdf"
    with open(temp_pdf_path, "wb") as f:
        f.write(await file.read())

    try:
        # 2. Gọi API parse PDF sang markdown (url1)
        url1 = "http://192.168.10.171:8090/file_parse"
        name = os.path.splitext(os.path.basename(file.filename))[0]
        print(f"Đang xử lý file PDF: {name}")
        files = [
            ("files", (file.filename, open(temp_pdf_path, "rb"), "application/pdf")),
        ]
        data = {
            "output_dir": "./outputs",
            "lang_list": "en",
            "backend": "pipeline",
            "parse_method": "auto",
            "formula_enable": "true",
            "table_enable": "true",
            "server_url": "",
            "return_md": "true",
            "return_middle_json": "false",
            "return_model_output": "false",
            "return_content_list": "false",
            "return_images": "False",
            "start_page_id": "0",
            "end_page_id": "99999"
        }
        res1 = requests.post(url1, files=files, data=data)
        res1.raise_for_status()
        # Lấy key đầu tiên trong results (tên file có thể khác nhau)
        results = json.loads(res1.text)['results'][name]['md_content']
        if not results:
            raise HTTPException(status_code=422, detail="Không có kết quả trả về từ dịch vụ parse PDF")
        markdown_content = results

        # 3. Gọi hàm convert markdown sang Excel (giống /convert-markdown-to-excel)
        unique_id = str(uuid.uuid4())
        if output_filename:
            if not output_filename.endswith('.xlsx'):
                output_filename += '.xlsx'
        else:
            output_filename = f"{name}_{unique_id[:8]}.xlsx"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        data = call_gemini_api(markdown_content)
        
        # with open(output_path, "wb") as f:
        #     json.dump(data, f, ensure_ascii=False, indent=4)
        return JSONResponse(content=data)

    except Exception as e:
        print(f"Lỗi khi xử lý: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

@app.get("/health")
async def health_check():
    """Kiểm tra tình trạng hoạt động của API"""
    return {
        "status": "healthy",
        "message": "API đang hoạt động bình thường",
        "output_directory": OUTPUT_DIR,
        "output_dir_exists": os.path.exists(OUTPUT_DIR)
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Khởi động Markdown to Excel API...")
    print("📂 Thư mục output:", OUTPUT_DIR)
