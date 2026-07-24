"""
===========================================
TMY Quiz Maker
Version 4.0

Fichier : widgets.py

Widgets modernes réutilisables.
===========================================
"""

import customtkinter as ctk

from ui.colors import (
    ENTRY,
    ENTRY_BORDER,
    ENTRY_PLACEHOLDER,
    TEXT,
    TEXT_SECONDARY,
    BORDER,
    PROGRESS,
)

from ui.fonts import (
    ENTRY as ENTRY_FONT,
    OPTION_MENU,
    SECTION_TITLE,
    TEXT as TEXT_FONT,
)


# ==================================================
# Titre de section
# ==================================================

class SectionTitle(ctk.CTkLabel):

    def __init__(self, master, text="", **kwargs):

        super().__init__(
            master,
            text=text,
            font=SECTION_TITLE,
            text_color=TEXT,
            anchor="w",
            **kwargs
        )


# ==================================================
# Champ de saisie moderne
# ==================================================

class ModernEntry(ctk.CTkEntry):

    def __init__(
        self,
        master,
        placeholder_text="",
        width=520,
        **kwargs
    ):

        super().__init__(
            master,
            width=width,
            height=42,
            corner_radius=12,
            fg_color=ENTRY,
            border_color=ENTRY_BORDER,
            border_width=1,
            text_color=TEXT,
            placeholder_text=placeholder_text,
            placeholder_text_color=ENTRY_PLACEHOLDER,
            font=ENTRY_FONT,
            **kwargs
        )


# ==================================================
# Menu déroulant moderne
# ==================================================

class ModernOptionMenu(ctk.CTkOptionMenu):

    def __init__(
        self,
        master,
        values,
        width=220,
        **kwargs
    ):

        super().__init__(
            master,
            values=values,
            width=width,
            height=42,
            corner_radius=12,
            font=OPTION_MENU,
            **kwargs
        )


# ==================================================
# Barre de progression moderne
# ==================================================

class ProgressWidget(ctk.CTkFrame):

    def __init__(self, master, width=520, **kwargs):

        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )

        self.label = ctk.CTkLabel(
            self,
            text="Prêt",
            font=TEXT_FONT,
            text_color=TEXT_SECONDARY
        )

        self.label.pack(pady=(0, 6))

        self.progress = ctk.CTkProgressBar(
            self,
            width=width,
            progress_color=PROGRESS
        )

        self.progress.pack()

        self.progress.set(0)

    def set(self, value):

        self.progress.set(value)

    def text(self, message):

        self.label.configure(text=message)

    def reset(self):

        self.progress.set(0)

        self.label.configure(text="")


# ==================================================
# Badge moderne
# ==================================================

class Badge(ctk.CTkFrame):

    def __init__(
        self,
        master,
        text="Badge",
        width=120,
        **kwargs
    ):

        super().__init__(
            master,
            width=width,
            height=35,
            corner_radius=15,
            fg_color=BORDER,
            **kwargs
        )

        self.pack_propagate(False)

        self.label = ctk.CTkLabel(
            self,
            text=text,
            text_color=TEXT,
            font=TEXT_FONT
        )

        self.label.pack(expand=True)

    def set_text(self, text):

        self.label.configure(text=text)


# ==================================================
# Compteur
# ==================================================

class Counter(ctk.CTkFrame):

    def __init__(
        self,
        master,
        title="Questions",
        value="0",
        **kwargs
    ):

        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )

        self.title = ctk.CTkLabel(
            self,
            text=title,
            font=TEXT_FONT,
            text_color=TEXT_SECONDARY
        )

        self.title.pack()

        self.value = ctk.CTkLabel(
            self,
            text=value,
            font=("Arial", 26, "bold"),
            text_color=TEXT
        )

        self.value.pack()

    def set(self, value):

        self.value.configure(text=str(value))


# ==================================================
# Ligne de séparation
# ==================================================

class Separator(ctk.CTkFrame):

    def __init__(
        self,
        master,
        width=520,
        **kwargs
    ):

        super().__init__(
            master,
            width=width,
            height=2,
            fg_color=BORDER,
            corner_radius=2,
            **kwargs
        )

        self.pack_propagate(False)