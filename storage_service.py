import boto3
import os
import mimetypes
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# Load and validate required environment variables
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_REGION = os.getenv("R2_REGION", "auto")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
S3_BASE_URL = os.getenv("S3_BASE_URL")

if not all([R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, S3_BASE_URL]):
    raise EnvironmentError(
        "Missing one or more required R2 environment variables.")

# Setup S3 (R2-compatible) client
s3_client = boto3.client(
    service_name="s3",
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name=R2_REGION,
)


def upload_folder_to_s3(local_folder, s3_folder):
    bucket = os.environ.get("R2_BUCKET_NAME")
    print(f"[DEBUG] Đã khởi tạo S3 client, bắt đầu upload các file trong {local_folder}")
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            # Đường dẫn trên S3 (giữ cấu trúc thư mục con)
            relative_path = os.path.relpath(local_path, local_folder)
            s3_key = os.path.join(s3_folder, relative_path).replace("\\", "/")
            content_type, _ = mimetypes.guess_type(local_path)
            print(f"[DEBUG] Đang upload {local_path} lên S3 key: {s3_key}")
            with open(local_path, "rb") as f:
                s3_client.upload_fileobj(f, bucket, s3_key, ExtraArgs={"ContentType": content_type or "application/octet-stream"})
            print(f"Đã upload {local_path} lên S3: {s3_key}")
    print(f"[DEBUG] Đã hoàn thành upload_folder_to_s3 cho {local_folder}")


def get_file_info(file_key: str) -> dict:
    """
    Get metadata about a file stored in R2.
    """
    try:
        return s3_client.head_object(Bucket=R2_BUCKET_NAME, Key=file_key)
    except ClientError as e:
        raise RuntimeError(f"Failed to retrieve file info: {e}")
    
def get_image_links(local_folder, s3_folder):
    base_url = os.environ.get("S3_BASE_URL")
    links = []
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), local_folder)
            s3_key = os.path.join(s3_folder, relative_path).replace("\\", "/")
            links.append(f"{base_url}/{s3_key}")
    return links



# upload_folder_to_s3("./de-cuoi-hoc-ky-2-toan-7-nam-2024-2025-phong-gddt-thu-dau-mot-binh-duong/auto/images", "audio_overview/images")
links = get_image_links("./de-cuoi-hoc-ky-2-toan-7-nam-2024-2025-phong-gddt-thu-dau-mot-binh-duong/auto/images", "audio_overview/images")
print(links[:5])