import json
import os
import requests
import logging
from typing import Optional
from urllib.parse import urlparse
import hashlib

from core.config import settings
from core.openai_client import get_openai_client

logger = logging.getLogger(__name__)


class ProductImage:
    def __init__(self, product_name: str):
        self.product_name = product_name
        self.client = get_openai_client()

    def get_product_images_with_ai(self) -> list[str]:
        """
        Uses AI to filter Yandex image search results and return
        only the most relevant product image URLs.

        Returns:
            list[str]: List of image URLs
        """

        images = self.search_yandex_images()
        if not images:
            return []

        system_prompt = (
            "You are an AI image selection agent.\n"
            "You receive a product name and a list of images (url, title).\n\n"
            "Rules:\n"
            "- Select ONLY images that clearly match the exact product\n"
            "- Ignore boxes, accessories, logos, diagrams, ads\n"
            "- Prefer real product photos and official catalog images\n\n"
            "Output:\n"
            "- Return ONLY a valid JSON array of image URLs (strings)\n"
            "- No explanations, no extra text\n"
            "- If nothing matches, return []"
        )

        user_prompt = (
            "Product name:\n"
            f"{self.product_name}\n\n"
            "Images:\n"
            f"{images}\n\n"
            "Task:\n"
            "Return a JSON array of URLs that best match the product."
        )

        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                temperature=settings.openai_temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "image_response",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "image_urls": {
                                    "type": "array",
                                    "items": {"type": "string", "format": "uri"},
                                }
                            },
                            "required": ["image_urls"],
                        },
                    },
                },
            )

            # SAFE extraction
            image_urls_str = response.choices[0].message.content

            if not image_urls_str:
                return []

            data = json.loads(image_urls_str)

            return data.get("image_urls", [])

        except Exception as e:
            logger.error(f"Error filtering images with AI: {e}", exc_info=True)
            return []

    def search_yandex_images(self):
        """
        Search for images on Yandex and return image URLs.

        Args:
            search_text: Search query text
            max_images: Maximum number of images to return

        Returns:
            List[str]: List of image URLs
        """

        url = "https://yandex.ru/images/search"
        params = {
            "tmpl_version": "releases-frontend-images-v1.1694.0__3f886c9a45c40401c1cf90d181d37709f734ebc2",
            "format": "json",
            "request": '{"blocks":[{"block":"extra-content","params":{},"version":2},{"block":{"block":"i-react-ajax-adapter:ajax"},"params":{"type":"ImagesApp","ajaxKey":"serpList/fetchByFilters"},"version":2}]}',
            "yu": "5167021401766310918",
            "source-serpid": "diSP3SNxpgMR8mPtYuUB6g",
            "text": self.product_name,
        }

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-US,en;q=0.9,uz;q=0.8,ru;q=0.7",
            "device-memory": "8",
            "downlink": "10",
            "dpr": "1.25",
            "ect": "4g",
            "priority": "u=1, i",
            # "referer": f"https://yandex.ru/images/search?text={quote(search_text)}",
            "rtt": "100",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-arch": '"x86"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-full-version": '"143.0.7499.169"',
            "sec-ch-ua-full-version-list": '"Google Chrome";v="143.0.7499.169", "Chromium";v="143.0.7499.169", "Not A(Brand";v="24.0.0.0"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"Linux"',
            "sec-ch-ua-platform-version": '""',
            "sec-ch-ua-wow64": "?0",
            "sec-ch-viewport-height": "719",
            "sec-ch-viewport-width": "892",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "viewport-width": "892",
            "x-requested-with": "XMLHttpRequest",
        }

        cookies = {
            "fi-expand": "1",
            "yandexuid": "5167021401766310918",
            "yashr": "8788835621766311715",
            "gdpr": "0",
            "_ym_uid": "1766311717107822658",
            "_ym_d": "1766311717",
            "is_gdpr": "0",
            "is_gdpr_b": "CKKubhDl6QIoAg==",
            "receive-cookie-deprecation": "1",
            "yuidss": "5167021401766310918",
            "ymex": "2082108447.yrts.1766748447#2081670918.yrtsi.1766310918",
            "amcuid": "461275411766751449",
            "i": "ZUPrnhXGMsNjyeAcoTtHIZfwoxWeIvxu4EmXD6LwMw4Wz3ViPW7xlUYbL30DVhEwgPxbObHemCQHoqn2bqc1VH0lBiw=",
            "yabs-dsp": "mts_banner.LW9XM1p1YkdRRW1PbFJDY3lnU0k3dw==",
            "_ym_isad": "2",
            "_yasc": "/d+2AA2X3MWY4CvTL5u0MvucaBB+PfVoeu9mu3HLOnmJlCvNA6B2Y5XQeAj+qXQSE58xO81ss4E=",
            "cycada": "hFpa/DirGwCD181RsSllLpG5x7LsmcQ941DgXI+Fj5A=",
            "yp": "1768675024.szm.1_25:1536x864:877x719",
            "bh": "EkEiR29vZ2xlIENocm9tZSI7dj0iMTQzIiwgIkNocm9taXVtIjt2PSIxNDMiLCAiTm90IEEoQnJhbmQiO3Y9IjI0IhoFIng4NiIiECIxNDMuMC43NDk5LjE2OSIqAj8wMgIiIjoHIkxpbnV4IkICIiJKBCI2NCJSXSJHb29nbGUgQ2hyb21lIjt2PSIxNDMuMC43NDk5LjE2OSIsICJDaHJvbWl1bSI7dj0iMTQzLjAuNzQ5OS4xNjkiLCAiTm90IEEoQnJhbmQiO3Y9IjI0LjAuMC4wIloCPzBgtdGYywZqGdzK6YgO8qy3pQv7+vDnDev//fYP+8zNhwg=",
        }

        response = requests.get(
            url, headers=headers, params=params, cookies=cookies, timeout=10
        )
        response.raise_for_status()
        data = response.json()

        images = self.extract_images(data=data)

        return images

    def extract_images(self, data):
        """
        Extract image URLs and Titles from Yandex API response.

        Args:
            data: JSON response from Yandex API

        Returns:
            List[str]: List of image URLs
        """
        image_urls = []
        blocks = data.get("blocks", [])

        for block in blocks:
            if block.get("name", {}).get("block") == "i-react-ajax-adapter:ajax":
                entities = (
                    block.get("params", {})
                    .get("adapterData", {})
                    .get("serpList", {})
                    .get("items", {})
                    .get("entities", {})
                )

                for item_id, item_data in entities.items():
                    img_url = item_data.get("origUrl")
                    img_title = item_data.get("snippet").get("title")
                    if img_url and img_title:
                        image_urls.append({"url": img_url, "title": img_title})

        return image_urls


