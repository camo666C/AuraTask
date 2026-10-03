import sys
import ctypes


class GlassColors:
    # Базовая темная палитра с эффектом матового стекла
    BG_WINDOW = "#0B0F17"
    BG_HEADER = "#0F1623"
    BG_CARD = "#141C2B"
    BG_CARD_HOVER = "#1B2538"
    BG_INPUT = "#0D131F"
    
    # Тонкие границы карточек для эффекта стекла
    BORDER_SUBTLE = "#1E293B"
    BORDER_FOCUS = "#0EA5E9"
    
    # Акцентные цвета
    ACCENT_CYAN = "#0EA5E9"
    ACCENT_HOVER = "#0284C7"
    ACCENT_GREEN = "#10B981"
    ACCENT_RED = "#EF4444"
    ACCENT_AMBER = "#F59E0B"
    
    # Текстовые оттенки
    TEXT_PRIMARY = "#F8FAFC"
    TEXT_SECONDARY = "#94A3B8"
    TEXT_MUTED = "#64748B"


def apply_windows_acrylic(window):
    """
    Применяет темную тему DWM и эффект акрила на Windows 10/11.
    На Linux/macOS вызов безопасно игнорируется.
    """
    if sys.platform != "win32":
        return

    try:
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        if not hwnd:
            hwnd = window.winfo_id()

        dwmapi = ctypes.windll.dwmapi

        # Темный заголовок окна (DWMWA_USE_IMMERSIVE_DARK_MODE)
        value = ctypes.c_int(2)
        dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))

        # Windows 11 System Backdrop: 3 = Acrylic, 2 = Mica
        backdrop = ctypes.c_int(3)
        dwmapi.DwmSetWindowAttribute(hwnd, 38, ctypes.byref(backdrop), ctypes.sizeof(backdrop))
    except Exception:
        pass
