"""
===========================================
TMY Quiz Maker
Version 4.5

home.py - Écran d'accueil Pro & Moderne avec Mode Multijoueur
===========================================
"""

import os
import customtkinter as ctk
from PIL import Image

import ui.colors as colors
import ui.fonts as fonts


class HomePage(ctk.CTkFrame):

    def __init__(
        self,
        master,
        tmy_callback,
        manual_callback,
        quizzes_callback=None,
        multiplayer_callback=None,
        join_callback=None,
        settings_callback=None,
        stats_callback=None
    ):
        super().__init__(master)

        self.tmy_callback = tmy_callback
        self.manual_callback = manual_callback
        self.quizzes_callback = quizzes_callback
        self.multiplayer_callback = multiplayer_callback
        self.join_callback = join_callback
        self.settings_callback = settings_callback
        self.stats_callback = stats_callback

        self.configure(fg_color=colors.BACKGROUND)

        # Conteneur principal avec décalage
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40, pady=20)

        # =========================================================
        # 1. BANNIÈRE / EN-TÊTE DASHBOARD
        # =========================================================
        self.header_card = ctk.CTkFrame(
            self.container, 
            fg_color="#1E222D", 
            corner_radius=15,
            border_width=1,
            border_color="#2B303C"
        )
        self.header_card.pack(fill="x", pady=(0, 20), ipady=5)

        self.header_content = ctk.CTkFrame(self.header_card, fg_color="transparent")
        self.header_content.pack(fill="x", padx=20, pady=10)

        # Logo
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            try:
                pil_image = Image.open(logo_path)
                self.logo_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(60, 60))
                self.logo_label = ctk.CTkLabel(self.header_content, image=self.logo_img, text="")
                self.logo_label.pack(side="left", padx=(5, 15))
            except Exception:
                pass

        # Titre + Sous-titre
        self.title_frame = ctk.CTkFrame(self.header_content, fg_color="transparent")
        self.title_frame.pack(side="left")

        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="TMY QUIZ MAKER",
            font=("Arial", 22, "bold"),
            text_color="#FFFFFF"
        )
        self.title_label.pack(anchor="w")

        self.subtitle = ctk.CTkLabel(
            self.title_frame,
            text="Smart Learning & Party Experience",
            font=("Arial", 12),
            text_color="#AAAAAA"
        )
        self.subtitle.pack(anchor="w")

        # Badge Joueur / XP (En haut à droite)
        self.player_badge = ctk.CTkFrame(self.header_content, fg_color="#121620", corner_radius=10)
        self.player_badge.pack(side="right", padx=10)

        self.xp_label = ctk.CTkLabel(
            self.player_badge,
            text="🏆 NIVEAU 1  •  0 XP",
            font=("Arial", 12, "bold"),
            text_color="#FFD700"
        )
        self.xp_label.pack(padx=15, pady=8)

        # =========================================================
        # 2. GRILLE DE SÉLECTION DE MODE DE JEU (2x2)
        # =========================================================
        self.grid_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, pady=10)

        self.grid_frame.grid_columnconfigure((0, 1), weight=1, uniform="group_home")
        self.grid_frame.grid_rowconfigure((0, 1), weight=1, uniform="group_home_row")

        # --- CARTE 1 : GÉNÉRER AVEC TMY (IA) ---
        self.card_tmy = self.create_action_card(
            parent=self.grid_frame,
            icon="🧠",
            tag="INTELLIGENCE ARTIFICIELLE",
            title="GÉNÉRER AVEC TMY",
            desc="Laisse l'IA créer un quiz sur-mesure en quelques secondes sur n'importe quel sujet.",
            btn_text="LANCER L'IA",
            btn_color="#1F6AA5",
            hover_color="#144870",
            command=self.open_tmy,
            row=0, col=0
        )

        # --- CARTE 2 : MULTIJOUEUR (NOUVEAU !) ---
        self.card_multi = self.create_action_card(
            parent=self.grid_frame,
            icon="🌐",
            tag="MULTIJOUEUR SOCIAL",
            title="DÉFIS ENTRE AMIS",
            desc="Défie tes amis en direct ! 10 niveaux de jeu, classement en temps réel.",
            btn_text="VOIR LES NIVEAUX",
            btn_color="#8A2BE2",
            hover_color="#6A1B9A",
            command=self.open_multiplayer,
            row=0, col=1,
            badge="NOUVEAU"
        )

        # --- CARTE 3 : CRÉATION MANUELLE ---
        self.card_manual = self.create_action_card(
            parent=self.grid_frame,
            icon="✍️",
            tag="ÉDITION MANUELLE",
            title="CRÉER MANUELLEMENT",
            desc="Rédige tes propres questions, réponses, explications et minuteurs personnalisés.",
            btn_text="CRÉER UN QUIZ",
            btn_color="#2B2D42",
            hover_color="#1A1B29",
            command=self.open_manual,
            row=1, col=0
        )

        # --- CARTE 4 : MES QUIZ & BIBLIOTHÈQUE ---
        self.card_quizzes = self.create_action_card(
            parent=self.grid_frame,
            icon="📚",
            tag="BIBLIOTHÈQUE",
            title="MES QUIZ",
            desc="Consulte tes quiz créés, rejoue à tes préférés ou exporte-les pour tes proches.",
            btn_text="BIBLIOTHÈQUE",
            btn_color="#2B2D42",
            hover_color="#1A1B29",
            command=self.my_quizzes,
            row=1, col=1
        )

        # =========================================================
        # 3. BARRE D'OUTILS ET ACCÈS RAPIDE (PIED DE PAGE)
        # =========================================================
        self.footer_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.footer_frame.pack(fill="x", pady=(15, 0))

        # Bouton Rejoindre rapidement avec un CODE
        self.join_code_btn = ctk.CTkButton(
            self.footer_frame,
            text="🔑 REJOINDRE AVEC UN CODE SALON",
            font=("Arial", 12, "bold"),
            height=40,
            fg_color="#008080",
            hover_color="#004D4D",
            command=self.join_with_code
        )
        self.join_code_btn.pack(side="left", padx=5)

        # Bouton Statistiques Globales
        self.stats_btn = ctk.CTkButton(
            self.footer_frame,
            text="📊 STATISTIQUES",
            font=("Arial", 12, "bold"),
            height=40,
            fg_color="#3A3D52",
            hover_color="#232533",
            command=self.open_stats
        )
        self.stats_btn.pack(side="right", padx=5)

        # Bouton Paramètres
        self.settings_btn = ctk.CTkButton(
            self.footer_frame,
            text="⚙️ PARAMÈTRES",
            font=("Arial", 12, "bold"),
            height=40,
            fg_color="#3A3D52",
            hover_color="#232533",
            command=self.settings
        )
        self.settings_btn.pack(side="right", padx=5)

    def create_action_card(self, parent, icon, tag, title, desc, btn_text, btn_color, hover_color, command, row, col, badge=None):
        """Créateur dynamique de carte UI moderne (v2 pro : liseré, badge icône, étiquette de catégorie)"""
        card = ctk.CTkFrame(parent, fg_color="#1E222D", corner_radius=16, border_width=1, border_color="#2B303C")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Liseré supérieur coloré = identité visuelle de la carte
        accent = ctk.CTkFrame(card, fg_color=btn_color, height=3, corner_radius=0)
        accent.pack(fill="x", side="top")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(14, 15))

        # Ligne du haut : badge icône circulaire + étiquette "NOUVEAU" éventuelle
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x")

        icon_badge = ctk.CTkFrame(top_row, fg_color=btn_color, corner_radius=14, width=48, height=48)
        icon_badge.pack(side="left")
        icon_badge.pack_propagate(False)
        ctk.CTkLabel(icon_badge, text=icon, font=("Arial", 20)).pack(expand=True)

        if badge:
            ctk.CTkLabel(
                top_row, text=badge, font=("Arial", 9, "bold"), text_color="#FFFFFF",
                fg_color="#E53935", corner_radius=8
            ).pack(side="right", ipadx=7, ipady=3)

        # Étiquette de catégorie
        ctk.CTkLabel(content, text=tag, font=("Arial", 9, "bold"), text_color=btn_color).pack(anchor="w", pady=(10, 0))

        lbl_title = ctk.CTkLabel(content, text=title, font=("Arial", 16, "bold"), text_color="#FFFFFF")
        lbl_title.pack(anchor="w", pady=(2, 5))

        lbl_desc = ctk.CTkLabel(content, text=desc, font=("Arial", 11), text_color="#AAAAAA", justify="left", wraplength=260)
        lbl_desc.pack(anchor="w", pady=(0, 10))

        # Bouton d'action bas de carte
        btn = ctk.CTkButton(
            content,
            text=btn_text,
            font=("Arial", 12, "bold"),
            height=38,
            corner_radius=10,
            fg_color=btn_color,
            hover_color=hover_color,
            command=command
        )
        btn.pack(fill="x", side="bottom")

        return card

    # =====================================
    # Callbacks & Actions
    # =====================================
    def open_tmy(self):
        if self.tmy_callback:
            self.tmy_callback()

    def open_manual(self):
        if self.manual_callback:
            self.manual_callback()

    def my_quizzes(self):
        if self.quizzes_callback:
            self.quizzes_callback()
        else:
            print("Ouverture Bibliothèque Quiz")

    def open_multiplayer(self):
        if self.multiplayer_callback:
            self.multiplayer_callback()
        else:
            print("Ouverture Mode Multijoueur")

    def join_with_code(self):
        if self.join_callback:
            self.join_callback()
        else:
            print("Saisie du code de salon multijoueur")

    def open_stats(self):
        if self.stats_callback:
            self.stats_callback()
        else:
            print("Ouverture Statistiques Profil")

    def settings(self):
        if self.settings_callback:
            self.settings_callback()
        else:
            print("Ouverture Paramètres")