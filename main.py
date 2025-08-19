from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from google_ai import call_gemini_api
from excel_process import convert_history_json_to_excel_strict
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

@app.post("/convert-markdown-to-excel")
async def convert_markdown_to_excel(
    file: UploadFile = File(...),
    output_filename: Optional[str] = None
):
    """
    API chuyển đổi file markdown thành file Excel
    
    Args:
        file: File markdown upload
        output_filename: Tên file Excel đầu ra (tùy chọn)
    
    Returns:
        File Excel đã được tạo
    """
    
    if not file.filename.endswith('.md'):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file .md")
    
    try:
        unique_id = str(uuid.uuid4())
        
        content = await file.read()
        content_str = content.decode('utf-8')
        
        print(f"Đang xử lý file: {file.filename}")
        data = call_gemini_api(content_str)
        
        if not data:
            raise HTTPException(status_code=422, detail="Không thể xử lý nội dung file markdown")
        
        if output_filename:
            if not output_filename.endswith('.xlsx'):
                output_filename += '.xlsx'
        else:
            base_name = os.path.splitext(file.filename)[0]
            output_filename = f"{base_name}_{unique_id[:8]}.xlsx"
        
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        convert_history_json_to_excel_strict(data, output_path=output_path)
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Lỗi khi tạo file Excel")
        
        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"Lỗi khi xử lý: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

@app.post("/convert-markdown-content-to-excel")
async def convert_markdown_content_to_excel(
    content: dict,
    output_filename: Optional[str] = None
):
    """
    API chuyển đổi nội dung markdown (dạng text) thành file Excel
    
    Args:
        content: Dict chứa nội dung markdown trong trường 'text'
        output_filename: Tên file Excel đầu ra (tùy chọn)
    
    Returns:
        File Excel đã được tạo
    """
    
    if 'text' not in content:
        raise HTTPException(status_code=400, detail="Thiếu trường 'text' trong request body")
    
    try:
        unique_id = str(uuid.uuid4())
        
        content_str = content['text']
        
        print("Đang xử lý nội dung markdown...")
        data = call_gemini_api(content_str)
        
        if not data:
            raise HTTPException(status_code=422, detail="Không thể xử lý nội dung markdown")
        
        if output_filename:
            if not output_filename.endswith('.xlsx'):
                output_filename += '.xlsx'
        else:
            output_filename = f"converted_{unique_id[:8]}.xlsx"
        
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        convert_history_json_to_excel_strict(data, output_path=output_path)
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Lỗi khi tạo file Excel")
        
        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"Lỗi khi xử lý: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

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
