import os, sys, requests, base64
from dotenv import load_dotenv
from openai import OpenAI
from urllib.parse import urlparse

# โหลดตัวแปรสภาพแวดล้อม
load_dotenv()

# ฟังก์ชันสำหรับแยกวิเคราะห์รูปภาพ
def parse_image(img_path, out_dir, prompt=None):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("Error: Missing OpenAI API key in .env file")
    
    prompt = prompt or "Extract all text and information from this image"
    client = OpenAI(api_key=api_key)
    img_name = os.path.basename(img_path)
    out_file = os.path.join(out_dir, f"{os.path.splitext(img_name)[0]}_parsed.md")
    
    try:
        with open(img_path, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode('utf-8')
        
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "Analyze this image:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]}
            ],
            max_tokens=1000
        )
        
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(resp.choices[0].message.content)
        print(f"✓ Analysis saved to {out_file}")
        return out_file
    except Exception as e:
        print(f"✗ Error processing image: {str(e)}")
        return None

# ฟังก์ชันสำหรับดาวน์โหลดรูปภาพจาก URL
def download_image(url, save_dir):
    filename = os.path.basename(urlparse(url).path) or "downloaded_image.jpeg"
    filepath = os.path.join(save_dir, filename)
    
    resp = requests.get(url, stream=True)
    if resp.status_code == 200:
        with open(filepath, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return filepath
    return None

def main():
    in_dir, out_dir = "data", "output"
    os.makedirs(in_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    
    default_url = "https://docelf.com/images/free_receipt_template_xs.png"
    
    # Prompt for user input
    user_url = input(f"Enter image URL (or press Enter to use default: {default_url}): ").strip()
    
    # Use default if no input provided
    url = user_url if user_url else default_url
    print(f"Using image: {url}")
    
    img_path = download_image(url, in_dir)
    if not img_path:
        sys.exit("Failed to download image")
        
    result = parse_image(img_path, out_dir)
    print("Analysis complete!" if result else "Analysis failed.")

if __name__ == "__main__":
    main()
