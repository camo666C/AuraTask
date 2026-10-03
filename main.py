import sys
import customtkinter as ctk
from src.app import AuraTaskApp


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    storage_file = "tasks.json"
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        storage_file = sys.argv[1]

    app = AuraTaskApp(storage_path=storage_file)
    app.mainloop()


if __name__ == "__main__":
    main()
