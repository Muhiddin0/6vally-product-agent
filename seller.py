import requests
import json
import logging
import os
from typing import List, Dict, Any, Optional

# Logging - jarayonni terminalda ko'rish uchun
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class VenuSellerAPI:
    BASE_URL = "https://api.venu.uz"

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.token: Optional[str] = None

        # Standart headerlar
        self.session.headers.update(
            {
                "user-agent": "Dart/3.10 (dart:io)",
                "accept-encoding": "gzip",
                "lang": "en",
            }
        )

    def login(self) -> bool:
        """1. Login qilish va Token olish"""
        url = f"{self.BASE_URL}/api/v3/seller/auth/login"
        payload = {"email": self.email, "password": self.password}

        # Login uchun hujjatdagi maxsus vaqtinchalik bearer token
        temp_headers = {
            "authorization": "Bearer mPzVh43jap7LOAy9bX8TwGdzj2eTxNOBq4DS3xhV7U4P8McxjC"
        }

        try:
            response = self.session.post(url, json=payload, headers=temp_headers)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("token")

            # Keyingi so'rovlar uchun asosiy tokenni o'rnatamiz
            self.session.headers.update({"authorization": f"Bearer {self.token}"})
            logging.info("Muvaffaqiyatli login qilindi.")
            return True
        except Exception as e:
            logging.error(f"Login xatosi: {e}")
            return False

    def upload_image(
        self, file_path: str, image_type: str = "product"
    ) -> Optional[str]:
        """
        2. Rasmni serverga yuklash (upload-images).
        Server qaytargan fayl nomini qaytaradi.
        """
        if not os.path.exists(file_path):
            logging.error(f"Fayl topilmadi: {file_path}")
            return None

        url = f"{self.BASE_URL}/api/v3/seller/products/upload-images"

        # Multipart so'rov uchun Content-Type'ni requests o'zi belgilaydi
        headers = {
            "authorization": f"Bearer {self.token}",
            "user-agent": "Dart/3.10 (dart:io)",
        }

        try:
            with open(file_path, "rb") as img_file:
                files = [
                    ("image", (os.path.basename(file_path), img_file, "image/png"))
                ]
                # API talab qiladigan qo'shimcha form-data maydonlari
                data = {
                    "type": image_type,  # 'thumbnail' yoki 'product'
                    "colors_active": "false",
                    "color": "",
                }

                response = requests.post(url, headers=headers, files=files, data=data)
                response.raise_for_status()
                res_data = response.json()

                # API muvaffaqiyatli yuklanganda fayl nomini qaytaradi
                # Logingizdan kelib chiqib: res_data['image_name'] bo'lishi kerak
                image_name = res_data.get("image_name")
                logging.info(f"Rasm serverga yuklandi: {image_name}")
                return image_name
        except Exception as e:
            logging.error(f"Rasm yuklashda xatolik: {e}")
            return None

    def add_product(
        self,
        name: str,
        description: str,
        meta_image: str,
        meta_title: str,
        meta_description: str,
        tags: List[str],
        price: float,
        category_id: str,
        brand_id: int,
        main_image_path: str,
        additional_images_paths: List[str] = [],
        stock: int = 10,
    ) -> Dict:
        """3. Mahsulotni barcha yuklangan rasmlar bilan birga qo'shish"""

        # A. Asosiy rasmni (Thumbnail) yuklash
        thumb_name = self.upload_image(main_image_path, "thumbnail")
        if not thumb_name:
            return {"error": "Thumbnail yuklanmadi"}

        # B. Galereya rasmlarini yuklash
        gallery_images = []
        # Birinchi bo'lib thumbnailni galereyaga qo'shamiz (API talabi bo'lishi mumkin)
        gallery_images.append({"image_name": thumb_name, "storage": "public"})

        for img_path in additional_images_paths:
            img_name = self.upload_image(img_path, "product")
            if img_name:
                gallery_images.append({"image_name": img_name, "storage": "public"})

        # C. Mahsulot ma'lumotlarini yig'ish (JSON string formatida bo'lishi shart!)
        # payload = {
        #     "name": json.dumps([name]),
        #     "description": json.dumps([description]),
        #     "unit_price": price,
        #     "discount": 0,
        #     "discount_type": "flat",
        #     "tax_ids": "[]",
        #     "tax": "0", # Majburiy maydon
        #     "tax_model": "exclude",
        #     "category_id": category_id,
        #     "sub_category_id": "600", # Kerak bo'lsa to'ldiriladi
        #     "sub_sub_category_id": "601",
        #     "unit": "pc",
        #     "brand_id": brand_id,
        #     "current_stock": stock,
        #     "minimum_order_qty": 1,
        #     "code": os.urandom(3).hex().upper(), # Avtomatik random kod
        #     "product_type": "physical",
        #     "thumbnail": thumb_name, # Serverdan qaytgan nom
        #     "images": json.dumps(gallery_images), # Yuklangan rasmlar massivi
        #     "meta_image": meta_image,
        #     "meta_title": meta_title,
        #     "meta_description": meta_description,
        #     "lang": json.dumps(["ru"]), # Til
        #     "colors_active": False,
        #     "shipping_cost": 0,
        #     "multiply_qty": 0,
        #     "tags": json.dumps(tags),
        #     "meta_max_image_preview_value": "large"
        # }

        print(json.dumps([name]))

        payload = {
            "name": json.dumps([name]),
            "description": json.dumps([description]),
            "unit_price": price,
            "discount": 0,
            "discount_type": "percent",
            "tax_ids": "[]",
            "tax_model": "exclude",
            "category_id": "424",
            "unit": "pc",
            "brand_id": 7,
            "meta_title": meta_title,
            "meta_description": "",
            "lang": json.dumps(["ru"]),
            "colors": "[]",
            "images": json.dumps(gallery_images),
            "thumbnail": thumb_name,
            "colors_active": False,
            "video_url": "",
            "meta_image": meta_image,
            "current_stock": stock,
            "shipping_cost": 0.0,
            "multiply_qty": 0,
            "code": os.urandom(3).hex().upper(),
            "minimum_order_qty": 1,
            "product_type": "physical",
            "digital_product_type": "ready_after_sell",
            "digital_file_ready": "",
            "tags": json.dumps(tags),
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
            "sub_category_id": "600",
            "sub_sub_category_id": "601",
            "tax": "0",
        }

        url = f"{self.BASE_URL}/api/v3/seller/products/add"
        try:
            # content-type: application/json orqali yuboramiz
            response = self.session.post(url, json=payload)
            result = response.json()
            if response.status_code == 200:
                logging.info(f"Mahsulot muvaffaqiyatli qo'shildi: {name}")
            else:
                logging.error(f"Xatolik: {result}")
            return result
        except Exception as e:
            logging.error(f"Mahsulot qo'shishda xatolik: {e}")
            return {"status": "error", "message": str(e)}


