#!/usr/bin/env python3
"""
โปรแกรมดึงข้อมูลข้อสอบจากหน้าเว็บโดยใช้ BeautifulSoup4
วิธีที่ 2: Web Scraping แทนการเรียก API
"""

import requests
import json
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

def sanitize_filename(filename):
    """แปลงชื่อไฟล์ให้ปลอดภัย โดยแทนที่อักขระพิเศษด้วย underscore"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def extract_exam_data_from_web(exam_id):
    """ดึงข้อมูลข้อสอบจากหน้าเว็บโดยใช้ BeautifulSoup"""
    try:
        # URL ของหน้าเว็บ
        web_url = f"https://www.trueplookpanya.com/examination2/examPreview?id={exam_id}"
        
        # ส่ง request ไปยังหน้าเว็บ
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(web_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # แปลง HTML ด้วย BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ดึงข้อมูลเมตาเดตา
            metadata = extract_metadata(soup, exam_id)
            
            # ดึงข้อมูลคำถาม
            questions = extract_questions(soup)
            
            if metadata and questions:
                return {
                    "metadata": metadata,
                    "questions": questions
                }
            else:
                print(f"ไม่พบข้อมูลข้อสอบในหน้าเว็บ exam_id {exam_id}")
                return None
        else:
            print(f"ไม่สามารถเข้าถึงหน้าเว็บ exam_id {exam_id} ได้ (Status: {response.status_code})")
            return None
    except Exception as e:
        print(f"เกิดข้อผิดพลาดกับ exam_id {exam_id}: {e}")
        return None

def extract_metadata(soup, exam_id):
    """ดึงข้อมูลเมตาเดตาจาก HTML"""
    try:
        metadata = {"exam_id": exam_id}
        
        # ลองหาข้อมูลเมตาเดตาจากหลายแหล่ง
        # หาชื่อข้อสอบ
        title_selectors = [
            'h1', 'h2', 'h3',
            '.exam-title', '.title', 
            '[class*="title"]', '[class*="exam"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                metadata["exam_name"] = title_elem.get_text().strip()
                break
        
        # หาข้อมูลระดับและวิชา
        info_text = soup.get_text()
        
        # ลองหาคำที่บ่งบอกระดับ
        level_patterns = [
            r'ระดับ\s*([^\n\r]+)',
            r'ชั้น\s*([^\n\r]+)',
            r'Level\s*([^\n\r]+)'
        ]
        
        for pattern in level_patterns:
            match = re.search(pattern, info_text)
            if match:
                metadata["level_name"] = match.group(1).strip()
                break
        
        # ลองหาคำที่บ่งบอกวิชา
        subject_patterns = [
            r'วิชา\s*([^\n\r]+)',
            r'Subject\s*([^\n\r]+)',
            r'เรื่อง\s*([^\n\r]+)'
        ]
        
        for pattern in subject_patterns:
            match = re.search(pattern, info_text)
            if match:
                metadata["subject_name"] = match.group(1).strip()
                break
        
        # ถ้าไม่พบข้อมูล ให้ใส่ค่าเริ่มต้น
        if "exam_name" not in metadata:
            metadata["exam_name"] = f"Exam_{exam_id}"
        if "level_name" not in metadata:
            metadata["level_name"] = "Unknown"
        if "subject_name" not in metadata:
            metadata["subject_name"] = "Unknown"
        
        return metadata
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการดึงเมตาเดตา: {e}")
        return None

def extract_questions(soup):
    """ดึงข้อมูลคำถามและตัวเลือกจาก HTML"""
    try:
        questions_list = []
        
        # ลองหาคำถามจากหลาย pattern
        question_selectors = [
            '.question', '.quiz-question', '[class*="question"]',
            'div[id*="question"]', 'li[class*="question"]'
        ]
        
        questions_found = []
        for selector in question_selectors:
            questions_found = soup.select(selector)
            if questions_found:
                break
        
        # ถ้าไม่เจอ ลองหาจาก pattern อื่น
        if not questions_found:
            # ลองหาจากข้อความที่มีหมายเลขข้อ
            text_content = soup.get_text()
            question_patterns = [
                r'(\d+)\.\s*([^\n\r]+)',
                r'ข้อ\s*(\d+)\s*[.:]?\s*([^\n\r]+)',
                r'Question\s*(\d+)\s*[.:]?\s*([^\n\r]+)'
            ]
            
            for pattern in question_patterns:
                matches = re.findall(pattern, text_content)
                if matches:
                    for i, (num, text) in enumerate(matches, 1):
                        question_detail = {
                            "question_number": i,
                            "question_id": f"q_{i}",
                            "question_text": text.strip(),
                            "choices": []
                        }
                        questions_list.append(question_detail)
                    break
        else:
            # ถ้าเจอ element ของคำถาม
            for i, question_elem in enumerate(questions_found, 1):
                question_text = question_elem.get_text().strip()
                
                question_detail = {
                    "question_number": i,
                    "question_id": f"q_{i}",
                    "question_text": question_text,
                    "choices": []
                }
                
                # ลองหาตัวเลือกในคำถามนี้
                choice_selectors = [
                    '.choice', '.option', '[class*="choice"]', '[class*="option"]'
                ]
                
                choices_found = []
                for selector in choice_selectors:
                    choices_found = question_elem.select(selector)
                    if choices_found:
                        break
                
                # ถ้าไม่เจอตัวเลือก ลองหาจาก pattern
                if not choices_found:
                    choice_patterns = [
                        r'[a-d]\)\s*([^\n\r]+)',
                        r'[1-4]\.\s*([^\n\r]+)',
                        r'[ก-ง]\)\s*([^\n\r]+)'
                    ]
                    
                    question_text_full = question_elem.get_text()
                    for pattern in choice_patterns:
                        choice_matches = re.findall(pattern, question_text_full)
                        if choice_matches:
                            for j, choice_text in enumerate(choice_matches, 1):
                                choice_detail = {
                                    "choice_number": j,
                                    "choice_text": choice_text.strip(),
                                    "is_correct": False  # ไม่สามารถระบุคำตอบที่ถูกจาก HTML ได้
                                }
                                question_detail["choices"].append(choice_detail)
                            break
                else:
                    # ถ้าเจอ element ของตัวเลือก
                    for j, choice_elem in enumerate(choices_found, 1):
                        choice_detail = {
                            "choice_number": j,
                            "choice_text": choice_elem.get_text().strip(),
                            "is_correct": False  # ไม่สามารถระบุคำตอบที่ถูกจาก HTML ได้
                        }
                        question_detail["choices"].append(choice_detail)
                
                questions_list.append(question_detail)
        
        # อัพเดทจำนวนคำถาม
        if questions_list:
            return questions_list
        else:
            print("ไม่พบคำถามในหน้าเว็บ")
            return []
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการดึงคำถาม: {e}")
        return []

def main():
    """ฟังก์ชันหลักสำหรับดึงและบันทึกข้อมูลข้อสอบ"""
    # สร้างโฟลเดอร์ output
    output_dir = os.path.join("data", "output")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # กำหนด exam ID ที่ต้องการ
    exam_id = 13500
    
    print(f"เริ่มดึงข้อมูลข้อสอบ ID {exam_id} จากหน้าเว็บ (BeautifulSoup)")
    
    # ดึงข้อมูลข้อสอบ
    exam_data = extract_exam_data_from_web(exam_id)
    
    if exam_data:
        # อัพเดทจำนวนคำถาม
        exam_data["metadata"]["question_count"] = len(exam_data["questions"])
        
        # สร้างชื่อไฟล์จากข้อมูลเมตาเดตา
        metadata = exam_data["metadata"]
        filename = f"{metadata['exam_id']}_{metadata['exam_name']}_{metadata['level_name']}_{metadata['subject_name']}_bs4.json"
        filename = sanitize_filename(filename)
        
        # บันทึกไฟล์
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(exam_data, json_file, ensure_ascii=False, indent=4)
        
        print(f"บันทึกข้อมูลสำเร็จ: {filename}")
        print(f"พบคำถาม {len(exam_data['questions'])} ข้อ")
        print("เสร็จสิ้น!")
    else:
        print(f"ไม่สามารถดึงข้อมูล exam_id {exam_id} ได้")

if __name__ == "__main__":
    main() 