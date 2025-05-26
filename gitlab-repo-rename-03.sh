#!/bin/bash

# วิธีที่ 3: Pure Shell Script - สั้นที่สุด!
echo "🚀 วิธีที่ 3: Pure Shell Script (สั้นที่สุด!)"
echo "================================================"

# โหลดตัวแปรจาก .env
source .env

# ตั้งค่า glab
glab config set gitlab_uri $GITLAB_URL
glab config set token $GITLAB_API_TOKEN

# หา group ID และเปลี่ยน branch ในคำสั่งเดียว
GROUP_ID=$(glab api groups --paginate | jq -r '.[] | select(.name=="Research Repos") | .id')

echo "เจอ group ID: $GROUP_ID"
echo "กำลังเปลี่ยนชื่อ branch ทั้งหมด..."

# ลูปผ่านทุก project และเปลี่ยน trunk → main
glab api groups/$GROUP_ID/projects --paginate | jq -r '.[].id' | while read PROJECT_ID; do
    PROJECT_NAME=$(glab api projects/$PROJECT_ID | jq -r '.name')
    echo "กำลังประมวลผล: $PROJECT_NAME (ID: $PROJECT_ID)"
    
    # เช็คและเปลี่ยน branch
    if glab api projects/$PROJECT_ID/repository/branches/trunk >/dev/null 2>&1; then
        if ! glab api projects/$PROJECT_ID/repository/branches/main >/dev/null 2>&1; then
            glab api projects/$PROJECT_ID/repository/branches --method POST --field branch=main --field ref=trunk
            glab api projects/$PROJECT_ID --method PUT --field default_branch=main
            glab api projects/$PROJECT_ID/repository/branches/trunk --method DELETE
            echo "  ✓ เปลี่ยน trunk → main สำเร็จ"
        else
            echo "  - main branch มีอยู่แล้ว"
        fi
    else
        echo "  - ไม่มี trunk branch"
    fi
    sleep 0.3
done

echo ""
echo "🎉 เสร็จสิ้น! Shell script ทำงานเร็วและสั้นที่สุด" 