def get_prompt_kh(content):
    return """
Bạn là AI phân tích tài liệu để kiểm tra chính tả và trả về dữ liệu theo cấu trúc JSON theo cấu trúc tôi mô tả bên dưới
Đầu vào: Nội dung của tài liệu: """ + content + """
Đầu ra: Trả về danh sách các bài tập dưới dạng JSON như cấu trúc bên dưới.
## 📦 Cấu trúc JSON
### Các trường bắt buộc:
* **Question**: Chứa câu hỏi và các thông tin đề bài cung cấp để giải quyết bài tập
* **Question type**: Loại câu hỏi (là 1 trong 8 dạng sau: Multiple Choice, Checkbox, Essay, Fill In, True False, Matching 1 answer, Order items, Matching multi-answer)
* **image**: Nếu bài tập có chứa hình ảnh (dạng `![](path/to/image.jpg)` trong Markdown), hãy lấy chính đường dẫn hoặc base64 trong đó và đưa vào trường "image". 
  - Nếu nhiều ảnh liên quan thì `"image"` là một mảng các chuỗi.
  - Nếu không có ảnh thì `"image": ""`.
  
### ví dụ cấu trúc JSON:
```json
{
  "Question type": "Multiple Choice",
  "Question": "Cho phương trình $x^2 + 2x - 3 = 0$. Nghiệm của phương trình là:",
  "options": ["$x = 1$ hoặc $x = -3$", "$x = -1$ hoặc $x = 3$", "$x = 2$ hoặc $x = -1$", "$x = 0$ hoặc $x = 3$"],
  "answer": "1",
  "image": "",
  "explanation": "Giải phương trình bậc 2"
}
```

### ⚡ Quy tắc về công thức toán, lý, hóa:
**Tất cả các công thức toán, lý, hóa PHẢI được biểu diễn dưới dạng LaTeX chuẩn:**
- Sử dụng ký hiệu `$...$` cho công thức inline
- Sử dụng ký hiệu `$$...$$` cho công thức block/display
- Phải có khoảng trắng( dấu cách trước và sau công thức)
- Ví dụ: 
  * `$E = mc^2$` thay vì `E = mc²`
  * `$H_2SO_4$` thay vì `H₂SO₄`  
  * `$\frac{1}{2}mv^2$` thay vì `½mv²`
  * `$$\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$` cho công thức phức tạp

## 🔐 8 dạng bài tập cố định là:
1. Trắc nghiệm 1 đáp án (Multiple Choice)
2. Trắc nghiệm nhiều đáp án (Checkbox)
3. Tự luận (Essay)
4. Điền khuyết (Fill In)
5. Đúng sai (True False)
6. Nối 1 đáp án (Matching 1 answer)
7. Sắp xếp (Order items)
8. Nối nhiều đáp án (Matching multi-answer)

##  Ví dụ minh họa
### 1. Trắc nghiệm 1 đáp án (Multiple Choice)
```json
{
  "Question type": "Multiple Choice",
  "Question": "Cho phương trình $x^2 + 2x - 3 = 0$. Nghiệm của phương trình là:",
  "options": ["$x = 1$ hoặc $x = -3$", "$x = -1$ hoặc $x = 3$", "$x = 2$ hoặc $x = -1$", "$x = 0$ hoặc $x = 3$"],
  "answer": "1",
  "image1": "image1.png",
  "explanation": "Giải phương trình bậc 2"
}
```
---
### 2. Trắc nghiệm nhiều đáp án (Checkbox)

```json
{
  "Question type": "Checkbox",
  "Question": "Những chất nào sau đây là axit?",
  "options": ["$HCl$", "$NaOH$", "$H_2SO_4$", "$NH_3$"],
  "answers": [1, 3],
  "explanation": "$HCl$ và $H_2SO_4$ là các axit"
}
```
---
### 3. Tự luận (Essay)
```json
{
  "Question type": "Essay",
  "Question": "Tính động năng của vật có khối lượng $m = 2kg$ chuyển động với vận tốc $v = 10m/s$. Sử dụng công thức $E_k = \\frac{1}{2}mv^2$",
  "explanation": "Áp dụng công thức động năng"
}
```
---
### 4. Điền khuyết (Fill In)
```json
{
  "Question type": "Fill In",
  "Question": "Điền vào chỗ trống: Phương trình cân bằng của phản ứng đốt cháy metan: $CH_4 + __(1)__O_2 \\rightarrow __(2)__CO_2 + __(3)__H_2O$",
  "explanation": "Cân bằng phương trình hóa học"
}
```
---
### 5. Đúng sai (True/False)
```json
{
  "Question type": "True False",
  "Question": "Đánh giá các mệnh đề sau về công thức vật lý",
  "statements": [
    {"text": "Công thức tính vận tốc: $v = \\frac{s}{t}$", "answer": true},
    {"text": "Định luật Ohm: $U = I \\times R$", "answer": true},
    {"text": "Khối lượng riêng: $D = \\frac{V}{m}$", "answer": false},
    {"text": "Áp suất: $p = \\frac{F}{S}$", "answer": true}
  ],
  "explanation": "Kiến thức cơ bản về công thức vật lý"
}
```
---
### 6. Nối 1 đáp án (Matching 1 answer)

```json
{
  "Question type": "Matching 1 answer",
  "Question": "Nối công thức với đại lượng tương ứng",
  "left": ["$F = ma$", "$E = mc^2$", "$pV = nRT$"],
  "right": ["Định luật khí lý tưởng", "Định luật Newton 2", "Công thức Einstein"],
  "explanation": "Các công thức vật lý cơ bản"
}
```
---
### 7. Sắp xếp (Order items)

```json
{
  "Question type": "Order items",
  "Question": "Sắp xếp các bước giải phương trình $2x + 5 = 11$ theo thứ tự đúng",
  "items": ["$x = 3$", "$2x = 6$", "$2x + 5 = 11$", "$2x = 11 - 5$"],
  "correct_order": [3, 4, 2, 1],
  "explanation": "Các bước giải phương trình bậc nhất"
}
```
---
### 8. Nối nhiều đáp án (Matching multi-answer)

```json
{
  "Question type": "Matching multi-answer",
  "Question": "Nối các nguyên tố với công thức hợp chất tương ứng",
  "left": ["Natri", "Canxi", "Nhôm", "Sắt"],
  "right": ["$NaCl$", "$CaO$", "$Al_2O_3$", "$Fe_2O_3$", "$NaOH$", "$Ca(OH)_2$", "$AlCl_3$", "$FeCl_3$"],
  "explanation": "Các hợp chất của kim loại"
}
```

## Quy tắc xử lý
1. **Chỉ trích xuất bài tập**, **không lấy phần lý thuyết** hoặc nội dung mô tả không yêu cầu học sinh trả lời.
2. **Với tất cả các dạng câu hỏi (trừ `Essay` và `Fill In`)**:
   * **Phải có đầy đủ tất cả các lựa chọn đáp án như trong đề bài**
   * **Phải có ít nhất một đáp án đúng**
   * **Không được tự bổ sung thêm lựa chọn**
   * Ở mỗi câu hỏi trắc nghiệm: Phần Question chỉ chứa câu hỏi k chứa đáp án. đáp án sẽ chứa ở trong options( buộc phải có nếu là Checkbox hoặc Multiple Choice). Và hãy đưa ra đáp án là(1,2,3,4,5,6) ở trường answer tương ứng với lựa chọn đúng
3. **QUAN TRỌNG - Xử lý công thức toán, lý, hóa:**
   * **TẤT CẢ** các công thức, ký hiệu hóa học, biểu thức toán học PHẢI được viết dưới dạng LaTeX
   * Sử dụng `$...$` cho công thức inline trong câu
   * Sử dụng `$$...$$` cho công thức độc lập/display
   * Các ký hiệu đặc biệt: `^` (mũ), `_` (chỉ số dưới), `\frac{}{}` (phân số), `\sqrt{}` (căn), `\rightarrow` (mũi tên), v.v.
   * Nhớ phải có khoảng trắng( dấu cách trước và sau công thức); sử dụng dấu . cho dấu phân cách thập phân. Tránh in nhầm định dạng
5. **Không cần giải thích hoặc phân tích.**
   → **Chỉ trả về kết quả ở dạng JSON thuần túy**, không thêm ghi chú.
6. Nếu trong ảnh không có bài tập nào → trả về:
   ```json
   []
   ```
7. Đối với dạng **Fill In (Điền khuyết)**:
   * Các vị trí cần điền đáp án **phải được đánh dấu bằng `__(1)__` (mỗi bên 2 gạch dưới)**
   *  **Không dùng `...`, `(...)` hay ký hiệu khác**
8. **Phân biệt rõ hai dạng câu hỏi nối (`Matching`)**:
   * `Matching 1 answer`: Khi mỗi mục ở cột trái chỉ nối với 1 đáp án, và hai cột có số lượng phần tử bằng nhau
   * `Matching multi-answer`: Khi mỗi mục có thể nối với nhiều đáp án, hoặc hai cột có số lượng phần tử không bằng nhau
   **Không được nhầm giữa hai dạng này.**
9. **TUYỆT ĐỐI KHÔNG ĐƯỢC BỎ SÓT BÀI NÀO trong phần tài liệu tôi gửi**
   → Nếu trong ảnh có bài tập thì phải trích xuất được đúng toàn bộ bài tập. Không được phép bỏ sót bất kỳ bài nào
10. Sửa lỗi chính tả trong nội dung câu hỏi, đáp án nếu có.
11. Nếu bài tập có chứa ảnh được nhúng trong Markdown bằng cú pháp `![](url hoặc data:image...)`:
    * Trích xuất chính xác nội dung trong ngoặc tròn (URL hoặc chuỗi base64).
    * Lưu vào trường `"image"`.
    * Nếu nhiều ảnh thì đưa vào mảng `"image": ["img1", "img2", ...]`.
    * Nếu không có ảnh thì `"image": ""`.
"""


