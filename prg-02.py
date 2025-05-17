import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from datetime import datetime

def create_zones_gdf(zones):
    """
    สร้าง GeoDataFrame จากรูปหลายเหลี่ยมของโซน
    
    พารามิเตอร์
        zones: พจนานุกรมของ zone_name
        
    ส่งคืน
        GeoDataFrame ที่มีรูปหลายเหลี่ยมของโซน
    """
    zone_data = []
    
    for zone_name, coordinates in zones.items():
        polygon = Polygon(coordinates)
        zone_data.append({
            'zone_name': zone_name,
            'geometry': polygon
        })
    
    return gpd.GeoDataFrame(zone_data)

def track_zone_transitions_geopandas(bird_df, zones_gdf, timestamp_col=None):
    """
    ติดตามเวลาที่นกเข้าหรือออกจากโซนที่กำหนดโดยใช้ GeoPandas
    
    พารามิเตอร์
        bird_df: DataFrame ที่มีคอลัมน์ 'latitude' และ 'longitude'
        zones_gdf: GeoDataFrame ที่มีรูปหลายเหลี่ยมของโซน
        timestamp_col: ชื่อคอลัมน์เวลาใน bird_df (ไม่บังคับ)
        
    ส่งคืน:
        รายการของพจนานุกรมที่ระบุเหตุการณ์การเปลี่ยนโซน
    """
    # แปลงตำแหน่งของนกเป็น GeoDataFrame
    geometry = [Point(xy) for xy in zip(bird_df['longitude'], bird_df['latitude'])]
    bird_gdf = gpd.GeoDataFrame(bird_df.copy(), geometry=geometry)
    
    transitions = []
    
    # สำหรับแต่ละโซน ตรวจสอบการเปลี่ยนแปลงที่เกิดขึ้น
    for _, zone_row in zones_gdf.iterrows():
        zone_name = zone_row['zone_name']
        
        # ตรวจสอบว่าจุดใดอยู่ในโซน
        bird_gdf[f'in_{zone_name}'] = bird_gdf['geometry'].within(zone_row['geometry'])
        
        # หาการเปลี่ยนโซนโดยเปรียบเทียบกับค่าก่อนหน้า
        bird_gdf[f'prev_in_{zone_name}'] = bird_gdf[f'in_{zone_name}'].shift(1).fillna(False)
        
        # เหตุการณ์เข้าโซน
        entries = bird_gdf[(bird_gdf[f'in_{zone_name}'] == True) & 
                           (bird_gdf[f'prev_in_{zone_name}'] == False)]
        
        # เหตุการณ์ออกจากโซน
        exits = bird_gdf[(bird_gdf[f'in_{zone_name}'] == False) & 
                          (bird_gdf[f'prev_in_{zone_name}'] == True)]
        
        # บันทึกการเปลี่ยนโซน
        for idx, row in entries.iterrows():
            event = {
                'index': idx,
                'zone': zone_name,
                'event': 'entry'
            }
            if timestamp_col and timestamp_col in row:
                event['timestamp'] = row[timestamp_col]
            transitions.append(event)
            
        for idx, row in exits.iterrows():
            event = {
                'index': idx,
                'zone': zone_name,
                'event': 'exit'
            }
            if timestamp_col and timestamp_col in row:
                event['timestamp'] = row[timestamp_col]
            transitions.append(event)
    
    # เรียงลำดับการเปลี่ยนโซนตามดัชนี/เวลา
    if transitions and 'timestamp' in transitions[0]:
        transitions.sort(key=lambda x: x['timestamp'])
    else:
        transitions.sort(key=lambda x: x['index'])
    
    return transitions

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    # ข้อมูลตัวอย่าง
    bird_data = {
        'latitude': [40.7128, 41.8781, 34.0522, 37.7749, 29.7604],
        'longitude': [-74.0060, -87.6298, -118.2437, -122.4194, -95.3698],
        'timestamp': [
            datetime(2023, 1, 1, 8, 0, 0),
            datetime(2023, 1, 2, 9, 30, 0),
            datetime(2023, 1, 3, 14, 15, 0),
            datetime(2023, 1, 4, 11, 45, 0),
            datetime(2023, 1, 5, 16, 20, 0),
        ]
    }
    
    bird_df = pd.DataFrame(bird_data)
    
    # กำหนดโซนตัวอย่าง
    zones = {
        'ชายฝั่งตะวันตก': [
            (-125.0, 33.0),
            (-115.0, 33.0),
            (-115.0, 42.0),
            (-125.0, 42.0)
        ],
        'ชายฝั่งตะวันออก': [
            (-82.0, 37.0),
            (-70.0, 37.0),
            (-70.0, 45.0),
            (-82.0, 45.0)
        ]
    }
    
    # สร้าง GeoDataFrame สำหรับโซน
    zones_gdf = create_zones_gdf(zones)
    
    # ติดตามการเปลี่ยนโซน
    transitions = track_zone_transitions_geopandas(bird_df, zones_gdf, 'timestamp')
    
    # แสดงผลลัพธ์
    for event in transitions:
        event_type = "เข้า" if event['event'] == 'entry' else "ออกจาก"
        print(f"นก{event_type}โซน{event['zone']} เมื่อ {event['timestamp']}")