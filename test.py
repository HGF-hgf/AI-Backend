import requests
import json

url1 = "http://192.168.10.171:8090/file_parse"

files = [
    ("files", ("data/de-cuoi-hoc-ky-2-toan-7-nam-2024-2025-phong-gddt-thu-dau-mot-binh-duong.pdf", open("data/de-cuoi-hoc-ky-2-toan-7-nam-2024-2025-phong-gddt-thu-dau-mot-binh-duong.pdf", "rb"), "image/jpeg")),
]

name = 'de-cuoi-hoc-ky-2-toan-7-nam-2024-2025-phong-gddt-thu-dau-mot-binh-duong'

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
markdown_content = json.loads(res1.text)['results'][name]['md_content']
with open(f"{name}.md", "w", encoding="utf-8") as f:
    f.write(markdown_content)
    
url2 = "http://0.0.0.0:8001/convert-markdown-to-excel"

res2 = requests.post(
    url2,
    # data={"output_filename": f"{name}.xlsx"},
    files={"file": ("./de-cuoi-hoc-ky-2-toan-7-nam-2024-2025-phong-gddt-thu-dau-mot-binh-duong.md", open("de-cuoi-hoc-ky-2-toan-7-nam-2024-2025-phong-gddt-thu-dau-mot-binh-duong.md", "rb"), "text/markdown")}
)

res2.raise_for_status()

print(f"✅ Done! File Excel đã được tạo: output/{name}.xlsx")