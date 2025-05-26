#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
โปรแกรมดึงข้อมูลคุณภาพอากาศในประเทศไทยผ่าน API
วิธีที่ 2: API Integration
"""

import requests
import json
import os
from datetime import datetime
import time

class AQIAPIClient:
    def __init__(self, api_key=None):
        # WAQI API (World Air Quality Index)
        self.waqi_base_url = "https://api.waqi.info"
        self.api_key = api_key or "demo"  # ใช้ demo key สำหรับทดสอบ
        
        # Air4Thai API (ทางเลือกสำหรับข้อมูลไทย)
        self.air4thai_base_url = "http://air4thai.pcd.go.th/services"
        
        self.output_dir = "output"
        
        # รายชื่อเมืองหลักในประเทศไทย
        self.thai_cities = [
            "Bangkok", "Chiang Mai", "Phuket", "Pattaya", 
            "Khon Kaen", "Nakhon Ratchasima", "Hat Yai",
            "Udon Thani", "Rayong", "Samut Prakan"
        ]
        
    def create_output_directory(self):
        """สร้างโฟลเดอร์ output หากยังไม่มี"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"สร้างโฟลเดอร์ {self.output_dir} เรียบร้อยแล้ว")
    
    def get_city_aqi_data(self, city_name):
        """ดึงข้อมูล AQI ของเมืองผ่าน WAQI API"""
        try:
            url = f"{self.waqi_base_url}/feed/{city_name}/"
            params = {"token": self.api_key}
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") == "ok":
                return self.parse_waqi_response(data["data"], city_name)
            else:
                print(f"ไม่พบข้อมูลสำหรับ {city_name}: {data.get('data', 'Unknown error')}")
                return None
                
        except requests.RequestException as e:
            print(f"เกิดข้อผิดพลาดในการดึงข้อมูล {city_name}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"เกิดข้อผิดพลาดในการแปลง JSON สำหรับ {city_name}: {e}")
            return None
    
    def parse_waqi_response(self, data, city_name):
        """แยกข้อมูลจาก WAQI API response"""
        try:
            station_data = {
                "city": city_name,
                "station_name": data.get("city", {}).get("name", city_name),
                "AQI": data.get("aqi"),
                "timestamp": data.get("time", {}).get("s"),
                "coordinates": {
                    "latitude": data.get("city", {}).get("geo", [None, None])[0],
                    "longitude": data.get("city", {}).get("geo", [None, None])[1]
                }
            }
            
            # ดึงข้อมูลมลพิษต่างๆ
            iaqi = data.get("iaqi", {})
            
            # PM2.5
            if "pm25" in iaqi:
                station_data["PM2.5"] = iaqi["pm25"].get("v")
            
            # PM10
            if "pm10" in iaqi:
                station_data["PM10"] = iaqi["pm10"].get("v")
            
            # O3 (โอโซน)
            if "o3" in iaqi:
                station_data["O3"] = iaqi["o3"].get("v")
            
            # ข้อมูลเพิ่มเติม
            if "co" in iaqi:
                station_data["CO"] = iaqi["co"].get("v")
            
            if "no2" in iaqi:
                station_data["NO2"] = iaqi["no2"].get("v")
            
            if "so2" in iaqi:
                station_data["SO2"] = iaqi["so2"].get("v")
            
            # ข้อมูลสภาพอากาศ
            if "t" in iaqi:
                station_data["temperature"] = iaqi["t"].get("v")
            
            if "h" in iaqi:
                station_data["humidity"] = iaqi["h"].get("v")
            
            if "p" in iaqi:
                station_data["pressure"] = iaqi["p"].get("v")
            
            if "w" in iaqi:
                station_data["wind"] = iaqi["w"].get("v")
            
            return station_data
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการแยกข้อมูล {city_name}: {e}")
            return None
    
    def get_thailand_stations_data(self):
        """ดึงข้อมูลจากสถานีต่างๆ ในประเทศไทย"""
        print("กำลังดึงข้อมูลจากสถานีต่างๆ ในประเทศไทย...")
        
        thailand_data = {
            "timestamp": datetime.now().isoformat(),
            "country": "Thailand",
            "data_source": "WAQI API",
            "api_key_used": "demo" if self.api_key == "demo" else "custom",
            "stations": []
        }
        
        for city in self.thai_cities:
            print(f"กำลังดึงข้อมูล {city}...")
            city_data = self.get_city_aqi_data(city)
            
            if city_data:
                thailand_data["stations"].append(city_data)
                print(f"✓ ดึงข้อมูล {city} สำเร็จ (AQI: {city_data.get('AQI', 'N/A')})")
            else:
                print(f"✗ ไม่สามารถดึงข้อมูล {city} ได้")
            
            # หน่วงเวลาเล็กน้อยเพื่อไม่ให้ API rate limit
            time.sleep(1)
        
        return thailand_data
    
    def get_thailand_summary(self, data):
        """สรุปข้อมูลคุณภาพอากาศของประเทศไทย"""
        if not data.get('stations'):
            return None
        
        stations = data['stations']
        summary = {
            "timestamp": data['timestamp'],
            "country": "Thailand",
            "data_source": data['data_source'],
            "total_stations": len(stations),
            "average_AQI": None,
            "average_PM2.5": None,
            "average_PM10": None,
            "average_O3": None,
            "stations_data": stations
        }
        
        # คำนวณค่าเฉลี่ย
        aqi_values = [s['AQI'] for s in stations if s.get('AQI') is not None]
        pm25_values = [s['PM2.5'] for s in stations if s.get('PM2.5') is not None]
        pm10_values = [s['PM10'] for s in stations if s.get('PM10') is not None]
        o3_values = [s['O3'] for s in stations if s.get('O3') is not None]
        
        if aqi_values:
            summary['average_AQI'] = round(sum(aqi_values) / len(aqi_values), 1)
        if pm25_values:
            summary['average_PM2.5'] = round(sum(pm25_values) / len(pm25_values), 1)
        if pm10_values:
            summary['average_PM10'] = round(sum(pm10_values) / len(pm10_values), 1)
        if o3_values:
            summary['average_O3'] = round(sum(o3_values) / len(o3_values), 1)
        
        return summary
    
    def save_to_json(self, data, filename="air_quality_api_data.json"):
        """บันทึกข้อมูลลงไฟล์ JSON"""
        filepath = os.path.join(self.output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"บันทึกข้อมูลลงไฟล์ {filepath} เรียบร้อยแล้ว")
            return True
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการบันทึกไฟล์: {e}")
            return False
    
    def get_aqi_level_description(self, aqi):
        """แปลงค่า AQI เป็นคำอธิบาย"""
        if aqi is None:
            return "ไม่มีข้อมูล"
        elif aqi <= 50:
            return "ดี (Good)"
        elif aqi <= 100:
            return "ปานกลาง (Moderate)"
        elif aqi <= 150:
            return "ไม่ดีต่อกลุ่มเสี่ยง (Unhealthy for Sensitive Groups)"
        elif aqi <= 200:
            return "ไม่ดี (Unhealthy)"
        elif aqi <= 300:
            return "แย่มาก (Very Unhealthy)"
        else:
            return "อันตราย (Hazardous)"
    
    def run(self):
        """เรียกใช้งานโปรแกรมหลัก"""
        print("=== โปรแกรมดึงข้อมูลคุณภาพอากาศในประเทศไทย (API) ===")
        
        if self.api_key == "demo":
            print("⚠️  กำลังใช้ demo API key (มีข้อจำกัดในการใช้งาน)")
            print("   สำหรับการใช้งานจริง ควรลงทะเบียนที่ https://aqicn.org/data-platform/token/")
        
        # สร้างโฟลเดอร์ output
        self.create_output_directory()
        
        # ดึงข้อมูลจากสถานีต่างๆ
        thailand_data = self.get_thailand_stations_data()
        
        # สรุปข้อมูลประเทศไทย
        thailand_summary = self.get_thailand_summary(thailand_data)
        
        if thailand_summary and thailand_summary['total_stations'] > 0:
            # บันทึกข้อมูลลงไฟล์
            success = self.save_to_json(thailand_summary)
            
            if success:
                print("\n=== สรุปข้อมูลคุณภาพอากาศในประเทศไทย ===")
                print(f"จำนวนสถานีตรวจวัด: {thailand_summary['total_stations']} สถานี")
                print(f"AQI เฉลี่ย: {thailand_summary['average_AQI']} ({self.get_aqi_level_description(thailand_summary['average_AQI'])})")
                print(f"PM2.5 เฉลี่ย: {thailand_summary['average_PM2.5']} μg/m³")
                print(f"PM10 เฉลี่ย: {thailand_summary['average_PM10']} μg/m³")
                print(f"O3 เฉลี่ย: {thailand_summary['average_O3']} μg/m³")
                print(f"เวลาที่ดึงข้อมูล: {thailand_summary['timestamp']}")
                
                print("\n=== รายละเอียดแต่ละสถานี ===")
                for station in thailand_summary['stations_data']:
                    aqi = station.get('AQI')
                    print(f"{station['city']}: AQI {aqi} ({self.get_aqi_level_description(aqi)})")
                
                return True
        else:
            print("ไม่พบข้อมูลคุณภาพอากาศในประเทศไทย")
            return False

def main():
    # สามารถใส่ API key ของคุณเองที่นี่
    # api_client = AQIAPIClient(api_key="YOUR_API_KEY_HERE")
    api_client = AQIAPIClient()  # ใช้ demo key
    api_client.run()

if __name__ == "__main__":
    main() 