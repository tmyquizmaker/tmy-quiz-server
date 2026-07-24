"""
===========================================
TMY Quiz Maker
Version 5.0

loading.py - Splash Screen de démarrage Ultra-Pro
===========================================
"""

import os
import customtkinter as ctk
from PIL import Image

import ui.colors as colors
import ui.fonts as fonts


class LoadingScreen(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color=colors.BACKGROUND)

        # Conteneur principal centré
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40, pady=40)

        # ===============================================
        # CARTE CENTRALE SPLASH
        # ===============================================
        self.card = ctk.CTkFrame(
            self.container,
            fg_color="#1E222D",
            corner_radius=24,
            border_width=1,
            border_color="#2B303C"
        )
        self.card.pack(expand=True, fill="both", padx=100, pady=50)

        # Frame de contenu interne
        self.content = ctk.CTkFrame(self.card, fg_color="transparent")
        self.content.pack(expand=True, padx=30, pady=30)

        # ===============================================
        # 1. AFFICHAGE DU LOGO PRINCIPAL
        # ===============================================
        self.logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(self.logo_path):
            try:
                raw_image = Image.open(self.logo_path)
                self.logo_image = ctk.CTkImage(
                    light_image=raw_image,
                    dark_image=raw_image,
                    size=(140, 140)
                )
                self.logo = ctk.CTkLabel(self.content, image=self.logo_image, text="")
                self.logo.pack(pady=(0, 15))
            except Exception:
                self.create_fallback_logo()
        else:
            self.create_fallback_logo()

        # ===============================================
        # 2. BADGE VERSION & TITRE
        # ===============================================
        self.badge = ctk.CTkFrame(self.content, fg_color="#121620", corner_radius=12)
        self.badge.pack(pady=(0, 8))

        self.badge_lbl = ctk.CTkLabel(
            self.badge,
            text="✨ VERSION 5.0 PRO",
            font=("Arial", 10, "bold"),
            text_color="#1F6AA5"
        )
        self.badge_lbl.pack(padx=14, pady=4)

        self.title = ctk.CTkLabel(
            self.content,
            text="TMY QUIZ MAKER",
            font=("Arial", 22, "bold"),
            text_color="#FFFFFF"
        )
        self.title.pack(pady=(0, 2))

        self.subtitle = ctk.CTkLabel(
            self.content,
            text="Initialisation du système & préparation de l'expérience...",
            font=("Arial", 11),
            text_color="#8A8F9E"
        )
        self.subtitle.pack(pady=(0, 25))

        # ===============================================
        # 3. BARRE DE PROGRESSION & POURCENTAGE
        # ===============================================
        self.progress_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=20)

        # Statut textuel (ex: "Chargement des modules...")
        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="Démarrage...",
            font=("Arial", 11, "bold"),
            text_color="#AAAAAA"
        )
        self.status_label.pack(side="left")

        # Pourcentage (ex: "90%")
        self.percent_label = ctk.CTkLabel(
            self.progress_frame,
            text="0%",
            font=("Arial", 11, "bold"),
            text_color="#1F6AA5"
        )
        self.percent_label.pack(side="right")

        # Barre de progression Custom
        self.progress_bar = ctk.CTkProgressBar(
            self.content,
            width=360,
            height=10,
            corner_radius=5,
            progress_color="#1F6AA5",
            fg_color="#121620"
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(6, 15))

        # Footer discret
        self.footer = ctk.CTkLabel(
            self.content,
            text="Powered by TMY Engine • Tout droit réservé",
            font=("Arial", 9),
            text_color="#555861"
        )
        self.footer.pack(pady=(10, 0))

    def create_fallback_logo(self):
        """Si logo.png est introuvable"""
        self.logo = ctk.CTkLabel(self.content, text="🧠", font=("Arial", 65))
        self.logo.pack(pady=(0, 15))

    # ===============================================
    # Méthodes de mise à jour pour l'animation
    # ===============================================
    def update_progress(self, valeur, message=""):
        """Mettre à jour la barre et les textes en direct"""
        # Limite entre 0.0 et 1.0
        valeur_clamped = max(0.0, min(1.0, valeur))
        
        self.progress_bar.set(valeur_clamped)
        self.percent_label.configure(text=f"{int(valeur_clamped * 100)}%")
        
        if message:
            self.status_label.configure(text=message)

    def animation(self):
        """Retourne la séquence d'étapes pour AppController"""
        return [
            (0.15, "Chargement des composants..."),
            (0.35, "Connexion aux services IA..."),
            (0.60, "Chargement de la base de données..."),
            (0.85, "Dernières vérifications..."),
            (1.00, "Prêt !")
        ]