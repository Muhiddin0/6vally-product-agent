"""
Venu Marketplace Product Uploader
Avtomatik mahsulot yuklovchi AI agent class
"""

import requests
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import random
import string
from datetime import datetime
from html import escape
from collections import Counter

# Category selection uchun
from categories import select_category_brand

# OpenAI API uchun (ixtiyoriy)
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ProductUploaderAgent:
    """Avtomatik mahsulot yuklovchi AI agent"""

    BASE_URL = "https://theantique.uz/api/v3"

    # API_KEY ni environment variable yoki config fayldan olish tavsiya etiladi
    API_KEY = os.getenv("VENU_API_KEY", "XOjOXviWzeiEBdeULDZYRfCKdDk6fMNPjSgKhjLZ")

    def __init__(self, email: str, password: str):
        """
        Args:
            email: Do'kon email manzili
            password: Do'kon paroli
        """
        self.email = email
        self.password = password
        self.token = None
        self.categories = []
        self.brands = []
        self.attributes = []

    def login(self) -> bool:
        """Login qilib token olish"""
        url = f"{self.BASE_URL}/seller/auth/login"
        headers = {
            "accept-encoding": "gzip",
            "content-type": "application/json; charset=UTF-8",
            "authorization": f"Bearer {self.API_KEY}",
            "user-agent": "Python/requests",
        }
        data = {"email": self.email, "password": self.password}

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("token")
                if self.token:
                    print(f"✅ Muvaffaqiyatli login qilindi!")
                    return True
            print(f"❌ Login xatosi: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            print(f"❌ Login xatosi: {str(e)}")
            return False

    def get_categories(self) -> List[Dict]:
        """Kategoriyalarni olish"""
        if not self.token:
            print("❌ Avval login qiling!")
            return []

        url = f"{self.BASE_URL}/seller/categories"
        headers = {
            "accept-encoding": "gzip",
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json; charset=UTF-8",
            "lang": "en",
            "user-agent": "Python/requests",
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                self.categories = response.json()
                print(f"✅ {len(self.categories)} ta kategoriya yuklandi")
                return self.categories
            return []
        except Exception as e:
            print(f"❌ Kategoriyalarni olishda xato: {str(e)}")
            return []

    def get_brands(self) -> List[Dict]:
        """Brendlarni olish"""
        if not self.token:
            print("❌ Avval login qiling!")
            return []

        url = f"{self.BASE_URL}/seller/brands"
        headers = {
            "accept-encoding": "gzip",
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json; charset=UTF-8",
            "user-agent": "Python/requests",
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                self.brands = response.json()
                print(f"✅ {len(self.brands)} ta brend yuklandi")
                return self.brands
            return []
        except Exception as e:
            print(f"❌ Brendlarni olishda xato: {str(e)}")
            return []

    def get_attributes(self) -> List[Dict]:
        """Atributlarni olish"""
        if not self.token:
            print("❌ Avval login qiling!")
            return []

        url = f"https://api.venu.uz/api/v1/attributes"
        headers = {
            "accept-encoding": "gzip",
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json; charset=UTF-8",
            "lang": "en",
            "user-agent": "Python/requests",
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                self.attributes = response.json()
                print(f"✅ {len(self.attributes)} ta atribut yuklandi")
                return self.attributes
            return []
        except Exception as e:
            print(f"❌ Atributlarni olishda xato: {str(e)}")
            return []

    def _extract_brand_name(self, description: str, name: str) -> str:
        """Tavsif va nomdan brend nomini ajratish (categories.py uchun)"""
        # HTML taglarini olib tashlash
        plain_text = re.sub(r"<[^>]+>", "", description)
        text = (plain_text + " " + name).lower()

        # Mashhur brendlar ro'yxati
        brand_names = [
            "samsung",
            "apple",
            "iphone",
            "xiaomi",
            "huawei",
            "oppo",
            "vivo",
            "asus",
            "acer",
            "hp",
            "lenovo",
            "dell",
            "msi",
            "gigabyte",
            "sony",
            "lg",
            "nokia",
            "motorola",
            "realme",
            "oneplus",
            "redmi",
            "honor",
            "poco",
            "zte",
            "meizu",
        ]

        # Matndan brend nomini topish
        for brand in brand_names:
            if brand in text:
                return brand

        # Agar brend topilmasa, bo'sh qator qaytarish
        return ""

    def find_brand_by_name(self, description: str, name: str) -> Optional[int]:
        """Tavsif va nomdan brendni topish"""
        # HTML taglarini olib tashlash brend topish uchun
        plain_text = re.sub(r"<[^>]+>", "", description)
        text = (plain_text + " " + name).lower()

        # Mashhur brendlar
        brand_names = [
            "samsung",
            "apple",
            "iphone",
            "xiaomi",
            "huawei",
            "oppo",
            "vivo",
            "asus",
            "acer",
            "hp",
            "lenovo",
            "dell",
            "msi",
            "gigabyte",
            "sony",
            "lg",
            "nokia",
            "motorola",
            "realme",
            "oneplus",
            "redmi",
            "honor",
            "poco",
            "zte",
            "meizu",
        ]

        for brand in self.brands:
            brand_name = brand.get("name", "").lower()
            if brand_name in text:
                return brand.get("id")

        # Agar brend topilmasa, birinchi brendni qaytarish (yoki None)
        if self.brands:
            return self.brands[0].get("id")
        return None

    def generate_product_code(self) -> str:
        """Yangi mahsulot kodi generatsiya qilish"""
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def generate_product_name(self, description: str) -> str:
        """
        AI yordamida tavsifdan mahsulot nomini generatsiya qilish
        Qisqa, aniq, chunarli nom - bitta gap, hech qanday "..." lar yo'q

        Args:
            description: Mahsulot tavsifi (HTML yoki oddiy matn)

        Returns:
            str: Generatsiya qilingan mahsulot nomi (qisqa va aniq)
        """
        # HTML taglarini olib tashlash
        plain_text = self.strip_html_tags(description)

        # Qatorlarga bo'lish
        lines = [line.strip() for line in plain_text.split("\n") if line.strip()]

        if not lines:
            return "Yangi mahsulot"

        # Birinchi qatorni tekshirish - ko'pincha sarlavha bo'ladi
        first_line = lines[0]

        # Emoji va maxsus belgilarni olib tashlash
        first_line_clean = re.sub(r"[^\w\s\-|]", "", first_line).strip()

        # Agar birinchi qator juda qisqa yoki bo'sh bo'lsa, keyingi qatorlarni tekshirish
        if len(first_line_clean) < 5 or not first_line_clean:
            # Keyingi qatorlarni tekshirish
            for line in lines[1:6]:  # Keyingi 5 qatorni tekshirish
                clean_line = re.sub(r"[^\w\s\-|]", "", line).strip()
                if len(clean_line) >= 5:
                    first_line_clean = clean_line
                    break

        # Agar hali ham topilmasa, barcha matndan muhim so'zlarni ajratish
        if not first_line_clean or len(first_line_clean) < 5:
            # Barcha matndan muhim so'zlarni topish
            words = re.findall(r"\b\w{3,}\b", plain_text.lower())

            # Eng ko'p ishlatilgan so'zlarni topish (stop words'larni olib tashlash)
            stop_words = {
                "bu",
                "va",
                "uchun",
                "bilan",
                "ham",
                "yoki",
                "lekin",
                "agar",
                "qilib",
                "qilish",
                "qiladi",
                "bo'ladi",
                "bo'lishi",
                "kerak",
                "xususiyatlar",
                "ma'lumotlar",
                "qo'shimcha",
                "asosiy",
                "the",
                "and",
                "or",
                "with",
                "for",
                "from",
                "this",
                "that",
                "these",
                "those",
            }

            important_words = [w for w in words if w not in stop_words and len(w) > 3]

            if important_words:
                # Eng ko'p ishlatilgan so'zlar (maksimal 4 ta so'z - qisqa nom uchun)
                word_freq = Counter(important_words)
                top_words = [word for word, _ in word_freq.most_common(4)]
                first_line_clean = " ".join(top_words).title()

        # Nomni tozalash va formatlash
        name = first_line_clean.strip()

        # So'zlarga bo'lish va faqat muhim so'zlarni olish (maksimal 4-5 so'z)
        words = name.split()
        if len(words) > 10:
            # Faqat birinchi 5 ta so'zni olish
            name = " ".join(words[:10])

        # Ko'p bo'shliqlarni bitta bo'shliqqa o'zgartirish
        name = re.sub(r"\s+", " ", name).strip()

        # Agar hali ham bo'sh bo'lsa
        if not name or len(name) < 3:
            name = "Yangi mahsulot"

        # Birinchi harfni katta qilish
        name = name[0].upper() + name[1:] if len(name) > 1 else name.upper()

        # Hech qanday "..." lar bo'lmasligi kerak - agar uzun bo'lsa, so'zlar bo'yicha kesish
        # Lekin maksimal uzunlikni cheklash (60 belgi - qisqa va aniq)
        if len(name) > 60:
            words = name.split()
            name = ""
            for word in words:
                if len(name + " " + word) <= 60:
                    name += " " + word if name else word
                else:
                    break
            name = name.strip()

        return name

    def generate_tags_for_product(
        self, description: str, product_name: Optional[str] = None
    ) -> List[str]:
        """
        Mahsulot uchun AI yordamida teglar (tags) generatsiya qilish.

        Args:
            description: Mahsulot tavsifi (HTML bo'lishi mumkin)
            product_name: Mahsulot nomi (ixtiyoriy)

        Returns:
            List[str]: Teglar ro'yxati
        """
        # Tavsifni tozalash (plain text)
        plain_text = self.strip_html_tags(description)

        # OpenAI API mavjudligini tekshirish
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if OPENAI_AVAILABLE and openai_api_key:
            try:
                client = openai.OpenAI(api_key=openai_api_key)

                base_info = product_name or ""
                prompt = f"""You are an SEO specialist assistant.

You will be given product information (name and description).
Your task: generate 5–12 keywords (tags) for this product.

Rules:
1. Return only a single JSON array, for example:
   ["tag1", "tag2", "tag3"]
2. Each tag should be:
   - short (1–3 words)
   - in lowercase
   - without '#' symbol
3. Tags must be in English only. If the text is in another language, translate and adapt to English.
4. Pay attention to brand, category, material, style, and main features.

Product name: {base_info}
Product description:
{plain_text}

Return only the JSON array."""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an experienced SEO specialist. Return only a valid JSON array with English tags.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.4,
                    max_tokens=400,
                )

                content = response.choices[0].message.content.strip()

                # ```json bilan o'ralgan bo'lsa, tozalash
                content = re.sub(r"```json\s*", "", content, flags=re.IGNORECASE)
                content = re.sub(r"```\s*$", "", content).strip()

                tags = json.loads(content)
                if isinstance(tags, list):
                    # Har bir elementni stringga aylantirish va tozalash
                    clean_tags = []
                    for t in tags:
                        if not isinstance(t, str):
                            t = str(t)
                        t = t.strip().lower()
                        t = t.lstrip("#")
                        if t:
                            clean_tags.append(t)
                    # Dublikatlarni olib tashlash va bo'sh bo'lmasligini tekshirish
                    unique_tags = list(dict.fromkeys(clean_tags))
                    if unique_tags:
                        return unique_tags
            except Exception as e:
                print(
                    f"⚠️ AI orqali tag generatsiya qilishda xato: {str(e)}. Heuristik usulga o'tiladi..."
                )

        # Agar AI ishlamasa yoki natija noto'g'ri bo'lsa – heuristik yondashuv
        text = plain_text.lower()
        # So'zlarni ajratish
        words = re.findall(r"\b\w{3,}\b", text)

        # Stop-so'zlar (ru + uz aralash)
        stop_words = {
            "и",
            "в",
            "на",
            "с",
            "для",
            "от",
            "до",
            "по",
            "при",
            "над",
            "под",
            "это",
            "этот",
            "эта",
            "эти",
            "также",
            "как",
            "что",
            "то",
            "же",
            "bu",
            "va",
            "uchun",
            "bilan",
            "ham",
            "yoki",
            "lekin",
            "agar",
            "qilib",
            "qilish",
            "qiladi",
            "bo'ladi",
            "bo'lishi",
            "kerak",
            "xususiyatlar",
            "ma'lumotlar",
            "qo'shimcha",
            "asosiy",
        }

        keywords = [w for w in words if w not in stop_words and len(w) > 3]

        # Eng ko'p uchraydigan so'zlardan 5–10 tasini olish
        if keywords:
            freq = Counter(keywords)
            common = [word for word, _ in freq.most_common(10)]
        else:
            common = []

        # Mahsulot nomidan ham so'zlar qo'shish
        if product_name:
            name_words = re.findall(r"\b\w{3,}\b", product_name.lower())
            for w in name_words:
                if w not in stop_words and w not in common:
                    common.append(w)

        # Takroriy so'zlarni olib tashlash
        unique = list(dict.fromkeys(common))

        # Juda kam bo'lsa, default taglar qo'shish
        if not unique:
            unique = ["product", "item"]

        # 12 tadan oshirmaslik
        return unique[:12]

    def generate_meta_title(self, description: str, product_name: str = None) -> str:
        """
        AI yordamida SEO-friendly meta title generatsiya qilish

        Args:
            description: Mahsulot tavsifi
            product_name: Mahsulot nomi (ixtiyoriy)

        Returns:
            str: Generatsiya qilingan meta title (maksimal 60 belgi)
        """
        # HTML taglarini olib tashlash
        plain_text = self.strip_html_tags(description)

        # Agar product_name berilgan bo'lsa, undan foydalanish
        if product_name:
            base_title = product_name
        else:
            # Tavsifdan muhim so'zlarni ajratish
            lines = [line.strip() for line in plain_text.split("\n") if line.strip()]
            if lines:
                base_title = lines[0]
                # Emoji va maxsus belgilarni olib tashlash
                base_title = re.sub(r"[^\w\s\-|]", "", base_title).strip()
            else:
                base_title = "Mahsulot"

        # Meta title uchun optimallashtirish
        # 1. Kategoriya yoki brend so'zlarini qo'shish (agar mavjud bo'lsa)
        text_lower = plain_text.lower()

        # Mashhur brendlar va kategoriyalar
        brand_keywords = [
            "samsung",
            "apple",
            "iphone",
            "xiaomi",
            "huawei",
            "oppo",
            "vivo",
            "asus",
            "acer",
            "hp",
            "lenovo",
            "dell",
            "sony",
            "lg",
            "nokia",
        ]

        category_keywords = [
            "smartfon",
            "telefon",
            "noutbuk",
            "laptop",
            "kompyuter",
            "planshet",
            "tablet",
            "monitor",
            "kamera",
            "televizor",
        ]

        # Brendni topish
        found_brand = None
        for brand in brand_keywords:
            if brand in text_lower:
                found_brand = brand.title()
                break

        # Kategoriyani topish
        found_category = None
        for category in category_keywords:
            if category in text_lower:
                found_category = category.title()
                break

        # Meta title yaratish
        if found_brand and found_brand.lower() not in base_title.lower():
            meta_title = f"{found_brand} {base_title}"
        elif found_category and found_category.lower() not in base_title.lower():
            meta_title = f"{base_title} - {found_category}"
        else:
            meta_title = base_title

        # Uzunligini cheklash (60 belgi - SEO uchun optimal)
        if len(meta_title) > 60:
            # So'zlar bo'yicha kesish
            words = meta_title.split()
            meta_title = ""
            for word in words:
                if len(meta_title + " " + word) <= 57:  # 3 belgi qoldirish "..."
                    meta_title += " " + word if meta_title else word
                else:
                    break
            if len(meta_title) < len(base_title):
                meta_title = base_title[:57] + "..."

        # Tozalash
        meta_title = meta_title.strip()

        # Agar hali ham bo'sh yoki juda qisqa bo'lsa
        if not meta_title or len(meta_title) < 5:
            meta_title = product_name[:60] if product_name else "Mahsulot"

        # Birinchi harfni katta qilish
        if len(meta_title) > 1:
            meta_title = meta_title[0].upper() + meta_title[1:]

        return meta_title[:60]  # Maksimal 60 belgi

    def upload_image(
        self, image_path: str, image_type: str = "thumbnail"
    ) -> Optional[str]:
        """Rasm yuklash"""
        if not self.token:
            print("❌ Avval login qiling!")
            return None

        if not os.path.exists(image_path):
            print(f"❌ Rasm topilmadi: {image_path}")
            return None

        url = f"{self.BASE_URL}/seller/products/upload-images"
        headers = {
            "accept-encoding": "gzip",
            "authorization": f"Bearer {self.token}",
            "user-agent": "Python/requests",
        }

        # Rasm fayl tipini aniqlash
        file_ext = os.path.splitext(image_path)[1].lower()
        content_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        content_type = content_type_map.get(file_ext, "image/jpeg")

        try:
            with open(image_path, "rb") as f:
                files = {"image": (os.path.basename(image_path), f, content_type)}
                data = {"type": image_type, "color": "", "colors_active": "false"}

                response = requests.post(url, headers=headers, files=files, data=data)
                if response.status_code == 200:
                    try:
                        result = response.json()
                        # Turli xil response formatlarini qo'llab-quvvatlash
                        if isinstance(result, dict):
                            # Birinchi navbatda turli xil key'larni tekshirish
                            image_name = (
                                result.get("image_name")
                                or result.get("name")
                                or result.get("filename")
                                or result.get("image")
                                or result.get("file_name")
                                or result.get("path")
                            )

                            # Agar dict ichida yana dict bo'lsa
                            if not image_name and "data" in result:
                                data_obj = result["data"]
                                if isinstance(data_obj, dict):
                                    image_name = (
                                        data_obj.get("image_name")
                                        or data_obj.get("name")
                                        or data_obj.get("filename")
                                    )

                            if image_name:
                                # Agar to'liq path bo'lsa, faqat fayl nomini olish
                                if "/" in str(image_name):
                                    image_name = str(image_name).split("/")[-1]
                                print(f"✅ Rasm yuklandi: {image_name}")
                                return str(image_name)

                        # Agar string formatida bo'lsa
                        if isinstance(result, str):
                            print(f"✅ Rasm yuklandi: {result}")
                            return result

                        print(f"⚠️ Rasm yuklandi, lekin format noto'g'ri: {result}")
                        # Response'dan fayl nomini qidirish
                        response_text = str(result)
                        # Pattern: yyyy-mm-dd-xxxxx.webp
                        pattern = r"\d{4}-\d{2}-\d{2}-[a-zA-Z0-9]+\.(webp|jpg|jpeg|png)"
                        match = re.search(pattern, response_text)
                        if match:
                            image_name = match.group(0)
                            print(f"✅ Rasm nomi topildi: {image_name}")
                            return image_name

                        return None
                    except json.JSONDecodeError:
                        # Agar JSON bo'lmasa, text formatida qaytgan bo'lishi mumkin
                        response_text = response.text
                        # Pattern qidirish
                        pattern = r"\d{4}-\d{2}-\d{2}-[a-zA-Z0-9]+\.(webp|jpg|jpeg|png)"
                        match = re.search(pattern, response_text)
                        if match:
                            image_name = match.group(0)
                            print(f"✅ Rasm yuklandi: {image_name}")
                            return image_name
                        print(
                            f"⚠️ JSON parse qilishda xato, lekin rasm yuklangan bo'lishi mumkin"
                        )
                        return None
                else:
                    print(f"❌ Rasm yuklash xatosi: {response.status_code}")
                    print(f"Xato javobi: {response.text[:200]}")
                    return None
        except Exception as e:
            print(f"❌ Rasm yuklash xatosi: {str(e)}")
            return None

    def extract_category_ids(self, category: Dict) -> Tuple[str, str, str]:
        """Kategoriya IDlarini olish"""
        category_id = str(category.get("id", ""))
        sub_category_id = ""
        sub_sub_category_id = ""

        # Sub-kategoriya topish
        childes = category.get("childes", [])
        if childes:
            sub_category = childes[0]  # Birinchi sub-kategoriyani olish
            sub_category_id = str(sub_category.get("id", ""))

            # Sub-sub-kategoriya topish
            sub_childes = sub_category.get("childes", [])
            if sub_childes:
                sub_sub_category = sub_childes[0]  # Birinchi sub-sub-kategoriyani olish
                sub_sub_category_id = str(sub_sub_category.get("id", ""))

        return category_id, sub_category_id, sub_sub_category_id

    def clean_html_description(self, html_content: str) -> str:
        """
        HTML description'ni tozalash va xavfsiz taglarni saqlash
        Ruxsat etilgan taglar: b, strong, i, em, u, ul, ol, li, h1-h6, p, br, div, span
        """
        # Ruxsat etilgan HTML taglari
        allowed_tags = [
            "b",
            "strong",
            "i",
            "em",
            "u",
            "s",
            "strike",
            "ul",
            "ol",
            "li",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "p",
            "br",
            "div",
            "span",
            "a",
            "img",
            "table",
            "tr",
            "td",
            "th",
            "thead",
            "tbody",
            "blockquote",
            "code",
            "pre",
        ]

        # Agar HTML bo'lmasa, oddiy text sifatida qaytarish
        if not re.search(r"<[^>]+>", html_content):
            return html_content

        # Ruxsat etilgan taglarni saqlash
        cleaned = re.sub(
            r"<(?!\/?(?:" + "|".join(allowed_tags) + r")(?:\s|>))[^>]+>",
            "",
            html_content,
            flags=re.IGNORECASE,
        )

        return cleaned

    def strip_html_tags(self, html_content: str) -> str:
        """HTML taglarini olib tashlash (meta description uchun)"""
        # HTML taglarini olib tashlash
        text = re.sub(r"<[^>]+>", "", html_content)
        # Ko'p bo'shliqlarni bitta bo'shliqqa o'zgartirish
        text = re.sub(r"\s+", " ", text)
        # HTML entity'larni decode qilish
        text = text.replace("&nbsp;", " ")
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')
        text = text.replace("&#39;", "'")
        return text.strip()

    def convert_text_to_html_with_ai(self, plain_text: str) -> str:
        """
        AI yordamida oddiy matnni chiroyli HTML formatiga o'tkazish

        Args:
            plain_text: Oddiy matn tavsifi

        Returns:
            str: HTML formatidagi tavsif
        """
        # Agar matn allaqachon HTML bo'lsa, o'zgartirmaydi
        if re.search(r"<[^>]+>", plain_text):
            return plain_text

        # OpenAI API mavjudligini tekshirish
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if OPENAI_AVAILABLE and openai_api_key:
            try:
                # OpenAI client yaratish
                client = openai.OpenAI(api_key=openai_api_key)

                # Prompt yaratish
                prompt = f"""Sizga mahsulot tavsifi berilgan. Uni chiroyli HTML formatiga o'tkazing.

Qoidalar:
1. Faqat quyidagi HTML taglaridan foydalaning: h1, h2, h3, h4, h5, h6, p, b, strong, i, em, u, ul, ol, li, br, div, span
2. Emoji bilan boshlangan qatorlarni sarlavha (h2 yoki h3) yoki ro'yxat elementi (li) sifatida formatlang
3. ":" bilan tugagan qisqa qatorlarni sarlavha (h3) sifatida formatlang
4. Oddiy matnlarni paragraf (p) taglari bilan o'rab oling
5. Ro'yxatlarni ul/ol va li taglari bilan formatlang
6. Muhim so'zlarni strong yoki b taglari bilan ajrating
7. Faqat HTML kodini qaytaring, boshqa izohlar bermang

Matn:
{plain_text}

HTML:"""

                # OpenAI API chaqiruv
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # yoki "gpt-3.5-turbo"
                    messages=[
                        {
                            "role": "system",
                            "content": "Siz HTML formatlovchi mutaxassissiz. Faqat HTML kodini qaytaring.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                )

                html_result = response.choices[0].message.content.strip()

                # HTML kodini tozalash (faqat HTML qismini olish)
                # Agar ```html yoki ``` bilan o'ralgan bo'lsa, olib tashlash
                html_result = re.sub(r"```html\s*", "", html_result)
                html_result = re.sub(r"```\s*$", "", html_result)
                html_result = html_result.strip()

                # Tozalash va tekshirish
                cleaned_html = self.clean_html_description(html_result)
                print("🤖 AI yordamida HTML formatiga o'tkazildi")
                return cleaned_html

            except Exception as e:
                print(
                    f"⚠️ AI API xatosi: {str(e)}. Oddiy formatlashdan foydalanilmoqda..."
                )
                # Xato bo'lsa, oddiy formatlashga o'tish
                return self._convert_text_to_html_simple(plain_text)
        else:
            # OpenAI mavjud emas yoki API key yo'q, oddiy formatlashdan foydalanish
            return self._convert_text_to_html_simple(plain_text)

    def _convert_text_to_html_simple(self, plain_text: str) -> str:
        """
        Oddiy matnni HTML formatiga o'tkazish (AI bo'lmasa)
        Bu funksiya rule-based yondashuvdan foydalanadi
        """
        lines = plain_text.split("\n")
        html_parts = []
        in_list = False
        in_paragraph = False
        current_paragraph = []
        heading_count = 0

        # Emoji pattern
        emoji_pattern = re.compile(
            r"^[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F600-\U0001F64F"
            r"\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0"
            r"\U000024C2-\U0001F251]"
        )

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Bo'sh qator
            if not line:
                if in_paragraph and current_paragraph:
                    html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
                    current_paragraph = []
                    in_paragraph = False
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                i += 1
                continue

            # Emoji bilan boshlanadigan qatorlar
            if emoji_pattern.match(line):
                if in_paragraph and current_paragraph:
                    html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
                    current_paragraph = []
                    in_paragraph = False

                next_line_empty = i + 1 >= len(lines) or not lines[i + 1].strip()
                next_line_emoji = False
                if i + 1 < len(lines) and lines[i + 1].strip():
                    next_line_emoji = bool(emoji_pattern.match(lines[i + 1].strip()))

                text_after_emoji = line[1:].strip() if len(line) > 1 else ""
                is_list_item = bool(
                    text_after_emoji and not next_line_empty and not next_line_emoji
                )

                if next_line_empty or next_line_emoji or not text_after_emoji:
                    if in_list:
                        html_parts.append("</ul>")
                        in_list = False

                    heading_count += 1
                    if heading_count == 1:
                        html_parts.append(f"<h2>{line}</h2>")
                    else:
                        html_parts.append(f"<h3>{line}</h3>")
                else:
                    if not in_list:
                        html_parts.append("<ul>")
                        in_list = True
                    html_parts.append(f"<li><strong>{text_after_emoji}</strong></li>")
            else:
                # Oddiy matn
                if line.endswith(":") and len(line) < 60:
                    if in_paragraph and current_paragraph:
                        html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")
                        current_paragraph = []
                        in_paragraph = False
                    if in_list:
                        html_parts.append("</ul>")
                        in_list = False
                    heading_count += 1
                    html_parts.append(f"<h3>{line}</h3>")
                else:
                    if not in_paragraph:
                        in_paragraph = True
                        current_paragraph = []
                    current_paragraph.append(line)

            i += 1

        # Qolgan paragrafni yopish
        if in_paragraph and current_paragraph:
            html_parts.append(f"<p>{' '.join(current_paragraph)}</p>")

        # Qolgan ro'yxatni yopish
        if in_list:
            html_parts.append("</ul>")

        result = "\n".join(html_parts)

        if not result.strip():
            return f"<p>{plain_text.strip()}</p>"

        return result

    def upload_product(
        self,
        description: str,
        image_paths: List[str] = None,  # Bir nechta rasm uchun list
        image_path: str = None,  # Orqaga moslik uchun (eski kodlar uchun)
        price: float = None,
        name: Optional[str] = None,
        category_id: Optional[str] = None,
        brand_id: Optional[int] = None,
        stock: int = 1,
        discount: float = 0.0,
        discount_type: str = "percent",
    ) -> Dict:
        """
        Mahsulot yuklash

        Args:
            description: Mahsulot tavsifi
            image_paths: Rasm yo'llari ro'yxati (bir nechta rasm) - yangi usul
            image_path: Bitta rasm yo'li (orqaga moslik uchun) - eski usul
            price: Narx (required)
            name: Mahsulot nomi (ixtiyoriy, tavsifdan generatsiya qilinadi)
            category_id: Kategoriya ID (ixtiyoriy, avtomatik topiladi)
            brand_id: Brend ID (ixtiyoriy, avtomatik topiladi)
            stock: Ombordagi miqdor
            discount: Chegirma foizi
            discount_type: Chegirma turi (percent yoki amount)

        Returns:
            Dict: Natija
        """
        # Price tekshirish
        if price is None:
            return {"success": False, "error": "Narx kiritilmagan"}

        # Orqaga moslik: agar image_path berilgan bo'lsa, uni listga aylantirish
        if image_path and not image_paths:
            image_paths = [image_path]

        # Agar image_paths list emas yoki bo'sh bo'lsa, xato
        if not isinstance(image_paths, list) or len(image_paths) == 0:
            return {"success": False, "error": "Hech bo'lmaganda bitta rasm kerak"}
        if not self.token:
            if not self.login():
                return {"success": False, "error": "Login qilishda xato"}

        # Ma'lumotlarni yuklash
        if not self.categories:
            self.get_categories()
        if not self.brands:
            self.get_brands()

        # Mahsulot nomini AI yordamida generatsiya qilish
        if not name:
            name = self.generate_product_name(description)
            print(f"🤖 AI generatsiya qilgan nom: {name}")

        # Kategoriya va brendni topish (categories.py funksiyasidan foydalanish)
        # O'zgaruvchilarni ishga tushirish
        sub_category_id = ""
        sub_sub_category_id = ""
        sub_sub_sub_category_id = ""

        if not category_id or not brand_id:
            # Brend nomini ajratish
            brand_name = self._extract_brand_name(description, name)

            # categories.py funksiyasidan foydalanish
            try:
                selection = select_category_brand(
                    product_name=name,
                    brand_name=brand_name,
                    categories=self.categories,
                    brands=self.brands,
                )

                # Agar category_id berilmagan bo'lsa, AI topgan kategoriyadan foydalanish
                if not category_id:
                    category_id = selection.category_id
                    sub_category_id = selection.sub_category_id or ""
                    sub_sub_category_id = selection.sub_sub_category_id or ""
                    sub_sub_sub_category_id = selection.sub_sub_sub_category_id or ""

                    if selection.category:
                        print(f"🤖 AI topgan kategoriya: {selection.category}")
                    if selection.sub_category:
                        print(f"🤖 AI topgan sub-kategoriya: {selection.sub_category}")
                    if selection.sub_sub_category:
                        print(
                            f"🤖 AI topgan sub-sub-kategoriya: {selection.sub_sub_category}"
                        )

                # Agar brand_id berilmagan bo'lsa, AI topgan brenddan foydalanish
                if not brand_id:
                    brand_id = selection.brand_id
                    print(f"🤖 AI topgan brend ID: {brand_id}")
            except Exception as e:
                print(f"⚠️ Kategoriya/brend tanlashda xato: {str(e)}")
                # Fallback: agar xato bo'lsa, eski usulga o'tish
                if not category_id:
                    if self.categories:
                        category_id = str(self.categories[0].get("id", "0"))
                        sub_category_id = ""
                        sub_sub_category_id = ""
                        sub_sub_sub_category_id = ""
                    else:
                        return {"success": False, "error": "Kategoriya topilmadi"}
                if not brand_id:
                    if self.brands:
                        brand_id = self.brands[0].get("id", 1)
                    else:
                        brand_id = 1
        else:
            # Agar category_id va brand_id berilgan bo'lsa, extract_category_ids dan foydalanish
            if category_id:
                # ID bo'yicha kategoriyani topish va sub-kategoriyalarni olish
                category = None
                for cat in self.categories:
                    if str(cat.get("id")) == str(category_id):
                        category = cat
                        break

                if category:
                    category_id, sub_category_id, sub_sub_category_id = (
                        self.extract_category_ids(category)
                    )
                    sub_sub_sub_category_id = ""
                else:
                    sub_category_id = ""
                    sub_sub_category_id = ""
                    sub_sub_sub_category_id = ""

        # Barcha rasmlarni yuklash
        print(f"📤 {len(image_paths)} ta rasm yuklanmoqda...")
        
        # A. Birinchi rasmini thumbnail sifatida yuklash
        first_image_path = image_paths[0]
        if not os.path.exists(first_image_path):
            return {"success": False, "error": "Birinchi rasm topilmadi"}
        
        thumbnail_name = self.upload_image(first_image_path, "thumbnail")
        if not thumbnail_name:
            return {
                "success": False,
                "error": "Birinchi rasm (thumbnail) yuklashda xato",
            }
        meta_image_name = thumbnail_name

        # B. Rasm ma'lumotlarini tayyorlash
        # API talabiga ko'ra, thumbnail birinchi bo'lishi kerak
        images_data = [
            {"image_name": thumbnail_name, "storage": "public"}
        ]

        # C. Qolgan rasmlarni product sifatida yuklash va qo'shish
        for image_path in image_paths[1:]:
            if not os.path.exists(image_path):
                print(f"⚠️ Rasm topilmadi: {image_path}")
                continue
            
            image_name = self.upload_image(image_path, "product")
            if image_name:
                images_data.append({"image_name": image_name, "storage": "public"})

        if len(images_data) == 0:
            return {"success": False, "error": "Hech qanday rasm yuklanmadi"}

        # Description'ni HTML formatiga o'tkazish (agar oddiy matn bo'lsa)
        # Agar allaqachon HTML bo'lsa, faqat tozalash
        if re.search(r"<[^>]+>", description):
            # HTML allaqachon mavjud, faqat tozalash
            html_description = self.clean_html_description(description)
        else:
            # Oddiy matn, AI yordamida HTML formatiga o'tkazish
            print("🤖 Oddiy matnni HTML formatiga o'tkazish...")
            html_description = self.convert_text_to_html_with_ai(description)
            html_description = self.clean_html_description(html_description)

        # Meta description uchun HTML taglarini olib tashlash
        plain_description = self.strip_html_tags(description)

        # Meta title ni AI yordamida generatsiya qilish
        meta_title = self.generate_meta_title(description, name)

        # Taglarni AI (yoki heuristika) yordamida generatsiya qilish
        tags = self.generate_tags_for_product(description, name)
        print(f"🤖 Generatsiya qilingan taglar: {tags}")
        print(f"🤖 AI generatsiya qilgan meta title: {meta_title}")

        # Mahsulot ma'lumotlarini tayyorlash
        product_data = {
            "name": json.dumps([name], ensure_ascii=False),
            "description": json.dumps([html_description], ensure_ascii=False),
            "unit_price": price,
            "discount": discount,
            "discount_type": discount_type,
            "tax_ids": "[]",
            "tax_model": "exclude",
            "unit": "pc",
            "brand_id": brand_id,
            "meta_title": meta_title,
            "meta_description": plain_description[:160] if plain_description else "",
            "lang": json.dumps(["ru"], ensure_ascii=False),
            "colors": "[]",
            "images": json.dumps(images_data, ensure_ascii=False),
            "thumbnail": thumbnail_name,
            "colors_active": False,
            "video_url": "",
            "meta_image": meta_image_name,
            "current_stock": stock,
            "shipping_cost": 0.0,
            "multiply_qty": 0,
            "code": os.urandom(3).hex().upper(),
            "minimum_order_qty": 1,
            "product_type": "physical",
            "digital_product_type": "ready_after_sell",
            "digital_file_ready": "",
            "tags": json.dumps(tags, ensure_ascii=False),
            "publishing_house": "[]",
            "authors": "[]",
            "color_image": "[]",
            "meta_index": "1",
            "meta_no_follow": "",
            "meta_no_image_index": "0",
            "meta_no_archive": "0",
            "meta_no_snippet": "0",
            "meta_max_snippet": "0",
            "meta_max_snippet_value": None,
            "meta_max_video_preview": "0",
            "meta_max_video_preview_value": None,
            "meta_max_image_preview": "0",
            "meta_max_image_preview_value": "large",
            "tax": "0",
            "category_id": category_id,
            "sub_category_id": sub_category_id or "",
            "sub_sub_category_id": sub_sub_category_id or "",
            "sub_sub_sub_category_id": sub_sub_sub_category_id or "",
        }

        # Mahsulot yaratish
        url = f"{self.BASE_URL}/seller/products/add"
        headers = {
            "accept-encoding": "gzip",
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json; charset=UTF-8",
            "user-agent": "Python/requests",
        }

        try:
            print("📦 Mahsulot yuklanmoqda...")
            response = requests.post(url, json=product_data, headers=headers)

            if response.status_code == 200:
                result = response.json()
                print("✅ Mahsulot muvaffaqiyatli yuklandi!")
                return {
                    "success": True,
                    "message": "Mahsulot muvaffaqiyatli yuklandi!",
                    "data": result,
                }
            else:
                error_msg = response.text
                print(f"❌ Mahsulot yuklash xatosi: {response.status_code}")
                print(f"Xato: {error_msg}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_msg}",
                    "status_code": response.status_code,
                }
        except Exception as e:
            print(f"❌ Mahsulot yuklash xatosi: {str(e)}")
            return {"success": False, "error": str(e)}

    def initialize(self):
        """Barcha kerakli ma'lumotlarni yuklash"""
        print("🔄 Tizim ishga tushmoqda...")
        if not self.login():
            return False

        self.get_categories()
        self.get_brands()
        self.get_attributes()

        print("✅ Tizim tayyor!")
        return True


# Foydalanish misoli
if __name__ == "__main__":
    # Do'kon ma'lumotlari
    # Iltimos, o'z email va parolingizni kiriting
    EMAIL = os.getenv("VENU_EMAIL", "your_email@venu.uz")
    PASSWORD = os.getenv("VENU_PASSWORD", "your_password")

    # Agent yaratish
    agent = ProductUploaderAgent(EMAIL, PASSWORD)

    # Tizimni ishga tushirish
    if agent.initialize():
        # Mahsulot yuklash
        result = agent.upload_product(
            description="Yangi smartfon - ajoyib xususiyatlar bilan",
            image_path="test_rasm.png",  # Rasm yo'li
            price=500000.0,  # Narx
            stock=5,  # Ombordagi miqdor
            discount=10.0,  # 10% chegirma
        )

        if result["success"]:
            print("\n🎉 Mahsulot muvaffaqiyatli yuklandi!")
        else:
            print(f"\n❌ Xato: {result.get('error', 'Nomalum xato')}")
