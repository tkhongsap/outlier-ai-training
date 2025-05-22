#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
โปรแกรมวิเคราะห์ข้อความภาษาไทย (วิธีที่ 2)
"""

import collections
import re
import statistics
from pythainlp import word_tokenize
from pythainlp.corpus import thai_stopwords


class ThaiTextAnalyzerV2:
    """คลาสสำหรับวิเคราะห์ข้อความภาษาไทยโดยใช้ PyThaiNLP"""

    def __init__(self):
        # รูปแบบสำหรับการตัดคำ
        self.word_pattern = re.compile(r'[ก-๙]+')
        # คำที่พบบ่อยที่จะไม่นับเป็นคำสำคัญ (stopwords)
        self.stopwords = set(thai_stopwords())
        custom_stopwords = {'และ', 'หรือ', 'ของ', 'ใน', 'ที่', 'มี', 'ไม่', 'ให้', 'ได้', 'ว่า', 'เป็น', 'กับ'}
        self.stopwords.update(custom_stopwords)
        
    def extract_words(self, text):
        """สกัดคำจากข้อความโดยใช้ PyThaiNLP"""
        # ลบช่องว่างซ้ำซ้อน
        text = re.sub(r'\s+', ' ', text).strip()
        
        # ใช้ PyThaiNLP สำหรับการตัดคำ
        words = word_tokenize(text, engine='newmm')
        
        # กรองคำที่สั้นและไม่มีตัวอักษรไทย
        return [word for word in words if len(word) > 1 and re.search(self.word_pattern, word)]
        
    def analyze(self, text):
        """วิเคราะห์ข้อความและคืนค่าข้อมูลสถิติ"""
        words = self.extract_words(text)
        
        # กรองคำที่ไม่ต้องการ (stopwords)
        filtered_words = [word for word in words if word.lower() not in self.stopwords]
        
        # ใช้ Counter เพื่อนับความถี่ของคำ
        word_counter = collections.Counter(words)
        filtered_counter = collections.Counter(filtered_words)
        
        # คำนวณสถิติพื้นฐาน
        word_lengths = [len(word) for word in words]
        avg_length = statistics.mean(word_lengths) if word_lengths else 0
        
        return {
            "จำนวนคำทั้งหมด": len(words),
            "จำนวนคำที่ไม่ซ้ำกัน": len(word_counter),
            "ความยาวเฉลี่ยของคำ": avg_length,
            "ความถี่ของคำ": word_counter.most_common(),
            "ความถี่ของคำ (ไม่รวมคำทั่วไป)": filtered_counter.most_common()
        }
    
    def print_word_cloud(self, text, threshold=2):
        """แสดงผลเป็น word cloud อย่างง่าย"""
        words = self.extract_words(text)
        filtered_words = [word for word in words if word.lower() not in self.stopwords]
        word_counter = collections.Counter(filtered_words)
        
        print("\nแสดงคำที่พบบ่อย:")
        print("-" * 40)
        
        for word, count in word_counter.most_common(10):
            if count >= threshold:
                print(f"{word.ljust(15)} | {'*' * count}")
        
        print("-" * 40)


def main():
    # ข้อความทดสอบ
    test_text = """จิรายุ ห่วงทรัพย์ โฆษกประจำสำนักนายกรัฐมนตรี เปิดเผยว่า จากสถานการณ์พบสารปนเปื้อน
    เกินค่ามาตรฐานในแม่น้ำกก นายกรัฐมนตรีมีข้อห่วงใยให้เร่งดำเนินการแก้ไขปัญหา"""
    
    # สร้างอ็อบเจกต์และวิเคราะห์ข้อความ
    analyzer = ThaiTextAnalyzerV2()
    result = analyzer.analyze(test_text)
    
    # แสดงผลการวิเคราะห์
    print("ผลการวิเคราะห์ข้อความภาษาไทย:")
    print("-" * 40)
    print(f"จำนวนคำทั้งหมด: {result['จำนวนคำทั้งหมด']}")
    print(f"จำนวนคำที่ไม่ซ้ำกัน: {result['จำนวนคำที่ไม่ซ้ำกัน']}")
    print(f"ความยาวเฉลี่ยของคำ: {result['ความยาวเฉลี่ยของคำ']:.2f} ตัวอักษร")
    
    print("\nคำที่พบบ่อย 5 อันดับแรก:")
    for i, (word, count) in enumerate(result["ความถี่ของคำ"][:5], 1):
        print(f"{i}. {word} ({count} ครั้ง)")
    
    print("\nคำสำคัญที่พบบ่อย:")
    for i, (word, count) in enumerate(result["ความถี่ของคำ (ไม่รวมคำทั่วไป)"][:5], 1):
        print(f"{i}. {word} ({count} ครั้ง)")
    
    # แสดง word cloud อย่างง่าย
    analyzer.print_word_cloud(test_text)


if __name__ == "__main__":
    main() 