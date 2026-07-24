"""
===========================================
TMY Quiz Maker
Version 5.0

quiz_loading.py - Écran de chargement dynamique et animé
===========================================
"""

import os
import customtkinter as ctk
from PIL import Image

import ui.colors as colors
import ui.fonts as fonts


class QuizLoadingPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color=colors.BACKGROUND)
        self.angle = 0
        self.is_animating = True

        # Liste des messages d'attente dynamiques
        self.loading_messages = [
            "🤖 Analyse du sujet par l'IA...",
            "✍️ Rédaction des questions & choix...",
            "🧩 Génération des explications détaillées...",
            "🎯 Calibrage du niveau de difficulté...",
            "✨ Finalisation de la session de jeu..."
        ]
        self.msg_index = 0

        # Conteneur principal centré
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40, pady=40)

        # ===============================================
        # CARTE CENTRALE MODERNE
        # ===============================================
        self.card = ctk.CTkFrame(
            self.container,
            fg_color="#1E222D",
            corner_radius=20,
            border_width=1,
            border_color="#2B303C"
        )
        self.card.pack(expand=True, fill="both", padx=80, pady=40)

        # Frame de contenu interne
        self.content = ctk.CTkFrame(self.card, fg_color="transparent")
        self.content.pack(expand=True)

        # ===============================================
        # 1. LOGO ANIMÉ
        # ===============================================
        self.logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(self.logo_path):
            try:
                raw_image = Image.open(self.logo_path)
                self.logo_image = ctk.CTkImage(
                    light_image=raw_image,
                    dark_image=raw_image,
                    size=(130, 130)
                )
                self.logo = ctk.CTkLabel(self.content, image=self.logo_image, text="")
                self.logo.pack(pady=(0, 20))
            except Exception:
                self.create_fallback_logo()
        else:
            self.create_fallback_logo()

        # ===============================================
        # 2. BADGE & TITRE
        # ===============================================
        self.badge = ctk.CTkFrame(self.content, fg_color="#121620", corner_radius=12)
        self.badge.pack(pady=(0, 10))

        self.badge_lbl = ctk.CTkLabel(
            self.badge,
            text="⚡ GENERATION IA TMY",
            font=("Arial", 10, "bold"),
            text_color="#1F6AA5"
        )
        self.badge_lbl.pack(padx=12, pady=4)

        self.title = ctk.CTkLabel(
            self.content,
            text="PRÉPARATION DE VOTRE QUIZ",
            font=("Arial", 20, "bold"),
            text_color="#FFFFFF"
        )
        self.title.pack(pady=(0, 5))

        # ===============================================
        # 3. BARRE DE PROGRESSION & TEXTE DYNAMIQUE
        # ===============================================
        self.subtitle = ctk.CTkLabel(
            self.content,
            text=self.loading_messages[0],
            font=("Arial", 12),
            text_color="#AAAAAA"
        )
        self.subtitle.pack(pady=(5, 20))

        # Progress Bar animée
        self.progress = ctk.CTkProgressBar(
            self.content,
            width=320,
            height=10,
            corner_radius=5,
            progress_color="#1F6AA5",
            fg_color="#121620"
        )
        self.progress.pack(pady=(0, 10))
        self.progress.configure(mode="indeterminate")
        self.progress.start()

        # Lancement des boucles d'animation
        self.rotate_logo()
        self.update_loading_text()

    def create_fallback_logo(self):
        """Logo alternatif au cas où l'image logo.png manque"""
        self.logo = ctk.CTkLabel(self.content, text="🧠", font=("Arial", 60))
        self.logo.pack(pady=(0, 20))

    def rotate_logo(self):
        """Rotation douce du logo"""
        if not self.is_animating:
            return

        if os.path.exists(self.logo_path):
            try:
                raw_image = Image.open(self.logo_path)
                self.angle = (self.angle - 8) % 360
                rotated = raw_image.rotate(self.angle)

                self.logo_image = ctk.CTkImage(
                    light_image=rotated,
                    dark_image=rotated,
                    size=(130, 130)
                )
                self.logo.configure(image=self.logo_image)
            except Exception:
                pass

        self.after(50, self.rotate_logo)

    def update_loading_text(self):
        """Fait défiler les messages d'attente dynamiquement"""
        if not self.is_animating:
            return

        self.msg_index = (self.msg_index + 1) % len(self.loading_messages)
        self.subtitle.configure(text=self.loading_messages[self.msg_index])

        # Change de message toutes les 1.8 secondes
        self.after(1800, self.update_loading_text)

    def destroy(self):
        """Arrête proprement les timers lors du changement de page"""
        self.is_animating = False
        try:
            self.progress.stop()
        except Exception:
            pass
        super().destroy()