import re
from pythainlp import word_tokenize
from docx import Document
import argparse

class ThaiTextAnalyzerV2:
    """คลาสสำหรับวิเคราะห์ข้อความภาษาไทย โดยใช้ PyThaiNLP"""

    def __init__(self):
        # ตัวอักษรไทย, สระไทย, วรรณยุกต์ และตัวเลข
        self.thai_chars = r'[ก-๙]+'

    def tokenize(self, text):
        """แบ่งข้อความเป็นคำโดยใช้ PyThaiNLP"""
        # ลบช่องว่างที่ไม่จำเป็น
        text = re.sub(r'\s+', ' ', text).strip()
        
        # ใช้ PyThaiNLP word_tokenize
        words = word_tokenize(text, engine='newmm')
        
        # กรองเอาเฉพาะคำที่มีตัวอักษรไทยและมีความยาวมากกว่า 1
        return [word for word in words if re.search(self.thai_chars, word) and len(word) > 1]

    def analyze(self, text):
        """วิเคราะห์ข้อความและส่งคืนผลลัพธ์การวิเคราะห์"""
        words = self.tokenize(text)
        
        # คำนวณความถี่ของคำ
        word_freq = {}
        for word in words:
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1
        
        # จำนวนคำทั้งหมด
        total_words = len(words)
        
        # จำนวนคำที่ไม่ซ้ำกัน
        unique_words = len(word_freq)
        
        # ความยาวเฉลี่ยของคำ
        avg_length = sum(len(word) for word in words) / total_words if total_words > 0 else 0
        
        # จัดเรียงความถี่ของคำจากมากไปน้อย
        sorted_freq = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "จำนวนคำทั้งหมด": total_words,
            "จำนวนคำที่ไม่ซ้ำกัน": unique_words,
            "ความยาวเฉลี่ยของคำ": avg_length,
            "ความถี่ของคำ": sorted_freq
        }

def read_text_from_file(file_path):
    """อ่านข้อความจากไฟล์ .txt หรือ .docx"""
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        return ' '.join(para.text for para in doc.paragraphs)
    else:
        raise ValueError("ไฟล์ที่ให้ไม่รองรับ กรุณาใส่ไฟล์ .txt หรือ .docx")

def main():
    parser = argparse.ArgumentParser(description="วิเคราะห์ข้อความภาษาไทยจากไฟล์ .txt หรือ .docx")
    parser.add_argument('--file', help='ไฟล์ข้อความ (.txt หรือ .docx)')
    args = parser.parse_args()
    
    # กำหนดข้อความเพื่อวิเคราะห์
    text = args.file if args.file else """จิรายุ ห่วงทรัพย์ โฆษกประจำสำนักนายกรัฐมนตรี เปิดเผยว่า จากสถานการณ์พบสารปนเปื้อน
    เกินค่ามาตรฐานในแม่น้ำกก นายกรัฐมนตรีมีข้อห่วงใยให้เร่งดำเนินการแก้ไขปัญหา"""
    
    # สร้างอ็อบเจกต์และวิเคราะห์
    analyzer = ThaiTextAnalyzerV2()
    result = analyzer.analyze(text)
    
    # แสดงผลลัพธ์
    print("ผลการวิเคราะห์ข้อความภาษาไทย:")
    print("-" * 40)
    print(f"จำนวนคำทั้งหมด: {result['จำนวนคำทั้งหมด']}")
    print(f"จำนวนคำที่ไม่ซ้ำกัน: {result['จำนวนคำที่ไม่ซ้ำกัน']}")
    print(f"ความยาวเฉลี่ยของคำ: {result['ความยาวเฉลี่ยของคำ']:.2f} ตัวอักษร")
    
    print("\nความถี่ของคำ (5 อันดับแรก):")
    for i, (word, freq) in enumerate(result["ความถี่ของคำ"][:5], 1):
        print(f"{i}. {word}: {freq} ครั้ง")

if __name__ == "__main__":
    main()