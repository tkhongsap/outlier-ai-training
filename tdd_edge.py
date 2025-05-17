import serial 
import time 
import threading 
 
ser = serial.Serial('COM6', baudrate=19200, timeout=0.1)  # กำหนดพอร์ต Serial และ Baud Rate 
seq_id = 0  # ตัวแปรสำหรับเก็บหมายเลขลำดับการส่ง 
 
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
    """Worker thread สำหรับส่งข้อมูล Sensor ไปยัง PC ทุก ๆ 100ms (80ms สำหรับการส่ง)""" 
    global seq_id 
    while True: 
        # ส่งข้อมูลทุก ๆ 100ms (ใช้เวลาส่ง 80ms) 
        payload = f"EDGE_DATA:{int(time.time()*1000)%100000}".encode()  # สร้าง payload ข้อมูล Sensor พร้อม Timestamp 
        pkt = build_packet(0x01, seq_id, payload)  # สร้างแพ็กเก็ตข้อมูล Sensor (0x01 คือประเภทแพ็กเก็ต DATA) 
        ser.write(pkt)  # ส่งแพ็กเก็ตข้อมูล 
        print(f"[EDGE] Sent DATA (seq {seq_id}): {payload}") 
        seq_id = (seq_id + 1) % 256  # เพิ่มหมายเลขลำดับ 
        time.sleep(0.08)  # หน่วงเวลา 80ms (Time Slot สำหรับส่งข้อมูลของ Edge) 
 
def rx_worker(): 
    """Worker thread สำหรับรับ Request จาก PC""" 
    global seq_id 
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
                        if pkt_type == 0x02:  # REQ (0x02 คือประเภทแพ็กเก็ต REQ ที่ PC ส่งมา) 
                            print(f"[EDGE] Received REQ (seq {seq}): {payload}") 
                            ack = build_packet(0x06, seq, b'')  # สร้างแพ็กเก็ต ACK (0x06 คือประเภทแพ็กเก็ต ACK) 
                            ser.write(ack)  # ส่งแพ็กเก็ต ACK