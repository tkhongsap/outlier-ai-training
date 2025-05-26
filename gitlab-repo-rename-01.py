#!/usr/bin/env python3
import os
import sys
import requests
from dotenv import load_dotenv
import time

OLD_BRANCH = "trunk"
NEW_BRANCH = "main"
REQUEST_DELAY = 0.3  # วินาทีระหว่าง API calls เพื่อไม่ให้โดน rate limit

load_dotenv()
gitlab_url = os.getenv('GITLAB_URL')
gitlab_token = os.getenv('GITLAB_API_TOKEN')

if not gitlab_url or not gitlab_token:
    print("Error: ต้องตั้งค่า GITLAB_URL และ GITLAB_API_TOKEN ในไฟล์ .env")
    print("กรุณาสร้างไฟล์ .env ตาม .env.example")
    sys.exit(1)

base_api_url = f"{gitlab_url.rstrip('/')}/api/v4"
session = requests.Session()
session.headers.update({
    'Private-Token': gitlab_token,
    'Content-Type': 'application/json'
})

def get_subgroup_id(subgroup_name):
    """หา subgroup ID จากชื่อ"""
    try:
        response = session.get(f"{base_api_url}/groups", params={'search': subgroup_name})
        response.raise_for_status()
        for group in response.json():
            if group['name'] == subgroup_name:
                return group['id']
        print(f"Error: ไม่เจอ subgroup '{subgroup_name}'")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error ดึงข้อมูล subgroup: {e}")
        return None

def get_projects_for_subgroup(subgroup_id):
    """ดึงโปรเจกต์ทั้งหมดใน subgroup"""
    try:
        projects = []
        page = 1
        while True:
            response = session.get(
                f"{base_api_url}/groups/{subgroup_id}/projects",
                params={'page': page, 'per_page': 100, 'include_subgroups': True}
            )
            response.raise_for_status()
            batch = response.json()
            if not batch:
                break
            projects.extend(batch)
            page += 1
        return projects
    except requests.exceptions.RequestException as e:
        print(f"Error ดึงข้อมูลโปรเจกต์: {e}")
        return []

def check_branch_exists(project_id, branch_name):
    """เช็คว่า branch มีอยู่ไหม"""
    try:
        response = session.get(f"{base_api_url}/projects/{project_id}/repository/branches/{branch_name}")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def rename_branch(project_id, project_name, old_branch, new_branch):
    """เปลี่ยนชื่อ branch ใน GitLab project"""
    try:
        if not check_branch_exists(project_id, old_branch):
            print(f"  - ไม่เจอ branch '{old_branch}' ในโปรเจกต์ '{project_name}'")
            return False
        if check_branch_exists(project_id, new_branch):
            print(f"  - branch '{new_branch}' มีอยู่แล้วในโปรเจกต์ '{project_name}'")
            return False
        
        session.post(
            f"{base_api_url}/projects/{project_id}/repository/branches",
            params={'branch': new_branch, 'ref': old_branch}
        ).raise_for_status()
        session.put(
            f"{base_api_url}/projects/{project_id}",
            json={'default_branch': new_branch}
        ).raise_for_status()
        session.delete(
            f"{base_api_url}/projects/{project_id}/repository/branches/{old_branch}"
        ).raise_for_status()
        
        print(f"  ✓ เปลี่ยนชื่อ '{old_branch}' เป็น '{new_branch}' ในโปรเจกต์ '{project_name}' สำเร็จ")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  × Error เปลี่ยนชื่อ branch ในโปรเจกต์ '{project_name}': {e}")
        return False

def process_group(group_name):
    """ประมวลผลโปรเจกต์ทั้งหมดใน group เพื่อเปลี่ยนชื่อ branch"""
    print(f"\nกำลังประมวลผล group: {group_name}")
    print("-" * 50)
    
    group_id = get_subgroup_id(group_name)
    if not group_id:
        return False
    
    projects = get_projects_for_subgroup(group_id)
    if not projects:
        print(f"ไม่เจอโปรเจกต์ใน group '{group_name}'")
        return False
    
    print(f"เจอ {len(projects)} โปรเจกต์ใน group '{group_name}'")
    
    success_count = 0
    for project in projects:
        print(f"\nกำลังประมวลผลโปรเจกต์: {project['name']} (ID: {project['id']})")
        if rename_branch(project['id'], project['name'], OLD_BRANCH, NEW_BRANCH):
            success_count += 1
        time.sleep(REQUEST_DELAY)
    
    print(f"\nสรุปผลลัพธ์ '{group_name}': เปลี่ยนชื่อสำเร็จ {success_count} จาก {len(projects)} โปรเจกต์")
    return True

def main():
    """ฟังก์ชันหลักสำหรับประมวลผล Research Repos group"""
    print(f"เครื่องมือเปลี่ยนชื่อ Branch ใน GitLab: '{OLD_BRANCH}' → '{NEW_BRANCH}'")
    print("=" * 60)
    
    group_name = "Research Repos"
    if process_group(group_name):
        print(f"\nประมวลผล group '{group_name}' สำเร็จ!")
    else:
        print(f"\nประมวลผล group '{group_name}' ไม่สำเร็จ")

if __name__ == "__main__":
    main()