from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import requests
import json
from pathlib import Path
from google_ai import call_gemini_api
from storage_service import upload_folder_to_s3, get_file_info, get_image_links
from typing import Optional
from excel_process import convert_history_json_to_excel_strict
from mineru.cli.common import convert_pdf_bytes_to_bytes_by_pypdfium2, prepare_env, read_fn
from mineru.data.data_reader_writer import FileBasedDataWriter
from mineru.utils.enum_class import MakeMode
from mineru.backend.pipeline.pipeline_analyze import doc_analyze as pipeline_doc_analyze
from mineru.backend.pipeline.pipeline_middle_json_mkcontent import union_make as pipeline_union_make
from mineru.backend.pipeline.model_json_to_middle_json import result_to_middle_json as pipeline_result_to_middle_json

MINERU_AVAILABLE = True
    

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

def do_parse_pdf(
    output_dir,
    pdf_file_names: list[str],
    pdf_bytes_list: list[bytes],
    p_lang_list: list[str],
    backend="pipeline",
    parse_method="auto",
    formula_enable=True,
    table_enable=True,
    server_url=None,
    f_dump_md=True,
    f_make_md_mode=None,
    start_page_id=0,
    end_page_id=None,
):
    """Hàm parse PDF sử dụng MinerU"""
    import copy
    
    if f_make_md_mode is None:
        f_make_md_mode = MakeMode.MM_MD
    
    if backend == "pipeline":
        for idx, pdf_bytes in enumerate(pdf_bytes_list):
            new_pdf_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(pdf_bytes, start_page_id, end_page_id)
            pdf_bytes_list[idx] = new_pdf_bytes

        infer_results, all_image_lists, all_pdf_docs, lang_list, ocr_enabled_list = pipeline_doc_analyze(
            pdf_bytes_list, p_lang_list, parse_method=parse_method, 
            formula_enable=formula_enable, table_enable=table_enable
        )

        for idx, model_list in enumerate(infer_results):
            pdf_file_name = pdf_file_names[idx]
            local_image_dir, local_md_dir = prepare_env(output_dir, pdf_file_name, parse_method)
            image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(local_md_dir)

            images_list = all_image_lists[idx]
            pdf_doc = all_pdf_docs[idx]
            _lang = lang_list[idx]
            _ocr_enable = ocr_enabled_list[idx]
            middle_json = pipeline_result_to_middle_json(
                model_list, images_list, pdf_doc, image_writer, _lang, _ocr_enable, formula_enable
            )

            pdf_info = middle_json["pdf_info"]

            if f_dump_md:
                image_dir = str(os.path.basename(local_image_dir))
                md_content_str = pipeline_union_make(pdf_info, f_make_md_mode, image_dir)
                md_writer.write_string(f"{pdf_file_name}.md", md_content_str)

            print(f"local output dir is {local_md_dir}")
            return local_md_dir  # Trả về đường dẫn để có thể đọc file markdown

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
        # 2. Xử lý PDF bằng MinerU (nếu có) hoặc gọi API
        name = os.path.splitext(os.path.basename(file.filename))[0]
        print(f"Đang xử lý file PDF: {name}")
        
        if MINERU_AVAILABLE:
            # Sử dụng MinerU trực tiếp
            print("📝 Sử dụng MinerU để parse PDF...")
            
            # Đọc bytes từ file PDF
            with open(temp_pdf_path, "rb") as f:
                pdf_bytes = f.read()
            
            # Chuẩn bị thư mục output
            outputs_dir = "./outputs"
            os.makedirs(outputs_dir, exist_ok=True)
            
            # Cấu hình cho MinerU
            pdf_file_names = [name]
            pdf_bytes_list = [pdf_bytes]
            p_lang_list = ["en"]
            
            # Gọi hàm parse PDF
            local_md_dir = do_parse_pdf(
                output_dir=outputs_dir,
                pdf_file_names=pdf_file_names,
                pdf_bytes_list=pdf_bytes_list,
                p_lang_list=p_lang_list,
                backend="pipeline",
                parse_method="auto",
                formula_enable=True,
                table_enable=True,
                server_url=None,
                f_dump_md=True,
                f_make_md_mode=MakeMode.MM_MD,
                start_page_id=0,
                end_page_id=None
            )
            
            # Đọc markdown đã được tạo
            md_file_path = os.path.join(local_md_dir, f"{name}.md")
            if os.path.exists(md_file_path):
                with open(md_file_path, "r", encoding="utf-8") as f:
                    markdown_content = f.read()
            else:
                raise HTTPException(status_code=500, detail="Không tìm thấy file markdown sau khi parse")
                
        else:
            # Fallback: sử dụng API như cũ
            print("📝 Sử dụng API để parse PDF...")
            url1 = "http://192.168.10.171:8090/file_parse"
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
                "return_images": "true",
                "start_page_id": "0",
                "end_page_id": "99999"
            }
            res1 = requests.post(url1, files=files, data=data)
            res1.raise_for_status()
            # upload_folder_to_s3(f"./{name}/auto/images", "audio_overview/images")

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

@app.post("/convert-pdf-to-excel")
async def convert_pdf_to_excel(
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
        upload_folder_to_s3(f"./{name}/auto/images", "audio_overview/images")
        links = get_image_links(f"./{name}/auto/images", "audio_overview/images")
        print(links)
        if not data:
            raise HTTPException(status_code=422, detail="Không thể xử lý nội dung file markdown")
        
        if output_filename:
            if not output_filename.endswith('.xlsx'):
                output_filename += '.xlsx'
        else:
            base_name = os.path.splitext(file.filename)[0]
            output_filename = f"{base_name}_{unique_id[:8]}.xlsx"
        
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
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
