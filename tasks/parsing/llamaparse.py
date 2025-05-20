import os
import sys
import requests
from dotenv import load_dotenv
from llama_parse import LlamaParse
from urllib.parse import urlparse

# โหลดตัวแปรสภาพแวดล้อม
load_dotenv()

# ฟังก์ชันสำหรับแยกวิเคราะห์รูปภาพ
def parse_image(img_path, out_dir, prompt=None):
    llama_cloud_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not llama_cloud_api_key:
        sys.exit("Error: ไม่พบ LLAMA_CLOUD_API_KEY ในไฟล์ .env")
    
    # กำหนดค่าคำแนะนำการแยกวิเคราะห์รูปภาพ
    prompt = prompt or "Extract all text and detailed information from this image. Describe any charts, diagrams, or visual elements present."
    
    img_name = os.path.basename(img_path)
    output_filename = f"{os.path.splitext(img_name)[0]}_parsed.md"
    output_file = os.path.join(out_dir, output_filename)
    
    # เริ่มต้น LlamaParse
    parser = LlamaParse(
        api_key=llama_cloud_api_key,
        system_prompt=prompt,
        result_type="markdown",
        verbose=True
    )
    
    print(f"กำลังประมวลผลรูปภาพ : {img_name}")
    
    try:
        # แยกวิเคราะห์รูปภาพ
        documents = parser.load_data(img_path)
        
        # ดึงเนื้อหาที่ได้จากการแยกวิเคราะห์
        combined_content = "\n\n".join([doc.text for doc in documents])
        
        # บันทึกเนื้อหาที่ได้จากการแยกวิเคราะห์
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(combined_content)
        print(f"✓ บันทึกเนื้อหาที่แยกวิเคราะห์แล้วไปที่ {output_file}")
        return output_file
    except Exception as e:
        print(f"✗ เกิดข้อผิดพลาดในการประมวลผล {img_name} : {str(e)}")
        return None

# ฟังก์ชันสำหรับดาวน์โหลดรูปภาพจาก URL
def download_image(url, save_dir):
    filename = os.path.basename(urlparse(url).path) or "downloaded_image.jpeg"
    filepath = os.path.join(save_dir, filename)
    
    print(f"กำลังดาวน์โหลดรูปภาพจาก {url}")
    resp = requests.get(url, stream=True)
    if resp.status_code == 200:
        with open(filepath, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"ดาวน์โหลดรูปภาพและบันทึกไปที่ {filepath} เรียบร้อยแล้ว")
        return filepath
    print(f"ไม่สามารถดาวน์โหลดรูปภาพได้ : {resp.status_code}")
    return None

def main():
    in_dir, out_dir = "data", "output"
    os.makedirs(in_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    
    default_url = "https://docelf.com/images/free_receipt_template_xs.png"
    
    # รับข้อมูลนำเข้าจากผู้ใช้
    user_url = input(f"กรอก URL รูปภาพ (หรือกด Enter เพื่อใช้ค่าเริ่มต้น: {default_url}): ").strip()
    
    # ใช้ค่าเริ่มต้นถ้าไม่มีข้อมูลนำเข้า
    url = user_url if user_url else default_url
    print(f"กำลังใช้รูปภาพจาก: {url}")
    
    img_path = download_image(url, in_dir)
    if not img_path:
        sys.exit("ดาวน์โหลดรูปภาพล้มเหลว")
        
    result = parse_image(img_path, out_dir)
    print("การแยกวิเคราะห์รูปภาพเสร็จสมบูรณ์แล้ว!" if result else "การแยกวิเคราะห์ล้มเหลว")

if __name__ == "__main__":
    main()