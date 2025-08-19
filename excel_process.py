import os
import json
import google.generativeai as genai
import re
from pdf2image import convert_from_path
import os
import os
import pandas as pd
import json

def convert_history_json_to_excel_strict(data, output_path="CÁCH MẠNG CÔNG NGHIỆP(NỬA SAU THẾ KỈ XVIII – GIỮA THẾ KỈ XIX).xlsx"):
    columns = [
    'Câu hỏi', 'Loại câu hỏi', 'Độ khó (Mặc định: Nhận biết)', 'Trộn lựa chọn (Mặc định: Có)',
    *[f"Lựa chọn {i}" for i in range(1, 11)],
    'Đáp án', 'Đúng', 'Sai',
    # So le Vế trái - Vế phải
    *[col for i in range(1, 11) for col in (f"Vế trái {i}", f"Vế phải {i}")],
    *[f"Cột trái {i}" for i in range(1, 11)],
    *[f"Cột phải {i}" for i in range(1, 11)],
    'Đáp án nối', 'Giải thích', "Ảnh minh họa"
]


    header_descriptions = {
        "Câu hỏi": "(Question)",
        "Loại câu hỏi": "(Question type)",
        "Độ khó (Mặc định: Nhận biết)": "(Difficulty level (Default: Remembering))",
        "Trộn lựa chọn (Mặc định: Có)": "(Shuffle choice (Default: Yes))",
        "Đáp án": "(Answers)",
        "Đúng": "(True)",
        "Sai": "(False)",
        "Đáp án nối": "(Match answer)",
        "Giải thích": "(Explain)",
        "Ảnh minh họa": "(Image)"
    }
    for i in range(1, 11):
        header_descriptions[f"Lựa chọn {i}"] = f"(Choice {i})"
        header_descriptions[f"Vế trái {i}"] = f"(Left Column {i})"
        header_descriptions[f"Vế phải {i}"] = f"(Right Column {i})"
        header_descriptions[f"Cột trái {i}"] = f"(Left column {i})"
        header_descriptions[f"Cột phải {i}"] = f"(Right column {i})"

    rows = []

    def get_type_label(qtype):
        mapping = {
            "multiple_choice": "Trắc nghiệm 1 đáp án (Multiple Choice)",
            "checkbox": "Trắc nghiệm nhiều đáp án (Checkbox)",
            "essay": "Tự luận (Essay)",
            "fill_in_blank": "Điền khuyết (Fill In)",
            "true_false": "Đúng sai (True False)",
            "matching_single": "Nối 1 đáp án (Matching 1 answer)",
            "matching_multiple": "Nối nhiều đáp án (Matching multi-answer)",
            "ordering": "Sắp xếp (Order items)",
            "Order items": "Sắp xếp (Order items)",
            "Matching multi-answer": "Nối nhiều đáp án (Matching multi-answer)",
            "Matching 1 answer": "Nối 1 đáp án (Matching 1 answer)",
            "True False": "Đúng sai (True False)",
            "Fill In": "Điền khuyết (Fill In)",
            "Essay": "Tự luận (Essay)",
            "Multiple Choice": "Trắc nghiệm 1 đáp án (Multiple Choice)",
            "image": "Ảnh minh họa (Image)"
        }
        return mapping.get(qtype.strip(), qtype)

    for item in data:
        row = {col: "" for col in columns}
        row["Câu hỏi"] = item.get("Question", "")
        row["Loại câu hỏi"] = get_type_label(item.get("Question type", ""))
        row["Độ khó (Mặc định: Nhận biết)"] = item.get("Difficulty level", "Nhận biết (Remembering)")
        row["Trộn lựa chọn (Mặc định: Có)"] = "Có (Yes)"
        row["Ảnh minh họa"] = item.get("image", "")
        
        qtype = item.get("Question type")

        if qtype == "Multiple Choice":
            ab = item.get("answer", 1)
            # Xử lý trường hợp ab là None hoặc empty string
            if ab is None or ab == "":
                row["Đáp án"] = 1
            else:
                try:
                    row["Đáp án"] = int(ab)
                except (ValueError, TypeError):
                    row["Đáp án"] = 1
            
            options = item.get("options")
            if not options:
                for i in range(1, 5):
                    row[f"Lựa chọn {i}"] = "lỗi không lấy được đáp án"
            else:
                for i, opt in enumerate(options):
                    if opt:
                        row[f"Lựa chọn {i+1}"] = opt
                    else:
                        for j in range(i+1, 5):
                            row[f"Lựa chọn {j}"] = "lỗi không lấy được đáp án"
                        break


        if qtype == "Checkbox":
            ab = ",".join(map(str, item.get("answer", [1, 2, 3])))
            row["Loại câu hỏi"] = "Trắc nghiệm nhiều đáp án (Checkbox)"
            # Xử lý trường hợp ab là None hoặc empty string
            if ab is None or ab == "":
                row["Đáp án"] = "1, 2, 3"
            else:
                try:
                    row["Đáp án"] = ab
                except (ValueError, TypeError):
                    row["Đáp án"] = "1, 2, 3"
            
            options = item.get("options")
            if not options:
                for i in range(1, 5):
                    row[f"Lựa chọn {i}"] = "lỗi không lấy được đáp án"
            else:
                for i, opt in enumerate(options):
                    if opt:
                        row[f"Lựa chọn {i+1}"] = opt
                    else:
                        for j in range(i+1, 5):
                            row[f"Lựa chọn {j}"] = "lỗi không lấy được đáp án"
                        break

        elif qtype == "True False":
            dung_list = []
            sai_list = []
            
            for idx, statement in enumerate(item.get("statements", []), start=1):
                if statement.get("answer", False):
                    dung_list.append(str(idx))
                else:
                    sai_list.append(str(idx))
            
            row["Đúng"] = ",".join(dung_list)
            row["Sai"] = ",".join(sai_list)

            for i, st in enumerate(item.get("statements", [])):
                row[f"Lựa chọn {i+1}"] = st["text"]

        elif qtype == "Fill In":
            # row["Giải thích"] = item.get("explanation", "")
            row["Giải thích"] = ""

        elif qtype == "Essay":
            # row["Giải thích"] = item.get("explanation", "")
            row["Giải thích"] = ""

        elif qtype == "Order items":
            
            for i, item_text in enumerate(item.get("items", [])):
                row[f"Lựa chọn {i+1}"] = item_text

        elif qtype == "Matching 1 answer" or qtype == "Matching multi-answer":
            if len(item.get("right", [])) == len(item.get("left", [])):
                # print(len(item.get("right", [])), len(item.get("left", [])))
                row["Loại câu hỏi"] = "Nối 1 đáp án (Matching 1 answer)"
                for i, (left, right) in enumerate(zip(item.get("left", []), item.get("right", []))):
                    row[f"Vế trái {i+1}"] = left
                    row[f"Vế phải {i+1}"] = right
            else:
                row["Loại câu hỏi"] = "Nối nhiều đáp án (Matching multi-answer)"
                for i, left in enumerate(item.get("left", [])):
                    row[f"Cột trái {i+1}"] = left
                for i, right in enumerate(item.get("right", [])):
                    row[f"Cột phải {i+1}"] = right
            if "match" in item:
                row["Đáp án nối"] = "\\n".join([f"{k} -> {v}" for k, v in item["match"].items()])

        rows.append(row)

    df = pd.DataFrame(rows, columns=columns)

    df_with_header = pd.concat([
        pd.DataFrame([header_descriptions], columns=columns),
        df
    ], ignore_index=True)

    df_with_header.to_excel(output_path, index=False)
    print(f" File Excel đã được tạo tại: {output_path}")








