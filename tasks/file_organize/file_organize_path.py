"""
สคริปต์นี้ใช้สำหรับจัดระเบียบไฟล์ในโฟลเดอร์ที่ผู้ใช้ระบุผ่าน argument --path
โดยจะย้ายไฟล์แต่ละประเภทไปยังโฟลเดอร์ย่อยที่เหมาะสม และลบโฟลเดอร์ว่างหลังจากจัดระเบียบเสร็จ
สามารถปรับแต่งหมวดหมู่ไฟล์ได้ผ่านไฟล์ file_categories.json
"""
import os
import shutil
import argparse
import json
from pathlib import Path

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
def get_category(extension):
    for category, ext_list in FILE_CATEGORIES.items():
        if extension.lower() in ext_list:
            return category
    return "อื่นๆ" # หมวดหมู่สำหรับไฟล์ที่ไม่ตรงกับประเภทใดๆ

# ฟังก์ชันหลักในการจัดระเบียบโฟลเดอร์
def organize(folder: Path):
    for dirpath, _, filenames in os.walk(folder):
        current_path = Path(dirpath)
        # ตรวจสอบว่าเป็นโฟลเดอร์หลักหรือไม่ และไม่ใช่โฟลเดอร์ที่มีการจัดระเบียบแล้ว
        if current_path == folder or current_path.name not in FILE_CATEGORIES.keys():
            for filename in filenames:
                file_path = current_path / filename
                if not file_path.is_file():
                    continue

                ext = file_path.suffix
                category = get_category(ext)
                dest_folder = folder / category
                dest_path = dest_folder / filename

                try:
                    dest_folder.mkdir(exist_ok=True)
                except Exception as e:
                    print(f"เกิดข้อผิดพลาดขณะสร้างโฟลเดอร์ {dest_folder}: {e}")
                    continue
            
                if dest_path.exists():
                    dest_path = dest_folder / f"{file_path.stem}_copy{ext}"
                try:
                    shutil.move(str(file_path), str(dest_path))
                    print(f"ย้าย {file_path} ไปยัง {dest_path} แล้ว")
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
    # รับตัวแปรจาก CLI
    parser = argparse.ArgumentParser(description="จัดระเบียบไฟล์ตามประเภทในโฟลเดอร์")
    parser.add_argument("path", type=str, help="ที่อยู่ของโฟลเดอร์ที่ต้องการจัดระเบียบ")

    args = parser.parse_args()
    target = Path(args.path).expanduser().resolve()

    if not target.exists() or not target.is_dir():
        print("ข้อผิดพลาด : โฟลเดอร์ไม่ถูกต้องหรือไม่พบ")
    else:
        print(f"กำลังจัดระเบียบโฟลเดอร์ : {target}")
        organize(target)
        remove_empty_folders(target)
        print("✅ ทำงานสำเร็จ")