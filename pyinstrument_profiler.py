#!/usr/bin/env python3
"""
Performance Profiling using pyinstrument

วิธีการใช้งาน:
1. ติดตั้ง pyinstrument: pip install pyinstrument
2. รันไฟล์นี้: python pyinstrument_profiler.py
3. ดูผลลัพธ์ในเทอร์มินัลและไฟล์ที่สร้างขึ้น

สามารถระบุฟังก์ชันที่ต้องการวัดได้ด้วย argument:
    python pyinstrument_profiler.py --function all      # วัดทุกฟังก์ชัน (default)
    python pyinstrument_profiler.py --function heavy    # วัดฟังก์ชัน heavy_calculation
    python pyinstrument_profiler.py --function sort     # วัดฟังก์ชัน sorting_test
    python pyinstrument_profiler.py --function io       # วัดฟังก์ชัน io_operations
"""

import argparse
import csv
import os
import time
from datetime import datetime
from pyinstrument import Profiler


def function_under_test(function_name="all"):
    """เรียกใช้งานฟังก์ชันที่ต้องการทดสอบ"""
    if function_name == "heavy" or function_name == "all":
        print("กำลังทดสอบฟังก์ชัน heavy_calculation...")
        heavy_calculation()
    
    if function_name == "sort" or function_name == "all":
        print("กำลังทดสอบฟังก์ชัน sorting_test...")
        sorting_test()
    
    if function_name == "io" or function_name == "all":
        print("กำลังทดสอบฟังก์ชัน io_operations...")
        io_operations()


def heavy_calculation():
    """ฟังก์ชันคำนวณหนัก"""
    sum_value = 0
    for n in range(10000000):
        sum_value = sum_value + n
    return sum_value


def sorting_test():
    """ฟังก์ชันทดสอบการเรียงลำดับ"""
    import random
    data = [random.randint(1, 1000) for _ in range(100000)]
    
    # ทดสอบแบบ bubble sort (ช้า)
    def bubble_sort(arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
    
    # ทดสอบเรียง 1000 รายการแรกด้วย bubble sort
    bubble_sort(data[:1000])
    
    # ทดสอบแบบ built-in sort (เร็ว)
    sorted_data = sorted(data)
    return sorted_data


def io_operations():
    """ฟังก์ชันทดสอบการอ่าน/เขียนไฟล์"""
    # สร้างไฟล์ชั่วคราว
    with open("temp_test_file.txt", "w") as f:
        for i in range(10000):
            f.write(f"บรรทัดที่ {i}: นี่คือการทดสอบการเขียนไฟล์\n")
    
    # อ่านไฟล์
    with open("temp_test_file.txt", "r") as f:
        content = f.read()
    
    # ลบไฟล์ชั่วคราว
    os.remove("temp_test_file.txt")
    return len(content)


def save_to_csv(profile_data, filename="profile_result.csv"):
    """บันทึกผลลงในไฟล์ CSV"""
    lines = profile_data.split('\n')
    
    # แยกข้อมูลเพื่อบันทึกลง CSV
    data_lines = []
    recording = False
    
    for line in lines:
        # ข้ามบรรทัดที่ไม่มีข้อมูล
        if not line.strip():
            continue
            
        # เริ่มเก็บข้อมูลเมื่อเจอบรรทัดที่มีชื่อไฟล์และฟังก์ชัน
        if '.py:' in line and recording == False:
            recording = True
        
        if recording:
            # ทำความสะอาดข้อมูล
            parts = line.strip().split()
            if len(parts) >= 2:
                time_value = parts[0]
                function_info = ' '.join(parts[1:])
                data_lines.append([time_value, function_info])
    
    # บันทึกลงไฟล์ CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time (s)', 'Function Info'])
        writer.writerows(data_lines)
    
    print(f"บันทึกผลเป็น CSV ที่: {filename}")


def main():
    """ฟังก์ชันหลัก"""
    # รับพารามิเตอร์จากคอมมานด์ไลน์
    parser = argparse.ArgumentParser(description='วัดประสิทธิภาพโปรแกรม Python ด้วย pyinstrument')
    parser.add_argument('--function', type=str, default='all',
                        choices=['all', 'heavy', 'sort', 'io'],
                        help='ฟังก์ชันที่ต้องการทดสอบ (all, heavy, sort, io)')
    args = parser.parse_args()
    
    # สร้างไดเรกทอรีสำหรับเก็บผลลัพธ์ถ้ายังไม่มี
    os.makedirs('output', exist_ok=True)
    
    # สร้าง timestamp สำหรับชื่อไฟล์
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # สร้าง Profiler และเริ่มต้นการ profile
    profiler = Profiler()
    profiler.start()
    
    # เรียกใช้งานฟังก์ชันที่ต้องการตรวจสอบประสิทธิภาพ
    function_under_test(args.function)
    
    # หยุดการ profile
    profiler.stop()
    
    # แสดงผลการ profile ผ่านทางเทอร์มินัล 
    print("\nผลการวัดประสิทธิภาพ:")
    profiler.print()
    
    # บันทึกผลการ profile ลงในไฟล์ Text
    text_filename = f"output/profile_result_{args.function}_{timestamp}.txt"
    with open(text_filename, "w", encoding="utf-8") as f:
        f.write(profiler.output_text())
    print(f"บันทึกผลเป็น Text ที่: {text_filename}")
    
    # บันทึกผลการ profile ลงในไฟล์ HTML 
    html_filename = f"output/profile_result_{args.function}_{timestamp}.html"
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(profiler.output_html())
    print(f"บันทึกผลเป็น HTML ที่: {html_filename}")
    
    # บันทึกผลการ profile ลงในไฟล์ CSV
    csv_filename = f"output/profile_result_{args.function}_{timestamp}.csv"
    save_to_csv(profiler.output_text(), csv_filename)


if __name__ == "__main__":
    main() 