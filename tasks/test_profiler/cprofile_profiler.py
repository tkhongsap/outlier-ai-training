#!/usr/bin/env python3
"""Performance Profiling using cProfile"""

import cProfile
import io
import os
import pstats
import random
from pstats import SortKey

def function_under_test():
    funcs = {"heavy": heavy_calculation, "sort": sorting_test, "io": io_operations}
    for name, func in funcs.items():
        print(f"กำลังทดสอบฟังก์ชัน {name}...")
        func()

def heavy_calculation():
    return sum(n for n in range(10000000))

def sorting_test():
    data = [random.randint(1, 1000) for _ in range(100000)]
    
    def bubble_sort(arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
    
    bubble_sort(data[:1000])
    return sorted(data)

def io_operations():
    with open("temp_test_file.txt", "w") as f:
        for i in range(10000):
            f.write(f"บรรทัดที่ {i}: นี่คือการทดสอบการเขียนไฟล์\n")
    
    with open("temp_test_file.txt", "r") as f:
        content = f.read()
    
    os.remove("temp_test_file.txt")
    return len(content)

def main():
    os.makedirs('output', exist_ok=True)
    
    profiler = cProfile.Profile()
    profiler.enable()
    function_under_test()
    profiler.disable()
    
    sort_key = SortKey.CUMULATIVE
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats(sort_key)
    ps.print_stats(20)
    
    print("\nผลการวัดประสิทธิภาพ:")
    print(s.getvalue())
    
    txt_filename = "output/cprofile_result.txt"
    with open(txt_filename, "w", encoding="utf-8") as f:
        pstats.Stats(profiler, stream=f).sort_stats(sort_key).print_stats()
    print(f"บันทึกผลเป็น Text ที่: {txt_filename}")

if __name__ == "__main__":
    main() 