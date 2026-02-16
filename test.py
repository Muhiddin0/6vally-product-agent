import os
from PIL import Image


def format_image(image_path: str, output_quality: int = 80):
    """
    Berilgan rasmni 853x1280 o'lchamli oq ramkaga soladi,
    ikki chekkadan 7px padding qoldiradi va .webp formatida saqlaydi.
    """
    # 1. Oq fondagi ramka yaratish (853x1280)
    canvas_width = 853
    canvas_height = 1280
    new_img = Image.new("RGB", (canvas_width, canvas_height), (255, 255, 255))

    # 2. Asl rasmni ochish
    img = Image.open(image_path).convert("RGB")

    # 3. O'lchamlarni hisoblash
    # Ikki chekkadan 7px padding qolsa: 853 - (7 * 2) = 839px
    max_allowed_width = canvas_width - 14

    # Rasmni proporsiyasini saqlab, ruxsat etilgan kenglikka moslash
    w_percent = max_allowed_width / float(img.size[0])
    h_size = int((float(img.size[1]) * float(w_percent)))

    # Agar rasm juda uzun bo'lib ketsa, bo'yi bo'yicha ham tekshiramiz
    if h_size > canvas_height:
        h_size = canvas_height
        w_percent = h_size / float(img.size[1])
        max_allowed_width = int((float(img.size[0]) * float(w_percent)))

    img = img.resize((max_allowed_width, h_size), Image.Resampling.LANCZOS)

    # 4. Markazga joylashtirish koordinatalarini topish
    offset_x = (canvas_width - img.size[0]) // 2
    offset_y = (canvas_height - img.size[1]) // 2

    # 5. Rasmni oq fonga qo'yish
    new_img.paste(img, (offset_x, offset_y))

    # 6. .webp formatida saqlash
    # Fayl nomini o'zgartirish (masalan: rasm.jpg -> rasm_formatted.webp)
    base_name = os.path.splitext(image_path)[0]
    output_path = f"{base_name}_formatted.webp"

    new_img.save(output_path, "WEBP", quality=output_quality)

    print(f"Rasm tayyor: {output_path}")
    return output_path


# Ishlatish:
format_image("./2026-02-10-698b0cdd68ee4.webp")