def get_prompt_van(content):
    return """
  Bạn là AI phân tích tài liệu để kiểm tra chính tả và trả về dữ liệu theo cấu trúc JSON theo cấu trúc tôi mô tả bên dưới
Đầu vào: Nội dung của tài liệu: """ + content + """
Đầu ra: Trả về danh sách các bài tập dưới dạng JSON như cấu trúc bên dưới.
## 📦 Cấu trúc JSON
### Các trường bắt buộc:
* **Question**: Chứa câu hỏi và các thông tin đề bài cung cấp để giải quyết bài tập
* **Question type**: Loại câu hỏi (là 1 trong 8 dạng sau: Multiple Choice, Checkbox, Essay, Fill In, True False, Matching 1 answer, Order items, Matching multi-answer)
* **image**: Nếu bài tập có chứa hình ảnh (dạng `![](path/to/image.jpg)` trong Markdown), hãy lấy chính đường dẫn hoặc base64 trong đó và đưa vào trường "image". 
  - Nếu nhiều ảnh liên quan thì `"image"` là một mảng các chuỗi.
  - Nếu không có ảnh thì `"image": ""`.
  
### ví dụ cấu trúc JSON:
```json
{
  "Question type": "Multiple Choice",
  "Question": "Cho phương trình $x^2 + 2x - 3 = 0$. Nghiệm của phương trình là:",
  "options": ["$x = 1$ hoặc $x = -3$", "$x = -1$ hoặc $x = 3$", "$x = 2$ hoặc $x = -1$", "$x = 0$ hoặc $x = 3$"],
  "answer": "1",
  "image": "",
  "explanation": "Giải phương trình bậc 2"
}
```

### ⚡ Quy tắc về công thức toán, lý, hóa:
**Tất cả các công thức toán, lý, hóa PHẢI được biểu diễn dưới dạng LaTeX chuẩn:**
- Sử dụng ký hiệu `$...$` cho công thức inline
- Sử dụng ký hiệu `$$...$$` cho công thức block/display
- Phải có khoảng trắng( dấu cách trước và sau công thức)
- Ví dụ: 
  * `$E = mc^2$` thay vì `E = mc²`
  * `$H_2SO_4$` thay vì `H₂SO₄`  
  * `$\frac{1}{2}mv^2$` thay vì `½mv²`
  * `$$\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$` cho công thức phức tạp

## 🔐 8 dạng bài tập cố định là:
1. Trắc nghiệm 1 đáp án (Multiple Choice)
2. Trắc nghiệm nhiều đáp án (Checkbox)
3. Tự luận (Essay)
4. Điền khuyết (Fill In)
5. Đúng sai (True False)
6. Nối 1 đáp án (Matching 1 answer)
7. Sắp xếp (Order items)
8. Nối nhiều đáp án (Matching multi-answer)

##  Ví dụ minh họa
### 1. Trắc nghiệm 1 đáp án (Multiple Choice)
```json
{
  "Question type": "Multiple Choice",
  "Question": "Cho phương trình $x^2 + 2x - 3 = 0$. Nghiệm của phương trình là:",
  "options": ["$x = 1$ hoặc $x = -3$", "$x = -1$ hoặc $x = 3$", "$x = 2$ hoặc $x = -1$", "$x = 0$ hoặc $x = 3$"],
  "answer": "1",
  "image1": "image1.png",
  "explanation": "Giải phương trình bậc 2"
}
```
---
### 2. Trắc nghiệm nhiều đáp án (Checkbox)

```json
{
  "Question type": "Checkbox",
  "Question": "Những chất nào sau đây là axit?",
  "options": ["$HCl$", "$NaOH$", "$H_2SO_4$", "$NH_3$"],
  "answers": [1, 3],
  "explanation": "$HCl$ và $H_2SO_4$ là các axit"
}
```
---
### 3. Tự luận (Essay)
```json
{
  "Question type": "Essay",
  "Question": "Tính động năng của vật có khối lượng $m = 2kg$ chuyển động với vận tốc $v = 10m/s$. Sử dụng công thức $E_k = \\frac{1}{2}mv^2$",
  "explanation": "Áp dụng công thức động năng"
}
```
---
### 4. Điền khuyết (Fill In)
```json
{
  "Question type": "Fill In",
  "Question": "Điền vào chỗ trống: Phương trình cân bằng của phản ứng đốt cháy metan: $CH_4 + __(1)__O_2 \\rightarrow __(2)__CO_2 + __(3)__H_2O$",
  "explanation": "Cân bằng phương trình hóa học"
}
```
---
### 5. Đúng sai (True/False)
```json
{
  "Question type": "True False",
  "Question": "Đánh giá các mệnh đề sau về công thức vật lý",
  "statements": [
    {"text": "Công thức tính vận tốc: $v = \\frac{s}{t}$", "answer": true},
    {"text": "Định luật Ohm: $U = I \\times R$", "answer": true},
    {"text": "Khối lượng riêng: $D = \\frac{V}{m}$", "answer": false},
    {"text": "Áp suất: $p = \\frac{F}{S}$", "answer": true}
  ],
  "explanation": "Kiến thức cơ bản về công thức vật lý"
}
```
---
### 6. Nối 1 đáp án (Matching 1 answer)

```json
{
  "Question type": "Matching 1 answer",
  "Question": "Nối công thức với đại lượng tương ứng",
  "left": ["$F = ma$", "$E = mc^2$", "$pV = nRT$"],
  "right": ["Định luật khí lý tưởng", "Định luật Newton 2", "Công thức Einstein"],
  "explanation": "Các công thức vật lý cơ bản"
}
```
---
### 7. Sắp xếp (Order items)

```json
{
  "Question type": "Order items",
  "Question": "Sắp xếp các bước giải phương trình $2x + 5 = 11$ theo thứ tự đúng",
  "items": ["$x = 3$", "$2x = 6$", "$2x + 5 = 11$", "$2x = 11 - 5$"],
  "correct_order": [3, 4, 2, 1],
  "explanation": "Các bước giải phương trình bậc nhất"
}
```
---
### 8. Nối nhiều đáp án (Matching multi-answer)

```json
{
  "Question type": "Matching multi-answer",
  "Question": "Nối các nguyên tố với công thức hợp chất tương ứng",
  "left": ["Natri", "Canxi", "Nhôm", "Sắt"],
  "right": ["$NaCl$", "$CaO$", "$Al_2O_3$", "$Fe_2O_3$", "$NaOH$", "$Ca(OH)_2$", "$AlCl_3$", "$FeCl_3$"],
  "explanation": "Các hợp chất của kim loại"
}
```

## Quy tắc xử lý
1. **Chỉ trích xuất bài tập**, **không lấy phần lý thuyết** hoặc nội dung mô tả không yêu cầu học sinh trả lời.
2. **Với tất cả các dạng câu hỏi (trừ `Essay` và `Fill In`)**:
   * **Phải có đầy đủ tất cả các lựa chọn đáp án như trong đề bài**
   * **Phải có ít nhất một đáp án đúng**
   * **Không được tự bổ sung thêm lựa chọn**
   * Ở mỗi câu hỏi trắc nghiệm: Phần Question chỉ chứa câu hỏi k chứa đáp án. đáp án sẽ chứa ở trong options( buộc phải có nếu là Checkbox hoặc Multiple Choice). Và hãy đưa ra đáp án là(1,2,3,4,5,6) ở trường answer tương ứng với lựa chọn đúng
3. **QUAN TRỌNG - Xử lý công thức toán, lý, hóa:**
   * **TẤT CẢ** các công thức, ký hiệu hóa học, biểu thức toán học PHẢI được viết dưới dạng LaTeX
   * Sử dụng `$...$` cho công thức inline trong câu
   * Sử dụng `$$...$$` cho công thức độc lập/display
   * Các ký hiệu đặc biệt: `^` (mũ), `_` (chỉ số dưới), `\frac{}{}` (phân số), `\sqrt{}` (căn), `\rightarrow` (mũi tên), v.v.
   * Nhớ phải có khoảng trắng( dấu cách trước và sau công thức); sử dụng dấu . cho dấu phân cách thập phân. Tránh in nhầm định dạng
5. **Không cần giải thích hoặc phân tích.**
   → **Chỉ trả về kết quả ở dạng JSON thuần túy**, không thêm ghi chú.
6. Nếu trong ảnh không có bài tập nào → trả về:
   ```json
   []
   ```
7. Đối với dạng **Fill In (Điền khuyết)**:
   * Các vị trí cần điền đáp án **phải được đánh dấu bằng `__(1)__` (mỗi bên 2 gạch dưới)**
   *  **Không dùng `...`, `(...)` hay ký hiệu khác**
8. **Phân biệt rõ hai dạng câu hỏi nối (`Matching`)**:
   * `Matching 1 answer`: Khi mỗi mục ở cột trái chỉ nối với 1 đáp án, và hai cột có số lượng phần tử bằng nhau
   * `Matching multi-answer`: Khi mỗi mục có thể nối với nhiều đáp án, hoặc hai cột có số lượng phần tử không bằng nhau
   **Không được nhầm giữa hai dạng này.**
9. **TUYỆT ĐỐI KHÔNG ĐƯỢC BỎ SÓT BÀI NÀO trong phần tài liệu tôi gửi**
   → Nếu trong ảnh có bài tập thì phải trích xuất được đúng toàn bộ bài tập. Không được phép bỏ sót bất kỳ bài nào
10. Sửa lỗi chính tả trong nội dung câu hỏi, đáp án nếu có.
11. Nếu bài tập có chứa ảnh được nhúng trong Markdown bằng cú pháp `![](url hoặc data:image...)`:
    * Trích xuất chính xác nội dung trong ngoặc tròn (URL hoặc chuỗi base64).
    * Lưu vào trường `"image"`.
    * Nếu nhiều ảnh thì đưa vào mảng `"image": ["img1", "img2", ...]`.
    * Nếu không có ảnh thì `"image": ""`.
"""