"""
===========================================
TMY Quiz Maker
Version 4.0

Fichier : cards.py

Cartes modernes réutilisables
===========================================
"""

import customtkinter as ctk


class ModernCard(ctk.CTkFrame):
    """
    Carte moderne utilisée dans toute l'application.
    """

    def __init__(
        self,
        master,
        width=600,
        height=300,
        corner_radius=20,
        fg_color="#1E293B",
        border_width=1,
        border_color="#334155",
        **kwargs
    ):

        super().__init__(
            master=master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            fg_color=fg_color,
            border_width=border_width,
            border_color=border_color,
            **kwargs
        )

        self.pack_propagate(False)


class SectionCard(ctk.CTkFrame):
    """
    Petite carte servant à regrouper un champ
    (Sujet, Niveau, Nombre de questions...)
    """

    def __init__(
        self,
        master,
        title="",
        width=540,
        height=95,
        **kwargs
    ):

        super().__init__(
            master=master,
            width=width,
            height=height,
            fg_color="#243447",
            corner_radius=15,
            border_width=1,
            border_color="#3B4A5A",
            **kwargs
        )

        self.pack_propagate(False)

        self.title = ctk.CTkLabel(
            self,
            text=title,
            font=("Arial", 15, "bold"),
            text_color="white"
        )

        self.title.pack(
            anchor="w",
            padx=15,
            pady=(10, 5)
        )


class StatsCard(ctk.CTkFrame):
    """
    Carte affichant une statistique.
    Exemple :
        📊 Quiz joués
        35
    """

    def __init__(
        self,
        master,
        icon="📊",
        title="Titre",
        value="0",
        width=170,
        height=110,
        **kwargs
    ):

        super().__init__(
            master=master,
            width=width,
            height=height,
            fg_color="#1E293B",
            corner_radius=18,
            border_width=1,
            border_color="#334155",
            **kwargs
        )

        self.pack_propagate(False)

        self.icon = ctk.CTkLabel(
            self,
            text=icon,
            font=("Segoe UI Emoji", 24)
        )

        self.icon.pack(pady=(10, 2))

        self.label = ctk.CTkLabel(
            self,
            text=title,
            font=("Arial", 13),
            text_color="#CBD5E1"
        )

        self.label.pack()

        self.value = ctk.CTkLabel(
            self,
            text=value,
            font=("Arial", 24, "bold"),
            text_color="white"
        )

        self.value.pack(pady=(5, 10))

    def set_value(self, value):
        """
        Met à jour la valeur affichée.
        """

        self.value.configure(text=str(value))


class ProgressCard(ctk.CTkFrame):
    """
    Carte contenant une barre de progression.
    """

    def __init__(
        self,
        master,
        width=560,
        height=90,
        **kwargs
    ):

        super().__init__(
            master=master,
            width=width,
            height=height,
            fg_color="#243447",
            corner_radius=15,
            border_width=1,
            border_color="#334155",
            **kwargs
        )

        self.pack_propagate(False)

        self.label = ctk.CTkLabel(
            self,
            text="Prêt",
            font=("Arial", 14)
        )

        self.label.pack(pady=(12, 5))

        self.progress = ctk.CTkProgressBar(
            self,
            width=500
        )

        self.progress.pack()

        self.progress.set(0)

    def set_progress(self, value):
        """
        value entre 0 et 1
        """
        self.progress.set(value)

    def set_text(self, text):
        self.label.configure(text=text)