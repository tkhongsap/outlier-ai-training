import pandas as pd
import csv
import os
import requests

from pythainlp.tokenize import word_tokenize

url = "http://legacy.orst.go.th/?knowledges=%E0%B8%84%E0%B8%B3%E0%B8%82%E0%B8%A7%E0%B8%B1%E0%B8%8D%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%88%E0%B8%B3%E0%B8%88%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%A7%E0%B8%B1%E0%B8%94-%E0%B9%81%E0%B8%A5%E0%B8%B0%E0%B8%95"


def read_html_tables(url):
    """
    ดึงข้อมูลตารางจากเว็บไซต์โดยใช้ requests และ pandas.read_html พร้อมจัดการ encoding ภาษาไทย
    :param url: URL ที่ต้องการอ่านข้อมูล
    :return: ตารางทั้งหมดในรูปแบบชุดข้อมูล Pandas หรือ None ถ้าเกิดข้อผิดพลาด
    """
    try:
        # ใช้ requests เพื่อให้สามารถระบุ encoding ได้
        response = requests.get(url)
        response.encoding = 'utf-8'
        
        # อ่านตารางด้วย pandas
        tables = pd.read_html(response.text, encoding='utf-8')
        
        if len(tables) > 0:
            return tables
        else:
            raise ValueError("ไม่พบข้อมูลตารางในเว็บไซต์")
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอ่านข้อมูลจากเว็บไซต์: {str(e)}")
        return None


def tokenize(text):
    """
    แยกข้อความภาษาไทยเป็นคำๆ โดยใช้ pythainlp.tokenize ด้วยอัลกอริทึม newmm
    :param text: ข้อความที่ต้องการตัดคำ
    :return: ลิสต์ของคำทั้งหมดที่ตัดออกมา
    """
    if pd.isna(text):
        return []
    word_count = word_tokenize(str(text), engine="newmm", keep_whitespace=False)
    return word_count


def process_province_data(tables):
    """
    แปลงข้อมูลตารางจากเว็บไซต์ให้เป็น DataFrame ที่มีข้อมูลจังหวัด คำขวัญ ต้นไม้ และจำนวนคำ
    :param tables: ตารางข้อมูลจากเว็บไซต์
    :return: DataFrame ที่ประมวลผลแล้ว หรือ None ถ้าเกิดข้อผิดพลาด
    """
    try:
        # ดึงตารางแรก
        df = tables[0]
        
        # ตรวจสอบว่า encoding ถูกต้อง
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        
        # เปลี่ยนชื่อคอลัมน์
        df.rename(columns={0: "จังหวัด", 1: "ประเภท", 2: "ข้อมูล"}, inplace=True)
        
        # แยกข้อมูลคำขวัญและต้นไม้
        slogan_df = df[df["ประเภท"] == "คำขวัญ"].copy()
        tree_df = df[df["ประเภท"] == "ต้นไม้"].copy()
        
        # เปลี่ยนชื่อคอลัมน์
        slogan_df.rename(columns={"ข้อมูล": "คำขวัญประจำจังหวัด"}, inplace=True)
        tree_df.rename(columns={"ข้อมูล": "ต้นไม้ประจำจังหวัด"}, inplace=True)
        
        # รวมข้อมูลโดยใช้จังหวัดเป็นคีย์
        result_df = pd.merge(
            slogan_df[["จังหวัด", "คำขวัญประจำจังหวัด"]],
            tree_df[["จังหวัด", "ต้นไม้ประจำจังหวัด"]],
            on="จังหวัด",
            how="outer"
        )
        
        # นับจำนวนคำในคำขวัญและต้นไม้ด้วยการตัดคำภาษาไทย
        result_df["คำในคำขวัญ"] = result_df["คำขวัญประจำจังหวัด"].apply(tokenize)
        result_df["จำนวนคำของคำขวัญประจำจังหวัด"] = result_df["คำในคำขวัญ"].apply(len)
        
        result_df["คำในต้นไม้"] = result_df["ต้นไม้ประจำจังหวัด"].apply(tokenize)
        result_df["จำนวนคำของต้นไม้ประจำจังหวัด"] = result_df["คำในต้นไม้"].apply(len)
        
        # ลบคอลัมน์ที่ไม่จำเป็น
        result_df = result_df.drop(["คำในคำขวัญ", "คำในต้นไม้"], axis=1)
        
        # เรียงลำดับตามชื่อจังหวัด
        result_df = result_df.sort_values("จังหวัด")
        
        return result_df
    
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการประมวลผลข้อมูล: {str(e)}")
        return None


def save_to_csv(df, filename):
    """
    บันทึก DataFrame เป็นไฟล์ CSV โดยใช้ encoding UTF-8-SIG เพื่อรองรับการแสดงภาษาไทยในโปรแกรมต่างๆ
    :param df: DataFrame ที่ต้องการบันทึก
    :param filename: ชื่อไฟล์ CSV ที่ต้องการบันทึก (ไม่รวมนามสกุล)
    """
    try:
        csv_path = f"{filename}.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"บันทึกข้อมูลลงในไฟล์ {csv_path} สำเร็จ")
        print(f"ตำแหน่งของไฟล์: {os.path.abspath(csv_path)}")
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการบันทึกไฟล์: {str(e)}")


if __name__ == '__main__':
    try:
        # อ่านข้อมูลจากเว็บไซต์
        tables = read_html_tables(url)
        
        if tables:
            # ประมวลผลข้อมูล
            result_df = process_province_data(tables)
            
            if result_df is not None:
                # แสดงข้อมูลที่ประมวลผล
                print("ข้อมูลที่ประมวลผล:")
                print(result_df)
                
                # บันทึกข้อมูลลงในไฟล์ CSV
                save_to_csv(result_df, "thai_province_slogans")
    
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการทำงานของโปรแกรม: {str(e)}")