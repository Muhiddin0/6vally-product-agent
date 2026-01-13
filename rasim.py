import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = """
1-rasimdagi posterdan andoza olib 2-rasimdagi maxsulot uchun poster yaratib ber.

2-rasimdagi maxsulotning parametrlari
DDR4 8GB
SSD 256 GB
Intel N4000
Экран: 14 дюймов HD 
"""

result = client.images.edit(
    model="gpt-image-1",
    image=[
        open("mask.png", "rb"),
        open("poster.png", "rb"),
    ],
    size="1024x1536",
    prompt=prompt,
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("gift-basket.png", "wb") as f:
    f.write(image_bytes)
