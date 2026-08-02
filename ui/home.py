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
from auth_client import session


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
        account_callback=None
    ):
        super().__init__(master)

        self.tmy_callback = tmy_callback
        self.manual_callback = manual_callback
        self.quizzes_callback = quizzes_callback
        self.multiplayer_callback = multiplayer_callback
        self.join_callback = join_callback
        self.settings_callback = settings_callback
        self.account_callback = account_callback

        self.configure(fg_color=colors.BACKGROUND)

        # Conteneur principal avec décalage
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40, pady=20)

        # =========================================================
        # 1. BANNIÈRE / EN-TÊTE D'ORIGINE (INTACT)
        # =========================================================
        self.header_card = ctk.CTkFrame(
            self.container, 
            fg_color="#1E222D", 
            corner_radius=15,
            border_width=1,
            border_color="#2B303C"
        )
        self.header_card.pack(fill="x", pady=(0, 15), ipady=5)

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

        # Badge Joueur / XP cliquable
        user = session.user or {}
        niveau = user.get("niveau", 1)
        xp = user.get("xp", 0)
        badge_kwargs = dict(
            font=("Arial", 12, "bold"),
            text_color="#FFD700",
            fg_color="#121620",
            hover_color="#1B2030",
            corner_radius=10,
            height=36,
            command=self.open_account,
        )
        avatar_img = session.avatar_image() if session.est_connecte() else None
        if avatar_img:
            self._avatar_ctk_img = ctk.CTkImage(light_image=avatar_img, dark_image=avatar_img, size=(24, 24))
            self.player_badge = ctk.CTkButton(
                self.header_content, text=f"  NIVEAU {niveau}  •  {xp} XP",
                image=self._avatar_ctk_img, compound="left", **badge_kwargs,
            )
        else:
            self.player_badge = ctk.CTkButton(
                self.header_content, text=f"👤 NIVEAU {niveau}  •  {xp} XP", **badge_kwargs,
            )
        self.player_badge.pack(side="right", padx=(6, 10))

        # Icône Paramètres (⚙️)
        self.settings_icon_btn = ctk.CTkButton(
            self.header_content,
            text="⚙️",
            font=("Arial", 15),
            width=36, height=36,
            fg_color="#121620",
            hover_color="#1B2030",
            corner_radius=10,
            command=self.settings
        )
        self.settings_icon_btn.pack(side="right", padx=(0, 4))

        # =========================================================
        # 1.Bis MESSAGE DE BIENVENUE (comme sur l'image)
        # =========================================================
        self.welcome_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.welcome_frame.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(
            self.welcome_frame,
            text="Bienvenue ! Que veux-tu faire aujourd'hui ?",
            font=("Arial", 15, "bold"),
            text_color="#FFFFFF"
        ).pack(anchor="center")

        ctk.CTkLabel(
            self.welcome_frame,
            text="Choisis ton mode de jeu et amuse-toi 🚀",
            font=("Arial", 11),
            text_color="#8888AA"
        ).pack(anchor="center", pady=(2, 0))

        # =========================================================
        # 2. GRILLE DE SÉLECTION DE MODE DE JEU (2x2) AVEC STYLE DESIGN
        # =========================================================
        self.grid_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, pady=5)

        self.grid_frame.grid_columnconfigure((0, 1), weight=1, uniform="group_home")
        self.grid_frame.grid_rowconfigure((0, 1), weight=1, uniform="group_home_row")

        # --- CARTE 1 : GÉNÉRER AVEC TMY (IA) ---
        self.card_tmy = self.create_advanced_card(
            parent=self.grid_frame,
            icon_badge_char="🧠",
            right_illustration="🧠",
            tag="INTELLIGENCE ARTIFICIELLE",
            title="GÉNÉRER AVEC TMY",
            desc="Laisse l'IA créer un quiz sur-mesure en quelques secondes sur n'importe quel sujet.",
            btn_text="🧠  LANCER L'IA",
            border_color="#1F6AA5",
            btn_color="#1F6AA5",
            hover_color="#144870",
            command=self.open_tmy,
            row=0, col=0
        )

        # --- CARTE 2 : MULTIJOUEUR ---
        self.card_multi = self.create_advanced_card(
            parent=self.grid_frame,
            icon_badge_char="🌐",
            right_illustration="🏆",
            tag="MULTIJOUEUR SOCIAL",
            title="DÉFIS ENTRE AMIS",
            desc="Défie tes amis en direct ! 10 niveaux de jeu, classement en temps réel.",
            btn_text="📊  VOIR LES NIVEAUX",
            border_color="#8A2BE2",
            btn_color="#8A2BE2",
            hover_color="#6A1B9A",
            command=self.open_multiplayer,
            row=0, col=1
        )

        # --- CARTE 3 : MODE CLASSE ---
        self.card_manual = self.create_advanced_card(
            parent=self.grid_frame,
            icon_badge_char="🎓",
            right_illustration="🏫",
            tag="CRÉATION & SALLE EN DIRECT",
            title="MODE CLASSE",
            desc="Crée ton propre quiz avec tes questions, ou rejoins une salle déjà lancée avec un code PIN.",
            btn_text="👥  COMMENCER",
            border_color="#8A2BE2",
            btn_color="#8A2BE2",
            hover_color="#6A1B9A",
            command=self.open_manual,
            row=1, col=0
        )

        # --- CARTE 4 : MES QUIZ & BIBLIOTHÈQUE ---
        self.card_quizzes = self.create_advanced_card(
            parent=self.grid_frame,
            icon_badge_char="📚",
            right_illustration="📚",
            tag="BIBLIOTHÈQUE",
            title="MES QUIZ",
            desc="Consulte tes quiz créés, rejoue à tes préférés ou exporte-les pour tes proches.",
            btn_text="📖  BIBLIOTHÈQUE",
            border_color="#1F6AA5",
            btn_color="#1F6AA5",
            hover_color="#144870",
            command=self.my_quizzes,
            row=1, col=1
        )

    def create_advanced_card(self, parent, icon_badge_char, right_illustration, tag, title, desc, btn_text, border_color, btn_color, hover_color, command, row, col):
        """Crée une carte de style haut de gamme avec bordure lumineuse et illustration latérale discrète"""
        card = ctk.CTkFrame(
            parent, 
            fg_color="#131620", 
            corner_radius=18, 
            border_width=1.5, 
            border_color=border_color
        )
        card.grid(row=row, column=col, padx=10, pady=8, sticky="nsew")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=16)

        # Ligne supérieure : Badge icône à gauche et Illustration optionnelle à droite
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 6))

        # Badge carré arrondi de l'icône principale
        icon_box = ctk.CTkFrame(top_row, fg_color=border_color, corner_radius=12, width=46, height=46)
        icon_box.pack(side="left")
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text=icon_badge_char, font=("Arial", 20)).pack(expand=True)

        # Illustration symbolique à droite (comme sur ton image de référence)
        illu_box = ctk.CTkFrame(top_row, fg_color="#1C2130", corner_radius=12, width=65, height=46)
        illu_box.pack(side="right")
        illu_box.pack_propagate(False)
        ctk.CTkLabel(illu_box, text=right_illustration, font=("Arial", 18)).pack(expand=True)

        # Étiquette de catégorie (Tag)
        ctk.CTkLabel(content, text=tag, font=("Arial", 9, "bold"), text_color=border_color).pack(anchor="w", pady=(4, 0))

        # Titre de la carte
        ctk.CTkLabel(content, text=title, font=("Arial", 16, "bold"), text_color="#FFFFFF").pack(anchor="w", pady=(2, 4))

        # Description
        ctk.CTkLabel(content, text=desc, font=("Arial", 11), text_color="#9999BB", justify="left", wraplength=270).pack(anchor="w", pady=(0, 12))

        # Bouton d'action en bas de carte avec effet de clic fluide
        btn = ctk.CTkButton(
            content,
            text=btn_text,
            font=("Arial", 12, "bold"),
            height=40,
            corner_radius=12,
            fg_color=btn_color,
            hover_color=hover_color,
            command=lambda c=command, b_color=btn_color: self._effet_clic(btn_ref[0], b_color, c)
        )
        btn_ref = [btn]
        btn.pack(fill="x", side="bottom")

        return card

    def _effet_clic(self, bouton, couleur_originale, command):
        """Petit flash visuel au clic"""
        bouton.configure(fg_color="#FFFFFF")
        self.after(90, lambda: bouton.configure(fg_color=couleur_originale))
        if command:
            command()

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

    def open_account(self):
        if self.account_callback:
            self.account_callback()
        else:
            print("Ouverture Compte / Connexion")

    def settings(self):
        if self.settings_callback:
            self.settings_callback()
        else:
            print("Ouverture Paramètres")