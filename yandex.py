"""Yandex image search service."""

import logging
import os
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)


def search_yandex_images(search_text: str, max_images: int = 5) -> List[str]:
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
        "iorient": "vertical",
        "source-serpid": "diSP3SNxpgMR8mPtYuUB6g",
        "text": search_text,
        "uinfo": "sw-1536-sh-864-ww-892-wh-719-pd-1.25-wp-16x9_1920x1080",
    }

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9,uz;q=0.8,ru;q=0.7",
        "device-memory": "8",
        "downlink": "10",
        "dpr": "1.25",
        "ect": "4g",
        "priority": "u=1, i",
        "referer": f"https://yandex.ru/images/search?text={quote(search_text)}",
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

    try:
        response = requests.get(
            url, headers=headers, params=params, cookies=cookies, timeout=10
        )
        response.raise_for_status()
        data = response.json()

        image_urls = extract_image_urls(data)
        return image_urls[:max_images]

    except Exception as e:
        logger.error(f"Yandex rasm qidirishda xatolik: {e}")
        return []


def extract_image_urls(data: dict) -> List[str]:
    """
    Extract image URLs from Yandex API response.

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
                if img_url:
                    image_urls.append(img_url)

    return image_urls


def download_image(image_url: str, save_path: str) -> bool:
    """
    Download an image from URL and save it locally.

    Args:
        image_url: URL of the image to download
        save_path: Local path where to save the image

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        response = requests.get(image_url, timeout=10, stream=True)
        response.raise_for_status()

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True
    except Exception as e:
        logger.error(f"Rasmni yuklab olishda xatolik ({image_url}): {e}")
        return False


def get_product_images_from_yandex(
    product_name: str, brand: str, max_images: int = 5
) -> List[str]:
    """
    Search and download product images from Yandex.

    Args:
        product_name: Name of the product
        brand: Brand of the product
        max_images: Maximum number of images to download

    Returns:
        List[str]: List of local file paths to downloaded images
    """
    # Create search query
    search_text = f"{product_name} {brand}"
    logger.info(f"Yandex'da rasm qidiryapman: {search_text}")

    # Search for images
    image_urls = search_yandex_images(search_text, max_images=max_images)

    if not image_urls:
        logger.warning(f"Yandex'da rasm topilmadi: {search_text}")
        return []

    # Download images
    downloaded_paths = []
    media_dir = Path("media/products")
    media_dir.mkdir(parents=True, exist_ok=True)

    # Create a safe filename from product name and brand
    safe_name = "".join(
        c for c in f"{product_name}_{brand}" if c.isalnum() or c in (" ", "-", "_")
    ).strip()
    safe_name = safe_name.replace(" ", "_").lower()

    for idx, img_url in enumerate(image_urls, start=1):
        # Get file extension from URL or default to .jpg
        file_ext = ".jpg"
        if "." in img_url.split("/")[-1].split("?")[0]:
            file_ext = "." + img_url.split("/")[-1].split("?")[0].split(".")[-1]
            if len(file_ext) > 5:  # Sanity check
                file_ext = ".jpg"

        save_path = media_dir / f"{safe_name}_{idx}{file_ext}"
        save_path_str = str(save_path)

        if download_image(img_url, save_path_str):
            downloaded_paths.append(save_path_str)
            logger.info(f"Rasm yuklandi: {save_path_str}")

    return downloaded_paths
