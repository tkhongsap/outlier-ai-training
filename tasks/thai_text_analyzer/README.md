# โปรแกรมวิเคราะห์ข้อความภาษาไทย (Thai Text Analyzer)

โปรแกรมนี้ใช้สำหรับวิเคราะห์ข้อความภาษาไทย โดยมีความสามารถในการวิเคราะห์ดังนี้:
1. นับจำนวนคำทั้งหมด
2. แสดงความถี่ของคำแต่ละคำที่พบ
3. นับจำนวนคำที่ไม่ซ้ำกัน
4. คำนวณความยาวเฉลี่ยของคำ

## การติดตั้ง

โปรแกรมเวอร์ชันปัจจุบันใช้ PyThaiNLP ซึ่งเป็นไลบรารีสำหรับการประมวลผลภาษาธรรมชาติภาษาไทย สามารถติดตั้งได้ด้วยคำสั่ง:

```bash
pip install pythainlp
```

## การใช้งาน

โปรแกรมมีสองเวอร์ชัน ซึ่งมีวิธีการใช้งานที่แตกต่างกันเล็กน้อย:

### เวอร์ชัน 1 (thai_text_analyzer_v1.py)

เวอร์ชันพื้นฐาน ใช้ PyThaiNLP ในการตัดคำและวิเคราะห์:

```bash
python thai_text_analyzer_v1.py
```

### เวอร์ชัน 2 (thai_text_analyzer_v2.py)

เวอร์ชันที่มีฟีเจอร์เพิ่มเติม ใช้ PyThaiNLP, collections และการวิเคราะห์ข้อมูลที่ลึกกว่า:

```bash
python thai_text_analyzer_v2.py
```

## ความแตกต่างระหว่างสองเวอร์ชัน

### เวอร์ชัน 1
- ใช้ PyThaiNLP สำหรับการตัดคำภาษาไทย
- แสดงผลวิเคราะห์ขั้นพื้นฐาน (จำนวนคำ, ความถี่, คำที่ไม่ซ้ำกัน, ความยาวเฉลี่ย)
- โค้ดเรียบง่าย เข้าใจง่าย

### เวอร์ชัน 2
- ใช้ PyThaiNLP และ collections.Counter สำหรับการตัดคำและการนับความถี่
- มีการตัดคำที่ละเอียดกว่า
- ใช้ stopwords จาก PyThaiNLP เพื่อกรองคำที่ไม่มีความหมายเฉพาะ
- แสดงข้อมูลสถิติเพิ่มเติม เช่น คำที่ยาวที่สุด/สั้นที่สุด
- แสดงความถี่ของตัวอักษร
- มีการแสดง word cloud อย่างง่าย

## การปรับแต่ง

หากต้องการวิเคราะห์ข้อความจากไฟล์ข้อความภายนอก ให้ดำเนินการดังนี้:

1. สร้างไฟล์ชื่อ `thai_text.txt` ในโฟลเดอร์เดียวกันกับโปรแกรม
2. เปิดการใช้งานส่วนของโค้ดที่เกี่ยวข้องกับการอ่านไฟล์ (นำเครื่องหมาย comment `"""` ออก)

## ข้อดีของการใช้ PyThaiNLP

การใช้ PyThaiNLP มีข้อดีดังนี้:

1. การตัดคำภาษาไทยที่แม่นยำกว่า เนื่องจากใช้อัลกอริทึมเฉพาะทาง
2. รองรับลักษณะพิเศษของภาษาไทยที่ไม่มีช่องว่างระหว่างคำ
3. มีชุดคำ stopwords ภาษาไทยมาให้ ทำให้กรองคำได้ดีขึ้น
4. สามารถใช้ฟีเจอร์อื่นๆ ของ PyThaiNLP ในการพัฒนาต่อยอด

## การพัฒนาต่อยอด

หากต้องการพัฒนาต่อเติมเพิ่มเติม สามารถใช้ความสามารถอื่นๆ ของ PyThaiNLP เช่น:

- การวิเคราะห์อารมณ์ (Sentiment Analysis)
- การแปลงเสียงเป็นข้อความ (Speech to Text)
- การแยกประเภทข้อความ (Text Classification)
- การสรุปความ (Text Summarization)