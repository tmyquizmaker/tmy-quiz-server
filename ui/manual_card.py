"""
===========================================
TMY Quiz Maker
Version 5.0

manual_card.py - Carte d'action "Créer Manuellement"
===========================================
"""

import customtkinter as ctk

class ManualQuizCard(ctk.CTkFrame):

    def __init__(self, master, create_callback):
        super().__init__(
            master,
            fg_color="#1E222D",
            corner_radius=18,
            border_width=1,
            border_color="#2B303C"
        )
        self.create_callback = create_callback

        # Conteneur interne avec padding
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Icône Stylo / Édition
        self.icon_label = ctk.CTkLabel(
            self.container,
            text="✍️",
            font=("Arial", 28)
        )
        self.icon_label.pack(anchor="w", pady=(0, 5))

        # Titre
        self.title_label = ctk.CTkLabel(
            self.container,
            text="CRÉER MANUELLEMENT",
            font=("Arial", 16, "bold"),
            text_color="#FFFFFF"
        )
        self.title_label.pack(anchor="w", pady=(0, 5))

        # Description
        self.desc_label = ctk.CTkLabel(
            self.container,
            text="Rédige tes propres questions, réponses, explications et minuteurs personnalisés.",
            font=("Arial", 11),
            text_color="#8A8F9E",
            wraplength=280,
            justify="left"
        )
        self.desc_label.pack(anchor="w", pady=(0, 15))

        # Bouton d'action
        self.action_btn = ctk.CTkButton(
            self.container,
            text="CRÉER UN QUIZ",
            font=("Arial", 12, "bold"),
            height=40,
            corner_radius=10,
            fg_color="#2B2D42",
            hover_color="#1F6AA5",
            text_color="#FFFFFF",
            command=self.create_callback
        )
        self.action_btn.pack(fill="x")