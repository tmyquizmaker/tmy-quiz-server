"""
===========================================
TMY Quiz Maker
Version 5.0

quiz_share_pin.py - Écran de génération de Code PIN & Partage
===========================================
"""

import random
import customtkinter as ctk

class QuizSharePinPage(ctk.CTkFrame):

    def __init__(self, master, quiz_title, export_pdf_callback, back_home_callback):
        super().__init__(master, fg_color="#121620")

        self.quiz_title = quiz_title
        self.export_pdf_callback = export_pdf_callback
        self.back_home_callback = back_home_callback

        # Génération d'un Code PIN unique à 6 chiffres
        self.game_pin = f"{random.randint(100, 999)} {random.randint(100, 999)}"

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40, pady=40)

        # Carte centrale
        self.card = ctk.CTkFrame(
            self.container,
            fg_color="#1E222D",
            corner_radius=20,
            border_width=1,
            border_color="#2B303C"
        )
        self.card.pack(expand=True, fill="both", padx=80, pady=30)

        self.content = ctk.CTkFrame(self.card, fg_color="transparent")
        self.content.pack(expand=True, padx=30, pady=30)

        # Titre & Statut
        self.badge = ctk.CTkLabel(
            self.content,
            text="🎉 QUIZ CRÉÉ AVEC SUCCÈS !",
            font=("Arial", 11, "bold"),
            text_color="#2E7D32"
        )
        self.badge.pack(pady=(0, 10))

        self.title = ctk.CTkLabel(
            self.content,
            text=f"« {self.quiz_title} »",
            font=("Arial", 18, "bold"),
            text_color="#FFFFFF"
        )
        self.title.pack(pady=(0, 20))

        # Encadré du CODE PIN
        self.pin_frame = ctk.CTkFrame(self.content, fg_color="#121620", corner_radius=14, border_width=1, border_color="#1F6AA5")
        self.pin_frame.pack(fill="x", padx=40, pady=(0, 20))

        self.pin_sub = ctk.CTkLabel(
            self.pin_frame,
            text="GAME PIN (PARTAGE CE CODE)",
            font=("Arial", 10, "bold"),
            text_color="#AAAAAA"
        )
        self.pin_sub.pack(pady=(10, 2))

        self.pin_val = ctk.CTkLabel(
            self.pin_frame,
            text=self.game_pin,
            font=("Arial", 32, "bold"),
            text_color="#FFD700"
        )
        self.pin_val.pack(pady=(0, 10))

        # Notice d'utilisation
        self.info_text = ctk.CTkLabel(
            self.content,
            text="🔒 En tant que créateur, vous ne pouvez pas jouer à ce quiz.\nDonnez ce code PIN à vos joueurs pour qu'ils s'affrontent !",
            font=("Arial", 11),
            text_color="#8A8F9E",
            justify="center"
        )
        self.info_text.pack(pady=(0, 20))

        # Boutons d'actions
        self.btn_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.btn_frame.pack(fill="x")

        # Exporter PDF
        self.pdf_btn = ctk.CTkButton(
            self.btn_frame,
            text="📄 Exporter en PDF",
            font=("Arial", 12, "bold"),
            height=40,
            fg_color="#1F6AA5",
            hover_color="#144870",
            command=self.export_pdf_callback
        )
        self.pdf_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        # Retour Accueil
        self.home_btn = ctk.CTkButton(
            self.btn_frame,
            text="🏠 Retour à l'accueil",
            font=("Arial", 12, "bold"),
            height=40,
            fg_color="#2B2D42",
            hover_color="#1A1B29",
            command=self.back_home_callback
        )
        self.home_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))