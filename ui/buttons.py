"""
===========================================
TMY Quiz Maker
Version 4.0

Fichier : buttons.py

Boutons modernes réutilisables.
===========================================
"""

import customtkinter as ctk

from ui.colors import (
    BUTTON,
    BUTTON_HOVER,
    BUTTON_SUCCESS,
    BUTTON_SUCCESS_HOVER,
    BUTTON_ERROR,
    BUTTON_ERROR_HOVER,
    BUTTON_WARNING,
    BUTTON_WARNING_HOVER,
    TEXT
)

from ui.fonts import (
    BUTTON as BUTTON_FONT,
    BUTTON_SMALL,
    BUTTON_LARGE
)


# ==================================================
# Bouton principal
# ==================================================

class PrimaryButton(ctk.CTkButton):

    def __init__(self, master, **kwargs):

        super().__init__(

            master,

            fg_color=BUTTON,

            hover_color=BUTTON_HOVER,

            text_color=TEXT,

            corner_radius=12,

            height=50,

            font=BUTTON_FONT,

            cursor="hand2",

            **kwargs

        )


# ==================================================
# Grand bouton
# ==================================================

class LargeButton(ctk.CTkButton):

    def __init__(self, master, **kwargs):

        super().__init__(

            master,

            fg_color=BUTTON,

            hover_color=BUTTON_HOVER,

            text_color=TEXT,

            corner_radius=14,

            width=320,

            height=60,

            font=BUTTON_LARGE,

            cursor="hand2",

            **kwargs

        )


# ==================================================
# Petit bouton
# ==================================================

class SmallButton(ctk.CTkButton):

    def __init__(self, master, **kwargs):

        super().__init__(

            master,

            fg_color=BUTTON,

            hover_color=BUTTON_HOVER,

            text_color=TEXT,

            corner_radius=10,

            height=40,

            font=BUTTON_SMALL,

            cursor="hand2",

            **kwargs

        )


# ==================================================
# Bouton succès
# ==================================================

class SuccessButton(ctk.CTkButton):

    def __init__(self, master, **kwargs):

        super().__init__(

            master,

            fg_color=BUTTON_SUCCESS,

            hover_color=BUTTON_SUCCESS_HOVER,

            text_color=TEXT,

            corner_radius=12,

            height=50,

            font=BUTTON_FONT,

            cursor="hand2",

            **kwargs

        )


# ==================================================
# Bouton erreur
# ==================================================

class DangerButton(ctk.CTkButton):

    def __init__(self, master, **kwargs):

        super().__init__(

            master,

            fg_color=BUTTON_ERROR,

            hover_color=BUTTON_ERROR_HOVER,

            text_color=TEXT,

            corner_radius=12,

            height=50,

            font=BUTTON_FONT,

            cursor="hand2",

            **kwargs

        )


# ==================================================
# Bouton avertissement
# ==================================================

class WarningButton(ctk.CTkButton):

    def __init__(self, master, **kwargs):

        super().__init__(

            master,

            fg_color=BUTTON_WARNING,

            hover_color=BUTTON_WARNING_HOVER,

            text_color=TEXT,

            corner_radius=12,

            height=50,

            font=BUTTON_FONT,

            cursor="hand2",

            **kwargs

        )


# ==================================================
# Bouton réponse du quiz
# ==================================================

class QuizButton(ctk.CTkButton):

    def __init__(self, master, **kwargs):

        super().__init__(

            master,

            fg_color=BUTTON,

            hover_color=BUTTON_HOVER,

            text_color=TEXT,

            corner_radius=15,

            width=520,

            height=55,

            font=BUTTON_FONT,

            anchor="w",

            cursor="hand2",

            **kwargs

        )

    # ------------------------------------------

    def reset(self):

        self.configure(

            fg_color=BUTTON,

            hover_color=BUTTON_HOVER,

            state="normal"

        )

    # ------------------------------------------

    def success(self):

        self.configure(

            fg_color=BUTTON_SUCCESS,

            hover_color=BUTTON_SUCCESS_HOVER

        )

    # ------------------------------------------

    def error(self):

        self.configure(

            fg_color=BUTTON_ERROR,

            hover_color=BUTTON_ERROR_HOVER

        )

    # ------------------------------------------

    def disable(self):

        self.configure(

            state="disabled"

        )

    # ------------------------------------------

    def enable(self):

        self.configure(

            state="normal"

        )