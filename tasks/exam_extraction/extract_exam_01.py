#!/usr/bin/env python3
"""
<CONTEMPLATOR>
Looking at the context, I notice:
1. The code is part of a larger exam scraping system that uses both Selenium and API approaches
2. The file contains functions for extracting exam data and saving it to JSON files
3. The comment should reflect the actual functionality shown in the code
4. The comment should be in English to maintain consistency with the rest of the codebase
</CONTEMPLATOR>

<FINAL_ANSWER
"""

import requests
import json
import os
import re
import time
from pathlib import Path

def sanitize_filename(filename):
    """แปลงชื่อไฟล์ให้ปลอดภัย โดยแทนที่อักขระพิเศษด้วย underscore"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def extract_exam_data(exam_id):
    """ดึงข้อมูลข้อสอบจาก API"""
    try:
        # URL
        api_url = f"https://www.trueplookpanya.com/webservice/api/examination/formdoexamination?exam_id={exam_id}"
        
        # ส่ง request ไปยัง API
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # ดึงข้อมูลเมตาเดตา
            metadata = {
                "exam_id": data['data']['exam']['exam_id'],
                "exam_name": data['data']['exam']['exam_name'],
                "level_name": data['data']['exam']['level_name'],
                "subject_name": data['data']['exam']['subject_name'],
                "question_count": data['data']['exam']['question_count']
            }
            
            # ดึงข้อมูลคำถามและตัวเลือก
            questions_list = []
            for i, question_data in enumerate(data['data']['formdo'], 1):
                question_detail = {
                    "question_number": i,
                    "question_id": question_data['question_id'],
                    "question_text": question_data['question_detail'],
                    "choices": []
                }
                
                for j, choice in enumerate(question_data['choice'], 1):
                    choice_detail = {
                        "choice_number": j,
                        "choice_text": choice['detail'],
                        "is_correct": choice['answer'] == "true"
                    }
                    question_detail["choices"].append(choice_detail)
                
                questions_list.append(question_detail)
            
            # รวมข้อมูลทั้งหมด
            return {
                "metadata": metadata,
                "questions": questions_list
            }
        else:
            print(f"ไม่สามารถดึงข้อมูล exam_id {exam_id} ได้ (Status: {response.status_code})")
            return None
    except Exception as e:
        print(f"เกิดข้อผิดพลาดกับ exam_id {exam_id}: {e}")
        return None

def main():
    """ฟังก์ชันหลักสำหรับดึงและบันทึกข้อมูลข้อสอบ"""
    # สร้างโฟลเดอร์ output
    output_dir = os.path.join("data", "output")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # กำหนด exam ID ที่ต้องการ
    exam_id = 13500
    
    print(f"เริ่มดึงข้อมูลข้อสอบ ID {exam_id}")
    
    # ดึงข้อมูลข้อสอบ
    exam_data = extract_exam_data(exam_id)
    
    if exam_data:
        # สร้างชื่อไฟล์จากข้อมูลเมตาเดตา
        metadata = exam_data["metadata"]
        filename = f"{metadata['exam_id']}_{metadata['exam_name']}_{metadata['level_name']}_{metadata['subject_name']}.json"
        filename = sanitize_filename(filename)
        
        # บันทึกไฟล์
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(exam_data, json_file, ensure_ascii=False, indent=4)
        
        print(f"บันทึกข้อมูลสำเร็จ: {filename}")
        print("เสร็จสิ้น!")
    else:
        print(f"ไม่สามารถดึงข้อมูล exam_id {exam_id} ได้")

if __name__ == "__main__":
    main()