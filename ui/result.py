"""
===========================================
TMY Quiz Maker
Version 4.1

result.py
Écran résultat avec logo dans assets/logo.png
===========================================
"""

import os
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageGrab

from ui.colors import *
from ui.buttons import LargeButton
import ui.fonts as fonts


class ResultPage(ctk.CTkFrame):

    def __init__(
        self,
        master,
        score,
        total,
        total_xp,
        max_combo,
        average_time,
        regenerate_callback,
        home_callback,
        quiz_callback=None
    ):
        super().__init__(master)

        self.regenerate_callback = regenerate_callback
        self.home_callback = home_callback
        self.quiz_callback = quiz_callback

        self.configure(fg_color=BACKGROUND)

        # Calculs
        pourcentage = int((score / total) * 100) if total > 0 else 0

        if pourcentage < 50:
            titre = "🌱 Explorateur"
            message = "Continue à apprendre !\nChaque erreur est une étape vers la réussite."
            rank_color = "#FF9800"
        elif pourcentage < 80:
            titre = "🔥 Maître du Savoir"
            message = "Excellent travail !\nTes connaissances deviennent solides."
            rank_color = "#2196F3"
        else:
            titre = "👑 Légende TMY"
            message = "Performance incroyable !\nTu maîtrises parfaitement ce sujet."
            rank_color = "#FFD700"

        # Conteneur central
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=40, pady=20)

        # ---------------------------------------------------------
        # 1. EN-TÊTE : Logos à gauche/droite & Titre au centre
        # ---------------------------------------------------------
        self.header_card = ctk.CTkFrame(
            self.main_container, 
            fg_color="#1E222D", 
            corner_radius=15, 
            border_width=2, 
            border_color=rank_color
        )
        self.header_card.pack(fill="x", pady=(0, 20), ipady=10)

        # Chargement du logo depuis assets/logo.png
        self.logo_image = None
        logo_path = os.path.join("assets", "logo.png")

        if os.path.exists(logo_path):
            try:
                pil_image = Image.open(logo_path)
                self.logo_image = ctk.CTkImage(
                    light_image=pil_image, 
                    dark_image=pil_image, 
                    size=(70, 70)
                )
                print(f"✅ Logo chargé avec succès depuis : {logo_path}")
            except Exception as e:
                print("Erreur lors du chargement du logo :", e)
        else:
            print(f"⚠️ Image non trouvée à l'emplacement : {logo_path}")

        # Frame horizontale interne
        self.header_content = ctk.CTkFrame(self.header_card, fg_color="transparent")
        self.header_content.pack(fill="x", padx=20, pady=10)

        # 👈 LOGO GAUCHE
        if self.logo_image:
            self.logo_left = ctk.CTkLabel(self.header_content, image=self.logo_image, text="")
            self.logo_left.pack(side="left", padx=(15, 0))

        # 👉 LOGO DROIT
        if self.logo_image:
            self.logo_right = ctk.CTkLabel(self.header_content, image=self.logo_image, text="")
            self.logo_right.pack(side="right", padx=(0, 15))

        # 🎯 TEXTES AU CENTRE
        self.center_text_frame = ctk.CTkFrame(self.header_content, fg_color="transparent")
        self.center_text_frame.pack(side="left", expand=True, fill="both")

        self.title_label = ctk.CTkLabel(
            self.center_text_frame,
            text="🎉 QUIZ TERMINÉ !",
            font=("Arial", 16, "bold"),
            text_color="#AAAAAA"
        )
        self.title_label.pack(pady=(0, 2))

        self.rank_label = ctk.CTkLabel(
            self.center_text_frame,
            text=titre,
            font=("Arial", 28, "bold"),
            text_color=rank_color
        )
        self.rank_label.pack(pady=(0, 2))

        self.msg_label = ctk.CTkLabel(
            self.center_text_frame,
            text=message,
            font=("Arial", 13),
            text_color="#DDDDDD",
            justify="center"
        )
        self.msg_label.pack(pady=(0, 0))

        # ---------------------------------------------------------
        # 2. GRILLE DE STATISTIQUES (2x2)
        # ---------------------------------------------------------
        self.stats_grid = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.stats_grid.pack(fill="x", pady=10)

        self.stats_grid.grid_columnconfigure((0, 1), weight=1, uniform="group1")

        # Stat 1 : Score & Précision
        self.create_stat_card(
            self.stats_grid,
            title="SCORE FINAL",
            value=f"{score}/{total}",
            sub_text=f"Précision : {pourcentage}%",
            color="#2196F3",
            row=0, col=0
        )

        # Stat 2 : Total XP
        self.create_stat_card(
            self.stats_grid,
            title="POINTS XP",
            value=f"+{total_xp}",
            sub_text="XP Gagnés",
            color="#FFD700",
            row=0, col=1
        )

        # Stat 3 : Meilleur Combo
        self.create_stat_card(
            self.stats_grid,
            title="MEILLEUR COMBO",
            value=f"x{max_combo}",
            sub_text="Série de réponses",
            color="#FF7A00",
            row=1, col=0
        )

        # Stat 4 : Temps Moyen
        self.create_stat_card(
            self.stats_grid,
            title="TEMPS MOYEN",
            value=f"{average_time}s",
            sub_text="Par question",
            color="#00E676",
            row=1, col=1
        )

        # ---------------------------------------------------------
        # 3. BOUTONS D'ACTION
        # ---------------------------------------------------------
        self.actions_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.actions_frame.pack(fill="x", pady=(20, 0))

        # Re-générer
        self.regenerate_button = ctk.CTkButton(
            self.actions_frame,
            text="🔄 RÉGÉNÉRER AVEC TMY",
            font=("Arial", 13, "bold"),
            height=45,
            fg_color="#1F6AA5",
            hover_color="#144870",
            command=self.regenerate_callback
        )
        self.regenerate_button.pack(side="left", expand=True, fill="x", padx=5)

        # Télécharger le résultat en image
        self.download_button = ctk.CTkButton(
            self.actions_frame,
            text="💾 TÉLÉCHARGER",
            font=("Arial", 13, "bold"),
            height=45,
            fg_color="#008080",
            hover_color="#004D4D",
            command=self.telecharger_resultat
        )
        self.download_button.pack(side="left", expand=True, fill="x", padx=5)

        # Mes Quiz (si présent)
        if self.quiz_callback:
            self.quiz_button = ctk.CTkButton(
                self.actions_frame,
                text="📚 MES QUIZ",
                font=("Arial", 13, "bold"),
                height=45,
                fg_color="#2B2D42",
                hover_color="#1A1B29",
                command=self.quiz_callback
            )
            self.quiz_button.pack(side="left", expand=True, fill="x", padx=5)

        # Retour Accueil
        self.home_button = ctk.CTkButton(
            self.actions_frame,
            text="🏠 ACCUEIL",
            font=("Arial", 13, "bold"),
            height=45,
            fg_color="#4A4E69",
            hover_color="#22223B",
            command=self.home_callback
        )
        self.home_button.pack(side="left", expand=True, fill="x", padx=5)

    def telecharger_resultat(self):
        """Capture la carte d'en-tête + les statistiques (sans les boutons d'action)
        et l'enregistre comme image PNG, au choix de l'utilisateur."""
        # On cache temporairement les boutons pour qu'ils n'apparaissent pas sur l'image
        self.actions_frame.pack_forget()
        self.update_idletasks()

        try:
            x = self.header_card.winfo_rootx()
            y = self.header_card.winfo_rooty()
            x2 = self.stats_grid.winfo_rootx() + self.stats_grid.winfo_width()
            y2 = self.stats_grid.winfo_rooty() + self.stats_grid.winfo_height()

            image = ImageGrab.grab(bbox=(x, y, x2, y2))
        except Exception as e:
            print(f"⚠️ Erreur lors de la capture du résultat : {e}")
            image = None
        finally:
            # On réaffiche les boutons dans tous les cas
            self.actions_frame.pack(fill="x", pady=(20, 0))

        if image is None:
            return

        nom_defaut = f"resultat_tmy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        chemin = filedialog.asksaveasfilename(
            title="Enregistrer le résultat",
            defaultextension=".png",
            initialfile=nom_defaut,
            filetypes=[("Image PNG", "*.png")],
        )
        if not chemin:
            return

        image.save(chemin, "PNG")

    def create_stat_card(self, parent, title, value, sub_text, color, row, col):
        """Méthode utilitaire pour créer une carte de statistique propre"""
        card = ctk.CTkFrame(parent, fg_color="#1E222D", corner_radius=12)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        accent_bar = ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=2)
        accent_bar.pack(fill="x", side="top", padx=10, pady=(8, 0))

        lbl_title = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 11, "bold"),
            text_color="#888888"
        )
        lbl_title.pack(pady=(8, 2))

        lbl_val = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 24, "bold"),
            text_color=color
        )
        lbl_val.pack(pady=2)

        lbl_sub = ctk.CTkLabel(
            card,
            text=sub_text,
            font=("Arial", 11),
            text_color="#666666"
        )
        lbl_sub.pack(pady=(0, 10))