import os
import re

def pdf_to_concatenated_images(pdf_path, k, output_dir='images/concat', temp_image_dir='images', start=None, end=None):
    import fitz
    from PIL import Image
    if os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            file_path = os.path.join(output_dir, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        os.makedirs(output_dir)
    if os.path.exists(temp_image_dir):
        for f in os.listdir(temp_image_dir):
            file_path = os.path.join(temp_image_dir, f)
            if os.path.isfile(file_path) and f.endswith('.png'):
                os.remove(file_path)
    else:
        os.makedirs(temp_image_dir)
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    # Determine start and end page indices
    page_start = start-1 if start is not None else 0
    page_end = end if end is not None else total_pages
    page_end = min(page_end, total_pages)
    for page_num in range(page_start, page_end):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        image_path = os.path.join(temp_image_dir, f'image_{page_num + 1}.png')
        pix.save(image_path)
    doc.close()
    def extract_page_num(filename):
        match = re.search(r'image_(\d+)\.png', filename)
        return int(match.group(1)) if match else 0
    image_files = [f for f in os.listdir(temp_image_dir) if f.endswith('.png')]
    image_files_sorted = sorted(image_files, key=extract_page_num)
    image_paths = [os.path.join(temp_image_dir, f) for f in image_files_sorted]
    def concatenate_images_vertical(image_paths):
        images = []
        try:
            # Mở từng ảnh bằng context manager để đảm bảo đóng file sau khi dùng
            for img_path in image_paths:
                img = Image.open(img_path)
                images.append(img.copy())  # copy dữ liệu ảnh vào RAM
                img.close()  # đóng file ngay sau khi copy
            total_height = sum(img.height for img in images)
            max_width = max(img.width for img in images)
            new_image = Image.new('RGB', (max_width, total_height))
            y_offset = 0
            for img in images:
                new_image.paste(img, (0, y_offset))
                y_offset += img.height
            return new_image
        finally:
            for img in images:
                if hasattr(img, 'close'):
                    img.close()
    for i in range(0, len(image_paths), k):
        batch = image_paths[i:i+k]
        concat_img = concatenate_images_vertical(batch)
        out_path = os.path.join(output_dir, f'concat_{i//k+1}.png')
        concat_img.save(out_path)
        print(f'Đã lưu ảnh ghép: {out_path}')
    for f in os.listdir(temp_image_dir):
        file_path = os.path.join(temp_image_dir, f)
        if os.path.isfile(file_path) and f.endswith('.png'):
            os.remove(file_path)