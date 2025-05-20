# การวัดประสิทธิภาพโปรแกรม Python (Python Performance Profiling)

โปรเจกต์นี้ประกอบด้วยเครื่องมือสำหรับวิเคราะห์ประสิทธิภาพโปรแกรม Python โดยตรวจจับเวลาการทำงานของฟังก์ชัน
แสดงผลในเทอร์มินัล และบันทึกผลลงในไฟล์รูปแบบต่างๆ

## วิธีที่ 1: pyinstrument

[pyinstrument](https://github.com/joerick/pyinstrument) เป็น profiler ที่ให้ผลลัพธ์ที่อ่านง่ายและรวดเร็ว โดยเฉพาะสำหรับการวิเคราะห์คอคอดในโปรแกรม เหมาะสำหรับการตรวจหาจุดที่ทำให้โปรแกรมทำงานช้า

### การติดตั้ง

```bash
pip install pyinstrument
```

### การใช้งาน

```bash
python pyinstrument_profiler.py
```

ตัวเลือกเพิ่มเติม:
```bash
python pyinstrument_profiler.py --function heavy  # ทดสอบเฉพาะฟังก์ชัน heavy_calculation
python pyinstrument_profiler.py --function sort   # ทดสอบเฉพาะฟังก์ชัน sorting_test
python pyinstrument_profiler.py --function io     # ทดสอบเฉพาะฟังก์ชัน io_operations
python pyinstrument_profiler.py --function all    # ทดสอบทุกฟังก์ชัน (ค่าเริ่มต้น)
```

## วิธีที่ 2: cProfile

cProfile เป็น profiler มาตรฐานที่มากับ Python มีความละเอียดสูงและให้ข้อมูลเชิงลึกเกี่ยวกับการทำงานของโปรแกรมแบบรายละเอียด

### การใช้งาน

```bash
python cprofile_profiler.py
```

ตัวเลือกเพิ่มเติม:
```bash
python cprofile_profiler.py --function heavy  # ทดสอบเฉพาะฟังก์ชัน heavy_calculation
python cprofile_profiler.py --function sort   # ทดสอบเฉพาะฟังก์ชัน sorting_test
python cprofile_profiler.py --function io     # ทดสอบเฉพาะฟังก์ชัน io_operations
python cprofile_profiler.py --function all    # ทดสอบทุกฟังก์ชัน (ค่าเริ่มต้น)

# การเรียงลำดับผลลัพธ์
python cprofile_profiler.py --sort time       # เรียงตามเวลารวม
python cprofile_profiler.py --sort calls      # เรียงตามจำนวนครั้งที่เรียก
python cprofile_profiler.py --sort cumulative # เรียงตามเวลาสะสม (ค่าเริ่มต้น)

# จำกัดจำนวนผลลัพธ์
python cprofile_profiler.py --limit 10       # แสดงเฉพาะ 10 รายการแรก
```

## ผลลัพธ์

ทั้งสองวิธีจะบันทึกผลไว้ในไดเรกทอรี `output/` ในรูปแบบ:
- ไฟล์ข้อความ (.txt)
- ไฟล์ CSV (.csv)
- ไฟล์ HTML (สำหรับ pyinstrument)

## การสร้างแผนภาพทางภาพจากผลการวัด

สำหรับ cProfile คุณสามารถสร้างแผนภาพได้ด้วย gprof2dot และ Graphviz:

```bash
# ติดตั้งเครื่องมือที่จำเป็น
pip install gprof2dot
# สำหรับ Windows ดาวน์โหลด Graphviz จาก https://graphviz.org/download/

# สร้างไฟล์โปรไฟล์
python -m cProfile -o profile.prof cprofile_profiler.py

# สร้างแผนภาพ PNG
gprof2dot -f pstats profile.prof | dot -Tpng -o profile_graph.png
```

## ความแตกต่างระหว่างสองวิธี

| คุณสมบัติ | pyinstrument | cProfile |
|----------|--------------|----------|
| ความเร็วในการวัด | เร็วกว่า | ช้ากว่าเล็กน้อย |
| รายละเอียด | ภาพรวมที่ชัดเจน | รายละเอียดมากกว่า |
| การแสดงผล | สวยงาม เข้าใจง่าย | ละเอียด เหมาะสำหรับการวิเคราะห์เชิงลึก |
| การติดตั้ง | ต้องติดตั้งเพิ่ม | มีในไลบรารีมาตรฐาน |
| รูปแบบไฟล์ผลลัพธ์ | txt, html, csv | txt, csv |
``` 