def download_image_from_url(image_url: str, save_dir: str = "media/products") -> Optional[str]:
    """
    Download an image from URL and save it to local directory.

    Args:
        image_url: URL of the image to download
        save_dir: Directory to save the image (default: media/products)

    Returns:
        Optional[str]: Path to saved image file, or None if download failed
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)

        # Get file extension from URL or default to .jpg
        parsed_url = urlparse(image_url)
        path = parsed_url.path
        ext = os.path.splitext(path)[1] or ".jpg"
        
        # Generate unique filename using URL hash
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
        filename = f"yandex_{url_hash}{ext}"
        file_path = os.path.join(save_dir, filename)

        # Download the image
        response = requests.get(image_url, timeout=10, stream=True)
        response.raise_for_status()

        # Save to file
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Downloaded image from {image_url} to {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Error downloading image from {image_url}: {e}", exc_info=True)
        return None


def get_product_images_from_yandex(
    product_name: str,
    brand_name: Optional[str] = None,
    max_images: int = 2,
    site: Optional[str] = None,
    additional_search: bool = False,
    download_images: bool = True,
    save_dir: str = "media/products",
) -> list[str]:
    """
    Get product images from Yandex using AI filtering.

    Args:
        product_name: Name of the product
        brand_name: Optional brand name
        max_images: Maximum number of images to return
        site: Optional site filter (not used in current implementation)
        additional_search: Optional flag for additional search (not used in current implementation)
        download_images: If True, download images to local files. If False, return URLs
        save_dir: Directory to save downloaded images (default: media/products)

    Returns:
        List of image URLs (if download_images=False) or local file paths (if download_images=True)
    """
    # Combine product name and brand for better search results
    search_query = product_name
    if brand_name:
        search_query = f"{brand_name} {product_name}"

    image_agent = ProductImage(search_query)
    image_urls = image_agent.get_product_images_with_ai()

    # Limit to max_images
    image_urls = image_urls[:max_images] if image_urls else []

    if not image_urls:
        return []

    # If download_images is True, download and return local paths
    if download_images:
        downloaded_paths = []
        for url in image_urls:
            local_path = download_image_from_url(url, save_dir)
            if local_path:
                downloaded_paths.append(local_path)
        return downloaded_paths

    # Otherwise, return URLs
    return image_urls
