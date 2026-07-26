"""
===========================================
TMY Quiz Maker
Version 4.1

result_eleve.py
Écran résultat pour les Élèves avec informations 
du prof, du quiz et de l'étudiant.
===========================================
"""

import os
from datetime import datetime
import customtkinter as ctk
from PIL import Image

from ui.colors import *
from ui.buttons import LargeButton
import ui.fonts as fonts


class ResultElevePage(ctk.CTkFrame):

    def __init__(
        self,
        master,
        # Infos Dynamiques (Quiz / Prof / Élève)
        titre_quiz="Maître du Savoir",
        nom_prof="Prof. Max Junior",
        nom_eleve="Max Student",
        date_quiz=None,
        # Statistiques
        score=2,
        total=3,
        total_xp=1788,
        max_combo=2,
        average_time=2.3,
        bonnes_reponses=2,
        mauvaises_reponses=1,
        non_repondues=0,
        # Callbacks
        certificat_callback=None,
        home_callback=None,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.home_callback = home_callback
        self.certificat_callback = certificat_callback

        # Date automatique si non fournie
        if not date_quiz:
            date_quiz = datetime.now().strftime("%d %b %Y")

        self.configure(fg_color="#090D16")  # Fond très sombre

        # ---------------------------------------------------------
        # CREATION DU CONTENEUR PRINCIPAL
        # ---------------------------------------------------------
        self.main_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # ---------------------------------------------------------
        # LOGIQUE DES MENTIONS ET STICKERS SELON LE SCORE
        # ---------------------------------------------------------
        pourcentage = int((score / total) * 100) if total > 0 else 0

        if pourcentage < 50:
            mention = "INSUFFISANT !"
            titre_rank = "🌱 Insuffisant"
            message = "Les connaissances évaluées ne sont pas encore acquises.\nUn travail plus régulier et des révisions approfondies sont nécessaires pour progresser."
            conseil_perf = "Ne décourage pas !\nRévise le cours et réessaie."
            rank_color = "#FF5252"  # Rouge
            sticker = "🌱"
        elif pourcentage < 80:
            mention = "SATISFAISANT !"
            titre_rank = "🔥 Satisfaisant"
            message = "Les objectifs principaux sont globalement atteints.\nDes efforts supplémentaires permettront de consolider les acquis et d'améliorer les résultats."
            conseil_perf = "Bon travail !\nEncore un petit effort pour l'excellence."
            rank_color = "#2196F3"  # Bleu
            sticker = "🔥"
        else:
            mention = "EXCELLENT !"
            titre_rank = "👑 Excellent"
            message = "Excellente maîtrise du sujet !\nLes compétences et connaissances évaluées sont parfaitement acquises."
            conseil_perf = "Félicitations !\nTu maîtrises parfaitement le sujet."
            rank_color = "#00E676"  # Vert
            sticker = "👑"

        # ---------------------------------------------------------
        # 1. BARRE SUPERIEURE : INFOS DU QUIZ & ÉLÈVE
        # ---------------------------------------------------------
        self.header_info = ctk.CTkFrame(
            self.main_container, 
            fg_color="#111726", 
            corner_radius=12,
            border_width=1,
            border_color="#1E293B"
        )
        self.header_info.pack(fill="x", pady=(0, 15), ipady=5)

        # Logo
        logo_path = os.path.join("assets", "logo.png")
        self.logo_img = None
        if os.path.exists(logo_path):
            try:
                pil_img = Image.open(logo_path)
                self.logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(50, 50))
            except Exception as e:
                print("Erreur logo:", e)

        if self.logo_img:
            ctk.CTkLabel(self.header_info, image=self.logo_img, text="").pack(side="left", padx=15)

        info_grid = ctk.CTkFrame(self.header_info, fg_color="transparent")
        info_grid.pack(side="left", expand=True, fill="x", padx=10)
        info_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._add_header_item(info_grid, "📖", "TITRE DU QUIZ", titre_quiz, "#2196F3", 0)
        self._add_header_item(info_grid, "🎓", "PROFESSEUR", nom_prof, "#00E676", 1)
        self._add_header_item(info_grid, "👤", "ÉTUDIANT", nom_eleve, "#FFD700", 2)
        self._add_header_item(info_grid, "📅", "DATE DU QUIZ", date_quiz, "#A855F7", 3)

        if self.logo_img:
            ctk.CTkLabel(self.header_info, image=self.logo_img, text="").pack(side="right", padx=15)

        # ---------------------------------------------------------
        # 2. CARTE BANNIÈRE : MENTION & STICKER
        # ---------------------------------------------------------
        self.banner_card = ctk.CTkFrame(
            self.main_container, 
            fg_color="#0F172A", 
            corner_radius=15, 
            border_width=1, 
            border_color="#1E293B"
        )
        self.banner_card.pack(fill="x", pady=(0, 15), ipady=15)

        text_banner = ctk.CTkFrame(self.banner_card, fg_color="transparent")
        text_banner.pack(side="left", expand=True, fill="both", padx=30)

        ctk.CTkLabel(
            text_banner, 
            text="🏆 QUIZ TERMINÉ !", 
            font=("Arial", 12, "bold"), 
            text_color="#94A3B8"
        ).pack(anchor="w", pady=(5, 0))

        # Affichage de la Mention à la place de "FÉLICITATIONS !"
        ctk.CTkLabel(
            text_banner, 
            text=mention, 
            font=("Arial", 26, "bold"), 
            text_color=rank_color
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_banner, 
            text=message, 
            font=("Arial", 13), 
            text_color="#94A3B8"
        ).pack(anchor="w")

        # Badge Visuel avec STICKER adapté
        badge_frame = ctk.CTkFrame(self.banner_card, fg_color="#1E293B", width=80, height=80, corner_radius=40)
        badge_frame.pack(side="right", padx=30)
        badge_frame.pack_propagate(False)
        ctk.CTkLabel(badge_frame, text=sticker, font=("Segoe UI Emoji", 38)).pack(expand=True)

        # ---------------------------------------------------------
        # 3. GRILLE DE STATISTIQUES (2x2)
        # ---------------------------------------------------------
        self.stats_grid = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.stats_grid.pack(fill="x", pady=(0, 15))
        self.stats_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.create_stat_card(self.stats_grid, "🎯 SCORE FINAL", f"{score}/{total}", f"Précision : {pourcentage}%", "#2196F3", 0)
        self.create_stat_card(self.stats_grid, "⚡ POINTS XP", f"+{total_xp}", "XP Gagnés", "#FFD700", 1)
        self.create_stat_card(self.stats_grid, "🔥 MEILLEUR COMBO", f"x{max_combo}", "Série de réponses", "#FF7A00", 2)
        self.create_stat_card(self.stats_grid, "⏱️ TEMPS MOYEN", f"{average_time}s", "Par question", "#00E676", 3)

        # ---------------------------------------------------------
        # 4. PANNEAUX BAS (PERFORMANCE + RÉCAPITULATIF)
        # ---------------------------------------------------------
        self.bottom_grid = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.bottom_grid.pack(fill="x", pady=(0, 15))
        self.bottom_grid.grid_columnconfigure((0, 1), weight=1)

        # Panel Gauche : Performance
        self.perf_card = ctk.CTkFrame(self.bottom_grid, fg_color="#111726", corner_radius=12)
        self.perf_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew", ipady=10)

        ctk.CTkLabel(self.perf_card, text="📈 PERFORMANCE GLOBALE", font=("Arial", 12, "bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=10)
        
        perf_sub = ctk.CTkFrame(self.perf_card, fg_color="transparent")
        perf_sub.pack(fill="x", padx=15)
        
        # Circle Score
        circle = ctk.CTkFrame(perf_sub, fg_color="#1E293B", width=70, height=70, corner_radius=35)
        circle.pack(side="left", padx=(0, 15))
        circle.pack_propagate(False)
        ctk.CTkLabel(circle, text=f"{pourcentage}%", font=("Arial", 16, "bold"), text_color=rank_color).pack(expand=True)

        perf_txt = ctk.CTkFrame(perf_sub, fg_color="transparent")
        perf_txt.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(perf_txt, text=titre_rank, font=("Arial", 14, "bold"), text_color=rank_color).pack(anchor="w")
        ctk.CTkLabel(perf_txt, text=conseil_perf, font=("Arial", 11), text_color="#94A3B8", justify="left").pack(anchor="w")

        # Panel Droit : Récapitulatif
        self.recap_card = ctk.CTkFrame(self.bottom_grid, fg_color="#111726", corner_radius=12)
        self.recap_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew", ipady=10)

        ctk.CTkLabel(self.recap_card, text="📊 RÉCAPITULATIF DES RÉPONSES", font=("Arial", 12, "bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=10)
        
        self._add_recap_line(self.recap_card, "✅ Bonnes réponses", bonnes_reponses, "#00E676")
        self._add_recap_line(self.recap_card, "❌ Mauvaises réponses", mauvaises_reponses, "#FF5252")
        self._add_recap_line(self.recap_card, "➖ Non répondues", non_repondues, "#2196F3")

        # ---------------------------------------------------------
        # 5. BOUTON ACTION : TÉLÉCHARGER CERTIFICAT
        # ---------------------------------------------------------
        self.cert_btn = ctk.CTkButton(
            self.main_container,
            text="🎖️ TÉLÉCHARGER LE CERTIFICAT\nObtiens ton certificat de réussite",
            font=("Arial", 14, "bold"),
            height=50,
            fg_color="#1D4ED8",
            hover_color="#1E40AF",
            command=self.certificat_callback
        )
        self.cert_btn.pack(fill="x", pady=(10, 0))

    def _add_header_item(self, parent, icon, title, val, color, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, sticky="ew")
        ctk.CTkLabel(frame, text=f"{icon} {title}", font=("Arial", 9, "bold"), text_color="#64748B").pack(anchor="w")
        ctk.CTkLabel(frame, text=val, font=("Arial", 12, "bold"), text_color=color).pack(anchor="w")

    def create_stat_card(self, parent, title, value, sub_text, color, col):
        card = ctk.CTkFrame(parent, fg_color="#111726", corner_radius=10, border_width=1, border_color="#1E293B")
        card.grid(row=0, column=col, padx=4, sticky="nsew")

        accent = ctk.CTkFrame(card, fg_color=color, height=3, corner_radius=2)
        accent.pack(fill="x", side="top", padx=8, pady=(6, 0))

        ctk.CTkLabel(card, text=title, font=("Arial", 10, "bold"), text_color="#64748B").pack(pady=(6, 2))
        ctk.CTkLabel(card, text=value, font=("Arial", 20, "bold"), text_color=color).pack(pady=0)
        ctk.CTkLabel(card, text=sub_text, font=("Arial", 10), text_color="#475569").pack(pady=(0, 6))

    def _add_recap_line(self, parent, label, val, color):
        line = ctk.CTkFrame(parent, fg_color="transparent")
        line.pack(fill="x", padx=15, pady=2)
        ctk.CTkLabel(line, text=label, font=("Arial", 11), text_color="#CBD5E1").pack(side="left")
        ctk.CTkLabel(line, text=str(val), font=("Arial", 11, "bold"), text_color=color).pack(side="right")