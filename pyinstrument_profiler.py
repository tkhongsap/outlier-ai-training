import os
import random
from pyinstrument import Profiler


def function_under_test():
    """เรียกใช้งานฟังก์ชันทดสอบ"""
    funcs = {
        "heavy": heavy_calculation,
        "sort": sorting_test,
        "io": io_operations
    }
    
    for name, func in funcs.items():
        print(f"กำลังทดสอบฟังก์ชัน {name}...")
        func()

def heavy_calculation():
    """ฟังก์ชันคำนวณหนัก"""
    return sum(n for n in range(10000000))

def sorting_test():
    """ฟังก์ชันทดสอบการเรียงลำดับ"""
    data = [random.randint(1, 1000) for _ in range(100000)]
    
    def bubble_sort(arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
    
    bubble_sort(data[:1000])  # เรียง 1000 รายการแรก
    return sorted(data)  # built-in sort (เร็ว)

def io_operations():
    """ฟังก์ชันทดสอบการอ่าน/เขียนไฟล์"""
    with open("temp_test_file.txt", "w") as f:
        for i in range(10000):
            f.write(f"บรรทัดที่ {i}: นี่คือการทดสอบการเขียนไฟล์\n")
    
    with open("temp_test_file.txt", "r") as f:
        content = f.read()
    
    os.remove("temp_test_file.txt")
    return len(content)

def main():
    """ฟังก์ชันหลัก"""
    os.makedirs('output', exist_ok=True)
    
    profiler = Profiler()
    profiler.start()
    function_under_test()
    profiler.stop()
    
    print("\nผลการวัดประสิทธิภาพ:")
    profiler.print()
    
    txt_filename = "output/profile_result.txt"
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(profiler.output_text())
    print(f"บันทึกผลเป็น Text ที่: {txt_filename}")

if __name__ == "__main__":
    main() 