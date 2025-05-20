#!/usr/bin/env python3
"""
Performance Profiling using cProfile

วิธีการใช้งาน:
1. รันไฟล์นี้: python cprofile_profiler.py
2. ดูผลลัพธ์ในเทอร์มินัลและไฟล์ที่สร้างขึ้น

สามารถระบุฟังก์ชันที่ต้องการวัดได้ด้วย argument:
    python cprofile_profiler.py --function all      # วัดทุกฟังก์ชัน (default)
    python cprofile_profiler.py --function heavy    # วัดฟังก์ชัน heavy_calculation
    python cprofile_profiler.py --function sort     # วัดฟังก์ชัน sorting_test
    python cprofile_profiler.py --function io       # วัดฟังก์ชัน io_operations
    
สามารถระบุการเรียงลำดับผลลัพธ์:
    python cprofile_profiler.py --sort cumulative   # เรียงตามเวลาสะสม (default)
    python cprofile_profiler.py --sort time         # เรียงตามเวลารวม
    python cprofile_profiler.py --sort calls        # เรียงตามจำนวนครั้งที่เรียก
"""

import argparse
import cProfile
import csv
import io
import os
import pstats
import random
import time
from datetime import datetime
from pstats import SortKey


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


def get_sort_key(sort_name):
    """แปลงชื่อการเรียงลำดับเป็น SortKey"""
    sort_keys = {
        "calls": SortKey.CALLS,
        "cumulative": SortKey.CUMULATIVE,
        "time": SortKey.TIME,
        "name": SortKey.NAME,
        "filename": SortKey.FILENAME,
        "line": SortKey.LINE
    }
    return sort_keys.get(sort_name, SortKey.CUMULATIVE)


def save_to_csv(stats, filename):
    """บันทึกผลลงในไฟล์ CSV"""
    # ดึงข้อมูลจาก Stats object
    s = io.StringIO()
    stats.stream = s
    stats.print_stats()
    
    lines = s.getvalue().split('\n')
    csv_data = []
    
    # หาบรรทัดที่เริ่มต้นด้วยข้อมูล
    header_found = False
    for line in lines:
        if 'ncalls' in line:
            header_found = True
            # บันทึกหัวตาราง
            headers = ['ncalls', 'tottime', 'percall_tot', 'cumtime', 'percall_cum', 'filename:lineno(function)']
            csv_data.append(headers)
            continue
        
        if header_found and line.strip():
            # แยกข้อมูลออกเป็นคอลัมน์
            # รูปแบบของบรรทัดคือ: ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            items = []
            parts = line.strip().split()
            
            if len(parts) >= 6:
                # รวมชื่อไฟล์และฟังก์ชันที่อาจจะมีช่องว่าง
                ncalls = parts[0]
                tottime = parts[1]
                percall_tot = parts[2]
                cumtime = parts[3]
                percall_cum = parts[4]
                func_info = ' '.join(parts[5:])
                
                items = [ncalls, tottime, percall_tot, cumtime, percall_cum, func_info]
                csv_data.append(items)
    
    # บันทึกลงไฟล์ CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)
    
    print(f"บันทึกผลเป็น CSV ที่: {filename}")


def main():
    """ฟังก์ชันหลัก"""
    # รับพารามิเตอร์จากคอมมานด์ไลน์
    parser = argparse.ArgumentParser(description='วัดประสิทธิภาพโปรแกรม Python ด้วย cProfile')
    parser.add_argument('--function', type=str, default='all',
                        choices=['all', 'heavy', 'sort', 'io'],
                        help='ฟังก์ชันที่ต้องการทดสอบ (all, heavy, sort, io)')
    parser.add_argument('--sort', type=str, default='cumulative',
                        choices=['calls', 'cumulative', 'time', 'name', 'filename', 'line'],
                        help='การเรียงลำดับผลลัพธ์')
    parser.add_argument('--limit', type=int, default=20,
                        help='จำนวนแถวผลลัพธ์ที่จะแสดง (default: 20)')
    args = parser.parse_args()
    
    # สร้างไดเรกทอรีสำหรับเก็บผลลัพธ์ถ้ายังไม่มี
    os.makedirs('output', exist_ok=True)
    
    # สร้าง timestamp สำหรับชื่อไฟล์
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # สร้าง Profiler และเริ่มต้นการ profile
    profiler = cProfile.Profile()
    profiler.enable()
    
    # เรียกใช้งานฟังก์ชันที่ต้องการตรวจสอบประสิทธิภาพ
    function_under_test(args.function)
    
    # หยุดการ profile
    profiler.disable()
    
    # เตรียมการแสดงผล
    sort_key = get_sort_key(args.sort)
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats(sort_key)
    ps.print_stats(args.limit)
    result = s.getvalue()
    
    # แสดงผลการ profile ผ่านทางเทอร์มินัล
    print("\nผลการวัดประสิทธิภาพ:")
    print(result)
    
    # บันทึกผลการ profile ลงในไฟล์ Text
    text_filename = f"output/cprofile_result_{args.function}_{timestamp}.txt"
    with open(text_filename, "w", encoding="utf-8") as f:
        ps = pstats.Stats(profiler, stream=f).sort_stats(sort_key)
        ps.print_stats()
    print(f"บันทึกผลเป็น Text ที่: {text_filename}")
    
    # บันทึกผลการ profile ลงในไฟล์ CSV
    csv_filename = f"output/cprofile_result_{args.function}_{timestamp}.csv"
    save_to_csv(ps, csv_filename)
    
    # สร้างกราฟ (ต้องติดตั้ง pstats2 ก่อนใช้งาน)
    print("\nหากต้องการสร้างกราฟจากผลการวัด สามารถติดตั้ง gprof2dot และ graphviz ด้วยคำสั่ง:")
    print("pip install gprof2dot")
    print("สำหรับ Windows: ติดตั้ง Graphviz จาก https://graphviz.org/download/")
    print("\nจากนั้นรันคำสั่ง:")
    print(f"python -m cProfile -o profile.prof cprofile_profiler.py --function {args.function}")
    print("gprof2dot -f pstats profile.prof | dot -Tpng -o profile_graph.png")


if __name__ == "__main__":
    main() 