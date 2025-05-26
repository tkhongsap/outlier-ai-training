#!/usr/bin/env python3
import subprocess
import json
import os
from dotenv import load_dotenv

load_dotenv()

def run_glab_command(cmd):
    """รัน glab command และคืนค่าผลลัพธ์"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return None

def main():
    """วิธีที่ 2: ใช้ GitLab CLI (glab) - สั้นและเร็วกว่า"""
    print("🚀 วิธีที่ 2: ใช้ GitLab CLI (glab)")
    print("=" * 50)
    
    # ตั้งค่า GitLab URL และ Token
    gitlab_url = os.getenv('GITLAB_URL')
    gitlab_token = os.getenv('GITLAB_API_TOKEN')
    
    if not gitlab_url or not gitlab_token:
        print("Error: ต้องตั้งค่า GITLAB_URL และ GITLAB_API_TOKEN ในไฟล์ .env")
        return
    
    # ตั้งค่า glab config
    run_glab_command(f'glab config set gitlab_uri {gitlab_url}')
    run_glab_command(f'glab config set token {gitlab_token}')
    
    # หา group ID
    group_output = run_glab_command('glab api groups --paginate | jq -r \'.[] | select(.name=="Research Repos") | .id\'')
    if not group_output:
        print("ไม่เจอ group 'Research Repos'")
        return
    
    group_id = group_output.strip()
    print(f"เจอ group ID: {group_id}")
    
    # ดึงรายชื่อ projects และเปลี่ยน branch ในคำสั่งเดียว
    script = f'''
    glab api groups/{group_id}/projects --paginate | jq -r '.[].id' | while read project_id; do
        project_name=$(glab api projects/$project_id | jq -r '.name')
        echo "กำลังประมวลผล: $project_name (ID: $project_id)"
        
        # เช็คว่ามี trunk branch ไหม
        if glab api projects/$project_id/repository/branches/trunk >/dev/null 2>&1; then
            # เช็คว่ามี main branch แล้วไหม
            if ! glab api projects/$project_id/repository/branches/main >/dev/null 2>&1; then
                # สร้าง main จาก trunk
                glab api projects/$project_id/repository/branches --method POST --field branch=main --field ref=trunk
                # ตั้ง main เป็น default
                glab api projects/$project_id --method PUT --field default_branch=main
                # ลบ trunk
                glab api projects/$project_id/repository/branches/trunk --method DELETE
                echo "  ✓ เปลี่ยน trunk → main สำเร็จ"
            else
                echo "  - main branch มีอยู่แล้ว"
            fi
        else
            echo "  - ไม่มี trunk branch"
        fi
        sleep 0.3
    done
    '''
    
    print("กำลังเปลี่ยนชื่อ branch ทั้งหมด...")
    result = run_glab_command(script)
    
    if result is not None:
        print("\n🎉 เสร็จสิ้น! ใช้ GitLab CLI ทำงานเร็วกว่ามาก")
    else:
        print("\n❌ เกิดข้อผิดพลาด")

if __name__ == "__main__":
    main() 