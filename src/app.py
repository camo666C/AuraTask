import tkinter as tk
from typing import List, Optional
import customtkinter as ctk
from PIL import ImageTk

from .models import Task
from .storage import TaskStorage
from .icons import IconManager
from .glass_theme import GlassColors, apply_windows_acrylic


class AuraTaskApp(ctk.CTk):
    def __init__(self, storage_path: str = "tasks.json"):
        super().__init__()

        # Инициализация хранилища и состояния
        self.storage = TaskStorage(storage_path)
        self.tasks: List[Task] = []
        self.filter_status = "Все"
        self.filter_priority = "Все приоритеты"
        self.search_query = ""

        # Настройки базового окна
        self.title("AuraTask - Диспетчер задач")
        self.geometry("860x640")
        self.minsize(760, 540)
        self.configure(fg_color=GlassColors.BG_WINDOW)

        # Применяем акрил/DWM при запуске на Windows
        apply_windows_acrylic(self)

        # Установка иконки приложения
        self._setup_app_icon()

        # Построение интерфейса
        self._build_ui()

        # Загрузка данных
        self.load_data()

    def _setup_app_icon(self):
        try:
            pil_icon = IconManager.get_app_icon_pil(64)
            self._icon_photo = ImageTk.PhotoImage(pil_icon)
            self.iconphoto(False, self._icon_photo)
        except Exception:
            pass

    def _build_ui(self):
        # Корневая сетка
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Верхняя панель (Header)
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color=GlassColors.BG_HEADER,
            corner_radius=0,
            border_width=1,
            border_color=GlassColors.BORDER_SUBTLE
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self._build_header()

        # 2. Панель добавления задачи и быстрых фильтров
        self.controls_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.controls_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(15, 10))
        self._build_controls()

        # 3. Список задач со скроллом
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=8
        )
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=5)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # 4. Нижний статус-бар
        self.status_bar = ctk.CTkFrame(
            self,
            fg_color=GlassColors.BG_HEADER,
            corner_radius=0,
            height=36,
            border_width=1,
            border_color=GlassColors.BORDER_SUBTLE
        )
        self.status_bar.grid(row=3, column=0, sticky="ew", padx=0, pady=0)
        self._build_status_bar()

    def _build_header(self):
        self.header_frame.grid_columnconfigure(1, weight=1)

        # Заголовок и подзаголовок
        title_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w", padx=20, pady=12)

        title_lbl = ctk.CTkLabel(
            title_box,
            text="AuraTask",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=GlassColors.ACCENT_CYAN
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            title_box,
            text="Персональный трекер задач",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=GlassColors.TEXT_MUTED
        )
        sub_lbl.pack(anchor="w")

        # Поле поиска
        search_box = ctk.CTkFrame(
            self.header_frame,
            fg_color=GlassColors.BG_INPUT,
            corner_radius=8,
            border_width=1,
            border_color=GlassColors.BORDER_SUBTLE
        )
        search_box.grid(row=0, column=1, sticky="ew", padx=(10, 20), pady=12)
        search_box.grid_columnconfigure(1, weight=1)

        search_icon = ctk.CTkLabel(
            search_box,
            text="",
            image=IconManager.get_icon("search", size=16, color=GlassColors.TEXT_MUTED)
        )
        search_icon.grid(row=0, column=0, padx=(10, 5), pady=6)

        self.search_entry = ctk.CTkEntry(
            search_box,
            placeholder_text="Поиск по задачам...",
            fg_color="transparent",
            border_width=0,
            text_color=GlassColors.TEXT_PRIMARY,
            placeholder_text_color=GlassColors.TEXT_MUTED,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=4)
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        # Счетчики и прогресс
        stats_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        stats_box.grid(row=0, column=2, sticky="e", padx=20, pady=12)

        self.stats_label = ctk.CTkLabel(
            stats_box,
            text="0 / 0 выполнено",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=GlassColors.TEXT_SECONDARY
        )
        self.stats_label.pack(anchor="e")

        self.progress_bar = ctk.CTkProgressBar(
            stats_box,
            width=140,
            height=8,
            corner_radius=4,
            progress_color=GlassColors.ACCENT_CYAN,
            fg_color=GlassColors.BG_INPUT
        )
        self.progress_bar.pack(anchor="e", pady=(4, 0))
        self.progress_bar.set(0.0)

    def _build_controls(self):
        self.controls_frame.grid_columnconfigure(0, weight=1)

        # Карточка быстрого добавления
        add_card = ctk.CTkFrame(
            self.controls_frame,
            fg_color=GlassColors.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=GlassColors.BORDER_SUBTLE
        )
        add_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        add_card.grid_columnconfigure(0, weight=1)

        # Верхняя строка карточки: инпут названия и кнопка добавления
        input_row = ctk.CTkFrame(add_card, fg_color="transparent")
        input_row.pack(fill="x", padx=12, pady=(10, 6))
        input_row.grid_columnconfigure(0, weight=1)

        self.task_entry = ctk.CTkEntry(
            input_row,
            placeholder_text="Новая задача...",
            fg_color=GlassColors.BG_INPUT,
            border_width=1,
            border_color=GlassColors.BORDER_SUBTLE,
            text_color=GlassColors.TEXT_PRIMARY,
            placeholder_text_color=GlassColors.TEXT_MUTED,
            height=36,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.task_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.task_entry.bind("<Return>", lambda e: self.add_task())

        add_btn = ctk.CTkButton(
            input_row,
            text="Добавить",
            image=IconManager.get_icon("plus", size=16, color="#FFFFFF"),
            compound="left",
            fg_color=GlassColors.ACCENT_CYAN,
            hover_color=GlassColors.ACCENT_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=36,
            corner_radius=6,
            command=self.add_task
        )
        add_btn.grid(row=0, column=1)

        # Нижняя строка карточки: категория и выбор приоритета
        meta_row = ctk.CTkFrame(add_card, fg_color="transparent")
        meta_row.pack(fill="x", padx=12, pady=(0, 10))

        cat_lbl = ctk.CTkLabel(
            meta_row,
            text="Категория:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=GlassColors.TEXT_MUTED
        )
        cat_lbl.pack(side="left", padx=(0, 6))

        self.category_var = tk.StringVar(value="Общее")
        self.category_opt = ctk.CTkOptionMenu(
            meta_row,
            values=["Общее", "Учеба", "Работа", "Личное", "Проект"],
            variable=self.category_var,
            fg_color=GlassColors.BG_INPUT,
            button_color=GlassColors.BORDER_SUBTLE,
            button_hover_color=GlassColors.ACCENT_CYAN,
            text_color=GlassColors.TEXT_PRIMARY,
            height=28,
            width=110,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.category_opt.pack(side="left", padx=(0, 20))

        prio_lbl = ctk.CTkLabel(
            meta_row,
            text="Приоритет:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=GlassColors.TEXT_MUTED
        )
        prio_lbl.pack(side="left", padx=(0, 6))

        self.priority_seg = ctk.CTkSegmentedButton(
            meta_row,
            values=["Низкий", "Обычный", "Срочно"],
            selected_color=GlassColors.ACCENT_CYAN,
            selected_hover_color=GlassColors.ACCENT_HOVER,
            unselected_color=GlassColors.BG_INPUT,
            unselected_hover_color=GlassColors.BG_CARD_HOVER,
            text_color=GlassColors.TEXT_PRIMARY,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.priority_seg.set("Обычный")
        self.priority_seg.pack(side="left")

        # Панель фильтров списка
        filter_row = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        filter_row.grid(row=1, column=0, sticky="ew")

        # Переключатель статуса: Все / В работе / Завершенные
        self.status_seg = ctk.CTkSegmentedButton(
            filter_row,
            values=["Все", "В работе", "Завершенные"],
            command=self._on_status_filter_changed,
            selected_color=GlassColors.ACCENT_CYAN,
            selected_hover_color=GlassColors.ACCENT_HOVER,
            unselected_color=GlassColors.BG_CARD,
            unselected_hover_color=GlassColors.BG_CARD_HOVER,
            text_color=GlassColors.TEXT_PRIMARY,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.status_seg.set("Все")
        self.status_seg.pack(side="left", padx=(0, 12))

        # Фильтр приоритета
        self.prio_filter_opt = ctk.CTkOptionMenu(
            filter_row,
            values=["Все приоритеты", "Срочно", "Обычный", "Низкий"],
            command=self._on_priority_filter_changed,
            fg_color=GlassColors.BG_CARD,
            button_color=GlassColors.BORDER_SUBTLE,
            button_hover_color=GlassColors.ACCENT_CYAN,
            text_color=GlassColors.TEXT_PRIMARY,
            height=28,
            width=140,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.prio_filter_opt.set("Все приоритеты")
        self.prio_filter_opt.pack(side="left")

    def _build_status_bar(self):
        self.status_bar.grid_columnconfigure(1, weight=1)

        self.storage_label = ctk.CTkLabel(
            self.status_bar,
            text=f"Файл: {self.storage.filename}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=GlassColors.TEXT_MUTED
        )
        self.storage_label.grid(row=0, column=0, sticky="w", padx=20, pady=6)

        clear_done_btn = ctk.CTkButton(
            self.status_bar,
            text="Очистить завершенные",
            image=IconManager.get_icon("trash", size=14, color=GlassColors.TEXT_MUTED),
            compound="left",
            fg_color="transparent",
            hover_color=GlassColors.BG_CARD_HOVER,
            text_color=GlassColors.TEXT_MUTED,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            height=24,
            command=self.clear_completed
        )
        clear_done_btn.grid(row=0, column=2, sticky="e", padx=20, pady=6)

    def load_data(self):
        self.tasks = self.storage.load_tasks()
        self.render_tasks()

    def save_data(self):
        self.storage.save_tasks(self.tasks)
        self._update_stats()

    def add_task(self):
        text = self.task_entry.get().strip()
        if not text:
            return

        prio_map = {"Низкий": "low", "Обычный": "medium", "Срочно": "high"}
        prio = prio_map.get(self.priority_seg.get(), "medium")
        category = self.category_var.get().strip() or "Общее"

        task = Task(title=text, priority=prio, category=category)
        self.tasks.insert(0, task)
        self.task_entry.delete(0, "end")
        self.save_data()
        self.render_tasks()

    def toggle_task(self, task: Task, switch_widget: ctk.CTkSwitch):
        task.completed = bool(switch_widget.get())
        self.save_data()
        # Перерисовываем для актуализации фильтров и стилей
        self.render_tasks()

    def delete_task(self, task: Task):
        if task in self.tasks:
            self.tasks.remove(task)
            self.save_data()
            self.render_tasks()

    def clear_completed(self):
        self.tasks = [t for t in self.tasks if not t.completed]
        self.save_data()
        self.render_tasks()

    def _on_search_changed(self, event=None):
        self.search_query = self.search_entry.get().strip().lower()
        self.render_tasks()

    def _on_status_filter_changed(self, value: str):
        self.filter_status = value
        self.render_tasks()

    def _on_priority_filter_changed(self, value: str):
        self.filter_priority = value
        self.render_tasks()

    def _get_filtered_tasks(self) -> List[Task]:
        filtered = self.tasks

        # Фильтр по статусу
        if self.filter_status == "В работе":
            filtered = [t for t in filtered if not t.completed]
        elif self.filter_status == "Завершенные":
            filtered = [t for t in filtered if t.completed]

        # Фильтр по приоритету
        prio_map = {"Срочно": "high", "Обычный": "medium", "Низкий": "low"}
        if self.filter_priority in prio_map:
            target = prio_map[self.filter_priority]
            filtered = [t for t in filtered if t.priority == target]

        # Поиск по подстроке
        if self.search_query:
            filtered = [
                t for t in filtered
                if self.search_query in t.title.lower() or self.search_query in t.category.lower()
            ]

        return filtered

    def _update_stats(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t.completed)
        self.stats_label.configure(text=f"{done} / {total} выполнено")
        ratio = (done / total) if total > 0 else 0.0
        self.progress_bar.set(ratio)

    def render_tasks(self):
        # Очищаем контейнер списка
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        filtered_tasks = self._get_filtered_tasks()

        if not filtered_tasks:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="Список задач пуст",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=GlassColors.TEXT_MUTED
            )
            empty_lbl.pack(pady=40)
            self._update_stats()
            return

        for task in filtered_tasks:
            self._render_task_item(task)

        self._update_stats()

    def _render_task_item(self, task: Task):
        # Карточка задачи со стеклянным фоном
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=GlassColors.BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=GlassColors.BORDER_SUBTLE
        )
        card.pack(fill="x", pady=4, padx=2)
        card.grid_columnconfigure(1, weight=1)

        # 1. Переключатель статуса (CTkSwitch)
        switch = ctk.CTkSwitch(
            card,
            text="",
            width=42,
            progress_color=GlassColors.ACCENT_GREEN,
            button_color=GlassColors.TEXT_PRIMARY,
            button_hover_color="#E2E8F0",
            fg_color=GlassColors.BG_INPUT
        )
        if task.completed:
            switch.select()
        else:
            switch.deselect()

        switch.configure(command=lambda t=task, s=switch: self.toggle_task(t, s))
        switch.grid(row=0, column=0, padx=(12, 8), pady=10)

        # 2. Центральная область: название, категория, дата
        info_box = ctk.CTkFrame(card, fg_color="transparent")
        info_box.grid(row=0, column=1, sticky="w", padx=4, pady=8)

        # Название задачи
        title_color = GlassColors.TEXT_MUTED if task.completed else GlassColors.TEXT_PRIMARY
        title_font = ctk.CTkFont(
            family="Segoe UI",
            size=13,
            overstrike=1 if task.completed else 0
        )
        title_lbl = ctk.CTkLabel(
            info_box,
            text=task.title,
            font=title_font,
            text_color=title_color,
            anchor="w"
        )
        title_lbl.pack(anchor="w")

        # Строка метаданных (категория, дата)
        meta_box = ctk.CTkFrame(info_box, fg_color="transparent")
        meta_box.pack(anchor="w", pady=(3, 0))

        cat_badge = ctk.CTkLabel(
            meta_box,
            text=task.category,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=GlassColors.ACCENT_CYAN,
            fg_color=GlassColors.BG_INPUT,
            corner_radius=4,
            padx=6,
            pady=1
        )
        cat_badge.pack(side="left", padx=(0, 8))

        date_lbl = ctk.CTkLabel(
            meta_box,
            text=task.created_at,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=GlassColors.TEXT_MUTED
        )
        date_lbl.pack(side="left")

        # 3. Правая область: бейдж приоритета и кнопка удаления
        actions_box = ctk.CTkFrame(card, fg_color="transparent")
        actions_box.grid(row=0, column=2, sticky="e", padx=(8, 12), pady=8)

        # Индикатор приоритета
        prio_colors = {
            "high": (GlassColors.ACCENT_RED, "Срочно"),
            "medium": (GlassColors.ACCENT_AMBER, "Обычный"),
            "low": (GlassColors.TEXT_MUTED, "Низкий")
        }
        prio_color, prio_text = prio_colors.get(task.priority, (GlassColors.TEXT_MUTED, "Обычный"))

        prio_badge = ctk.CTkLabel(
            actions_box,
            text=prio_text,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=prio_color,
            fg_color=GlassColors.BG_INPUT,
            corner_radius=4,
            padx=6,
            pady=2
        )
        prio_badge.pack(side="left", padx=(0, 10))

        # Кнопка удаления с иконкой корзины
        del_btn = ctk.CTkButton(
            actions_box,
            text="",
            image=IconManager.get_icon("trash", size=15, color=GlassColors.TEXT_MUTED),
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=GlassColors.BG_INPUT,
            corner_radius=6,
            command=lambda t=task: self.delete_task(t)
        )
        del_btn.pack(side="left")
