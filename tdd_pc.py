import serial 
import time 
import threading 
 
ser = serial.Serial('COM5', baudrate=19200, timeout=0.1)  # กำหนดพอร์ต Serial และ Baud Rate 
 
def build_packet(pkt_type, seq, payload): 
    """สร้างแพ็กเก็ตข้อมูลพร้อมส่วนหัว ลำดับ ข้อมูล และ Checksum""" 
    pkt = bytearray([0xAA, pkt_type, seq]) + payload  # ส่วนหัว (0xAA) ประเภทแพ็กเก็ต ลำดับ และข้อมูล 
    pkt.append(sum(pkt) & 0xFF)  # คำนวณ Checksum อย่างง่าย (ผลรวม modulo 256) 
    return bytes(pkt) 
 
def parse_packet(data): 
    """ตรวจสอบและแยกข้อมูลออกจากแพ็กเก็ต""" 
    if len(data) < 4 or data[0] != 0xAA:  # ตรวจสอบความยาวขั้นต่ำและส่วนหัว 
        return None 
    pkt_type = data[1]  # ประเภทแพ็กเก็ต 
    seq = data[2]     # หมายเลขลำดับ 
    payload = data[3:-1]  # ข้อมูล 
    crc = data[-1]    # Checksum ที่ได้รับ 
    if sum(data[:-1]) & 0xFF != crc:  # ตรวจสอบ Checksum 
        return None 
    return pkt_type, seq, payload 
 
def tx_worker(): 
    """Worker thread สำหรับส่ง Request ไปยังอุปกรณ์ Edge ทุก ๆ 20ms""" 
    seq_id = 0 
    while True: 
        # ขอข้อมูลจากอุปกรณ์ Edge ทุก ๆ 20ms (ส่งคำขอภายในช่วงเวลา 20 มิลลิวินาที) 
        req_payload = f"REQ:{int(time.time()*1000)%100000}".encode()  # สร้าง payload สำหรับ Request พร้อม Timestamp 
        req_pkt = build_packet(0x02, seq_id, req_payload)  # สร้างแพ็กเก็ต Request 
        ser.write(req_pkt)  # ส่งแพ็กเก็ต Request 
        print(f"[PC] Sent REQ (seq {seq_id}): {req_payload}") 
        seq_id = (seq_id + 1) % 256  # เพิ่มหมายเลขลำดับ 
        time.sleep(0.02)  # หน่วงเวลา 20ms (Time Slot สำหรับส่ง Request ของ PC) 
 
def rx_worker(): 
    """Worker thread สำหรับรับข้อมูลจากอุปกรณ์ Edge""" 
    rx_buffer = bytearray() 
    while True: 
        if ser.in_waiting: 
            byte = ser.read(1)  # อ่านข้อมูลทีละ 1 ไบต์ 
            if byte: 
                rx_buffer.append(byte[0])  # เพิ่มไบต์ที่ได้รับลงในบัฟเฟอร์ 
                if len(rx_buffer) >= 4 and rx_buffer[0] == 0xAA:  # ตรวจสอบความยาวขั้นต่ำและส่วนหัว 
                    pkt = parse_packet(bytes(rx_buffer))  # พยายาม Parse แพ็กเก็ต 
                    if pkt: 
                        pkt_type, seq, payload = pkt 
                        if pkt_type == 0x06:  # ACK (0x06 คือประเภทแพ็กเก็ต ACK ที่อุปกรณ์ Edge ส่งมา) 
                            print(f"[PC] Received ACK (seq {seq}): {payload}") 
                        rx_buffer.clear()  # ล้างบัฟเฟอร์หลังจากประมวลผลแพ็กเก็ตแล้ว 
 
# เริ่ม worker threads สำหรับการรับและส่งข้อมูลแบบ Non-blocking 
threading.Thread(target=rx_worker, daemon=True).start() 
threading.Thread(target=tx_worker, daemon=True).start() 
 
while True: 
    time.sleep(1)  # รักษา Thread หลักให้ทำงานอยู่
