from get_product_params import get_product_params, ProductInput
import pandas as pd
import asyncio
import logging
from typing import List, Optional
from fastapi import UploadFile

from api.venu_api import VenuSellerAPI
from services.product_service import ProductService, get_default_image_path
from core.manager import ConnectionManager
from api.yandex import get_product_images_from_yandex
from agent.image import generate_poster
import os
import random

logger = logging.getLogger(__name__)


class BulkUploadService:
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        self.product_service = ProductService()

    async def process_excel(
        self, file: UploadFile, email: str, password: str, client_id: str = None
    ):
        """
        Process uploaded Excel file and upload products to Venu.
        """
        websocket = None
        # In a real scenario, we might want to target a specific websocket.
        # For this simplified version, we'll try to broadcast or hopefully the client ID mapping handles it.
        # But `ConnectionManager` as implemented only broadcasts or sends to a socket object.
        # We'll just broadcast for now as we don't have a mapping of client_id -> socket in the simple manager.
        # To make it better, we should probably update ConnectionManager to map IDs,
        # but for this verified single-user AI agent, broadcasting is acceptable or we pass the socket if possible.
        # But this service runs in a background task, so we don't have the socket object easily unless we store it.
        # Let's rely on broadcast for this "AI" feel (all open tabs see the progress).

        await self._log("🚀 Excel fayl qabul qilindi. Jarayon boshlanmoqda...")

        try:
            # Login to Venu
            await self._log(f"🔑 {email} hisobiga kirilmoqda...")
            venu_api = VenuSellerAPI(email=email, password=password)
            if not venu_api.login():
                await self._log(
                    "❌ Venu tizimiga kirishda xatolik! Login yoki parolni tekshiring."
                )
                return

            await self._log("✅ Muvaffaqiyatli kirildi!")

            # Read Excel
            # Helper to read uploaded file into pandas
            contents = await file.read()
            # Save temporary to read with pandas (as bytes) might be tricky depending on engine
            # Pandas can read bytes directly
            from io import BytesIO

            df = pd.read_excel(BytesIO(contents))

            total_rows = len(df)
            await self._log(f"📄 Faylda {total_rows} ta mahsulot topildi.")

            for index, row in df.iterrows():
                try:
                    # Expected columns: Name, Brand, Price, Stock (optional)
                    # We will try to map loosely
                    row_data = row.to_dict()

                    # Fallback to index based if keys not found (assuming Name (0), Brand (1), Price (2))
                    # Convert row to list to access by index
                    row_values = list(row_data.values())

                    print(row_values)

                    product_name = row_values[0]
                    brand_name = row_values[1]
                    price = row_values[2]
                    stock = 100

                    await self._log(f"--- {index+1}/{total_rows}: {product_name} ---")
                    await self._log(f"🤖 AI kontent yaratmoqda...")

                    # Generate Content
                    product = self.product_service.generate_product_content(
                        name=product_name, brand=brand_name, price=price, stock=stock
                    )

                    await self._log("📸 Rasmlar qidirilmoqda...")

                    # Images
                    additional_images = get_product_images_from_yandex(
                        product_name, brand_name, max_images=3
                    )
                    if not additional_images:
                        additional_images = [get_default_image_path()]

                    template_image_path = None
                    templates_dir = "seo-images"
                    if os.path.exists(templates_dir):
                        template_files = [
                            f
                            for f in os.listdir(templates_dir)
                            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
                        ]
                        if template_files:
                            selected_template = random.choice(template_files)
                            template_image_path = os.path.join(
                                templates_dir, selected_template
                            )
                        else:
                            await self._log("⚠️ Templates papkasida rasm topilmadi")

                    # Poster generation
                    product_params_str = f"{product.name}\n{product.description}"

                    # main_image = generate_poster(
                    #     template_image_path=template_image_path,
                    #     product_image_path=additional_images[0],
                    #     product_params=product_params_str,
                    # )
                    
                    main_image = additional_images[0]

                    # Category Selection
                    await self._log("📂 Kategoriya tanlanmoqda...")
                    success, error_resp, selection = (
                        self.product_service.select_category_and_brand(
                            product_name, brand_name, api_client=venu_api
                        )
                    )

                    if not success or not selection:
                        await self._log(
                            f"⚠️ Kategoriya yoki brend topilmadi: {error_resp}"
                        )
                        continue

                    product_params = get_product_params(
                        product_input=ProductInput(
                            name=product_name,
                            category=selection.category,
                            sub_category=selection.sub_category,
                            sub_sub_category=selection.sub_sub_category,
                            brand=brand_name,
                            image_paths=additional_images,
                        )
                    )

                    # Upload
                    await self._log("⬆️ Do'konga yuklanmoqda...")
                    shop_saved, shop_response = (
                        self.product_service.save_product_to_shop(
                            product=product,
                            category_selection=selection,
                            main_image_path=main_image,
                            additional_images_paths=additional_images,
                            api_client=venu_api,
                            product_params=product_params,
                            price=price,
                            stock=stock,
                        )
                    )

                    if shop_saved:
                        await self._log(
                            f"✅ Yuklandi! ID:"
                        )
                    else:
                        await self._log(f"❌ Yuklashda xatolik: {shop_response}")

                    # Sleep briefly to avoid rate limits and allow frontend to update
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"Error processing row {index}: {e}", exc_info=True)
                    await self._log(f"❌ Qatorni ishlashda xatolik: {str(e)}")

            await self._log("🏁 Barcha mahsulotlar qayta ishlandi!")

        except Exception as e:
            logger.error(f"Bulk upload error: {e}", exc_info=True)
            await self._log(f"❌ Kutilmagan xatolik: {str(e)}")

    async def _log(self, message: str):
        # Broadcast message to websockets
        # We send a JSON structure so frontend can render it nicely if needed, or just text
        await self.manager.broadcast(message)
