import datetime
import sys

# ส่วนลดที่ใช้ได้
VALID_DISCOUNT_CODES = {
    "DISCOUNT50": 0.5,   
    "DISCOUNT20": 0.8,   
    "VIP": 0.7           
}

def คำนวณค่าจอดรถ(เวลาเข้า, เวลาออก):
    """คำนวณค่าจอดรถตามระยะเวลา"""
    # คำนวณระยะเวลาจอดเป็นนาที
    ระยะเวลา = เวลาออก - เวลาเข้า
    จำนวนนาที = ระยะเวลา.total_seconds() / 60
    จำนวนชั่วโมง = จำนวนนาที / 60
    
    # คำนวณค่าจอดรถตามอัตรา
    if จำนวนนาที <= 15:
        return 0  
    elif จำนวนชั่วโมง <= 2:
        return 30  
    elif จำนวนชั่วโมง <= 3:
        return 50  
    elif จำนวนชั่วโมง <= 6:
        return 100  
    elif จำนวนชั่วโมง <= 12:
        return 200  
    elif จำนวนชั่วโมง <= 24:
        return 500  
    else:
        # เกิน 24 ชั่วโมง: คิดวันละ 700 บาท โดยปัดเศษขึ้นเป็นจำนวนวันเต็ม
        จำนวนวัน = (จำนวนชั่วโมง / 24)
        return 700 * (int(จำนวนวัน) + (1 if จำนวนวัน % 1 > 0 else 0))

def แปลงเวลา(เวลาที่ป้อน):
    try:
        ชั่วโมง, นาที = map(int, เวลาที่ป้อน.split(':'))
        if ชั่วโมง < 0 or ชั่วโมง > 23 or นาที < 0 or นาที > 59:
            return None
        เวลา = datetime.datetime.now().replace(hour=ชั่วโมง, minute=นาที, second=0, microsecond=0)
        return เวลา
    except:
        return None

def ตรวจสอบรหัสส่วนลด(รหัส):
    รหัส = รหัส.upper()
    if รหัส in VALID_DISCOUNT_CODES:
        return VALID_DISCOUNT_CODES[รหัส]
    return 1  # ไม่มีส่วนลด

def main():   
    # รับข้อมูลเวลาเข้า
    while True:
        เวลาเข้า_str = input("\nเวลาเข้า (รูปแบบ HH:MM) : ")
        เวลาเข้า = แปลงเวลา(เวลาเข้า_str)
        if เวลาเข้า:
            break
        print("รูปแบบเวลาไม่ถูกต้องในรูปแบบ HH:MM (24 ชั่วโมง)")
    
    # รับข้อมูลเวลาออก
    while True:
        เวลาออก_str = input("เวลาออก (รูปแบบ HH:MM) : ")
        เวลาออก = แปลงเวลา(เวลาออก_str)
        if เวลาออก:
            break
        print("รูปแบบเวลาไม่ถูกต้องในรูปแบบ HH:MM (24 ชั่วโมง)")
    
    # จัดการกรณีเวลาออกน้อยกว่าเวลาเข้า (ข้ามวัน)
    if เวลาออก < เวลาเข้า:
        เวลาออก += datetime.timedelta(days=1)
    
    # คำนวณค่าจอดรถ
    ค่าจอดรถ = คำนวณค่าจอดรถ(เวลาเข้า, เวลาออก)
    if ค่าจอดรถ is None:
        print("ไม่สามารถคำนวณค่าจอดรถได้")
        return
    
    # คำนวณระยะเวลาจอด
    ระยะเวลา = เวลาออก - เวลาเข้า
    จำนวนนาที = ระยะเวลา.total_seconds() / 60
    จำนวนชั่วโมง = จำนวนนาที / 60
    
    # สอบถามเรื่องส่วนลด
    มีบัตรส่วนลด = input("\nคุณมีบัตรส่วนลดหรือไม่ (Y/N) : ").strip().lower()
    ส่วนลด = 1  # เริ่มต้นไม่มีส่วนลด
    
    if มีบัตรส่วนลด == "y":
        จำนวนครั้ง = 0
        while จำนวนครั้ง < 3:  # จำกัดการป้อนผิดไม่เกิน 3 ครั้ง
            รหัสส่วนลด = input("กรุณาป้อนรหัสส่วนลด : ").strip()
            ส่วนลด = ตรวจสอบรหัสส่วนลด(รหัสส่วนลด)
            
            if ส่วนลด < 1:  # มีส่วนลด
                break
            
            print(f"รหัสส่วนลดไม่ถูกต้อง กรุณาลองใหม่ (รหัสตัวอย่าง: {', '.join(VALID_DISCOUNT_CODES.keys())})")
            จำนวนครั้ง += 1
            
            if จำนวนครั้ง == 3:
                print("รหัสผิดเกินจำนวนครั้งที่กำหนด")
    
    # คำนวณราคาสุทธิ
    ราคาสุทธิ = ค่าจอดรถ * ส่วนลด
    ส่วนลดเป็นบาท = ค่าจอดรถ - ราคาสุทธิ
    
    # แสดงผลลัพธ์
    print("\n===== ค่าบริการ =====")
    print(f"เวลาเข้า : {เวลาเข้า.strftime('%H:%M')} น.")
    print(f"เวลาออก : {เวลาออก.strftime('%H:%M')} น.")
    print(f"ระยะเวลาจอด : {int(จำนวนชั่วโมง)} ชั่วโมง {int(จำนวนนาที % 60)} นาที")
    print(f"ค่าจอดรถ : {ค่าจอดรถ:.2f} บาท")
    
    if ส่วนลด < 1:
        เปอร์เซ็นต์ส่วนลด = (1 - ส่วนลด) * 100
        print(f"ส่วนลด {เปอร์เซ็นต์ส่วนลด:.0f}% : {ส่วนลดเป็นบาท:.2f} บาท")
    
    print(f"ราคาสุทธิ : {ราคาสุทธิ:.2f} บาท")
    print("ขอบคุณที่ใช้บริการ")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nโปรแกรมถูกยกเลิกโดยผู้ใช้")
    except Exception as e:
        print(f"\nเกิดข้อผิดพลาด: {e}")
        sys.exit(1)
