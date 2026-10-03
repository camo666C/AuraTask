from PIL import Image, ImageDraw
import customtkinter as ctk


class IconManager:
    _cache = {}

    @classmethod
    def get_icon(cls, name: str, size: int = 20, color: str = "#F1F5F9") -> ctk.CTkImage:
        key = (name, size, color)
        if key in cls._cache:
            return cls._cache[key]

        scale = 3
        dim = size * scale
        img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Рендерим нужную иконку по вектору
        if name == "plus":
            w = max(2, int(scale * 1.8))
            pad = int(dim * 0.22)
            draw.line([(dim // 2, pad), (dim // 2, dim - pad)], fill=color, width=w)
            draw.line([(pad, dim // 2), (dim - pad, dim // 2)], fill=color, width=w)

        elif name == "trash":
            w = max(2, int(scale * 1.5))
            # Крышка
            draw.line([(int(dim * 0.2), int(dim * 0.28)), (int(dim * 0.8), int(dim * 0.28))], fill=color, width=w)
            draw.line([(int(dim * 0.4), int(dim * 0.20)), (int(dim * 0.6), int(dim * 0.20))], fill=color, width=w)
            # Корпус
            draw.line([(int(dim * 0.28), int(dim * 0.28)), (int(dim * 0.34), int(dim * 0.82))], fill=color, width=w)
            draw.line([(int(dim * 0.72), int(dim * 0.28)), (int(dim * 0.66), int(dim * 0.82))], fill=color, width=w)
            draw.line([(int(dim * 0.34), int(dim * 0.82)), (int(dim * 0.66), int(dim * 0.82))], fill=color, width=w)
            # Внутренние линии
            draw.line([(int(dim * 0.44), int(dim * 0.38)), (int(dim * 0.44), int(dim * 0.72))], fill=color, width=w)
            draw.line([(int(dim * 0.56), int(dim * 0.38)), (int(dim * 0.56), int(dim * 0.72))], fill=color, width=w)

        elif name == "check":
            w = max(2, int(scale * 2.0))
            pts = [(int(dim * 0.2), int(dim * 0.52)), (int(dim * 0.42), int(dim * 0.74)), (int(dim * 0.82), int(dim * 0.28))]
            draw.line(pts, fill=color, width=w, joint="curve")

        elif name == "search":
            w = max(2, int(scale * 1.6))
            r = int(dim * 0.26)
            cx, cy = int(dim * 0.42), int(dim * 0.42)
            draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=color, width=w)
            draw.line([(int(dim * 0.62), int(dim * 0.62)), (int(dim * 0.82), int(dim * 0.82))], fill=color, width=w)

        elif name == "filter":
            w = max(2, int(scale * 1.5))
            poly = [
                (int(dim * 0.2), int(dim * 0.25)),
                (int(dim * 0.8), int(dim * 0.25)),
                (int(dim * 0.56), int(dim * 0.55)),
                (int(dim * 0.56), int(dim * 0.78)),
                (int(dim * 0.44), int(dim * 0.78)),
                (int(dim * 0.44), int(dim * 0.55)),
            ]
            draw.polygon(poly, outline=color, width=w)

        elif name == "refresh":
            w = max(2, int(scale * 1.6))
            bbox = [(int(dim * 0.2), int(dim * 0.2)), (int(dim * 0.8), int(dim * 0.8))]
            draw.arc(bbox, start=30, end=300, fill=color, width=w)
            # Стрелка
            arrow = [(int(dim * 0.75), int(dim * 0.22)), (int(dim * 0.85), int(dim * 0.38)), (int(dim * 0.66), int(dim * 0.42))]
            draw.polygon(arrow, fill=color)

        elif name == "clear":
            w = max(2, int(scale * 1.8))
            pad = int(dim * 0.26)
            draw.line([(pad, pad), (dim - pad, dim - pad)], fill=color, width=w)
            draw.line([(dim - pad, pad), (pad, dim - pad)], fill=color, width=w)

        else:
            # Дефолтный круг
            r = int(dim * 0.35)
            draw.ellipse([(dim // 2 - r, dim // 2 - r), (dim // 2 + r, dim // 2 + r)], outline=color, width=scale * 2)

        # Создаем CTkImage с высоким качеством сглаживания
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
        cls._cache[key] = ctk_img
        return ctk_img

    @classmethod
    def get_app_icon_pil(cls, size: int = 64) -> Image.Image:
        # Иконка приложения для окна
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Скругленный стеклянный фон
        pad = int(size * 0.08)
        draw.rounded_rectangle([(pad, pad), (size - pad, size - pad)], radius=int(size * 0.25), fill="#0F172A", outline="#0EA5E9", width=2)

        # Внутренний акцент
        inner_pad = int(size * 0.2)
        draw.line([(inner_pad, int(size * 0.35)), (size - inner_pad, int(size * 0.35))], fill="#38BDF8", width=3)
        draw.line([(inner_pad, int(size * 0.52)), (int(size * 0.65), int(size * 0.52))], fill="#94A3B8", width=3)
        draw.line([(inner_pad, int(size * 0.69)), (int(size * 0.5), int(size * 0.69))], fill="#64748B", width=3)

        return img
