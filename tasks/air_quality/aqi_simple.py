#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
โปรแกรมดึงข้อมูลคุณภาพอากาศในประเทศไทย (เวอร์ชันง่าย)
ใช้ API ฟรีและข้อมูลจำลองสำหรับการทดสอบ
"""

import requests
import json
import os
from datetime import datetime
import random

class SimpleAQIClient:
    def __init__(self):
        self.output_dir = "output"
        
        # ข้อมูลเมืองหลักในประเทศไทยพร้อมพิกัด
        self.thai_cities = {
            "กรุงเทพฯ": {"lat": 13.7563, "lon": 100.5018, "en": "Bangkok"},
            "เชียงใหม่": {"lat": 18.7883, "lon": 98.9853, "en": "Chiang Mai"},
            "ภูเก็ต": {"lat": 7.8804, "lon": 98.3923, "en": "Phuket"},
            "ขอนแก่น": {"lat": 16.4322, "lon": 102.8236, "en": "Khon Kaen"},
            "นครราชสีมา": {"lat": 14.9799, "lon": 102.0977, "en": "Nakhon Ratchasima"},
            "หาดใหญ่": {"lat": 7.0061, "lon": 100.4681, "en": "Hat Yai"},
            "อุดรธานี": {"lat": 17.4138, "lon": 102.7870, "en": "Udon Thani"},
            "ระยอง": {"lat": 12.6868, "lon": 101.2539, "en": "Rayong"}
        }
        
    def create_output_directory(self):
        """สร้างโฟลเดอร์ output หากยังไม่มี"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"สร้างโฟลเดอร์ {self.output_dir} เรียบร้อยแล้ว")
    
    def get_openweather_aqi(self, lat, lon, city_name):
        """ดึงข้อมูล AQI จาก OpenWeatherMap API (ฟรี)"""
        try:
            # ใช้ API ฟรีจาก OpenWeatherMap (ต้องลงทะเบียน)
            # สำหรับ demo นี้ เราจะสร้างข้อมูลจำลองที่สมจริง
            
            # สร้างข้อมูลจำลองที่สมจริงตามสถานการณ์ปัจจุบัน
            base_aqi = random.randint(25, 85)  # AQI ปกติของไทย
            
            # ปรับค่าตามเมือง (กรุงเทพฯ มักจะสูงกว่า)
            if "กรุงเทพ" in city_name:
                base_aqi += random.randint(10, 25)
            elif "เชียงใหม่" in city_name:
                # เชียงใหม่ในช่วงหมอกควันอาจสูง
                base_aqi += random.randint(5, 20)
            
            # คำนวณค่าอื่นๆ จาก AQI
            pm25 = max(5, base_aqi * 0.6 + random.randint(-10, 10))
            pm10 = max(10, pm25 * 1.5 + random.randint(-5, 15))
            o3 = max(10, random.randint(15, 45))
            
            station_data = {
                "city": city_name,
                "city_en": self.thai_cities[city_name]["en"],
                "coordinates": {
                    "latitude": lat,
                    "longitude": lon
                },
                "AQI": min(base_aqi, 150),  # จำกัดไม่ให้สูงเกินไป
                "PM2.5": round(pm25, 1),
                "PM10": round(pm10, 1),
                "O3": round(o3, 1),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_source": "จำลอง (Simulated)"
            }
            
            return station_data
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการดึงข้อมูล {city_name}: {e}")
            return None
    
    def get_thailand_air_quality(self):
        """ดึงข้อมูลคุณภาพอากาศจากเมืองต่างๆ ในประเทศไทย"""
        print("กำลังดึงข้อมูลคุณภาพอากาศจากเมืองต่างๆ ในประเทศไทย...")
        
        thailand_data = {
            "timestamp": datetime.now().isoformat(),
            "country": "ประเทศไทย",
            "data_source": "จำลองข้อมูลสำหรับการทดสอบ",
            "note": "ข้อมูลนี้เป็นการจำลองเพื่อการทดสอบโปรแกรม ไม่ใช่ข้อมูลจริง",
            "stations": []
        }
        
        for city_th, info in self.thai_cities.items():
            print(f"กำลังดึงข้อมูล {city_th}...")
            
            city_data = self.get_openweather_aqi(
                info["lat"], 
                info["lon"], 
                city_th
            )
            
            if city_data:
                thailand_data["stations"].append(city_data)
                aqi_level = self.get_aqi_level_description(city_data["AQI"])
                print(f"✓ {city_th}: AQI {city_data['AQI']} ({aqi_level})")
            else:
                print(f"✗ ไม่สามารถดึงข้อมูล {city_th} ได้")
        
        return thailand_data
    
    def get_thailand_summary(self, data):
        """สรุปข้อมูลคุณภาพอากาศของประเทศไทย"""
        if not data.get('stations'):
            return None
        
        stations = data['stations']
        summary = {
            "timestamp": data['timestamp'],
            "country": data['country'],
            "data_source": data['data_source'],
            "note": data.get('note', ''),
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
    
    def get_aqi_level_description(self, aqi):
        """แปลงค่า AQI เป็นคำอธิบายภาษาไทย"""
        if aqi is None:
            return "ไม่มีข้อมูล"
        elif aqi <= 50:
            return "ดี"
        elif aqi <= 100:
            return "ปานกลาง"
        elif aqi <= 150:
            return "ไม่ดีต่อกลุ่มเสี่ยง"
        elif aqi <= 200:
            return "ไม่ดี"
        elif aqi <= 300:
            return "แย่มาก"
        else:
            return "อันตราย"
    
    def get_aqi_color(self, aqi):
        """กำหนดสีตาม AQI"""
        if aqi is None:
            return "เทา"
        elif aqi <= 50:
            return "เขียว"
        elif aqi <= 100:
            return "เหลือง"
        elif aqi <= 150:
            return "ส้ม"
        elif aqi <= 200:
            return "แดง"
        elif aqi <= 300:
            return "ม่วง"
        else:
            return "น้ำตาลแดง"
    
    def save_to_json(self, data, filename="thailand_air_quality.json"):
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
    
    def display_summary(self, summary):
        """แสดงสรุปข้อมูลในรูปแบบที่อ่านง่าย"""
        print("\n" + "="*60)
        print("📊 สรุปข้อมูลคุณภาพอากาศในประเทศไทย")
        print("="*60)
        
        print(f"🕐 เวลาที่ดึงข้อมูล: {summary['timestamp'][:19]}")
        print(f"📍 จำนวนเมืองที่ตรวจวัด: {summary['total_stations']} เมือง")
        print(f"📊 แหล่งข้อมูล: {summary['data_source']}")
        
        if summary.get('note'):
            print(f"⚠️  หมายเหตุ: {summary['note']}")
        
        print("\n📈 ค่าเฉลี่ยทั่วประเทศ:")
        avg_aqi = summary['average_AQI']
        aqi_level = self.get_aqi_level_description(avg_aqi)
        aqi_color = self.get_aqi_color(avg_aqi)
        
        print(f"   AQI: {avg_aqi} ({aqi_level} - {aqi_color})")
        print(f"   PM2.5: {summary['average_PM2.5']} μg/m³")
        print(f"   PM10: {summary['average_PM10']} μg/m³")
        print(f"   O3: {summary['average_O3']} μg/m³")
        
        print("\n🏙️ รายละเอียดแต่ละเมือง:")
        print("-" * 60)
        
        for station in summary['stations_data']:
            aqi = station['AQI']
            level = self.get_aqi_level_description(aqi)
            color = self.get_aqi_color(aqi)
            
            print(f"📍 {station['city']:<12} | AQI: {aqi:>3} ({level:<15}) | PM2.5: {station['PM2.5']:>5} μg/m³")
        
        print("\n💡 คำแนะนำ:")
        if avg_aqi <= 50:
            print("   ✅ คุณภาพอากาศดี เหมาะสำหรับกิจกรรมกลางแจ้ง")
        elif avg_aqi <= 100:
            print("   ⚠️  คุณภาพอากาศปานกลาง ควรระวังสำหรับผู้ที่มีปัญหาระบบหายใจ")
        elif avg_aqi <= 150:
            print("   🚨 คุณภาพอากาศไม่ดีต่อกลุ่มเสี่ยง ควรหลีกเลี่ยงกิจกรรมกลางแจ้งนาน")
        else:
            print("   ❌ คุณภาพอากาศไม่ดี ควรอยู่ในที่ร่มและสวมหน้ากาก")
    
    def run(self):
        """เรียกใช้งานโปรแกรมหลัก"""
        print("🌤️  โปรแกรมตรวจสอบคุณภาพอากาศในประเทศไทย")
        print("=" * 50)
        
        # สร้างโฟลเดอร์ output
        self.create_output_directory()
        
        # ดึงข้อมูลคุณภาพอากาศ
        thailand_data = self.get_thailand_air_quality()
        
        # สรุปข้อมูล
        summary = self.get_thailand_summary(thailand_data)
        
        if summary and summary['total_stations'] > 0:
            # แสดงผลสรุป
            self.display_summary(summary)
            
            # บันทึกข้อมูล
            success = self.save_to_json(summary)
            
            if success:
                print(f"\n💾 ข้อมูลถูกบันทึกในไฟล์ {self.output_dir}/thailand_air_quality.json")
                return True
        else:
            print("❌ ไม่สามารถดึงข้อมูลคุณภาพอากาศได้")
            return False

def main():
    client = SimpleAQIClient()
    client.run()

if __name__ == "__main__":
    main() 