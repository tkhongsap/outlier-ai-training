#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
โปรแกรมสาธิตการดึงข้อมูลคุณภาพอากาศในประเทศไทย
รวมทั้ง 2 วิธี: Web Scraping และ API Integration
"""

import sys
import os

# เพิ่ม path ปัจจุบันเพื่อให้ import ได้
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aqi_scraper import AQIScraper
from aqi_api import AQIAPIClient
from aqi_simple import SimpleAQIClient

def show_menu():
    """แสดงเมนูตัวเลือก"""
    print("\n" + "="*60)
    print("🌤️  โปรแกรมตรวจสอบคุณภาพอากาศในประเทศไทย")
    print("="*60)
    print("เลือกวิธีการดึงข้อมูล:")
    print()
    print("1. 🌐 Web Scraping จาก aqi.in")
    print("   - ดึงข้อมูลโดยตรงจากเว็บไซต์")
    print("   - ไม่ต้องใช้ API key")
    print("   - อาจไม่เสถียรหากเว็บไซต์เปลี่ยนโครงสร้าง")
    print()
    print("2. 🔗 API Integration (WAQI)")
    print("   - ใช้ WAQI API (demo key)")
    print("   - ข้อมูลเชื่อถือได้")
    print("   - มีข้อจำกัดในการใช้งาน demo key")
    print()
    print("3. 🎯 Simple Demo (แนะนำ)")
    print("   - ข้อมูลจำลองที่สมจริง")
    print("   - แสดงผลสวยงาม")
    print("   - เหมาะสำหรับการทดสอบและเรียนรู้")
    print()
    print("4. 🚀 รันทั้งหมด")
    print("   - ทดสอบทุกวิธีพร้อมกัน")
    print()
    print("0. ❌ ออกจากโปรแกรม")
    print("="*60)

def run_web_scraping():
    """รันโปรแกรม Web Scraping"""
    print("\n🌐 กำลังรันโปรแกรม Web Scraping...")
    print("-" * 50)
    
    try:
        scraper = AQIScraper()
        success = scraper.run()
        
        if success:
            print("✅ Web Scraping เสร็จสิ้น")
        else:
            print("❌ Web Scraping ไม่สำเร็จ")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

def run_api_integration():
    """รันโปรแกรม API Integration"""
    print("\n🔗 กำลังรันโปรแกรม API Integration...")
    print("-" * 50)
    
    try:
        api_client = AQIAPIClient()
        success = api_client.run()
        
        if success:
            print("✅ API Integration เสร็จสิ้น")
        else:
            print("❌ API Integration ไม่สำเร็จ")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

def run_simple_demo():
    """รันโปรแกรม Simple Demo"""
    print("\n🎯 กำลังรันโปรแกรม Simple Demo...")
    print("-" * 50)
    
    try:
        simple_client = SimpleAQIClient()
        success = simple_client.run()
        
        if success:
            print("✅ Simple Demo เสร็จสิ้น")
        else:
            print("❌ Simple Demo ไม่สำเร็จ")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

def run_all():
    """รันทุกโปรแกรม"""
    print("\n🚀 กำลังรันทุกโปรแกรม...")
    print("=" * 60)
    
    # รัน Simple Demo ก่อน (เพราะทำงานได้แน่นอน)
    run_simple_demo()
    
    print("\n" + "="*60)
    
    # รัน API Integration
    run_api_integration()
    
    print("\n" + "="*60)
    
    # รัน Web Scraping
    run_web_scraping()
    
    print("\n🎉 รันทุกโปรแกรมเสร็จสิ้น!")
    print("📁 ตรวจสอบไฟล์ผลลัพธ์ในโฟลเดอร์ 'output'")

def show_output_files():
    """แสดงไฟล์ output ที่มีอยู่"""
    output_dir = "output"
    
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        if files:
            print(f"\n📁 ไฟล์ในโฟลเดอร์ {output_dir}:")
            for i, file in enumerate(files, 1):
                file_path = os.path.join(output_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"   {i}. {file} ({file_size:,} bytes)")
        else:
            print(f"\n📁 โฟลเดอร์ {output_dir} ว่างเปล่า")
    else:
        print(f"\n📁 ยังไม่มีโฟลเดอร์ {output_dir}")

def main():
    """ฟังก์ชันหลัก"""
    while True:
        show_menu()
        show_output_files()
        
        try:
            choice = input("\n👉 เลือกตัวเลือก (0-4): ").strip()
            
            if choice == "0":
                print("\n👋 ขอบคุณที่ใช้โปรแกรม!")
                break
            elif choice == "1":
                run_web_scraping()
            elif choice == "2":
                run_api_integration()
            elif choice == "3":
                run_simple_demo()
            elif choice == "4":
                run_all()
            else:
                print("❌ กรุณาเลือกตัวเลือกที่ถูกต้อง (0-4)")
                
        except KeyboardInterrupt:
            print("\n\n👋 โปรแกรมถูกยกเลิก")
            break
        except Exception as e:
            print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        
        input("\n⏸️  กด Enter เพื่อดำเนินการต่อ...")

if __name__ == "__main__":
    main() 