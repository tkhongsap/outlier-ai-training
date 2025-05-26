#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
โปรแกรมดึงข้อมูลคุณภาพอากาศในประเทศไทยจาก aqi.in
วิธีที่ 1: Web Scraping
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time

class AQIScraper:
    def __init__(self):
        self.base_url = "https://www.aqi.in/dashboard/thailand"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.output_dir = "output"
        
    def create_output_directory(self):
        """สร้างโฟลเดอร์ output หากยังไม่มี"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"สร้างโฟลเดอร์ {self.output_dir} เรียบร้อยแล้ว")
    
    def fetch_page_content(self):
        """ดึงข้อมูล HTML จากเว็บไซต์"""
        try:
            print("กำลังดึงข้อมูลจาก aqi.in...")
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
            return None
    
    def parse_air_quality_data(self, html_content):
        """แยกข้อมูลคุณภาพอากาศจาก HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        air_quality_data = {
            "timestamp": datetime.now().isoformat(),
            "country": "Thailand",
            "data_source": "aqi.in",
            "stations": []
        }
        
        try:
            # ค้นหาข้อมูลสถานีต่างๆ ในประเทศไทย
            station_cards = soup.find_all('div', class_=['station-card', 'city-card', 'location-card'])
            
            if not station_cards:
                # ลองหาด้วย pattern อื่น
                station_cards = soup.find_all('div', attrs={'data-city': True})
            
            for card in station_cards:
                station_data = self.extract_station_data(card)
                if station_data:
                    air_quality_data["stations"].append(station_data)
            
            # หากไม่พบข้อมูลจาก card ให้ลองหาจาก table
            if not air_quality_data["stations"]:
                table_data = self.extract_table_data(soup)
                air_quality_data["stations"].extend(table_data)
                
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการแยกข้อมูล: {e}")
        
        return air_quality_data
    
    def extract_station_data(self, card):
        """แยกข้อมูลจากการ์ดของแต่ละสถานี"""
        try:
            station_info = {}
            
            # ชื่อสถานี
            name_elem = card.find(['h3', 'h4', 'h5', 'div'], class_=['city-name', 'station-name', 'location-name'])
            if name_elem:
                station_info['station_name'] = name_elem.get_text(strip=True)
            
            # AQI
            aqi_elem = card.find(['span', 'div'], class_=['aqi-value', 'aqi-number'])
            if aqi_elem:
                try:
                    station_info['AQI'] = int(aqi_elem.get_text(strip=True))
                except ValueError:
                    station_info['AQI'] = None
            
            # PM2.5
            pm25_elem = card.find(text=lambda text: text and 'PM2.5' in text)
            if pm25_elem:
                pm25_value = self.extract_numeric_value(pm25_elem.parent)
                station_info['PM2.5'] = pm25_value
            
            # PM10
            pm10_elem = card.find(text=lambda text: text and 'PM10' in text)
            if pm10_elem:
                pm10_value = self.extract_numeric_value(pm10_elem.parent)
                station_info['PM10'] = pm10_value
            
            # O3 (โอโซน)
            o3_elem = card.find(text=lambda text: text and 'O3' in text)
            if o3_elem:
                o3_value = self.extract_numeric_value(o3_elem.parent)
                station_info['O3'] = o3_value
            
            return station_info if len(station_info) > 1 else None
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการแยกข้อมูลสถานี: {e}")
            return None
    
    def extract_table_data(self, soup):
        """แยกข้อมูลจากตาราง"""
        stations = []
        try:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # ข้าม header row
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        station_data = {
                            'station_name': cells[0].get_text(strip=True),
                            'AQI': self.safe_int_convert(cells[1].get_text(strip=True)),
                            'PM2.5': self.safe_float_convert(cells[2].get_text(strip=True)) if len(cells) > 2 else None,
                            'PM10': self.safe_float_convert(cells[3].get_text(strip=True)) if len(cells) > 3 else None,
                            'O3': self.safe_float_convert(cells[4].get_text(strip=True)) if len(cells) > 4 else None
                        }
                        stations.append(station_data)
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการแยกข้อมูลจากตาราง: {e}")
        
        return stations
    
    def extract_numeric_value(self, element):
        """แยกค่าตัวเลขจาก element"""
        try:
            text = element.get_text(strip=True)
            # หาตัวเลขในข้อความ
            import re
            numbers = re.findall(r'\d+\.?\d*', text)
            return float(numbers[0]) if numbers else None
        except:
            return None
    
    def safe_int_convert(self, value):
        """แปลงค่าเป็น int อย่างปลอดภัย"""
        try:
            return int(float(value.replace(',', '').strip()))
        except:
            return None
    
    def safe_float_convert(self, value):
        """แปลงค่าเป็น float อย่างปลอดภัย"""
        try:
            return float(value.replace(',', '').strip())
        except:
            return None
    
    def save_to_json(self, data, filename="air_quality_data.json"):
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
    
    def get_thailand_summary(self, data):
        """สรุปข้อมูลคุณภาพอากาศของประเทศไทย"""
        if not data.get('stations'):
            return None
        
        stations = data['stations']
        summary = {
            "timestamp": data['timestamp'],
            "country": "Thailand",
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
    
    def run(self):
        """เรียกใช้งานโปรแกรมหลัก"""
        print("=== โปรแกรมดึงข้อมูลคุณภาพอากาศในประเทศไทย (Web Scraping) ===")
        
        # สร้างโฟลเดอร์ output
        self.create_output_directory()
        
        # ดึงข้อมูลจากเว็บไซต์
        html_content = self.fetch_page_content()
        if not html_content:
            print("ไม่สามารถดึงข้อมูลจากเว็บไซต์ได้")
            return False
        
        # แยกข้อมูลคุณภาพอากาศ
        air_quality_data = self.parse_air_quality_data(html_content)
        
        # สรุปข้อมูลประเทศไทย
        thailand_summary = self.get_thailand_summary(air_quality_data)
        
        if thailand_summary and thailand_summary['total_stations'] > 0:
            # บันทึกข้อมูลลงไฟล์
            success = self.save_to_json(thailand_summary)
            
            if success:
                print("\n=== สรุปข้อมูลคุณภาพอากาศในประเทศไทย ===")
                print(f"จำนวนสถานีตรวจวัด: {thailand_summary['total_stations']} สถานี")
                print(f"AQI เฉลี่ย: {thailand_summary['average_AQI']}")
                print(f"PM2.5 เฉลี่ย: {thailand_summary['average_PM2.5']} μg/m³")
                print(f"PM10 เฉลี่ย: {thailand_summary['average_PM10']} μg/m³")
                print(f"O3 เฉลี่ย: {thailand_summary['average_O3']} μg/m³")
                print(f"เวลาที่ดึงข้อมูล: {thailand_summary['timestamp']}")
                return True
        else:
            print("ไม่พบข้อมูลคุณภาพอากาศในประเทศไทย")
            return False

def main():
    scraper = AQIScraper()
    scraper.run()

if __name__ == "__main__":
    main() 