import google.generativeai as genai
import json
import re
import os
from base_prompt import get_prompt
from dotenv import load_dotenv

load_dotenv()

def fix_json_with_gemini(broken_json_string):
    """
    Gọi Gemini API để sửa JSON bị lỗi
    """
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    fix_prompt = f"""
    Bạn là chuyên gia sửa lỗi JSON.

    Tôi có một đoạn JSON bị lỗi cú pháp. Hãy sửa lại để JSON trở nên hợp lệ 100% theo chuẩn RFC 8259.

    ⚠️ Một số lỗi thường gặp có thể bao gồm (nhưng không giới hạn):
    - Dấu ngoặc kép (") không được escape đúng
    - Dấu gạch chéo ngược (\\) dư hoặc thiếu
    - Thiếu dấu phẩy, thiếu hoặc sai ngoặc

    🎯 Yêu cầu:
    1. Sửa tất cả lỗi cú pháp để đoạn JSON hợp lệ.
    2. Không thay đổi nội dung các giá trị – chỉ điều chỉnh cú pháp.
    3. Escape các dấu ngoặc kép trong chuỗi bằng `\"` đúng chuẩn.
    4. Trả về duy nhất đoạn JSON đã được sửa, bọc trong thẻ code ```json```. Không thêm lời giải thích hay bình luận nào.

    🔧 JSON bị lỗi:

    {broken_json_string}

"""
    
    try:
        response = model.generate_content(fix_prompt)
        part = response.candidates[0].content.parts[0]
        if hasattr(part, 'text') and isinstance(part.text, str):
            result_text = part.text
            print("Gemini fix JSON response:", result_text[:200] + "...")
            
            # Tìm JSON trong response
            match = re.search(r"```json\s*([\s\S]+?)\s*```", result_text)
            if match:
                fixed_json_string = match.group(1)
            else:
                # Loại bỏ mọi dấu ``` và khoảng trắng
                fixed_json_string = result_text.replace('```json', '').replace('```', '').strip()
            
            return fixed_json_string
        else:
            print("Lỗi khi fix JSON:", part.text if hasattr(part, 'text') else "No text")
            return None
    except Exception as e:
        print(f"Exception khi fix JSON: {e}")
        return None

def call_gemini_api(content):
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = get_prompt(content)
    response = model.generate_content(prompt)
    try:
        part = response.candidates[0].content.parts[0]
        if hasattr(part, 'text') and isinstance(part.text, str):
            result_text = part.text
            print("Gemini text:", result_text)
            match = re.search(r"```json\s*([\s\S]+?)\s*```", result_text)
            if match:
                json_string = match.group(1)
            else:
                # Loại bỏ mọi dấu ``` và khoảng trắng
                json_string = result_text.replace('```json', '').replace('```', '').strip()
            
            # Thử parse JSON
            try:
                json_string = json_string.replace('“', '"').replace('”', '"').replace("’", "'")
                return json.loads(json_string)
            except json.JSONDecodeError as json_err:
                print(f"JSON Parse Error: {json_err}")
                print("Đang thử sửa JSON bằng Gemini...")
                
                # Thử fix JSON tối đa 3 lần
                current_json_string = json_string +"Lỗi được thông báo:" + str(json_err)
                max_fix_attempts = 3
                
                for fix_attempt in range(1, max_fix_attempts + 1):
                    print(f"🔧 Lần fix thứ {fix_attempt}/{max_fix_attempts}")
                    
                    fixed_json_string = fix_json_with_gemini(current_json_string)
                    if fixed_json_string:
                        try:
                            json_string = json_string.replace('“', '"').replace('”', '"').replace("’", "'")
                            fixed_data = json.loads(fixed_json_string)
                            print(f"✅ Đã sửa JSON thành công sau {fix_attempt} lần thử!")
                            return fixed_data
                        except json.JSONDecodeError as fix_err:
                            print(f"❌ Lần fix {fix_attempt} vẫn lỗi: {fix_err}")
                            if fix_attempt < max_fix_attempts:
                                print(f"🔄 Thử fix lại lần {fix_attempt + 1}...")
                                current_json_string = fixed_json_string +"Lỗi được thông báo:"+ str(fix_err)  # Dùng JSON đã fix làm input cho lần tiếp theo
                            else:
                                print(f"❌ Đã thử fix {max_fix_attempts} lần nhưng vẫn lỗi")
                                return []
                    else:
                        print(f"❌ Không thể sửa JSON ở lần {fix_attempt}")
                        return []
                
                return []
                    
        else:
            print("Lỗi. response", part.text if hasattr(part, 'text') else "No text")
            return []
    except Exception as e:
        print('Gemini response error:', response)
        print('Exception:', e)
        return []