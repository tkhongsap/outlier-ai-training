from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from transformers import pipeline
import requests
from io import BytesIO

image_url = "https://i.imgur.com/R0PuhAp.jpg"

pipe = pipeline(model='microsoft/trocr-large-printed')

def trocr_extract(file_path=None, image=None):
    if image is None and file_path:
        img = Image.open(file_path).convert('L')
    elif image:
        img = image.convert('L')
    else:
        raise ValueError("Either file_path or image must be provided")
    
    lst_raw_text = pipe(img)
    text_result = lst_raw_text[0]['generated_text']
    text_result = text_result.replace(' ', '')
    text_result = text_result.replace('.', '')
    return text_result

def process_image_from_url(url):
    print(f"Downloading image from: {url}")
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    print("Processing image with TrOCR...")
    result = trocr_extract(image=img)
    print(f"Extracted text: {result}")
    return result

if __name__ == "__main__":
    process_image_from_url(image_url)