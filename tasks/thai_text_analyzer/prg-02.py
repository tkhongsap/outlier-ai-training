import re
from pythainlp import word_tokenize
from docx import Document
import argparse


class ThaiTextAnalyzerV2:
    """
    คลาสสำหรับวิเคราะห์ข้อความภาษาไทย โดยใช้ PyThaiNLP

    สามารถอ่านข้อความจากสตริงหรือไฟล์ .txt และ .docx
    """

    def __init__(self):
        # ตัวอักษรไทย, สระไทย, วรรณยุกต์ และตัวเลข
        self.thai_chars = r'[ก-๙]+'

    def tokenize(self, text):
        """
        แบ่งข้อความเป็นคำโดยใช้ PyThaiNLP

        :param text: ข้อความที่จะแบ่งเป็นคำ
        :return: รายการคำที่ถูกแบ่งตระหนัก
        """
        # ลบช่องว่างที่ไม่จำเป็น
        text = re.sub(r'\s+', ' ', text).strip()

        # ใช้ PyThaiNLP word_tokenize
        words = word_tokenize(text, engine='newmm')

        # กรองเอาเฉพาะคำที่มีตัวอักษรไทยและมีความยาวมากกว่า 1
        return [word for word in words if re.search(self.thai_chars, word) and len(word) > 1]

    def analyze(self, text):
        """
        วิเคราะห์ข้อความและส่งคืนผลลัพธ์การวิเคราะห์

        :param text: ข้อความที่จะวิเคราะห์
        :return: dict ที่含ผลลัพธ์การวิเคราะห์
        """
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

    def read_text_from_file(self, file_path):
        """
        อ่านข้อความจากไฟล์ .txt หรือ .docx

        :param file_path: เส้นทางไฟล์ที่จะอ่าน
        :return: ข้อความในไฟล์
        """
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            return ' '.join(paragraph.text for paragraph in doc.paragraphs)
        else:
            raise ValueError("ไม่รองรับไฟล์ประเภทนี้ โปรดใช้ .txt หรือ .docx")


def main():
    parser = argparse.ArgumentParser(description="วิเคราะห์ข้อความภาษาไทยโดยใช้ PyThaiNLP")
    parser.add_argument('--file', '-f', help='เส้นทางไฟล์ที่จะวิเคราะห์ (โปรดใช้ .txt หรือ .docx)')
    args = parser.parse_args()

    analyzer = ThaiTextAnalyzerV2()

    if args.file:
        try:
            text = analyzer.read_text_from_file(args.file)
        except FileNotFoundError:
            print(f"ไม่สามารถเจอไฟล์ {args.file} โปรดตรวจสอบและลองใหม่")
            return
        except ValueError as ve:
            print(ve)
            return
    else:
        # ข้อความตัวอย่างสำหรับทดสอบ
        test_text = """จิรายุ ห่วงทรัพย์ โฆษกประจำสำนักนายกรัฐมนตรี เปิดเผยว่า จากสถานการณ์พบสารปนเปื้อน
        เกินค่ามาตรฐานในแม่น้ำกก นายกรัฐมนตรีมีข้อห่วงใยให้เร่งดำเนินการแก้ไขปัญหา"""
        text = test_text

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