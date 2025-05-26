#!/usr/bin/env python3
"""
โปรแกรมดึงข้อมูลข้อสอบด้วย Selenium
"""

import json
import os
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def extract_exam_data_selenium(exam_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"https://www.trueplookpanya.com/examination2/examPreview?id={exam_id}")
        driver.implicitly_wait(5)
        
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # เมตาเดตา
        metadata = {"exam_id": exam_id}
        
        # หาชื่อข้อสอบ
        try:
            title = driver.find_element(By.CSS_SELECTOR, "h1, h2, h3").text.strip()
            metadata["exam_name"] = title if title else f"Exam_{exam_id}"
        except:
            metadata["exam_name"] = f"Exam_{exam_id}"
        
        # หาระดับและวิชา
        level_match = re.search(r'ม\.\s*(\d+)', page_text)
        subject_match = re.search(r'(คณิตศาสตร์|ภาษาไทย|ภาษาอังกฤษ|วิทยาศาสตร์|สังคมศึกษา)', page_text)
        
        metadata["level_name"] = f"ม.{level_match.group(1)}" if level_match else "Unknown"
        metadata["subject_name"] = subject_match.group(1) if subject_match else "Unknown"
        
        # หาคำถาม
        questions_list = []
        matches = re.findall(r'(\d+)\.\s*([^\n\r]{10,})', page_text)
        
        for i, (num, text) in enumerate(matches, 1):
            questions_list.append({
                "question_number": i,
                "question_id": f"q_{i}",
                "question_text": text.strip(),
                "choices": []
            })
        
        driver.quit()
        
        if questions_list:
            metadata["question_count"] = len(questions_list)
            return {"metadata": metadata, "questions": questions_list}
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    output_dir = os.path.join("data", "output")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    exam_id = 13500
    exam_data = extract_exam_data_selenium(exam_id)
    
    if exam_data:
        metadata = exam_data["metadata"]
        filename = f"{metadata['exam_id']}_{metadata['exam_name']}_{metadata['level_name']}_{metadata['subject_name']}_selenium.json"
        filename = sanitize_filename(filename)
        
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
            json.dump(exam_data, f, ensure_ascii=False, indent=4)
        
        print(f"บันทึกสำเร็จ: {filename} ({len(exam_data['questions'])} ข้อ)")
    else:
        print("ไม่สามารถดึงข้อมูลได้")

if __name__ == "__main__":
    main() 