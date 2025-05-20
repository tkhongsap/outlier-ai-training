"""
สคริปต์นี้ใช้สำหรับจัดระเบียบไฟล์ในโฟลเดอร์ตามประเภทไฟล์ เช่น รูปภาพ เอกสาร วิดีโอ ฯลฯ
โดยจะย้ายไฟล์แต่ละประเภทไปยังโฟลเดอร์ย่อยที่เหมาะสม และลบโฟลเดอร์ว่างหลังจากจัดระเบียบเสร็จ
สามารถปรับแต่งหมวดหมู่ไฟล์ได้ผ่านไฟล์ file_categories.json
"""
# การใช้งาน: python file_organize.py
import os
import shutil
import json
from pathlib import Path

# เปลี่ยนเส้นทางนี้เป็นโฟลเดอร์ที่คุณต้องการจัดระเบียบ
TARGET_FOLDER = Path.cwd() / "test_dir"
print(TARGET_FOLDER)

# กำหนดประเภทไฟล์และนามสกุลที่เกี่ยวข้อง
def load_file_categories():
    config_path = Path(__file__).parent / "file_categories.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"เกิดข้อผิดพลาดขณะโหลดไฟล์หมวดหมู่: {e}")
    # fallback
    return {
        "รูปภาพ": [".png", ".jpg", ".jpeg", ".gif", ".webp"],
        "เอกสาร": [".doc", ".docx", ".txt", ".odt", ".pdf"],
        "สเปรดชีต": [".xls", ".xlsx", ".csv"],
        "งานนำเสนอ": [".ppt", ".pptx"],
        "ไฟล์บีบอัด": [".zip", ".tar", ".gz", ".rar", ".7z"],
        "สคริปต์หรือโค้ด": [".py", ".js", ".sh", ".bat", ".ipynb"],
        "วิดีโอ": [".mp4", ".mov", ".avi", ".mkv"],
        "เสียง": [".mp3", ".wav", ".m4a"],
    }

FILE_CATEGORIES = load_file_categories()

# ฟังก์ชันเพื่อหาหมวดหมู่จากนามสกุลไฟล์
def get_category(file_extension):
    for category, extensions in FILE_CATEGORIES.items():
        if file_extension.lower() in extensions:
            return category
    return "อื่นๆ" # หมวดหมู่สำหรับไฟล์ที่ไม่ตรงกับประเภทใดๆ

# ฟังก์ชันหลักในการจัดระเบียบโฟลเดอร์
def organize_folder(root_folder: Path):
    for dir_path, _, filenames in os.walk(root_folder):
        current_path = Path(dir_path)
        # ตรวจสอบว่าเป็นโฟลเดอร์หลักหรือไม่ และไม่ใช่โฟลเดอร์ที่มีการจัดระเบียบแล้ว
        if current_path == root_folder or current_path.name not in FILE_CATEGORIES.keys():
            for filename in filenames:
                file_path = current_path / filename
                if file_path.is_file():
                    ext = file_path.suffix
                    category = get_category(ext)
                    dest_folder = root_folder / category
                    dest_folder.mkdir(exist_ok=True)
                    try:
                        dest_folder.mkdir(exist_ok=True)
                    except Exception as e:
                        print(f"เกิดข้อผิดพลาดขณะสร้างโฟลเดอร์ {dest_folder}: {e}")
                    # รองรับการย้ายไฟล์ที่มีชื่อซ้ำ
                    new_file_path = dest_folder / filename
                    if new_file_path.exists():
                        new_file_path = dest_folder / f"{file_path.stem}_copy{ext}"
                    try:
                        shutil.move(str(file_path), str(new_file_path))
                        print(f"ย้าย {file_path} ไปยัง {new_file_path} แล้ว")
                    except Exception as e:
                        print(f"เกิดข้อผิดพลาดขณะย้ายไฟล์ {file_path}: {e}")

def remove_empty_folders(root_folder: Path):
    # ลบโฟลเดอร์ว่าง
    for dir_path, dir_names, _ in os.walk(root_folder, topdown=False):
        current_path = Path(dir_path)
        if current_path == root_folder:
            continue
        try:
            if not any(current_path.iterdir()):
                current_path.rmdir()
                print(f"ลบโฟลเดอร์ว่าง: {current_path}")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดขณะลบโฟลเดอร์ {current_path}: {e}")

if __name__ == "__main__":
    print(f"กำลังจัดระเบียบโฟลเดอร์: {TARGET_FOLDER}")
    organize_folder(TARGET_FOLDER)
    remove_empty_folders(TARGET_FOLDER)
    print("✅ ทำงานสำเร็จ")