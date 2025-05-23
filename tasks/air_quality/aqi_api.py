import requests
import json
import os
from datetime import datetime

# สร้างโฟลเดอร์สำหรับเก็บผลลัพธ์
def สร้างโฟลเดอร์():
    """
    สร้างโฟลเดอร์ output ถ้ายังไม่มี
    """
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"สร้างโฟลเดอร์: {output_dir}")
    return output_dir

class AirQualityAPI:
    """
    คลาสสำหรับดึงข้อมูลคุณภาพอากาศผ่าน API
    """
    
    def __init__(self, api_key=None):
        """
        กำหนดค่าเริ่มต้นสำหรับ API
        """
        # คุณควรใช้ API key จริงของคุณที่นี่
        self.api_key = api_key or "YOUR_API_KEY_HERE"
        self.base_url = "https://api.waqi.info"
    
    def ดึงข้อมูลเมือง(self, city):
        """
        ดึงข้อมูลคุณภาพอากาศสำหรับเมืองที่ระบุ
        """
        endpoint = f"{self.base_url}/feed/{city}/"
        params = {"token": self.api_key}
        
        try:
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    return data.get("data")
                else:
                    print(f"ไม่พบข้อมูลสำหรับเมือง {city}")
                    return None
            else:
                print(f"เกิดข้อผิดพลาด: {response.status_code}")
                return None
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการเรียก API: {str(e)}")
            return None
    
    def ดึงข้อมูลประเทศไทย(self):
        """
        ดึงข้อมูลคุณภาพอากาศของประเทศไทย
        """
        endpoint = f"{self.base_url}/map/bounds"
        
        # พิกัดทางภูมิศาสตร์ครอบคลุมประเทศไทย (lat1,lon1,lat2,lon2)
        bounds = "20.5,97.4,5.6,105.7"
        
        params = {
            "token": self.api_key,
            "latlng": bounds
        }
        
        try:
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    # รวบรวมข้อมูลจากทุกสถานีในประเทศไทย
                    ข้อมูลคุณภาพอากาศ = []
                    
                    for station in data.get("data", []):
                        # ดึงข้อมูลละเอียดของแต่ละสถานี
                        station_data = self.ดึงข้อมูลเมือง(station.get("station", {}).get("name"))
                        
                        if station_data:
                            try:
                                # ข้อมูลพื้นฐาน
                                iaqi = station_data.get("iaqi", {})
                                
                                ข้อมูล = {
                                    "สถานี": station_data.get("city", {}).get("name"),
                                    "ตำแหน่ง": station_data.get("city", {}).get("geo"),
                                    "เวลาอัปเดต": station_data.get("time", {}).get("s"),
                                    "AQI": station_data.get("aqi"),
                                    "PM2.5": iaqi.get("pm25", {}).get("v"),
                                    "PM10": iaqi.get("pm10", {}).get("v"),
                                    "O3": iaqi.get("o3", {}).get("v"),
                                    "อุณหภูมิ": iaqi.get("t", {}).get("v"),
                                    "ความชื้น": iaqi.get("h", {}).get("v"),
                                    "ความกดอากาศ": iaqi.get("p", {}).get("v")
                                }
                                
                                ข้อมูลคุณภาพอากาศ.append(ข้อมูล)
                            except Exception as e:
                                print(f"เกิดข้อผิดพลาดในการประมวลผลข้อมูลสถานี: {str(e)}")
                    
                    return ข้อมูลคุณภาพอากาศ
                else:
                    print("ไม่พบข้อมูลคุณภาพอากาศในประเทศไทย")
                    return None
            else:
                print(f"เกิดข้อผิดพลาด: {response.status_code}")
                return None
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการเรียก API: {str(e)}")
            return None

# บันทึกข้อมูลเป็นไฟล์ JSON
def บันทึกข้อมูล(ข้อมูล):
    """
    บันทึกข้อมูลเป็นไฟล์ JSON
    """
    if not ข้อมูล:
        print("ไม่มีข้อมูลที่จะบันทึก")
        return
    
    # สร้างโฟลเดอร์ output
    output_dir = สร้างโฟลเดอร์()
    
    # สร้างชื่อไฟล์พร้อมวันที่และเวลา
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"air_quality_api_data_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # เตรียมข้อมูลพร้อมกับเวลาดึงข้อมูล
    ข้อมูลพร้อมเมตาดาต้า = {
        "เวลาดึงข้อมูล": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "จำนวนสถานี": len(ข้อมูล),
        "ข้อมูลคุณภาพอากาศ": ข้อมูล
    }
    
    # บันทึกข้อมูลลงไฟล์ JSON
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(ข้อมูลพร้อมเมตาดาต้า, f, indent=4, ensure_ascii=False)
        print(f"บันทึกข้อมูลลงไฟล์ {filepath} สำเร็จ")
        
        # บันทึกข้อมูลล่าสุดแยกอีกไฟล์
        latest_filepath = os.path.join(output_dir, "air_quality_api_latest.json")
        with open(latest_filepath, 'w', encoding='utf-8') as f:
            json.dump(ข้อมูลพร้อมเมตาดาต้า, f, indent=4, ensure_ascii=False)
        print(f"บันทึกข้อมูลล่าสุดลงไฟล์ {latest_filepath} สำเร็จ")
        
        return filepath
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}")
        return None

# ฟังก์ชันหลัก
def main():
    """
    ฟังก์ชันหลักสำหรับการทำงาน
    """
    print(f"เริ่มดึงข้อมูลคุณภาพอากาศเวลา {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # สร้างอ็อบเจกต์ API
    api = AirQualityAPI()
    
    # ดึงข้อมูลคุณภาพอากาศประเทศไทย
    ข้อมูล = api.ดึงข้อมูลประเทศไทย()
    
    if ข้อมูล:
        print(f"พบข้อมูลคุณภาพอากาศ {len(ข้อมูล)} สถานี")
        
        # บันทึกข้อมูลเป็นไฟล์ JSON
        บันทึกข้อมูล(ข้อมูล)
    else:
        print("ไม่พบข้อมูลคุณภาพอากาศ")

if __name__ == "__main__":
    main() 