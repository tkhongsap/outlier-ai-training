#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()
gitlab_url = os.getenv('GITLAB_URL')
gitlab_token = os.getenv('GITLAB_API_TOKEN')

if not gitlab_url or not gitlab_token:
    print("Error: ต้องตั้งค่า GITLAB_URL และ GITLAB_API_TOKEN ในไฟล์ .env")
    exit(1)

api = f"{gitlab_url.rstrip('/')}/api/v4"
headers = {'Private-Token': gitlab_token}

def api_call(method, endpoint, **kwargs):
    """เรียก GitLab API แบบสั้น"""
    response = requests.request(method, f"{api}/{endpoint}", headers=headers, **kwargs)
    return response.json() if response.status_code < 400 else None

def rename_branch(project_id, name):
    """เปลี่ยนชื่อ branch แบบสั้น"""
    print(f"ประมวลผล: {name}")
    
    # เช็ค trunk และ main
    trunk_exists = requests.get(f"{api}/projects/{project_id}/repository/branches/trunk", headers=headers).status_code == 200
    main_exists = requests.get(f"{api}/projects/{project_id}/repository/branches/main", headers=headers).status_code == 200
    
    if not trunk_exists:
        print("  - ไม่มี trunk")
        return False
    if main_exists:
        print("  - main มีแล้ว")
        return False
    
    # สร้าง main, ตั้งเป็น default, ลบ trunk
    try:
        api_call('POST', f"projects/{project_id}/repository/branches", params={'branch': 'main', 'ref': 'trunk'})
        api_call('PUT', f"projects/{project_id}", json={'default_branch': 'main'})
        api_call('DELETE', f"projects/{project_id}/repository/branches/trunk")
        print("  ✓ สำเร็จ")
        return True
    except:
        print("  × ผิดพลาด")
        return False

def main():
   
    # หา group
    groups = api_call('GET', 'groups', params={'search': 'Research Repos'})
    if not groups:
        print("ไม่เจอ group")
        return
    
    group_id = next((g['id'] for g in groups if g['name'] == 'Research Repos'), None)
    if not group_id:
        print("ไม่เจอ Research Repos")
        return
    
    # ดึง projects และประมวลผล
    projects = api_call('GET', f'groups/{group_id}/projects', params={'per_page': 100, 'include_subgroups': True})
    if not projects:
        print("ไม่เจอ projects")
        return
    
    print(f"เจอ {len(projects)} projects")
    success = sum(rename_branch(p['id'], p['name']) or time.sleep(0.3) or 0 for p in projects)
    print(f"\nสำเร็จ {success}/{len(projects)} projects")

if __name__ == "__main__":
    main() 