# ==================== ISHLATIB KO'RISH ====================

if __name__ == "__main__":
    # 1. API klasini yaratish
    api = VenuSellerAPI(email="themodestn@venu.uz", password="Themodestn@venu3001.uz")

    if api.login():
        # Kompyuteringizda bor bo'lgan rasm yo'lini ko'rsating
        # Masalan: "C:/rasmlar/iphone.png" yoki "image.jpg"
        image_path = "test_rasm.png"

        # Agar rasm fayli mavjud bo'lsa
        if os.path.exists(image_path):
            result = api.add_product(
                name="Smartfon iPhone 15 Pro",
                description="Eng yangi model, 256GB, Titan",
                meta_image="test_rasm.png",
                meta_title="Smartfon iPhone 15 Pro",
                meta_description="Eng yangi model, 256GB, Titan",
                tags=["new", "product"],
                price=1500,
                category_id="424",  # Smartfonlar ID si
                brand_id=2,  # Apple/Iphone ID si
                main_image_path=image_path,
                additional_images_paths=[image_path],  # Qo'shimcha rasmlar bo'lsa
                stock=5,
            )
            print("\nNatija:")
            print(json.dumps(result, indent=2))
        else:
            print(
                f"Xato: {image_path} fayli topilmadi! Iltimos kompyuteringizdagi rasm yo'lini bering."
            )


# Example usage (for testing)
if __name__ == "__main__":
    import sys

    # Setup logging
    from utils.logging_config import setup_logging

    setup_logging()

    # Get credentials from environment or use defaults
    email = os.getenv("VENU_EMAIL", "themodestn@venu.uz")
    password = os.getenv("VENU_PASSWORD", "Themodestn@venu3001.uz")

    api = VenuSellerAPI(email=email, password=password)

    if api.login():
        image_path = "test_rasm.png"

        if os.path.exists(image_path):
            result = api.add_product(
                name="Smartfon iPhone 15 Pro",
                description="Eng yangi model, 256GB, Titan",
                meta_image="test_rasm.png",
                meta_title="Smartfon iPhone 15 Pro",
                meta_description="Eng yangi model, 256GB, Titan",
                tags=["new", "product"],
                price=1500.0,
                category_id="424",
                brand_id=2,
                main_image_path=image_path,
                additional_images_paths=[image_path],
                stock=5,
            )
            print("\nResult:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {image_path} file not found!")
            sys.exit(1)
    else:
        print("Login failed!")
        sys.exit(1)
