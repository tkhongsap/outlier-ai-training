import serial
import time
import threading

ser = serial.Serial("COM5", baudrate=19200, timeout=0.1)


def build_packet(pkt_type: int, seq: int, payload: bytes) -> bytes:
    pkt = bytearray([0xAA, pkt_type, seq]) + payload
    pkt.append(sum(pkt) & 0xFF)
    return bytes(pkt)


def parse_packet(data: bytes):
    if len(data) < 4 or data[0] != 0xAA:
        return None
    if sum(data[:-1]) & 0xFF != data[-1]:
        return None
    return data[1], data[2], data[3:-1]


def tx_worker():
    seq_id = 0
    while True:
        payload = f"REQ:{int(time.time()*1000)%100000}".encode()
        pkt = build_packet(0x02, seq_id, payload)
        ser.write(pkt)
        print(f"[PC] Sent REQ seq={seq_id} payload={payload}")
        seq_id = (seq_id + 1) % 256
        time.sleep(0.02)


def rx_worker():
    buffer = bytearray()
    while True:
        if ser.in_waiting:
            byte = ser.read(1)
            if byte:
                buffer.append(byte[0])
                if len(buffer) >= 4 and buffer[0] == 0xAA:
                    pkt = parse_packet(bytes(buffer))
                    if pkt:
                        pkt_type, seq, payload = pkt
                        if pkt_type == 0x06:
                            print(f"[PC] Received ACK seq={seq} payload={payload}")
                        buffer.clear()
        time.sleep(0.01)


if __name__ == "__main__":
    threading.Thread(target=rx_worker, daemon=True).start()
    threading.Thread(target=tx_worker, daemon=True).start()
    while True:
        time.sleep(1)
